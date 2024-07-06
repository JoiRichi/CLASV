from Bio import AlignIO
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq

import pandas as pd
import os
import glob
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

from joblib import load
from sklearn.ensemble import RandomForestClassifier

#this is the verdict function!
def get_verdict(row):
    filtered_row = row[row > 0.5]
    if filtered_row.empty:
        return "inconclusive"
    else:
        return filtered_row.idxmax()




def translate_alignment(alignment_path, output_path):
    def translate(seq):
        table = {
            'ATA': 'I', 'ATC': 'I', 'ATT': 'I', 'ATG': 'M',
            'ACA': 'T', 'ACC': 'T', 'ACG': 'T', 'ACT': 'T',
            'AAC': 'N', 'AAT': 'N', 'AAA': 'K', 'AAG': 'K',
            'AGC': 'S', 'AGT': 'S', 'AGA': 'R', 'AGG': 'R',
            'CTA': 'L', 'CTC': 'L', 'CTG': 'L', 'CTT': 'L',
            'CCA': 'P', 'CCC': 'P', 'CCG': 'P', 'CCT': 'P',
            'CAC': 'H', 'CAT': 'H', 'CAA': 'Q', 'CAG': 'Q',
            'CGA': 'R', 'CGC': 'R', 'CGG': 'R', 'CGT': 'R',
            'GTA': 'V', 'GTC': 'V', 'GTG': 'V', 'GTT': 'V',
            'GCA': 'A', 'GCC': 'A', 'GCG': 'A', 'GCT': 'A',
            'GAC': 'D', 'GAT': 'D', 'GAA': 'E', 'GAG': 'E',
            'GGA': 'G', 'GGC': 'G', 'GGG': 'G', 'GGT': 'G',
            'TCA': 'S', 'TCC': 'S', 'TCG': 'S', 'TCT': 'S',
            'TTC': 'F', 'TTT': 'F', 'TTA': 'L', 'TTG': 'L',
            'TAC': 'Y', 'TAT': 'Y', 'TAA': 'X', 'TAG': 'X',
            'TGC': 'C', 'TGT': 'C', 'TGA': 'X', 'TGG': 'W',
        }
        protein = ""
        if len(seq) % 3 == 0:
            for i in range(0, len(seq), 3):
                codon = seq[i:i + 3]
                protein += table.get(codon, 'X')  # Use 'X' for unrecognized codons
        else:
            raise ValueError('The lenght of the sequence is not divisible by 3. Are you sure the sequence is well aligned?')
        
        return protein

  
    # Read the alignment
    alignment = AlignIO.read(alignment_path, "fasta")

    # Translate each sequence in the alignment
    translated_records = []
    for record in alignment:
        translated_seq = translate(str(record.seq))
        translated_record = SeqRecord(Seq(translated_seq[:-1]), id=record.id, description="")
        translated_records.append(translated_record)

    # Write the translated sequences back to the alignment file
    with open(output_path, "w") as output_handle:
        SeqIO.write(translated_records, output_handle, "fasta")



class MakePredictions:
  def __init__(self, model_path):
    self.model = load(model_path)
    self.columns =['lineage3', 'lineage4_5', 'lineage7', 'lineage_2']



  def predict(self, encoding_path, output_path):
      df = pd.read_csv(encoding_path)
      sample_names = df.iloc[:, 0]
    
    # Drop the first column (assuming it contains sample names)
      df = df.iloc[:, 1:]
      probabilities = self.model.predict_proba(df)
      all_pred = {}
      for i, each in enumerate(self.columns):
          false, true = np.transpose(probabilities[i])
          all_pred[f'{each}_false'] =  false
          all_pred[f'{each}'] =  true
      all_pred_df = pd.DataFrame(all_pred)
      all_pred_df.index = sample_names
      columns_to_drop = [col for col in all_pred_df.columns if 'false' in col.lower()]
      all_pred_df.drop(columns=columns_to_drop, inplace=True)
      
      results = all_pred_df.apply(get_verdict, axis=1)
      all_pred_df['verdict'] = results

      with open(output_path, "w") as output_handle:
          all_pred_df.to_csv(output_handle)


  


def generate_onehot_mapping(alphabet):
    mapping = {}
    for i, char in enumerate(alphabet):
        vec = [0.] * 21
        vec[i] = 1.
        mapping[char] = vec
    # Setting the 'X' vector to all zeros
    mapping['X'] = [0.] * 21


    return mapping


