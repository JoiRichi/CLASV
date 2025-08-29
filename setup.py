from setuptools import setup, find_packages
from setuptools.command.install import install
import subprocess
import os
import sys

# Custom post-install step to install Nextclade
def install_nextclade():
    try:
        print("Installing Nextclade...")
        subprocess.run(["python", "-m", "CLASV.install_nextclade"], check=True)
        print("Nextclade installation completed.")
        print(
            "\nIMPORTANT: To ensure the Nextclade CLI is available, you may need to restart your terminal "
            "or run the following command:\n"
        )
    except Exception as e:
        print(f"Failed to install Nextclade: {e}")


def install_seqkit():
    try:
        print("Installing Seqkit...")
        subprocess.run(["python", "-m", "CLASV.install_seqkit"], check=True)
        print("Seqkit installation completed.")
        print(
            "\nIMPORTANT: To ensure the Seqkit CLI is available, you may need to restart your terminal "
            "or run the following command:\n"
        )
    except Exception as e:
        print(f"Failed to install Seqkit: {e}")


class CustomInstallCommand(install):
    def run(self):
        install.run(self)
        install_nextclade()
        install_seqkit()


print('Running setup...')

setup(
    name='CLASV',
    version='1.0.6',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        # Core runtime deps with Python-version-specific markers
        "numpy>=1.18,<1.20; python_version<'3.8'",
        "numpy>=1.21,<1.24; python_version>='3.8' and python_version<'3.12'",
        "numpy>=1.26; python_version>='3.12'",

        # Biopython for sequence IO
        "biopython<1.79; python_version<'3.7'",
        "biopython<1.81; python_version>='3.7' and python_version<'3.8'",
        "biopython<1.85; python_version>='3.8' and python_version<'3.13'",
        "biopython>=1.85; python_version>='3.13'",

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
        "CLASV": [
            "predict_lineage.smk",
            "config/config.yaml",
            "*.smk",
            "config/*.yaml",
            "results/*.fasta",
            "results/*.csv",
            "predictions/*.csv",
            "visuals/*.html"
        ]
    },
    entry_points={
        "console_scripts": [
            "clasv=CLASV.cli:main",
        ]
    },
    description='CLASV is a pipeline designed for rapidly predicting Lassa virus lineages using a Random Forest model.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Richard Daodu, Ebenezer Awotoro, Jens-Uwe Ulrich, Denise Kühnert',
    author_email='lordrichado@gmail.com',
    url='https://github.com/JoiRichi/CLASV/commits?author=JoiRichi',
    python_requires=">=3.7,<3.14",
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
