configfile: "CLASV/config/config.yaml"

# Include necessary imports
from core import *
import glob
import os

# Get the current working directory for outputs
cwd = os.getcwd()
output_folder_name = config["output"]
# Directories for outputs
visuals_dir = os.path.join(cwd, output_folder_name, "visuals")
predictions_dir = os.path.join(cwd,output_folder_name, "predictions")
results_dir = os.path.join(cwd,output_folder_name, "results")

# Ensure directories exist
os.makedirs(visuals_dir, exist_ok=True)
os.makedirs(predictions_dir, exist_ok=True)
os.makedirs(results_dir, exist_ok=True)

# Input files
input_path = config["raw_seq_folder"]
all_fasta = glob.glob(os.path.join(input_path, '*.fasta'))
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

# Define rule align_and_extract_region
rule align_and_extract_region:
    input:
        sequences=lambda wildcards: get_path(wildcards.analysis_name, all_fasta),
        reference="CLASV/config/NC_004296.fasta"
    output:
        sequences=f"{results_dir}/{{analysis_name}}_extracted_GPC_sequences.fasta"
    params:
        min_length=config["filter"]['min_length']
    run:
        try:
            shell("""
                nextclade run \
                   -j 2 \
                   --input-ref {input.reference} \
                   --output-fasta {output.sequences} \
                   --min-seed-cover 0.01 \
                   --min-length {params.min_length} \
                   --silent \
                   {input.sequences}
            """)
        except Exception as e:
            print(f"Error in align_and_extract_region for {wildcards.analysis_name}: {e}")
            shell("touch {output.sequences}")

# Define rule convert_nt_to_aa
rule convert_nt_to_aa:
    input:
        sequences=f"{results_dir}/{{analysis_name}}_extracted_GPC_sequences.fasta"
    output:
        sequences=f"{results_dir}/{{analysis_name}}_extracted_GPC_sequences_aa.fasta"
    run:
        try:
            translate_alignment(input.sequences, output.sequences)
        except Exception as e:
            print(f"Error in convert_nt_to_aa for {wildcards.analysis_name}: {e}")
            shell("touch {output.sequences}")

# Define rule encode_sequences
rule encode_sequences:
    input:
        sequences=f"{results_dir}/{{analysis_name}}_extracted_GPC_sequences_aa.fasta"
    output:
        encoding=f"{results_dir}/{{analysis_name}}_extracted_GPC_sequences_aa_encoded.csv"
    run:
        try:
            onehot_alignment_aa(input.sequences, output.encoding)
        except Exception as e:
            print(f"Error in encode_sequences for {wildcards.analysis_name}: {e}")
            shell("touch {output.encoding}")

# Define rule make_predictions_save
rule make_predictions_save:
    input:
        encoding=f"{results_dir}/{{analysis_name}}_extracted_GPC_sequences_aa_encoded.csv"
    output:
        prediction=f"{predictions_dir}/{{analysis_name}}_LASV_lin_pred.csv"
    params:
        model_path=config["model"]
    run:
        try:
            model = MakePredictions(params.model_path)
            model.predict(input.encoding, output.prediction)
        except Exception as e:
            print(f"Error in make_predictions_save for {wildcards.analysis_name}: {e}")
            shell("touch {output.prediction}")

# Define rule statistics
rule statistics:
    input:
        prediction=f"{predictions_dir}/{{analysis_name}}_LASV_lin_pred.csv"
    output:
        figures=f"{visuals_dir}/{{analysis_name}}_LASV_lin_pred.html"
    params:
        figures_title=config["figures_title"]
    run:
        try:
            plot_lineage_data(
                csv_file=input.prediction,
                title=params.figures_title,
                output_html=output.figures
            )
        except Exception as e:
            print(f"Error in statistics for {wildcards.analysis_name}: {e}")
            shell("touch {output.figures}")
