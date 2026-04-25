import pytest
from fastapi.testclient import TestClient
from dotenv import load_dotenv
import os

load_dotenv()

# Use a test API key (add to .env for local testing)
TEST_API_KEY = os.getenv("API_KEYS", "test-key").split(",")[0].strip()

def test_health_check_bypass():
    """Health check should not require API key"""
    from main import app
    client = TestClient(app)

    response = client.get("/api/v1/health")
    assert response.status_code == 200

def test_api_key_required():
    """API key always required in header"""
    from main import app
    client = TestClient(app)

    # Without key -> 401
    response = client.get("/api/v1/parse?nik=3201010101010001")
    assert response.status_code == 401

    # With valid key -> 200
    response = client.get("/api/v1/parse?nik=3201010101010001", headers={"X-API-Key": TEST_API_KEY})
    assert response.status_code == 200

def test_docs_bypass_auth():
    """Docs endpoints should bypass auth"""
    from main import app
    client = TestClient(app)

    response = client.get("/docs")
    assert response.status_code == 200

    response = client.get("/redoc")
    assert response.status_code == 200

    response = client.get("/")
    assert response.status_code == 200
