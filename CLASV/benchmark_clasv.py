#!/usr/bin/env python3
"""
CLASV Benchmark Tool - Command-line interface for benchmarking CLASV performance.
This script provides a scientific publication-grade benchmarking tool for the CLASV pipeline.
"""

import sys
import os
from pathlib import Path
from CLASV.tools.benchmark_clasv import main as benchmark_main

def main():
    """Main entry point for the CLASV benchmark tool"""
    # Add current directory to path to ensure imports work correctly
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    # Run the benchmark main function
    benchmark_main()

if __name__ == "__main__":
    main() 