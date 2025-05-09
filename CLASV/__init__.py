"""
CLASV - Classification of Lassa Virus

A tool for predicting Lassa virus lineages from genomic sequences
using a random forest model trained on glycoprotein precursor (GPC) sequences.
"""

import os

# Get version from VERSION file
__version__ = "1.0.0"  # Default version
version_file = os.path.join(os.path.dirname(__file__), "VERSION")
if os.path.exists(version_file):
    with open(version_file, "r") as f:
        __version__ = f.read().strip()

# Import core functionality
from .core import (
    translate_alignment,
    MakePredictions,
    onehot_alignment_aa,
    plot_lineage_data
)

# Define what's available when using "from CLASV import *"
__all__ = [
    "translate_alignment",
    "MakePredictions",
    "onehot_alignment_aa",
    "plot_lineage_data"
]
