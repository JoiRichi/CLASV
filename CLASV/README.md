# CLASV: Classification of Lassa Virus

![Python Version](https://img.shields.io/badge/python-3.11-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-stable-brightgreen.svg)

## Overview
CLASV (Classification of Lassa Virus) is a tool for predicting Lassa virus lineages from genomic sequences. It uses a random forest model trained on glycoprotein precursor (GPC) sequences to classify Lassa virus isolates into their respective lineages.

Information on the research can be found in our [publication](#).

## Project Repositories
- **Data and Processing:** [LASV_ML_Manuscript_Data](https://github.com/JoiRichi/LASV_ML_manuscript_data)
- **Lassa Virus Lineage Prediction:** [CLASV_GITHUB](https://github.com/JoiRichi/CLASV)

## Prediction Pipeline Overview
![CLASV](predflow.png)

## ⚠️ Installation Guide ⚠️

### Step 1: Install Python 3.11
**CLASV requires Python 3.11 for optimal compatibility.**

- **macOS/Linux**: Download from [Python.org](https://www.python.org/downloads/release/python-3110/) or use a package manager:
  ```sh
  # macOS with Homebrew
  brew install python@3.11
  
  # Ubuntu/Debian
  sudo apt update
  sudo apt install python3.11 python3.11-venv python3.11-dev
  ```

- **Windows**: Download and run the installer from [Python.org](https://www.python.org/downloads/release/python-3110/). Be sure to check "Add Python 3.11 to PATH" during installation.

### Step 2: Create a Virtual Environment
```sh
# Create a dedicated directory for your project (optional)
mkdir clasv_project
cd clasv_project

# Create a virtual environment
python3.11 -m venv clasv_env

# Activate the virtual environment
# On macOS/Linux:
source clasv_env/bin/activate
# On Windows:
# clasv_env\Scripts\activate
```

### Step 3: Install CLASV
With your virtual environment activated:
```sh
# Update pip to the latest version
pip install --upgrade pip

# Install CLASV
pip install clasv
```

### Step 4: Verify Installation
```sh
# Check that CLASV is installed
clasv --version

# Test the help command
clasv -h
```

## Running the Pipeline

The main command for CLASV is `find-lassa`. This is how you run it:

```sh
# Basic usage
clasv find-lassa --input myinputfolderpath --output mychosenfolderpath --cores 4 --minlength 500

# Find Fasta files recursively
clasv find-lassa --input myinputfolderpath --output mychosenfolderpath --cores 4 --recursive 

# Force rerun
clasv find-lassa --input myinputfolderpath --output mychosenfolderpath --cores 4 --force
```

Upon completion, go to the pipeline 'visuals' folder and open the html files in a browser.

## Benchmarking

CLASV includes a powerful benchmark tool for scientific publication-grade performance evaluation.

### Running Benchmarks

```sh
# Basic benchmark
clasv-benchmark --input /path/to/fasta/files --output /path/to/output/dir

# Advanced options
clasv-benchmark --input /path/to/fasta/files --output /path/to/output/dir --cores 8 --iterations 5
```

### Benchmark Outputs

- A comprehensive HTML report with visualizations
- Detailed CSV files with timing information
- Step-by-step breakdown of pipeline performance
- System information and configuration details

For more information, see the [benchmarking documentation](tools/README-benchmark.md).

## Technical Documentation

### Command Line Interface Options

#### CLASV Pipeline
```sh
clasv find-lassa [options]
```
Options:
- `--input`: Path to the input folder containing FASTA files (required)
- `--output`: Path to the output folder for results (required)
- `--recursive`: Search input folder recursively for FASTA files
- `--cores`: Number of CPU cores to use (default: 4)
- `--force`: Force rerun of all pipeline steps
- `--minlength`: Minimum length of GPC sequences to consider (default: 500)
- `--version`: Show the version number and exit

#### Benchmark Tool
```sh
clasv-benchmark [options]
```
Options:
- `--input`: Directory containing FASTA files to benchmark (required)
- `--output`: Directory to store benchmark results (required)
- `--cores`: Number of CPU cores to use (default: 4)
- `--minlength`: Minimum sequence length filter (default: 500)
- `--iterations`: Number of iterations for each test (default: 3)
- `--quiet`: Suppress detailed output

### Pipeline Workflow
1. **Dependency Check**: Verifies Nextclade and Seqkit are installed or installs them automatically
2. **Preprocessing**: Collects and prepares input FASTA files
3. **Alignment & Extraction**: Uses Nextclade to align sequences and extract GPC regions
4. **Translation**: Translates nucleotide sequences to amino acids
5. **Encoding**: One-hot encodes amino acid sequences
6. **Prediction**: Applies Random Forest model to predict Lassa virus lineages
7. **Visualization**: Generates plots and visualizations of prediction results

### Directory Structure
After running the pipeline, the output folder will contain:
- `results/`: Intermediate files from the pipeline
  - `preprocessed/`: Preprocessed input files
  - `*_extracted_GPC_sequences.fasta`: Extracted GPC sequences
  - `*_extracted_GPC_sequences_aa.fasta`: Translated amino acid sequences
  - `*_extracted_GPC_sequences_aa_encoded.csv`: Encoded sequences
- `predictions/`: CSV files containing lineage predictions
- `visuals/`: HTML visualization files

## Troubleshooting

### Common Issues

1. **Python Version Issues**: If you encounter errors during installation or runtime, ensure you are using Python 3.11.
   ```sh
   python --version
   ```

2. **Nextclade Installation Failure**: If Nextclade fails to install automatically:
   - Ensure you have appropriate permissions
   - Try running the CLASV command again
   - Consider installing Nextclade [manually](https://docs.nextstrain.org/projects/nextclade/en/stable/user/nextclade-cli.html)

3. **Snakemake Compatibility**: If you encounter Snakemake errors, trying reinstalling CLASV in a fresh virtual environment with Python 3.11.

4. **Memory Issues**: For large datasets, increase available memory or process files in smaller batches.

## Citation

If you use CLASV in your research, please cite our paper:

```
[Citation information will be added upon publication]
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Nextclade](https://docs.nextstrain.org/projects/nextclade/en/stable/) for sequence alignment
- [Seqkit](https://bioinf.shenwei.me/seqkit/) for sequence manipulation
- All contributors and testers who helped improve this tool 