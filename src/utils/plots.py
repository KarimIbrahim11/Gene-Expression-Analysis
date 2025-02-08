import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import ticker

from typing import List
from pathlib import Path

from src.configs.config_parser import PathConfigParser, data_config_file, project_root

from matplotlib.patches import Patch
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from scipy.cluster.hierarchy import dendrogram, linkage


from matplotlib.colors import LinearSegmentedColormap
from nilearn import plotting
from nilearn.image import new_img_like, smooth_img
from nilearn.datasets import load_mni152_template
import nibabel as nib


# Configs Directory
parser = PathConfigParser(str(data_config_file))
parser.load()

# Path of Plots 
PLOTS_PTH = project_root / parser.get("output_paths", {}).get("plots")
PLOTS_PTH.mkdir(parents=True, exist_ok=True)


# Define colors using a modern, muted color palette for clusters
cluster_colors = {
    0: sns.color_palette("muted")[0],  # Soft Blue for Cluster 0
    1: sns.color_palette("muted")[3],  # Soft Red for Cluster 1
    2: 'green',  # Soft Green for Cluster 2
}

# Define modern colors for mean and variance
mean_color = "#2D2D2D"  # Dark gray for mean (modern and minimal)
variance_color = "#B0B0B0"  # Light gray for variance
threshold_color = "#707070"  # Muted Dark Gray or Slate Gray


def plot_values(x: List[int], y: List[int], plot_title: str= "Values per Label", x_title: str="Labels", y_title: str="Values", save: bool = False)-> None:
    """
        A generic function for plotting x agains the y 
    """
    # Line plot with markers
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_facecolor('seashell')
    formatter = ticker.ScalarFormatter()
    formatter.set_scientific(False)

    # plot
    ax.plot(x, y, marker='o', linestyle='-', color='b')

    # Customize Y-axis ticks
    ax.xaxis.set_major_formatter(formatter)
    ax.yaxis.set_major_formatter(formatter)
    ax.ticklabel_format(style='plain')

    # x_ticks_interval = 10  # Show every 10th tick
    # ax.set_xticks(np.arange(0, len(x), x_ticks_interval))  # Set positions for x ticks
    # ax.set_xticklabels(x[::x_ticks_interval], rotation=45, ha='right')  # Display every 10th label with rotation

    # Labeling
    ax.set_xlabel(x_title)
    ax.set_ylabel(y_title)
    ax.set_title(plot_title)
    # ax.tick_params(axis='x', rotation=90)
    ax.grid(True)

    # Save if necessary
    if save:
        fig.savefig(PLOTS_PTH / Path(f"{plot_title}.png"), dpi=300, bbox_inches='tight')

    # Show plot
    fig.tight_layout()
    plt.show()
    plt.close()

def plot_histogram(values: List[int], plot_title: str= "Values per Label", x_title: str="Labels", y_title: str="Values", bins: int = 10, save: bool = False)-> None:
    """
        A generic function for a histogram of the values
    """
    
    # Compute statistics
    mean_value = np.mean(values)
    std_dev = np.std(values)

    # Plot histogram
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_facecolor('seashell')
    formatter = ticker.ScalarFormatter()
    formatter.set_scientific(False)

    # Plot histogram
    ax.hist(values, bins=bins, color='skyblue', edgecolor='black', alpha=0.7, label=plot_title)

    # Customize ticks
    ax.xaxis.set_major_formatter(formatter)
    ax.yaxis.set_major_formatter(formatter)
    ax.ticklabel_format(style='plain')

    # Enable grid
    ax.grid(axis='y', linestyle='--', linewidth=0.5, alpha=0.7)

    # Add mean and std deviation lines
    ax.axvline(mean_value, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_value:.2f}')
    ax.axvline(mean_value + std_dev, color='green', linestyle='--', linewidth=2, label=f'+1 Std Dev: {mean_value + std_dev:.2f}')
    ax.axvline(mean_value - std_dev, color='green', linestyle='--', linewidth=2, label=f'-1 Std Dev: {mean_value - std_dev:.2f}')

    # Labeling
    ax.set_title(plot_title)
    ax.set_xlabel(x_title)
    ax.set_ylabel(y_title)
    ax.legend()

    # Save if necessary
    if save:
        fig.savefig(PLOTS_PTH / Path(f"{plot_title}.png"), dpi=300, bbox_inches='tight')

    # Show plot
    fig.tight_layout()
    plt.show()
    plt.close()



def plot_scatter_log(x: List[int], y: List[int], plot_title: str = "Values per Label", x_title: str = "Labels", 
                     y_title: str = "Values", label: str = "(X,Y)", save: bool = False) -> None:
    """
    A generic function for a scatter plot of the values with connected lines and a logarithmic x-axis (base 2).
    """
    # Create a plot with connected lines
    plt.figure(figsize=(10, 6))
    plt.plot(x, np.log(y), color='gray', marker='o', linestyle='-', label=label)

    # Annotate each point with its original value
    for xi, yi in zip(x, np.log(y)):
        plt.text(xi, yi, f'  ({round(np.exp(yi))})', fontsize=9, ha='left', color='black')

    # Set x-axis to logarithmic scale with base 2
    plt.xscale("log", base=2)
    
    # Set x-axis ticks to powers of 2
    x_ticks = [2**i for i in range(3, 11)]
    plt.xticks(x_ticks, [f"$2^{{{i}}}$" for i in range(3, 11)], fontsize=8)

    # Remove the top and right spines
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)

    # Add labels, title, and legend
    plt.xlabel(x_title)
    plt.ylabel(y_title)
    plt.title(plot_title, pad=20)  # Increase pad to move the title further away
    plt.legend()
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)

    # Save the plot as a PNG file
    if save:
        plt.savefig(plot_title, dpi=300, bbox_inches='tight')

    # Display the plot
    plt.show()
    
    
