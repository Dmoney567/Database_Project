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

        tables = {  
            "User": """
                CREATE TABLE IF NOT EXISTS USERS (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL
                )
            """,
            
            "Production_Stage": """
                CREATE TABLE IF NOT EXISTS PRODUCTION_STAGE (
                    stage_id INT AUTO_INCREMENT PRIMARY KEY,
                    stage_name VARCHAR(100) NOT NULL,
                    stage_capacity INT NOT NULL,
                    production_time INT NOT NULL
                )
            """,

            "Vendor": """
                CREATE TABLE IF NOT EXISTS VENDOR (
                    vend_id INT AUTO_INCREMENT PRIMARY KEY,
                    vend_name VARCHAR(100) NOT NULL,
                    vend_address VARCHAR(255),
                    vend_phone VARCHAR(20),
                    vend_email VARCHAR(100)
                )
            """,

            "Raw_Material": """
                CREATE TABLE IF NOT EXISTS RAW_MATERIAL (
                    raw_mat_id INT AUTO_INCREMENT PRIMARY KEY,
                    raw_mat_name VARCHAR(100) NOT NULL,
                    raw_mat_quantity INT NOT NULL
                )
            """,

            "Production_Order": """
                CREATE TABLE IF NOT EXISTS PRODUCTION_ORDER (
                    order_id INT AUTO_INCREMENT PRIMARY KEY,
                    order_placed_date DATE,
                    order_due_date DATE,
                    order_status VARCHAR(20) NOT NULL,
                    order_production_flag BOOLEAN,
                    vend_id INT,
                    FOREIGN KEY (vend_id) REFERENCES VENDOR(vend_id)
                )
            """,

            "Production_Order_Part": """
                CREATE TABLE IF NOT EXISTS PRODUCTION_ORDER_PART (
                    order_id INT,
                    part_id INT,
                    quantity INT NOT NULL,
                    unit_price DECIMAL(10,2),
                    PRIMARY KEY (order_id, part_id),
                    FOREIGN KEY (order_id) REFERENCES PRODUCTION_ORDER(order_id)
                )
            """,

            "Bill_Of_Materials": """
                CREATE TABLE IF NOT EXISTS BILL_OF_MATERIALS (
                    raw_mat_id INT,
                    part_id INT,
                    quantity INT NOT NULL,
                    PRIMARY KEY (raw_mat_id, part_id),
                    FOREIGN KEY (raw_mat_id) REFERENCES RAW_MATERIAL(raw_mat_id)
                )
            """,

            "Production_Report": """
                CREATE TABLE IF NOT EXISTS PRODUCTION_REPORT (
                    report_id INT AUTO_INCREMENT PRIMARY KEY,
                    report_date DATE NOT NULL,
                    part_id INT NOT NULL,
                    num_parts_finished INT NOT NULL,
                    production_status BOOLEAN NOT NULL,
                    estimated_completion_date DATE,
                    stage_id INT,
                    FOREIGN KEY (stage_id) REFERENCES PRODUCTION_STAGE(stage_id)
                )
            """}
    

        for name,ddl in tables.items():
            cursor.execute(ddl)
            print(f"Table '{name}' verified/created.")

    #seed data
    #cursor.execute("INSERT IGNORE INTO Tiers VALUES (1,'Standerd',5.00),
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