# BED/BAM Coverage Analysis Tool

Calculates coverage metrics from BED and BAM files using mosdepth.

## Requirements
- Python 3.8+
- mosdepth 0.3.11 or later

## Installation
https://github.com/brentp/mosdepth

## Usage
```bash
python3 src/main.py --bed Bed_and_Bam_file/test_fixed.bed \
                   --bam Bed_and_Bam_file/RMNISTHS_30xdownsample.bam \
                   --output-prefix test_output
```

## Options
- `--bed`: Input BED file (default: Bed_and_Bam_file/test_fixed.bed)
- `--bam`: Input BAM file (required)
- `--output-prefix`: Output file prefix (required)
- `--full-bed`: Use full Twist Exome Core Covered Targets bed file
- `--keep-intermediates`: Keep intermediate files

## Output Files
- `Result_cov_file/<prefix>.coverage.bed`: Final coverage results
- `Intermediate_Files/<prefix>.*`: Temporary files (removed by default)

## Example Output
```
Validating input files...
Running mosdepth on Bed_and_Bam_file/RMNISTHS_30xdownsample.bam using regions from Bed_and_Bam_file/test_fixed.bed...
Processing coverage data from Intermediate_Files/test_output.regions.bed.gz...
Successfully created coverage file at Result_cov_file/test_output.coverage.bed
