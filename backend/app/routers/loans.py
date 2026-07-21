from fastapi import APIRouter, Depends, HTTPException
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
           (amount, interest_rate, tenure_months, start_date, customer_id, officer_id)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (loan.amount, loan.interest_rate, loan.tenure_months, today,
         loan.customer_id, loan.officer_id),
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


@router.get("/{loan_id}", response_model=schemas.LoanOut)
def get_loan_status(loan_id: int, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM loans WHERE id = ?", (loan_id,))
    loan_row = cursor.fetchone()
    if not loan_row:
        raise HTTPException(404, "Loan not found")

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
    cursor.execute("SELECT amount FROM loans WHERE id = ?", (loan_id,))
    loan_row = cursor.fetchone()
    if not loan_row:
        raise HTTPException(404, "Loan not found")

    cursor.execute(
        """SELECT COALESCE(SUM(p.amount_paid), 0) AS total_paid
           FROM payments p
           JOIN emi_schedule e ON p.emi_id = e.id
           WHERE e.loan_id = ?""",
        (loan_id,),
    )
    total_paid = cursor.fetchone()["total_paid"]
    outstanding = loan_row["amount"] - total_paid

    return {"loan_id": loan_id, "outstanding_balance": round(outstanding, 2)} 

