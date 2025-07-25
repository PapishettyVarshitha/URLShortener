import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))
from main import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    return app.test_client()

def test_shorten_valid_url(client):
    response = client.post("/api/shorten", json={"url": "https://example.com"})
    data = response.get_json()
    assert response.status_code == 200
    assert "short_code" in data
    assert "short_url" in data

def test_shorten_invalid_url(client):
    response = client.post("/api/shorten", json={"url": "invalid-url"})
    assert response.status_code == 400

def test_shorten_missing_url(client):
    response = client.post("/api/shorten", json={})
    assert response.status_code == 400

def test_redirect_and_stats(client):
    # First shorten a URL
    response = client.post("/api/shorten", json={"url": "https://google.com"})
    data = response.get_json()
    short_code = data["short_code"]

    # Test redirect
    redirect_response = client.get(f"/{short_code}", follow_redirects=False)
    assert redirect_response.status_code == 302  # should redirect

    # Test stats
    stats_response = client.get(f"/api/stats/{short_code}")
    stats_data = stats_response.get_json()
    assert stats_response.status_code == 200
    assert stats_data["url"] == "https://google.com"
    assert stats_data["clicks"] >= 1

def test_stats_not_found(client):
    response = client.get("/api/stats/unknownCode")
    assert response.status_code == 404
