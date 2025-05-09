# CLASV

## Overview
Lassa virus lineage prediction based on random forest.

Information on the research can be found here: 
https://github.com/JoiRichi/CLASV

## Project Repositories
- **Data and Processing:** [LASV_ML_Manuscript_Data](https://github.com/JoiRichi/LASV_ML_manuscript_data)
- **Lassa Virus Lineage Prediction:** [CLASV_GITHUB](https://github.com/JoiRichi/CLASV)

## Jupyter Notebooks on Google Colab
- **General Preprocessing:** [Notebook Link](https://colab.research.google.com/drive/1JOgS2-dDoQ7OPHPcXm3AIBDnGQAFxIyR)
- **Lassa Virus Lineage Prediction Training:** [Notebook Link](https://colab.research.google.com/drive/11U0NbLCTi_l0OaW6Vjil0g4evNHJHnWT?usp=share_link)

## Prediction Pipeline Overview
![CLASV](predflow.png)

## Installation Guide

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

### Step 2: Verify Python Installation
Confirm that Python 3.11 is installed correctly:
```sh
python3.11 --version
# Should output: Python 3.11.x
```

### Step 3: Create a Virtual Environment
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

# Confirm you're using Python 3.11 in the virtual environment
python --version
# Should output: Python 3.11.x
```

### Step 4: Install CLASV
With your virtual environment activated:
```sh
# Update pip to the latest version
pip install --upgrade pip

# Install CLASV
pip install clasv
```

### Step 5: Verify Installation
```sh
# Check that CLASV is installed
clasv --version

# Test the help command
clasv -h
```

### Troubleshooting Installation
- If you encounter errors with dependencies, try installing in a fresh virtual environment.
- If Nextclade fails to install automatically, run your CLASV command again, as it attempts installation on first use.
- For Snakemake-related errors, ensure you're using Python 3.11 as other versions may have compatibility issues.

## Running the Pipeline

The main command for CLASV is `find-lassa`. This is how you run it:

```sh
clasv find-lassa --input myinputfolderpath --output mychosenfolderpath --cores 4 --minlength 500 #default 
```

Find Fasta files in the input directory and subdirectories recursively:

```sh
# 
clasv find-lassa --input myinputfolderpath --output mychosenfolderpath  --cores 4 --recursive #Add the recursive flag
```


Force rerun:

```sh
# 
clasv find-lassa --input myinputfolderpath --output mychosenfolderpath --cores 4 --force #add the force flag
```


Upon completion, go to the pipeline 'visuals' folder and open the html files in a browser.


## Customization

This pipeline has the ability to process multiple FASTA files containing multiple sequences with proficiency and speed. It is recommended that multiple FASTA files are concatenated into one; however, this is not compulsory, especially if the projects are different. By default, the pipeline finds all files with the extension `.fasta` in your **input_folder** folder and tries to find LASV GPC sequences in the files. 

To ensure Snakemake has a memory of what files have been checked, intermediary files are created for all files checked, even if they contain no GPC sequences. However, those files would be empty.

### Important Outputs

At the end of the run, you can check the **predictions** folder for the CSV files containing the predictions per sample. A visualization of the prediction can be found in the **visuals** folder. Open the HTML files in a browser. The images are high quality and reactive, allowing you to hover over them to see more information.

For further details, please refer to the respective notebooks and repositories linked above. You can also leave a comment for help regarding the pipeline.

## Technical Documentation

### Command Line Interface Options
The CLASV tool provides the following command-line options:

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

### Pipeline Workflow
CLASV executes the following sequence of operations:

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

## Model training

Learn how the data was preprocessed here: [LASV_ML_Manuscript_Data](https://github.com/JoiRichi/LASV_ML_manuscript_data). Training process here [Notebook Link](https://colab.research.google.com/drive/11U0NbLCTi_l0OaW6Vjil0g4evNHJHnWT?usp=share_link).

