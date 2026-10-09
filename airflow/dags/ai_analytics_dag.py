from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import sys
import os

PROJECT_DIR = "/home/pradeep/AI_Analytics_Platform"

sys.path.append(PROJECT_DIR)

from pipeline.airflow_pipeline import (
    read_dataset,
    validate_and_profile,
    clean_and_load_mysql,
    generate_pipeline_pdf,
    send_email_report
)

with DAG(
    dag_id="ai_analytics_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule="0 8 * * *",
    catchup=False,
    tags=["data-engineering", "analytics", "ai"]
) as dag:

    read_dataset_task = PythonOperator(
        task_id="read_latest_dataset",
        python_callable=read_dataset
    )

    validate_task = PythonOperator(
        task_id="validate_and_profile",
        python_callable=validate_and_profile
    )

    clean_load_task = PythonOperator(
    task_id="clean_and_load_mysql",
    python_callable=clean_and_load_mysql
)

pdf_task = PythonOperator(
    task_id="generate_pdf_report",
    python_callable=generate_pipeline_pdf
)

email_task = PythonOperator(
    task_id="send_email_report",
    python_callable=send_email_report
)

read_dataset_task >> validate_task >> clean_load_task >> pdf_task >> email_task