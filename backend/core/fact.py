from typing import Tuple

from pymongo import MongoClient

from schemas import Article, TextInputData


def fetch_from_db_if_exists(uri: str, data: TextInputData) -> Tuple[Article, bool]:
    """
    fact_checker checks the data against the database.

    Parameters
    ----------
    uri : str
        The MongoDB connection string to be used.
    data : TextInputData
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

    # check if connection is working
    client = MongoClient(uri)
    collection = client["NewsFul"]["articles"]
    if client.admin.command("ping")["ok"] != 1:
        raise Exception("No connection to database")

    # fetch from database if exists
    res = collection.find_one({"url": url, "summary": summary})
    client.close()

    if res:
        return Article(**res), True

    result = Article(
        url=url,
        summary=summary,
        response="",
    )

    return result, False
