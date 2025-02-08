import logging
import ijson
import numpy as np
from decimal import Decimal
from pathlib import Path
from typing import List, Tuple
from scipy.stats import t
from statsmodels.stats.power import TTestPower

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

# Calculate Gene Mean Expression Values per Brain Region
def calculate_br_mean_expression_values(df: pd.DataFrame) -> pd.DataFrame:
    """
        Get the H0 mean expression value per gene id.
    """
    # Add sample_count and mean_expression columns
    df["sample_count"] = df["gene_expression_values"].apply(len)
    df["sum_expression"] = df["gene_expression_values"].apply(np.sum)

    # Group by gene_id to calculate total sum and total sample count
    grouped = df.groupby("brain_region").agg(
        total_expression=("sum_expression", "sum"),
        total_sample_count=("sample_count", "sum")
    )

    # Calculate the weighted mean
    grouped["weighted_mean"] = grouped["total_expression"] / grouped["total_sample_count"]
    
    # Reset the index to make the output clearer
    grouped = grouped.reset_index()

    # Return the result
    return grouped

# Calculate the standard deviation for each gene_id without exploding the list
def calculate_std_gene_id_optimized(df: pd.DataFrame) -> pd.DataFrame:
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

# Calculate Cohen's D Effect Size
def calculate_cohen_d_pooled(sample_mean: float, control_group_mean: float, 
                      sample_std: float, control_group_std: float,
                      sample_length: int, control_group_length: int):
    """
        Function to calculate the effect size using Cohen's D Equation
    """   
    # Calculate the pooled standard deviation
    pooled_sd = np.sqrt(((sample_length - 1) * sample_std**2 + (control_group_length - 1) * control_group_std**2) 
                        / (sample_length + control_group_length - 2))
    
    # Calculate Cohen's d
    d = (sample_mean - control_group_mean) / pooled_sd

    return d


# Calculate Cohen's D Effect Size
def calculate_cohen_d(sample_mean: float, control_group_mean: float, 
                      sample_std: float, control_group_std: float,
                      sample_length: int, control_group_length: int):
    """
        Function to calculate the effect size using Cohen's D Equation
    """  
    
    # Calculate Cohen's d
    d = (sample_mean - control_group_mean) / sample_std

    return d


# Calculate the Sample T statistic
def calculate_t_statistic(sample_mean: float, sample_std: float, 
                                sample_size: int, population_mean: float) -> float:
    """
        Function to calculate the t statistic of a sample
    """   
    # Calculate the T-statistic
    np.seterr(divide='ignore', invalid='ignore')
    t_stat = (sample_mean - population_mean) / (sample_std / ((float(sample_size) ** 0.5 )))
    
    return t_stat 


# Calculate P-value using Bootstraping
def calculate_bootstrap_p_value(sample: List[float], t_statistic: float, B: int,
                                population_mean: float) -> Tuple[float, List[float]]:
    """
        Function to calculate p-value from B bootstraped samples
    """   
    n = len(sample)
    t = np.zeros(B)
    boostraped_samples =[]
    
    # Resample the data B times
    np.random.seed(42)
    for b in range(B):
        x_b = np.random.choice(sample, n, replace=True)
        boostraped_samples.extend(x_b)
        t[b] = calculate_t_statistic(np.mean(x_b), np.std(x_b), len(x_b), population_mean)

    # Compute the p-value
    p_value = np.mean(t > t_statistic, dtype=float)
    
    return p_value, boostraped_samples
 
 
 # Calculate the test Power
def calculate_test_power(effect_size: float, sample_mean: float, population_mean: float, 
                          sample_std: float, sample_size: int, alpha: float = 0.05) ->  float:
    """
        Function to calculate power for a test
    """   
    # Initialize TTestPower object
    power_analysis = TTestPower()

    # Calculate power
    power = power_analysis.solve_power(effect_size=effect_size, nobs=sample_size, alpha=alpha, alternative='larger')
    
    return power


from statsmodels.stats.power import TTestPower, TTestIndPower
# Calculate the test Power
def calculate_Indtest_power(effect_size: float, sample_mean: float, population_mean: float, 
                          sample_std: float, sample_size: int, alpha: float = 0.05) ->  float:
    """
        Function to calculate power for a test
    """   
    # Initialize TTestPower object
    # power_analysis = TTestPower()
    power_analysis = TTestIndPower()

    # Calculate power
    power = power_analysis.power(effect_size=effect_size, nobs1=sample_size, alpha=alpha, alternative='larger')
    
    return power
