#!/usr/bin/env python
import os
from contextlib import asynccontextmanager

import logfire
import pytesseract  # type: ignore
import requests
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from groq import AsyncGroq
from openai import AsyncOpenAI
from pymongo import AsyncMongoClient

from core import add_to_db, db_is_working, fact_check_process, get_image, summarize, to_english
from schemas import FactCheckResponse, HealthResponse, ImageInputData, TextInputData

# Load environment variables
load_dotenv()


# Global variables
ENV = os.environ.get("ENV", "dev")
DEBUG = ENV == "dev"
URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")


oai_client = AsyncOpenAI()
groq_client = AsyncGroq()
mongo_client = AsyncMongoClient(URI)  # type: ignore


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages the lifespan of the FastAPI app."""
    print("Lifespan starting...")
    await mongo_client.aconnect()
    print("Lifespan started")
    yield
    print("Lifespan ending...")
    await mongo_client.aclose()
    print("Lifespan ended")


# FastAPI app
app = FastAPI(
    debug=DEBUG,
    title="Newsful API",
    description="API for Newsful - a news summarization and fact checking app.",
    version="0.1.0",
    lifespan=lifespan,
)

# FastAPI CORS
app.add_middleware(
    CORSMiddleware,
    allow_methods=["GET", "POST"],
    allow_origins=["*"],
    allow_headers=["*"],
)

# Logfire logging
logfire.configure()
logfire.instrument_fastapi(app, capture_headers=True, record_send_receive=True)
# logfire.instrument_openai(client)


@app.get("/health/")
async def health() -> HealthResponse:
    """Health check endpoint."""

    return HealthResponse(database_is_working=await db_is_working(mongo_client))  # type: ignore


@app.post("/verify/text/")
async def verify_news(data: TextInputData, background_tasks: BackgroundTasks) -> FactCheckResponse:
    """Endpoint to verify a news article."""

    data.content = await summarize(groq_client, to_english(data.content))
    fact_check, is_present_in_db = await fact_check_process(oai_client, groq_client, data, mongo_client, "text")  # type: ignore
    if not is_present_in_db:
        background_tasks.add_task(add_to_db, mongo_client, fact_check)  # type: ignore
    return fact_check


@app.post("/verify/image/")
async def image_check(data: ImageInputData, background_tasks: BackgroundTasks) -> FactCheckResponse:
    """Endpoint to check if an image is fake."""

    pytesseract.pytesseract.tesseract_cmd = os.environ.get("TESSERACT_PATH")

    pic_url_str = str(data.url)
    response = requests.get(pic_url_str, allow_redirects=True, timeout=15)
    response.raise_for_status()
    image = get_image(pic_url_str)
    res = pytesseract.image_to_string(image)  # type: ignore
    assert isinstance(res, (str, bytes))
    text = res if isinstance(res, str) else res.decode("utf-8")
    text_data = TextInputData(
        url=data.url,
        content=text,
    )

    fact_check, is_present_in_db = await fact_check_process(oai_client, groq_client, text_data, mongo_client, "image")  # type: ignore
    if not is_present_in_db:
        background_tasks.add_task(add_to_db, mongo_client, fact_check)  # type: ignore
    return fact_check
