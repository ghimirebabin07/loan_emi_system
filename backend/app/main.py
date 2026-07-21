from fastapi import FastAPI
from .database import get_connection
from .models import create_tables
from .routers import customers, officers, loans, payments, dashboard

app = FastAPI(title="Loan / EMI Management System")

# create the tables once, at startup, using a short-lived connection
conn = get_connection()
create_tables(conn)
conn.close()

app.include_router(customers.router)
app.include_router(officers.router)
app.include_router(loans.router)
app.include_router(payments.router)
app.include_router(dashboard.router)


@app.get("/")
def root():
    return {"message": "Loan/EMI Management System API running"}