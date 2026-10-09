def calculate_quality_score(
    total_rows,
    null_count,
    duplicate_rows
):

    if total_rows == 0:
        return 0

    score = 100

    score -= (
        (null_count / total_rows)
        * 50
    )

    score -= (
        (duplicate_rows / total_rows)
        * 50
    )

    return round(
        max(score,0),
        2
    )