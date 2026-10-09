from sqlalchemy import create_engine
from dotenv import load_dotenv
from urllib.parse import quote_plus
import os

load_dotenv()

def get_engine():

    host = os.getenv("DB_HOST")
    user = os.getenv("DB_USER")
    password = quote_plus(os.getenv("DB_PASSWORD"))
    db = os.getenv("DB_NAME")
    port = os.getenv("DB_PORT")

    engine = create_engine(
        f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"
    )

    return engine