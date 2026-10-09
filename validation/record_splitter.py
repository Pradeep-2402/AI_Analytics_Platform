import pandas as pd

def split_valid_invalid_records(df):
    invalid_records = []

    duplicate_mask = df.duplicated(keep=False)
    null_mask = df.isnull().any(axis=1)

    for index, row in df[duplicate_mask].iterrows():
        record = row.to_dict()
        record["error_reason"] = "Duplicate Record"
        invalid_records.append(record)

    for index, row in df[null_mask].iterrows():
        record = row.to_dict()
        record["error_reason"] = "Missing Value"
        invalid_records.append(record)

    invalid_df = pd.DataFrame(invalid_records)

    invalid_indexes = set(df[duplicate_mask].index).union(
        set(df[null_mask].index)
    )

    valid_df = df.drop(index=invalid_indexes)

    return valid_df, invalid_df