from enum import Enum
from pydantic import BaseModel

class FileFormatEnum(str, Enum):
    fasta = "fasta"
    fastq = "fastq"
    genbank = "genbank"
    text = "text"
    bam = "bam"
    gff = "gff"
    gtf = "gtf"
    vcf = "vcf"
    string = "string"
    unknown = "unknown"

class FormatDetection(BaseModel):
    detected_format: FileFormatEnum
    confidence: str

class SequenceStats(BaseModel):
    num_records: int
    min_length: int | None
    max_length: int | None
    avg_length: float | None
    total_bases: int | None
    gc_percent: float | None
    ambiguous_chars: int | None

class FastqStats(BaseModel):
    avg_quality: float | None
    min_quality: float | None
    max_quality: float | None

class BamStats(BaseModel):
    total_reads: int
    mapped_reads: int | None
    unmapped_reads: int | None
    avg_read_length: float | None

class GtfGffStats(BaseModel):
    total_features: int
    feature_counts: dict[str, int]

class VcfStats(BaseModel):
    total_variants: int
    snps: int
    indels: int
    transitions: int
    transversions: int

class FileStatsResponse(BaseModel):
    filename: str
    content_type: str
    size_bytes: int
    lines: int | None
    format: FormatDetection
    sequence_stats: SequenceStats | None
    fastq_stats: FastqStats | None
    bam_stats: BamStats | None = None
    gff_stats: GtfGffStats | None = None
    vcf_stats: VcfStats | None = None
    preview_ids: list[str]
