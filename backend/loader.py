def load_to_mysql(df, table_name, engine):
    df.to_sql(
        name=table_name,
        con=engine,
        if_exists="replace",
        index=False
    )