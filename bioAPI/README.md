# bioAPI

A production-ready Python FastAPI project for bioinformatics utility workflows. Provides a fast, scalable REST API for sequence manipulation, file statistics, and format conversions using Biopython and FastAPI.

![Tests](https://img.shields.io/badge/tests-passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-teal.svg)

## Overview

`bioAPI` was built to provide a modern, strongly-typed backend for common bioinformatics tasks. It leverages Pydantic for rigorous validation and FastAPI's dependency injection to maintain a clean architecture.

## Features

- **Sequence Utilities**: Reverse complement, transcribe, translate, GC-content, k-mer counts, motif searching.
- **File Statistics**: Upload `FASTA`, `FASTQ`, `GenBank`, `BAM`, `VCF`, `GFF`, `GTF` or raw `String` files and get rich internal metadata (GC counts, read mapping scores, or precise feature aggregation).
- **Advanced Extractions**: Filter features dynamically across formats using `GFF+FASTA` overlay extractions, or isolate selective mutations via `VCF` endpoints.
- **Conversions & Consensus**: Convert between standard formats, or inject `VCF` alterations into a reference `FASTA` to derive a mutated consensus genome entirely natively.
- **Production Ready**: Dockerized, CORS enabled, typed, linted, and tested.
- **Self-Documenting**: Auto-generated Swagger UI and ReDoc.

## API Endpoints

| Category | Endpoint | Method | Description |
| --- | --- | --- | --- |
| Health | `/` | GET | Welcome and metadata |
| Health | `/health` | GET | Simple health check |
| Health | `/ready` | GET | Readiness check |
| Health | `/version` | GET | Version metadata |
| Sequences | `/api/v1/sequences/reverse` | POST | Reverse a sequence |
| Sequences | `/api/v1/sequences/complement` | POST | Complement a sequence |
| Sequences | `/api/v1/sequences/reverse-complement` | POST | Reverse-complement |
| Sequences | `/api/v1/sequences/transcribe` | POST | DNA to RNA |
| Sequences | `/api/v1/sequences/back-transcribe` | POST | RNA to DNA |
| Sequences | `/api/v1/sequences/translate` | POST | Nucleotide to protein |
| Sequences | `/api/v1/sequences/gc-content` | POST | Calulate GC content |
| Sequences | `/api/v1/sequences/count-bases` | POST | Count nucleotide/amino acid frequencies |
| Sequences | `/api/v1/sequences/kmer` | POST | K-mer frequency counting |
| Sequences | `/api/v1/sequences/find-motif` | POST | Search for substrings |
| Sequences | `/api/v1/sequences/validate` | POST | Validate against an alphabet |
| Files | `/api/v1/files/stats` | POST | Upload file and get rich bio-stats |
| Files | `/api/v1/files/summary` | POST | Alias for /stats |
| Files | `/api/v1/files/extract-gff` | POST | Extract sliced FASTA targets via GFF bounds |
| Files | `/api/v1/files/vcf/extract` | POST | Isolate SNPs/INDELs explicitly from a VCF |
| Conversions | `/api/v1/conversions/convert` | POST | Upload file and convert format |
| Conversions | `/api/v1/conversions/vcf-to-fasta` | POST | Mutatable consensus FASTA derivations |

## Project Structure

```text
bioAPI/
├── app/
│   ├── main.py                 # FastAPI entrypoint
│   ├── core/                   # App config, constants, error handlers
│   ├── api/                    # Routers and Dependencies
│   ├── schemas/                # Pydantic models (Input/Output)
│   ├── services/               # Core business logic / Biopython ops
│   └── utils/                  # Helper functions and validators
├── tests/                      # Pytest suite
├── .env.example
├── Dockerfile
├── Makefile
├── README.md
├── requirements.txt
└── requirements-dev.txt
```

## Local Setup & Development

### 1. Requirements

Ensure you have Python 3.11+ installed.

### 2. Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate (Linux/macOS)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

### 4. Configuration

Copy the `.env.example` file to create your local config.

```bash
cp .env.example .env
```

### 5. Run Server

Run the dev server using Uvicorn directly or via Makefile.

```bash
# Using Makefile
make dev

# Or directly
uvicorn app.main:app --reload
```

Access the documentation at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

### 6. Testing & Quality

We use `pytest`, `ruff`, `black`, and `mypy` to maintain code health. General commands can be run via the Makefile, however testing components reliant on `pysam` C-bindings should be executed isolated in the Docker container to ensure exact platform compatibility:

```bash
# Standard local metrics
make test
make lint
make format

# Isolated Docker Test Routine (Recommended)
docker run --rm \
  -e PYTHONPATH=/app \
  -v "$(pwd)/tests:/app/tests" \
  -v "$(pwd)/app:/app/app" \
  bioAPI bash -c "pip install pytest httpx pytest-asyncio && pytest tests/"
```

## Example Usage

### cURL Examples

**1. Root Endpoint**

```bash
curl http://127.0.0.1:8000/
```

**2. Reverse Complement (JSON)**

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/sequences/reverse-complement" \
  -H "Content-Type: application/json" \
  -d '{"sequence":"ATGCGTAA","alphabet":"dna"}'
```

**3. Upload File for Statistics**

*FASTA Output:*

```bash
echo -e ">seq1\nATGC\n>seq2\nCGTA" > example.fasta
curl -X POST "http://127.0.0.1:8000/api/v1/files/stats" \
  -F "file=@example.fasta"
```

*BAM Output:*

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/files/stats" \
  -F "file=@sample.bam"
```

*GFF Output:*

```bash
echo -e "chr1\t.\tgene\t100\t200\t.\t+\t.\tID=1" > test.gff
curl -X POST "http://127.0.0.1:8000/api/v1/files/stats" \
  -F "file=@test.gff"
```

**4. Convert Format**

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/conversions/convert?source_format=text&target_format=fasta" \
  -F "file=@example.txt" \
  -o converted.fasta
```

**5. Extract VCF Variants**

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/files/vcf/extract" \
  -F "vcf_file=@mutations.vcf" \
  -F "variant_type=SNP"
```

**6. Generate Consensus FASTA from VCF**

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/conversions/vcf-to-fasta" \
  -F "reference_fasta=@ref.fasta" \
  -F "vcf_file=@mutations.vcf" \
  -o derived_mutant.fasta
```

**7. Extract GFF Features from Reference**

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/files/extract-gff" \
  -F "fasta_file=@genome.fasta" \
  -F "gff_file=@annotations.gff" \
  -F "feature_type=gene" \
  -o extracted_genes.fasta
```

### Postman Examples

To interact with the sequence endpoints via Postman:

1. **Method**: `POST`
2. **URL**: `http://127.0.0.1:8000/api/v1/sequences/kmer`
3. **Headers**: `Content-Type: application/json`
4. **Body Type**: `raw`
5. **Payload**:

```json
{
  "sequence": "ACTGACGACTGA",
  "k": 3
}
```

To interact with file upload endpoints via Postman:

1. **Method**: `POST`
2. **URL**: `http://127.0.0.1:8000/api/v1/files/stats`
3. **Body Type**: `form-data`
4. **Key**: `file` (Change the type of the key from 'Text' to 'File')
5. **Value**: Select your `.fastq` or `.fasta` file.

## Deployment

### Docker

The application includes a production-ready `Dockerfile`.

```bash
# Build the image
docker build -t bioAPI .

# Run the container
docker run -p 8000:8000 --env-file .env bioAPI
```

### Deploy to Render

Render provides excellent support for FastAPI through native Python environments or Docker.
A `render.yaml` blueprint is included in the directory.

1. Create a GitHub repository and push this code.
2. Log into Render.com and connect your GitHub account.
3. Choose "Blueprints" and select the `render.yaml` file.
4. Render will automatically detect the Python environment, `Requirements.txt`, and Uvicorn start command.
5. The Swagger Docs `/docs` will be publicly available at your `.onrender.com` URL once successfully deployed.

### GitHub Setup Guide

If you haven't initialized Git yet:

```bash
git init
git add .
git commit -m "Initial commit of bioAPI"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/bioAPI.git
git push -u origin main
```

*(You can also set up GitHub Actions later to run tests automatically on push).*

## Security Notes

- If `API_KEY` is set in `.env`, all `/api/v1/` endpoints require the `X-API-Key` header. Health endpoints (`/health`, `/ready`) will remain open so orchestrators/Render can poll them.
- File uploads are capped structurally by the naive size middleware checking `MAX_UPLOAD_SIZE_MB`, but in a true production cluster, enforcing limits at the Nginx ingress or API Gateway is recommended.

## Known Limitations

- The conversion endpoint streams into temporary disk files. For massive datasets (> 500MB), consider queue-based off-loading (e.g., Celery) rather than synchronous REST handling which might timeout.
- Ambiguous FASTQ features might be unparsable strictly depending on the instrument quality offsets.

## Changelog

- **v1.0.0**: Initial release with robust schemas and Biopython integration.
