
from database.connection import get_engine

engine = get_engine()

with engine.connect() as conn:
    print("Connected Successfully")