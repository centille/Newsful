from typing import List
from deep_translator import GoogleTranslator
from langchain import GoogleSearchAPIWrapper
from pydantic import AnyHttpUrl
from summarizer import Summarizer
from textblob import TextBlob
from waybackpy import WaybackMachineSaveAPI


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

    text = text.strip().replace("\n", " ").replace("\t", " ")
    translator = GoogleTranslator(source="auto", target="en")
    return translator.translate(text)


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
    if len(text) < 1000:
        summary = model(text, num_sentences=4, algorithm="gmm")
    else:
        summary = model(text, ratio=0.25, algorithm="gmm")
    return summary


def archiveURL(url: AnyHttpUrl) -> str:
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

    user_agent = "Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Mobile/7B405"
    save_api = WaybackMachineSaveAPI(
        url=str(url),
        user_agent=user_agent,
        max_tries=12,
    )
    archive_url = save_api.save()
    return archive_url


def get_polarity(text: str) -> float:
    return TextBlob(text).polarity  # type: ignore


def get_top_5_google_results(query: str) -> List[AnyHttpUrl]:
    """Get top 5 google results for a query."""
    google_search = GoogleSearchAPIWrapper(search_engine="google")
    results = google_search.results(query, 5)
    return [result["link"] for result in results]
