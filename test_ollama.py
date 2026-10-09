from ai_engine.sql_generator import generate_sql

columns = [
    "city",
    "revenue",
    "product",
    "sales_amount"
]

sql = generate_sql(
    "Show top 5 cities by revenue",
    columns
)

print(sql)