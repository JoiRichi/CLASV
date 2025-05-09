configfile: "config/config.yaml"

from core import *
import glob
import os
import shutil
import logging

# Configure logging for error tracking
logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

cwd = os.getcwd()

# Set up directories
output_folder_name = config["output"]
visuals_dir = os.path.join(cwd, output_folder_name, "visuals")
predictions_dir = os.path.join(cwd, output_folder_name, "predictions")
results_dir = os.path.join(cwd, output_folder_name, "results")
preprocessed_dir = os.path.join(results_dir, "preprocessed")

def create_directories(*dirs):
    for d in dirs:
        os.makedirs(d, exist_ok=True)

create_directories(visuals_dir, predictions_dir, results_dir, preprocessed_dir)

# Collect input files
input_path = config["raw_seq_folder"]
recursive = config["recursive"]
include_fastq = config["include_fastq"]

def collect_input_files(input_dir, recursive, include_fastq):
    patterns = [".fasta", ".fasta.gz"]
    if include_fastq:
        patterns += [".fastq", ".fastq.gz"]

    files = glob.glob(os.path.join(input_dir, "**/*"), recursive=recursive) if recursive else glob.glob(os.path.join(input_dir, "*"))
    return [f for f in files if any(f.endswith(ext) for ext in patterns)]

all_input_files = collect_input_files(input_path, recursive, include_fastq)
if not all_input_files:
    raise ValueError(f"No FASTA/FASTQ files found in {input_path}.")
print(f"Found {len(all_input_files)} FASTA/FASTQ file(s) in {input_path}.")

# Precompute raw file mapping for speed
def strip_extensions(filename):
    base = os.path.basename(filename)
    extensions = (".fasta.gz", ".fastq.gz", ".fasta", ".fastq")
    for ext in extensions:
        if base.endswith(ext):
            return base[: -len(ext)]
    return base

raw_file_map = {strip_extensions(f): f for f in all_input_files}

def get_raw_file(aname):
    return raw_file_map.get(aname)

analysis_name = list(raw_file_map.keys())

# Utility for error logging
def log_error(log_file, message):
    logging.error(message)
    with open(log_file, "a") as lg:
        lg.write(f"{message}\n")

def create_dummy(path):
    with open(path, "w") as placeholder:
        placeholder.write("")

# Workflow rules
rule all:
    input:
        expand(f"{predictions_dir}/{{analysis_name}}_LASV_lin_pred.csv", analysis_name=analysis_name),
        expand(f"{visuals_dir}/{{analysis_name}}_LASV_lin_pred.html", analysis_name=analysis_name)

rule preprocess_sequences:
    input:
        seq=lambda wc: get_raw_file(wc.analysis_name)
    output:
        fasta=temp(os.path.join(preprocessed_dir, "{analysis_name}.fasta"))
    run:
        infile, outfile = input.seq, output.fasta
        if infile.endswith((".fasta", ".fasta.gz")):
            shutil.copy(infile, outfile)
        else:
            shell(f"seqkit fq2fa '{infile}' -o '{outfile}'")

rule align_and_extract_region:
    input:
        sequences=os.path.join(preprocessed_dir, "{analysis_name}.fasta"),
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
            log_error(log.convert_log, f"Error in convert_nt_to_aa for {wildcards.analysis_name}: {e}")
            create_dummy(output.sequences)

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
            log_error(log.encode_log, f"Error in encode_sequences for {wildcards.analysis_name}: {e}")
            create_dummy(output.encoding)

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
            log_error(log.prediction_log, f"Error in make_predictions_save for {wildcards.analysis_name}: {e}")
            create_dummy(output.prediction)

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
            log_error(log.statistics_log, f"Error in statistics for {wildcards.analysis_name}: {e}")
            create_dummy(output.figures)
