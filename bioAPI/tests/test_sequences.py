import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_reverse_complement_valid(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/sequences/reverse-complement",
        json={"sequence": "ATGC", "alphabet": "dna"}
    )
    assert response.status_code == 200
    assert response.json()["success"]
    assert response.json()["data"]["result"] == "GCAT"

@pytest.mark.asyncio
async def test_reverse_complement_invalid_chars(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/sequences/reverse-complement",
        json={"sequence": "ATGCXZ", "alphabet": "dna"}
    )
    # Should get 400 Bad Request due to validation
    assert response.status_code == 400
    assert not response.json()["success"]
    assert "Invalid sequence characters" in response.json()["message"]

@pytest.mark.asyncio
async def test_gc_content(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/sequences/gc-content",
        json={"sequence": "ATGCGC"}
    )
    assert response.status_code == 200
    assert response.json()["data"]["gc_percent"] == 66.6667
