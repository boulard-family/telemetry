from fastapi import FastAPI
from contextlib import asynccontextmanager

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy import create_engine, select


app = FastAPI()


class Base(DeclarativeBase):
    pass


class Counter(Base):
    __tablename__ = "counter"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    value: Mapped[int]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield
    # Shutdown
    db.close()


@app.post("/counter/blog/{article}")
def increment_article_counter(article: str):
    """
    Increments by one the number of views of the specified article.
    """
    path = f"blog.{article}"
    with Session(engine) as session:
        stmt = select(Counter).where(Counter.name == path)
        counter = session.scalars(stmt).one_or_none()
        if counter:
            counter.value += 1
        else:
            counter = Counter(name=path, value=1)
            session.add(counter)
        session.commit()


@app.get("/counter/blog/{article}")
def get_article_counter(article: str):
    """
    Returns the number of views on an article.
    Returns 0 if the requested article doesn't exist.
    """
    path = f"blog.{article}"
    with Session(engine) as session:
        stmt = select(Counter).where(Counter.name == path)
        counter = session.scalars(stmt).one_or_none()
        if counter:
            value = counter.value
        else:
            value = 0
    return {"views": value}


engine = create_engine("sqlite:///telemetry.db")
Base.metadata.create_all(engine)
