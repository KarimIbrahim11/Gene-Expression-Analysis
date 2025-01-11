import re
import logging

from pathlib import Path

from utils.data import *
from utils.memory_management import *

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a console handler
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)
# Add the handler to the logger
logger.addHandler(sh)

# Raw data directory path has directories of the donors in the form normalized_microarray_donorxxxxx /
RAW_DATA_PATH = Path('data/raw')
PROCESSED_DATA_PATH = Path('data/processed')

if __name__ == "__main__":
    
    donor_pattern = r"^normalized_microarray_donor\d+$"
    donor_dirs = [d for d in RAW_DATA_PATH.iterdir() if d.is_dir() and re.match(donor_pattern, d.name)]
    for donor_path in donor_dirs:
        # Processing path
        logger.info(f"Processing data of {donor_path}")

        # Processing SampleAnnot to get the brain region id ("structure id")
        donor_sa = load_df_from_csv(donor_path / "SampleAnnot.csv")

        # Keep certain columns in the SampleAnnot.csv file
        donor_sa_processed = keep_df_cols(donor_sa, ["structure_id"])

        # Write processed file in processed directory
        write_df_to_csv(donor_sa_processed, PROCESSED_DATA_PATH / f"{get_donor_id_from_path(donor_path)}_SampleAnnot.csv")

        # Deallocate df
        deallocate_df(donor_sa)

        # Adding gene_id column to the sample gene_expressions.csv
        donor_ge = load_df_from_csv(donor_path / "MicroarrayExpression.csv")
        donor_probes = load_df_from_csv(donor_path / "Probes.csv")

        # Add Brain Region id as a column name in the gene_expression data
        donor_ge.columns = ['probe_id'] + list(donor_sa_processed["structure_id"])

        # Add gene_id Column in the gene_expressions data
        donor_ge.insert(0, 'gene_id', donor_probes['gene_id'])

        # Write processed file in processed directory
        write_df_to_csv(donor_ge, PROCESSED_DATA_PATH / f"{get_donor_id_from_path(donor_path)}_MicroarrayExpression.csv")






        
