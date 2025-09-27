from sqlmodel import Field, Session, SQLModel, create_engine, select
from datetime import datetime

class Movie(SQLModel, table=True):
    name: str | None = Field(default=None, primary_key=True)
    genre: str | None = Field(default=None, index=True)
    year_release: str = Field(index=True)
    year_watched: str = Field(index=True)
    rating: int | None = Field(default=None, index=True)