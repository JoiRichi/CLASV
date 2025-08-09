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
    version='1.0.6',
    packages=packages_to_include(),
    include_package_data=True,
    install_requires=[
        # Core runtime deps with Python-version-specific markers
        "numpy>=1.18,<1.20; python_version<'3.8'",
        "numpy>=1.21,<1.24; python_version>='3.8' and python_version<'3.12'",
        "numpy>=1.26; python_version>='3.12'",

        # Biopython for sequence IO
        "biopython<1.79; python_version<'3.7'",
        "biopython<1.81; python_version>='3.7' and python_version<'3.8'",
        "biopython<1.85; python_version>='3.8'",

        "pandas>=1.1,<1.2; python_version<'3.7'",
        "pandas>=1.3,<1.5; python_version>='3.7' and python_version<'3.8'",
        "pandas>=1.5,<2.0; python_version>='3.8' and python_version<'3.9'",
        "pandas>=2.1,<2.3; python_version>='3.9'",

        "scipy<1.6; python_version<'3.7'",
        "scipy<1.8; python_version>='3.7' and python_version<'3.8'",
        "scipy<1.11; python_version>='3.8' and python_version<'3.10'",
        "scipy>=1.11,<1.15; python_version>='3.10' and python_version<'3.12'",
        "scipy>=1.14; python_version>='3.12'",

        "scikit-learn<0.25; python_version<'3.7'",
        "scikit-learn<1.2; python_version>='3.7' and python_version<'3.8'",
        "scikit-learn<1.4; python_version>='3.8' and python_version<'3.11'",
        "scikit-learn>=1.4; python_version>='3.11'",

        "plotly<5; python_version<'3.7'",
        "plotly>=5,<6; python_version>='3.7'",

        "matplotlib<3.4; python_version<'3.7'",
        "matplotlib<3.6; python_version>='3.7' and python_version<'3.8'",
        "matplotlib<3.8; python_version>='3.8' and python_version<'3.10'",
        "matplotlib<3.10; python_version>='3.10'",

        "PyYAML<6; python_version<'3.7'",
        "PyYAML>=6; python_version>='3.7'",

        "requests<2.28; python_version<'3.7'",
        "requests>=2.31; python_version>='3.7'",

        "urllib3<2; python_version<'3.8'",
        "urllib3>=2; python_version>='3.8'",

        "joblib>=1.0,<1.2; python_version<'3.7'",
        "joblib>=1.2; python_version>='3.7'",

        # Snakemake compatibility across versions
        "snakemake<6; python_version<'3.8'",
        "snakemake>=7,<9; python_version>='3.8'",

        # Ensure PuLP API compatibility with Snakemake on older Pythons
        "PuLP>=2.6,<2.8",

        # Backports and compatibility helpers
        "importlib_metadata<5; python_version<'3.8'",
        "zipp<3.0; python_version<'3.7'",
        "typing-extensions>=4.1; python_version<'3.8'",
        "dataclasses; python_version<'3.7'"
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
    python_requires=">=3.7, <3.14",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    cmdclass={
        "install": CustomInstallCommand,
    },
)