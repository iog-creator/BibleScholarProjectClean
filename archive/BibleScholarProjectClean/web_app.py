from flask import Flask, flash, render_template, request, redirect, url_for, session
from flask_caching import Cache
import os
import logging
import json
from src.dspy_programs.contextual_insights_program import query_lm_studio

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure value in production

# Add caching config if not present
if not hasattr(app, 'cache'):
    app.config['CACHE_TYPE'] = 'SimpleCache'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300
    cache = Cache(app)
else:
    cache = app.cache

API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000')

@app.route('/contextual-insights', methods=['GET', 'POST'])
def contextual_insights():
    if request.method == 'POST':
        return redirect(url_for('search_insights'))
    input_data = session.pop('input_data', None)
    insights = session.pop('insights', None)
    error = session.pop('error', None)
    return render_template('contextual_insights.html', input_data=input_data, insights=insights, error=error)

@app.route('/search', methods=['GET', 'POST'])
@cache.cached(timeout=300, query_string=True)
def search_insights():
    if request.method == 'POST':
        query = request.form.get('query')
        if not query:
            flash("Please enter a search query.", "danger")
            session['input_data'] = None
            session['insights'] = None
            session['error'] = "No query provided"
            return redirect(url_for('search_insights'))
        input_data = {'type': 'text_snippet', 'text': query, 'translation': 'KJV'}
        try:
            import requests
            resp = requests.post(f"{API_BASE_URL}/api/contextual_insights/insights", json=input_data, timeout=120)
            if resp.status_code == 200:
                response = resp.json()
                if response and 'insights' in response:
                    session['input_data'] = input_data
                    session['insights'] = response['insights']
                    session['error'] = None
                else:
                    session['input_data'] = input_data
                    session['insights'] = None
                    session['error'] = "Invalid API response format"
                    flash("Invalid API response format", "danger")
            else:
                session['input_data'] = input_data
                session['insights'] = None
                session['error'] = f"API error: {resp.status_code} - {resp.text}"
                flash(f"API error: {resp.status_code} - {resp.text}", "danger")
        except Exception as e:
            session['input_data'] = input_data
            session['insights'] = None
            session['error'] = f"Error connecting to Contextual Insights API: {e}"
            flash(f"Error connecting to Contextual Insights API: {e}", "danger")
        return redirect(url_for('search_insights'))
    input_data = session.pop('input_data', None)
    insights = session.pop('insights', None)
    error = session.pop('error', None)
    return render_template('contextual_insights.html', input_data=input_data, insights=insights, error=error)

@app.route('/health', methods=['GET'])
def health():
    return {'status': 'ok'}

@app.route('/skills', methods=['GET'])
def skills_page():
    try:
        with open('user_skills.json') as f:
            skills = json.load(f)
    except Exception as e:
        logging.error(f"Error loading user skills: {e}")
        skills = {}
    return render_template('skills.html', skills=skills)

@app.route('/skills/advice', methods=['POST'])
def skills_advice():
    try:
        with open('user_skills.json') as f:
            skills = json.load(f)
    except Exception as e:
        logging.error(f"Error loading user skills: {e}")
        skills = {}
    # Compose a prompt for LM Studio
    prompt = (
        "You are a programming coach. Here is my current skill progress as JSON: "
        f"{json.dumps(skills)}\n"
        "Please give me personalized advice, next steps, or a challenge to help me level up. "
        "Be specific and encouraging."
    )
    advice = query_lm_studio(prompt, max_tokens=512, mode="coach")
    # advice may be a dict or string; handle both
    advice_text = advice.get('summary') if isinstance(advice, dict) and 'summary' in advice else str(advice)
    return render_template('skills.html', skills=skills, advice=advice_text)

if __name__ == "__main__":
    try:
        logger.info("Starting Web UI Server on port 5001...")
        app.run(host="0.0.0.0", port=5001, debug=True)
        logger.info("Web UI Server running successfully.")
    except Exception as e:
        logger.error(f"Failed to start Web UI Server: {str(e)}")
        raise 