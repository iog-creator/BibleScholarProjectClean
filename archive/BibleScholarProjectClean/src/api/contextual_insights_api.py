"""
Contextual Insights API for BibleScholarProject

This API provides an endpoint to generate rich contextual insights for Bible verses, topics, or text snippets.
Features:
- Summaries
- Cross-references
- Theological term explanations
- Historical context
- Original language notes
- Related entities (people, places)

Version: 1.0.0

NOTE: Always run with PYTHONPATH=src from the project root for all scripts and API runs.
"""
from flask import Blueprint, request, jsonify, Flask
from flask_caching import Cache
import logging
import json
import datetime
from dspy_programs.contextual_insights_program import generate_insights
import os

contextual_insights_api = Blueprint("contextual_insights_api", __name__)

app = Flask(__name__)
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 300
cache = Cache(app)

logging.basicConfig(level=logging.INFO, handlers=[
    logging.StreamHandler()
])
logger = logging.getLogger(__name__)

@contextual_insights_api.route("/insights", methods=["POST"])
def get_contextual_insights():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        input_type = data.get("type")
        if input_type not in ["verse", "topic", "text_snippet"]:
            logger.error(f"Invalid input type received: {input_type}")
            return jsonify({"error": "Invalid input type: must be 'verse', 'topic', or 'text_snippet'"}), 400

        raw_reference = data.get("reference")
        translation = data.get("translation", "KJV")
        if not raw_reference:
            return jsonify({"error": "Missing required field: 'reference'"}), 400

        if input_type == "verse":
            from dspy_programs.contextual_insights_program import normalize_reference
            reference = normalize_reference(raw_reference)
            # Fallback: if normalization fails, try local parser
            if reference.strip().lower() == raw_reference.strip().lower() or not parse_reference(reference):
                logger.warning(f"[get_contextual_insights] AI normalization failed or returned unchanged: {reference}. Trying local parser.")
                parsed = parse_reference(raw_reference)
                if parsed:
                    book, chapter, verse, _ = parsed
                    reference = f"{book} {chapter}:{verse}"
                else:
                    logger.error(f"[get_contextual_insights] Could not normalize reference: {raw_reference}")
                    return jsonify({"error": f"Could not normalize reference '{raw_reference}'. Please check your input or try a different format."}), 400
        else:
            reference = raw_reference

        logger.info(f"Generating insights for {input_type}: {reference}")
        start_time = datetime.datetime.now()

        try:
            insights_result = generate_insights(input_type, reference, translation)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            return jsonify({"error": str(e)}), 500

        if isinstance(insights_result, dict) and "theological_terms" in insights_result and isinstance(insights_result["theological_terms"], list):
            logger.warning("Correcting 'theological_terms' from list to dict.")
            insights_result["theological_terms"] = {}

        end_time = datetime.datetime.now()
        response = {
            "input": {
                "type": input_type,
                "reference": reference,
                "translation": translation
            },
            "insights": insights_result,
            "processing_time_seconds": (end_time - start_time).total_seconds()
        }
        logger.info("Response JSON:\n%s", json.dumps(response, indent=2, ensure_ascii=False))
        return jsonify(response)
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return jsonify({"error": str(e)}), 500

@contextual_insights_api.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    print('*** [DEBUG] Starting contextual_insights_api.py as __main__ ***')
    app = Flask(__name__)
    app.config['CACHE_TYPE'] = 'SimpleCache'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300
    cache = Cache(app)
    @app.route('/health', methods=['GET'])
    def health():
        return {'status': 'ok'}
    app.run(debug=True) 