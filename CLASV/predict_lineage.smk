configfile: "config/config.yaml"

# Import necessary modules
from core import *
import glob
import os

# Get current working directory
cwd = os.getcwd()

# Directories for outputs
output_folder_name = config["output"]
visuals_dir = os.path.join(cwd, output_folder_name, "visuals")
predictions_dir = os.path.join(cwd, output_folder_name, "predictions")
results_dir = os.path.join(cwd, output_folder_name, "results")

# Ensure output directories exist
os.makedirs(visuals_dir, exist_ok=True)
os.makedirs(predictions_dir, exist_ok=True)
os.makedirs(results_dir, exist_ok=True)

# Input files
input_path = config["raw_seq_folder"]
all_fasta = glob.glob(os.path.join(input_path, '*.fasta'))
if not all_fasta:
    raise ValueError(f"No FASTA files found in {input_path}.")
analysis_name = [os.path.basename(x).split('.')[0] for x in all_fasta]

# Helper function to get file path
def get_path(file_name, path_list):
    for path in path_list:
        if os.path.basename(path).split('.')[0] == file_name:
            return path
    raise ValueError(f"File with name {file_name} not found in the provided path list.")

# Define the all rule
rule all:
    input:
        expand(f"{predictions_dir}/{{analysis_name}}_LASV_lin_pred.csv", analysis_name=analysis_name),
        expand(f"{visuals_dir}/{{analysis_name}}_LASV_lin_pred.html", analysis_name=analysis_name)

# Rule: Align and Extract Region
rule align_and_extract_region:
    input:
        sequences=lambda wildcards: get_path(wildcards.analysis_name, all_fasta),
        reference=config["reference"]
    output:
        sequences=f"{results_dir}/{{analysis_name}}_extracted_GPC_sequences.fasta"
    params:
        min_length=config["filter"]["min_length"]
    shell:
        """
        nextclade run \
           -j 2 \
           --input-ref {input.reference} \
           --output-fasta {output.sequences} \
           --min-seed-cover 0.01 \
           --min-length {params.min_length} \
           --silent \
           {input.sequences} || touch {output.sequences}
        """

# Rule: Convert Nucleotide to Amino Acid
rule convert_nt_to_aa:
    input:
        sequences=f"{results_dir}/{{analysis_name}}_extracted_GPC_sequences.fasta"
    output:
        sequences=f"{results_dir}/{{analysis_name}}_extracted_GPC_sequences_aa.fasta"
    run:
        translate_alignment(input.sequences, output.sequences)

# Rule: Encode Sequences
rule encode_sequences:
    input:
        sequences=f"{results_dir}/{{analysis_name}}_extracted_GPC_sequences_aa.fasta"
    output:
        encoding=f"{results_dir}/{{analysis_name}}_extracted_GPC_sequences_aa_encoded.csv"
    run:
        onehot_alignment_aa(input.sequences, output.encoding)

# Rule: Make Predictions and Save
rule make_predictions_save:
    input:
        encoding=f"{results_dir}/{{analysis_name}}_extracted_GPC_sequences_aa_encoded.csv"
    output:
        prediction=f"{predictions_dir}/{{analysis_name}}_LASV_lin_pred.csv"
    params:
        model_path=config["model"]
    run:
        model = MakePredictions(params.model_path)
        model.predict(input.encoding, output.prediction)

# Rule: Generate Statistics
rule statistics:
    input:
        prediction=f"{predictions_dir}/{{analysis_name}}_LASV_lin_pred.csv"
    output:
        figures=f"{visuals_dir}/{{analysis_name}}_LASV_lin_pred.html"
    params:
        figures_title=config["figures_title"]
    run:
        plot_lineage_data(
            csv_file=input.prediction,
            title=params.figures_title,
            output_html=output.figures
        )
