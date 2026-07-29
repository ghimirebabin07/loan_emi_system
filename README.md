# Loan / EMI Management System

A backend-driven system that digitizes how a bank or micro-finance branch manages customers, loans, EMI (Equated Monthly Installment) schedules, and repayments — replacing manual ledger tracking with a structured, rule-enforced database and a REST API that drives all business logic.

**Live demo:** [loan-emi-system-1.onrender.com](https://loan-emi-system-1.onrender.com/index.html)

> Note: the demo is hosted on Render's free tier, so the first request after inactivity may take 30–60 seconds to wake the server.

---

## Why This Project

This is a micro project assigned by DBMS course teacher **Dr. Ram Govinda Aryal**. The main goal isn't the finished app itself — it's to actually learn how a database and a backend work together: designing relational tables, enforcing rules at the database level with constraints and foreign keys, and building an API that turns raw data into real business logic (like generating an EMI schedule or calculating a live balance) instead of just doing CRUD.

---

## The Problem

In any lending institution, five things need to be tracked and kept perfectly in sync:

1. Who the customers are
2. Which loan officer handled each loan
3. What loans exist — amount, interest rate, tenure
4. What monthly installments (EMIs) are due, and when
5. What payments have actually been received against those installments

Doing this manually (spreadsheets, paper ledgers) is error-prone: EMI schedules get miscalculated, overdue status goes unnoticed, and outstanding balances drift out of sync with actual payments.

This project solves that by modeling the whole workflow as a relational database and exposing it through an API that enforces the rules — no negative loan amounts, no duplicate phone numbers, no invalid EMI statuses — so the data can't get corrupted, whether the request comes from the frontend or somewhere else.

The core idea: **once a loan is created, the system automatically works out the entire month-by-month repayment plan** using the standard reducing-balance EMI formula. Nobody manually types in 12/24/36 EMI rows. Loan status (pending → overdue → paid) and outstanding balance are also never stored as fixed numbers — they're calculated live, every time they're requested, so they're always accurate.

---

## Core Features

- **Customer management** — register and look up customers, with phone numbers enforced as unique.
- **Loan officer management** — track which staff member is responsible for which loans, by branch.
- **Automated loan creation with EMI generation** — creating a loan calculates the monthly installment and generates the full repayment schedule with correct due dates, automatically.
- **Live loan status tracking** — pending installments are checked against today's date and marked overdue on the fly, not manually.
- **Payment recording** — payments are matched to a specific EMI, with safeguards against double-paying an already-settled installment, and partial payments handled distinctly from full payments.
- **Live outstanding balance calculation** — worked out as loan amount minus everything actually paid, every time it's requested.
- **Branch/portfolio dashboard** — a single summary view: total active loans, total overdue installments, total outstanding amount.
- **Database-level data integrity** — primary keys, foreign keys, and constraints (`NOT NULL`, `UNIQUE`, `CHECK`) physically block bad data, regardless of what the application code does.
- **Safe deletion behavior** — deleting a loan cascades to remove its dependent EMI rows instead of leaving orphaned records.

---

## Technology Used

| Layer | Technology | Role |
|---|---|---|
| Backend framework | FastAPI (Python) | Exposes the system's logic as REST API endpoints; handles request validation automatically |
| Database | SQLite | Stores all data in a single file — no separate database server needed |
| ORM | SQLAlchemy | Maps Python classes to database tables |
| Data validation | Pydantic | Enforces the exact shape of data allowed in and out of each API endpoint |
| Date handling | python-dateutil | Correctly calculates monthly due dates across different month lengths |
| API server | Uvicorn | Runs the FastAPI application |
| Frontend | HTML, CSS, JavaScript (vanilla) | Lightweight interface that calls the API to display and interact with customers, loans, payments, and the dashboard |
| SQL | Raw SQL script | A hand-written script demonstrating table creation, constraints, and queries independently of the ORM |
| Deployment | Render | Hosts the live demo |

---

## Running It Locally

**1. Clone the repository**
```bash
git clone <your-repo-url>
cd <repo-folder>
```

**2. Set up the backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**3. Start the backend server**
```bash
uvicorn app.main:app --reload
```
The API will be running at `http://127.0.0.1:8000`, with interactive docs at `http://127.0.0.1:8000/docs`.

**4. Run the frontend**

The frontend is plain HTML/CSS/JS, so it doesn't need a build step. Open `frontend/index.html` directly in your browser, or — if your browser blocks `fetch()` from a `file://` page — serve it locally:
```bash
cd frontend
python -m http.server 5500
```
Then visit `http://127.0.0.1:5500`.

**Test it in this order:**
1. Dashboard loads with all zeros on an empty database
2. Add a loan officer
3. Add a customer
4. Create a loan → confirm the EMI schedule fills in automatically
5. Record a payment against one EMI → confirm its status updates to "paid"
6. Refresh the dashboard → confirm the totals reflect what you just did