import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_convert_text_to_fasta(async_client: AsyncClient):
    file_content = b"ATGC\nCGTA\n"
    files = {'file': ('test.txt', file_content, 'text/plain')}
    
    response = await async_client.post(
        "/api/v1/conversions/convert?source_format=text&target_format=fasta",
        files=files
    )
    assert response.status_code == 200
    assert "application/octet-stream" in response.headers["content-type"]
    assert response.headers["x-records-converted"] == "2"
    
    content = response.content.decode('utf-8')
    assert ">seq_1" in content
    assert "ATGC" in content
