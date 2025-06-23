from fastapi import FastAPI
from .database import Base, engine
from .routes import users, discussions, comments

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users.router)
app.include_router(discussions.router)
app.include_router(comments.router)
