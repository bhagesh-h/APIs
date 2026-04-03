"""
fasta_utils_service.py
~~~~~~~~~~~~~~~~~~~~~~
Service layer for FASTA / FASTQ string-level utility operations.

All methods operate on raw in-memory strings (no file I/O),
raise BioFastAPIError on invalid input, and return plain Python
objects that the router wraps in EnvelopeResponse.
"""
from __future__ import annotations

import base64
import gzip
import io
import random
from typing import Iterator

from app.core.errors import BioFastAPIError
from app.schemas.fasta_utils import (
    ConvertCaseRequest,
    ExtractSubsequenceRequest,
    FastaStringResult,
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


# ─── Internal FASTA parser ────────────────────────────────────────────────────

def _parse_fasta(fasta_string: str) -> list[tuple[str, str]]:
    """
    Parse a FASTA string into a list of (header_line, sequence) tuples.
    header_line includes the leading '>'.
    Raises BioFastAPIError on malformed input.
    """
    lines = fasta_string.strip().splitlines()
    if not lines:
        raise BioFastAPIError(message="FASTA string is empty.")

    records: list[tuple[str, str]] = []
    current_header: str | None = None
    seq_parts: list[str] = []

    for line in lines:
        if line.startswith(">"):
            if len(line) == 1:
                raise BioFastAPIError(message="Found a FASTA header line with no ID (bare '>').")
            if current_header is not None:
                records.append((current_header, "".join(seq_parts)))
                seq_parts = []
            current_header = line
        else:
            if current_header is None:
                raise BioFastAPIError(
                    message="FASTA data line found before any header line."
                )
            seq_parts.append(line)

    if current_header is not None:
        records.append((current_header, "".join(seq_parts)))

    if not records:
        raise BioFastAPIError(message="No valid FASTA records found in the input.")

    return records


def _records_to_fasta(records: list[tuple[str, str]]) -> str:
    """Serialize (header, seq) tuple list back to a FASTA string."""
    return "\n".join(f"{hdr}\n{seq}" for hdr, seq in records)


def _header_id(header_line: str) -> str:
    """Extract the sequence ID (first token after '>') from a header line."""
    return header_line[1:].split()[0]


# ─── Internal FASTQ parser ────────────────────────────────────────────────────

def _parse_fastq(fastq_string: str) -> list[tuple[str, str, str, str]]:
    """
    Parse FASTQ string into list of (header, seq, plus, quality) tuples.
    Raises BioFastAPIError on malformed input.
    """
    lines = fastq_string.strip().splitlines()
    if len(lines) % 4 != 0:
        raise BioFastAPIError(
            message=f"Invalid FASTQ: expected line count divisible by 4, got {len(lines)}."
        )
    records = []
    for i in range(0, len(lines), 4):
        header, seq, plus, qual = lines[i], lines[i + 1], lines[i + 2], lines[i + 3]
        if not header.startswith("@"):
            raise BioFastAPIError(
                message=f"FASTQ read {i // 4 + 1}: header line must start with '@'."
            )
        if not plus.startswith("+"):
            raise BioFastAPIError(
                message=f"FASTQ read {i // 4 + 1}: third line must start with '+'."
            )
        if len(seq) != len(qual):
            raise BioFastAPIError(
                message=f"FASTQ read {i // 4 + 1}: sequence and quality lengths differ."
            )
        records.append((header, seq, plus, qual))
    return records


def _records_to_fastq(records: list[tuple[str, str, str, str]]) -> str:
    return "\n".join(f"{h}\n{s}\n{p}\n{q}" for h, s, p, q in records)


# ─── Service ──────────────────────────────────────────────────────────────────

class FastaUtilsService:

    # ── FASTA utilities ─────────────────────────────────────────────────────

    @staticmethod
    def shorten_headers(req: ShortenHeaderRequest) -> FastaStringResult:
        """Truncate every FASTA header to the first n characters (excluding '>')."""
        records = _parse_fasta(req.fasta_string)
        result = []
        for hdr, seq in records:
            short_hdr = ">" + hdr[1 : req.n + 1]  # slice chars after '>'
            result.append((short_hdr, seq))
        return FastaStringResult(
            fasta_string=_records_to_fasta(result),
            num_sequences=len(result),
        )

    @staticmethod
    def get_n_sequences(req: GetNSequencesRequest) -> FastaStringResult:
        """Return the first n sequences from a FASTA string."""
        records = _parse_fasta(req.fasta_string)
        warnings: list[str] = []
        if req.n > len(records):
            warnings.append(
                f"Requested {req.n} sequences but only {len(records)} present. Returning all."
            )
        sliced = records[: req.n]
        return FastaStringResult(
            fasta_string=_records_to_fasta(sliced),
            num_sequences=len(sliced),
        )

    @staticmethod
    def filter_by_length(req: FilterByLengthRequest) -> FastaStringResult:
        """Keep only sequences whose length is within [min_length, max_length]."""
        records = _parse_fasta(req.fasta_string)
        max_len = req.max_length if req.max_length is not None else float("inf")
        filtered = [
            (hdr, seq)
            for hdr, seq in records
            if req.min_length <= len(seq) <= max_len
        ]
        return FastaStringResult(
            fasta_string=_records_to_fasta(filtered) if filtered else "",
            num_sequences=len(filtered),
        )

    @staticmethod
    def extract_subsequence(req: ExtractSubsequenceRequest) -> FastaStringResult:
        """Slice [start, end] (1-based, inclusive) from every sequence."""
        records = _parse_fasta(req.fasta_string)
        result = []
        for hdr, seq in records:
            if req.end > len(seq):
                raise BioFastAPIError(
                    message=(
                        f"Sequence '{_header_id(hdr)}' has length {len(seq)}, "
                        f"but requested end={req.end}."
                    )
                )
            result.append((hdr, seq[req.start - 1 : req.end]))
        return FastaStringResult(
            fasta_string=_records_to_fasta(result),
            num_sequences=len(result),
        )

    @staticmethod
    def sample_sequences(req: SampleSequencesRequest) -> FastaStringResult:
        """Randomly sample n sequences without replacement."""
        records = _parse_fasta(req.fasta_string)
        warnings: list[str] = []
        if req.n > len(records):
            warnings.append(
                f"Requested {req.n} samples but only {len(records)} sequences exist. Returning all."
            )
        sampled = random.sample(records, min(req.n, len(records)))
        return FastaStringResult(
            fasta_string=_records_to_fasta(sampled),
            num_sequences=len(sampled),
        )

    @staticmethod
    def split_fasta(req: SplitFastaRequest) -> SplitFastaResult:
        """Split a FASTA into chunks of equal-ish size."""
        records = _parse_fasta(req.fasta_string)
        total = len(records)

        if req.n is not None:
            if req.n > total:
                raise BioFastAPIError(
                    message=f"Cannot split {total} sequences into {req.n} chunks (n > total)."
                )
            chunk_size = (total + req.n - 1) // req.n
        else:
            chunk_size = req.size  # type: ignore[assignment]

        chunks: list[str] = []
        seq_counts: list[int] = []
        for i in range(0, total, chunk_size):
            chunk = records[i : i + chunk_size]
            chunks.append(_records_to_fasta(chunk))
            seq_counts.append(len(chunk))

        return SplitFastaResult(
            chunks=chunks,
            num_chunks=len(chunks),
            sequences_per_chunk=seq_counts,
        )

    @staticmethod
    def merge_fasta(req: MergeFastaRequest) -> FastaStringResult:
        """Concatenate multiple FASTA strings into one."""
        all_records: list[tuple[str, str]] = []
        for i, fasta in enumerate(req.fasta_strings):
            try:
                all_records.extend(_parse_fasta(fasta))
            except BioFastAPIError as exc:
                raise BioFastAPIError(
                    message=f"Error in fasta_strings[{i}]: {exc.message}"
                ) from exc
        return FastaStringResult(
            fasta_string=_records_to_fasta(all_records),
            num_sequences=len(all_records),
        )

    @staticmethod
    def convert_case(req: ConvertCaseRequest) -> FastaStringResult:
        """Convert all sequence characters to uppercase or lowercase."""
        records = _parse_fasta(req.fasta_string)
        convert = str.upper if req.case == "upper" else str.lower
        result = [(hdr, convert(seq)) for hdr, seq in records]
        return FastaStringResult(
            fasta_string=_records_to_fasta(result),
            num_sequences=len(result),
        )

    @staticmethod
    def remove_unknown_chars(req) -> FastaStringResult:
        """Strip any character that is not A, C, G, T (case-insensitive) from sequences."""
        records = _parse_fasta(req.fasta_string)
        valid = set("ACGTacgt")
        result = [
            (hdr, "".join(c for c in seq if c in valid)) for hdr, seq in records
        ]
        return FastaStringResult(
            fasta_string=_records_to_fasta(result),
            num_sequences=len(result),
        )

    @staticmethod
    def rename_sequences(req: RenameSequencesRequest) -> FastaStringResult:
        """Rename sequence IDs according to rename_map."""
        records = _parse_fasta(req.fasta_string)
        result = []
        for hdr, seq in records:
            seq_id = _header_id(hdr)
            if seq_id in req.rename_map:
                # Preserve the rest of the description after the ID
                rest = hdr[len(seq_id) + 1 :]  # everything after ">old_id"
                new_hdr = f">{req.rename_map[seq_id]}{rest}"
            else:
                new_hdr = hdr
            result.append((new_hdr, seq))
        return FastaStringResult(
            fasta_string=_records_to_fasta(result),
            num_sequences=len(result),
        )

    @staticmethod
    def modify_descriptions(req: ModifyDescriptionsRequest) -> FastaStringResult:
        """Replace the description (text after the ID on the header line) for given IDs."""
        records = _parse_fasta(req.fasta_string)
        result = []
        for hdr, seq in records:
            seq_id = _header_id(hdr)
            if seq_id in req.description_map:
                new_hdr = f">{seq_id} {req.description_map[seq_id]}"
            else:
                new_hdr = hdr
            result.append((new_hdr, seq))
        return FastaStringResult(
            fasta_string=_records_to_fasta(result),
            num_sequences=len(result),
        )

    @staticmethod
    def find_unique_sequences(req) -> FastaStringResult:
        """Return only sequences whose nucleotide content is unique (first occurrence wins)."""
        records = _parse_fasta(req.fasta_string)
        seen: set[str] = set()
        unique: list[tuple[str, str]] = []
        for hdr, seq in records:
            key = seq.upper()
            if key not in seen:
                seen.add(key)
                unique.append((hdr, seq))
        return FastaStringResult(
            fasta_string=_records_to_fasta(unique),
            num_sequences=len(unique),
        )

    @staticmethod
    def extract_sequence_ids(req) -> SequenceIdsResult:
        """Return the list of all sequence IDs in the order they appear."""
        records = _parse_fasta(req.fasta_string)
        ids = [_header_id(hdr) for hdr, _ in records]
        return SequenceIdsResult(ids=ids, count=len(ids))

    # ── FASTQ utilities ─────────────────────────────────────────────────────

    @staticmethod
    def quality_filter_fastq(req: FastqQualityFilterRequest) -> FastqStringResult:
        """Keep FASTQ reads whose average Phred quality is >= min_quality."""
        reads = _parse_fastq(req.fastq_string)
        kept = []
        for header, seq, plus, qual in reads:
            avg_q = sum(ord(c) - 33 for c in qual) / len(qual)
            if avg_q >= req.min_quality:
                kept.append((header, seq, plus, qual))
        return FastqStringResult(
            fastq_string=_records_to_fastq(kept) if kept else "",
            num_reads=len(kept),
        )

    @staticmethod
    def compress_fastq_gz(req) -> FastqGzResult:
        """Gzip-compress a FASTQ string and return the result as base64."""
        raw = req.fastq_string.encode("utf-8")
        buf = io.BytesIO()
        with gzip.GzipFile(fileobj=buf, mode="wb", compresslevel=9) as gz:
            gz.write(raw)
        compressed = buf.getvalue()
        return FastqGzResult(
            data_base64=base64.b64encode(compressed).decode("ascii"),
            original_size_bytes=len(raw),
            compressed_size_bytes=len(compressed),
        )

    @staticmethod
    def decompress_fastq_gz(req) -> FastqStringResult:
        """
        Decompress a gzipped FASTQ.
        Accepts the raw base64-encoded gzip bytes as a string field.
        """
        try:
            compressed = base64.b64decode(req.fastq_gz_base64)
        except Exception as exc:
            raise BioFastAPIError(
                message="Could not base64-decode the input. Make sure it is valid base64."
            ) from exc
        try:
            decompressed = gzip.decompress(compressed).decode("utf-8")
        except Exception as exc:
            raise BioFastAPIError(
                message=f"Decompression failed – not a valid gzip stream: {exc}"
            ) from exc
        reads = _parse_fastq(decompressed)
        return FastqStringResult(
            fastq_string=_records_to_fastq(reads),
            num_reads=len(reads),
        )
