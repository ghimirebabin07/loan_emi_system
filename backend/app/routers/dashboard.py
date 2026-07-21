from fastapi import APIRouter, Depends
from datetime import date
from ..database import get_db

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
def dashboard_summary(db=Depends(get_db)):
    cursor = db.cursor()
    today = date.today().isoformat()

    cursor.execute("SELECT COUNT(*) AS total FROM loans")
    total_loans = cursor.fetchone()["total"]

    cursor.execute(
        "UPDATE emi_schedule SET status = 'overdue' WHERE status = 'pending' AND due_date < ?",
        (today,),
    )
    db.commit()

    cursor.execute("SELECT COUNT(*) AS total FROM emi_schedule WHERE status = 'overdue'")
    overdue_count = cursor.fetchone()["total"]

    cursor.execute("SELECT COALESCE(SUM(amount_paid), 0) AS total FROM payments")
    total_paid = cursor.fetchone()["total"]

    cursor.execute("SELECT COALESCE(SUM(amount), 0) AS total FROM loans")
    total_loan_amount = cursor.fetchone()["total"]

    total_outstanding = total_loan_amount - total_paid

    return {
        "total_active_loans": total_loans,
        "total_overdue_emis": overdue_count,
        "total_outstanding_amount": round(total_outstanding, 2),
    }