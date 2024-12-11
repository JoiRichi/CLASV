import os
import yaml
import glob
from pathlib import Path
import subprocess


def update_config(input_folder, output_folder, recursive):
    """
    Updates the `config.yaml` file with the provided input and output folders.
    """
    # Resolve the path to the `config.yaml` dynamically
    library_path = Path(__file__).resolve().parent
    config_path = library_path / "config/config.yaml"
    reference_path = library_path / "config/NC_004296.fasta"
    model_path = library_path / "config/RF_LASV_lineage_n1000_aa.joblib"
    
    print(f"Config path resolved to: {config_path}")

    # Ensure the config directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Read or create the configuration
    if config_path.exists():
        with config_path.open("r") as file:
            config = yaml.safe_load(file) or {}
    else:
        print(f"Warning: Config file {config_path} does not exist. A new one will be created.")
        config = {}

    # Update the configuration
    config["raw_seq_folder"] = str(input_folder)
    config["output"] = str(output_folder)
    config["reference"] = str(reference_path)
    config["filter"] = {"min_length": 500}
    config["model"] = str(model_path)
    config["figures_title"] = "LASV Lineage Prediction"
    config["recursive"] = True if recursive else False

    # Save the updated configuration
    with config_path.open("w") as config_file:
        yaml.dump(config, config_file)

    print(f"Config updated successfully at {config_path}")


def run_pipeline(input_folder, output_folder, recursive, cores, force):
    """
    Runs the Snakemake pipeline with the specified parameters.
    """
    # Resolve paths for input and output
    input_path = Path(input_folder).resolve()
    output_path = Path(output_folder).resolve()

    # Resolve library paths
    library_path = Path(__file__).resolve().parent
    snakefile_path = library_path / "predict_lineage.smk"
    config_path = library_path / "config/config.yaml"

    # Validate paths
    if not input_path.exists():
        print(f"Error: Input folder '{input_path}' does not exist.")
        exit(1)

    if not snakefile_path.exists():
        print(f"Error: Snakefile '{snakefile_path}' does not exist.")
        exit(1)

    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)

    # Update configuration and collect FASTA files
    update_config(input_path, output_path, recursive)
    
    # Construct the Snakemake command
    snakemake_command = [
        "snakemake",
        "-s", str(snakefile_path),
        "--configfile", str(config_path),
        "--cores", str(cores),
    ]
    if force:
        snakemake_command.append("--forceall")

    # Run Snakemake
    print(f"Running Snakemake with command: {' '.join(snakemake_command)}")
    try:
        subprocess.run(snakemake_command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Snakemake: {e}")
        exit(1)
