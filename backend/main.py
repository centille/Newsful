import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine

from core import summarize, to_english, fact_checker
from schemas import Data

app = FastAPI(
    title="Newsful API",
    description="API for Newsful - a news summarization and fact checking app.",
    version="0.0.1",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    swagger_ui_oauth2_redirect_url="api/docs/oauth2-redirect",
    deprecated=False,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = create_engine(os.environ["DATABASE_URL"])
conn = engine.connect()


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/verify")
async def give_this_crap_function_a_name(data: Data):
    data.content = to_english(data.content)
    summary = summarize(data.content)
    new_data = Data(content=summary, title=data.title)
    fact_check = fact_checker(conn, new_data)
    pass


@app.get("/api/summarize")
def summarize_text(text: str):
    return {"summary": summarize(text)}
