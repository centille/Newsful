from typing import Union

import ujson
from pymongo import MongoClient
from pymongo.errors import PyMongoError

from schemas import FactCheckResponse, TextInputData


def db_is_working(uri: str):
    """Checks if the database is working."""
    try:
        client = MongoClient(uri)  # type: ignore
        assert client.admin.command("ping")["ok"] == 1  # type: ignore
        client.close()
        return True
    except (PyMongoError, AssertionError):
        return False


def add_to_db(uri: str, data: FactCheckResponse):
    """adds the Pydantic object to the mongo database"""

    # Add object to DB
    client = MongoClient(uri)  # type: ignore
    collection = client["newsful"]["articles"]  # type: ignore
    collection.insert_one(ujson.loads(data.model_dump_json()))  # type: ignore
    client.close()


def fetch_from_db_if_exists(
    uri: str,
    data: TextInputData,
) -> Union[FactCheckResponse, None]:
    """
    fetch_from_db_if_exists checks the data against the database.

    Parameters
    ----------
    uri : str
        The MongoDB connection string to be used.
    data : TextInputData
        The data to be checked.

    Returns
    -------
    FactCheckResponse | None
        The result of the fact check, if present. Otherwise, return None.
    """

    url = str(data.url or "")
    summary: str = data.content

    client = MongoClient(uri)  # type: ignore
    collection = client["newsful"]["articles"]  # type: ignore

    # fetch from database if exists
    res = collection.find_one({"url": url, "summary": summary})  # type: ignore
    client.close()

    if res is not None:
        return FactCheckResponse.model_validate(res)
    return None
