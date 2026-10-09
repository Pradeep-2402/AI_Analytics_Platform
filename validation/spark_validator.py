from pyspark.sql import SparkSession
from pyspark.sql.functions import col,isnan

spark = SparkSession.builder \
    .appName("DataValidation") \
    .getOrCreate()


def validate_dataset(file_path):

    df = spark.read.csv(
        file_path,
        header=True,
        inferSchema=True
    )

    total_rows = df.count()

    duplicate_rows = (
        total_rows -
        df.dropDuplicates().count()
    )

    null_count = 0

    for column in df.columns:
        null_count += df.filter(
            col(column).isNull()
        ).count()

    valid_df = df.dropDuplicates()

    invalid_df = spark.createDataFrame(
        [],
        df.schema
    )

    return {
        "total_rows": total_rows,
        "duplicate_rows": duplicate_rows,
        "null_count": null_count,
        "valid_df": valid_df,
        "invalid_df": invalid_df
    }