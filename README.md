# Loan / EMI Management System

A backend-driven system that digitizes how a bank or micro-finance branch manages customers, loans, EMI (Equated Monthly Installment) schedules, and repayments — replacing manual ledger tracking with a structured, rule-enforced database and a REST API that drives all business logic.

---

## What This Project Actually Is

In any lending institution, five things need to be tracked and kept perfectly in sync:

1. **Who the customers are**
2. **Which staff member (loan officer) handled each loan**
3. **What loans exist** — amount, interest rate, tenure
4. **What monthly installments (EMIs) are due**, and when
5. **What payments have actually been received** against those installments

This project models exactly that as a relational database, and wraps it in an API so those records can be created, updated, and queried safely — with the database itself enforcing the rules (no negative loan amounts, no duplicate phone numbers, no invalid EMI statuses) rather than trusting application code to always get it right.

The core idea it demonstrates: **once a loan is created, the system automatically works out the entire month-by-month repayment plan on its own** — nobody manually calculates or types in 12/24/36 EMI rows. That calculation, and keeping loan status accurate over time (pending → overdue → paid), is the real "brain" of the project.

---

## Core Features

- **Customer management** — register customers and look them up, with phone numbers enforced as unique so no duplicate customer records can exist.

- **Loan officer management** — track which staff member is responsible for which loans, by branch.

- **Automated loan creation with EMI generation** — when a new loan is created (principal, interest rate, tenure), the system:
  - calculates the exact monthly installment using the standard reducing-balance EMI formula (the same formula real banks use)
  - automatically generates the full repayment schedule, one row per month, with correct due dates
  - links every installment back to the loan and the customer

- **Live loan status tracking** — nothing is manually marked "overdue." Every time a loan is viewed, the system checks each pending installment's due date against today's date and updates its status accordingly.

- **Payment recording** — payments are recorded against a specific EMI row, with safeguards so an already fully-paid installment can't be paid again, and partial payments are recognized distinctly from full payments.

- **Outstanding balance calculation** — the amount a customer still owes on a loan is never stored as a fixed number; it's calculated live by subtracting everything actually paid from the original loan amount, so it's always accurate.

- **Branch/portfolio dashboard** — a single summary view showing total active loans, total overdue installments, and total outstanding amount across the entire system — the kind of report a branch manager would actually want.

- **Data integrity enforced at the database level, not just in code** — every table has a primary key, related tables are linked with foreign keys, and constraints (`NOT NULL`, `UNIQUE`, `CHECK`) physically block bad data (like a zero-amount loan or an invalid status) from ever being saved, regardless of what the application code does.

- **Safe deletion behavior** — deleting a loan automatically removes its dependent EMI rows too, instead of leaving orphaned records that point to something that no longer exists.

---

## How It Works, Conceptually

1. A **customer** and a **loan officer** are registered first — every loan must belong to exactly one of each.
2. A **loan** is created against that customer/officer pair, with an amount, interest rate, and tenure (in months).
3. The moment that loan is saved, the **EMI calculation engine** runs:
   - converts the yearly interest rate into a monthly rate
   - applies the reducing-balance EMI formula to get one fixed monthly installment amount
   - generates that installment across the correct number of future months, one month apart
4. Those installments are stored as an **EMI schedule**, each one initially marked `pending`.
5. As real-world time passes, any `pending` installment whose due date has passed gets recalculated as `overdue` whenever the loan is looked up — this is intentionally never a permanently stored flag, since "overdue" depends entirely on the current date.
6. When a **payment** comes in, it's matched to a specific installment. If the amount covers it fully, that installment becomes `paid`; if not, it's marked `partially_paid`.
7. At any point, the **outstanding balance** for a loan is worked out live: total loan amount minus everything actually paid so far.
8. The **dashboard** aggregates all of this across every loan in the system, to give a single "health of the portfolio" snapshot.

The relationships form a clear hierarchy:

```
Customer ──< Loan >── Loan Officer
                │
                ▼
          EMI Schedule ──< Payment
```

(One customer can have many loans. One loan has many EMI installments. Each installment can have at most one payment.)

---

## Technologies Used

| Layer | Technology | Role |
|---|---|---|
| **Backend framework** | FastAPI (Python) | Exposes the system's logic as REST API endpoints; handles request validation automatically |
| **Database** | SQLite | Stores all data in a single file — no separate database server needed, ideal for this scale of project |
| **ORM** | SQLAlchemy | Maps Python classes to database tables, so table creation and queries are written as Python instead of raw SQL |
| **Data validation** | Pydantic | Defines and enforces the exact shape of data allowed in and out of each API endpoint, independent of the database structure |
| **Date handling** | python-dateutil | Correctly calculates monthly due dates (e.g., "add 1 month") across different month lengths |
| **API server** | Uvicorn | Runs the FastAPI application and handles incoming requests |
| **Frontend** | HTML, CSS, JavaScript (vanilla) | A lightweight interface that calls the API to display and interact with customers, loans, payments, and the dashboard |
| **SQL** | Raw SQL script | A separate, hand-written script demonstrating table creation, constraints, and queries directly — independent of the ORM, used to show the underlying database design explicitly |

---

## Why It's Built This Way

- **FastAPI + SQLAlchemy** is used because it mirrors how real backend systems are actually built in industry — business logic in Python, but with a real relational database underneath enforcing structural rules, not just application-level checks.
- **SQLite** is chosen deliberately for scale and simplicity — the concepts (foreign keys, constraints, joins) are identical to what a larger database (PostgreSQL, MySQL) would use, but with zero setup overhead.
- **Live-calculated fields** (overdue status, outstanding balance) reflect how real financial systems behave — those values change with time and payments, so storing them as fixed numbers would make the data go stale and unreliable.
- **A separate raw SQL script** exists alongside the ORM-driven app specifically to show that the underlying relational design — and not just the Python code — is understood, since it's easy to build something that "works" through an ORM without actually knowing what's happening at the database level.
