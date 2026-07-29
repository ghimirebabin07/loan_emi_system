from fastapi import APIRouter, Depends, HTTPException
from .. import schemas
from ..database import get_db

router = APIRouter(prefix="/customers",tags=["Customers"])

@router.post("/", response_model=schemas.CustomerOut)
def create_customer(customer: schemas.CustomerCreate, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO customers(name,phone,address) VALUES (?,?,?)",
        (customer.name, customer.phone, customer.address),
    )
    db.commit()
    new_id = cursor.lastrowid

    cursor.execute("SELECT * FROM customers WHERE id = ?", (new_id,))
    row = cursor.fetchone()
    return dict(row)

@router.get("/", response_model=list[schemas.CustomerOut])
def list_customers(db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM customers")
    rows = cursor.fetchall()
    return [dict(row) for row in rows]

@router.delete("/{customer_id}")
def delete_customer(customer_id: int, db=Depends(get_db)):
    cursor = db.cursor()

    cursor.execute("SELECT id FROM customers WHERE id = ?", (customer_id,))
    if not cursor.fetchone():
        raise HTTPException(404, "Customer not found")

    # block deletion if any of this customer's loans still has an unpaid EMI
    cursor.execute(
        """SELECT COUNT(*) AS pending
           FROM loans l
           JOIN emi_schedule e ON e.loan_id = l.id
           WHERE l.customer_id = ? AND e.status != 'paid'""",
        (customer_id,),
    )
    if cursor.fetchone()["pending"] > 0:
        raise HTTPException(400, "Cannot delete: customer still has an active/unpaid loan")

    # all loans are fully paid — safe to clean up, child rows first
    cursor.execute("SELECT id FROM loans WHERE customer_id = ?", (customer_id,))
    loan_ids = [row["id"] for row in cursor.fetchall()]

    for loan_id in loan_ids:
        cursor.execute(
            "DELETE FROM payments WHERE emi_id IN (SELECT id FROM emi_schedule WHERE loan_id = ?)",
            (loan_id,),
        )
        cursor.execute("DELETE FROM emi_schedule WHERE loan_id = ?", (loan_id,))
        cursor.execute("DELETE FROM loans WHERE id = ?", (loan_id,))

    cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
    db.commit()

    return {"message": f"Customer {customer_id} deleted along with their completed loan history"}
