# Snakefile
configfile: "config/config.yaml"

# Include necessary imports
from core import *
import glob
import os

input_path = config["raw_seq_folder"]
all_fasta = glob.glob(os.path.join(input_path, '*.fasta'))
analysis_name = [os.path.basename(x).split('.')[0] for x in all_fasta]

def get_path(file_name, path_list):
    for path in path_list:
        if os.path.basename(path).split('.')[0] == file_name:
            return path
    raise ValueError(f"File with name {file_name} not found in the provided path list.")

# Define the all rule
rule all:
    input:
        expand("predictions/{analysis_name}_LASV_lin_pred.csv", analysis_name=analysis_name),
        expand("visuals/{analysis_name}_LASV_lin_pred.html", analysis_name=analysis_name)

# Define rule align_and_extract_region
rule align_and_extract_region:
    input:
        sequences = lambda wildcards: get_path(wildcards.analysis_name, all_fasta),
        reference = "config/NC_004296.fasta"
    output:
        sequences = "results/{analysis_name}_extracted_GPC_sequences.fasta"
    params:
        min_length = config["filter"]['min_length']
    run:
        try:
            shell("""
                nextclade3 run \
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
            # Create empty output file to allow workflow continuation
            shell("touch {output.sequences}")

# Define rule convert_nt_to_aa
rule convert_nt_to_aa:
    input:
        sequences = "results/{analysis_name}_extracted_GPC_sequences.fasta"
    output:
        sequences = "results/{analysis_name}_extracted_GPC_sequences_aa.fasta"
    run:
        try:
            translate_alignment(input.sequences, output.sequences)
        except Exception as e:
            print(f"Error in convert_nt_to_aa for {wildcards.analysis_name}: {e}")
            # Create empty output file to allow workflow continuation
            shell("touch {output.sequences}")

# Define rule encode_sequences
rule encode_sequences:
    input:
        sequences = "results/{analysis_name}_extracted_GPC_sequences_aa.fasta"
    output:
        encoding = "results/{analysis_name}_extracted_GPC_sequences_aa_encoded.csv"
    run:
        try:
            onehot_alignment_aa(input.sequences, output.encoding)
        except Exception as e:
            print(f"Error in encode_sequences for {wildcards.analysis_name}: {e}")
            # Create empty output file to allow workflow continuation
            shell("touch {output.encoding}")

# Define rule make_predictions_save
rule make_predictions_save:
    input:
        encoding = "results/{analysis_name}_extracted_GPC_sequences_aa_encoded.csv"
    output:
        prediction = "predictions/{analysis_name}_LASV_lin_pred.csv"
    params:
        model_path = config["model"]
    run:
        try:
            model = MakePredictions(params.model_path)
            model.predict(input.encoding, output.prediction)
        except Exception as e:
            print(f"Error in make_predictions_save for {wildcards.analysis_name}: {e}")
            # Create empty output file to allow workflow continuation
            shell("touch {output.prediction}")

# Define rule statistics
rule statistics:
    input:
        prediction = "predictions/{analysis_name}_LASV_lin_pred.csv"
    output:
        figures = "visuals/{analysis_name}_LASV_lin_pred.html"
    params:
        figures_title = config["figures_title"]
    run:
        try:
            plot_lineage_data(
                csv_file=input.prediction,
                title=params.figures_title,
                output_html=output.figures
            )
        except Exception as e:
            print(f"Error in statistics for {wildcards.analysis_name}: {e}")
            # Create empty output file to allow workflow continuation
            shell("touch {output.figures}")
