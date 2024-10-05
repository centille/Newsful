import io
import os
import warnings

import pytesseract  # type: ignore
import requests
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo.errors import PyMongoError
from pymongo.mongo_client import MongoClient

from core import fact_check_process, get_image, summarize, to_english
from schemas import FactCheckResponse, HealthResponse, ImageInputData, TextInputData

# Load environment variables
load_dotenv()

# Suppress warnings
warnings.filterwarnings("ignore")

# Global variables
DEBUG: bool = True
URI: str = str(os.environ.get("MONGO_URI"))

# FastAPI app
app = FastAPI(
    debug=DEBUG,
    title="Newsful API",
    description="API for Newsful - a news summarization and fact checking app.",
    summary=open("./README.md", "r", encoding="utf-8").read(),
    version="0.0.1",
)

# FastAPI CORS
app.add_middleware(
    CORSMiddleware,
    allow_methods=["*"],
    allow_origins=["*"],
    allow_headers=["*"],
)


@app.get("/health/")
def health() -> HealthResponse:
    """Health check endpoint."""

    client = MongoClient(URI)  # type: ignore
    try:
        client.admin.command("ping")  # type: ignore
        client.close()
        db_is_working = True
        if DEBUG:
            print("Pinged your deployment. You successfully connected to MongoDB!")
    except PyMongoError as e:
        db_is_working = False
        if DEBUG:
            print(f"Mongo error: {e}. Check if MongoDB is running.")
    return HealthResponse(database_is_working=db_is_working)


@app.post("/verify/text/")
async def verify_news(data: TextInputData) -> FactCheckResponse:
    """Endpoint to verify a news article."""

    data.content = await summarize(to_english(data.content))
    if DEBUG:
        print(data.model_dump_json())
    return await fact_check_process(data, URI, "text", DEBUG)


@app.post("/verify/image/")
async def image_check(data: ImageInputData) -> FactCheckResponse | bool:
    """Endpoint to check if an image is fake."""
    if DEBUG:
        print(data.model_dump_json())
    pytesseract.pytesseract.tesseract_cmd = os.environ.get("TESSERACT_PATH")

    pic_url_str = str(data.picture_url)
    response: requests.Response = requests.get(pic_url_str, allow_redirects=True, timeout=15)
    response.raise_for_status()
    image = get_image(pic_url_str)
    res: bytes | str | dict[str, bytes | str] = pytesseract.image_to_string(image)  # type: ignore
    assert isinstance(res, (str, bytes))
    text: str = res if isinstance(res, str) else str(res)
    if DEBUG:
        print(f"{text=}")

    if len(text) < 10:
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="PNG")
        image_bytes = image_bytes.getvalue()
        raise NotImplementedError("Image is not supported yet.")
    text_data = TextInputData(
        url=data.url,
        content=text,
    )

    print(text_data.model_dump_json())
    return await fact_check_process(text_data, URI, "image", DEBUG)
