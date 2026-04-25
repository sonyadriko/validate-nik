import pytest
from fastapi.testclient import TestClient
from dotenv import load_dotenv
import os

load_dotenv()

# Use a test API key (add to .env for local testing)
TEST_API_KEY = os.getenv("API_KEYS", "test-key").split(",")[0].strip()

# Import will be updated after main.py is created
# from main import app

def test_parse_nik_valid():
    from main import app
    client = TestClient(app)
    response = client.get(f"/api/v1/parse?nik=3201010101010001", headers={"X-API-Key": TEST_API_KEY})
    assert response.status_code == 200
    data = response.json()
    assert data["nik"] == "3201010101010001"
    assert data["kelamin"] == "LAKI-LAKI"
    assert "provinsi" in data

def test_parse_nik_invalid_length():
    from main import app
    client = TestClient(app)
    response = client.get(f"/api/v1/parse?nik=123", headers={"X-API-Key": TEST_API_KEY})
    assert response.status_code == 422  # Validation error

def test_parse_nik_missing_param():
    from main import app
    client = TestClient(app)
    response = client.get("/api/v1/parse", headers={"X-API-Key": TEST_API_KEY})
    assert response.status_code == 422  # Validation error

def test_health_check():
    from main import app
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "validasi-nik"}

def test_parse_nik_no_api_key():
    """Request without API key should return 401"""
    from main import app
    client = TestClient(app)
    response = client.get("/api/v1/parse?nik=3201010101010001")
    assert response.status_code == 401
    assert response.json()["error"] == "Unauthorized"

def test_parse_nik_invalid_api_key():
    """Request with invalid API key should return 401 when keys are configured"""
    from main import app
    client = TestClient(app)
    # Only test if keys are actually configured
    if os.getenv("API_KEYS"):
        response = client.get("/api/v1/parse?nik=3201010101010001", headers={"X-API-Key": "wrong-key"})
        assert response.status_code == 401
        assert response.json()["error"] == "Unauthorized"
