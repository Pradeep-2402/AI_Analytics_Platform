import json
import os

PROJECT_DIR = "/home/pradeep/AI_Analytics_Platform"

def generate_quality_report(
    profile,
    quality_score,
    valid_count,
    invalid_count
):

    report = {
        "total_rows": profile["rows"],
        "total_columns": profile["columns"],
        "duplicate_rows": int(profile["duplicate_rows"]),
        "total_nulls": int(profile["total_nulls"]),
        "valid_records": int(valid_count),
        "invalid_records": int(invalid_count),
        "quality_score": quality_score
    }

    output_dir = os.path.join(
        PROJECT_DIR,
        "outputs"
    )

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    output_path = os.path.join(
        output_dir,
        "quality_report.json"
    )

    with open(output_path, "w") as file:
        json.dump(
            report,
            file,
            indent=4
        )

    return output_path, report