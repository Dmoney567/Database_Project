import os
from mysql.connector import pooling
from dotenv import load_dotenv

load_dotenv()

db_pool = pooling.MySQLConnectionPool(
    pool_name="supply_pool",
    pool_size=10,
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    database=os.getenv("DB_NAME")
)


def get_db_conn():
    """retrieves a connection from the pre-warmed connection pool"""
    return db_pool.get_connection()