from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field, model_validator


# ─── Request Models ─────────────────────────────────────────────────────────


class FastaStringRequest(BaseModel):
    """Base request carrying a raw FASTA string."""

    fasta_string: str = Field(..., description="A valid FASTA-formatted string", min_length=3)


class ShortenHeaderRequest(FastaStringRequest):
    n: int = Field(..., description="Maximum number of characters to keep in each header", ge=1)


class GetNSequencesRequest(FastaStringRequest):
    n: int = Field(..., description="Number of sequences to extract from the top", ge=1)


class FilterByLengthRequest(FastaStringRequest):
    min_length: int = Field(0, description="Minimum sequence length (inclusive)", ge=0)
    max_length: int | None = Field(None, description="Maximum sequence length (inclusive, None = no limit)", ge=0)


class ExtractSubsequenceRequest(FastaStringRequest):
    start: int = Field(..., description="1-based start position of the subsequence", ge=1)
    end: int = Field(..., description="1-based end position of the subsequence (inclusive)", ge=1)

    @model_validator(mode="after")
    def start_before_end(self) -> "ExtractSubsequenceRequest":
        if self.start > self.end:
            raise ValueError("start must be <= end")
        return self


class SampleSequencesRequest(FastaStringRequest):
    n: int = Field(..., description="Number of sequences to randomly sample", ge=1)


class SplitFastaRequest(FastaStringRequest):
    n: int | None = Field(None, description="Number of output chunks (mutually exclusive with size)", ge=1)
    size: int | None = Field(None, description="Number of sequences per chunk (mutually exclusive with n)", ge=1)

    @model_validator(mode="after")
    def n_xor_size(self) -> "SplitFastaRequest":
        if self.n is not None and self.size is not None:
            raise ValueError("'n' and 'size' are mutually exclusive – supply only one.")
        if self.n is None and self.size is None:
            raise ValueError("Either 'n' or 'size' must be provided.")
        return self


class MergeFastaRequest(BaseModel):
    fasta_strings: list[str] = Field(..., description="List of FASTA strings to concatenate", min_length=2)


class ConvertCaseRequest(FastaStringRequest):
    case: Literal["upper", "lower"] = Field("upper", description="Target case for sequence characters")


class RenameSequencesRequest(FastaStringRequest):
    rename_map: dict[str, str] = Field(
        ..., description="Mapping of {old_sequence_id: new_sequence_id}"
    )


class ModifyDescriptionsRequest(FastaStringRequest):
    description_map: dict[str, str] = Field(
        ..., description="Mapping of {sequence_id: new_description_text}"
    )


class FastqStringRequest(BaseModel):
    """Base request carrying a raw FASTQ string."""

    fastq_string: str = Field(..., description="A valid FASTQ-formatted string", min_length=1)


class FastqQualityFilterRequest(FastqStringRequest):
    min_quality: int = Field(20, description="Minimum average Phred quality score per read", ge=0)


class FastqGzDecompressRequest(BaseModel):
    fastq_gz_base64: str = Field(
        ...,
        description="Base64-encoded content of a gzipped FASTQ file (as produced by POST /fastq/compress-gz)",
    )


# ─── Response Models ─────────────────────────────────────────────────────────


class FastaStringResult(BaseModel):
    fasta_string: str = Field(..., description="Resulting FASTA-formatted string")
    num_sequences: int = Field(..., description="Number of sequences in the result")


class SplitFastaResult(BaseModel):
    chunks: list[str] = Field(..., description="List of FASTA string chunks")
    num_chunks: int = Field(..., description="Number of chunks produced")
    sequences_per_chunk: list[int] = Field(..., description="Sequence count per chunk")


class SequenceIdsResult(BaseModel):
    ids: list[str] = Field(..., description="Ordered list of sequence IDs found in the FASTA")
    count: int = Field(..., description="Total number of sequences")


class FastqStringResult(BaseModel):
    fastq_string: str = Field(..., description="Resulting FASTQ-formatted string")
    num_reads: int = Field(..., description="Number of reads in the result")


class FastqGzResult(BaseModel):
    """Result for gzip compression – returns base64-encoded bytes."""

    data_base64: str = Field(..., description="Base64-encoded gzipped content")
    original_size_bytes: int
    compressed_size_bytes: int
