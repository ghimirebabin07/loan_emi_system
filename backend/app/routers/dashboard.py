from fastapi import APIRouter, Depends
from datetime import date
from ..database import get_db

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
def dashboard_summary(db=Depends(get_db)):
    cursor = db.cursor()
    today = date.today().isoformat()

    cursor.execute("SELECT COUNT(*) AS total FROM loans WHERE status = 'active'")
    total_loans = cursor.fetchone()["total"]

    cursor.execute(
        """UPDATE emi_schedule
           SET status = 'overdue'
           WHERE status = 'pending'
             AND due_date < ?
             AND loan_id IN (SELECT id FROM loans WHERE status = 'active')""",
        (today,),
    )
    db.commit()

    cursor.execute(
        """SELECT COUNT(*) AS total
           FROM emi_schedule e
           JOIN loans l ON l.id = e.loan_id
           WHERE l.status = 'active' AND e.status = 'overdue'"""
    )
    overdue_count = cursor.fetchone()["total"]

    cursor.execute(
        """SELECT COALESCE(SUM(e.emi_amount), 0) AS total
           FROM emi_schedule e
           JOIN loans l ON l.id = e.loan_id
           WHERE l.status = 'active' AND e.status != 'paid'"""
    )
    total_outstanding = cursor.fetchone()["total"]

    return {
        "total_active_loans": total_loans,
        "total_overdue_emis": overdue_count,
        "total_outstanding_amount": round(max(total_outstanding, 0), 2),
    }