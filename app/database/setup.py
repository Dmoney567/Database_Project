import mysql.connector
import os
from dotenv import load_dotenv


from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

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

        #insert seed data
        # insert seed data
        try:
            cursor.execute("INSERT IGNORE INTO USERS (username,password_hash) VALUES (%s, %s)", 
                ("admin", hash_password("admin123")))
            conn.commit()
            print("Users seeded.")
        except Exception as e:
            print("Error seeding USERS:", e)

        try:
            cursor.executemany("""
                INSERT IGNORE INTO PRODUCTION_STAGE (stage_name, stage_capacity, production_time)
                VALUES (%s, %s, %s)
            """, [
                ("Cutting", 100, 30),
                ("Assembly", 80, 45),
                ("Packaging", 120, 20)
            ])
            conn.commit()
            print("Production stages seeded.")
        except Exception as e:
            print("Error seeding PRODUCTION_STAGE:", e)

        try:
            cursor.executemany("""
                INSERT IGNORE INTO VENDOR (vend_name, vend_address, vend_phone, vend_email)
                VALUES (%s, %s, %s, %s)
            """, [
                ("Vendor A", "Detroit, MI", "111-111-1111", "a@vendor.com"),
                ("Vendor B", "Chicago, IL", "222-222-2222", "b@vendor.com"),
                ("Vendor C", "Cleveland, OH", "333-333-3333", "c@vendor.com")
            ])
            conn.commit()
            print("Vendors seeded.")
        except Exception as e:
            print("Error seeding VENDOR:", e)

        try:
            cursor.execute("""
                INSERT IGNORE INTO PRODUCTION_ORDER 
                (order_placed_date, order_due_date, order_status, order_production_flag, vend_id)
                VALUES
                ('2026-04-01', '2026-04-10', 'Pending', 0, 1),
                ('2026-04-03', '2026-04-12', 'In Progress', 1, 2),
                ('2026-04-05', '2026-04-15', 'Completed', 1, 1),
                ('2026-04-06', '2026-04-20', 'Pending', 0, 3),
                ('2026-04-07', '2026-04-18', 'Delayed', 0, 2)
            """)
            conn.commit()
            print("Production orders seeded.")
        except Exception as e:
            print("Error seeding PRODUCTION_ORDER:", e)

        try:
            cursor.executemany("""
                INSERT IGNORE INTO RAW_MATERIAL (raw_mat_name, raw_mat_quantity)
                VALUES (%s, %s)
            """, [
                ("Steel", 500),
                ("Plastic", 1000),
                ("Rubber", 300)
            ])
            conn.commit()
            print("Raw materials seeded.")
        except Exception as e:
            print("Error seeding RAW_MATERIAL:", e)

        try:
            cursor.executemany("""
                INSERT IGNORE INTO PRODUCTION_ORDER_PART 
                (order_id, part_id, quantity, unit_price)
                VALUES (%s, %s, %s, %s)
            """, [
                (1, 101, 10, 25.00),
                (1, 102, 5, 40.00),
                (2, 103, 20, 15.00),
                (3, 101, 8, 25.00),
                (4, 104, 12, 30.00)
            ])
            conn.commit()
            print("Production order parts seeded.")
        except Exception as e:
            print("Error seeding PRODUCTION_ORDER_PART:", e)

        try:
            cursor.executemany("""
                INSERT IGNORE INTO BILL_OF_MATERIALS 
                (raw_mat_id, part_id, quantity)
                VALUES (%s, %s, %s)
            """, [
                (1, 101, 5),
                (2, 102, 3),
                (1, 103, 7),
                (3, 104, 2)
            ])
            conn.commit()
            print("Bill of materials seeded.")
        except Exception as e:
            print("Error seeding BILL_OF_MATERIALS:", e)

        try:
            cursor.executemany("""
                INSERT IGNORE INTO PRODUCTION_REPORT 
                (report_date, part_id, num_parts_finished, production_status, estimated_completion_date, stage_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, [
                ("2026-04-02", 101, 5, True, "2026-04-10", 1),
                ("2026-04-04", 102, 3, False, "2026-04-12", 2),
                ("2026-04-06", 103, 10, True, "2026-04-15", 3)
            ])
            conn.commit()
            print("Production reports seeded.")
        except Exception as e:
    
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