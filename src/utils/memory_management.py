import gc
import pandas as pd


def deallocate_df(df: pd.DataFrame) -> None:
        # df is your DataFrame
        del df  # Removes the reference to df

        # Force garbage collection to free up memory
        gc.collect()
