from app import models, schemas, database
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(prefix="/discussions", tags=["discussions"])

@router.post("/", response_model=schemas.DiscussionOut)
def create_discussion(discussion: schemas.DiscussionCreate, author_id: int, db: Session = Depends(database.get_db)):
    author = db.query(models.User).get(author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    db_disc = models.Discussion(**discussion.dict(), author_id=author_id)
    db.add(db_disc)
    db.commit()
    db.refresh(db_disc)
    return db_disc


@router.get("/", response_model=List[schemas.DiscussionOut])
def list_discussions(db: Session = Depends(database.get_db)):
    return db.query(models.Discussion).all()


@router.patch("/{discussion_id}", response_model=schemas.DiscussionOut)
def update_discussion(
    discussion_id: int,
    update_data: dict,
    author_id: int,
    db: Session = Depends(database.get_db)
):
    discussion = db.query(models.Discussion).get(discussion_id)
    if not discussion:
        raise HTTPException(status_code=404, detail="Discussion not found")
    if discussion.author_id != author_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    if "title" in update_data:
        discussion.title = update_data["title"]
    if "body" in update_data:
        discussion.body = update_data["body"]

    db.commit()
    db.refresh(discussion)
    return discussion


@router.delete("/{discussion_id}")
def soft_delete_comment(discussion_id: int, author_id: int, db: Session = Depends(database.get_db)):
    discussion = db.query(models.Discussion).get(discussion_id)
    if not discussion:
        raise HTTPException(status_code=404, detail="Discussion not found")
    if discussion.author_id != author_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    discussion.deleted = True
    discussion.deleted_at = datetime.utcnow()
    db.commit()
    return {"message": "Discussion marked as deleted"}
