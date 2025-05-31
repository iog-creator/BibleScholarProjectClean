import os
import requests
import json
import psycopg
import logging
import tempfile
import datetime
import time
import re
import threading
from utils.vector_search_demo import search_similar_verses
from flask import flash
from config.loader import get_config, ConfigValidationError

# ... existing code ... 

def query_lm_studio(prompt, max_tokens=4096, mode="general"):
    logger = init_debug_logging()  # Ensure logger is always defined at the top
    try:
        config = get_config()
    except ConfigValidationError as e:
        logger.error(f"Config validation failed: {e}")
        raise RuntimeError(f"Teaching Mode: Config validation failed: {e}")
    # If skipping LLM (e.g., in tests), return minimal structure immediately
    if os.getenv("SKIP_LLM", "").lower() in ["1", "true"]:
        return {
            "summary": "",
            "theological_terms": {},
            "cross_references": [],
            "historical_context": "",
            "original_language_notes": [],
            "related_entities": {"people": [], "places": []}
        }
    logger.info("Waiting for LM Studio inference lock...")
    with lm_studio_lock:
        logger.info("Acquired LM Studio inference lock. Running model inference.")
        url = config.api.lm_studio_url
        headers = {"Content-Type": "application/json"}
        model_settings = config.models[config.defaults["model"]]["parameters"]
        enable_thinking = config.features.enable_thinking
        payload = {
            "model": config.defaults["model"],
            "messages": [
                {"role": "system", "content": "You are a Bible study assistant. Respond with a valid JSON object containing: 'summary' (2-3 sentence summary from primary sources), 'theological_terms' (dict from primary sources), 'cross_references' (array from primary sources), 'historical_context' (string from primary and pre-1990 commentaries), 'original_language_notes' (array from primary sources), 'related_entities' (object with 'people' and 'places' arrays from primary sources). Ensure 'theological_terms' is a dict and arrays contain objects. Exclude post-1990 commentaries and community notes."},
                {"role": "user", "content": prompt}
            ],
            **model_settings,
            "max_tokens": max_tokens,
            "stream": False,
            "enable_thinking": enable_thinking
        }

        response = requests.post(url, headers=headers, json=payload)
        resp_json = response.json()
        content = resp_json.get('choices', [])[0].get('message', {}).get('content', '')
        # Log the full raw output to a file
        raw_output_file = os.path.join(os.path.dirname(__file__), '..', '..', 'logs', 'raw_model_output.txt')
        with open(raw_output_file, 'a', encoding='utf-8') as f:
            f.write(f'[query_lm_studio] Raw model output at {datetime.datetime.now()}:\n{repr(content)}\n{"-"*50}\n')
        logger.info(f'Raw model output written to {raw_output_file}')
        # Clean the content before parsing
        content = content.strip()
        # Remove markdown code block markers if present
        content = re.sub(r'^```json\s*|^```\s*|```$', '', content, flags=re.MULTILINE)
        # Teaching Mode: Always parse the model output string as JSON before returning to the API/UI.
        # This ensures the UI always receives a dict, never a raw string, and prevents template errors.
        try:
            parsed_content = json.loads(content)
            logger.info('Successfully parsed model output as JSON (teaching mode enforced)')
            return parsed_content
        except Exception as e:
            logger.warning(f'json.loads failed: {e}')
            if json5:
                try:
                    parsed_content = json5.loads(content)
                    logger.info('Successfully parsed model output as JSON5 (tolerant fallback, teaching mode)')
                    return parsed_content
                except Exception as e2:
                    logger.error(f'json5 also failed to parse: {e2}')
            else:
                logger.warning('json5 is not installed. Install it for more tolerant JSON parsing.')
        # If all parsing fails, return a minimal structure with error
        logger.error('Model output could not be parsed as JSON. Returning error structure.')
        return {'error': 'Model output could not be parsed as JSON', 'raw_output': content}

# ... existing code ... 