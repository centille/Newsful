#!/usr/bin/env python
import os
from contextlib import asynccontextmanager

import logfire
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from groq import AsyncGroq
from pymongo import AsyncMongoClient

from core import add_to_db, db_is_working, fact_check_process, summarize, to_english
from schemas import FactCheckResponse, HealthResponse, TextInputData

# Load environment variables
load_dotenv()


# Global variables
ENV = os.environ.get("ENV", "dev")
DEBUG = ENV == "dev"
URI = "mongodb://localhost:27017"


groq_client = AsyncGroq()
mongo_client = AsyncMongoClient(URI)  # type: ignore


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manages the lifespan of the FastAPI app."""
    print(f"Lifespan starting for {app.title}...")
    await mongo_client.aconnect()
    print("Lifespan started")
    yield
    print(f"Lifespan ending for {app.title}...")
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
    allow_methods=["*"],
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
    fact_check, is_present_in_db = await fact_check_process(groq_client, data, mongo_client, "text")  # type: ignore
    if not is_present_in_db:
        background_tasks.add_task(add_to_db, mongo_client, fact_check)  # type: ignore
    return fact_check
