import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()


def init_db():
    """connnects to mysql server, create database, defines table schema and insert seed data."""

    try:
        conn = mysql.connector.connect(
            host = os.getenv("DB_HOST"),
            user = os.getenv("DB_USER"),
            password = os.getenv("DB_PASS")
        )
        cursor = conn.cursor()

        #schema definition
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {os.getenv('DB_NAME')}")
        cursor.execute(f"Use {os.getenv('DB_NAME')}")


        tables = {"Production_Stage":
                """CREATE TABLE IF NOT EXISTS PRODUCTION_STAGE (
                    stage_id INT PRIMARY KEY,
                    stage_name VARCHAR(100) NOT NULL,
                    stage_capacity INT NOT NULL,
                    production_time INT NOT NULL)
                """,
                "Vendor":
                """CREATE TABLE IF NOT EXISTS VENDOR (
                    vendor_id INT PRIMARY KEY,
                    vend_name VARCHAR(100) NOT NULL,
                    vend_address VARCHAR(255),
                    vend_phone VARCHAR(20),
                    vend_email VARCHAR(100)
                )
                """,
                "Raw_Material":
                """CREATE TABLE IF NOT EXISTS RAW_MATERIAL (
                    raw_mat_id INT PRIMARY KEY,
                    raw_mat_name VARCHAR(100) NOT NULL,
                    raw_mat_quantity INT NOT NULL
                );"""


                );}
    
    

        for name,ddl in tables.items():
            cursor.execute(ddl)
            print(f"Table '{name}' verified/created.")

    #seed data
    #cursor.execute("INSERT IGNORE INTO Ters VALUES (1,'Standerd',5.00),
    # (2)") etc etc

        conn.commit()
        print("--database setup complete --")

    except mysql.connector.Error as e:
        print(f"Database error during setup: {e}")

    except Exception as e:
        print(f"CRITICAL ERROR during DB setup: {e}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


##initialization check
if __name__ == "__main__":
    init_db()