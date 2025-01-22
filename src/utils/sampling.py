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

# Counts
def get_total_number_of_samples(df: pd.DataFrame) -> int:
    """
        Get the total number of Samples available
    """
    return df['gene_expression_values'].apply(len).sum()

def get_total_number_of_br(df: pd.DataFrame) -> int:
    """
        Get the total number of Brain Regions
    """
    return df["brain_region"].nunique()

def get_number_of_genes_per_br(df: pd.DataFrame) -> List[int]:
    """
        Get the number of Genes per Brain Region
    """
    # Count the number of gene_ids per brain region
    return df.groupby("brain_region")["gene_id"].count()

def get_number_of_samples_per_br(df: pd.DataFrame) -> List[int]:
    """
        Get the number of Samples per Brain Region.
    """
    df['num_gene_expression_values'] = df['gene_expression_values'].apply(len)

    # Group by 'brain_region' and sum the 'num_gene_expression_values' for each region
    result = df.groupby('brain_region')['num_gene_expression_values'].sum()

    # Drop the 'num_gene_expression_values' column if you no longer need it
    df.drop(columns=['num_gene_expression_values'])

    # Convert the result to a list
    return result.tolist()

def get_number_of_samples_per_br_ge(df:  pd.DataFrame) ->  List[int]:
    """
        Get the number of Samples per Brain Region-Gene Id pair.
    """
    # Count the number of samples for each brain_region-gene_id pair
    df["sample_count"] = df["gene_expression_values"].apply(len)
    return df[["brain_region", "gene_id", "sample_count"]]


# Basic Getters
def get_br_list(df: pd.DataFrame) -> List[str]:
    """
        Get a list of brain regions available.
    """
    return df["brain_region"].unique().tolist()

def get_ge_list(df:pd.DataFrame) -> List[int]:
    """
        Get a list of Gene Ids available.
    """
    return df["gene_id"].unique().tolist()


# Sampling per brain-region-gene-id pair
def get_br_ge_sample(df: pd.DataFrame, br: int, ge: int) -> List[int]:
    """
        Get the Samples of a Brain Region-Gene Id pair
    """
    return df[(df['brain_region'] == br) & (df['gene_id'] == ge)]["gene_expression_values"].to_list()[0]


# Getting the BR-Region IDs pairs with different sample sizes
def get_br_ge_count_above_sample_size(df:pd.DataFrame, range: List[int]) -> List[int]:
    """
        Get the count of a Brain Region pair with a samples more than certain thresholds
    """
    count_per_sample_size = []
    for threshold in range:  # Thresholds from 10 to 100 in steps of 10
        count_per_sample_size.append( df[df["sample_count"] >= threshold].shape[0])
    
    return count_per_sample_size


# Calculate the standard deviation for each gene_id without exploding the list
def std_gene_id_optimized(df: pd.DataFrame) -> pd.DataFrame:
    """
        Get the STD of each Gene ID
    """
    def calculate_std(gene_expression_list):
        return pd.Series(gene_expression_list).std()

    # Apply the std calculation to the gene expression values for each group of gene_id
    def group_std(x):
        return calculate_std([item for sublist in x for item in sublist])  # Flatten the list of lists
    
    # Group by gene_id and apply the function
    std_per_gene = df.groupby('gene_id')['gene_expression_values'].apply(group_std).reset_index(name='std')
    
    return std_per_gene