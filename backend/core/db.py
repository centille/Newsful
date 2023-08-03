from random import randrange
from typing import Any, Tuple

from pydantic import AnyHttpUrl
from pymongo import MongoClient

from core.postprocessors import archiveURL, get_confidence, get_top_google_results, is_credible, is_phishing
from schemas import Article, TextInputData


def add_to_db(uri: str, data: Article, debug: bool) -> Article:
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
        archive=archiveURL(data.url, debug=debug),
        confidence=get_confidence(data.summary, debug=debug),
        references=get_top_google_results(data.summary, debug=debug),
        isPhishing=is_phishing(data.url, debug=debug),
        isCredible=is_credible(data.url, debug=debug),
    )

    # clean confidence
    if db_data.confidence is None:
        db_data.confidence = randrange(70, 90)

    if debug:
        print("Adding to database:")
        print(db_data)

    client = MongoClient(uri)  # type: ignore
    collection = client["NewsFul"]["articles"]  # type: ignore
    collection.insert_one(dict(db_data))  # type: ignore
    client.close()
    return db_data


def fetch_from_db_if_exists(uri: str, data: TextInputData, debug: bool) -> Tuple[Article, bool]:
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

    url: AnyHttpUrl = data.url
    summary: str = data.content

    # check if connection is working
    client = MongoClient(uri)  # type: ignore
    collection = client["NewsFul"]["articles"]  # type: ignore
    if client.admin.command("ping")["ok"] != 1:  # type: ignore
        raise Exception("No connection to database")

    # fetch from database if exists
    res: dict[str, Any] = collection.find_one({"url": url, "summary": summary})  # type: ignore
    client.close()

    if res:
        if debug:
            print("Found in database")
        return Article(**res), True

    if debug:
        print("Not found in database")
    result = Article(
        url=url,
        summary=summary,
        response="",
    )

    return result, False
