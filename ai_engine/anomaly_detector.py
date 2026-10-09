def detect_anomalies(df):

    anomalies = []

    total_rows = len(df)

    total_nulls = df.isnull().sum().sum()

    duplicate_rows = df.duplicated().sum()

    if total_nulls > total_rows * 0.1:

        anomalies.append(
            f"High Null Values Detected ({total_nulls})"
        )

    if duplicate_rows > total_rows * 0.05:

        anomalies.append(
            f"High Duplicate Records Detected ({duplicate_rows})"
        )

    # Column Null Percentage

    for col in df.columns:

        null_pct = (
            df[col].isnull().sum() / len(df)
        ) * 100

        if null_pct > 20:

            anomalies.append(
                f"{col}: {null_pct:.1f}% Missing Values"
            )

    # Constant Columns

    for col in df.columns:

        if df[col].nunique() == 1:

            anomalies.append(
                f"{col}: Contains only one unique value"
            )

    # High Cardinality

    for col in df.select_dtypes(
        include="object"
    ).columns:

        unique_pct = (
            df[col].nunique() / len(df)
        ) * 100

        if unique_pct > 90:

            anomalies.append(
                f"{col}: Extremely high unique values"
            )

    # Numeric Checks

    numeric_cols = df.select_dtypes(
        include="number"
    ).columns

    for col in numeric_cols:

        if df[col].min() < 0:

            anomalies.append(
                f"{col}: Negative values detected"
            )

        mean = df[col].mean()

        std = df[col].std()

        upper = mean + (3 * std)

        lower = mean - (3 * std)

        outliers = df[
            (df[col] > upper)
            |
            (df[col] < lower)
        ]

        if len(outliers) > 0:

            anomalies.append(
                f"{col}: {len(outliers)} Outliers Found"
            )

    health_score = 100

    health_score -= min(
        total_nulls // 10,
        30
    )

    health_score -= min(
        duplicate_rows // 5,
        30
    )

    health_score -= len(anomalies) * 2

    health_score = max(
        0,
        health_score
    )
    health_score = 100

    health_score -= min(total_nulls // 10, 30)

    health_score -= min(duplicate_rows // 5, 30)

    health_score -= len(anomalies) * 2

    health_score = max(0, health_score)

    return anomalies, health_score

   