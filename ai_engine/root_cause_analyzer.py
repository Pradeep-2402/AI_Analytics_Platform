from ai_engine.ollama_client import ask_ollama


def generate_root_cause_analysis(
    profile,
    quality_report
):

    prompt = f"""
You are a Senior Data Quality Analyst.

Analyze the following dataset quality metrics.

Dataset Summary:
Rows: {profile['rows']}
Columns: {profile['columns']}
Duplicate Rows: {profile['duplicate_rows']}
Null Values: {profile['total_nulls']}

Quality Report:
Valid Records: {quality_report['valid_records']}
Invalid Records: {quality_report['invalid_records']}
Quality Score: {quality_report['quality_score']}

Provide:

1. Root Causes
2. Business Impact
3. Recommendations

Keep response professional.
"""

    return ask_ollama(prompt)