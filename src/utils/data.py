import re
import pandas as pd
from typing import List
from pathlib import Path


def load_df_from_csv(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)

def write_df_to_csv(df: pd.DataFrame, path:Path) -> pd.DataFrame:  df.to_csv(path, index=False)


def keep_df_cols(df:  pd.DataFrame, cols: List) -> pd.DataFrame: 
    return df[cols] if cols else None

def keep_df_m_cols(df: pd.DataFrame, m: int) -> pd.DataFrame:
    return df.iloc[:, 0:m]

def keep_df_n_rows(df: pd.DataFrame, n: int) -> pd.DataFrame:
    return df.iloc[0:n, :]

def keep_df_n_rows_m_cols(df: pd.DataFrame, n: int, m: int) -> pd.DataFrame:
    return df.iloc[0:n, 0:m]


def get_donor_id_from_path (path: Path) -> int:
    number = ""
    for char in reversed(str(path)):
        if char.isdigit():
            number = char + number
        else:
            # Stop when we reach a non-digit character
            break
    # If we found a number, return it
    return int(number) if number else None