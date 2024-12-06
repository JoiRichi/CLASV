import os
import subprocess
from importlib.resources import files

def main():
    # Get the current working directory
    cwd = os.getcwd()

    # Ensure required directories (e.g., visuals, predictions) are created in the current working directory
    output_dirs = ["visuals", "predictions", "results"]
    for dir_name in output_dirs:
        dir_path = os.path.join(cwd, dir_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"Created directory: {dir_path}")

    # Locate the Snakefile and config.yaml within the package
    try:
        snakefile = files("CLASV").joinpath("predict_lineage.smk")
        config_file = files("CLASV").joinpath("config/config.yaml")
    except Exception as e:
        raise FileNotFoundError(f"Failed to locate necessary files: {e}")

    # Ensure the Snakefile exists
    if not snakefile.exists():
        raise FileNotFoundError(f"Snakefile not found at {snakefile}")

    # Run Snakemake with verbose output
    command = [
        "snakemake",
        "-s", str(snakefile),
        "--configfile", str(config_file),
        "--cores", "5",
        "--printshellcmds",  # Print executed shell commands
        "--verbose",         # Enable verbose mode
    ]
    print(f"Running pipeline with Snakefile at {snakefile}...")
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Snakemake pipeline failed with error: {e}")
