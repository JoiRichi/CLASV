from setuptools import setup, find_packages
from setuptools.command.install import install
import subprocess
import os
import sys
import shutil
from pathlib import Path

# Custom post-install step to install Nextclade
def install_nextclade(package_path):
    """Install nextclade in the package directory"""
    print("Installing nextclade...")
    script_path = os.path.join(package_path, "install_nextclade.py")
    if os.path.exists(script_path):
        subprocess.run([sys.executable, script_path])


def install_seqkit(package_path):
    """Install seqkit in the package directory"""
    print("Installing seqkit...")
    script_path = os.path.join(package_path, "install_seqkit.py")
    if os.path.exists(script_path):
        subprocess.run([sys.executable, script_path])


def find_data_files(base_dir):
    """Find all data files in the given directory"""
    data_files = []
    for root, dirs, files in os.walk(base_dir):
        if '__pycache__' in root:  # Skip __pycache__ directories
            continue
        # Get path relative to the package root
        rel_path = os.path.relpath(root, base_dir)
        if rel_path == '.':  # Top-level files
            for file in files:
                if file.endswith('.py') or file == '__pycache__':
                    continue  # Skip Python files and __pycache__
                data_files.append(os.path.join(rel_path, file))
        else:  # Subdirectory files
            for file in files:
                if file.endswith('.py') or file == '__pycache__':
                    continue  # Skip Python files and __pycache__
                data_files.append(os.path.join(rel_path, file))
    return data_files


def packages_to_include():
    """Return a list of packages to include"""
    packages = ['CLASV']
    for pkg in find_packages():
        if pkg.startswith('CLASV.'):
            packages.append(pkg)
    return packages


class CustomInstallCommand(install):
    def run(self):
        install.run(self)
        install_nextclade(os.path.dirname(os.path.abspath(__file__)))
        install_seqkit(os.path.dirname(os.path.abspath(__file__)))


print('Running setup...')

# Check Python version
if sys.version_info < (3, 6) or sys.version_info >= (3, 12):
    print("\n" + "!" * 80)
    print("⚠️  WARNING: PYTHON VERSION COMPATIBILITY ISSUE ⚠️")
    print("!" * 80)
    print(f"Current Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print("CLASV requires Python 3.6-3.11, with Python 3.11 strongly recommended.")
    print("You may encounter issues with dependencies like Snakemake on other versions.")
    print("Please install Python 3.11 from: https://www.python.org/downloads/release/python-3110/")
    print("!" * 80 + "\n")
elif sys.version_info.minor != 11 and sys.version_info.major == 3:
    print("\n" + "-" * 80)
    print("Note: While Python {}.{} is supported, Python 3.11 is recommended for optimal compatibility.".format(
        sys.version_info.major, sys.version_info.minor))
    print("-" * 80 + "\n")

setup(
    name='CLASV',
    version='1.0.0',
    packages=packages_to_include(),
    include_package_data=True,
    install_requires=[
            "appdirs==1.4.4",
        "argparse-dataclass==2.0.0",
        "attrs==24.2.0",
        "biopython==1.84",
        "certifi==2024.8.30",
        "charset-normalizer==3.4.0",
        "conda-inject==1.3.2",
        "ConfigArgParse==1.7",
        "connection_pool==0.0.3",
        "contourpy==1.3.1",
        "cycler==0.12.1",
        "datrie==0.8.2",
        "docutils==0.21.2",
        "dpath==2.2.0",
        "fastjsonschema==2.21.1",
        "fonttools==4.55.2",
        "gitdb==4.0.11",
        "GitPython==3.1.43",
        "humanfriendly==10.0",
        "idna==3.10",
        "immutables==0.21",
        "Jinja2==3.1.4",
        "joblib==1.4.2",
        "jsonschema==4.23.0",
        "jsonschema-specifications==2024.10.1",
        "jupyter_core==5.7.2",
        "kiwisolver==1.4.7",
        "MarkupSafe==3.0.2",
        "matplotlib==3.9.3",
        "nbformat==5.10.4",
        "numpy==1.23.5",
        "packaging==24.2",
        "pandas==2.2.3",
        "pillow==11.0.0",
        "plac==1.4.3",
        "platformdirs==4.3.6",
        "plotly==5.24.1",
        "psrecord==1.4",
        "psutil==6.1.0",
        "PuLP==2.9.0",
        "pyparsing==3.2.0",
        "python-dateutil==2.9.0.post0",
        "pytz==2024.2",
        "PyYAML==6.0.2",
        "referencing==0.35.1",
        "requests==2.32.3",
        "reretry==0.11.8",
        "rpds-py==0.22.3",
        "scikit-learn==1.6.1",
        "scipy==1.14.1",
        "six==1.17.0",
        "smart-open==7.0.5",
        "smmap==5.0.1",
        "snakemake==8.25.5",
        "snakemake-interface-common==1.17.4",
        "snakemake-interface-executor-plugins==9.3.2",
        "snakemake-interface-report-plugins==1.1.0",
        "snakemake-interface-storage-plugins==3.3.0",
        "tabulate==0.9.0",
        "tenacity==9.0.0",
        "threadpoolctl==3.5.0",
        "throttler==1.2.2",
        "traitlets==5.14.3",
        "tzdata==2024.2",
        "urllib3==2.2.3",
        "wrapt==1.17.0",
        "yte==1.5.4",
        "zipp==3.21.0"
    ],
    package_data={
        "CLASV": find_data_files(os.path.join(os.path.dirname(os.path.abspath(__file__)), "CLASV"))
    },
    entry_points={
        "console_scripts": [
            "clasv=CLASV.cli:main",
            "clasv-benchmark=CLASV.benchmark_clasv:main"
        ]
    },
    description='CLASV is a pipeline designed for rapidly predicting Lassa virus lineages using a Random Forest model.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Richard Daodu, Ebenezer Awotoro, Jens-Uwe Ulrich, Denise Kühnert',
    author_email='lordrichado@gmail.com',
    url='https://github.com/JoiRichi/CLASV/commits?author=JoiRichi',
    python_requires=">=3.6, <3.12",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    cmdclass={
        "install": CustomInstallCommand,
    },
) 