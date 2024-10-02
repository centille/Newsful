from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from pydantic import AnyHttpUrl


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


def split_to_words(text: str) -> list[str]:
    """
    split_to_words A custom tokenizer.

    Parameters
    ----------
    text : str
        The text to be tokenized.

    Returns
    -------
    list[str]
        The tokenized text.
    """

    tokens: list[str] = []
    token = ""
    for char in text:
        if char.isalnum():
            token += char
        elif char.isspace() and len(token) > 1:
            tokens.append(token.lower())
            token = ""
    return tokens


def extract_text_from_url(url: str) -> str:
    """
    extract_text_from_url extracts text from a url.

    Parameters
    ----------
    url : str
        The url to be extracted.

    Returns
    -------
    str
        The extracted text.
    """
    try:
        response: requests.Response = requests.get(url, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        text: str = soup.get_text()
        return text
    except requests.exceptions.RequestException:
        return ""


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
