from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import date
from .. import schemas
from ..database import get_db
from ..emi_logic import calculate_emi, generate_schedule

router = APIRouter(prefix="/loans", tags=["Loans"])


@router.post("/", response_model=schemas.LoanOut)
def create_loan(loan: schemas.LoanCreate, db=Depends(get_db)):
    cursor = db.cursor()
    today = date.today().isoformat()

    cursor.execute(
          """INSERT INTO loans
              (amount, interest_rate, tenure_months, start_date, status, customer_id, officer_id)
              VALUES (?, ?, ?, ?, 'active', ?, ?)""",
          (loan.amount, loan.interest_rate, loan.tenure_months, today, loan.customer_id, loan.officer_id),
    )
    db.commit()
    loan_id = cursor.lastrowid

    emi_amount = calculate_emi(loan.amount, loan.interest_rate, loan.tenure_months)
    schedule = generate_schedule(date.today(), emi_amount, loan.tenure_months)

    cursor.executemany(
        "INSERT INTO emi_schedule (due_date, emi_amount, status, loan_id) VALUES (?, ?, 'pending', ?)",
        [(due.isoformat(), amount, loan_id) for due, amount in schedule],
    )
    db.commit()

    return get_loan_status(loan_id, db)


@router.get("/", response_model=list[schemas.LoanListOut])
def list_loans(status: str | None = Query(default=None), db=Depends(get_db)):
    if status is not None and status not in {"active", "completed"}:
        raise HTTPException(400, "status must be either 'active' or 'completed'")

    cursor = db.cursor()
    query = """
        SELECT
            l.id,
            c.name AS customer_name,
            o.name AS officer_name,
            l.amount,
            l.status,
            l.start_date
        FROM loans l
        JOIN customers c ON c.id = l.customer_id
        LEFT JOIN loan_officers o ON o.id = l.officer_id
    """
    params = ()
    if status is not None:
        query += " WHERE l.status = ?"
        params = (status,)
    query += " ORDER BY l.id DESC"

    cursor.execute(query, params)
    return [dict(row) for row in cursor.fetchall()]


@router.get("/{loan_id}", response_model=schemas.LoanOut)
def get_loan_status(loan_id: int, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM loans WHERE id = ?", (loan_id,))
    loan_row = cursor.fetchone()
    if not loan_row:
        raise HTTPException(404, "Loan not found")

    if loan_row["status"] == "active":
        today = date.today().isoformat()
        cursor.execute(
            "UPDATE emi_schedule SET status = 'overdue' WHERE loan_id = ? AND status = 'pending' AND due_date < ?",
            (loan_id, today),
        )
        db.commit()

    cursor.execute(
        "SELECT * FROM emi_schedule WHERE loan_id = ? ORDER BY due_date", (loan_id,)
    )
    emi_rows = cursor.fetchall()

    loan = dict(loan_row)
    loan["emis"] = [dict(row) for row in emi_rows]
    return loan


@router.get("/{loan_id}/balance")
def get_outstanding_balance(loan_id: int, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT id FROM loans WHERE id = ?", (loan_id,))
    loan_row = cursor.fetchone()
    if not loan_row:
        raise HTTPException(404, "Loan not found")

    cursor.execute(
        """SELECT COALESCE(SUM(emi_amount), 0) AS outstanding_balance
           FROM emi_schedule
           WHERE loan_id = ? AND status != 'paid'""",
        (loan_id,),
    )
    outstanding = cursor.fetchone()["outstanding_balance"] or 0

    return {"loan_id": loan_id, "outstanding_balance": round(max(outstanding, 0), 2)} 

