from urllib.parse import urlparse

from deep_translator import GoogleTranslator
from pydantic import AnyHttpUrl
from summarizer import Summarizer


def to_english(text: str) -> str:
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

    translator = GoogleTranslator(source="auto", target="en")
    text = translator.translate(text)
    return wordopt(text)


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
        The 3 sentence summary of the text.
    """

    model = Summarizer()
    if len(text) < 250 or len(text.split()) < 50:
        return text
    if len(text) < 1000:
        summary = model(text, num_sentences=4, algorithm="gmm")
    else:
        summary = model(text, ratio=0.25, algorithm="gmm")
    return summary


def wordopt(text: str) -> str:
    text = text.strip().replace("\n", " ").replace("\t", " ").replace("\r", " ")
    return text.rstrip(".")
