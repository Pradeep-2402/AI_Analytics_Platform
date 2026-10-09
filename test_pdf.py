from reports.pdf_report import generate_pdf_report

profile = {
    "rows": 100,
    "columns": 5,
    "duplicate_rows": 2,
    "total_nulls": 4
}

quality_report = {
    "valid_records": 95,
    "invalid_records": 5,
    "quality_score": 95
}

generate_pdf_report(
    profile,
    quality_report,
    "This is a test insight"
)

print("PDF Created")