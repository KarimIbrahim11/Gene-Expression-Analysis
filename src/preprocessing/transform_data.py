import re
import json
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

# Raw data directory path has directories of the donors in the form normalized_microarray_donorxxxxx /
configs_dir = "src/configs/"

parser = PathConfigParser(configs_dir + "data_config.yaml")
parser.load()

# Access paths
RAW_DATA_PATH = parser.get("data_paths", {}).get("raw_data") 
PROCESSED_DATA_PATH = parser.get("data_paths", {}).get("processed_data")

def transform_sample_annotations(donor_sa: pd.DataFrame, left_mask : pd.Series) -> pd.DataFrame:
    # Keep certain columns in the SampleAnnot.csv file
    donor_sa_processed = keep_df_cols(donor_sa, ["structure_id", "structure_name"])
    deallocate_df(donor_sa)
    # Applying mask on Sample annotations file
    donor_sa_filtered= donor_sa_processed[left_mask].reset_index(drop=True)
    deallocate_df(donor_sa_processed)
    return donor_sa_filtered

def transform_gene_expressions(donor_ge: pd.DataFrame, left_mask : pd.Series) -> pd.DataFrame:
    # Applying mask on the Columns of the donor_ge file
    left_mask_ge = pd.concat([pd.Series([True], index=[0]), left_mask], ignore_index=True)
    left_mask_ge_filtered = left_mask_ge[left_mask_ge].index.values.tolist()
    donor_ge_filtered  = donor_ge.iloc[:, left_mask_ge_filtered]
    deallocate_df(donor_ge)
    return donor_ge_filtered
        
if __name__ == "__main__":
    
    donor_pattern = r"^normalized_microarray_donor\d+$"
    donor_dirs = [d for d in RAW_DATA_PATH.iterdir() if d.is_dir() and re.match(donor_pattern, d.name)]
    donors_ges = []
    for donor_path in donor_dirs:
        # Processing path
        logger.info(f"Processing data of {donor_path}")

        # Processing SampleAnnot to get the brain region id ("structure id")
        donor_sa = load_df_from_csv(donor_path / "SampleAnnot.csv")
        # Create a mask for left hemisphere entries
        left_mask = mask_left_hemisphere(donor_sa)
        # Transform donor_sa
        donor_sa_filtered = transform_sample_annotations(donor_sa, left_mask)
        # Write processed file in processed directory
        write_df_to_csv(donor_sa_filtered, PROCESSED_DATA_PATH / f"sample_annotations/{get_donor_id_from_path(donor_path)}.csv")

        # Loading Gene Expressions
        donor_ge = load_df_from_csv(donor_path / "MicroarrayExpression.csv")
        # Transform Gene Expressions
        donor_ge_filtered = transform_gene_expressions(donor_ge, left_mask)
        # Load probes data 
        donor_probes = load_df_from_csv(donor_path / "Probes.csv")
        # Add Brain Region id as a column name in the gene_expression data
        donor_ge_filtered.columns = ['probe_id'] + list(donor_sa_filtered["structure_id"])
        deallocate_df(donor_sa_filtered)
        # Add gene_id Column in the gene_expressions data
        donor_ge_filtered.insert(0, 'gene_id', donor_probes['gene_id'])
        # Write processed file in processed directory
        write_df_to_csv(donor_ge_filtered, PROCESSED_DATA_PATH / f"gene_expressions/{get_donor_id_from_path(donor_path)}.csv")

        # Drop probe_id column        
        donor_ge_filtered = donor_ge_filtered.drop(columns=['probe_id'])
        # Create a new CSV with grouped gene_ids by melting the DataFrame to make it easier to manipulate
        df_melted = donor_ge_filtered.melt(id_vars=["gene_id"], var_name="brain_region", value_name="gene_expression_values")
        # Now, group by brain_region and gene_id  and aggregate the test values into lists
        df_grouped = df_melted.groupby(["brain_region", "gene_id"])["gene_expression_values"].apply(list).reset_index()
        # apply json dumps to be able to load the file appropiately
        df_grouped["gene_expression_values"] = df_grouped["gene_expression_values"].apply(json.dumps)
        # Save the grouped csvs per each donor
        write_df_to_csv(df_grouped, PROCESSED_DATA_PATH / f"brain_regions_genes_geneexpressions/{get_donor_id_from_path(donor_path)}_grouped.csv")
        deallocate_df(df_melted)
        deallocate_df(donor_ge_filtered)

        # Create a new CSV with brain region and corresponding gene ids
        brain_region_samples = df_grouped.groupby("brain_region")["gene_id"].apply(list).reset_index()
        write_df_to_csv(brain_region_samples, PROCESSED_DATA_PATH / f"brain_region_samples/{get_donor_id_from_path(donor_path)}_samples.csv")
        deallocate_df(df_grouped)
        deallocate_df(brain_region_samples)

        


        
