from io import BytesIO

import requests
from deep_translator import GoogleTranslator  # type: ignore
from openai import AsyncOpenAI
from PIL import Image
from PIL.ImageFile import ImageFile

from core.utils import clean_text, split_to_words


def to_english(text: str) -> str:  # type: ignore
    """
    to_english translates text to english if it is not already in english.

    Parameters
    ----------
    text : str
        The text to be translated.

    Returns
    -------
    str
        The text translated to english.
    """
    translator: GoogleTranslator = GoogleTranslator(source="auto", target="en")  # type: ignore
    text: str = translator.translate(text)  # type: ignore
    return clean_text(text)  # type: ignore


async def summarize(text: str) -> str:
    """
    summarize summarizes text.

    Parameters
    ----------
    text : str
        The text to be summarized.

    Returns
    -------
    str
        The summary of the text.
    """
    if len(text) < 200:
        return text
    client = AsyncOpenAI()
    res = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Summarize this conent without adding any context: {text}"}],
        max_tokens=500,
        temperature=0,
    )
    return str(res.choices[0].message.content) if res.choices[0].message else ""


def is_government_related(text: str) -> bool:
    """
    is_government_related checks if the text is related to the government.

    Parameters
    ----------
    text : str
        The text to be checked.

    Returns
    -------
    bool
        True if the text is related to the government, False otherwise.
    """
    words: list[str] = split_to_words(text)
    gov_rel_words: list[str] = ["india", "government", "indian"]
    for word in words:
        if word in gov_rel_words:
            return True
    return False


def get_image(image_url: str) -> ImageFile:
    """
    get_image fetches an image from a url.

    Parameters
    ----------
    image_url : str
        The url of the image.

    Returns
    -------
    PIL.Image
        The image fetched from the url.

    Raises
    ------
    Exception
        Raised if the image could not be fetched.
    """

    response: requests.Response = requests.get(image_url, allow_redirects=True, timeout=15)
    response.raise_for_status()
    image_content: bytes = response.content
    return Image.open(BytesIO(image_content))
