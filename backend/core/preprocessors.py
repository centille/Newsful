from io import BytesIO

import instructor
import requests
import tiktoken
from deep_translator import GoogleTranslator  # type: ignore
from openai import AsyncOpenAI
from PIL import Image
from PIL.ImageFile import ImageFile

from core.utils import clean_text, split_to_words
from schemas import GPTGeneratedSummary


def to_english(text: str) -> str:  # type: ignore
    """translates text to english if it is not already in english."""
    translator = GoogleTranslator(source="auto", target="en")  # type: ignore
    text = translator.translate(text)  # type: ignore
    return clean_text(text)


def num_of_tokens(text: str) -> int:
    """calculates the number of tokens in a text."""
    tiktokens = tiktoken.encoding_for_model("gpt-4o-mini")
    return len(tiktokens.encode(text))


async def summarize(text: str) -> str:
    """summarizes the text via OpenAI."""
    if num_of_tokens(text) <= 200:
        return text
    client = instructor.from_openai(AsyncOpenAI())
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        response_model=GPTGeneratedSummary,
        messages=[
            {
                "role": "system",
                "content": "Generate a concise summary in the language of the article. ",
            },
            {
                "role": "user",
                "content": f"Summarize the following text in a concise way:\n{text}",
            },
        ],
    )  # type: ignore
    return response.summary


def is_government_related(text: str) -> bool:
    """checks if the text is related to the government."""
    words = split_to_words(text)
    gov_rel_words = (
        "india",
        "government",
        "indian",
        "state",
        "union",
        "president",
        "minister",
        "elections",
        "election",
        "congress",
    )
    return any(word in gov_rel_words for word in words)


def get_image(image_url: str) -> ImageFile:
    """fetches an image from a url and returns a PIL ImageFile."""
    response = requests.get(image_url, allow_redirects=True, timeout=15)
    response.raise_for_status()
    return Image.open(BytesIO(response.content))
