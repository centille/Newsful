from typing import Any, Dict, List

import pandas as pd
from langchain_google_community import GoogleSearchAPIWrapper
from pydantic import AnyHttpUrl
from waybackpy import WaybackMachineSaveAPI
from waybackpy.exceptions import MaximumSaveRetriesExceeded

from core.utils import get_domain


def is_phishing(url: AnyHttpUrl) -> bool:
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

    domain = get_domain(url)

    websites = pd.read_csv("./assets/websites.csv")["hostname"]  # type: ignore
    if domain in websites:
        return False

    if not str(url).startswith("https://"):
        return False

    safe_tlds: list[str] = [".gov", ".org", ".edu", ".gov.in"]
    if domain.endswith(tuple(safe_tlds)):
        return False
    return True


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

    domain = get_domain(url)

    websites = pd.read_csv("./assets/websites.csv", usecols=["hostname"])  # type: ignore
    if websites.hostname.str.contains(domain).any(bool_only=True):  # type: ignore
        return False

    if not str(url).startswith("https://"):
        return False

    safe_tlds: list[str] = [".gov", ".org", ".edu", ".gov.in"]
    if any(domain.endswith(tld) for tld in safe_tlds):
        return True
    return is_phishing(url)


def is_safe(url: AnyHttpUrl) -> bool:
    """
    is_safe Checks is the URL is credible and not a phishing URL.

    Parameters
    ----------
    url : AnyHttpUrl
        The url to be checked.
    debug : bool, optional
        Whether to print debug statements, by default False

    Returns
    -------
    bool
        True if the url is safe, False otherwise.
    """
    return not is_phishing(url) and is_credible(url)


def archiveURL(url: AnyHttpUrl, debug: bool = False) -> str | None:
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
    except MaximumSaveRetriesExceeded:
        return None


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
