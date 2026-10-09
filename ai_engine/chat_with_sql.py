from ai_engine.sql_generator import generate_sql
from ai_engine.sql_executor import execute_sql
from ai_engine.ollama_client import ask_ollama

def chat_with_data(question, columns):

    sql = generate_sql(
        question,
        columns
    )

    result = execute_sql(sql)

    prompt = f"""
Question:
{question}

Result:
{result.head(5).to_string()}

Explain in simple business language.
"""

    answer = ask_ollama(prompt)

    return answer, sql, result