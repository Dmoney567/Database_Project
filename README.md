Supply Chain Database App
---------------------------------------------------------------------------------------------------------------------------
Supply chain database CRUD application written in Python with FastAPI and MySQL for database backend, and Jinja2 Template.
This app allows the user to lookup, read, write, and modify, production orders for part production, and track their location throughout a simulated
production facility.

Ensure that .env is located in root folder with format:<br>
DB_HOST=portnumber<br>
DB_USER=username<br>
DB_PASS=password<br>
DB_NAME=databasename<br>

Ensure an instance of your database is already created before connecting <br>
Then if running the db setup with the same file structure, use "python app/database/setup.py" <br>
Then reload with "uvicorn app.main:app --reload"<br>


demo of 5 unique category of operations that will specifically require access to the<br>
database (The following five operations are mandatory)<br>
Create new entries <br>
Read existing entries<br>
Update existing entries<br>
Delete existing entries<br>
Search entries or perform user authentication (user validation through log-in operations)<br>


<img width="3240" height="1808" alt="Screenshot (924)" src="https://github.com/user-attachments/assets/62304978-e107-4474-9fa2-1e2ead6402d1" />

