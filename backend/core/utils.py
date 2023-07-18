from googletrans import Translator
from pydantic import AnyHttpUrl
from summarizer import Summarizer
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

    translator = Translator()
    if translator.detect(text).lang == "en":
        return text
    obj = translator.translate(text)
    return obj.text


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
    summary = model(text, ratio=0.25, use_first=False)
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
