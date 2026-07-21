from fastapi import APIRouter,Depends
from ..database import get_db

router = APIRouter(prefix="/officers",tags=["Officers"])

@router.post("/")
def create_officer(name:str,branch:str = None, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO loan_officers (name,branch) VALUES(?,?)",
        (name,branch),
    )
    db.commit()
    cursor.execute("SELECT * FROM loan_officers WHERE id = ?",
    (cursor.lastrowid,))
    return dict(cursor.fetchone())

@router.get("/")
def list_officers(db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM loan_officers")
    return [dict(row) for row in cursor.fetchall()] 