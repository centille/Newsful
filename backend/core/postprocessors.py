import pandas as pd

from pydantic import AnyHttpUrl

import requests
from waybackpy import WaybackMachineSaveAPI
from waybackpy.exceptions import MaximumSaveRetriesExceeded


def is_safe(url: AnyHttpUrl) -> bool:
    """checks if the url is a phishing url."""

    # check is the url is a homographic url
    host = url.host
    unicode_host = url.unicode_host()
    if host != unicode_host or host is None:
        return False

    # check if the url is a https url
    if url.scheme != "https":
        return False

    # check if the url is a very popular website
    websites = pd.read_csv("./assets/websites.csv")["hostname"]  # type: ignore
    if host in websites:
        return True

    # check if the url is a safe tld
    safe_tlds = (".gov", ".org", ".edu", ".gov.in")
    return host.endswith(safe_tlds)


def archive_url(url: AnyHttpUrl) -> str | None:
    """returns the archive url of given url"""

    try:
        user_agent = "Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Mobile/7B405"
        save_api = WaybackMachineSaveAPI(
            url=str(url),
            user_agent=user_agent,
            max_tries=3,
        )
        return save_api.save()
    except (MaximumSaveRetriesExceeded, requests.exceptions.RetryError):
        return str(url)
