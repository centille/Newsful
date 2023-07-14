import os

import mysql.connector as sql
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core import fact_checker, summarize, to_english
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

username = os.environ.get("USERNAME")
password = os.environ.get("PASSWORD")
host = os.environ.get("HOST")
dbname = os.environ.get("DATABASE")
conn = sql.connect(
    host=host,
    user=username,
    passwd=password,
    db=dbname,
)


@app.get("/api/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/api/verify")
def give_this_crap_function_a_name(data: Data):
    """Endpoint to verify a news article."""
    data.content = to_english(data.content)
    summary = summarize(data.content)
    new_data = Data(content=summary, title=data.title)
    fact_check = fact_checker(conn, new_data)
    pass


@app.get("/api/summarize")
def summarize_text(text: str):
    """Endpoint to summarize a news article."""
    return {"summary": summarize(text)}
