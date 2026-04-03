import time
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.errors import (
    BioFastAPIError,
    custom_http_exception_handler,
    validation_exception_handler,
    biofast_exception_handler,
    global_exception_handler,
)
from app.api.routers import health, sequences, files, conversions
from app.api.routers.fasta_utils import fasta_router, fastq_router

# Initialize FastAPI App
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    description="A production-ready FastAPI project for bioinformatics utility workflows.",
)

# Exception Handlers
app.add_exception_handler(StarletteHTTPException, custom_http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(BioFastAPIError, biofast_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Middlewares
# CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Gzip
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Request ID & Logging Middleware
@app.middleware("http")
async def add_request_id_and_log(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    start_time = time.time()
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = request_id
        return response
    except Exception as e:
        # We let the exception handlers catch it, but we could log it here
        raise e

# Include Routers
app.include_router(health.router)
app.include_router(sequences.router, prefix=settings.API_V1_STR)
app.include_router(files.router, prefix=settings.API_V1_STR)
app.include_router(conversions.router, prefix=settings.API_V1_STR)
app.include_router(fasta_router, prefix=settings.API_V1_STR)
app.include_router(fastq_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
