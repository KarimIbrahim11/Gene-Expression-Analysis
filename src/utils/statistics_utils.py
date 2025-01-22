import logging
import ijson
import numpy as np
from decimal import Decimal
from pathlib import Path
from typing import List, Tuple

from src.utils.data import *
from src.utils.plots import *
from src.utils.memory_management import *
from src.configs.config_parser import PathConfigParser, data_config_file

# Configs Directory
parser = PathConfigParser(str(data_config_file))
parser.load()

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a console handler
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
# Add the handler to the logger
logger.addHandler(sh)


PROCESSED_DATA_PATH = parser.get("data_paths", {}).get("processed_data")
GE_PATH = parser.get("data_paths", {}).get("brain_regions_genes_ge")
PROCESSED_DONORS_GE_PATH = PROCESSED_DATA_PATH / GE_PATH

# Donors_ids
DONORS_IDS = parser.get("donors_ids")

# Calculate Gene Mean Expression Values per Gene ID
def calculate_gene_mean_expression_values(df: pd.DataFrame) -> pd.DataFrame:
    """
        Get the H0 mean expression value per gene id.
    """
    # Add sample_count and mean_expression columns
    df["sample_count"] = df["gene_expression_values"].apply(len)
    df["sum_expression"] = df["gene_expression_values"].apply(np.sum)

    # Group by gene_id to calculate total sum and total sample count
    grouped = df.groupby("gene_id").agg(
        total_expression=("sum_expression", "sum"),
        total_sample_count=("sample_count", "sum")
    )

    # Calculate the weighted mean
    grouped["weighted_mean"] = grouped["total_expression"] / grouped["total_sample_count"]
    
    # Reset the index to make the output clearer
    grouped = grouped.reset_index()

    # Return the result
    return grouped

 