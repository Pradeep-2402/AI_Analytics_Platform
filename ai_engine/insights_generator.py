from ai_engine.ollama_client import ask_ollama

def generate_ai_insights(summary):

    prompt = f"""
You are a Senior Data Analytics Consultant.

Dataset Summary:

{summary}

IMPORTANT:

You will be penalized if you focus mainly on null values and duplicates.

Spend:
- 80% of the response on revenue, products, cities, trends and opportunities.
- 20% on data quality.

Start with Executive Summary.

Provide:

1. Executive Summary
2. Data Quality Insights
3. Business Insights
4. Key Trends
5. Risks
6. Recommendations
7. Next Actions

Rules:

- Explain each section in 2-3 detailed points.
- Explain the business impact.
- Mention data quality concerns if present.
- Mention opportunities if present.
- Use professional business language.
- Keep answer between 250 and 400 words.

Answer:
"""
    return ask_ollama(prompt)