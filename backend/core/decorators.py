import re


def clean_text(text: str) -> str:
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

    text = re.sub(r"\n", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()
