#!/usr/bin/env python3
"""
CLASV Benchmark Tool - Comprehensive performance benchmarking for CLASV.

This tool provides a scientific publication-grade benchmarking capability for the CLASV pipeline,
measuring timing of each pipeline step and generating detailed reports for performance analysis.
"""
import subprocess
import time
import os
import pandas as pd
import argparse
import json
import datetime
import shutil
from pathlib import Path


class CLASVBenchmark:
    def __init__(self, input_dir, output_dir, cores=4, minlength=500, iterations=3, verbose=True):
        """
        Initialize the CLASV benchmark tool
        
        Parameters:
        -----------
        input_dir : str
            Path to directory containing input FASTA files
        output_dir : str
            Path to directory where benchmark results will be stored
        cores : int
            Number of cores to use for CLASV
        minlength : int
            Minimum length filter for sequences
        iterations : int
            Number of times to run each test for averaging
        verbose : bool
            Whether to print detailed progress information
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.cores = cores
        self.minlength = minlength
        self.iterations = iterations
        self.verbose = verbose
        self.benchmark_results = []
        
        # Create benchmark directory if it doesn't exist
        self.benchmark_dir = self.output_dir / "benchmark_results"
        os.makedirs(self.benchmark_dir, exist_ok=True)
        
        # Create a temp directory for isolated file testing
        self.temp_dir = self.output_dir / "temp_input"
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Details for report
        self.start_time = None
        self.end_time = None
        self.system_info = self._get_system_info()
        
        if verbose:
            print(f"CLASV Benchmark initialized with:")
            print(f"  - Input directory: {self.input_dir}")
            print(f"  - Output directory: {self.output_dir}")
            print(f"  - Cores: {self.cores}")
            print(f"  - Min sequence length: {self.minlength}")
            print(f"  - Iterations: {iterations}")
            print(f"  - System: {self.system_info.get('os', 'Unknown')}, {self.system_info.get('cpu', 'Unknown')}")

    def _get_system_info(self):
        """Get system information for the benchmark report"""
        info = {}
        
        # OS information
        try:
            import platform
            info['os'] = f"{platform.system()} {platform.release()}"
            info['python'] = platform.python_version()
        except:
            info['os'] = "Unknown"
            info['python'] = "Unknown"
            
        # CPU information
        try:
            if platform.system() == "Darwin":  # macOS
                cmd = "sysctl -n machdep.cpu.brand_string"
                info['cpu'] = subprocess.check_output(cmd.split()).decode().strip()
            elif platform.system() == "Linux":
                cmd = "cat /proc/cpuinfo | grep 'model name' | uniq"
                output = subprocess.check_output(cmd, shell=True).decode().strip()
                info['cpu'] = output.split(':')[1].strip() if ':' in output else output
            elif platform.system() == "Windows":
                try:
                    import wmi
                    computer = wmi.WMI()
                    info['cpu'] = computer.Win32_Processor()[0].Name
                except ImportError:
                    # WMI not available, try another approach
                    info['cpu'] = platform.processor()
            else:
                info['cpu'] = "Unknown"
        except:
            info['cpu'] = "Unknown"
            
        # Memory information
        try:
            if platform.system() == "Darwin":  # macOS
                cmd = "sysctl -n hw.memsize"
                mem_bytes = int(subprocess.check_output(cmd.split()).decode().strip())
                info['memory'] = f"{mem_bytes / (1024**3):.2f} GB"
            elif platform.system() == "Linux":
                cmd = "cat /proc/meminfo | grep MemTotal"
                output = subprocess.check_output(cmd, shell=True).decode().strip()
                if ":" in output:
                    mem_kb = int(output.split(':')[1].strip().split()[0])
                    info['memory'] = f"{mem_kb / (1024**2):.2f} GB"
                else:
                    info['memory'] = "Unknown"
            elif platform.system() == "Windows":
                try:
                    import wmi
                    computer = wmi.WMI()
                    total_memory = 0
                    for mem in computer.Win32_PhysicalMemory():
                        total_memory += int(mem.Capacity)
                    info['memory'] = f"{total_memory / (1024**3):.2f} GB"
                except ImportError:
                    import psutil
                    info['memory'] = f"{psutil.virtual_memory().total / (1024**3):.2f} GB"
            else:
                info['memory'] = "Unknown"
        except:
            info['memory'] = "Unknown"
            
        # Add CLASV version
        try:
            from CLASV import __version__
            info['clasv_version'] = __version__
        except:
            info['clasv_version'] = "Unknown"
            
        return info
    
    def run_benchmark(self):
        """Run the benchmark tests"""
        self.start_time = datetime.datetime.now()
        
        if self.verbose:
            print(f"\nStarting benchmark at {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 80)
        
        # Get list of FASTA files from input directory
        fasta_files = list(self.input_dir.glob("*.fasta"))
        
        if not fasta_files:
            print(f"Error: No .fasta files found in {self.input_dir}")
            return
            
        if self.verbose:
            print(f"Found {len(fasta_files)} FASTA files in {self.input_dir}")
        
        # Run benchmarks for each file
        for fasta_file in fasta_files:
            file_name = fasta_file.name
            sample_name = file_name.replace('.fasta', '')
            
            if self.verbose:
                print(f"\nBenchmarking file: {file_name}")
                print("-" * 80)
            
            # Prepare output dir for this test
            test_output_dir = self.output_dir / f"test_{sample_name}"
            
            # Run multiple iterations
            iteration_times = []
            
            for iter_num in range(1, self.iterations + 1):
                if self.verbose:
                    print(f"  Iteration {iter_num}/{self.iterations}...")
                
                # Delete existing output dir if it exists
                if test_output_dir.exists():
                    subprocess.run(f"rm -rf {test_output_dir}", shell=True)
                os.makedirs(test_output_dir, exist_ok=True)
                
                # Clear and recreate temp input directory with only this file
                subprocess.run(f"rm -rf {self.temp_dir}/*", shell=True)
                temp_file_path = self.temp_dir / file_name
                
                # Copy the target file to the temp directory
                shutil.copy2(fasta_file, temp_file_path)
                
                # Measure time for CLASV execution
                start_time = time.time()
                clasv_command = f"clasv find-lassa --input {self.temp_dir} --output {test_output_dir} --cores {self.cores} --minlength {self.minlength} --force"
                
                if self.verbose:
                    print(f"  Running: {clasv_command}")
                
                # Run command and capture output
                with open(self.benchmark_dir / f"{sample_name}_iter{iter_num}_log.txt", "w") as log_file:
                    result = subprocess.run(
                        clasv_command,
                        shell=True,
                        stdout=log_file,
                        stderr=subprocess.STDOUT,
                        text=True
                    )
                
                end_time = time.time()
                execution_time = end_time - start_time
                
                # Parse the execution logs to get step-by-step timing
                step_times = self._parse_execution_times(
                    self.benchmark_dir / f"{sample_name}_iter{iter_num}_log.txt",
                    sample_name
                )
                
                # Add to results
                iteration_times.append({
                    "iteration": iter_num,
                    "sample": sample_name,
                    "total_time": execution_time,
                    "exit_code": result.returncode,
                    "step_times": step_times
                })
                
                if self.verbose:
                    print(f"  Execution time: {execution_time:.2f} seconds")
            
            # Calculate average execution time
            avg_time = sum(item["total_time"] for item in iteration_times) / len(iteration_times)
            
            # Calculate average step times
            avg_step_times = {}
            if iteration_times and iteration_times[0]["step_times"]:
                for step in iteration_times[0]["step_times"]:
                    avg_step_times[step] = sum(
                        item["step_times"].get(step, 0) for item in iteration_times
                    ) / len(iteration_times)
            
            benchmark_result = {
                "sample": sample_name,
                "file_size_bytes": fasta_file.stat().st_size,
                "avg_execution_time": avg_time,
                "iterations": self.iterations,
                "iteration_times": [item["total_time"] for item in iteration_times],
                "avg_step_times": avg_step_times,
                "step_times_by_iteration": {
                    item["iteration"]: item["step_times"] for item in iteration_times
                }
            }
            
            self.benchmark_results.append(benchmark_result)
            
            if self.verbose:
                print(f"  Average execution time: {avg_time:.2f} seconds")
        
        # Clean up temp directory
        subprocess.run(f"rm -rf {self.temp_dir}", shell=True)
        
        self.end_time = datetime.datetime.now()
        self._generate_reports()
        
        if self.verbose:
            print("\nBenchmark completed successfully!")
            print(f"Results saved to {self.benchmark_dir}")
    
    def _parse_execution_times(self, log_file_path, sample_name):
        """
        Parse the Snakemake execution logs to extract timing information for each step
        """
        step_times = {}
        current_step = None
        start_time = None
        
        try:
            with open(log_file_path, 'r') as f:
                for line in f:
                    # Look for job start indicators
                    if "rule " in line and ":" in line and "[" in line:
                        # Extract step name from lines like: "rule align_and_extract_region:"
                        parts = line.strip().split("rule ")
                        if len(parts) > 1:
                            step_parts = parts[1].split(":")
                            if len(step_parts) > 0:
                                current_step = step_parts[0].strip()
                                # Extract timestamp
                                if "[" in line and "]" in line:
                                    time_str = line.split("[")[1].split("]")[0].strip()
                                    try:
                                        start_time = datetime.datetime.strptime(time_str, "%a %b %d %H:%M:%S %Y")
                                    except ValueError:
                                        start_time = None
                    
                    # Look for job finish indicators
                    elif "Finished job" in line and current_step is not None and start_time is not None:
                        if "[" in line and "]" in line:
                            time_str = line.split("[")[1].split("]")[0].strip()
                            try:
                                end_time = datetime.datetime.strptime(time_str, "%a %b %d %H:%M:%S %Y")
                                duration = (end_time - start_time).total_seconds()
                                step_times[current_step] = duration
                            except ValueError:
                                pass
                        
                        current_step = None
                        start_time = None
        except Exception as e:
            print(f"Error parsing log file {log_file_path}: {e}")
        
        return step_times
    
    def _generate_reports(self):
        """Generate benchmark reports"""
        # Save detailed JSON results
        with open(self.benchmark_dir / "benchmark_detailed.json", "w") as f:
            json.dump({
                "system_info": self.system_info,
                "benchmark_params": {
                    "cores": self.cores,
                    "minlength": self.minlength,
                    "iterations": self.iterations
                },
                "start_time": self.start_time.isoformat() if self.start_time else None,
                "end_time": self.end_time.isoformat() if self.end_time else None,
                "results": self.benchmark_results
            }, f, indent=2)
        
        # Create CSV report for easy analysis
        csv_data = []
        
        for result in self.benchmark_results:
            sample = result["sample"]
            file_size_mb = result["file_size_bytes"] / (1024 * 1024)
            
            for i, time_val in enumerate(result["iteration_times"], 1):
                row = {
                    "Sample": sample,
                    "File_Size_MB": file_size_mb,
                    "Iteration": i,
                    "Total_Time_Seconds": time_val
                }
                
                # Add step times
                step_times = result["step_times_by_iteration"].get(i, {})
                for step, time_val in step_times.items():
                    row[f"Step_{step}_Seconds"] = time_val
                
                csv_data.append(row)
        
        # Create and save DataFrame
        df = pd.DataFrame(csv_data)
        df.to_csv(self.benchmark_dir / "benchmark_results.csv", index=False)
        
        # Generate summary report
        summary_data = []
        
        for result in self.benchmark_results:
            summary_row = {
                "Sample": result["sample"],
                "File_Size_MB": result["file_size_bytes"] / (1024 * 1024),
                "Avg_Total_Time_Seconds": result["avg_execution_time"],
                "Iterations": result["iterations"]
            }
            
            # Add average step times
            for step, time_val in result["avg_step_times"].items():
                summary_row[f"Avg_{step}_Seconds"] = time_val
            
            summary_data.append(summary_row)
        
        # Create and save summary DataFrame
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv(self.benchmark_dir / "benchmark_summary.csv", index=False)
        
        # Generate HTML report
        self._generate_html_report()
    
    def _generate_html_report(self):
        """Generate an HTML report with visualizations"""
        try:
            import matplotlib
            matplotlib.use('Agg')  # Use non-interactive backend
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            # Load result data
            df = pd.read_csv(self.benchmark_dir / "benchmark_results.csv")
            summary_df = pd.read_csv(self.benchmark_dir / "benchmark_summary.csv")
            
            # Style settings
            plt.style.use('ggplot')
            sns.set(font_scale=1.1)
            
            # Create figures directory
            figures_dir = self.benchmark_dir / "figures"
            os.makedirs(figures_dir, exist_ok=True)
            
            # Figure 1: Total Execution Time by Sample
            plt.figure(figsize=(12, 6))
            ax = sns.barplot(x="Sample", y="Avg_Total_Time_Seconds", data=summary_df)
            ax.set_title('Average Execution Time by Sample')
            ax.set_ylabel('Time (seconds)')
            ax.set_xlabel('Sample')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig(figures_dir / "total_time_by_sample.png", dpi=300)
            plt.close()
            
            # Figure 2: Step Time Breakdown
            step_cols = [col for col in summary_df.columns if col.startswith("Avg_") and col != "Avg_Total_Time_Seconds"]
            
            if step_cols:
                # Reshape data for stacked bar chart
                step_data = []
                
                for _, row in summary_df.iterrows():
                    sample = row['Sample']
                    for step in step_cols:
                        step_name = step.replace("Avg_", "").replace("_Seconds", "")
                        step_data.append({
                            'Sample': sample,
                            'Step': step_name,
                            'Time': row[step]
                        })
                
                step_df = pd.DataFrame(step_data)
                
                plt.figure(figsize=(14, 8))
                ax = sns.barplot(x="Sample", y="Time", hue="Step", data=step_df)
                ax.set_title('Pipeline Step Time Breakdown by Sample')
                ax.set_ylabel('Time (seconds)')
                ax.set_xlabel('Sample')
                plt.xticks(rotation=45)
                plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
                plt.tight_layout()
                plt.savefig(figures_dir / "step_breakdown.png", dpi=300)
                plt.close()
            
            # Figure 3: Time vs File Size
            plt.figure(figsize=(10, 6))
            ax = sns.scatterplot(x="File_Size_MB", y="Avg_Total_Time_Seconds", 
                              data=summary_df, s=100)
            
            # Add text labels for each point
            for _, row in summary_df.iterrows():
                ax.text(row['File_Size_MB'], row['Avg_Total_Time_Seconds'], 
                        row['Sample'], fontsize=9)
                
            ax.set_title('Execution Time vs File Size')
            ax.set_ylabel('Time (seconds)')
            ax.set_xlabel('File Size (MB)')
            plt.tight_layout()
            plt.savefig(figures_dir / "time_vs_size.png", dpi=300)
            plt.close()
            
            # Generate HTML
            html_content = self._get_html_template()
            
            benchmark_time = f"{self.start_time.strftime('%Y-%m-%d %H:%M:%S')} to {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Replace placeholders with actual data
            html_content = html_content.replace("{{BENCHMARK_TIME}}", benchmark_time)
            html_content = html_content.replace("{{SYSTEM_INFO}}", 
                f"{self.system_info.get('os', 'Unknown')}, {self.system_info.get('cpu', 'Unknown')}, {self.system_info.get('memory', 'Unknown')}")
            html_content = html_content.replace("{{PYTHON_VERSION}}", self.system_info.get('python', 'Unknown'))
            html_content = html_content.replace("{{CLASV_VERSION}}", self.system_info.get('clasv_version', 'Unknown'))
            html_content = html_content.replace("{{CORES}}", str(self.cores))
            html_content = html_content.replace("{{ITERATIONS}}", str(self.iterations))
            
            # Generate results table
            table_html = summary_df.to_html(index=False, border=0, classes="table table-striped")
            html_content = html_content.replace("{{RESULTS_TABLE}}", table_html)
            
            # Write the HTML file
            with open(self.benchmark_dir / "benchmark_report.html", "w") as f:
                f.write(html_content)
                
        except ImportError as e:
            print(f"Warning: Could not generate HTML report. Missing dependency: {e}")
            print("To generate reports, install matplotlib, seaborn and pandas: pip install matplotlib seaborn pandas")
    
    def _get_html_template(self):
        """Return HTML template for the report"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CLASV Benchmark Report</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { padding: 20px; }
        .report-header { margin-bottom: 30px; }
        .results-section { margin-top: 30px; }
        .figure-section { margin-top: 40px; }
        .figure-container { margin-bottom: 30px; }
        .table-responsive { margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="report-header">
            <h1 class="text-center">CLASV Benchmark Report</h1>
            <p class="text-center text-muted">{{BENCHMARK_TIME}}</p>
        </div>
        
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>System Information</h5>
                    </div>
                    <div class="card-body">
                        <p><strong>System:</strong> {{SYSTEM_INFO}}</p>
                        <p><strong>Python:</strong> {{PYTHON_VERSION}}</p>
                        <p><strong>CLASV Version:</strong> {{CLASV_VERSION}}</p>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Benchmark Configuration</h5>
                    </div>
                    <div class="card-body">
                        <p><strong>CPU Cores:</strong> {{CORES}}</p>
                        <p><strong>Iterations:</strong> {{ITERATIONS}}</p>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="results-section">
            <h2>Benchmark Results</h2>
            <div class="table-responsive">
                {{RESULTS_TABLE}}
            </div>
        </div>
        
        <div class="figure-section">
            <h2>Visualizations</h2>
            
            <div class="figure-container">
                <h4>Average Execution Time by Sample</h4>
                <img src="figures/total_time_by_sample.png" class="img-fluid" alt="Total Time by Sample">
            </div>
            
            <div class="figure-container">
                <h4>Pipeline Step Time Breakdown</h4>
                <img src="figures/step_breakdown.png" class="img-fluid" alt="Step Breakdown">
            </div>
            
            <div class="figure-container">
                <h4>Execution Time vs File Size</h4>
                <img src="figures/time_vs_size.png" class="img-fluid" alt="Time vs Size">
            </div>
        </div>
    </div>
</body>
</html>"""


def main():
    parser = argparse.ArgumentParser(description='CLASV Performance Benchmark Tool')
    parser.add_argument('--input', required=True, help='Directory containing FASTA files to benchmark')
    parser.add_argument('--output', required=True, help='Directory to store benchmark results')
    parser.add_argument('--cores', type=int, default=4, help='Number of CPU cores to use (default: 4)')
    parser.add_argument('--minlength', type=int, default=500, help='Minimum sequence length filter (default: 500)')
    parser.add_argument('--iterations', type=int, default=3, help='Number of iterations for each test (default: 3)')
    parser.add_argument('--quiet', action='store_true', help='Suppress detailed output')
    
    args = parser.parse_args()
    
    benchmark = CLASVBenchmark(
        input_dir=args.input,
        output_dir=args.output,
        cores=args.cores,
        minlength=args.minlength,
        iterations=args.iterations,
        verbose=not args.quiet
    )
    
    benchmark.run_benchmark()


if __name__ == "__main__":
    main() 