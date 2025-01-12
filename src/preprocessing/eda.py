import logging

import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from mpl_toolkits.mplot3d import Axes3D

from utils.data import *
from configs.config_parser import PathConfigParser



# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a console handler
sh = logging.StreamHandler()
sh.setLevel(logging.INFO)

# Add the handler to the logger
logger.addHandler(sh)

configs_dir = "src/configs/"

parser = PathConfigParser(configs_dir + "data_config.yaml")
parser.load()

# Access paths
PROCESSED_DATA_PATH = parser.get("data_paths", {}).get("processed_data")
GE_PATH = parser.get("data_paths", {}).get("genes")
PROCESSED_DONORS_GE_PATH = PROCESSED_DATA_PATH / GE_PATH 

# Donors_ids
DONORS_IDS = parser.get("donors_ids")

def save_correlation_heat_map(df: pd.DataFrame, path: Path, title: str) ->  None:
    """
    Save Correlation Heat Map from df
    """
    # Correlation heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(df.corr(), annot=False, cmap='coolwarm')
    plt.title(title)
    plt.savefig(path, dpi=300, bbox_inches='tight')
    plt.show()
    plt.close()



if __name__ == "__main__":
    for donor_ge_path in PROCESSED_DONORS_GE_PATH.iterdir():
        # Check if the file is a file (not a directory) and if its name matches any ID in the list
        if donor_ge_path.is_file() and int(donor_ge_path.stem) in DONORS_IDS:
            donor_ge = load_df_from_csv(donor_ge_path)
            donor_id = donor_ge_path.stem

            # Saving Brain Region Correlation Maps
            brain_correlation_pth = parser.get("data_paths", {}).get("analysis")/ Path("Brain Region Correlation")
            brain_correlation_pth.mkdir(parents=True, exist_ok=True)
            save_correlation_heat_map(donor_ge.iloc[:, 2:], brain_correlation_pth / Path(donor_id),
                                      f"Brain Region Correlation heatmap of {donor_id}")
            
            # # Distribution for a single brain region
            # plt.hist(donor_ge['4215'], bins=30, color='blue', edgecolor='black')

            # # Add labels and title
            # plt.xlabel('Values')
            # plt.ylabel('Gene Expression Values')
            # plt.title("Distribution of Region 4215")
            # plt.show()

            # # PCA for dimensionality reduction
            # brain_region_data = donor_ge.iloc[:, 2:].values
            # pca = PCA(n_components=3)
            # pca_result = pca.fit_transform(brain_region_data)
            # donor_ge['PCA1'] = pca_result[:, 0]
            # donor_ge['PCA2'] = pca_result[:, 1]
            # donor_ge['PCA3'] = pca_result[:, 2]

            # # Create a 3D plot
            # fig = plt.figure(figsize=(8, 6))
            # ax = fig.add_subplot(111, projection='3d')

            # # Scatter plot
            # sc = ax.scatter(donor_ge['PCA1'], donor_ge['PCA2'], donor_ge['PCA3'], c='b', marker='o')

            # # Add labels
            # ax.set_xlabel('PCA1')
            # ax.set_ylabel('PCA2')
            # ax.set_zlabel('PCA3')
            # ax.set_title('PCA of Brain Region Data')

            # plt.show()
            
            # break