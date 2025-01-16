import logging
import ijson
import json
import numpy as np
from decimal import Decimal
from pathlib import Path
from typing import List, Tuple

from src.utils.data import *
from src.utils.sampling import *
from src.utils.plots import *
from src.utils.memory_management import *
from src.configs.config_parser import PathConfigParser, data_config_file

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a console handler
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
# Add the handler to the logger
logger.addHandler(sh)

# Configs Directory
parser = PathConfigParser(str(data_config_file))
parser.load()

# parser = PathConfigParser(configs_dir + "data_config.yaml")
# parser.load()

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
    samples_sizes_br = []
    samples_sizes_br_ge = []
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
                samples_sizes_br_ge.append(len(gene_expression_values))
                number_of_samples_per_brain_region+=len(gene_expression_values)

                # Calculate the total number of sample sizes
                total_number_of_samples+= len(gene_expression_values)

                # Print or process the values
                # logger.info(f"  Gene ID: {gene_id}")
                # logger.info(f"  Gene Expression Values (length {len(gene_expression_values)}): {gene_expression_values}...")  # Print first 5 values

            samples_sizes_br.append(number_of_samples_per_brain_region)
            brain_regions.append(brain_region)
    
    return brain_regions, gene_ids, samples_sizes_br, samples_sizes_br_ge, total_number_of_samples,      

def main():
    # EXP1 
    # Path of the meta_donor data
    # meta_donor_json_pth = PROCESSED_DONORS_GE_PATH / Path("meta_donor.json")
    # brain_regions, brain_regions_gene_ids, samples_sizes_br, samples_sizes_br_ge, total_number_of_samples= get_meta_donor_lists(meta_donor_json_pth)

    # gene_ids = list(set(brain_regions_gene_ids))

    # logger.info(f"Number of Total Brain Regions: {len(brain_regions)}")
    # logger.info(f"Number of Sample Sizes Calculated {len(samples_sizes_br)}")
    # logger.info(f"Number of Gene Ids  {len(gene_ids)}")
    # logger.info(f"Total Samples across all Brain Regions {total_number_of_samples}")
    
    # #Plots
    # plot_values(brain_regions, samples_sizes_br, "Number of Samples Per Brain Regions", 
    #                 "Brain Regions", "Number of Samples", True)

    # plot_histogram(samples_sizes_br, plot_title="Sample Size per Brain Region Histogram-20", 
    #                x_title="Sample Size Per Brain Region", y_title="Number of Brain Regions (Frequence)", bins=20, save=True)      
    
    # EXP2
    meta_donor_csv_pth = PROCESSED_DONORS_GE_PATH / Path("meta_donor.csv")
    meta_donor_df = load_df_from_csv(meta_donor_csv_pth)

    meta_donor_df["gene_expression_values"]=meta_donor_df["gene_expression_values"].apply(json.loads)
    logger.info(meta_donor_df["gene_expression_values"][0][0])
    
    total_number_of_samples = get_total_number_of_samples(meta_donor_df)
    logger.info(f"Number of Total Samples: {total_number_of_samples}")

    number_of_br = get_total_number_of_br(meta_donor_df)
    logger.info(f"Number of Total Brain Regions: {number_of_br}")

    number_of_ge_per_br = get_number_of_genes_per_br(meta_donor_df)
    logger.info(f"Number of Genes ids per Brain Region: \n{number_of_ge_per_br}")

    number_of_samples_per_br = get_number_of_samples_per_br(meta_donor_df)
    logger.info(f"Number of Samples per Brain Region:\n{number_of_samples_per_br}")

    number_of_samples_per_br_ge = get_number_of_samples_per_br_ge(meta_donor_df)
    logger.info(f"Number of Samples per Brain Region-Gene Id pair:\n{number_of_samples_per_br_ge}")

    br_ids = get_br_list(meta_donor_df)
    logger.info(f"List of Brain Regions:\n{br_ids}")

    sample = get_br_ge_sample(meta_donor_df, 4012, 2)
    logger.info(f"Sample of Brain Region-Gene Id pair\n{sample}")

    plot_values(br_ids, number_of_samples_per_br, "Number of Samples Per Brain Regions_python_test", 
                    "Brain Regions", "Number of Samples", True)


if __name__=="__main__":
   main()