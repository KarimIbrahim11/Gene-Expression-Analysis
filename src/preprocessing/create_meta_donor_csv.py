import logging
import json
from pathlib import Path

from utils.data import *
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

# Raw data directory path has directories of the donors in the form normalized_microarray_donorxxxxx /
configs_dir = "src/configs/"

parser = PathConfigParser(configs_dir + "data_config.yaml")
parser.load()

PROCESSED_DATA_PATH = parser.get("data_paths", {}).get("processed_data")
GE_PATH = parser.get("data_paths", {}).get("brain_regions_genes_ge")
PROCESSED_DONORS_GE_PATH = PROCESSED_DATA_PATH / GE_PATH

# Donors_ids
DONORS_IDS = parser.get("donors_ids")

if __name__ == "__main__":
    donor_ges = []
    for donor in DONORS_IDS:
        # Load donor csv from processed data 
        donor_ge = load_df_from_csv(PROCESSED_DONORS_GE_PATH / Path(f"{donor}_grouped.csv"))
        # logger.info(donor_ge.describe())
        logger.info(f"Donor Id: {str(donor)}")
        logger.info(f"Number of brain regions: {donor_ge['brain_region'].nunique()}")
        logger.info(f"Number of gene ids: {donor_ge['gene_id'].nunique()}")
        donor_ge["gene_expression_values"]=donor_ge["gene_expression_values"].apply(json.loads)
        donor_ges.append(donor_ge)
        deallocate_df(donor_ge)

    # Finding common brain regions and filtering them out
    common_brain_regions = set.intersection(*(set(donor_ge['brain_region']) for donor_ge in donor_ges))

    print("Number of common brain regions", len(common_brain_regions))

    meta_donor_df = pd.concat(donor_ges, ignore_index=True)

    # print("Types: ", meta_donor_df["gene_expression_values"].apply(type).unique())

    # meta_donor_df["gene_expression_values"] = meta_donor_df["gene_expression_values"].apply(
    # lambda x: x if isinstance(x, list) else [x])

    # print("Types: ", meta_donor_df["gene_expression_values"].apply(type).unique())

    print(meta_donor_df.head(5))

    concatenated_ges = meta_donor_df.groupby(["brain_region", "gene_id"])["gene_expression_values"].apply(lambda x: sum(x, [])).reset_index()

    write_df_to_csv(concatenated_ges, PROCESSED_DONORS_GE_PATH / f"meta_donor_1.csv")


    # print("Common Brain Regions", common_brain_regions)

    # # Keep only the common columns in each DataFrame
    # filtered_ges = [donor_ge[list(common_brain_regions)] for donor_ge in donor_ges]

    # # Concatenate all filtered DataFrames
    # concatenated_ges = pd.concat(filtered_ges, ignore_index=True)
        
    # # Write processed file in processed directory
    # write_df_to_csv(concatenated_ges, PROCESSED_DATA_PATH / f"gene_expressions/combined.csv")      

