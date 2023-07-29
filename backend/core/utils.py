from pydantic import AnyHttpUrl


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
    from deep_translator import GoogleTranslator

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
    from urllib.parse import urlparse

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
    from summarizer import Summarizer

    model = Summarizer()
    if len(text) < 250 or len(text.split()) < 50:
        return text
    if len(text) < 1000:
        summary = model(text, num_sentences=4)
    else:
        summary = model(text, ratio=0.25)
    return summary


def wordopt(text: str) -> str:
    """
    wordopt optimizes text.

    Parameters
    ----------
    text : str
        The text to be optimized.

    Returns
    -------
    str
        The optimized text.
    """
    text = text.strip().replace("\n", " ").replace("\t", " ").replace("\r", " ")
    return text.rstrip(".")
