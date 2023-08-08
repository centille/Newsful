from io import BytesIO
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator  # type: ignore
from PIL import Image
from pydantic import AnyHttpUrl
from summarizer import Summarizer  # type: ignore


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
    translator: GoogleTranslator = GoogleTranslator(source="auto", target="en")
    text: str = translator.translate(text)  # type: ignore
    return clean_text(text)


def get_domain(url: AnyHttpUrl) -> str:
    """
    get_domain returns the domain of the url.

    Parameters
    ----------
    url : AnyHttpUrl
        The url to be checked.

    Returns
    -------
    str
        The domain of the url.
    """
    return urlparse(str(url)).netloc


def summarize(text: str) -> str:
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
    if len(text) < 250 or len(text.split()) < 50:
        return text
    model = Summarizer()
    if len(text) < 1000:
        return model(text, num_sentences=4, use_first=True)
    return model(text, ratio=0.25, use_first=True)


def clean_text(text: str) -> str:
    """
    clean_text cleans text.

    Parameters
    ----------
    text : str
        The text to be optimized.

    Returns
    -------
    str
        The optimized text.
    """
    return text.strip().replace("\n", " ").replace("\t", " ").replace("\r", " ").rstrip(".")


def get_image(image_url: str):
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

    response: requests.Response = requests.get(image_url, allow_redirects=True)
    if response.status_code == 200:
        image_content: bytes = response.content
        return Image.open(BytesIO(image_content))
    raise Exception(f"Failed to fetch image: {response.status_code}")


def extract_text_from_url(url: str) -> str:
    try:
        response: requests.Response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        text: str = soup.get_text()
        return text
    except requests.exceptions.RequestException:
        return ""
