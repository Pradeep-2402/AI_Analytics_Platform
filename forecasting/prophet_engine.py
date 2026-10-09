import pandas as pd
from prophet import Prophet


def detect_date_column(df):

    for col in df.columns:

        try:
            pd.to_datetime(df[col])

            return col

        except:
            continue

    return None


def detect_numeric_column(df):

    numeric_columns = df.select_dtypes(
        include=["int64", "float64"]
    ).columns.tolist()

    if len(numeric_columns) > 0:
        return numeric_columns[0]

    return None


def generate_forecast(
    df,
    date_column,
    value_column,
    periods=30
):

    forecast_df = df[[date_column, value_column]].copy()

    forecast_df.columns = ["ds", "y"]

    forecast_df["ds"] = pd.to_datetime(
        forecast_df["ds"]
    )

    model = Prophet()

    model.fit(forecast_df)

    future = model.make_future_dataframe(
        periods=periods
    )

    forecast = model.predict(future)

    return forecast[
        [
            "ds",
            "yhat",
            "yhat_lower",
            "yhat_upper"
        ]
    ]