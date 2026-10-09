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
from ai_engine.insight_metrics import generate_dataset_summary
from ai_engine.anomaly_detector import detect_anomalies
from ai_engine.anomaly_ai import explain_anomalies
from reports.pdf_report import generate_pdf_report
from ai_engine.root_cause_analyzer import generate_root_cause_analysis
from ai_engine.sql_generator import generate_sql
from ai_engine.sql_executor import execute_sql
from frontend.styles.theme import load_css

st.set_page_config(
    page_title="AI Analytics Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(f"<style>{load_css()}</style>", unsafe_allow_html=True)

st.markdown("""
<style>

/* ══════════════════════════════════════════════════════════
   METRIC LABELS & VALUES  —  yellow
   ══════════════════════════════════════════════════════════ */
[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] p { color: #FFD700 !important; font-weight: bold !important; }
[data-testid="stMetricValue"]   { color: #FFD700 !important; font-weight: bold !important; }

/* ══════════════════════════════════════════════════════════
   UPLOAD BUTTON  —  animated gradient + pulse glow
   ══════════════════════════════════════════════════════════ */
@keyframes uploadGradient {
    0%   { background-position: 0%   50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0%   50%; }
}
@keyframes uploadPulse {
    0%,100% { box-shadow: 0 0 0   4px rgba(0,212,255,0.00), 0 0 0   8px rgba(124,58,237,0.00); }
    50%     { box-shadow: 0 0 14px 6px rgba(0,212,255,0.60), 0 0 28px 12px rgba(124,58,237,0.35); }
}
@keyframes uploadBorderSpin {
    0%   { border-color: #00d4ff; }
    25%  { border-color: #7c3aed; }
    50%  { border-color: #10b981; }
    75%  { border-color: #f59e0b; }
    100% { border-color: #00d4ff; }
}

/* Browse-files button */
[data-testid="stFileUploader"] button,
[data-testid="stFileUploaderDropzone"] button {
    background: linear-gradient(135deg, #00d4ff 0%, #7c3aed 35%, #10b981 65%, #00d4ff 100%) !important;
    background-size: 300% 300% !important;
    animation: uploadGradient 3s ease infinite,
               uploadPulse    2.5s ease-in-out infinite !important;
    color:           #ffffff !important;
    font-weight:     800 !important;
    font-size:       0.9rem !important;
    letter-spacing:  0.09em !important;
    text-transform:  uppercase !important;
    border:          none !important;
    border-radius:   10px !important;
    padding:         11px 30px !important;
    cursor:          pointer !important;
    transition:      transform 0.2s ease, filter 0.2s ease !important;
}
[data-testid="stFileUploader"] button:hover,
[data-testid="stFileUploaderDropzone"] button:hover {
    transform: translateY(-3px) scale(1.05) !important;
    filter:    brightness(1.18) !important;
}
[data-testid="stFileUploader"] button:active,
[data-testid="stFileUploaderDropzone"] button:active {
    transform: translateY(0) scale(1.0) !important;
}


</style>
""", unsafe_allow_html=True)

# ─── ANIMATED HEADER ──────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <div class="main-title">⚡ AI Analytics Platform</div>
    <div class="main-subtitle">Data Quality · Validation · Forecasting · AI Insights</div>
    <span class="header-line"></span>
</div>
""", unsafe_allow_html=True)

# ─── TOP NAV BUTTONS ──────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "🏠 Upload"

pages = [
    "🏠 Upload",
    "🔍 Validation",
    "🧹 Cleaning",
    "📊 Analytics",
    "📈 Forecast",
    "🚨 Anomaly Detection",
    "🧠 AI Insights",
    "📄 PDF Report",
    "🗄️ SQL",
]

row1 = st.columns(4)
for i, p in enumerate(pages[:4]):
    with row1[i]:
        active = st.session_state.page == p
        if st.button(p, key=f"nav_{i}", use_container_width=True,
                     type="primary" if active else "secondary"):
            st.session_state.page = p
            st.rerun()

row2 = st.columns(len(pages[4:]))
for i, p in enumerate(pages[4:]):
    with row2[i]:
        active = st.session_state.page == p
        if st.button(p, key=f"nav_{i+4}", use_container_width=True,
                     type="primary" if active else "secondary"):
            st.session_state.page = p
            st.rerun()

page = st.session_state.page
st.markdown("---")

# ─── SESSION STATE ─────────────────────────────────────────────────────────────
if "df"                  not in st.session_state: st.session_state.df                  = None
if "profile"             not in st.session_state: st.session_state.profile             = None
if "column_profile"      not in st.session_state: st.session_state.column_profile      = None
if "quality_score"       not in st.session_state: st.session_state.quality_score       = 0
if "valid_df"            not in st.session_state: st.session_state.valid_df            = None
if "invalid_df"          not in st.session_state: st.session_state.invalid_df          = None
if "quality_report"      not in st.session_state: st.session_state.quality_report      = None
if "quality_report_path" not in st.session_state: st.session_state.quality_report_path = None
if "upload_path"         not in st.session_state: st.session_state.upload_path         = None
if "root_cause_analysis" not in st.session_state: st.session_state.root_cause_analysis = None
if "insights"            not in st.session_state: st.session_state.insights            = None
if "forecast_df"         not in st.session_state: st.session_state.forecast_df         = None
if "forecast_metric"     not in st.session_state: st.session_state.forecast_metric     = None
if "anomalies"           not in st.session_state: st.session_state.anomalies           = None
if "health_score"        not in st.session_state: st.session_state.health_score        = None

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — UPLOAD & PROFILE
# ═══════════════════════════════════════════════════════════════════════════════
if "Upload" in page:

    st.markdown('<div class="page-badge">Phase 1</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Upload & Data Profiling</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Upload a CSV or Excel file to begin analysis.</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload CSV or Excel File", type=["csv", "xlsx"])

    if uploaded_file:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        upload_path = f"uploads/{uploaded_file.name}"
        with open(upload_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.session_state.df          = df
        st.session_state.upload_path = upload_path

        profile, column_profile = profile_dataset(df)
        st.session_state.profile        = profile
        st.session_state.column_profile = column_profile

        st.markdown('<div class="section-title">Dataset Preview</div>', unsafe_allow_html=True)
        st.dataframe(df.head(), use_container_width=True)

        st.markdown('<div class="section-title">Profile Overview</div>', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Rows",      profile["rows"])
        col2.metric("Total Columns",   profile["columns"])
        col3.metric("Duplicate Rows",  profile["duplicate_rows"])
        col4.metric("Total Nulls",     profile["total_nulls"])

        st.markdown('<div class="section-title">Column Profile</div>', unsafe_allow_html=True)
        st.dataframe(column_profile, use_container_width=True)

        st.markdown('<div class="section-title">Null Values by Column</div>', unsafe_allow_html=True)
        fig = px.bar(
            column_profile, x="column", y="null_count",
            title="Null Values By Column",
            template="plotly_dark",
            color_discrete_sequence=["#00d4ff"]
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15,22,41,0.8)",
            font_family="Exo 2",
            title_font_color="#00d4ff",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.success("✅ Dataset uploaded and profiled successfully! Navigate to the next page.")

    else:
        st.markdown("""
        <div class="upload-zone">
            <div class="upload-icon">📂</div>
            <div class="upload-title">Drop your dataset here</div>
            <div class="upload-hint">Supports CSV and Excel (.xlsx) files</div>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — VALIDATION ENGINE
# ═══════════════════════════════════════════════════════════════════════════════
elif "Validation" in page:

    st.markdown('<div class="page-badge">Phase 2 & 3</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Validation Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">PySpark-powered validation with quality scoring and record splitting.</div>', unsafe_allow_html=True)

    df          = st.session_state.df
    upload_path = st.session_state.upload_path

    if df is None:
        st.warning("⚠️ Please upload a dataset on the Upload & Profile page first.")
    else:
        st.markdown('<div class="section-title">PySpark Validation</div>', unsafe_allow_html=True)
        try:
            validation_result = validate_dataset(upload_path)
            quality_score = calculate_quality_score(
                validation_result["total_rows"],
                validation_result["null_count"],
                validation_result["duplicate_rows"]
            )
            st.session_state.quality_score = quality_score

            s1, s2, s3, s4 = st.columns(4)
            s1.metric("Spark Rows",      validation_result["total_rows"])
            s2.metric("Duplicate Rows",  validation_result["duplicate_rows"])
            s3.metric("Null Values",     validation_result["null_count"])
            s4.metric("Quality Score",   f"{quality_score}%")
            st.success("✅ Spark Validation Completed")

        except Exception as e:
            st.error(f"Spark Validation Error: {e}")
            quality_score = 0
            st.session_state.quality_score = 0

        st.markdown("---")
        st.markdown('<div class="section-title">Record Splitter</div>', unsafe_allow_html=True)

        valid_df, invalid_df = split_valid_invalid_records(df)
        st.session_state.valid_df   = valid_df
        st.session_state.invalid_df = invalid_df

        q1, q2, q3 = st.columns(3)
        q1.metric("Valid Records",      len(valid_df))
        q2.metric("Invalid Records",    len(invalid_df))
        q3.metric("Final Quality Score", f"{st.session_state.quality_score}%")

        st.markdown('<div class="section-title">Valid Records Preview</div>', unsafe_allow_html=True)
        st.dataframe(valid_df.head(), use_container_width=True)

        st.markdown('<div class="section-title">Invalid Records Preview</div>', unsafe_allow_html=True)
        if len(invalid_df) > 0:
            st.dataframe(invalid_df.head(), use_container_width=True)
        else:
            st.success("✅ No invalid records found")

        valid_path   = "outputs/valid_records.csv"
        invalid_path = "outputs/invalid_records.csv"
        valid_df.to_csv(valid_path,   index=False)
        invalid_df.to_csv(invalid_path, index=False)

        quality_report_path, quality_report = generate_quality_report(
            st.session_state.profile,
            st.session_state.quality_score,
            len(valid_df),
            len(invalid_df)
        )
        st.session_state.quality_report      = quality_report
        st.session_state.quality_report_path = quality_report_path

        st.markdown("---")
        st.markdown('<div class="section-title">🧠 AI Root Cause Analysis</div>', unsafe_allow_html=True)

        if st.button("Generate Root Cause Analysis"):
            with st.spinner("Analysing root causes..."):
                st.session_state.root_cause_analysis = generate_root_cause_analysis(
                    st.session_state.profile, quality_report
                )

        if st.session_state.root_cause_analysis:
            st.markdown(st.session_state.root_cause_analysis)
            st.markdown('<div class="section-title">Quality Report</div>', unsafe_allow_html=True)
            st.json(quality_report)

            d1, d2, d3 = st.columns(3)
            with open(valid_path, "rb") as file:
                d1.download_button("⬇ Valid Records",   file, file_name="valid_records.csv")
            with open(invalid_path, "rb") as file:
                d2.download_button("⬇ Invalid Records", file, file_name="invalid_records.csv")
            with open(quality_report_path, "rb") as file:
                d3.download_button("⬇ Quality Report",  file, file_name="quality_report.json")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — DATA CLEANING
# ═══════════════════════════════════════════════════════════════════════════════
elif "Cleaning" in page:

    st.markdown('<div class="page-badge">Phase 4</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Data Cleaning</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Clean nulls, fix types, remove duplicates, and load to MySQL.</div>', unsafe_allow_html=True)

    df = st.session_state.df
    if df is None:
        st.warning("⚠️ Please upload a dataset on the Upload & Profile page first.")
    else:
        if st.button("🧹 Clean Dataset"):
            cleaned_df, error_df, cleaning_summary = clean_dataset(df)
            st.success("✅ Dataset cleaned successfully")
            st.json(cleaning_summary)

            st.markdown('<div class="section-title">Cleaned Dataset Preview</div>', unsafe_allow_html=True)
            st.dataframe(cleaned_df.head(), use_container_width=True)

            cleaned_path = "outputs/cleaned_dataset.csv"
            cleaned_df.to_csv(cleaned_path, index=False)
            with open(cleaned_path, "rb") as file:
                st.download_button("⬇ Download Cleaned Dataset", file, file_name="cleaned_dataset.csv")

            try:
                engine = get_engine()
                load_to_mysql(cleaned_df, "cleaned_dataset", engine)
                st.success("✅ Cleaned data loaded into MySQL table")
            except Exception as e:
                st.error(f"MySQL Error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — ANALYTICS DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════
elif "Analytics" in page:

    st.markdown('<div class="page-badge">Phase 4</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Advanced Analytics Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Interactive charts, top-N analysis, and correlation heatmaps.</div>', unsafe_allow_html=True)

    df = st.session_state.df
    if df is None:
        st.warning("⚠️ Please upload a dataset on the Upload & Profile page first.")
    else:
        kpis = generate_kpis(df)
        a1, a2, a3, a4 = st.columns(4)
        a1.metric("Rows",               kpis["total_rows"])
        a2.metric("Columns",            kpis["total_columns"])
        a3.metric("Numeric Columns",    kpis["numeric_columns"])
        a4.metric("Categorical Columns",kpis["categorical_columns"])

        numeric_columns     = get_numeric_columns(df)
        categorical_columns = get_categorical_columns(df)

        st.markdown("---")
        st.markdown('<div class="section-title">Chart Builder</div>', unsafe_allow_html=True)

        cc1, cc2, cc3 = st.columns(3)
        with cc1:
            chart_type = st.selectbox("Chart Type",
                ["Bar Chart","Line Chart","Pie Chart","Scatter Plot","Histogram","Box Plot"])
        with cc2:
            x_axis = st.selectbox("X Axis", df.columns)
        with cc3:
            y_axis = st.selectbox("Y Axis", df.columns)

        if st.button("Generate Chart"):
            try:
                fig = create_chart(df, chart_type, x_axis, y_axis)
                if fig:
                    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                                      plot_bgcolor="rgba(15,22,41,0.8)",
                                      font_family="Exo 2")
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Chart Error: {e}")

        st.markdown("---")
        st.markdown('<div class="section-title">Top 10 Analysis</div>', unsafe_allow_html=True)

        if categorical_columns and numeric_columns:
            t1, t2 = st.columns(2)
            with t1: category_column = st.selectbox("Category Column", categorical_columns)
            with t2: value_column    = st.selectbox("Value Column",    numeric_columns)

            if st.button("Generate Top 10 Chart"):
                fig = create_top_n_chart(df, category_column, value_column, 10)
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                                  plot_bgcolor="rgba(15,22,41,0.8)",
                                  font_family="Exo 2")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Top 10 Analysis needs at least one categorical column and one numeric column.")

        st.markdown("---")
        st.markdown('<div class="section-title">Correlation Heatmap</div>', unsafe_allow_html=True)

        if st.button("Generate Correlation Heatmap"):
            fig = create_correlation_heatmap(df)
            if fig:
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", font_family="Exo 2")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Correlation heatmap requires numeric columns.")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — FORECASTING
# ═══════════════════════════════════════════════════════════════════════════════
elif "Forecast" in page:

    st.markdown('<div class="page-badge">Phase 5</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Forecasting Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Prophet-powered time-series forecasting with auto column detection.</div>', unsafe_allow_html=True)

    df = st.session_state.df
    if df is None:
        st.warning("⚠️ Please upload a dataset on the Upload & Profile page first.")
    else:
        date_columns = []
        for col in df.columns:
            converted = pd.to_datetime(df[col], errors="coerce", dayfirst=True)
            if converted.notna().sum() >= 2:
                date_columns.append(col)

        numeric_columns = df.select_dtypes(include=["int64","float64"]).columns.tolist()

        if len(date_columns) == 0:
            st.warning("No valid date columns found for forecasting.")
        elif len(numeric_columns) == 0:
            st.warning("No numeric columns found for forecasting.")
        else:
            fc1, fc2, fc3 = st.columns(3)
            with fc1: date_column    = st.selectbox("Select Date Column",       date_columns)
            with fc2: numeric_column = st.selectbox("Select Forecast Metric",   numeric_columns)
            with fc3: forecast_days  = st.selectbox("Forecast Period (days)",   [7, 30, 90])

            if st.button("📈 Generate Forecast"):
                try:
                    forecast_df = df[[date_column, numeric_column]].copy()
                    forecast_df[date_column]    = pd.to_datetime(forecast_df[date_column],    errors="coerce", dayfirst=True)
                    forecast_df[numeric_column] = pd.to_numeric(forecast_df[numeric_column],  errors="coerce")
                    forecast_df = forecast_df.dropna()
                    forecast_df = forecast_df.rename(columns={date_column: "ds", numeric_column: "y"})

                    from prophet import Prophet
                    model  = Prophet()
                    model.fit(forecast_df)
                    future   = model.make_future_dataframe(periods=forecast_days)
                    forecast = model.predict(future)

                    # ── Save for PDF ───────────────────────────────────────
                    st.session_state.forecast_df     = forecast[["ds","yhat","yhat_lower","yhat_upper"]]
                    st.session_state.forecast_metric = numeric_column

                    st.markdown('<div class="section-title">Forecast Preview</div>', unsafe_allow_html=True)
                    st.dataframe(forecast[["ds","yhat","yhat_lower","yhat_upper"]].tail(20),
                                 use_container_width=True)

                    fig = px.line(forecast, x="ds", y="yhat",
                                  title=f"{numeric_column} Forecast Trend",
                                  template="plotly_dark",
                                  color_discrete_sequence=["#00d4ff"])
                    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                                      plot_bgcolor="rgba(15,22,41,0.8)",
                                      font_family="Exo 2", title_font_color="#00d4ff")
                    st.plotly_chart(fig, use_container_width=True)

                    forecast_path = "outputs/forecast.csv"
                    forecast.to_csv(forecast_path, index=False)
                    with open(forecast_path, "rb") as file:
                        st.download_button("⬇ Download Forecast CSV", file, file_name="forecast.csv")

                except Exception as e:
                    st.error(f"Forecast Error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 6 — ANOMALY DETECTION
# ═══════════════════════════════════════════════════════════════════════════════
elif "Anomaly" in page:

    st.markdown('<div class="page-badge">Phase 6</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🚨 AI Anomaly Detection</div>', unsafe_allow_html=True)

    df = st.session_state.df
    if df is None:
        st.warning("⚠️ Please upload a dataset on the Upload & Profile page first.")
    else:
        if st.button("Detect Anomalies"):
            anomalies, health_score = detect_anomalies(df)

            # ── Save for PDF ───────────────────────────────────────────────
            st.session_state.anomalies    = anomalies
            st.session_state.health_score = health_score

            if   health_score >= 80: st.success(f"🟢 Dataset Health Score: {int(health_score)}/100")
            elif health_score >= 50: st.warning(f"🟡 Dataset Health Score: {int(health_score)}/100")
            else:                    st.error(  f"🔴 Dataset Health Score: {int(health_score)}/100")

            st.subheader("Detected Issues")
            if len(anomalies) > 0:
                for issue in anomalies:
                    st.warning(issue)
            else:
                st.success("No anomalies found")

            explanation = explain_anomalies(anomalies)
            st.subheader("AI Analysis")
            st.write(explanation)

        elif st.session_state.anomalies is not None:
            health_score = st.session_state.health_score
            anomalies    = st.session_state.anomalies

            if   health_score >= 80: st.success(f"🟢 Dataset Health Score: {int(health_score)}/100")
            elif health_score >= 50: st.warning(f"🟡 Dataset Health Score: {int(health_score)}/100")
            else:                    st.error(  f"🔴 Dataset Health Score: {int(health_score)}/100")

            st.subheader("Detected Issues")
            if len(anomalies) > 0:
                for issue in anomalies:
                    st.warning(issue)
            else:
                st.success("No anomalies found")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 7 — AI INSIGHTS & CHAT
# ═══════════════════════════════════════════════════════════════════════════════
elif "Insights" in page:

    st.markdown('<div class="page-badge">Phase 6 & 7</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">AI Insights & Chat with Data</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Auto-generated insights and natural language Q&A over your dataset.</div>', unsafe_allow_html=True)

    df = st.session_state.df
    if df is None:
        st.warning("⚠️ Please upload a dataset on the Upload & Profile page first.")
    else:
        st.markdown('<div class="section-title">🧠 Generate AI Insights</div>', unsafe_allow_html=True)

        if st.button("Generate AI Insights"):
            with st.spinner("Generating insights..."):
                summary  = generate_dataset_summary(df)
                insights = generate_ai_insights(summary)
                st.session_state.insights = insights

        if st.session_state.insights:
            st.markdown(st.session_state.insights)

        st.markdown("---")
        st.markdown('<div class="section-title">💬 Chat With Data</div>', unsafe_allow_html=True)

        question = st.text_input("Ask anything about your dataset", key="chat_question")

        if st.button("ASK AI"):
            with st.spinner("Analyzing..."):
                try:
                    answer, sql, result = chat_with_data(df, question)

                    if sql is not None:
                        st.markdown('<div class="section-title">Generated SQL</div>', unsafe_allow_html=True)
                        st.code(sql, language="sql")

                    if result is not None:
                        st.markdown('<div class="section-title">Query Result</div>', unsafe_allow_html=True)
                        st.dataframe(result, use_container_width=True)

                    st.markdown('<div class="section-title">AI Explanation</div>', unsafe_allow_html=True)
                    st.write(answer)

                except Exception as e:
                    st.error(f"Chat Error: {e}")

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 8 — PDF REPORT
# ═══════════════════════════════════════════════════════════════════════════════
elif "PDF" in page:

    st.markdown('<div class="page-badge">Phase 8</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">PDF Report Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Export a full analytics PDF including charts, forecast, anomalies and AI insights.</div>', unsafe_allow_html=True)

    profile        = st.session_state.profile
    quality_report = st.session_state.quality_report

    if profile is None:
        st.warning("⚠️ Please complete Upload & Validation steps first.")
    else:
        col_a, col_b = st.columns(2)
        with col_a:
            st.success("✅ Column profile ready") if st.session_state.column_profile is not None \
                else st.info("ℹ️ Column profile not available")
            st.success(f"✅ Forecast ready  ({st.session_state.forecast_metric})") \
                if st.session_state.forecast_df is not None \
                else st.info("ℹ️ Run Forecasting page to include forecast chart")
        with col_b:
            st.success(f"✅ Anomalies ready  (health score: {st.session_state.health_score})") \
                if st.session_state.anomalies is not None \
                else st.info("ℹ️ Run Anomaly Detection page to include anomaly section")
            st.success("✅ AI Insights ready") if st.session_state.insights \
                else st.info("ℹ️ Run AI Insights page to include insights section")

        st.markdown("---")

        if st.button("📄 Generate PDF Report"):
            try:
                ai_text  = st.session_state.get("insights", "AI insights not generated yet.")
                pdf_path = generate_pdf_report(
                    profile,
                    quality_report,
                    ai_text,
                    output_path      = "outputs/analytics_report.pdf",
                    column_profile_df= st.session_state.column_profile,
                    forecast_df      = st.session_state.forecast_df,
                    forecast_metric  = st.session_state.forecast_metric,
                    anomalies        = st.session_state.anomalies,
                    health_score     = st.session_state.health_score,
                )
                st.success("✅ PDF Report Generated Successfully")
                with open(pdf_path, "rb") as file:
                    st.download_button("⬇ Download Analytics PDF Report", file,
                                       file_name="analytics_report.pdf", mime="application/pdf")
            except Exception as e:
                st.error(f"PDF ERROR: {str(e)}")
                import traceback
                st.code(traceback.format_exc())

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 9 — SQL GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════
elif "SQL" in page:

    st.markdown('<div class="page-badge">Phase 9</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🗄️ Natural Language SQL Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-desc">Convert plain English questions into SQL queries and execute them.</div>', unsafe_allow_html=True)

    df = st.session_state.df
    if df is None:
        st.warning("⚠️ Please upload a dataset on the Upload & Profile page first.")
    else:
        sql_question = st.text_input("Ask using natural language (e.g. 'Show top 10 rows by revenue')")
        st.subheader("Dataset Columns")
        st.write(list(df.columns))

        if st.button("⚡ Generate SQL & Execute"):
            with st.spinner("🤖 Generating SQL Query..."):
                sql_query = generate_sql(sql_question, list(df.columns))
            st.success("✅ Query Generated Successfully")

            try:
                st.markdown('<div class="section-title">Generated SQL</div>', unsafe_allow_html=True)
                st.code(sql_query, language="sql")

                result = execute_sql(sql_query)

                st.markdown('<div class="section-title">Query Result</div>', unsafe_allow_html=True)
                st.dataframe(result, use_container_width=True)

                csv = result.to_csv(index=False)
                st.download_button("⬇ Download Result CSV", csv,
                                   file_name="query_result.csv", mime="text/csv")
            except Exception as e:
                import traceback
                st.error(f"SQL Error: {e}")
                st.code(traceback.format_exc())

# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("""
<center>
AI-Powered Data Quality &amp; Analytics Platform<br>
Built using Streamlit · PySpark · MySQL · Ollama · Prophet
</center>
""", unsafe_allow_html=True)