import argparse
import subprocess
from CLASV.pipeline import run_pipeline
from CLASV.install_nextclade import install_nextclade, is_nextclade_installed
    
    
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

    args = parser.parse_args()

    # Handle subcommands
    if args.command == "find-lassa":
        if is_nextclade_installed():
            print("Nextclade installation verified successfully.")
            run_pipeline(args.input, args.output, args.recursive, args.cores, args.force)
        else:
            print("Nextclade has not been installed. Installation in progress. If Nextclade installs and the analysis did not auto-continue, please rerun your command.")
            install_nextclade()
            run_pipeline(args.input, args.output, args.recursive, args.cores, args.force)
            
    else:
        parser.print_help()
