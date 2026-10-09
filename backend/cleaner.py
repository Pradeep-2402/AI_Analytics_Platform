import pandas as pd

def clean_dataset(df):
    error_records = []

    before_rows = len(df)

    df = df.drop_duplicates()

    for col in df.columns:
        if df[col].isnull().sum() > 0:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].fillna(df[col].median())
            else:
                df[col] = df[col].fillna("Unknown")

    after_rows = len(df)

    cleaning_summary = {
        "rows_before": before_rows,
        "rows_after": after_rows,
        "duplicates_removed": before_rows - after_rows,
        "remaining_nulls": int(df.isnull().sum().sum())
    }

    error_df = pd.DataFrame(error_records)

    return df, error_df, cleaning_summary