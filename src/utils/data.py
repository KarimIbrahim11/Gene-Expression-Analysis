import pandas as pd
from typing import List
from pathlib import Path


def load_df_from_csv(path: Path) -> pd.DataFrame:
    """
        Loads df from csv path
    """
    return pd.read_csv(path)

def write_df_to_csv(df: pd.DataFrame, path:Path) -> None:  
    """
        Writes df to csv path
    """
    # Create the directory if it doesn't exist
    path.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def keep_df_cols(df:  pd.DataFrame, cols: List) -> pd.DataFrame: 
    """
        General helper for keeping cols in a column list
    """
    return df[cols] if cols else None

def keep_df_m_cols(df: pd.DataFrame, m: int) -> pd.DataFrame:
    """
        General helper for bissecting a dataframe m cols
    """
    return df.iloc[:, 0:m]

def keep_df_n_rows(df: pd.DataFrame, n: int) -> pd.DataFrame:
    """
        General helper for bissecting a dataframe n rows
    """
    return df.iloc[0:n, :]

def keep_df_n_rows_m_cols(df: pd.DataFrame, n: int, m: int) -> pd.DataFrame:
    """
        General helper for bissecting a dataframe n rows and m cols
    """
    return df.iloc[0:n, 0:m]

def get_donor_id_from_path (path: Path) -> int:
    """
        Retrieves the donor id from the path
    """
    number = ""
    for char in reversed(str(path)):
        if char.isdigit():
            number = char + number
        else:
            # Stop when we reach a non-digit character
            break
    # If we found a number, return it
    return int(number) if number else None

def mask_left_hemisphere(sample_annotations: pd.DataFrame) -> pd.Series:
    """
        Filtering out probe samples from the right hemisphere and returns mask
    """
    # Check for rows in sample_annotations where the entries in 'structure_name' contain the word 'left'
    return sample_annotations['structure_name'].str.contains(r'\bleft\b', case=False, na=False)

   