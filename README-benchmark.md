# CLASV Benchmark Tool

This tool provides comprehensive performance benchmarking for the CLASV pipeline.

## Overview

The benchmark tool runs the CLASV pipeline multiple times on input datasets, measuring:

- Total execution time
- Step-by-step timing breakdown
- Performance variance across iterations
- Scaling with file size
- System resource utilization

## Requirements

- Python 3.11
- Installed CLASV package
- possible Additional Python packages for reporting:
  - pandas
  - matplotlib
  - seaborn

Install required dependencies:
```bash
pip install pandas matplotlib seaborn
```

## Usage

```bash
python benchmark_clasv.py --input /path/to/fasta/files --output /path/to/output/dir
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
# Basic usage (test data)
python benchmark_clasv.py --input CLASV/raw_data --output benchmark_output

# Advanced usage with more iterations and different core count
python benchmark_clasv.py --input CLASV/raw_data --output benchmark_output --cores 8 --iterations 5
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
