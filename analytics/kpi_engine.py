import pandas as pd

def get_numeric_columns(df):
    return df.select_dtypes(include=["int64", "float64"]).columns.tolist()

def get_categorical_columns(df):
    return df.select_dtypes(include=["object"]).columns.tolist()

def generate_kpis(df):
    numeric_columns = get_numeric_columns(df)

    kpis = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "numeric_columns": len(numeric_columns),
        "categorical_columns": len(get_categorical_columns(df))
    }

    return kpis