import tempfile
import os
from fastapi import UploadFile
from Bio import SeqIO
from Bio.SeqUtils import gc_fraction
import numpy as np

from app.schemas.file_stats import (
    FileStatsResponse, FileFormatEnum, FormatDetection, SequenceStats, FastqStats, BamStats, GtfGffStats, VcfStats
)
from app.core.errors import BioFastAPIError

class FileService:
    @staticmethod
    def _detect_format(filename: str) -> FileFormatEnum:
        ext = filename.lower().split('.')[-1]
        if ext in ['fasta', 'fa', 'fna', 'faa']:
            return FileFormatEnum.fasta
        if ext in ['fastq', 'fq']:
            return FileFormatEnum.fastq
        if ext in ['gb', 'gbk', 'genbank']:
            return FileFormatEnum.genbank
        if ext in ['bam']:
            return FileFormatEnum.bam
        if ext in ['gff', 'gff3']:
            return FileFormatEnum.gff
        if ext in ['gtf']:
            return FileFormatEnum.gtf
        if ext in ['vcf']:
            return FileFormatEnum.vcf
        if ext in ['string']:
            return FileFormatEnum.string
        if ext in ['txt', 'seq']:
            return FileFormatEnum.text
        return FileFormatEnum.unknown

    @classmethod
    async def analyze_file(cls, file: UploadFile) -> FileStatsResponse:
        filename = file.filename or "unknown"
        detected_format = cls._detect_format(filename)
        
        # We need to process the file, so we read it into a temporary file
        fd, temp_path = tempfile.mkstemp()
        try:
            size_bytes = 0
            with os.fdopen(fd, 'wb') as out_file:
                while content := await file.read(1024 * 1024):
                    out_file.write(content)
                    size_bytes += len(content)

            if detected_format in [FileFormatEnum.fasta, FileFormatEnum.fastq, FileFormatEnum.genbank]:
                stats = cls._analyze_bio_format(temp_path, detected_format.value)
                return FileStatsResponse(
                    filename=filename,
                    content_type=file.content_type or "application/octet-stream",
                    size_bytes=size_bytes,
                    lines=None,
                    format=FormatDetection(detected_format=detected_format, confidence="high if parsable"),
                    sequence_stats=stats.get("sequence_stats"),
                    fastq_stats=stats.get("fastq_stats"),
                    preview_ids=stats.get("preview_ids", [])
                )
            elif detected_format == FileFormatEnum.bam:
                bam_stats = cls._analyze_bam_format(temp_path)
                return FileStatsResponse(
                    filename=filename,
                    content_type=file.content_type or "application/octet-stream",
                    size_bytes=size_bytes,
                    lines=None,
                    format=FormatDetection(detected_format=detected_format, confidence="high if parsable"),
                    sequence_stats=None,
                    fastq_stats=None,
                    bam_stats=bam_stats,
                    preview_ids=[]
                )
            elif detected_format in [FileFormatEnum.gff, FileFormatEnum.gtf]:
                gff_stats = cls._analyze_gff_gtf_format(temp_path)
                lines = cls._count_lines(temp_path)
                return FileStatsResponse(
                    filename=filename,
                    content_type=file.content_type or "application/octet-stream",
                    size_bytes=size_bytes,
                    lines=lines,
                    format=FormatDetection(detected_format=detected_format, confidence="high if parsable"),
                    sequence_stats=None,
                    fastq_stats=None,
                    gff_stats=gff_stats,
                    preview_ids=[]
                )
            elif detected_format == FileFormatEnum.vcf:
                vcf_stats = cls._analyze_vcf_format(temp_path)
                lines = cls._count_lines(temp_path)
                return FileStatsResponse(
                    filename=filename,
                    content_type=file.content_type or "application/octet-stream",
                    size_bytes=size_bytes,
                    lines=lines,
                    format=FormatDetection(detected_format=detected_format, confidence="high if parsable"),
                    sequence_stats=None,
                    fastq_stats=None,
                    vcf_stats=vcf_stats,
                    preview_ids=[]
                )
            else:
                # Text, String, or unknown fallback
                lines = cls._count_lines(temp_path)
                # If it's unknown, we map it to text for fallback stats
                final_format = detected_format if detected_format != FileFormatEnum.unknown else FileFormatEnum.text
                return FileStatsResponse(
                    filename=filename,
                    content_type=file.content_type or "application/octet-stream",
                    size_bytes=size_bytes,
                    lines=lines,
                    format=FormatDetection(detected_format=final_format, confidence="fallback"),
                    sequence_stats=None,
                    fastq_stats=None,
                    gff_stats=None,
                    preview_ids=[]
                )
        except Exception as e:
            raise BioFastAPIError(message=f"Failed to analyze file: {str(e)}")
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    @staticmethod
    def _count_lines(filepath: str) -> int:
        count = 0
        with open(filepath, 'rb') as f:
            for _ in f:
                count += 1
        return count

    @staticmethod
    def _analyze_bio_format(filepath: str, fmt: str) -> dict:
        num_records = 0
        lengths = []
        bases_list = []
        ambiguous_count = 0
        preview_ids = []
        
        # FASTQ specific
        all_qualities = []

        try:
            for i, record in enumerate(SeqIO.parse(filepath, fmt)):
                num_records += 1
                seq_len = len(record.seq)
                lengths.append(seq_len)
                bases_list.append(str(record.seq).upper())
                
                if i < 5:
                    preview_ids.append(record.id)
                    
                if fmt == "fastq" and "phred_quality" in record.letter_annotations:
                    all_qualities.extend(record.letter_annotations["phred_quality"])

        except Exception as e:
            raise BioFastAPIError(message=f"File parsing error for format {fmt}. Are you sure it's valid? Error: {str(e)}")

        if num_records == 0:
            raise BioFastAPIError(message=f"No valid {fmt} records found in file.")

        full_seq = "".join(bases_list)
        total_bases = len(full_seq)
        gc_percent = round(gc_fraction(full_seq) * 100, 4) if total_bases > 0 else 0.0
        ambiguous_count = full_seq.count('N') + full_seq.count('X') # rough metric

        sequence_stats = SequenceStats(
            num_records=num_records,
            min_length=min(lengths),
            max_length=max(lengths),
            avg_length=round(sum(lengths) / num_records, 2),
            total_bases=total_bases,
            gc_percent=gc_percent,
            ambiguous_chars=ambiguous_count
        )

        fastq_stats = None
        if fmt == "fastq" and all_qualities:
            fastq_stats = FastqStats(
                avg_quality=round(np.mean(all_qualities), 2) if all_qualities else None,
                min_quality=min(all_qualities) if all_qualities else None,
                max_quality=max(all_qualities) if all_qualities else None
            )

        return {
            "sequence_stats": sequence_stats,
            "fastq_stats": fastq_stats,
            "preview_ids": preview_ids
        }

    @staticmethod
    def _analyze_bam_format(filepath: str) -> BamStats:
        import pysam
        total_reads = 0
        mapped_reads = 0
        unmapped_reads = 0
        lengths = []
        try:
            # We use AlignmentFile for both SAM and BAM
            with pysam.AlignmentFile(filepath, "r" if filepath.endswith(".sam") else "rb", check_sq=False) as samfile:
                for read in samfile:
                    total_reads += 1
                    if read.is_unmapped:
                        unmapped_reads += 1
                    else:
                        mapped_reads += 1
                    if read.query_length:
                        lengths.append(read.query_length)
                        
            avg_len = sum(lengths)/len(lengths) if lengths else None
            return BamStats(
                total_reads=total_reads,
                mapped_reads=mapped_reads,
                unmapped_reads=unmapped_reads,
                avg_read_length=round(avg_len, 2) if avg_len else None
            )
        except Exception as e:
            raise BioFastAPIError(message=f"BAM/SAM parsing error. Ensure the file is valid. Error: {str(e)}")

    @staticmethod
    def _analyze_gff_gtf_format(filepath: str) -> GtfGffStats:
        from collections import defaultdict
        feature_counts = defaultdict(int)
        total_features = 0
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('#') or not line.strip():
                        continue
                    parts = line.strip().split('\t')
                    if len(parts) >= 3:
                        feature_type = parts[2]
                        feature_counts[feature_type] += 1
                        total_features += 1
            return GtfGffStats(
                total_features=total_features,
                feature_counts=dict(feature_counts)
            )
        except Exception as e:
            raise BioFastAPIError(message=f"GFF/GTF parsing error. Error: {str(e)}")

    @staticmethod
    def _analyze_vcf_format(filepath: str) -> VcfStats:
        import pysam
        snps = indels = transitions = transversions = total = 0
        try:
            with pysam.VariantFile(filepath, "r") as vcf_in:
                for rec in vcf_in:
                    total += 1
                    is_indel = False
                    if rec.ref and any(len(alt) != len(rec.ref) for alt in rec.alts or []):
                        indels += 1
                        is_indel = True
                    elif rec.alts:
                        snps += 1
                        
                    if not is_indel and rec.alts and len(rec.ref) == 1 and len(rec.alts[0]) == 1:
                        r, a = rec.ref.upper(), rec.alts[0].upper()
                        if (r == 'A' and a == 'G') or (r == 'G' and a == 'A') or (r == 'C' and a == 'T') or (r == 'T' and a == 'C'):
                            transitions += 1
                        else:
                            transversions += 1
            return VcfStats(
                total_variants=total, snps=snps, indels=indels,
                transitions=transitions, transversions=transversions
            )
        except Exception as e:
            raise BioFastAPIError(message=f"VCF parsing error.: {str(e)}")

    @staticmethod
    def extract_gff_features(fasta_path: str, gff_path: str, feature_type: str = None) -> str:
        from Bio import SeqIO
        records = SeqIO.to_dict(SeqIO.parse(fasta_path, "fasta"))
        extracted_fasta = []
        try:
            with open(gff_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('#') or not line.strip():
                        continue
                    parts = line.strip().split('\t')
                    if len(parts) >= 9:
                        seq_id, f_type, start, end, strand, attr = parts[0], parts[2], int(parts[3]), int(parts[4]), parts[6], parts[8]
                        if feature_type and f_type.lower() != feature_type.lower():
                            continue
                        if seq_id in records:
                            sub_record = records[seq_id][start - 1:end] # 1 based to 0 index
                            if strand == '-':
                                sub_record.seq = sub_record.seq.reverse_complement()
                            sub_record.id = f"{seq_id}_{start}_{end}_{f_type}"
                            sub_record.description = attr
                            extracted_fasta.append(sub_record.format("fasta"))
            return "".join(extracted_fasta)
        except Exception as e:
            raise BioFastAPIError(message=f"Failed to extract GFF features: {str(e)}")

    @staticmethod
    def extract_vcf_variants(vcf_path: str, variant_type: str = "ALL") -> list[dict]:
        import pysam
        extracted = []
        try:
            with pysam.VariantFile(vcf_path, "r") as vcf_in:
                for rec in vcf_in:
                    is_indel = rec.ref and any(len(alt) != len(rec.ref) for alt in rec.alts or [])
                    c_type = "INDEL" if is_indel else "SNP"
                    
                    if variant_type.upper() == "ALL" or c_type == variant_type.upper():
                        extracted.append({
                            "chrom": rec.chrom,
                            "pos": rec.pos,
                            "id": rec.id,
                            "ref": rec.ref,
                            "alts": list(rec.alts) if rec.alts else [],
                            "type": c_type,
                            "qual": rec.qual
                        })
            return extracted
        except Exception as e:
            raise BioFastAPIError(message=f"Failed to extract VCF. {str(e)}")
