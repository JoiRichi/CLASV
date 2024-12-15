import argparse
import subprocess
from CLASV.pipeline import run_pipeline
from CLASV.install_nextclade import install_nextclade, is_nextclade_installed
from CLASV.install_seqkit import install_seqkit, is_seqkit_installed

    
def main():
    parser = argparse.ArgumentParser(prog="clasv", description="CLASV: Lassa Virus Analysis Pipeline")
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Subcommand: find-lassa
    find_parser = subparsers.add_parser("find-lassa", help="Find Lassa virus sequences")
    find_parser.add_argument("--input", required=True, help="Path to the input folder.")
    find_parser.add_argument("--output", required=True, help="Path to the output folder.")
    find_parser.add_argument("--recursive", action="store_true", help="Search input folder recursively.")
    find_parser.add_argument("--cores", type=int, default=4, help="Number of cores to use (default: 4).")
    find_parser.add_argument("--force", action="store_true", help="Force rerun of all pipeline steps.")
    find_parser.add_argument("--minlength", type=int, default=500, help="Minimum length of GPC.")
    find_parser.add_argument("--include_fastq", action="store_true", help="Include fastq files.")



    args = parser.parse_args()

    # Handle subcommands
    if args.command == "find-lassa":
        if is_nextclade_installed() and is_seqkit_installed():
            print("Nextclade and Seqkit installation verified successfully.")
            run_pipeline(args.input, args.output, args.recursive, args.cores, args.force, args.minlength, args.include_fastq)

        elif is_nextclade_installed() and not is_seqkit_installed():
            print("Nextclade installation verified successfully but seqkit is unavailable. Installing ...")
            install_seqkit()
            run_pipeline(args.input, args.output, args.recursive, args.cores, args.force, args.minlength, args.include_fastq)

        elif not is_nextclade_installed() and is_seqkit_installed():
            print("Seqkit installation verified successfully but Nextclade is unavailable. Installing ...")
            install_nextclade()
            run_pipeline(args.input, args.output, args.recursive, args.cores, args.force, args.minlength, args.include_fastq)
 
        else:
            print("Nextclade and Seqkit has not been installed. Installation in progress. If Nextclade installs and the analysis did not auto-continue, please rerun your command.")
            install_nextclade()
            install_seqkit()
            run_pipeline(args.input, args.output, args.recursive, args.cores, args.force, args.minlength, args.include_fastq)
            
    else:
        parser.print_help()
