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


@router.get("/{customer_id}/loans", response_model=list[schemas.LoanListOut])
def customer_loan_history(customer_id: int, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT id FROM customers WHERE id = ?", (customer_id,))
    if not cursor.fetchone():
        raise HTTPException(404, "Customer not found")

    cursor.execute(
        """SELECT
               l.id,
               c.name AS customer_name,
               o.name AS officer_name,
               l.amount,
               l.status,
               l.start_date
           FROM loans l
           JOIN customers c ON c.id = l.customer_id
           LEFT JOIN loan_officers o ON o.id = l.officer_id
           WHERE l.customer_id = ?
           ORDER BY l.id DESC""",
        (customer_id,),
    )
    return [dict(row) for row in cursor.fetchall()]

@router.delete("/{customer_id}")
def delete_customer(customer_id: int, db=Depends(get_db)):
    cursor = db.cursor()

    cursor.execute("SELECT id FROM customers WHERE id = ?", (customer_id,))
    if not cursor.fetchone():
        raise HTTPException(404, "Customer not found")

    cursor.execute(
        "SELECT COUNT(*) AS total FROM loans WHERE customer_id = ?",
        (customer_id,),
    )
    if cursor.fetchone()["total"] > 0:
        raise HTTPException(400, "Cannot delete: customer has loan history that must remain permanent")

    cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
    db.commit()

    return {"message": f"Customer {customer_id} deleted"}