def onehot_alignment_aa(alignment_path, output_path):
    alignment = AlignIO.read(alignment_path, "fasta")
    alphabet = '-ACDEFGHIKLMNPQRSTVWY'
    encoded_alignment = []

    mapping = generate_onehot_mapping(alphabet)

    def onehot(sequence):
        seq_array = list(sequence.upper())

        # Find start and end indices of actual sequence
        start_index = next((i for i, aa in enumerate(seq_array) if aa != '-'), None)
        end_index = len(seq_array) - next((i for i, aa in enumerate(seq_array[::-1]) if aa != '-'), None)

        # Replace gaps with 'X' within the sequence
        if start_index is not None and start_index > 0:
            seq_array[:start_index] = ['X'] * start_index
        if end_index is not None and end_index < len(seq_array):
            seq_array[end_index:] = ['X'] * (len(seq_array) - end_index)

        # One-hot encode amino acids and gaps
        seq2 = [mapping.get(aa, mapping['X']) for aa in seq_array]

        return np.array(seq2).flatten()

    for record in alignment:
        encoded_sequence = onehot(str(record.seq))
        encoded_alignment.append(list(encoded_sequence))

    df = pd.DataFrame(encoded_alignment)
    df.index = [record.id for record in alignment]

    with open(output_path, "w") as output_handle:
        df.to_csv(output_handle)



def plot_lineage_data(csv_file, title, cutoff=0.5, line_color='Red', line_style='dashdot', title_font_size=14, x_axis_title='ID or ID_index', y_axis_title='Probability', output_html=None):
    """
    Plot lineage data from a CSV file, create a bar chart, and a pie chart, and save the plots as an HTML file.

    Parameters:
    - csv_file (str): Path to the CSV file.
    - title (str): Title of the plot.
    - cutoff (float): Y-value for the cutoff line.
    - line_color (str): Color of the cutoff line.
    - line_style (str): Style of the cutoff line (e.g., 'dash', 'dashdot').
    - title_font_size (int): Font size of the title.
    - x_axis_title (str): Title for the x-axis.
    - y_axis_title (str): Title for the y-axis.
    - output_html (str): Path to save the HTML file. If None, the file won't be saved.
    """
    # Reading the data from the CSV file
    data = pd.read_csv(csv_file)

    # Set index to the first column
    data.set_index(data.columns[0], inplace=True)

    # Separate numeric and non-numeric columns
    numeric_data = data.select_dtypes(include=['number'])
    non_numeric_data = data.select_dtypes(exclude=['number'])

    # Interactive plot of numeric lineage data
    fig_lineage = go.Figure()

    if len(numeric_data) > 50:
        x_values = list(range(1, len(numeric_data) + 1))
        hover_texts = numeric_data.index
    else:
        x_values = numeric_data.index
        hover_texts = numeric_data.index

    for column in numeric_data.columns:
        fig_lineage.add_trace(go.Scatter(
            x=x_values,
            y=numeric_data[column],
            mode='lines+markers',
            name=column,
            text=hover_texts,
            hoverinfo='text+y'
        ))

    fig_lineage.update_layout(
        title=f'<b>{title}</b>',
        title_font=dict(size=title_font_size, family='Arial', color='black'),
        title_x=0.5,
        xaxis_title=x_axis_title,
        yaxis_title=y_axis_title,
        hovermode='x unified'
    )

    fig_lineage.add_shape(
        type="line",
        x0=0,
        y0=cutoff,
        x1=1,
        y1=cutoff,
        xref='paper',
        yref='y',
        line=dict(
            color=line_color,
            width=2,
            dash=line_style,
        )
    )

    # Bar chart of lineage frequencies
    fig_bar = px.histogram(data.reset_index(), x='verdict')

    fig_bar.update_traces(texttemplate='%{y}', textposition='outside')

    fig_bar.update_layout(
        title=f'<b>{title}</b>',
        title_font=dict(size=14, family='Arial', color='black'),
        title_x=0.5,
        xaxis_title='Predicted Lineage',
        yaxis_title='Count',
        hovermode='x unified'
    )

    # Pie chart of lineage percentages
    fig_pie = px.pie(data.reset_index(), names='verdict')

    fig_pie.update_traces(textinfo='percent+label')

    fig_pie.update_layout(
        title=f'<b>{title}</b>',
        title_font=dict(size=14, family='Arial', color='black'),
        title_x=0.5
    )

    # Display the figures
    #fig_lineage.show()
    #fig_bar.show()
    #fig_pie.show()

    # Save the figures as an HTML file if the output path is specified
    if output_html:
        with open(output_html, 'w') as f:
            f.write(fig_lineage.to_html(full_html=False, include_plotlyjs='cdn'))
            f.write(fig_bar.to_html(full_html=False, include_plotlyjs='cdn'))
            f.write(fig_pie.to_html(full_html=False, include_plotlyjs='cdn'))



# Example usage

