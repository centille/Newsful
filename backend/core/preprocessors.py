import pickle

import pandas as pd

from core.utils import get_domain


def isPhishing(url: str) -> bool:
    """
    isPhishing checks if the url is a phishing url.

    Parameters
    ----------
    url : str
        The url to be checked.

    Returns
    -------
    bool
        True if the url is a phishing url, False otherwise.
    """

    model = pickle.load(open("./assets/model.pkl", "rb"))
    prediction = model.predict([url])
    return prediction[0] == "good"


def isCredible(url: str) -> str:
    """
    isCredible checks if the url is a credible url.

    Parameters
    ----------
    url : str
        The url to be checked.

    Returns
    -------
    bool
        True if the url is a credible url, False otherwise.
    """

    domain = get_domain(url)
    df = pd.read_csv("assets/sources.csv", engine="pyarrow")
    row = df.loc[df["domain"] == domain]
    if row.empty:
        return isPhishing(url)
    return not any(
        [
            row["type1"].values[0] == "fake",
            row["type2"].values[0] == "fake",
            row["type3"].values[0] == "fake",
        ]
    )
