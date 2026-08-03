from fastapi import APIRouter, Depends, HTTPException
from .. import schemas
from ..database import get_db

router = APIRouter(prefix="/officers", tags=["Officers"])


@router.post("/", response_model=schemas.OfficerOut)
def create_officer(officer: schemas.OfficerCreate, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO loan_officers (name,branch) VALUES(?,?)",
        (officer.name, officer.branch),
    )
    db.commit()
    cursor.execute("SELECT * FROM loan_officers WHERE id = ?", (cursor.lastrowid,))
    return dict(cursor.fetchone())


@router.get("/", response_model=list[schemas.OfficerOut])
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

    cursor.execute(
        "SELECT COUNT(*) AS total FROM loans WHERE officer_id = ?",
        (officer_id,),
    )
    if cursor.fetchone()["total"] > 0:
        raise HTTPException(400, "Cannot delete: officer has loan history that must remain permanent")

    cursor.execute("DELETE FROM loan_officers WHERE id = ?", (officer_id,))
    db.commit()

    return {"message": f"Officer {officer_id} deleted"}