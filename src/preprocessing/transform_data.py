import re
import json
import logging
import numpy as np
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

def write_df_to_json(df: pd.DataFrame) -> None:
    # Create a dictionary to hold the restructured data
    restructured_data = {}

    # Iterate over the columns (brain regions)
    for col in df.columns[1:]:  # Skip the first column which is gene_id
        # Create a dictionary for each brain region
        region_data = {}
        
        # Iterate through the rows for each gene_id
        for idx, row in df.iterrows():
            gene_id = row['gene_id']
            test_value = row[col]
            
            # If the gene_id is not already in the dictionary, add it with an empty list
            if gene_id not in region_data:
                region_data[gene_id] = []
            
            # Append the test value to the gene_id entry
            region_data[gene_id].append(test_value)
        
        # Add the region_data for the current brain region to the restructured_data dictionary
        restructured_data[col] = region_data

    # Convert the dictionary to JSON
    json_output = json.dumps(restructured_data, indent=4)
        
if __name__ == "__main__":
    
    donor_pattern = r"^normalized_microarray_donor\d+$"
    donor_dirs = [d for d in RAW_DATA_PATH.iterdir() if d.is_dir() and re.match(donor_pattern, d.name)]
    donors_ges = []
    for donor_path in donor_dirs:
        # Processing path
        logger.info(f"Processing data of {donor_path}")

        # Processing SampleAnnot to get the brain region id ("structure id")
        donor_sa = load_df_from_csv(donor_path / "SampleAnnot.csv")

        # Keep certain columns in the SampleAnnot.csv file
        donor_sa_processed = keep_df_cols(donor_sa, ["structure_id"])

        # Write processed file in processed directory and deallocate it
        write_df_to_csv(donor_sa_processed, PROCESSED_DATA_PATH / f"sample_annotations/{get_donor_id_from_path(donor_path)}.csv")
        deallocate_df(donor_sa)

        # Adding gene_id column to the sample gene_expressions.csv
        donor_ge = load_df_from_csv(donor_path / "MicroarrayExpression.csv")
        donor_probes = load_df_from_csv(donor_path / "Probes.csv")

        # Add Brain Region id as a column name in the gene_expression data
        donor_ge.columns = ['probe_id'] + list(donor_sa_processed["structure_id"])

        # Add gene_id Column in the gene_expressions data
        donor_ge.insert(0, 'gene_id', donor_probes['gene_id'])

        # Write processed file in processed directory
        write_df_to_csv(donor_ge, PROCESSED_DATA_PATH / f"gene_expressions/{get_donor_id_from_path(donor_path)}.csv")

        # Drop probe_id column        
        donor_ge = donor_ge.drop(columns=['probe_id'])

        # Create a new CSV with grouped gene_ids by melting the DataFrame to make it easier to manipulate
        df_melted = donor_ge.melt(id_vars=["gene_id"], var_name="brain_region", value_name="gene_expression_values")

        # Now, group by brain_region and gene_id  and aggregate the test values into lists
        df_grouped = df_melted.groupby(["brain_region", "gene_id"])["gene_expression_values"].apply(list).reset_index()

        # Save the grouped csvs per each donor
        write_df_to_csv(df_grouped, PROCESSED_DATA_PATH / f"brain_regions_genes_geneexpressions/{get_donor_id_from_path(donor_path)}_grouped.csv")
        deallocate_df(df_melted)
        deallocate_df(donor_ge)

        # Create a new CSV with brain region and corresponding gene ids
        brain_region_samples = df_grouped.groupby("brain_region")["gene_id"].apply(list).reset_index()
        write_df_to_csv(brain_region_samples, PROCESSED_DATA_PATH / f"brain_regions_genes/{get_donor_id_from_path(donor_path)}_samples.csv")
        deallocate_df(df_grouped)
        deallocate_df(brain_region_samples)

        


        
