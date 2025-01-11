from utils.data import load_df_from_csv, keep_df_n_rows_m_cols

df = load_df_from_csv("data/raw/normalized_microarray_donor9861/MicroarrayExpression.csv")

print(keep_df_n_rows_m_cols(df, 10, 2))
