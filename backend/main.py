import json
import os
import warnings
from datetime import datetime
from pprint import pprint

import pytesseract
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain.agents import AgentType, initialize_agent, load_tools
from langchain.llms import OpenAI
from PIL import Image
from pymongo.mongo_client import MongoClient

from core import add_to_db, fact_check_process, fact_check_this, fetch_from_db_if_exists, summarize, to_english
from schemas import Article, Health, ImageInputData, TextInputData

# FastAPI app
app = FastAPI(
    title="Newsful API",
    description="API for Newsful - a news summarization and fact checking app.",
    version="0.0.1",
)

# FastAPI CORS
app.add_middleware(
    CORSMiddleware,
    allow_methods=["*"],
    allow_origins=["*"],
    allow_headers=["*"],
)

# Load environment variables
load_dotenv()
URI = str(os.environ.get("URI"))
# Suppress warnings
warnings.filterwarnings("ignore")
# Global variables
DEBUG = True


@app.get("/api/health/")
def health() -> Health:
    """Health check endpoint."""

    db_is_working = False
    client = MongoClient(URI)
    if client.admin.command("ping")["ok"] == 1:
        client.close()
        if DEBUG:
            print("Pinged your deployment. You successfully connected to MongoDB!")
        db_is_working = True
        return Health(status="ok", database=db_is_working, status_code=200)
    raise Exception("Unable to connect to the database.")


@app.get("/api/summarize/")
def summarize_text(text: str):
    """Endpoint to summarize a news article."""
    summary = summarize(text)
    if DEBUG:
        pprint(summary, width=120)
    return {"summary": summary}


@app.post("/api/verify/text/")
async def verify_news(data: TextInputData) -> Article:
    """Endpoint to verify a news article."""

    data.content = summarize(to_english(data.content))
    return fact_check_process(data, URI, DEBUG)


@app.post("/api/verify/image/")
def image_check(data: ImageInputData):
    """Endpoint to check if an image is fake."""
    if DEBUG:
        pprint(dict(data))
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    image = Image.open(data.picture_url)
    text_data = TextInputData(
        url=data.url,
        content=pytesseract.image_to_string(image),
    )
    return fact_check_process(text_data, URI, DEBUG)
