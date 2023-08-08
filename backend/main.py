import io
import os
import warnings
from pprint import pprint
import pytesseract  # type: ignore
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo.mongo_client import MongoClient
import requests

from core import fact_check_process, get_image, summarize, to_english, fact_check_chat

# from core.image import image_is_true
from schemas import (
    Article,
    Health,
    ImageInputData,
    TextInputData,
    ChatTextInputData,
    ChatReply,
)

# Load environment variables
load_dotenv()
# Suppress warnings
warnings.filterwarnings("ignore")
# Global variables
DEBUG: bool = True
URI: str = str(os.environ.get("URI"))

# FastAPI app
app = FastAPI(
    title="Newsful API",
    description="API for Newsful - a news summarization and fact checking app.",
    version="0.0.1",
    debug=DEBUG,
    docs_url="/",
)

# FastAPI CORS
app.add_middleware(
    CORSMiddleware,
    allow_methods=["*"],
    allow_origins=["*"],
    allow_headers=["*"],
)


@app.get("/api/health/")
def health() -> Health:
    """Health check endpoint."""

    db_is_working = False
    client = MongoClient(URI)  # type: ignore
    if client.admin.command("ping")["ok"] == 1:  # type: ignore
        client.close()
        if DEBUG:
            print("Pinged your deployment. You successfully connected to MongoDB!")
        db_is_working = True
        return Health(status="ok", database=db_is_working, status_code=200)
    raise Exception("Unable to connect to the database.")


@app.get("/api/summarize/")
def summarize_text(text: str) -> dict[str, str]:
    """Endpoint to summarize a news article."""
    summary: str = summarize(text)
    if DEBUG:
        pprint(summary)
    return {"summary": summary}


@app.post("/api/verify/text/")
async def verify_news(data: TextInputData) -> Article:
    """Endpoint to verify a news article."""

    data.content = summarize(to_english(data.content))
    if DEBUG:
        pprint(dict(data))
    return fact_check_process(data, URI, "text", DEBUG)


@app.post("/api/verify/image/")
def image_check(data: ImageInputData) -> Article | bool:
    """Endpoint to check if an image is fake."""
    if DEBUG:
        pprint(dict(data))
    pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"  # type: ignore

    response: requests.Response = requests.get(data.picture_url, allow_redirects=True)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch image: {response.status_code}")
    image = get_image(data.picture_url)
    res: bytes | str | dict[str, bytes | str] = pytesseract.image_to_string(image)  # type: ignore
    if not isinstance(res, (str, bytes)):
        raise Exception("Unable to read image.")
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

    pprint(dict(text_data))
    return fact_check_process(text_data, URI, "image", DEBUG)


@app.post("/api/chat/text/")
async def chat_text(data: ChatTextInputData) -> ChatReply:
    data.content = summarize(to_english(data.content))
    if DEBUG:
        pprint(dict(data))
    return fact_check_chat(data, "text", DEBUG)
