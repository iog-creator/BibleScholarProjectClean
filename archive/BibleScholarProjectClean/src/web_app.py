import logging
import sys
import requests
from flask import render_template, request

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/web_app.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('web_app')

@app.route('/contextual-insights', methods=['GET', 'POST'])
def contextual_insights_page():
    """
    Contextual Insights UI: Accepts user input (verse, topic, or text snippet), fetches insights from the API, and displays all fields including original_language_words.
    Teaching Mode: Only the 'insights' field from the API response should be passed to the template, not the full API response. This prevents UI parsing issues and ensures the template always receives the expected structure.
    """
    insights = None
    error = None
    input_data = None
    if request.method == 'POST':
        focus_type = request.form.get('focus_type')
        reference = request.form.get('reference')
        topic = request.form.get('topic')
        snippet = request.form.get('snippet')
        input_data = {'type': focus_type}
        if focus_type == 'verse':
            input_data['reference'] = reference
        elif focus_type == 'topic':
            input_data['query_text'] = topic
        elif focus_type == 'text_snippet':
            input_data['text'] = snippet
        logger.info(f"[UI] POST /contextual-insights input_data: {input_data}")
        try:
            api_url = f"{CI_API_URL}/api/contextual_insights/insights"
            resp = requests.post(api_url, json=input_data, timeout=120)
            logger.info(f"[UI] API POST {api_url} status: {resp.status_code}")
            logger.info(f"[UI] API response: {resp.text[:500]}")
            if resp.status_code == 200:
                api_response = resp.json()
                # Robustly extract only the 'insights' field for the template
                if isinstance(api_response, dict) and 'insights' in api_response and isinstance(api_response['insights'], dict):
                    insights = api_response['insights']
                else:
                    error = "Malformed API response: missing or invalid 'insights' field."
                    logger.error(error)
                    insights = {}
            else:
                error = f"API error: {resp.status_code} - {resp.text}"
                logger.error(error)
                insights = {}
        except Exception as e:
            error = f"Error connecting to Contextual Insights API: {e}"
            logger.error(error)
            insights = {}
    try:
        return render_template('contextual_insights.html', insights=insights, error=error, input_data=input_data)
    except Exception as e:
        import traceback
        print('Error rendering contextual_insights.html:', e)
        print(traceback.format_exc())
        return f"Error rendering contextual_insights.html: {e}", 500

if __name__ == "__main__":
    try:
        logger.info("Starting Web UI Server on port 5001...")
        app.run(host="0.0.0.0", port=5001, debug=True)
        logger.info("Web UI Server running successfully.")
    except Exception as e:
        logger.error(f"Failed to start Web UI Server: {str(e)}")
        raise 