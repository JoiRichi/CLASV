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
        "scikit-learn==1.2.2",
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
