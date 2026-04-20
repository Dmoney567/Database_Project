from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from mysql.connector import pooling
from dotenv import load_dotenv
from starlette.middleware.sessions import SessionMiddleware
from passlib.context import CryptContext
import random


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

@app.get("/dashboard")
async def dashboard(request: Request):

    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM PRODUCTION_STAGE")
        divisions = cursor.fetchall()

        query = ("""
            SELECT * FROM VENDOR
            WHERE vend_name IS NULL""")
        cursor.execute(query)
        active_rentals = cursor.fetchall()

        return templates.TemplateResponse(
            request = request,
            name="dashboard.html",
            context={
                "PRODUCTION_STAGE": divisions,
                "VENDOR": active_rentals
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
            "INSERT INTO Production_Stage (stage_name) VALUES (%s)",
            (name,)
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()

    return RedirectResponse("/dashboard", status_code=303)



def get_user(username):
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT user_id,username, password_hash FROM USERS WHERE username = %s",(username,))
        return cursor.fetchone()
    
    finally:
        cursor.close()
        conn.close()

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)





# ### demo of 5 unique category of operations that will specifically require access to the
# database (The following five operations are mandatory)
# ▪ Create new entries
# ▪ Read existing entries
# ▪ Update existing entries
# ▪ Delete existing entries
# ▪ Search entries or perform user authentication (user validation through log-in
# operations)
