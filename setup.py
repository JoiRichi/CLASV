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

class CustomInstallCommand(install):
    def run(self):
        install.run(self)
        install_nextclade()

print('Running setup...')

setup(
    name='CLASV',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "biopython",
        "pandas",
        "matplotlib",
        "scikit-learn",
        "snakemake"
    ],
    package_data={
        "CLASV": [
            "predict_lineage.smk", 
            "config/*.yaml",
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
    author='Daodu Richard, Awotoro Ebenezer',
    author_email='lordrichado@gmail.com',
    url='https://github.com/JoiRichi/CLASV/commits?author=JoiRichi',
    python_requires=">=3.6",
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
