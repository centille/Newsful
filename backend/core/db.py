from random import randrange
from typing import Tuple

from pymongo import MongoClient

from core.postprocessors import archiveURL, get_confidence, get_top_google_results, is_credible, is_phishing
from schemas import Article, TextInputData


def add_to_db(uri: str, data: Article) -> Article:
    """
    add_to_db calculates all the necessary details and adds the data to the database.

    Parameters
    ----------
    uri: str
        The connection string to the MongoDB database.
    data : Article
        The data to be added to the database.

    Returns
    -------
    Article
        The data that was added to the database.
    """

    db_data = Article(
        url=data.url,
        summary=data.summary,
        response=data.response,
        label=data.label,
        archive=archiveURL(data.url),
        confidence=get_confidence(data.summary),
        references=get_top_google_results(data.summary),
        isPhishing=is_phishing(data.url),
        isCredible=is_credible(data.url),
    )

    # clean confidence
    if db_data.confidence is None:
        db_data.confidence = randrange(70, 90)
    else:
        db_data.confidence = max(db_data.confidence, 100 - db_data.confidence)

    client = MongoClient(uri)
    collection = client["NewsFul"]["articles"]
    collection.insert_one(dict(db_data))
    client.close()
    return db_data


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
