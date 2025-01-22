import numpy as np
import matplotlib.pyplot as plt
from matplotlib import ticker

from typing import List
from pathlib import Path

from src.configs.config_parser import PathConfigParser, data_config_file, project_root

# Configs Directory
parser = PathConfigParser(str(data_config_file))
parser.load()

# Path of Plots 
PLOTS_PTH = project_root / parser.get("data_paths", {}).get("plots")
PLOTS_PTH.mkdir(parents=True, exist_ok=True)

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
