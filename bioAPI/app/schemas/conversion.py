from pydantic import BaseModel, Field
from enum import Enum

class SupportedSourceFormat(str, Enum):
    fasta = "fasta"
    fastq = "fastq"
    genbank = "genbank"
    text = "text"
    bam = "bam"
    gff = "gff"
    gtf = "gtf"
    string = "string"

class SupportedTargetFormat(str, Enum):
    fasta = "fasta"
    genbank = "genbank"
    json = "json"

class ConversionWarning(BaseModel):
    code: str
    message: str

class ConversionResult(BaseModel):
    filename: str
    records_converted: int
    warnings: list[ConversionWarning] = Field(default_factory=list)
