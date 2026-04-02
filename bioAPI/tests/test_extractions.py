import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
import os
import tempfile

from app.main import app

@pytest.fixture
def anyio_backend():
    return "asyncio"

@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client

@pytest.fixture
def mock_fasta_file():
    fd, path = tempfile.mkstemp(suffix=".fasta")
    content = b">chr1\nATGCATGCATGCATGC\n"
    os.write(fd, content)
    os.close(fd)
    yield path
    os.remove(path)

@pytest.fixture
def mock_gff_file():
    fd, path = tempfile.mkstemp(suffix=".gff")
    content = b"##gff\nchr1\t.\tgene\t1\t4\t.\t+\t.\tID=1\nchr1\t.\tgene\t5\t8\t.\t-\t.\tID=2\n"
    os.write(fd, content)
    os.close(fd)
    yield path
    os.remove(path)

@pytest.fixture
def mock_vcf_file():
    fd, path = tempfile.mkstemp(suffix=".vcf")
    # Simple VCF: Two variants on chr1. Position 1 (A->T SNP), Position 5 (A->AAA Indel)
    content = b'##fileformat=VCFv4.2\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\nchr1\t1\t.\tA\tT\t.\tPASS\t.\nchr1\t5\t.\tT\tTAA\t.\tPASS\t.\n'
    os.write(fd, content)
    os.close(fd)
    yield path
    os.remove(path)

@pytest.mark.asyncio
async def test_extract_gff(async_client: AsyncClient, mock_fasta_file, mock_gff_file):
    with open(mock_fasta_file, 'rb') as fa, open(mock_gff_file, 'rb') as gff:
        files = {
            'fasta_file': ('ref.fasta', fa, 'text/plain'),
            'gff_file': ('annot.gff', gff, 'text/plain')
        }
        res = await async_client.post("/api/v1/files/extract-gff", files=files, data={'feature_type': 'gene'})
        assert res.status_code == 200
        content = res.content.decode()
        assert "chr1_1_4_gene" in content
        # chr1 1->4 is ATGC
        assert "ATGC" in content
        assert "chr1_5_8_gene" in content

@pytest.mark.asyncio
async def test_extract_vcf_variants(async_client: AsyncClient, mock_vcf_file):
    with open(mock_vcf_file, 'rb') as vcf:
        files = {'vcf_file': ('mutations.vcf', vcf, 'text/plain')}
        res = await async_client.post("/api/v1/files/vcf/extract", files=files, data={'variant_type': 'ALL'})
        assert res.status_code == 200
        data = res.json()["data"]
        assert len(data) == 2
        assert data[0]["type"] == "SNP"
        assert data[1]["type"] == "INDEL"

@pytest.mark.asyncio
async def test_vcf_to_fasta_consensus(async_client: AsyncClient, mock_fasta_file, mock_vcf_file):
    with open(mock_fasta_file, 'rb') as fa, open(mock_vcf_file, 'rb') as vcf:
        files = {
            'reference_fasta': ('ref.fasta', fa, 'text/plain'),
            'vcf_file': ('mutations.vcf', vcf, 'text/plain')
        }
        res = await async_client.post("/api/v1/conversions/vcf-to-fasta", files=files)
        assert res.status_code == 200
        content = res.content.decode()
        assert ">chr1_consensus" in content
        assert "TTGC" in content 
