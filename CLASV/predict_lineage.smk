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

recursive = config["recursive"]
print(recursive)
if recursive:
    all_fasta = glob.glob(os.path.join(input_path, '**', '*.fasta'), recursive = True)
else:
    all_fasta = glob.glob(os.path.join(input_path, '*.fasta'))


if not all_fasta:
    raise ValueError(f"No FASTA files found in {input_path}.")
else:
    print(f"Found {len(all_fasta)} FASTA file(s) in {input_path}.")


analysis_name = [os.path.basename(x).split('.')[0] for x in all_fasta]


def create_dummy(path):
    with open(path, "w") as placeholder_file:
        placeholder_file.write("")



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
    log:
        align_log=f"{results_dir}/{{analysis_name}}_align.log"
    shell:
        """
        nextclade run \
           -j 2 \
           --input-ref "{input.reference}" \
           --output-fasta "{output.sequences}" \
           --min-seed-cover 0.01 \
           --min-length {params.min_length} \
           --silent \
           "{input.sequences}" > "{log.align_log}" 2>&1 || touch "{output.sequences}"
        """

# Rule: Convert Nucleotide to Amino Acid
rule convert_nt_to_aa:
    input:
        sequences=f"{results_dir}/{{analysis_name}}_extracted_GPC_sequences.fasta"
    output:
        sequences=f"{results_dir}/{{analysis_name}}_extracted_GPC_sequences_aa.fasta"
    log:
        convert_log=f"{results_dir}/{{analysis_name}}_convert.log"
    run:
        try:
            translate_alignment(input.sequences, output.sequences)
        except Exception as e:
            with open(log.convert_log, "a") as log_file:
                log_file.write(f"Error in convert_nt_to_aa for {wildcards.analysis_name}: {e}\n")
            create_dummy(output.sequences)

# Rule: Encode Sequences
rule encode_sequences:
    input:
        sequences=f"{results_dir}/{{analysis_name}}_extracted_GPC_sequences_aa.fasta"
    output:
        encoding=f"{results_dir}/{{analysis_name}}_extracted_GPC_sequences_aa_encoded.csv"
    log:
        encode_log=f"{results_dir}/{{analysis_name}}_encode.log"
    run:
        try:
            onehot_alignment_aa(input.sequences, output.encoding)
        except Exception as e:
            with open(log.encode_log, "a") as log_file:
                log_file.write(f"Error in encode_sequences for {wildcards.analysis_name}: {e}\n")
            create_dummy(output.encoding)

# Rule: Make Predictions and Save
rule make_predictions_save:
    input:
        encoding=f"{results_dir}/{{analysis_name}}_extracted_GPC_sequences_aa_encoded.csv"
    output:
        prediction=f"{predictions_dir}/{{analysis_name}}_LASV_lin_pred.csv"
    params:
        model_path=config["model"]
    log:
        prediction_log=f"{results_dir}/{{analysis_name}}_predict.log"
    run:
        model = MakePredictions(params.model_path)
        try:
            model.predict(input.encoding, output.prediction)
        except Exception as e:
            with open(log.prediction_log, "a") as log_file:
                log_file.write(f"Error in make_predictions_save for {wildcards.analysis_name}: {e}\n")
            create_dummy(output.prediction)

# Rule: Generate Statistics
rule statistics:
    input:
        prediction=f"{predictions_dir}/{{analysis_name}}_LASV_lin_pred.csv"
    output:
        figures=f"{visuals_dir}/{{analysis_name}}_LASV_lin_pred.html"
    params:
        figures_title=config["figures_title"]
    log:
        statistics_log=f"{results_dir}/{{analysis_name}}_stats.log"
    run:
        try:
            plot_lineage_data(
                csv_file=input.prediction,
                title=params.figures_title,
                output_html=output.figures
            )
        except Exception as e:
            with open(log.statistics_log, "a") as log_file:
                log_file.write(f"Error in statistics for {wildcards.analysis_name}: {e}\n")
            create_dummy(output.figures)
