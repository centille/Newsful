from typing import Any, Dict, List

import pandas as pd
from langchain_google_community import GoogleSearchAPIWrapper  # type: ignore
from pydantic import AnyHttpUrl
from waybackpy import WaybackMachineSaveAPI
from waybackpy.exceptions import MaximumSaveRetriesExceeded

from core.utils import get_domain


def is_phishing(url: AnyHttpUrl) -> bool:
    """checks if the url is a phishing url."""

    domain = get_domain(url)

    websites = pd.read_csv("./assets/websites.csv")["hostname"]  # type: ignore
    if domain in websites:
        return False

    if not str(url).startswith("https://"):
        return False

    safe_tlds = (".gov", ".org", ".edu", ".gov.in")
    return not domain.endswith(safe_tlds)


def is_credible(url: AnyHttpUrl) -> bool:
    """checks if the url is a credible url."""

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
    """Checks is the URL is credible and not a phishing URL."""
    return not is_phishing(url) and is_credible(url)


def archive_url(url: AnyHttpUrl, debug: bool = False) -> str | None:
    """returns the archive url of given url"""

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


def get_top_google_results(query: str, count: int = 5) -> list[AnyHttpUrl]:
    """returns the top google search results for the given query."""

    google_search = GoogleSearchAPIWrapper(search_engine="google")
    results: List[Dict[str, Any]] = google_search.results(query, count)  # type: ignore
    result_links = [result["link"] for result in results]
    return result_links
