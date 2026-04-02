import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings

client = TestClient(app)
prefix = settings.API_V1_PREFIX + "/items"


@pytest.fixture
def test_item_payload() -> dict[str, str]:
    return {
        "name": "Test Item",
        "description": "A highly specialized test item."
    }


def test_create_item(test_item_payload: dict[str, str]) -> None:
    response = client.post(f"{prefix}/", json=test_item_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == test_item_payload["name"]
    assert "id" in data


def test_list_items(test_item_payload: dict[str, str]) -> None:
    client.post(f"{prefix}/", json=test_item_payload)
    response = client.get(f"{prefix}/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_item(test_item_payload: dict[str, str]) -> None:
    create_response = client.post(f"{prefix}/", json=test_item_payload)
    item_id = create_response.json()["id"]
    response = client.get(f"{prefix}/{item_id}")
    assert response.status_code == 200
    assert response.json()["id"] == item_id


def test_get_nonexistent_item() -> None:
    response = client.get(f"{prefix}/999999")
    assert response.status_code == 404


def test_update_item(test_item_payload: dict[str, str]) -> None:
    create_response = client.post(f"{prefix}/", json=test_item_payload)
    item_id = create_response.json()["id"]
    update_payload = {"name": "Updated Name"}
    response = client.put(f"{prefix}/{item_id}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Name"
    # Ensure description remains consistent on partial update model
    assert response.json()["description"] == test_item_payload["description"]


def test_delete_item(test_item_payload: dict[str, str]) -> None:
    create_response = client.post(f"{prefix}/", json=test_item_payload)
    item_id = create_response.json()["id"]
    response = client.delete(f"{prefix}/{item_id}")
    assert response.status_code == 204
    get_response = client.get(f"{prefix}/{item_id}")
    assert get_response.status_code == 404
