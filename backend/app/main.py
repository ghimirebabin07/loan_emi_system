from fastapi import FastAPI
from .database import get_connection
from .models import create_tables
from .routers import customers, officers, loans, payments, dashboard
from fastapi.middleware.cors import CORSMiddleware 


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Loan/EMI Management System API running"}