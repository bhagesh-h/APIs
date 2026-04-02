import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_upload_text_file(async_client: AsyncClient):
    file_content = b"ATGC\nCGTA\n"
    files = {'file': ('test.txt', file_content, 'text/plain')}
    
    response = await async_client.post(
        "/api/v1/files/stats",
        files=files
    )
    assert response.status_code == 200
    assert response.json()["data"]["format"]["detected_format"] == "text"
    assert response.json()["data"]["lines"] == 2

@pytest.mark.asyncio
async def test_upload_gff_file(async_client: AsyncClient):
    file_content = b"##gff-version 3\n#comment\nchr1\t.\tgene\t100\t200\t.\t+\t.\tID=1\nchr1\t.\texon\t100\t150\t.\t+\t.\tID=2\n"
    files = {'file': ('test.gff', file_content, 'text/plain')}
    
    response = await async_client.post(
        "/api/v1/files/stats",
        files=files
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["format"]["detected_format"] == "gff"
    assert data["gff_stats"]["total_features"] == 2
    assert data["gff_stats"]["feature_counts"]["gene"] == 1
    assert data["gff_stats"]["feature_counts"]["exon"] == 1

@pytest.mark.asyncio
async def test_upload_string_format(async_client: AsyncClient):
    file_content = b"random string content\n"
    files = {'file': ('test.string', file_content, 'text/plain')}
    
    response = await async_client.post(
        "/api/v1/files/stats",
        files=files
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["format"]["detected_format"] == "string"
    assert data["lines"] == 1

