import pickle
from datetime import datetime
from typing import List

import pandas as pd
import requests
from bs4 import BeautifulSoup
from langchain import GoogleSearchAPIWrapper
from pydantic import AnyHttpUrl
from waybackpy import WaybackMachineSaveAPI

from core.utils import get_domain


def is_phishing(url: AnyHttpUrl) -> bool:
    """
    is_phishing checks if the url is a phishing url.

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


def is_credible(url: AnyHttpUrl) -> bool:
    """
    is_credible checks if the url is a credible url.

    Parameters
    ----------
    url : AnyHttpUrl
        The url to be checked.

    Returns
    -------
    bool
        True if the url is a credible url, False otherwise.

    Reference
    ---------
    - https://www.microsoft.com/en-us/edge/learning-center/how-to-tell-if-a-site-is-credible
    - https://www.thoughtco.com/gauging-website-reliability-2073838
    """

    if url.startswith("http://"):
        return False

    domain = get_domain(url)
    domain_without_subdomain = ".".join(domain.split(".")[-2:])
    try:
        req = requests.get(f"https://who.is/whois/{domain_without_subdomain}")
        soup = BeautifulSoup(req.text, "html.parser")
        registry_data = soup.find_all("div", {"class": "row queryResponseBodyRow"})
        if registry_data is not None:
            for i in registry_data:
                if i.find("div", {"class": "col-md-4 queryResponseBodyKey"}).text == "Registered On":
                    date_str = i.find("div", {"class": "col-md-8 queryResponseBodyValue"}).text
                    date = datetime.strptime(date_str, "%Y-%m-%d")
                    # if domain is registered in past 500 days, it is not credible
                    if (datetime.now() - date).days < 500:
                        return False
    except Exception:
        pass

    safe_tlds = [".com", ".gov", ".org", ".edu", ".gov.in"]
    if any(domain.endswith(tld) for tld in safe_tlds):
        return True

    unsafe_tlds = [".info", ".biz", ".online", ".site"]
    if any(domain.endswith(tld) for tld in unsafe_tlds):
        return False

    unreliable_domains = pd.read_parquet("./data/sources.parquet", engine="fastparquet")["domain"].tolist()
    return domain not in unreliable_domains


def get_confidence(news: str) -> int:
    """
    get_confidence returns the confidence of the news being fake.

    Parameters
    ----------
    news : str
        The news to be checked.

    Returns
    -------
    int
        The confidence of the news being fake.
    """

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
        The archive url of the given url. If the url is not archived, the original url is returned.
    """

    try:
        user_agent = "Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Mobile/7B405"
        save_api = WaybackMachineSaveAPI(
            url=str(url),
            user_agent=user_agent,
            max_tries=12,
        )
        archive_url = save_api.save()
        return archive_url
    except Exception:
        return url


def get_top_google_results(query: str, count: int = 5) -> List[AnyHttpUrl]:
    """
    get_top_google_results returns the top google search results for the given query.

    Parameters
    ----------
    query : str
        The query to be searched.
    count : int, optional
        The number of results to be returned, by default 5

    Returns
    -------
    List[AnyHttpUrl]
        The list of top google search results for the given query.
    """
    try:
        google_search = GoogleSearchAPIWrapper(search_engine="google")
        results = google_search.results(query, count)
        return [result["link"] for result in results]
    except Exception:
        return get_top_google_results(query, count - 1)
