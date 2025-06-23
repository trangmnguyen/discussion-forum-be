from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database


router = APIRouter(prefix="/comments", tags=["comments"])

@router.post("/discussion/{discussion_id}", response_model=schemas.CommentOut)
def create_comment(discussion_id: int, comment: schemas.CommentCreate, author_id: int, db: Session = Depends(database.get_db)):
    db_comment = models.Comment(
        body=comment.body,
        author_id=author_id,
        discussion_id=discussion_id,
        parent_id=comment.parent_id,
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


@router.get("/discussion/{discussion_id}", response_model=List[schemas.CommentOut])
def get_comments(discussion_id: int, db: Session = Depends(database.get_db)):
    return db.query(models.Comment).filter_by(discussion_id=discussion_id).all()


@router.patch("/{comment_id}")
def update_comment(comment_id: int, body: dict, author_id: int, db: Session = Depends(database.get_db)):
    comment = db.query(models.Comment).get(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.author_id != author_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    if "body" in body:
        comment.body = body["body"]

    db.commit()
    db.refresh(comment)
    return comment


@router.delete("/{comment_id}")
def soft_delete_comment(comment_id: int, author_id: int, db: Session = Depends(database.get_db)):
    comment = db.query(models.Comment).get(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.author_id != author_id:
        raise HTTPException(status_code=403, detail="Unauthorized")

    comment.deleted = True
    comment.deleted_at = datetime.utcnow()
    db.commit()
    return {"message": "Comment marked as deleted"}
