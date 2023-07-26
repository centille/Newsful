import pickle
from typing import List

import pandas as pd
from langchain import GoogleSearchAPIWrapper
from pydantic import AnyHttpUrl
from waybackpy import WaybackMachineSaveAPI

from core.utils import get_domain


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

    model = pickle.load(open("./models/model.pkl", "rb"))
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


def get_confidence(news: str) -> int:
    model = pickle.load(open("./models/PA.pickle", "rb"))
    vectorizer = pickle.load(open("./models/tfidf_vectorizer.pickle", "rb"))
    tfidf_x = vectorizer.transform([news])
    confidence = round(model._predict_proba_lr(tfidf_x)[0][1] * 100)
    return confidence


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


def get_top_5_google_results(query: str) -> List[AnyHttpUrl]:
    """Get top 5 google results for a query."""
    google_search = GoogleSearchAPIWrapper(search_engine="google")
    results = google_search.results(query, 5)
    return [result["link"] for result in results]
