from fastapi import APIRouter, UploadFile, File, Query, Depends, BackgroundTasks
import tempfile
import os
from fastapi.responses import FileResponse
from app.api.deps import get_api_key, rate_limit_placeholder
from app.schemas.conversion import SupportedSourceFormat, SupportedTargetFormat
from app.services.conversion_service import ConversionService
from app.core.config import settings
from app.core.errors import BioFastAPIError
import starlette.background

router = APIRouter(
    prefix="/conversions",
    tags=["Conversions"],
    dependencies=[Depends(get_api_key), Depends(rate_limit_placeholder)]
)

def cleanup_temp_file(filepath: str):
    import os
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
        except Exception:
            pass

@router.post("/convert")
async def convert_file(
    source_format: SupportedSourceFormat = Query(..., description="Format of the uploaded file"),
    target_format: SupportedTargetFormat = Query(..., description="Desired output format"),
    file: UploadFile = File(...)
):
    """
    Convert a biological sequence file between formats.
    Returns the converted file.
    """
    # Naive size check
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    if size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise BioFastAPIError(message="File exceeds maximum allowed size.")

    out_path, result = await ConversionService.convert(file, source_format, target_format)
    
    # We use a background task to clean up the temporary file after it has been sent
    tasks = starlette.background.BackgroundTask(cleanup_temp_file, filepath=out_path)
    
    return FileResponse(
        path=out_path, 
        filename=result.filename,
        media_type="application/octet-stream",
        background=tasks,
        headers={
            "X-Records-Converted": str(result.records_converted),
            "X-Conversion-Warnings": str(len(result.warnings))
        }
    )

@router.post("/vcf-to-fasta")
async def convert_vcf_to_fasta(
    background_tasks: BackgroundTasks,
    reference_fasta: UploadFile = File(...),
    vcf_file: UploadFile = File(...)
):
    """Derive a mutant consensus sequence FASTA substituting ALT alleles across VCF loci."""
    reference_fasta.file.seek(0, 2)
    s1 = reference_fasta.file.tell()
    reference_fasta.file.seek(0)
    vcf_file.file.seek(0, 2)
    s2 = vcf_file.file.tell()
    vcf_file.file.seek(0)
    
    max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if s1 > max_size or s2 > max_size:
        raise BioFastAPIError(message="Files exceed maximum allowed size.")

    fd_fa, fa_path = tempfile.mkstemp(suffix=".fasta")
    fd_vcf, vcf_path = tempfile.mkstemp(suffix=".vcf")
    out_fd, out_path = tempfile.mkstemp(suffix=".fasta")
    os.close(out_fd)

    try:
        with os.fdopen(fd_fa, 'wb') as f:
            while c := await reference_fasta.read(1024*1024): f.write(c)
        with os.fdopen(fd_vcf, 'wb') as f:
            while c := await vcf_file.read(1024*1024): f.write(c)
            
        records = ConversionService.derive_consensus_sequence(fa_path, vcf_path, out_path)
        
        background_tasks.add_task(cleanup_temp_file, filepath=fa_path)
        background_tasks.add_task(cleanup_temp_file, filepath=vcf_path)
        background_tasks.add_task(cleanup_temp_file, filepath=out_path)
        
        return FileResponse(
            path=out_path, 
            filename="consensus.fasta",
            media_type="text/plain",
            headers={"X-Records-Converted": str(records)}
        )
    except Exception as e:
        cleanup_temp_file(fa_path)
        cleanup_temp_file(vcf_path)
        cleanup_temp_file(out_path)
        raise BioFastAPIError(message=f"Failed to generate consensus string: {str(e)}")
