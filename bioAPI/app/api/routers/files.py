from typing import Optional
import tempfile
import os
from fastapi import APIRouter, UploadFile, File, Depends, Form, BackgroundTasks
from fastapi.responses import FileResponse
from app.api.deps import get_api_key, rate_limit_placeholder
from app.schemas.common import EnvelopeResponse
from app.schemas.file_stats import FileStatsResponse
from app.services.file_service import FileService
from app.core.config import settings
from app.core.errors import BioFastAPIError

router = APIRouter(
    prefix="/files",
    tags=["Files"],
    dependencies=[Depends(get_api_key), Depends(rate_limit_placeholder)]
)

async def validate_file_size(file: UploadFile):
    # This is a naive check; real deployments usually handle this in Nginx/FastAPI middleware globally
    file.file.seek(0, 2)
    size = file.file.tell()
    file.file.seek(0)
    max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if size > max_size:
        raise BioFastAPIError(message=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB}MB.")
    return file

@router.post("/stats", response_model=EnvelopeResponse[FileStatsResponse])
async def analyze_file_stats(file: UploadFile = File(...)):
    """Analyze an uploaded bioinformatics file (FASTA, FASTQ, GenBank, Text) and return detailed statistics."""
    await validate_file_size(file)
    stats = await FileService.analyze_file(file)
    return EnvelopeResponse(success=True, data=stats)

@router.post("/summary", response_model=EnvelopeResponse[FileStatsResponse])
async def analyze_file_summary(file: UploadFile = File(...)):
    """Alias for /stats, summarizes sequence file contents."""
    await validate_file_size(file)
    stats = await FileService.analyze_file(file)
    return EnvelopeResponse(success=True, data=stats)

def remove_tmp_file(path: str):
    if os.path.exists(path):
        os.remove(path)

@router.post("/extract-gff", response_class=FileResponse)
async def extract_gff(
    background_tasks: BackgroundTasks,
    fasta_file: UploadFile = File(...),
    gff_file: UploadFile = File(...),
    feature_type: Optional[str] = Form(None)
):
    """Extract FASTA sequences dynamically by overlaying GFF coordinates."""
    await validate_file_size(fasta_file)
    await validate_file_size(gff_file)

    fd_fa, fa_path = tempfile.mkstemp(suffix=".fasta")
    fd_gff, gff_path = tempfile.mkstemp(suffix=".gff")
    out_fd, out_path = tempfile.mkstemp(suffix=".fasta")
    os.close(out_fd)

    try:
        with os.fdopen(fd_fa, 'wb') as f:
            while c := await fasta_file.read(1024*1024): f.write(c)
        with os.fdopen(fd_gff, 'wb') as f:
            while c := await gff_file.read(1024*1024): f.write(c)
                
        fasta_str = FileService.extract_gff_features(fa_path, gff_path, feature_type)
        with open(out_path, 'w') as f:
            f.write(fasta_str)
            
        background_tasks.add_task(remove_tmp_file, fa_path)
        background_tasks.add_task(remove_tmp_file, gff_path)
        background_tasks.add_task(remove_tmp_file, out_path)
        
        return FileResponse(out_path, media_type="text/plain", filename="extracted_features.fasta")
    except Exception as e:
        remove_tmp_file(fa_path)
        remove_tmp_file(gff_path)
        remove_tmp_file(out_path)
        raise BioFastAPIError(message=f"Extraction failed: {str(e)}")

@router.post("/vcf/extract", response_model=EnvelopeResponse[list])
async def extract_vcf_variants(
    vcf_file: UploadFile = File(...),
    variant_type: str = Form("ALL")
):
    """Extract list of specific variants (SNP, INDEL, ALL) natively from a VCF using pysam."""
    await validate_file_size(vcf_file)
    fd, vcf_path = tempfile.mkstemp(suffix=".vcf")
    try:
        with os.fdopen(fd, 'wb') as f:
            while c := await vcf_file.read(1024*1024):
                f.write(c)
                
        variants = FileService.extract_vcf_variants(vcf_path, variant_type)
        return EnvelopeResponse(success=True, data=variants)
    except Exception as e:
        raise BioFastAPIError(message=f"Extraction failed: {str(e)}")
    finally:
        remove_tmp_file(vcf_path)
