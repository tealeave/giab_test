#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
import gzip
import shutil
import pysam
from pathlib import Path

def validate_file(path: str, description: str) -> Path:
    """Validate file exists and is readable"""
    path = Path(path)
    if not path.exists():
        sys.exit(f"Error: {description} file not found at {path}")
    if not os.access(path, os.R_OK):
        sys.exit(f"Error: Cannot read {description} file at {path}")
    return path

def validate_bam(bam_path: Path) -> None:
    """Validate BAM file format and index using pysam"""
    try:
        with pysam.AlignmentFile(str(bam_path), "rb") as bam:
            if not bam.check_index():
                sys.exit(f"Error: BAM file {bam_path} is not indexed")
    except ValueError as e:
        sys.exit(f"Error: Invalid BAM file {bam_path}: {str(e)}")
    except Exception as e:
        sys.exit(f"Error validating BAM file {bam_path}: {str(e)}")

def create_directory(dir_path: str) -> Path:
    """Create directory if it doesn't exist"""
    dir_path = Path(dir_path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path

def run_mosdepth(bed: Path, bam: Path, output_prefix: str, intermediates_dir: Path) -> Path:
    """Execute mosdepth command and return path to regions.bed.gz"""
    print(f"Running mosdepth on {bam} using regions from {bed}...")
    cmd = [
        "mosdepth",
        "--by", str(bed),
        "-x",
        "-n",
        str(intermediates_dir / output_prefix),
        str(bam)
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        sys.exit(f"mosdepth failed: {e.stderr}")
    except FileNotFoundError:
        sys.exit("Error: mosdepth not found in PATH")

    return intermediates_dir / f"{output_prefix}.regions.bed.gz"

def process_coverage_file(regions_gz: Path, output_file: Path):
    """Extract coverage data from compressed regions file"""
    print(f"Processing coverage data from {regions_gz}...")
    try:
        with gzip.open(regions_gz, 'rt') as f_in:
            with open(output_file, 'w') as f_out:
                for line in f_in:
                    f_out.write(line)
    except Exception as e:
        sys.exit(f"Error processing coverage file: {str(e)}")

def main():
    parser = argparse.ArgumentParser(
        add_help=False,  # We'll add our own help with alias
        description="Calculate coverage metrics from BED and BAM files using mosdepth")
    
    # Required arguments
    parser.add_argument("--bed", required=True,
                        help="Input BED file",
                        default="Bed_and_Bam_file/test_fixed.bed")
    parser.add_argument("--bam", required=True,
                        help="Input BAM file")
    parser.add_argument("--output-prefix", required=True,
                        help="Output file prefix")
    
    # Optional arguments
    parser.add_argument("--full-bed", action="store_true",
                        help="Use full Twist Exome Core Covered Targets bed file")
    parser.add_argument("--keep-intermediates", action="store_true",
                        help="Keep intermediate files")
    # Add help with alias
    parser.add_argument("-h", "--help", "--hlep", action="help", default=argparse.SUPPRESS,
                      help="Show this help message and exit")
    
    args = parser.parse_args()

    print("Validating input files...")
    # Set up directories
    intermediates_dir = create_directory("Intermediate_Files")
    results_dir = create_directory("Result_cov_file")

    # Validate inputs
    bed_file = validate_file(args.bed, "BED")
    bam_file = validate_file(args.bam, "BAM")
    validate_bam(bam_file)

    # Run mosdepth
    regions_gz = run_mosdepth(bed_file, bam_file, args.output_prefix, intermediates_dir)

    # Process output
    output_file = results_dir / f"{args.output_prefix}.coverage.bed"
    process_coverage_file(regions_gz, output_file)

    # Cleanup if requested
    if not args.keep_intermediates:
        print("Cleaning up intermediate files...")
        for f in intermediates_dir.glob(f"{args.output_prefix}*"):
            if f != regions_gz:  # Keep the regions file we just processed
                f.unlink()

    print(f"Successfully created coverage file at {output_file}")

if __name__ == "__main__":
    main()