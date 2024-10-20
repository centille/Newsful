from urllib.parse import urlparse

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
    return " ".join(text.split()).rstrip(".")


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
