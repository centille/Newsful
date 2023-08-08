from typing import Any, Literal, Tuple

from pydantic import AnyHttpUrl
from pymongo import MongoClient

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
    debug : bool
        Whether to print debug statements or not.

    Returns
    -------
    Article
        The data that was added to the database.
    """

    # Print object being added to DB
    if debug:
        print("Adding to database:")
        print(data)

    # Add object to DB
    client = MongoClient(uri)  # type: ignore
    collection = client["NewsFul"]["articles"]  # type: ignore
    collection.insert_one(dict(data))  # type: ignore
    client.close()
    return data


def fetch_from_db_if_exists(
    uri: str, data: TextInputData, dtype: Literal["image", "text"], debug: bool
) -> Tuple[Article, bool]:
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
    res: dict[str, Any] | None = collection.find_one({"url": url, "summary": summary})  # type: ignore
    client.close()

    if res is not None:
        if debug:
            print("Found in database")
        return Article(**res), True  # type: ignore

    if debug:
        print("Not found in database")
    result = Article(url=url, summary=summary, response="", dataType=dtype)

    return result, False
