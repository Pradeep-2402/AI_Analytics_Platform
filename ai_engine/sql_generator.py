from ai_engine.ollama_client import ask_ollama


def generate_sql(question, columns):
    
    print("AVAILABLE COLUMNS:")
    print(columns)

    column_text = "\n".join(columns)

    prompt = f"""
You are an Expert MySQL SQL Generator.

Table Name:
cleaned_dataset

Available Columns:

{column_text}

STRICT RULES:

1. Use ONLY columns listed above.
2. NEVER invent column names.
3. NEVER use Total_Sales unless it exists above.
4. NEVER use Revenue unless it exists above.
5. NEVER use aliases that are not defined.
6. If using:
   SUM(Quantity) AS total_quantity

   Then use:

   ORDER BY total_quantity

7. Return ONLY SQL.
8. No explanation.
9. No markdown.
10. Output must start with SELECT.
11. Use MySQL syntax only.

Examples

Question:
show top 5 products

SQL:
SELECT Product,
SUM(Quantity) AS total_quantity
FROM cleaned_dataset
GROUP BY Product
ORDER BY total_quantity DESC
LIMIT 5;

Question:
show top 5 cities

SQL:
SELECT City,
COUNT(*) AS total_orders
FROM cleaned_dataset
GROUP BY City
ORDER BY total_orders DESC
LIMIT 5;

Question:
{question}

SQL:
"""

    sql = ask_ollama(prompt)

    sql = (
        sql.replace("```sql", "")
           .replace("```", "")
           .strip()
    )

    if "SELECT" in sql.upper():

        sql = sql[
            sql.upper().find("SELECT"):
        ]

    if ";" in sql:

        sql = sql[
            :sql.rfind(";") + 1
        ]

    return sql