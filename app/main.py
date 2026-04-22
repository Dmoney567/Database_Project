from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from mysql.connector import pooling
from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware
from passlib.context import CryptContext
from fastapi import Form
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#load environment variables
load_dotenv()
app = FastAPI(title = "Supply Chain Database")
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    SessionMiddleware,
    secret_key="super-secret-key",  # change this later
)

db_pool = pooling.MySQLConnectionPool(
    pool_name = "supply_pool",
    pool_size = 10,
    host=os.getenv("DB_HOST"),
    user = os.getenv("DB_USER"),
    password = os.getenv("DB_PASS"),
    database = os.getenv("DB_NAME")
)


print("DB_HOST =", os.getenv("DB_HOST"))
print("DB_USER =", os.getenv("DB_USER"))
print("DB_NAME =", os.getenv("DB_NAME"))

def get_db_conn():
    """retrieves a connection from the pre-warmed connection pool"""
    return db_pool.get_connection()

###ROUTES##################################################################
##defaults to login page
@app.get("/")
async def root():
    return RedirectResponse(url="/login")

##shows login page
@app.get("/login")
def login_page(request:Request):

    return templates.TemplateResponse(request = request,name = "login.html")

##called when user logs in -> go to main dashboard
@app.post("/login")
async def login(request:Request):
    form = await request.form()
    username = form["username"]
    password = form["password"]
    ##connect to database user table
    user = get_user(username)

    ##check if user exists
    if user and verify_password(password, user["password_hash"]):
        request.session["username"] = username
        return RedirectResponse(url="/dashboard", status_code=302)
    ##if not, redirect to login page
    else:
        return RedirectResponse(url="/login?error=invalid", status_code=302)
        ##return templates.TemplateResponse(request = request, name = "login.html")

#register button for storing a new user into db or checking if they exist already
@app.post("/register")
async def register(request: Request):
    form = await request.form()
  
    username = form["username"]
    password = str(form["password"]) 

    ##ensuring no null username or passwords work
    if not username or not password:
        return RedirectResponse(url="/login?error=empty", status_code=302)

    ##check for a pre-existing user
    user = get_user(username)
    if user:
        return RedirectResponse(url="/login?error=exists", status_code=302)
    
    hashed_password = hash_password(password)

    conn = get_db_conn()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO USERS (username, password_hash) VALUES (%s, %s)",
            (username, hashed_password)
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return RedirectResponse(url="/login", status_code=302)  

##default dashboard
@app.get("/dashboard")
async def dashboard(request: Request):
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM PRODUCTION_ORDER")
    orders = cursor.fetchall()

    cursor.execute("SELECT * FROM VENDOR")
    vendors = cursor.fetchall()

    cursor.execute("SELECT * FROM PRODUCTION_REPORT")
    reports = cursor.fetchall()

    cursor.execute("SELECT * FROM RAW_MATERIAL")
    inventory = cursor.fetchall()

    cursor.close()
    conn.close()

    return templates.TemplateResponse(
        request = request,
        name="dashboard.html",
        context={
            "request": request,
            "orders": orders,
            "vendors": vendors,
            "reports":reports,
            "inventory":inventory
        }
    )

##insert
@app.post("/dashboard/orders/create")
async def create_order(request:Request, 
                       order_date_placed :str = Form(), 
                       order_date_due:str = Form() ,status: str = Form() ,
                       production_flag:int = Form(), vendor_id:int = Form()):
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)
    try:
        placed = datetime.strptime(order_date_placed, "%Y-%m-%d").date()
        due = datetime.strptime(order_date_due, "%Y-%m-%d").date()

        query = """
        INSERT IGNORE INTO PRODUCTION_ORDER
        (order_placed_date, order_due_date, order_status, order_production_flag, vend_id)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (placed, due, status, production_flag, vendor_id))
        conn.commit()

        cursor.execute("SELECT * FROM PRODUCTION_ORDER")
        orders = cursor.fetchall()

        return RedirectResponse(url="/dashboard", status_code=302)
    
    finally:
        cursor.close()
        conn.close()
    

def get_user(username):
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT user_id,username, password_hash FROM USERS WHERE username = %s",(username,))
        return cursor.fetchone()
    except Exception as e:
        print(f"Error getting user: {e}")
    finally:
        cursor.close()
        conn.close()

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)





