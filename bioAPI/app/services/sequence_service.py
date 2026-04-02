from Bio.Seq import Seq
from Bio.SeqUtils import gc_fraction
from collections import Counter
from app.schemas.sequence import (
    SequenceRequest, SequenceResult, GCContentResult, BaseCountResult,
    TranslationRequest, KmerRequest, KmerResult, MotifRequest, MotifResult, MotifHit,
    ValidationResult
)
from app.utils.validators import validate_sequence_content, clean_sequence
from app.core.errors import BioFastAPIError

class SequenceService:
    @staticmethod
    def _prepare(req: SequenceRequest) -> str:
        seq = clean_sequence(req.sequence, req.uppercase, req.remove_whitespace)
        is_valid, detected, invalid = validate_sequence_content(seq, req.alphabet)
        if not is_valid:
            raise BioFastAPIError(
                message=f"Invalid sequence characters for expected alphabet. Invalid: {', '.join(invalid)}",
                warnings=[f"Detected alphabet: {detected}"] if detected else []
            )
        return seq

    @classmethod
    def reverse(cls, req: SequenceRequest) -> SequenceResult:
        seq = cls._prepare(req)
        return SequenceResult(result=seq[::-1])

    @classmethod
    def complement(cls, req: SequenceRequest) -> SequenceResult:
        seq = cls._prepare(req)
        # Assuming DNA by default, Bio.Seq automatically handles it but might warn if mixed.
        try:
            result = str(Seq(seq).complement())
            return SequenceResult(result=result)
        except Exception as e:
            raise BioFastAPIError(message=f"Failed to complement sequence: {str(e)}")

    @classmethod
    def reverse_complement(cls, req: SequenceRequest) -> SequenceResult:
        seq = cls._prepare(req)
        try:
            result = str(Seq(seq).reverse_complement())
            return SequenceResult(result=result)
        except Exception as e:
            raise BioFastAPIError(message=f"Failed to reverse complement sequence: {str(e)}")

    @classmethod
    def transcribe(cls, req: SequenceRequest) -> SequenceResult:
        seq = cls._prepare(req)
        # DNA to RNA
        try:
            result = str(Seq(seq).transcribe())
            return SequenceResult(result=result)
        except Exception as e:
            raise BioFastAPIError(message=f"Transcription failed: {str(e)}")

    @classmethod
    def back_transcribe(cls, req: SequenceRequest) -> SequenceResult:
        seq = cls._prepare(req)
        # RNA to DNA
        try:
            result = str(Seq(seq).back_transcribe())
            return SequenceResult(result=result)
        except Exception as e:
            raise BioFastAPIError(message=f"Back-transcription failed: {str(e)}")

    @classmethod
    def translate(cls, req: TranslationRequest) -> SequenceResult:
        seq = cls._prepare(req)
        try:
            result = str(Seq(seq).translate(table=req.table.value, to_stop=req.to_stop))
            return SequenceResult(result=result)
        except Exception as e:
            raise BioFastAPIError(message=f"Translation failed. Make sure sequence length is a multiple of 3 if no padding. Error: {str(e)}")

    @classmethod
    def gc_content(cls, req: SequenceRequest) -> GCContentResult:
        seq = cls._prepare(req)
        fraction = gc_fraction(seq)
        return GCContentResult(gc_percent=round(fraction * 100, 4))

    @classmethod
    def count_bases(cls, req: SequenceRequest) -> BaseCountResult:
        seq = cls._prepare(req)
        counts = dict(Counter(seq))
        return BaseCountResult(counts=counts, length=len(seq))

    @classmethod
    def kmer(cls, req: KmerRequest) -> KmerResult:
        seq = cls._prepare(req)
        k = req.k
        if k > len(seq):
            raise BioFastAPIError(message="k cannot be greater than sequence length")
        
        kmers = Counter(seq[i:i+k] for i in range(len(seq) - k + 1))
        return KmerResult(kmers=dict(kmers))

    @classmethod
    def find_motif(cls, req: MotifRequest) -> MotifResult:
        seq = cls._prepare(req)
        motif = req.motif.upper() if req.uppercase else req.motif
        if req.remove_whitespace:
            motif = "".join(motif.split())
            
        if not motif:
            raise BioFastAPIError(message="Motif cannot be empty")

        hits = []
        start = 0
        while True:
            start = seq.find(motif, start)
            if start == -1:
                break
            hits.append(MotifHit(start=start, end=start+len(motif), match=motif))
            # Overlapping search -> advance by 1
            start += 1
            
        return MotifResult(count=len(hits), hits=hits)

    @classmethod
    def validate(cls, req: SequenceRequest) -> ValidationResult:
        # Don't use _prepare to avoid raising exception
        seq = clean_sequence(req.sequence, req.uppercase, req.remove_whitespace)
        is_valid, detected, invalid = validate_sequence_content(seq, req.alphabet)
        return ValidationResult(
            is_valid=is_valid,
            alphabet_detected=detected,
            invalid_chars=invalid
        )
