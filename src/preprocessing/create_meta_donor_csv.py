import logging
import json
from pathlib import Path

from src.utils.data import *
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

PROCESSED_DATA_PATH = parser.get("data_paths", {}).get("processed_data")
GE_PATH = parser.get("data_paths", {}).get("brain_regions_genes_ge")
PROCESSED_DONORS_GE_PATH = PROCESSED_DATA_PATH / GE_PATH

# Donors_ids
DONORS_IDS = parser.get("donors_ids")

def main():
    donor_ges = []

    # Loading previously transformed files and creating the meta_donor.csv file
    for donor in DONORS_IDS:
        # Load donor .csv from processed data 
        donor_ge = load_df_from_csv(PROCESSED_DONORS_GE_PATH / Path(f"{donor}_grouped.csv"))
        logger.info(f"Donor Id: {str(donor)}")
        logger.info(f"Number of brain regions: {donor_ge['brain_region'].nunique()}")
        logger.info(f"Number of gene ids: {donor_ge['gene_id'].nunique()}")
        donor_ge["gene_expression_values"]=donor_ge["gene_expression_values"].apply(json.loads)
        donor_ges.append(donor_ge)
        deallocate_df(donor_ge)

    # Finding common brain regions and filtering the others out
    common_brain_regions = set.intersection(*(set(donor_ge['brain_region']) for donor_ge in donor_ges))
    logger.info(f"Number of common brain regions: {len(common_brain_regions)}")

    # Keep only the common columns in each DataFrame
    filtered_donors_ges = [donor_ge[donor_ge['brain_region'].isin(common_brain_regions)] for donor_ge in donor_ges]
    set(filtered_donors_ges[3]['brain_region'])==common_brain_regions

    # Concatenate all filtered DataFrames
    meta_donor_df = pd.concat(filtered_donors_ges, ignore_index=True)
    logger.info(f"meta_donor_df size:{len(meta_donor_df)}")
    logger.info(f"Meta Donor DF has only list of common_brain_regions: {set(meta_donor_df['brain_region'])==common_brain_regions}")

    concatenated_ges = meta_donor_df.groupby(["brain_region", "gene_id"])["gene_expression_values"].apply(lambda x: sum(x, [])).reset_index()

    write_df_to_csv(concatenated_ges, PROCESSED_DONORS_GE_PATH / f"meta_donor.csv")

if __name__ == "__main__":
    main()