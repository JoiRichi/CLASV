# CLASV

## Overview
Lassa virus lineage prediction based on random forest.

Information on the research can be found here: 
https://www.biorxiv.org/content/10.1101/2024.07.31.605963v2

## Project Repositories
- **Data and Processing:** [LASV_ML_Manuscript_Data](https://github.com/JoiRichi/LASV_ML_manuscript_data)
- **Lassa Virus Lineage Prediction:** [CLASV_GITHUB](https://github.com/JoiRichi/CLASV)

## Jupyter Notebooks on Google Colab
- **General Preprocessing:** [Notebook Link](https://colab.research.google.com/drive/1JOgS2-dDoQ7OPHPcXm3AIBDnGQAFxIyR)
- **Lassa Virus Lineage Prediction Training:** [Notebook Link](https://colab.research.google.com/drive/1G0lEjuvPR07bcb181Rfhm-S0WenMFSmR)

## Prediction Pipeline Overview
![CLASV](predflow.png)

## Running the Pipeline

It is recommended that python 3.11 is used (or at least between 3.6 - 3.11). [Python3.11](https://www.python.org/downloads/release/python-3110/)


Highly recommended to use a virtual environment:
```sh
python3.11 -m venv myenv #where myenv can be any name of your chioce

source myenv/bin/activate  # activates the virtual environment
```

Install CLASV using pip
```sh
pip install clasv
```
This tool relies on Nextclade for gene extraction and alignment. This is automatically installed. More information about the nextstrain project here: [installation guide](https://docs.nextstrain.org/projects/cli/en/stable/installation/). This tool uses the Snakemake engine which is automatically installed.


```sh
clasv find-lassa --input myinputfolderpath --output mychosenfolderpath --cores 4 --minlength 500 #default 

```

Find Fasta files in the input directory and subdirectories recursively:

```sh
# 
clasv find-lassa --input myinputfolderpath --output mychosenfolderpath  --cores 4 --recursive #Add the recursive flag
```


Force rerun:

```sh
# 
clasv find-lassa --input myinputfolderpath --output mychosenfolderpath --cores 4 --force #add the force flag
```


Upon completion, go to the pipeline 'visuals' folder and open the html files in a browser.


## Customization

This pipeline has the ability to process multiple FASTA files containing multiple sequences with proficiency and speed. It is recommended that multiple FASTA files are concatenated into one; however, this is not compulsory, especially if the projects are different. By default, the pipeline finds all files with the extension `.fasta` in your **input_folder** folder and tries to find LASV GPC sequences in the files. 

To ensure Snakemake has a memory of what files have been checked, intermediary files are created for all files checked, even if they contain no GPC sequences. However, those files would be empty.

### Important Outputs

At the end of the run, you can check the **predictions** folder for the CSV files containing the predictions per sample. A visualization of the prediction can be found in the **visuals** folder. Open the HTML files in a browser. The images are high quality and reactive, allowing you to hover over them to see more information.

For further details, please refer to the respective notebooks and repositories linked above. You can also leave a comment for help regarding the pipeline.



## Model training

Learn how the data was preprocessed here: [LASV_ML_Manuscript_Data](https://github.com/JoiRichi/LASV_ML_manuscript_data). Training process here [Notebook Link](https://colab.research.google.com/drive/1G0lEjuvPR07bcb181Rfhm-S0WenMFSmR).

