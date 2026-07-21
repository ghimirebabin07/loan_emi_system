from fastapi import APIRouter, Depends, HTTPException
from datetime import date
from .. import schemas
from ..database import get_db

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/")
def record_payment(payment: schemas.PaymentCreate, db=Depends(get_db)):
    cursor = db.cursor()

    cursor.execute("SELECT * FROM emi_schedule WHERE id = ?", (payment.emi_id,))
    emi = cursor.fetchone()
    if not emi:
        raise HTTPException(404, "EMI row not found")
    if emi["status"] == "paid":
        raise HTTPException(400, "This EMI is already paid")

    paid_date = (payment.paid_date or date.today()).isoformat()

    cursor.execute(
        "INSERT INTO payments (paid_date, amount_paid, payment_mode, emi_id) VALUES (?, ?, ?, ?)",
        (paid_date, payment.amount_paid, payment.payment_mode, payment.emi_id),
    )

    new_status = "paid" if payment.amount_paid >= emi["emi_amount"] else "partially_paid"
    cursor.execute(
        "UPDATE emi_schedule SET status = ? WHERE id = ?",
        (new_status, payment.emi_id),
    )

    db.commit()
    return {"message": "Payment recorded", "emi_id": payment.emi_id, "status": new_status}