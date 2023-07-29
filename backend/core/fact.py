from typing import Tuple

from schemas import Article, InputData


def fetch_from_db_if_exists(collection, data: InputData) -> Tuple[Article, bool]:
    """
    fact_checker checks the data against the database.

    Parameters
    ----------
    conn : mongoDB Collection
        The MongoDB Collection to be used.
    data : InputData
        The data to be checked.

    Returns
    -------
    Article
        The result of the fact check.
    bool
        Whether the data was found in the database.
    """
    url = data.url
    summary = data.content

    res = collection.find_one({"url": url, "summary": summary})
    if res:
        return Article(**res), True

    result = Article(
        url=url,
        summary=summary,
        response="",
    )

    return result, False
