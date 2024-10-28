from io import BytesIO

import instructor
import requests
import tiktoken
from deep_translator.google import GoogleTranslator  # type: ignore
from groq import AsyncGroq
from PIL import Image
from PIL.ImageFile import ImageFile

from core.utils import clean_text
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


async def summarize(client: AsyncGroq, text: str) -> str:
    """summarizes the text via Groq."""
    if num_of_tokens(text) <= 200:
        return text
    try:
        # client_ = instructor.from_openai(client)
        client_ = instructor.from_groq(client)
        response = await client_.chat.completions.create(
            model="llama-3.1-8b-instant",
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
        )
        assert isinstance(response, GPTGeneratedSummary)
        return response.summary
    except AssertionError:
        return text


def get_image(image_url: str) -> ImageFile:
    """fetches an image from a url and returns a PIL ImageFile."""
    response = requests.get(image_url, allow_redirects=True, timeout=15)
    response.raise_for_status()
    return Image.open(BytesIO(response.content))
