import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings

client = TestClient(app)
prefix = settings.API_V1_PREFIX + "/examples"

def test_ping() -> None:
    response = client.get(f"{prefix}/ping")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}

def test_protected_endpoint_unauthorized() -> None:
    response = client.get(f"{prefix}/protected")
    assert response.status_code == 403
    data = response.json()
    # Our centralized error handler returns {"error": ..., "message": ...}
    assert "error" in data
    assert "message" in data

def test_protected_endpoint_authorized() -> None:
    headers = {"X-API-Key": settings.API_KEY}
    response = client.get(f"{prefix}/protected", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"message": "You have successfully accessed a protected endpoint!"}

def test_protected_endpoint_wrong_key() -> None:
    headers = {"X-API-Key": "wrong_key_here"}
    response = client.get(f"{prefix}/protected", headers=headers)
    assert response.status_code == 403
