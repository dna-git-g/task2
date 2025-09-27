import uvicorn
from fastapi import Depends, FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Field, Session, SQLModel, create_engine, select
from models.movie import Movie
from contextlib import asynccontextmanager
from typing import Annotated

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(
        "index.html", {
            "request": request,
            "data": "Some dynamic data"
        }
    )

"""
@app.post("/submit_form")
async def submit_form(
    name=Form(),
    genre=Form(),
    year_release=Form(),
    year_watched=Form(),
    rating=Form(),
    ):
    print(name, genre, year_release, year_watched, rating)
    return {"message": "OK"}"""

@app.post("/submit_form")
async def submit_form(movie: Annotated[Movie, Form()], session: SessionDep):
    session.add(movie)
    session.commit()
    session.refresh(movie)
    return {"message": "OK"}

if __name__ == "__main__":
    sqlite_file_name = "database.db"
    sqlite_url = f"sqlite:///{sqlite_file_name}"

    connect_args = {"check_same_thread": False}
    engine = create_engine(sqlite_url, connect_args=connect_args)
    SQLModel.metadata.create_all(engine)
    uvicorn.run(app, host="0.0.0.0", port=8000)