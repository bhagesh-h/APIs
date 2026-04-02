import os
import tempfile
from fastapi import UploadFile
from Bio import SeqIO
from app.schemas.conversion import SupportedSourceFormat, SupportedTargetFormat, ConversionResult, ConversionWarning
from app.core.errors import BioFastAPIError

class ConversionService:
    @classmethod
    async def convert(
        cls, 
        file: UploadFile, 
        source_format: SupportedSourceFormat, 
        target_format: SupportedTargetFormat
    ) -> tuple[str, ConversionResult]:
        """
        Converts the uploaded file to the target format.
        Returns a tuple of (path_to_converted_file, ConversionResult).
        The caller is responsible for cleaning up the returned temporary file after sending.
        """
        # Validate conversion compatibility
        warnings = []
        if source_format == SupportedSourceFormat.fastq and target_format == SupportedTargetFormat.fasta:
            warnings.append(ConversionWarning(
                code="LOSSY_CONVERSION",
                message="Converting FASTQ to FASTA strips quality scores."
            ))
        elif source_format == SupportedSourceFormat.text and target_format != SupportedTargetFormat.fasta:
            raise BioFastAPIError(message="Text formatting can only be pseudo-converted to FASTA.")
            
        if source_format == target_format:
            raise BioFastAPIError(message="Source and target formats are the same.")

        # Read input to temp file
        fd_in, temp_in = tempfile.mkstemp(suffix=f".{source_format.value}")
        fd_out, temp_out = tempfile.mkstemp(suffix=f".{target_format.value}")
        os.close(fd_out) # Will be opened by SeqIO
        
        try:
            with os.fdopen(fd_in, 'wb') as f_in:
                while content := await file.read(1024 * 1024):
                    f_in.write(content)

            records_converted = 0

            if source_format == SupportedSourceFormat.text and target_format == SupportedTargetFormat.fasta:
                # Basic text to FASTA dummy conversion
                records_converted = cls._convert_text_to_fasta(temp_in, temp_out)
            else:
                # BioPython SeqIO conversion
                records = SeqIO.parse(temp_in, source_format.value)
                try:
                    records_converted = SeqIO.write(records, temp_out, target_format.value)
                except ValueError as e:
                    raise BioFastAPIError(message=f"Conversion failed. Data might lack required metadata for {target_format.value}. Error: {str(e)}")

            if records_converted == 0:
                raise BioFastAPIError(message="No records were successfully converted.")

            result = ConversionResult(
                filename=f"converted.{target_format.value}",
                records_converted=records_converted,
                warnings=warnings
            )
            return temp_out, result

        except BioFastAPIError:
            if os.path.exists(temp_out):
                os.remove(temp_out)
            raise
        except Exception as e:
            if os.path.exists(temp_out):
                os.remove(temp_out)
            raise BioFastAPIError(message=f"An unexpected error occurred during conversion: {str(e)}")
        finally:
            if os.path.exists(temp_in):
                os.remove(temp_in)

    @staticmethod
    def _convert_text_to_fasta(in_path: str, out_path: str) -> int:
        count = 0
        with open(in_path, 'r') as fin, open(out_path, 'w') as fout:
            # Assume each line is a sequence if it's text
            for i, line in enumerate(fin):
                seq = line.strip()
                if seq:
                    fout.write(f">seq_{i+1}\n{seq}\n")
                    count += 1
        return count

    @staticmethod
    def derive_consensus_sequence(fasta_path: str, vcf_path: str, out_path: str) -> int:
        from Bio import SeqIO
        from Bio.Seq import Seq
        from Bio.SeqRecord import SeqRecord
        import pysam
        from collections import defaultdict
        
        try:
            records = SeqIO.to_dict(SeqIO.parse(fasta_path, "fasta"))
        except Exception as e:
            raise BioFastAPIError(message=f"Failed to parse Reference FASTA: {str(e)}")
            
        variants = defaultdict(list)
        try:
            with pysam.VariantFile(vcf_path, "r") as vcf:
                for rec in vcf:
                    if rec.alts:
                        variants[rec.chrom].append(rec)
        except Exception as e:
            raise BioFastAPIError(message=f"Failed to parse VCF: {str(e)}")

        records_converted = 0
        try:
            with open(out_path, 'w') as fout:
                for seq_id, record in records.items():
                    if seq_id not in variants:
                        fout.write(record.format("fasta"))
                        records_converted += 1
                        continue
                    
                    seq_chars = list(str(record.seq))
                    # Apply from end-to-start to prevent index shifting on indels
                    chrom_vars = sorted(variants[seq_id], key=lambda x: x.pos, reverse=True)
                    for rec in chrom_vars:
                        pos = rec.pos - 1 # 1-based to 0-based
                        ref = rec.ref
                        alt = rec.alts[0]
                        # Verify we match ref to avoid reckless patching
                        if "".join(seq_chars[pos:pos+len(ref)]).upper() == ref.upper():
                            seq_chars[pos:pos+len(ref)] = list(alt)
                    
                    new_record = SeqRecord(
                        Seq("".join(seq_chars)),
                        id=f"{seq_id}_consensus",
                        description="Derived from VCF"
                    )
                    fout.write(new_record.format("fasta"))
                    records_converted += 1
            return records_converted
        except Exception as e:
            raise BioFastAPIError(message=f"Failed to derive consensus: {str(e)}")
