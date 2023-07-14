from urllib.parse import urlparse

from googletrans import Translator
from summarizer import Summarizer
from waybackpy import WaybackMachineSaveAPI

# from core.decorators import clean_text


def get_domain(url: str) -> str:
    """
    get_domain returns the domain of the url.

    Parameters
    ----------
    url : str
        The url to be checked.

    Returns
    -------
    str
        The domain of the url.
    """

    return urlparse(url).netloc


# @clean_text
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

    translator = Translator()
    if translator.detect(text).lang == "en":
        return text
    obj = translator.translate(text)
    return obj.text


# @clean_text
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
    summary = model(text, num_sentences=3)
    return summary


def archiveURL(url: str) -> str:
    """
    archiveURL returns the archive url of given url

    Parameters
    ----------
    url : str
        The url to be archived.

    Returns
    -------
    str
        The archive url of the given url.
    """

    user_agent = "Mozilla/5.0 (Windows NT 5.1; rv:40.0) Gecko/20100101 Firefox/40.0"
    save_api = WaybackMachineSaveAPI(url, user_agent)
    return save_api.save()
