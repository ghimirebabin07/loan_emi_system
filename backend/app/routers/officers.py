from fastapi import APIRouter,Depends,HTTPException 
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

@router.delete("/{officer_id}")
def delete_officer(officer_id: int, db=Depends(get_db)):
    cursor = db.cursor()

    cursor.execute("SELECT id FROM loan_officers WHERE id = ?", (officer_id,))
    if not cursor.fetchone():
        raise HTTPException(404, "Officer not found")

    # block deletion if the officer still has a customer mid-loan
    cursor.execute(
        """SELECT COUNT(*) AS pending
           FROM loans l
           JOIN emi_schedule e ON e.loan_id = l.id
           WHERE l.officer_id = ? AND e.status != 'paid'""",
        (officer_id,),
    )
    if cursor.fetchone()["pending"] > 0:
        raise HTTPException(400, "Cannot delete: officer still has an active/unpaid loan under them")

    cursor.execute("UPDATE loans SET officer_id = NULL WHERE officer_id = ?", (officer_id,))
    cursor.execute("DELETE FROM loan_officers WHERE id = ?", (officer_id,))
    db.commit()

    return {"message": f"Officer {officer_id} deleted"}