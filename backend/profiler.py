import pandas as pd

def profile_dataset(df):
    profile = {}

    profile["rows"] = df.shape[0]
    profile["columns"] = df.shape[1]
    profile["duplicate_rows"] = df.duplicated().sum()
    profile["total_nulls"] = df.isnull().sum().sum()

    column_profile = []

    for col in df.columns:
        column_profile.append({
            "column": col,
            "data_type": str(df[col].dtype),
            "null_count": int(df[col].isnull().sum()),
            "unique_count": int(df[col].nunique()),
            "null_percentage": round(
                (df[col].isnull().sum() / len(df)) * 100, 2
            )
        })

    return profile, pd.DataFrame(column_profile)