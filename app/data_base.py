import psycopg2
from app.db_config import db_config

def get_db_connection():
    connection = psycopg2.connect(**db_config)
    return connection