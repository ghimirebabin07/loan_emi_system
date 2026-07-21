from fastapi import APIRouter,Depends
from ..import schemas 
from ..database import get_db 

router = APIRouter(prefix="/customers",tags=["Customers"])

@router.post("/",response_model=schemas.CustomerOut) 
def create_customer (customer:schemas.CustomerCreate,db =Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO customers(name,phone,address) VALUES (?,?,?)",
        (customer.name, customer.phone,customer.address),

    )
    db.commit()
    new_id = cursor.lastrowid 

    cursor.execute("SELECT * FROM customers WHERE id = ?",(new_id,))
    row = cursor.fetchone()
    return dict (row)

@router.get("/",response_model=list[schemas.CustomerOut])
def list_customers(db = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM customers")
    rows = cursor.fetchall()
    return[dict(row) for row in rows] 