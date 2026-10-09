import sys
import os
import pandas as pd
import streamlit as st
import plotly.express as px

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

from backend.profiler import profile_dataset
from backend.cleaner import clean_dataset
from backend.loader import load_to_mysql
from database.connection import get_engine

from validation.spark_validator import validate_dataset
from validation.quality_score import calculate_quality_score

st.set_page_config(
    page_title="AI Analytics Platform",
    layout="wide"
)
st.markdown("""
<style>

/* Main App Background */
.stApp {
    background: linear-gradient(
        135deg,
        #0f172a 0%,
        #1e3a8a 50%,
        #60a5fa 100%
    );
}

/* Main Title */
h1 {
    color: white !important;
    text-align: center;
    font-size: 3rem !important;
    font-weight: bold !important;
}

/* Section Headers */
h2, h3 {
    color: #dbeafe !important;
}

/* Upload Box */
[data-testid="stFileUploader"] {
    background-color: rgba(255,255,255,0.08);
    border-radius: 15px;
    padding: 15px;
    border: 2px solid #60a5fa;
    backdrop-filter: blur(10px);
}

/* Upload Button */
[data-testid="stFileUploader"] button {
    background-color: #60a5fa !important;
    color: white !important;
    border-radius: 10px !important;
    border: none !important;
    transition: all 0.3s ease !important;
}

/* Upload Button Hover Glow */
[data-testid="stFileUploader"] button:hover {
    background-color: #1e3a8a !important;
    box-shadow: 0 0 20px #60a5fa;
    transform: scale(1.05);
}

/* Normal Buttons */
.stButton > button {
    background-color: #3b82f6;
    color: white;
    border-radius: 10px;
    border: none;
    font-weight: bold;
    transition: all 0.3s ease;
}

/* Hover Effect */
.stButton > button:hover {
    background-color: #1d4ed8;
    box-shadow: 0px 0px 20px #60a5fa;
    transform: scale(1.05);
}

/* Metric Cards */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.08);
    border: 1px solid #60a5fa;
    padding: 15px;
    border-radius: 15px;
    backdrop-filter: blur(10px);
}

/* Dataframe */
[data-testid="stDataFrame"] {
    background-color: white;
    border-radius: 15px;
}

/* Success Messages */
.stSuccess {
    border-radius: 12px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: rgba(15,23,42,0.95);
}

</style>
""", unsafe_allow_html=True)

st.title("AI-Powered Data Quality & Analytics Platform")

uploaded_file = st.file_uploader(
    "Upload CSV or Excel File",
    type=["csv", "xlsx"]
)

if uploaded_file:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    upload_path = f"uploads/{uploaded_file.name}"

    with open(upload_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # --------------------------
    # DATASET PREVIEW
    # --------------------------

    st.subheader("Dataset Preview")
    st.dataframe(df.head())

    # --------------------------
    # PANDAS PROFILING
    # --------------------------

    profile, column_profile = profile_dataset(df)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Rows",
        profile["rows"]
    )

    col2.metric(
        "Total Columns",
        profile["columns"]
    )

    col3.metric(
        "Duplicate Rows",
        profile["duplicate_rows"]
    )

    col4.metric(
        "Total Nulls",
        profile["total_nulls"]
    )

    st.subheader("Column Profile")
    st.dataframe(column_profile)

    # --------------------------
    # NULL VALUE CHART
    # --------------------------

    st.subheader("Data Quality Chart")

    fig = px.bar(
        column_profile,
        x="column",
        y="null_count",
        title="Null Values By Column"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # --------------------------
    # PHASE 2 - SPARK VALIDATION
    # --------------------------

    st.subheader("PySpark Validation Engine")

    try:

        validation_result = validate_dataset(
            upload_path
        )

        quality_score = calculate_quality_score(
            validation_result["total_rows"],
            validation_result["null_count"],
            validation_result["duplicate_rows"]
        )

        s1, s2, s3, s4 = st.columns(4)

        s1.metric(
            "Spark Rows",
            validation_result["total_rows"]
        )

        s2.metric(
            "Duplicate Rows",
            validation_result["duplicate_rows"]
        )

        s3.metric(
            "Null Values",
            validation_result["null_count"]
        )

        s4.metric(
            "Quality Score",
            f"{quality_score}%"
        )

        st.success(
            "Spark Validation Completed"
        )

    except Exception as e:

        st.error(
            f"Spark Validation Error: {e}"
        )

    # --------------------------
    # CLEAN DATASET
    # --------------------------

    st.subheader("Clean Dataset")

    if st.button("Clean Dataset"):

        cleaned_df, error_df, cleaning_summary = clean_dataset(df)

        st.success(
            "Dataset cleaned successfully"
        )

        st.json(cleaning_summary)

        st.subheader(
            "Cleaned Dataset Preview"
        )

        st.dataframe(
            cleaned_df.head()
        )

        cleaned_path = (
            "outputs/cleaned_dataset.csv"
        )

        cleaned_df.to_csv(
            cleaned_path,
            index=False
        )

        with open(
            cleaned_path,
            "rb"
        ) as file:

            st.download_button(
                "Download Cleaned Dataset",
                file,
                file_name="cleaned_dataset.csv"
            )

        try:

            engine = get_engine()

            load_to_mysql(
                cleaned_df,
                "cleaned_dataset",
                engine
            )

            st.success(
                "Cleaned data loaded into MySQL table"
            )

        except Exception as e:

            st.error(
                f"MySQL Error: {e}"
            )

    # --------------------------
    # CHART BUILDER
    # --------------------------

    st.subheader("Chart Builder")

    chart_type = st.selectbox(
        "Select Chart Type",
        [
            "Bar Chart",
            "Line Chart",
            "Pie Chart",
            "Scatter Plot"
        ]
    )

    x_axis = st.selectbox(
        "Select X Axis",
        df.columns
    )

    y_axis = st.selectbox(
        "Select Y Axis",
        df.columns
    )

    if st.button("Generate Chart"):

        try:

            if chart_type == "Bar Chart":

                fig = px.bar(
                    df,
                    x=x_axis,
                    y=y_axis
                )

            elif chart_type == "Line Chart":

                fig = px.line(
                    df,
                    x=x_axis,
                    y=y_axis
                )

            elif chart_type == "Pie Chart":

                fig = px.pie(
                    df,
                    names=x_axis,
                    values=y_axis
                )

            elif chart_type == "Scatter Plot":

                fig = px.scatter(
                    df,
                    x=x_axis,
                    y=y_axis
                )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        except Exception as e:

            st.error(
                f"Chart Error: {e}"
            )