"""
fasta_utils.py  (router)
~~~~~~~~~~~~~~~~~~~~~~~~
Router for FASTA / FASTQ string-level utility endpoints.
Prefix: /fasta  and  /fastq
"""
from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_api_key, rate_limit_placeholder
from app.core.errors import BioFastAPIError
from app.schemas.common import EnvelopeResponse
from app.schemas.fasta_utils import (
    ConvertCaseRequest,
    ExtractSubsequenceRequest,
    FastaStringRequest,
    FastaStringResult,
    FastqGzDecompressRequest,
    FastqGzResult,
    FastqQualityFilterRequest,
    FastqStringResult,
    FilterByLengthRequest,
    GetNSequencesRequest,
    MergeFastaRequest,
    ModifyDescriptionsRequest,
    RenameSequencesRequest,
    SampleSequencesRequest,
    SequenceIdsResult,
    ShortenHeaderRequest,
    SplitFastaRequest,
    SplitFastaResult,
)
from app.services.fasta_utils_service import FastaUtilsService

_DEPS = [Depends(get_api_key), Depends(rate_limit_placeholder)]

# ─── FASTA router ─────────────────────────────────────────────────────────────

fasta_router = APIRouter(prefix="/fasta", tags=["FASTA Utilities"], dependencies=_DEPS)


@fasta_router.post(
    "/shorten-headers",
    response_model=EnvelopeResponse[FastaStringResult],
    summary="Shorten FASTA headers",
    description="Truncate every sequence header to at most **n** characters (the ID + description combined, excluding '>').",
)
async def shorten_headers(req: ShortenHeaderRequest):
    return EnvelopeResponse(success=True, data=FastaUtilsService.shorten_headers(req))


@fasta_router.post(
    "/get-n-sequences",
    response_model=EnvelopeResponse[FastaStringResult],
    summary="Get first N sequences",
    description="Extract the first **n** sequences from a FASTA string.",
)
async def get_n_sequences(req: GetNSequencesRequest):
    return EnvelopeResponse(success=True, data=FastaUtilsService.get_n_sequences(req))


@fasta_router.post(
    "/filter-by-length",
    response_model=EnvelopeResponse[FastaStringResult],
    summary="Filter sequences by length",
    description="Keep only sequences whose length falls within [min_length, max_length].",
)
async def filter_by_length(req: FilterByLengthRequest):
    return EnvelopeResponse(success=True, data=FastaUtilsService.filter_by_length(req))


@fasta_router.post(
    "/extract-subsequence",
    response_model=EnvelopeResponse[FastaStringResult],
    summary="Extract a coordinate range from every sequence",
    description=(
        "Slice positions **start** to **end** (1-based, inclusive) from every sequence. "
        "Returns an error if any sequence is shorter than the requested end position."
    ),
)
async def extract_subsequence(req: ExtractSubsequenceRequest):
    return EnvelopeResponse(success=True, data=FastaUtilsService.extract_subsequence(req))


@fasta_router.post(
    "/sample-sequences",
    response_model=EnvelopeResponse[FastaStringResult],
    summary="Randomly sample N sequences",
    description="Select **n** sequences at random (without replacement).",
)
async def sample_sequences(req: SampleSequencesRequest):
    return EnvelopeResponse(success=True, data=FastaUtilsService.sample_sequences(req))


@fasta_router.post(
    "/split",
    response_model=EnvelopeResponse[SplitFastaResult],
    summary="Split FASTA into chunks",
    description=(
        "Split a FASTA string into multiple chunks. "
        "Supply **n** (number of output chunks) *or* **size** (sequences per chunk), not both."
    ),
)
async def split_fasta(req: SplitFastaRequest):
    return EnvelopeResponse(success=True, data=FastaUtilsService.split_fasta(req))


@fasta_router.post(
    "/merge",
    response_model=EnvelopeResponse[FastaStringResult],
    summary="Merge multiple FASTA strings",
    description="Concatenate two or more FASTA strings into a single FASTA string.",
)
async def merge_fasta(req: MergeFastaRequest):
    return EnvelopeResponse(success=True, data=FastaUtilsService.merge_fasta(req))


@fasta_router.post(
    "/convert-case",
    response_model=EnvelopeResponse[FastaStringResult],
    summary="Convert sequence case",
    description="Convert all sequence characters to **upper** or **lower** case.",
)
async def convert_case(req: ConvertCaseRequest):
    return EnvelopeResponse(success=True, data=FastaUtilsService.convert_case(req))


