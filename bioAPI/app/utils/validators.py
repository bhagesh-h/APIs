from typing import Tuple
from app.schemas.sequence import AlphabetEnum

DNA_ALPHABET = set("ACGTN")
RNA_ALPHABET = set("ACGUN")
PROTEIN_ALPHABET = set("ACDEFGHIKLMNPQRSTVWY*BXZJ") # Includes ambiguity codes and stop


def validate_sequence_content(sequence: str, expected_alphabet: AlphabetEnum | None = None) -> Tuple[bool, str | None, list[str]]:
    """
    Validates a sequence against standard bioinformatics alphabets.
    Returns (is_valid, detected_alphabet, list_of_invalid_chars).
    """
    if not sequence:
        return False, None, []

    seq_upper = sequence.upper()
    chars_used = set(seq_upper)

    
    if expected_alphabet:
        if expected_alphabet == AlphabetEnum.dna:
            invalid = chars_used - DNA_ALPHABET
            if invalid:
                return False, AlphabetEnum.dna.value, list(invalid)
            return True, AlphabetEnum.dna.value, []
            
        elif expected_alphabet == AlphabetEnum.rna:
            invalid = chars_used - RNA_ALPHABET
            if invalid:
                return False, AlphabetEnum.rna.value, list(invalid)
            return True, AlphabetEnum.rna.value, []
            
        elif expected_alphabet == AlphabetEnum.protein:
            invalid = chars_used - PROTEIN_ALPHABET
            if invalid:
                return False, AlphabetEnum.protein.value, list(invalid)
            return True, AlphabetEnum.protein.value, []

    # Auto-detect if not specified
    if chars_used.issubset(DNA_ALPHABET):
        return True, AlphabetEnum.dna.value, []
    if chars_used.issubset(RNA_ALPHABET):
        return True, AlphabetEnum.rna.value, []
    if chars_used.issubset(PROTEIN_ALPHABET):
        return True, AlphabetEnum.protein.value, []

    return False, "unknown", list(chars_used - PROTEIN_ALPHABET)


def clean_sequence(sequence: str, uppercase: bool = True, remove_whitespace: bool = True) -> str:
    """Pre-process sequence string."""
    res = sequence
    if remove_whitespace:
        res = "".join(res.split())
    if uppercase:
        res = res.upper()
    return res
