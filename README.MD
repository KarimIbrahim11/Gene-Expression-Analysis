# Project Setup Instructions

This guide will help you set up the project by installing Poetry, cloning the repository, and setting up the environment.

## Prerequisites

Ensure you have the following installed:

- **Git** (for cloning the repository)
- **Python 3.8+** (make sure it is installed and accessible in your terminal)

## Steps to Set Up the Project

### 1. Install Poetry (version 1.8.3)

Poetry is a tool for dependency management and packaging in Python. To install Poetry version 1.8.3, follow these steps:

#### For Unix-based Systems (Linux/macOS):

Run the following command to install Poetry version 1.8.3:

```bash
curl -sSL https://install.python-poetry.org | python3 - --version 1.8.3
```

You can confirm the installation by running the command:
```bash
poetry --version
```
and the result should be:
```bash
Poetry (version 1.8.3)
```

#### For Windows:

Use the documentation for [Poetry installation](https://python-poetry.org/docs/1.8/]) to guide you.


### 2. Install Dependencies using Poetry 

Clone the repo: 
```bash
git clone https://github.com/KarimIbrahim11/Gene-Expression-Analysis.git
```
Then run the commands in order: 
```bash 
cd gene-expression-analysis
poetry install
poetry shell
```
To run a `*.py` file: 
```bash
python <RELATIVE PATH OF THE PYTHON FILE>
```
or
```bash
poetry run python <RELATIVE PATH OF THE PYTHON FILE>
```

### 3. Download Dataset

To download the dataset simply run: 
```bash
poetry src/download_dataset.py
```
You should be seeing:
```bash
Downloading from URL: https://human.brain-map.org/api/v2/well_known_file_download/178238387
normalized_microarray_donor9861.zip:   1%|▋                                                                                                 | 2.91M/426M [00:09<23:15, 303kB/s
...
```
dataset will be downloaded in `data/raw`. 
