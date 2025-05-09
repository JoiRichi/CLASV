import os
import yaml
import glob
from pathlib import Path
import subprocess
import sys


def validate_inputs(input_folder, output_folder):
    """
    Validates input and output folders.
    Returns True if valid, raises ValueError with informative message if not.
    """
    input_path = Path(input_folder).resolve()
    output_path = Path(output_folder).resolve()
    
    # Check if input folder exists
    if not input_path.exists():
        raise ValueError(f"Input folder does not exist: {input_path}")
    if not input_path.is_dir():
        raise ValueError(f"Input path is not a directory: {input_path}")
        
    # Check if output folder can be created or exists
    try:
        output_path.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        raise ValueError(f"Permission denied when creating output folder: {output_path}")
    except Exception as e:
        raise ValueError(f"Error creating output folder: {e}")
    
    return True


def update_config(input_folder, output_folder, recursive, minlength, include_fastq):
    """
    Updates the `config.yaml` file with the provided input and output folders.
    """
    # Resolve the path to the `config.yaml` dynamically
    library_path = Path(__file__).resolve().parent
    config_path = library_path / "config/config.yaml"
    reference_path = library_path / "config/NC_004296.fasta"
    model_path = library_path / "config/RF_LASV_lineage_n500_aa.joblib"
    
    print(f"Config path resolved to: {config_path}")

    # Ensure the config directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Validate crucial files
    if not reference_path.exists():
        raise FileNotFoundError(f"Reference genome file not found: {reference_path}")
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")

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
    config["filter"] = {"min_length": int(minlength)}
    config["model"] = str(model_path)
    config["figures_title"] = "LASV Lineage Prediction"
    config["recursive"] = True if recursive else False
    config["include_fastq"] = True if include_fastq else False

    # Save the updated configuration
    with config_path.open("w") as config_file:
        yaml.dump(config, config_file)

    print(f"Config updated successfully at {config_path}")


def run_pipeline(input_folder, output_folder, recursive, cores, force, minlength, include_fastq):
    """
    Runs the Snakemake pipeline with the specified parameters.
    """
    try:
        # Validate inputs
        validate_inputs(input_folder, output_folder)
        
        # Resolve paths for input and output
        input_path = Path(input_folder).resolve()
        output_path = Path(output_folder).resolve()

        # Resolve library paths
        library_path = Path(__file__).resolve().parent
        snakefile_path = library_path / "predict_lineage.smk"
        config_path = library_path / "config/config.yaml"

        # Create output directory if it doesn't exist
        output_path.mkdir(parents=True, exist_ok=True)

        # Update configuration and collect FASTA files
        update_config(input_path, output_path, recursive, minlength, include_fastq)
        
        # Construct the Snakemake command
        snakemake_command = [
            "snakemake",
            "-s", str(snakefile_path),
            "--configfile", str(config_path),
            "--cores", str(cores),
            "--rerun-incomplete", #always rerun incomplete files
        ]
        if force:
            snakemake_command.append("--forceall")

        # Run Snakemake
        print(f"Running Snakemake with command: {' '.join(snakemake_command)}")
        try:
            result = subprocess.run(snakemake_command, check=True, capture_output=True, text=True)
            print("Pipeline completed successfully!")
            print(f"Results are available in: {output_path}")
            print("Prediction files are in the 'predictions' directory.")
            print("Visualization files are in the 'visuals' directory.")
        except subprocess.CalledProcessError as e:
            print(f"Error running Snakemake: {e}")
            if e.stderr:
                print(f"Error details: {e.stderr}")
            sys.exit(1)
    except Exception as e:
        print(f"Error in pipeline execution: {e}")
        sys.exit(1)
