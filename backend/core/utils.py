from googletrans import Translator
from summarizer import Summarizer

from core.decorators import clean_text


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


@clean_text
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
