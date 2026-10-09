
import sys
import os
import json
import pandas as pd
import streamlit as st
import plotly.express as px

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.profiler import profile_dataset
from backend.cleaner import clean_dataset
from backend.loader import load_to_mysql
from database.connection import get_engine

from validation.spark_validator import validate_dataset
from validation.quality_score import calculate_quality_score
from validation.record_splitter import split_valid_invalid_records
from reports.quality_report import generate_quality_report
from analytics.kpi_engine import generate_kpis, get_numeric_columns, get_categorical_columns
from analytics.chart_engine import create_chart, create_top_n_chart, create_correlation_heatmap
from forecasting.prophet_engine import (
    detect_date_column,
    detect_numeric_column,
    generate_forecast
)
from ai_engine.insights_generator import generate_ai_insights
from ai_engine.chat_engine import chat_with_data

from reports.pdf_report import generate_pdf_report
from ai_engine.root_cause_analyzer import generate_root_cause_analysis
from ai_engine.sql_generator import generate_sql
from ai_engine.sql_executor import execute_sql
from frontend.styles.theme import load_css
st.set_page_config(
    page_title="AI Analytics Platform",
    layout="wide"
)
st.sidebar.title("🚀 AI Analytics Platform")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Data Profile",
        "Validation",
        "Cleaning",
        "Analytics",
        "Forecasting",
        "AI Insights",
        "Root Cause Analysis",
        "SQL Assistant",
        "PDF Reports",
        "Pipeline Status"
    ]
)
st.markdown(
    f"""
    <style>
    {load_css()}
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown("""
<h1 style='text-align:center;color:#00D4FF'>
🚀 AI Analytics Platform
</h1>

<h4 style='text-align:center;color:gray'>
AI-Powered Data Quality, Analytics & Forecasting
</h4>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload CSV or Excel File",
    type=["csv", "xlsx"]
)

