# APIs

A monorepo of Python FastAPI projects — from a reusable production starter template to a domain-specific bioinformatics service.

## Projects

### [`template/`](./template/README.md) — FastAPI Starter Template

A production-minded, reusable FastAPI starter kit designed to bootstrap new API services with minimal setup. Copy the folder, rename a few values, and start building.

**Highlights:**

- Multi-file app architecture following FastAPI's "bigger applications" pattern
- Versioned routing (`/api/v1`), health & readiness endpoints
- Centralized error handling, structured logging, CORS middleware
- API key security example with `X-API-Key` dependency injection
- In-memory CRUD example for `items` (swap in a real DB when ready)
- Pydantic v2 schemas for all request and response shapes
- Docker + Docker Compose setup with proper layer caching
- Full test suite (`pytest` + `httpx`) with 89% coverage
- Code quality tooling: `ruff`, `black`, `mypy`
- Render deployment blueprint (`render.yaml`)
- Helper scripts in `scripts/` for dev, test, lint, format, and Docker

📖 [Read the template README →](./template/README.md)

### [`bioAPI/`](./bioAPI/README.md) — Bioinformatics REST API

A production-ready FastAPI service for common bioinformatics workflows. Handles file parsing, sequence manipulation, format conversions, and mutation-aware consensus generation — natively in Python via Biopython.

**Highlights:**

- **Sequence Utilities**: reverse complement, transcribe, translate, GC content, k-mers, motif search
- **File Statistics**: upload `FASTA`, `FASTQ`, `GenBank`, `BAM`, `VCF`, `GFF/GTF` and get rich metadata
- **Cross-file Extraction**: GFF + FASTA overlay to slice genomic features by coordinates
- **VCF Support**: extract SNPs/INDELs, or inject variants into a reference FASTA for consensus generation
- **Format Conversion**: convert between standard bioinformatics file types
- Dockerized with `pysam` C-binding support, CORS, API key auth
- Auto-generated Swagger UI at `/docs` and ReDoc at `/redoc`

📖 [Read the bioAPI README →](./bioAPI/README.md)

## Tech Stack

| Tool | Purpose |
|---|---|
| [FastAPI](https://fastapi.tiangolo.com/) | Web framework & OpenAPI docs |
| [Pydantic v2](https://docs.pydantic.dev/) | Data validation & settings |
| [Uvicorn](https://www.uvicorn.org/) | ASGI server |
| [Biopython](https://biopython.org/) | Bioinformatics operations (bioAPI) |
| [pytest](https://pytest.org/) | Testing |
| [ruff](https://docs.astral.sh/ruff/) | Linting |
| [black](https://black.readthedocs.io/) | Formatting |
| [mypy](https://mypy-lang.org/) | Static type checking |
| [Docker](https://www.docker.com/) | Containerization |
