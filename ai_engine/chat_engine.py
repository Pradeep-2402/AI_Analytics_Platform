from ai_engine.ollama_client import ask_ollama
from ai_engine.sql_generator import generate_sql
from database.connection import get_engine

import pandas as pd


def chat_with_data(df, question):

    question_lower = question.lower()

    business_keywords = [
        "recommend",
        "recommendation",
        "recommendations",
        "insight",
        "insights",
        "trend",
        "trends",
        "analysis",
        "analyze",
        "improve",
        "improvement",
        "summary",
        "suggest",
        "suggestion",
        "risk",
        "risks",
        "issue",
        "issues",
        "quality",
        "opportunity",
        "opportunities"
    ]

    # =====================================================
    # BUSINESS INSIGHTS MODE
    # =====================================================

    if any(keyword in question_lower for keyword in business_keywords):

        rows = len(df)
        cols = len(df.columns)

        nulls = int(df.isnull().sum().sum())
        duplicates = int(df.duplicated().sum())

        summary = f"""
Dataset Summary

Rows: {rows}
Columns: {cols}

Null Values: {nulls}
Duplicate Records: {duplicates}
"""

        # Revenue KPI

        revenue_cols = [
            "Total_Sales",
            "Sales",
            "Revenue",
            "Amount"
        ]

        for col in revenue_cols:

            if col in df.columns:

                total_revenue = df[col].sum()

                summary += f"""

Total Revenue:
{total_revenue:,.2f}
"""

                break

        # Top Product

        if "Product" in df.columns:

            top_product = (
                df["Product"]
                .value_counts()
                .idxmax()
            )

            summary += f"""

Top Product:
{top_product}
"""

        # Top City

        if "City" in df.columns:

            top_city = (
                df["City"]
                .value_counts()
                .idxmax()
            )

            summary += f"""

Top City:
{top_city}
"""

        prompt = f"""
You are a Senior Business Analyst.

Question:
{question}

SQL Result:

{result.head(10).to_string()}

Based on the query result provide:

1. Executive Summary
2. Key Findings
3. Business Impact
4. Trends & Patterns
5. Risks or Opportunities
6. Recommendations
7. Action Items

Rules:

- For each section provide 2-3 detailed points.
- Do not simply repeat table values.
- Explain WHY the result matters.
- Focus on business decision making.
- Use professional business language.
- Keep answer between 200 and 350 words.

Answer:
"""

        answer = ask_ollama(prompt)

        return answer, None, None

    # =====================================================
    # SQL ANALYTICS MODE
    # =====================================================

    sql = generate_sql(
        question,
        list(df.columns)
    )

    result = pd.read_sql(
        sql,
        get_engine()
    )

    prompt = f"""
Question:
{question}

SQL Result:
{result.head(10).to_string()}

Explain the result in simple business language.
Keep answer under 100 words.
"""

    answer = ask_ollama(prompt)

    return answer, sql, result