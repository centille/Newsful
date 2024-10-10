#!/usr/bin/env python
import os

import logfire
import pytesseract  # type: ignore
import requests
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI

from core import db_is_working, fact_check_process, get_image, summarize, to_english
from schemas import FactCheckResponse, HealthResponse, ImageInputData, TextInputData

# Load environment variables
load_dotenv()


# Global variables
ENV = os.environ.get("ENV", "dev")
DEBUG = ENV == "dev"
URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")

# FastAPI app
app = FastAPI(
    debug=DEBUG,
    title="Newsful API",
    description="API for Newsful - a news summarization and fact checking app.",
    version="0.1.0",
)

if not DEBUG:
    import warnings

    warnings.filterwarnings("ignore")

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


@app.get("/health/")
def health() -> HealthResponse:
    """Health check endpoint."""

    return HealthResponse(database_is_working=db_is_working(URI))


@app.post("/verify/text/")
async def verify_news(data: TextInputData) -> FactCheckResponse:
    """Endpoint to verify a news article."""

    data.content = await summarize(to_english(data.content))
    return await fact_check_process(data, URI, "text")


@app.post("/verify/image/")
async def image_check(data: ImageInputData) -> FactCheckResponse | bool:
    """Endpoint to check if an image is fake."""

    pytesseract.pytesseract.tesseract_cmd = os.environ.get("TESSERACT_PATH")

    pic_url_str = str(data.picture_url)
    response: requests.Response = requests.get(pic_url_str, allow_redirects=True, timeout=15)
    response.raise_for_status()
    image = get_image(pic_url_str)
    res = pytesseract.image_to_string(image)  # type: ignore
    assert isinstance(res, (str, bytes))
    text = res if isinstance(res, str) else res.decode("utf-8")
    text_data = TextInputData(
        url=data.url,
        content=text,
    )

    print(text_data.model_dump_json())
    return await fact_check_process(text_data, URI, "image")
