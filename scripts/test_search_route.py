import requests
import logging
from logging.handlers import RotatingFileHandler
import tempfile
import os

def get_log_file_handler(log_file_path):
    try:
        return RotatingFileHandler(log_file_path, maxBytes=102400, backupCount=1, encoding='utf-8')
    except PermissionError:
        temp_log = tempfile.NamedTemporaryFile(delete=False, suffix='.log')
        print(f"[WARNING] Log file {log_file_path} is locked. Using temporary log file: {temp_log.name}")
        return RotatingFileHandler(temp_log.name, maxBytes=102400, backupCount=1, encoding='utf-8')

log_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../logs/web_app.log'))
file_handler = get_log_file_handler(log_file_path)
file_handler.setLevel(logging.INFO)
logging.basicConfig(
    level=logging.INFO,
    handlers=[file_handler],
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_search_route():
    # Perform contextual search via POST form
    url = "http://localhost:5001/search"
    form_data = {'query': 'Let there be light'}
    try:
        response = requests.post(url, data=form_data, timeout=120)
        if response.status_code == 200:
            with open("logs/search_test.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            logger.info("Saved /search output to logs/search_test.html")
        else:
            logger.error(f"/search failed: {response.status_code} - {response.text}")
    except Exception as e:
        logger.error(f"/search error: {e}")

if __name__ == "__main__":
    test_search_route() 