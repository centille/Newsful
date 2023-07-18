import re

from pydantic import AnyHttpUrl


def clean_text(text: AnyHttpUrl) -> str:
    """
    clean_text cleans the text by removing extra spaces and newlines.

    Parameters
    ----------
    text : str
        The text to be cleaned.

    Returns
    -------
    str
        The cleaned text.
    """

    crap = str(text)
    crap = re.sub(r"\n", " ", crap)
    crap = re.sub(r"\s+", " ", crap)
    return crap.strip()
