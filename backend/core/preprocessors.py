from deep_translator import GoogleTranslator  # type: ignore
from PIL import Image
from summarizer import Summarizer  # type: ignore
import requests
from io import BytesIO

from core.utils import tokenize
from core.utils import clean_text


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


def is_government_related(text: str) -> bool:
    words: list[str] = tokenize(text)
    gov_rel_words: list[str] = ["india", "government", "indian"]
    for word in words:
        if word in gov_rel_words:
            return True
    return False


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
