from enum import Enum
from pydantic import BaseModel, Field


class AlphabetEnum(str, Enum):
    dna = "dna"
    rna = "rna"
    protein = "protein"


class SequenceRequest(BaseModel):
    sequence: str = Field(..., description="The biological sequence string", min_length=1)
    alphabet: AlphabetEnum | None = Field(None, description="Expected alphabet for validation")
    uppercase: bool = Field(True, description="Whether to uppercase the result/input")
    remove_whitespace: bool = Field(True, description="Whether to strip whitespace before processing")


class TranslationTableEnum(int, Enum):
    standard = 1
    vertebrate_mitochondrial = 2
    yeast_mitochondrial = 3
    mold_mitochondrial = 4
    invertebrate_mitochondrial = 5
    ciliate_nuclear = 6
    echinoderm_mitochondrial = 9
    euplotid_nuclear = 10
    bacterial = 11
    alternative_yeast_nuclear = 12
    ascidian_mitochondrial = 13
    alternative_flatworm_mitochondrial = 14
    blepharisma_macronuclear = 15
    chlorophycean_mitochondrial = 16
    trematode_mitochondrial = 21
    scenedesmus_obliquus_mitochondrial = 22
    thraustochytrium_mitochondrial = 23
    pterobranchia_mitochondrial = 24
    candidate_division_sr1 = 25
    pachysolen_tannophilus_nuclear = 26
    karyorelict_nuclear = 27
    condylostoma_nuclear = 28
    mesodinium_nuclear = 29
    peritrich_nuclear = 30
    blastocrithidia_nuclear = 31
    cephalodiscidae_mitochondrial = 33


class TranslationRequest(SequenceRequest):
    table: TranslationTableEnum = Field(TranslationTableEnum.standard, description="NCBI translation table ID")
    to_stop: bool = Field(False, description="Translate up to the first stop codon")


class KmerRequest(SequenceRequest):
    k: int = Field(3, description="Length of k-mer", ge=1)


class MotifRequest(SequenceRequest):
    motif: str = Field(..., description="Substring to search for", min_length=1)


# Responses

class SequenceResult(BaseModel):
    result: str

class GCContentResult(BaseModel):
    gc_percent: float

class BaseCountResult(BaseModel):
    counts: dict[str, int]
    length: int

class KmerResult(BaseModel):
    kmers: dict[str, int]
    
class MotifHit(BaseModel):
    start: int
    end: int
    match: str
    
class MotifResult(BaseModel):
    count: int
    hits: list[MotifHit]

class ValidationResult(BaseModel):
    is_valid: bool
    alphabet_detected: str | None
    invalid_chars: list[str] = Field(default_factory=list)
