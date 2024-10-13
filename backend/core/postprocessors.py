import pandas as pd
from pydantic import AnyHttpUrl
from waybackpy import WaybackMachineSaveAPI
from waybackpy.exceptions import MaximumSaveRetriesExceeded

from core.utils import get_domain


def is_safe(url: AnyHttpUrl) -> bool:
    """checks if the url is a phishing url."""

    domain = get_domain(url)

    websites = pd.read_csv("./assets/websites.csv")["hostname"]  # type: ignore
    if domain in websites:
        return True

    if not str(url).startswith("https://"):
        return False

    safe_tlds = (".gov", ".org", ".edu", ".gov.in")
    return domain.endswith(safe_tlds)


def archive_url(url: AnyHttpUrl) -> str | None:
    """returns the archive url of given url"""

    user_agent = "Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Mobile/7B405"
    save_api = WaybackMachineSaveAPI(
        url=str(url),
        user_agent=user_agent,
        max_tries=5,
    )
    try:
        return save_api.save()
    except MaximumSaveRetriesExceeded:
        return None