@fasta_router.post(
    "/remove-unknown-chars",
    response_model=EnvelopeResponse[FastaStringResult],
    summary="Remove non-ACGT characters",
    description="Strip any character that is not A, C, G, or T (case-insensitive) from every sequence.",
)
async def remove_unknown_chars(req: FastaStringRequest):
    return EnvelopeResponse(success=True, data=FastaUtilsService.remove_unknown_chars(req))


@fasta_router.post(
    "/rename-sequences",
    response_model=EnvelopeResponse[FastaStringResult],
    summary="Rename sequence IDs",
    description=(
        "Rename sequence IDs using a mapping dict `{old_id: new_id}`. "
        "Any ID not in the mapping is left unchanged. Descriptions after the ID are preserved."
    ),
)
async def rename_sequences(req: RenameSequencesRequest):
    return EnvelopeResponse(success=True, data=FastaUtilsService.rename_sequences(req))


@fasta_router.post(
    "/modify-descriptions",
    response_model=EnvelopeResponse[FastaStringResult],
    summary="Replace sequence descriptions",
    description=(
        "Replace the description text (everything after the ID on the header line) "
        "for specified IDs using a `{sequence_id: new_description}` mapping."
    ),
)
async def modify_descriptions(req: ModifyDescriptionsRequest):
    return EnvelopeResponse(success=True, data=FastaUtilsService.modify_descriptions(req))


@fasta_router.post(
    "/find-unique",
    response_model=EnvelopeResponse[FastaStringResult],
    summary="Deduplicate sequences",
    description=(
        "Return only sequences with unique nucleotide content. "
        "The first occurrence of each unique sequence is kept; subsequent duplicates are dropped."
    ),
)
async def find_unique_sequences(req: FastaStringRequest):
    return EnvelopeResponse(success=True, data=FastaUtilsService.find_unique_sequences(req))


@fasta_router.post(
    "/extract-ids",
    response_model=EnvelopeResponse[SequenceIdsResult],
    summary="List all sequence IDs",
    description="Return an ordered list of every sequence ID present in the FASTA string.",
)
async def extract_sequence_ids(req: FastaStringRequest):
    return EnvelopeResponse(success=True, data=FastaUtilsService.extract_sequence_ids(req))


# ─── FASTQ router ─────────────────────────────────────────────────────────────

fastq_router = APIRouter(prefix="/fastq", tags=["FASTQ Utilities"], dependencies=_DEPS)


@fastq_router.post(
    "/quality-filter",
    response_model=EnvelopeResponse[FastqStringResult],
    summary="Filter reads by quality",
    description=(
        "Discard FASTQ reads whose **average Phred quality score** is below `min_quality`. "
        "Quality is decoded from the standard Sanger/Illumina 1.8+ encoding (ASCII − 33)."
    ),
)
async def quality_filter_fastq(req: FastqQualityFilterRequest):
    return EnvelopeResponse(success=True, data=FastaUtilsService.quality_filter_fastq(req))


@fastq_router.post(
    "/compress-gz",
    response_model=EnvelopeResponse[FastqGzResult],
    summary="Gzip-compress a FASTQ string",
    description=(
        "Compress the provided FASTQ string with gzip and return the result base64-encoded. "
        "The `data_base64` field can be passed directly to **POST /fastq/decompress-gz**."
    ),
)
async def compress_fastq_gz(req: FastqStringRequest):
    return EnvelopeResponse(success=True, data=FastaUtilsService.compress_fastq_gz(req))


@fastq_router.post(
    "/decompress-gz",
    response_model=EnvelopeResponse[FastqStringResult],
    summary="Decompress a gzipped FASTQ",
    description=(
        "Decompress a base64-encoded gzipped FASTQ (e.g. from **POST /fastq/compress-gz**) "
        "and return the plaintext FASTQ string with read count."
    ),
)
async def decompress_fastq_gz(req: FastqGzDecompressRequest):
    return EnvelopeResponse(success=True, data=FastaUtilsService.decompress_fastq_gz(req))


# ─── Combined export ─────────────────────────────────────────────────────────

# Both routers are exported so main.py can register each individually.
router = fasta_router  # primary export for backward compat
