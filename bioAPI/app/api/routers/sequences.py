from fastapi import APIRouter, Depends
from app.api.deps import get_api_key, rate_limit_placeholder
from app.schemas.common import EnvelopeResponse
from app.schemas.sequence import (
    SequenceRequest, SequenceResult, GCContentResult, BaseCountResult,
    TranslationRequest, KmerRequest, KmerResult, MotifRequest, MotifResult, ValidationResult
)
from app.services.sequence_service import SequenceService

router = APIRouter(
    prefix="/sequences",
    tags=["Sequences"],
    dependencies=[Depends(get_api_key), Depends(rate_limit_placeholder)]
)

@router.post("/reverse", response_model=EnvelopeResponse[SequenceResult])
async def reverse_sequence(req: SequenceRequest):
    return EnvelopeResponse(success=True, data=SequenceService.reverse(req))

@router.post("/complement", response_model=EnvelopeResponse[SequenceResult])
async def complement_sequence(req: SequenceRequest):
    return EnvelopeResponse(success=True, data=SequenceService.complement(req))

@router.post("/reverse-complement", response_model=EnvelopeResponse[SequenceResult])
async def reverse_complement_sequence(req: SequenceRequest):
    return EnvelopeResponse(success=True, data=SequenceService.reverse_complement(req))

@router.post("/transcribe", response_model=EnvelopeResponse[SequenceResult])
async def transcribe_sequence(req: SequenceRequest):
    return EnvelopeResponse(success=True, data=SequenceService.transcribe(req))

@router.post("/back-transcribe", response_model=EnvelopeResponse[SequenceResult])
async def back_transcribe_sequence(req: SequenceRequest):
    return EnvelopeResponse(success=True, data=SequenceService.back_transcribe(req))

@router.post("/translate", response_model=EnvelopeResponse[SequenceResult])
async def translate_sequence(req: TranslationRequest):
    return EnvelopeResponse(success=True, data=SequenceService.translate(req))

@router.post("/gc-content", response_model=EnvelopeResponse[GCContentResult])
async def gc_content(req: SequenceRequest):
    return EnvelopeResponse(success=True, data=SequenceService.gc_content(req))

@router.post("/count-bases", response_model=EnvelopeResponse[BaseCountResult])
async def count_bases(req: SequenceRequest):
    return EnvelopeResponse(success=True, data=SequenceService.count_bases(req))

@router.post("/kmer", response_model=EnvelopeResponse[KmerResult])
async def extract_kmers(req: KmerRequest):
    return EnvelopeResponse(success=True, data=SequenceService.kmer(req))

@router.post("/find-motif", response_model=EnvelopeResponse[MotifResult])
async def find_motif(req: MotifRequest):
    return EnvelopeResponse(success=True, data=SequenceService.find_motif(req))

@router.post("/validate", response_model=EnvelopeResponse[ValidationResult])
async def validate_sequence(req: SequenceRequest):
    return EnvelopeResponse(success=True, data=SequenceService.validate(req))
