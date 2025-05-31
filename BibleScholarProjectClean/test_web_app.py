import pytest
from web_app import app
import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_skills_page(client):
    response = client.get('/skills')
    assert response.status_code == 200
    assert b'Skill Tracker' in response.data
    assert b'terminal_basics' in response.data or b'Terminal Basics' in response.data

def test_skills_advice(client, monkeypatch):
    # Patch query_lm_studio to avoid real LM Studio call
    from web_app import query_lm_studio
    monkeypatch.setattr('web_app.query_lm_studio', lambda prompt, **kwargs: {'summary': 'Test advice'})
    response = client.post('/skills/advice')
    assert response.status_code == 200
    assert b'Coach Advice' in response.data
    assert b'Test advice' in response.data 