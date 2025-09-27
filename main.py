import uvicorn
from fastapi import Depends, FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, SQLModel, create_engine, select
from models.movie import Movie
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
        }
    )

@app.get("/form_edit", response_class=HTMLResponse)
async def form_edit(request: Request, session: SessionDep):
    movies = session.exec(select(Movie)).all()
    return templates.TemplateResponse(
        "form_edit.html", {
            "request": request,
            "movies": movies
        }
    )

@app.post("/submit_form")
async def submit_form(
    name: str = Form(...),
    genre: str = Form(...),
    year_release: str = Form(...),
    year_watched: str = Form(...),
    rating: int = Form(...),
    session: SessionDep = None
):
    movie = Movie(
        name=name,
        genre=genre,
        year_release=year_release,
        year_watched=year_watched,
        rating=rating
    )
    session.add(movie)
    session.commit()
    session.refresh(movie)
    return RedirectResponse(url="/form_edit", status_code=303)

@app.post("/delete_movie/{movie_name}")
async def delete_movie(movie_name: str, session: SessionDep):
    import urllib.parse
    movie_name = urllib.parse.unquote(movie_name)
    
    movie = session.exec(select(Movie).where(Movie.name == movie_name)).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    session.delete(movie)
    session.commit()
    return RedirectResponse(url="/form_edit", status_code=303)

@app.get("/edit_movie/{movie_name}", response_class=HTMLResponse)
async def edit_movie_form(request: Request, movie_name: str, session: SessionDep):
    import urllib.parse
    movie_name = urllib.parse.unquote(movie_name)
    
    movie = session.exec(select(Movie).where(Movie.name == movie_name)).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return templates.TemplateResponse(
        "edit_movie.html", {
            "request": request,
            "movie": movie
        }
    )

@app.post("/update_movie/{movie_name}")
async def update_movie(
    movie_name: str, 
    session: SessionDep,
    name: str = Form(...), 
    genre: str = Form(...),
    year_release: str = Form(...),
    year_watched: str = Form(...),
    rating: int = Form(...)
):
    import urllib.parse
    movie_name = urllib.parse.unquote(movie_name)
    
    movie = session.exec(select(Movie).where(Movie.name == movie_name)).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    session.delete(movie)
    session.commit()
    
    updated_movie = Movie(
        name=name,
        genre=genre,
        year_release=year_release,
        year_watched=year_watched,
        rating=rating
    )
    session.add(updated_movie)
    session.commit()
    
    return RedirectResponse(url="/form_edit", status_code=303)

if __name__ == "__main__":
    sqlite_file_name = "database.db"
    sqlite_url = f"sqlite:///{sqlite_file_name}"

    connect_args = {"check_same_thread": False}
    engine = create_engine(sqlite_url, connect_args=connect_args)
    SQLModel.metadata.create_all(engine)
    uvicorn.run(app, host="0.0.0.0", port=8000)