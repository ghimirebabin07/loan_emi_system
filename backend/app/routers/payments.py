from decimal import Decimal, ROUND_HALF_UP
from fastapi import APIRouter, Depends, HTTPException
from datetime import date
from .. import schemas
from ..database import get_db

router = APIRouter(prefix="/payments", tags=["Payments"])


def _to_money(value: float | Decimal) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _reprice_remaining_emis(cursor, loan_id: int, remaining_balance: Decimal):
    cursor.execute(
        """SELECT id
           FROM emi_schedule
           WHERE loan_id = ? AND status != 'paid'
           ORDER BY due_date, id""",
        (loan_id,),
    )
    remaining_rows = cursor.fetchall()

    if not remaining_rows:
        return

    if remaining_balance <= 0:
        cursor.execute(
            "UPDATE emi_schedule SET status = 'paid' WHERE loan_id = ? AND status != 'paid'",
            (loan_id,),
        )
        return

    row_count = len(remaining_rows)
    total_cents = int((remaining_balance * 100).to_integral_value(rounding=ROUND_HALF_UP))
    base_cents, extra_cents = divmod(total_cents, row_count)

    for index, row in enumerate(remaining_rows, start=1):
        new_cents = base_cents + (1 if index <= extra_cents else 0)
        new_amount = Decimal(new_cents) / Decimal("100")

        cursor.execute(
            "UPDATE emi_schedule SET emi_amount = ? WHERE id = ?",
            (float(new_amount), row["id"]),
        )


def _mark_loan_completed_if_finished(cursor, loan_id: int):
    cursor.execute(
        "SELECT COUNT(*) AS remaining FROM emi_schedule WHERE loan_id = ? AND status != 'paid'",
        (loan_id,),
    )
    if cursor.fetchone()["remaining"] == 0:
        cursor.execute("UPDATE loans SET status = 'completed' WHERE id = ?", (loan_id,))


@router.post("/")
def record_payment(payment: schemas.PaymentCreate, db=Depends(get_db)):
    cursor = db.cursor()

    cursor.execute("SELECT * FROM emi_schedule WHERE id = ?", (payment.emi_id,))
    emi = cursor.fetchone()
    if not emi:
        raise HTTPException(404, "EMI row not found")
    if emi["status"] == "paid":
        raise HTTPException(400, "This EMI is already paid")

    cursor.execute(
        """SELECT COALESCE(SUM(emi_amount), 0) AS total_outstanding
           FROM emi_schedule
           WHERE loan_id = ? AND status != 'paid'""",
        (emi["loan_id"],),
    )
    total_outstanding_before = _to_money(cursor.fetchone()["total_outstanding"] or 0)

    if _to_money(payment.amount_paid) < _to_money(emi["emi_amount"]):
        raise HTTPException(400, "Payment must be at least the EMI amount due")

    paid_date = (payment.paid_date or date.today()).isoformat()
    remaining_balance = max(total_outstanding_before - _to_money(payment.amount_paid), Decimal("0.00"))

    with db:
        cursor.execute(
            "INSERT INTO payments (paid_date, amount_paid, payment_mode, emi_id) VALUES (?, ?, ?, ?)",
            (paid_date, payment.amount_paid, payment.payment_mode, payment.emi_id),
        )

        cursor.execute(
            "UPDATE emi_schedule SET status = 'paid' WHERE id = ?",
            (payment.emi_id,),
        )

        _reprice_remaining_emis(cursor, emi["loan_id"], remaining_balance)
        _mark_loan_completed_if_finished(cursor, emi["loan_id"])

        cursor.execute("SELECT status FROM loans WHERE id = ?", (emi["loan_id"],))
        loan_status = cursor.fetchone()["status"]

    if remaining_balance <= 0:
        message = "Payment recorded. Loan fully paid and marked completed."
    elif remaining_balance < total_outstanding_before - _to_money(emi["emi_amount"]):
        message = "Payment recorded. Remaining EMIs were recalculated."
    else:
        message = "Payment recorded."

    return {
        "message": message,
        "emi_id": payment.emi_id,
        "loan_id": emi["loan_id"],
        "emi_status": "paid",
        "loan_status": loan_status,
        "outstanding_balance": float(remaining_balance),
    }