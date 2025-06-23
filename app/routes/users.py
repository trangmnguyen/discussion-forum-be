from app import models, schemas, database
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    print("Incoming discussion data:", user.dict())
    db_user = models.User(username=user.username)
    db.add(db_user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Username already taken")
    db.refresh(db_user)
    return db_user