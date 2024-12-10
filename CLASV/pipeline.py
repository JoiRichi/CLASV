import os
import yaml
import glob
from pathlib import Path

def update_config(input_folder, output_folder, recursive):
    """
    Updates the `config.yaml` file with the provided input and output folders.
    """
    
    
    config_path = "CLASV/config/config.yaml"
    if os.path.exists(config_path):
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)
    else:
        config = {}

    config["raw_seq_folder"] = input_folder
    config["output"] = output_folder


    with open(config_path, "w") as config_file:
        yaml.dump(config, config_file)

def collect_fasta_files(input_folder, recursive):
    if recursive:
        all_fasta = glob.glob(f"{input_folder}/**/*.fasta", recursive=True)
    else:
        all_fasta = glob.glob(f"{input_folder}/*.fasta")

    if not all_fasta:
        print(f"No FASTA files found in {input_folder} (recursive={recursive}).")
        exit(1)

    print(f"Found {len(all_fasta)} FASTA file(s) in {input_folder}.")
    return all_fasta

def run_pipeline(input_folder, output_folder, recursive, cores, force):
    if not os.path.exists(input_folder):
        print(os.path.exists(input_folder))
        print(f"Error: Input folder '{input_folder}' does not exist.")
        exit(1)

    update_config(input_folder, output_folder, recursive)
    collect_fasta_files(input_folder, recursive)

    snakemake_command = f"snakemake -s CLASV/predict_lineage.smk --cores {cores}"
    if force:
        snakemake_command += " --forceall"

    print(f"Running Snakemake with command: {snakemake_command}")
    os.system(snakemake_command)
