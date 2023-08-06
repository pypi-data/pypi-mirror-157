from sqlalchemy import Column, String
import asyncio
from dotenv import load_dotenv
import json
import os
import uvicorn


from fastapi import Request, HTTPException
from pydantic import BaseModel

from fastapi.templating import Jinja2Templates
from fastapi import FastAPI
from fastapi import Depends

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base

# from sqlalchemy.future import select
from fastapi_sqlalchemy import DBSessionMiddleware
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from fastapialchemycollector import setup, MetisInstrumentor
templates = Jinja2Templates(directory="templates")


load_dotenv(override=True)  # take environment variables from .env.

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# to avoid csrftokenError
db_url = os.environ["DATABASE_URI"]

assert db_url is not None

app.add_middleware(DBSessionMiddleware, db_url=db_url)

project_dir = os.path.dirname(os.path.abspath(__file__))

engine = create_async_engine(db_url, future=True, echo=True)

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Book(Base):
    __tablename__ = "booking"
    title = Column(String(80), unique=True, nullable=False, primary_key=True)

    def __repr__(self):
        return f"<Title: {self.title}>"


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        if db:
            db.close()


@app.get("/")
async def home(request: Request):
    async with async_session() as session:
        async with session.begin():
            q = await session.execute(select(Book))
            return templates.TemplateResponse(
                "home.html",
                {"request": request, "books": q.scalars().all()},
            )


class BookUpdatePayload(BaseModel):
    newtitle: str
    oldtitle: str


class BookCreatePayload(BaseModel):
    title: str


@app.post("/")
async def create(req: Request):
    try:
        async with async_session() as session:
            async with session.begin():
                book = await req.form()
                new_book = Book(title=book.get("title"))
                session.add(new_book)
                await session.flush()
                q = await session.execute(select(Book).order_by(Book.title))
                return templates.TemplateResponse(
                    "home.html",
                    {"request": req, "books": q.scalars().all()},
                )
    except Exception as e:
        print("Couldn't create book title")
        print(e)
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete(req: Request, db: Session = Depends(get_db)):
    book = await req.form()
    title = book.get("title")
    book = db.get(Book, title)
    if not book:
        raise HTTPException(status_code=404, detail=f'Book: "{title}" not found')
    db.delete(book)
    db.commit()
    return templates.TemplateResponse(
        "home.html",
        {"request": req, "books": db.query(Book).all()},
    )


@app.delete("/{title}", status_code=status.HTTP_200_OK)
async def delete_title(title: str, db: Session = Depends(get_db)):
    book = db.get(Book, title)
    if not book:
        raise HTTPException(status_code=404, detail=f'Book: "{title}" not found')
    db.delete(book)
    db.commit()
    return book


instrumentation: MetisInstrumentor = setup('service-name')
instrumentation.instrument_app(app, engine)

# @app.on_event("startup")
async def startup():
    # create db tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", debug=True, port=5012)
