import pandas as pd
from database.connection import get_engine

def execute_sql(query):

    engine = get_engine()

    result = pd.read_sql(
        query,
        engine
    )

    return result