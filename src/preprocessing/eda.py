import logging
import ijson
import numpy as np
from decimal import Decimal
from pathlib import Path
from typing import List, Tuple

from utils.data import *
from utils.plots import *
from utils.memory_management import *
from configs.config_parser import PathConfigParser

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a console handler
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
# Add the handler to the logger
logger.addHandler(sh)

# Configs Directory
configs_dir = "src/configs/"

parser = PathConfigParser(configs_dir + "data_config.yaml")
parser.load()

PROCESSED_DATA_PATH = parser.get("data_paths", {}).get("processed_data")
GE_PATH = parser.get("data_paths", {}).get("brain_regions_genes_ge")
PROCESSED_DONORS_GE_PATH = PROCESSED_DATA_PATH / GE_PATH

# Donors_ids
DONORS_IDS = parser.get("donors_ids")

def get_meta_donor_lists(pth: Path) -> Tuple[List[str], List[int], List[int], int]:
    """
        Export Brain Regions, Gene_Ids and Brain Samples Per Region Lists for plotting. 
    """
    # Lists to store information for plotting
    brain_regions = []
    gene_ids = []
    samples_sizes_per_brain_region = []
    gene_lengths = []
    total_number_of_samples = 0

    # Stream through the JSON file using ijson
    with open(pth, "r") as f:
        # Parse key-value pairs at the root level
        for brain_region, genes in ijson.kvitems(f, ''):
            logger.info(f"Brain Region: {brain_region}")  # Access the brain region key (e.g., "4012")
            number_of_samples_per_brain_region = 0
            for gene in genes:
                # Access gene_id
                gene_id = gene["gene_id"]
                gene_ids.append(gene_id)
                
                # Access gene_expression_values and convert to float if Decimal
                gene_expression_values = [float(val) if isinstance(val, Decimal) else val for val in gene["gene_expression_values"]]
                gene_lengths.append(len(gene_expression_values))
                number_of_samples_per_brain_region+=len(gene_expression_values)

                # Calculate the total number of sample sizes
                total_number_of_samples+= len(gene_expression_values)

                # Print or process the values
                # logger.info(f"  Gene ID: {gene_id}")
                # logger.info(f"  Gene Expression Values (length {len(gene_expression_values)}): {gene_expression_values}...")  # Print first 5 values

            samples_sizes_per_brain_region.append(number_of_samples_per_brain_region)
            brain_regions.append(brain_region)
    
    return brain_regions, gene_ids, samples_sizes_per_brain_region, total_number_of_samples       


if __name__=="__main__":
    # Path of the meta_donor data
    brain_regions, brain_regions_gene_ids, samples_sizes_per_brain_region, total_number_of_samples= get_meta_donor_lists(PROCESSED_DONORS_GE_PATH / Path("meta_donor.json"))

    gene_ids = list(set(brain_regions_gene_ids))

    logger.info("Number of Total Brain Regions: ", len(brain_regions))
    logger.info("Number of Sample Sizes Calculated", len(samples_sizes_per_brain_region))
    logger.info("Number of Gene Ids", len(gene_ids))
    logger.info("Total Samples across all Brain Regions \n", total_number_of_samples)
    
    # Plots
    plot_values(brain_regions, samples_sizes_per_brain_region, "Number of Samples Per Brain Regions", 
                    "Brain Regions", "Number of Samples", True)

    plot_histogram(samples_sizes_per_brain_region, plot_title="Sample Size per Brain Region Histogram-20", 
                   x_title="Sample Size Per Brain Region", y_title="Number of Brain Regions (Frequence)", bins=20, save=True)      