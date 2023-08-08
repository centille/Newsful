import pickle
import socket
import ssl
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd
import whois  # type: ignore
from backports.ssl_match_hostname import match_hostname  # type: ignore
from langchain import GoogleSearchAPIWrapper
from pydantic import AnyHttpUrl
from waybackpy import WaybackMachineSaveAPI

from core.utils import get_domain


def is_phishing(url: AnyHttpUrl, debug: bool = False) -> bool:
    """
    is_phishing checks if the url is a phishing url.

    Parameters
    ----------
    url : AnyHttpUrl
        The url to be checked.
    debug : bool, optional
        Whether to print debug statements, by default False

    Returns
    -------
    bool
        True if the url is a phishing url, False otherwise.
    """

    domain: str = get_domain(url)
    if debug:
        print(f"Domain: {domain}")

    websites: pd.Series[str] = pd.read_csv("./assets/websites.csv")["hostname"]  # type: ignore
    if domain in websites:
        return False

    # check SSL certificate
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sslsock: ssl.SSLSocket = ssl.wrap_socket(sock, cert_reqs=ssl.CERT_REQUIRED)
        match_hostname(sslsock.getpeercert(), domain)
    except Exception as e:
        if debug:
            print(f"{e}: SOME SSL CRAP HAPPENED")
        return True

    w: Any = whois.whois(domain)  # type: ignore
    creation_date: datetime = w.creation_date[0] if isinstance(w.creation_date, list) else w.creation_date  # type: ignore
    if creation_date:
        today: datetime = datetime.today()
        if isinstance(creation_date, datetime):
            if (today - creation_date).days < 365:
                return True

    model = pickle.load(open("./models/model.pickle", "rb"))
    prediction: str = model.predict([url])
    if debug:
        print(f"Prediction: {prediction[0]}")
    return prediction[0] != "good"


def is_credible(url: AnyHttpUrl, is_phishing: bool, debug: bool = False) -> bool:
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

    domain: str = get_domain(url)
    if debug:
        print(f"Domain: {domain}")

    websites: pd.Series[str] = pd.read_csv("./assets/websites.csv")["hostname"]  # type: ignore
    if domain in websites:
        return False

    if not url.startswith("https://"):
        if debug:
            print("URL isn't HTTPS")
        return False

    safe_tlds: list[str] = [".gov", ".org", ".edu", ".gov.in"]
    if any(domain.endswith(tld) for tld in safe_tlds):
        if debug:
            print(f"Domain ends with {' or '.join(safe_tlds)}")
        return True

    if is_phishing:
        if debug:
            print(f"{domain} is a phishing URL")
        return False

    return True


def get_confidence(news: str, debug: bool = False) -> int:
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
    confidence = int(round(model._predict_proba_lr(tfidf_x)[0][1] * 100))
    if debug:
        print(f"Confidence: {confidence}%")
    return confidence


def archiveURL(url: AnyHttpUrl, debug: bool = False) -> str:
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

    user_agent = "Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Mobile/7B405"
    save_api = WaybackMachineSaveAPI(
        url=str(url),
        user_agent=user_agent,
        max_tries=12,
    )
    try:
        archive_url: str = save_api.save()
        if debug:
            print(f"Archived URL: {archive_url}")
        return archive_url
    except Exception:
        return url


def get_top_google_results(query: str, count: int = 5, debug: bool = False) -> list[AnyHttpUrl]:
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
    list[AnyHttpUrl]
        The list of top google search results for the given query.
    """

    google_search = GoogleSearchAPIWrapper(search_engine="google")
    results: List[Dict[str, Any]] = google_search.results(query, count)  # type: ignore
    result_links: list[AnyHttpUrl] = [result["link"] for result in results]
    if debug:
        print(f"Top {count} Google Search Results:")
        for i, link in enumerate(result_links, start=1):
            print(f"{i}) {link}")
    return result_links
