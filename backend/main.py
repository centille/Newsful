import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo.mongo_client import MongoClient

from core import fact_checker, summarize, to_english
from schemas import InputData

app = FastAPI(
    title="Newsful API",
    description="API for Newsful - a news summarization and fact checking app.",
    version="0.0.1",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    swagger_ui_oauth2_redirect_url="api/docs/oauth2-redirect",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

uri = str(os.environ.get("URI"))
client = MongoClient(uri)
db = client["newsful"]
collection = db["articles"]


@app.get("/api/health")
def health():
    """Health check endpoint."""

    db_is_working = False
    try:
        client.admin.command("ping")
        print("Pinged your deployment. You successfully connected to MongoDB!")
        db_is_working = True
    except Exception as e:
        print(e)

    return {"status": "ok", "database": db_is_working, "status_code": 200}


@app.get("/api/verify")
def give_this_crap_function_a_name(data: InputData):
    """Endpoint to verify a news article."""

    data.content = to_english(data.content)
    summary = summarize(data.content)
    new_data = InputData(url=data.url, content=summary)
    fact_check = fact_checker(collection, new_data)
    pass


@app.get("/api/summarize")
def summarize_text(text: str):
    """Endpoint to summarize a news article."""

    return {"summary": summarize(text)}