if uploaded_file:
        if page == "Dashboard":

        st.header("📊 Dashboard")

    elif page == "Data Profile":

        st.header("📋 Data Profile")

    elif page == "Validation":

        st.header("⚡ Validation Engine")

    elif page == "Cleaning":

        st.header("🧹 Data Cleaning")

    elif page == "Analytics":

        st.header("📈 Analytics")

    elif page == "Forecasting":

        st.header("🔮 Forecasting")

    elif page == "AI Insights":

        st.header("🤖 AI Insights")

    elif page == "Root Cause Analysis":

        st.header("🧠 Root Cause Analysis")

    elif page == "SQL Assistant":

        st.header("🗄 Natural Language SQL")

    elif page == "PDF Reports":

        st.header("📄 PDF Reports")

    elif page == "Pipeline Status":

        st.header("⚙ Pipeline Status")

        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        upload_path = f"uploads/{uploaded_file.name}"

    with open(upload_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.subheader("Dataset Preview")
    st.dataframe(df.head())

    profile, column_profile = profile_dataset(df)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Rows", profile["rows"])
    col2.metric("Total Columns", profile["columns"])
    col3.metric("Duplicate Rows", profile["duplicate_rows"])
    col4.metric("Total Nulls", profile["total_nulls"])

    st.subheader("Column Profile")
    st.dataframe(column_profile)

    st.subheader("Data Quality Chart")

    fig = px.bar(
        column_profile,
        x="column",
        y="null_count",
        title="Null Values By Column"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("PySpark Validation Engine")

    try:
        validation_result = validate_dataset(upload_path)

        quality_score = calculate_quality_score(
            validation_result["total_rows"],
            validation_result["null_count"],
            validation_result["duplicate_rows"]
        )

        s1, s2, s3, s4 = st.columns(4)

        s1.metric("Spark Rows", validation_result["total_rows"])
        s2.metric("Duplicate Rows", validation_result["duplicate_rows"])
        s3.metric("Null Values", validation_result["null_count"])
        s4.metric("Quality Score", f"{quality_score}%")

        st.success("Spark Validation Completed")

    except Exception as e:
        st.error(f"Spark Validation Error: {e}")
        quality_score = 0

    st.subheader("Phase 3 - Data Quality Engine")

    valid_df, invalid_df = split_valid_invalid_records(df)

    q1, q2, q3 = st.columns(3)

    q1.metric("Valid Records", len(valid_df))
    q2.metric("Invalid Records", len(invalid_df))
    q3.metric("Final Quality Score", f"{quality_score}%")

    st.subheader("Valid Records Preview")
    st.dataframe(valid_df.head())

    st.subheader("Invalid Records Preview")
    if len(invalid_df) > 0:
        st.dataframe(invalid_df.head())
    else:
        st.success("No invalid records found")

    valid_path = "outputs/valid_records.csv"
    invalid_path = "outputs/invalid_records.csv"

    valid_df.to_csv(valid_path, index=False)
    invalid_df.to_csv(invalid_path, index=False)

    quality_report_path, quality_report = generate_quality_report(
    profile,
    quality_score,
    len(valid_df),
    len(invalid_df)
)

if "root_cause_analysis" not in st.session_state:
    st.session_state.root_cause_analysis = None

st.subheader("🧠 AI Root Cause Analysis")

if st.button("Generate Root Cause Analysis"):

    st.session_state.root_cause_analysis = (
        generate_root_cause_analysis(
            profile,
            quality_report
        )
    )

if st.session_state.root_cause_analysis:

    st.markdown(
        st.session_state.root_cause_analysis
    )

    st.subheader("Quality Report")
    st.json(quality_report)

    d1, d2, d3 = st.columns(3)

    with open(valid_path, "rb") as file:
        d1.download_button(
            "Download Valid Records",
            file,
            file_name="valid_records.csv"
        )

    with open(invalid_path, "rb") as file:
        d2.download_button(
            "Download Invalid Records",
            file,
            file_name="invalid_records.csv"
        )

    with open(quality_report_path, "rb") as file:
        d3.download_button(
            "Download Quality Report",
            file,
            file_name="quality_report.json"
        )

    st.subheader("Clean Dataset")

    if st.button("Clean Dataset"):

        cleaned_df, error_df, cleaning_summary = clean_dataset(df)

        st.success("Dataset cleaned successfully")

        st.json(cleaning_summary)

        st.subheader("Cleaned Dataset Preview")
        st.dataframe(cleaned_df.head())

        cleaned_path = "outputs/cleaned_dataset.csv"
        cleaned_df.to_csv(cleaned_path, index=False)

        with open(cleaned_path, "rb") as file:
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

            st.success("Cleaned data loaded into MySQL table")

        except Exception as e:
            st.error(f"MySQL Error: {e}")

        st.markdown(
    """
    <div class='section-header'>
        📊 Advanced Analytics Dashboard
    </div>
    """,
    unsafe_allow_html=True)
        st.markdown(
    f"""
    <div class='kpi-card'>
        <div class='kpi-title'>
            Total Rows
        </div>
        <div class='kpi-value'>
            {profile['rows']}
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
        
        

    kpis = generate_kpis(df)

    a1, a2, a3, a4 = st.columns(4)

    a1.metric("Rows", kpis["total_rows"])
    a2.metric("Columns", kpis["total_columns"])
    a3.metric("Numeric Columns", kpis["numeric_columns"])
    a4.metric("Categorical Columns", kpis["categorical_columns"])

    numeric_columns = get_numeric_columns(df)
    categorical_columns = get_categorical_columns(df)

    st.subheader("Advanced Chart Builder")

    chart_type = st.selectbox(
        "Select Chart Type",
        [
            "Bar Chart",
            "Line Chart",
            "Pie Chart",
            "Scatter Plot",
            "Histogram",
            "Box Plot"
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

    if st.button("Generate Advanced Chart"):

        try:
            fig = create_chart(
                df,
                chart_type,
                x_axis,
                y_axis
            )

            if fig:
                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

        except Exception as e:
            st.error(f"Chart Error: {e}")

    st.subheader("Top 10 Analysis")

    if categorical_columns and numeric_columns:

        category_column = st.selectbox(
            "Select Category Column",
            categorical_columns
        )

        value_column = st.selectbox(
            "Select Value Column",
            numeric_columns
        )

        if st.button("Generate Top 10 Chart"):

            fig = create_top_n_chart(
                df,
                category_column,
                value_column,
                10
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    else:
        st.warning(
            "Top 10 Analysis needs at least one categorical column and one numeric column."
        )

    st.subheader("Correlation Heatmap")

    if st.button("Generate Correlation Heatmap"):

        fig = create_correlation_heatmap(df)

        if fig:
            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:
            st.warning(
                "Correlation heatmap requires numeric columns."
            )

    a1, a2, a3, a4 = st.columns(4)

    a1.metric("Rows", kpis["total_rows"])
    a2.metric("Columns", kpis["total_columns"])
    a3.metric("Numeric Columns", kpis["numeric_columns"])
    a4.metric("Categorical Columns", kpis["categorical_columns"])

    numeric_columns = get_numeric_columns(df)
    categorical_columns = get_categorical_columns(df)
    # -----------------------------------
# PHASE 5 - FORECASTING ENGINE
# -----------------------------------

    st.subheader("Phase 5 - Forecasting Engine")

    date_column = detect_date_column(df)

    numeric_column = detect_numeric_column(df)

    if date_column and numeric_column:

        st.success(
            f"Detected Date Column: {date_column}"
        )

        st.success(
            f"Detected Numeric Column: {numeric_column}"
        )

        forecast_days = st.selectbox(
            "Forecast Period",
            [7, 30, 90]
        )

        if st.button("Generate Forecast"):

            try:

                forecast = generate_forecast(
                    df,
                    date_column,
                    numeric_column,
                    forecast_days
                )

                st.subheader(
                    "Forecast Preview"
                )

                st.dataframe(
                    forecast.tail(20)
                )

                import plotly.express as px

                fig = px.line(
                    forecast,
                    x="ds",
                    y="yhat",
                    title="Forecast Trend"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

                forecast_path = (
                    "outputs/forecast.csv"
                )

                forecast.to_csv(
                    forecast_path,
                    index=False
                )

                with open(
                    forecast_path,
                    "rb"
                ) as file:

                    st.download_button(
                        "Download Forecast CSV",
                        file,
                        file_name="forecast.csv"
                    )

            except Exception as e:

                st.error(
                    f"Forecast Error: {e}"
                )

    else:

        st.warning(
            "No valid date column or numeric column detected."
        )
    st.subheader("Phase 6 - AI Insights")

if st.button("Generate AI Insights"):

    insights = generate_ai_insights(
        profile,
        quality_score,
        "Forecast Generated"
    )
    st.session_state["insights"] = insights

    st.markdown(insights)
    st.subheader("Phase 7 - Chat With Data")

question = st.text_input(
    "Ask anything about your dataset"
)

if st.button("Ask AI"):

    answer = chat_with_data(
        df,
        question
    )

    st.markdown(answer)
    st.subheader("Phase 8 - PDF Report Generator")

if st.button("Generate PDF Report"):

    try:

        ai_text = st.session_state.get(
            "insights",
            "AI insights not generated yet."
        )

        pdf_path = generate_pdf_report(
            profile,
            quality_report,
            ai_text
        )

        st.success("PDF Report Generated Successfully")

        st.write("PDF Path:", pdf_path)

        import os

        st.write(
            "File Exists:",
            os.path.exists(pdf_path)
        )

        with open(pdf_path, "rb") as file:
            st.download_button(
                "Download Analytics PDF Report",
                file,
                file_name="analytics_report.pdf"
            )

    except Exception as e:

        st.error(f"PDF ERROR: {str(e)}")

        import traceback

        st.code(traceback.format_exc())
        st.subheader("🗄️ Natural Language SQL")

sql_question = st.text_input(
    "Ask using natural language"
)

if st.button("Generate SQL & Execute"):

    try:

        sql_query = generate_sql(
            sql_question,
            list(df.columns)
        )

        sql_query = (
            sql_query
            .replace("```sql", "")
            .replace("```", "")
            .strip()
        )

        st.code(
            sql_query,
            language="sql"
        )

        result = execute_sql(
            sql_query
        )

        st.subheader("Query Result")

        st.dataframe(
            result,
            use_container_width=True
        )

        csv = result.to_csv(index=False)

        st.download_button(
            "Download Result CSV",
            csv,
            file_name="query_result.csv",
            mime="text/csv"
        )

    except Exception as e:

        st.error(
            f"SQL Error: {e}"
        )