import matplotlib.pyplot as plt
import numpy as np
from typing import List

def plot_multiple_scatter_log(x: List[int], y_lists: List[List[int]], threshold: int = -1, plot_title: str = "Values per Label", 
                     x_title: str = "Labels", y_title: str = "Values", labels: List[str] = None, 
                     save: bool = False) -> None:
    """
    A generic function for a scatter plot of multiple y lists with connected lines and a logarithmic x-axis (base 2).
    
    Parameters:
        x (List[int]): The x-axis values (common for all y lists).
        y_lists (List[List[int]]): A list of y-axis value lists.
        plot_title (str): Title of the plot.
        x_title (str): Label for the x-axis.
        y_title (str): Label for the y-axis.
        labels (List[str]): Labels for each y list in the legend.
        save (bool): Whether to save the plot as a PNG file.
    """
    # Create a plot with connected lines
    plt.figure(figsize=(10, 5))

    # Plot each y list
    for i, y in enumerate(y_lists):
        # Use the corresponding label if provided, otherwise use a default label
        label = labels[i] if labels else f"Y{i+1}"
        # Plot the line
        plt.plot(x, np.log(y), color=cluster_colors[i], marker='o', linestyle='-', label=label)

        # Annotate each point with its original value
        for xi, yi in zip(x, np.log(y)):
            if xi == threshold and threshold !=-1:
                plt.text(
                    xi, 
                    yi, 
                    f' ({round(np.exp(yi))})', 
                    fontsize=9, 
                    ha='left',  # Horizontally center text above point
                    va='bottom',  # Position text above point   
                    color=cluster_colors[i], 
                    zorder=10,
                    bbox=dict(facecolor='white', edgecolor='none', boxstyle='round,pad=0.001', alpha=0.6)  # Set alpha for transparency
                )



    # Set x-axis to logarithmic scale with base 2
    plt.xscale("log", base=2)
    
    # Set x-axis ticks to powers of 2
    x_ticks = [2**i for i in range(3, 11)]
    plt.xticks(x_ticks, [f"$2^{{{i}}}$" for i in range(3, 11)], fontsize=10)
    
    plt.yticks(fontsize=10)
    # Remove the top and right spines
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)

    # draw threshold colour
    if threshold !=-1:
        plt.axvline(x=threshold, color=threshold_color, linestyle='--', linewidth=1, label="Threshold")


    # Add labels, title, and legend
    plt.xlabel(x_title)
    plt.ylabel(y_title)
    plt.title(plot_title, pad=20)  # Increase pad to move the title further away
    plt.legend()
    plt.grid(True, which="both", linestyle="--", linewidth=0.5)

    # Save the plot as a PNG file
    if save:
        plt.savefig(plot_title, dpi=300, bbox_inches='tight')

    # Display the plot
    plt.show()
    
    
    
    
def create_cluster_image(cluster_data, color_value, fwhm=6):
    """Create a smoothed 3D image for a single cluster"""
    # Merge with the expanded coordinates
    # cluster_data = cluster.merge(all_coordinates_expanded, 
    #                            left_on='brain_region', 
    #                            right_on='structure_id')
    
    # Use the _y coordinates (from all_coordinates_expanded)
    coords = cluster_data[['mni_x', 'mni_y', 'mni_z']].values
    
    # Load template and get affine transformation
    template = load_mni152_template()
    affine = template.affine
    
    # Initialize empty volume
    data = np.zeros(template.shape)
    
    # Create a sphere for each coordinate
    for x, y, z in coords:
        # Convert MNI coordinates to voxel coordinates
        vox_coords = nib.affines.apply_affine(np.linalg.inv(affine), 
                                            np.array([[x, y, z]]))
        vox_coords = np.round(vox_coords[0]).astype(int)
        
        # Ensure coordinates are within bounds
        if (0 <= vox_coords[0] < data.shape[0] and 
            0 <= vox_coords[1] < data.shape[1] and 
            0 <= vox_coords[2] < data.shape[2]):
            
            # Create a small sphere around the point
            xx, yy, zz = np.ogrid[-2:3, -2:3, -2:3]
            sphere = (xx**2 + yy**2 + zz**2 <= 2**2)
            
            # Get coordinates for the sphere
            x_coords = np.clip(vox_coords[0] + xx, 0, data.shape[0]-1)
            y_coords = np.clip(vox_coords[1] + yy, 0, data.shape[1]-1)
            z_coords = np.clip(vox_coords[2] + zz, 0, data.shape[2]-1)
            
            # Set the sphere value
            data[x_coords, y_coords, z_coords] = np.where(sphere, color_value, data[x_coords, y_coords, z_coords])
    
    # Create image
    img = new_img_like(template, data, affine=affine)
    
    # Apply smoothing
    smoothed_img = smooth_img(img, fwhm=fwhm)
    
    return smoothed_img
