from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import os
from mysql.connector import pooling
from dotenv import load_dotenv

#load environment variables
load_dotenv()

app = FastAPI(title = "Supply Chain Database")

# Templates
templates = Jinja2Templates(directory="templates")

# Mount the static folder at /static
app.mount("/static", StaticFiles(directory="static"), name="static")

db_pool = pooling.MySQLConnectionPool(
    pool_name = "velocity_pool",
    pool_size = 10,
    host=os.getenv("DB_HOST"),
    user = os.getenv("DB_USER"),
    password = os.getenv("DB_PASS"),
    database = os.getenv("DB_NAME")
)

def get_db_conn():
    """retrieves a connection from the pre-warmed connection pool"""
    return db_pool.get_connection()


@app.get("/")
async def root():
    return RedirectResponse(url="/login")

@app.get("/login")
def login(request:Request):
    return templates.TemplateResponse(request = request,name = "login.html")

@app.get("/dashboard")
async def dashboard(request: Request):

    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM Divisions")
        divisions = cursor.fetchall()

        query = ("""
            SELECT * FROM Rentals
            WHERE return_date IS NULL""")
        cursor.execute(query)
        active_rentals = cursor.fetchall()

        return templates.TemplateResponse(
            request = request,
            name="dashboard.html",
            context={
                "divisions": divisions,
                "active_rentals": active_rentals
                }
        )
    except Exception as e:
         conn.rollback()
         print(f"Transaction Failed: {e}")

    #close cursor connection
    finally:
        cursor.close()
        conn.close()
    return RedirectResponse(url="/",status_code = 303)


#write operation
@app.post("/divisions/create")
async def create_division(request: Request):
    form = await request.form()
    name = form["name"]

    conn = get_db_conn()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO Production_Stage (name) VALUES (%s)",
            (name,)
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return RedirectResponse("/dashboard", status_code=303)


# ### demo of 5 unique category of operations that will specifically require access to the
# database (The following five operations are mandatory)
# ▪ Create new entries
# ▪ Read existing entries
# ▪ Update existing entries
# ▪ Delete existing entries
# ▪ Search entries or perform user authentication (user validation through log-in
# operations)
