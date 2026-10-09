import os
import sys
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.profiler import profile_dataset
from backend.cleaner import clean_dataset
from backend.loader import load_to_mysql
from database.connection import get_engine
from validation.record_splitter import split_valid_invalid_records
from validation.quality_score import calculate_quality_score
from reports.quality_report import generate_quality_report
from reports.pdf_report import generate_pdf_report
from notifications.email_sender import send_email_with_attachment



PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOAD_DIR = os.path.join(PROJECT_DIR, "uploads")
OUTPUT_DIR = os.path.join(PROJECT_DIR, "outputs")


def get_latest_file():
    files = [
        os.path.join(UPLOAD_DIR, f)
        for f in os.listdir(UPLOAD_DIR)
        if f.endswith(".csv") or f.endswith(".xlsx")
    ]

    if not files:
        raise FileNotFoundError("No CSV or Excel file found in uploads folder")

    return max(files, key=os.path.getctime)


def read_dataset():
    file_path = get_latest_file()

    if file_path.endswith(".csv"):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)

    df.to_csv(os.path.join(OUTPUT_DIR, "airflow_input_data.csv"), index=False)

    return file_path


def validate_and_profile():
    input_path = os.path.join(OUTPUT_DIR, "airflow_input_data.csv")
    df = pd.read_csv(input_path)

    profile, column_profile = profile_dataset(df)

    valid_df, invalid_df = split_valid_invalid_records(df)

    total_rows = profile["rows"]
    null_count = profile["total_nulls"]
    duplicate_rows = profile["duplicate_rows"]

    quality_score = calculate_quality_score(
        total_rows,
        null_count,
        duplicate_rows
    )

    valid_df.to_csv(os.path.join(OUTPUT_DIR, "airflow_valid_records.csv"), index=False)
    invalid_df.to_csv(os.path.join(OUTPUT_DIR, "airflow_invalid_records.csv"), index=False)

    quality_report_path, quality_report = generate_quality_report(
        profile,
        quality_score,
        len(valid_df),
        len(invalid_df)
    )

    return quality_report_path


def clean_and_load_mysql():
    input_path = os.path.join(OUTPUT_DIR, "airflow_input_data.csv")
    df = pd.read_csv(input_path)

    cleaned_df, error_df, cleaning_summary = clean_dataset(df)

    cleaned_path = os.path.join(OUTPUT_DIR, "airflow_cleaned_dataset.csv")
    cleaned_df.to_csv(cleaned_path, index=False)

    engine = get_engine()
    load_to_mysql(cleaned_df, "airflow_cleaned_dataset", engine)

    return cleaned_path


def generate_pipeline_pdf():
    input_path = os.path.join(OUTPUT_DIR, "airflow_input_data.csv")
    df = pd.read_csv(input_path)

    profile, column_profile = profile_dataset(df)
    valid_df, invalid_df = split_valid_invalid_records(df)

    quality_score = calculate_quality_score(
        profile["rows"],
        profile["total_nulls"],
        profile["duplicate_rows"]
    )

    quality_report = {
        "valid_records": len(valid_df),
        "invalid_records": len(invalid_df),
        "quality_score": quality_score
    }

    pdf_path = generate_pdf_report(
        profile,
        quality_report,
        "Airflow automated report generated successfully.",
        output_path=os.path.join(OUTPUT_DIR, "airflow_analytics_report.pdf")
    )

    return pdf_path
def send_email_report():

    pdf_path = (
        "/home/pradeep/AI_Analytics_Platform/"
        "outputs/airflow_analytics_report.pdf"
    )

    return send_email_with_attachment(pdf_path)