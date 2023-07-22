import re
import string
import pickle
from urllib.parse import urlparse

import pandas as pd
from pydantic import AnyHttpUrl


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


def isPhishing(url: AnyHttpUrl) -> bool:
    """
    isPhishing checks if the url is a phishing url.

    Parameters
    ----------
    url : AnyHttpUrl
        The url to be checked.

    Returns
    -------
    bool
        True if the url is a phishing url, False otherwise.
    """

    model = pickle.load(open("./assets/model.pkl", "rb"))
    prediction = model.predict([url])
    return prediction[0] == "good"


def isCredible(url: AnyHttpUrl) -> bool:
    """
    isCredible checks if the url is a credible url.

    Parameters
    ----------
    url : AnyHttpUrl
        The url to be checked.

    Returns
    -------
    bool
        True if the url is a credible url, False otherwise.
    """

    domain = get_domain(url)
    df: pd.DataFrame = pd.read_csv("assets/sources.csv", engine="pyarrow")[["domain"]]
    row = df.loc[df["domain"] == domain]
    if row.empty:
        return isPhishing(url)
    return "fake" not in [
        str(row["type1"]).lower(),
        str(row["type2"]).lower(),
        str(row["type3"]).lower(),
    ]


def wordopt(text: str) -> str:
    text = text.lower()
    text = re.sub("\[.*?\]", "", text)
    text = re.sub("\\W", " ", text)
    text = re.sub("https?://\S+|www\.\S+", "", text)
    text = re.sub("<.*?>+", "", text)
    text = re.sub("[%s]" % re.escape(string.punctuation), "", text)
    text = re.sub("\n", "", text)
    text = re.sub("\w*\d\w*", "", text)
    return text
