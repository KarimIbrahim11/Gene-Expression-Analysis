import json
from ast import literal_eval
import logging
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

# Configs Directory
configs_dir = "src/configs/"

# Configuration Parser Loading
parser = PathConfigParser(configs_dir + "data_config.yaml")
parser.load()

# Access paths 
PROCESSED_DATA_PATH = parser.get("data_paths", {}).get("processed_data")
GE_PATH = parser.get("data_paths", {}).get("brain_regions_genes_ge")
PROCESSED_DONORS_GE_PATH = PROCESSED_DATA_PATH / GE_PATH

# Donors_ids
DONORS_IDS = parser.get("donors_ids")

def write_geneexpressions_to_json(df: pd.DataFrame, pth: Path) -> None:
    """
        Specific to writing gene_expression files to json and keep the lists as numbers
    """
    # Ensure 'gene_expression_values' is a list, not a string
    df["gene_expression_values"] = df["gene_expression_values"].apply(
        lambda x: literal_eval(x) if isinstance(x, str) else x
    )
    # Group by `brain_region`
    grouped = (
        df.groupby("brain_region")
        .apply(lambda x: x[["gene_id", "gene_expression_values"]].to_dict(orient="records"))
        .to_dict()
    )
    # Change group keys to number
    grouped = {int(key): value for key, value in grouped.items()}

    # Write grouped data to JSON
    with open(pth, "w") as f:
        json.dump(grouped, f, indent=4)

if __name__== "__main__":
    # Creating Json files for Hierarchal Data
    for donor in DONORS_IDS:
        logger.info(f"Creating donor id: {str(donor)} json file")
        # Load donor csv from processed data 
        donor_ge = load_df_from_csv(PROCESSED_DONORS_GE_PATH / Path(f"{donor}_grouped.csv"))
        write_geneexpressions_to_json(donor_ge, PROCESSED_DONORS_GE_PATH / Path(f"{donor}_grouped.json"))
    # Creating Meta Donor Json File
    logger.info(f"Creating meta_donor.json file")
    meta_donor_ge = load_df_from_csv(PROCESSED_DONORS_GE_PATH / Path(f"meta_donor.csv"))
    write_geneexpressions_to_json(meta_donor_ge, PROCESSED_DONORS_GE_PATH / Path(f"meta_donor.json"))