# CLASV Benchmark Tool

This tool provides comprehensive performance benchmarking for the CLASV pipeline, designed for scientific publication-grade testing and reporting.

## Overview

The benchmark tool runs the CLASV pipeline multiple times on your input datasets, measuring:

- Total execution time
- Step-by-step timing breakdown
- Performance variance across iterations
- Scaling with file size
- System resource utilization

## Requirements

- Python 3.11
- Installed CLASV package
- Additional Python packages for reporting:
  - pandas
  - matplotlib
  - seaborn

These dependencies are automatically installed with CLASV.

## Usage

```bash
# When installed via pip
clasv-benchmark --input /path/to/fasta/files --output /path/to/output/dir

# When running from source
python -m CLASV.benchmark_clasv --input /path/to/fasta/files --output /path/to/output/dir
```

### Command Line Options

| Option       | Description                                       | Default |
|--------------|---------------------------------------------------|---------|
| `--input`    | Directory containing FASTA files to benchmark     | (Required) |
| `--output`   | Directory to store benchmark results              | (Required) |
| `--cores`    | Number of CPU cores to use                        | 4       |
| `--minlength`| Minimum sequence length filter                    | 500     |
| `--iterations`| Number of iterations for each test               | 3       |
| `--quiet`    | Suppress detailed output                          | False   |

### Example

```bash
# Basic usage
clasv-benchmark --input path/to/samples --output benchmark_output

# Advanced usage with more iterations and different core count
clasv-benchmark --input path/to/samples --output benchmark_output --cores 8 --iterations 5
```

## Output

The benchmark tool generates the following outputs in the specified output directory:

- `benchmark_results/`: Directory containing all benchmark data
  - `benchmark_report.html`: Interactive HTML report with visualizations
  - `benchmark_summary.csv`: CSV summary of average execution times
  - `benchmark_detailed.json`: Detailed JSON with all raw timing data
  - `figures/`: Directory with visualization images
  - Log files for each benchmark iteration

### Visualizations

1. **Average Execution Time by Sample**: Bar chart showing total runtime for each input file
2. **Pipeline Step Time Breakdown**: Stacked bar chart showing time spent in each step
3. **Execution Time vs File Size**: Scatter plot showing correlation between file size and runtime

## Scientific Publication Usage

When using this tool for scientific publications, consider:

1. **Multiple Iterations**: Use at least 5 iterations (`--iterations 5`) for robust statistics
2. **Diverse Datasets**: Test with a range of file sizes and sequence counts
3. **Controlled Environment**: Run benchmarks on a dedicated machine with minimal background processes
4. **Reporting**: Include the HTML report or images in your supplementary materials

### Example Reporting Statement

"Performance measurements were conducted using the CLASV benchmark tool on a [SYSTEM DETAILS] with [CORES] cores. Each test was repeated [ITERATIONS] times, with the average execution time and standard deviation reported. The benchmark datasets included [DESCRIPTION OF DATASETS]."

## Troubleshooting

- **Memory Errors**: For large datasets, ensure your system has sufficient RAM
- **Missing Dependencies**: If visualizations fail, ensure matplotlib, seaborn, and pandas are installed
- **Log Files**: Check the individual log files in the benchmark_results directory for detailed error messages 