from typing import Union

from pymongo import MongoClient

from schemas import FactCheckResponse, TextInputData


def add_to_db(uri: str, data: FactCheckResponse):
    """
    add_to_db calculates all the necessary details and adds the data to the database.

    Parameters
    ----------
    uri: str
        The connection string to the MongoDB database.
    data : FactCheckResponse
        The data to be added to the database.
    debug : bool
        Whether to print debug statements or not.

    Returns
    -------
    FactCheckResponse
        The data that was added to the database.
    """

    # Add object to DB
    client = MongoClient(uri)  # type: ignore
    collection = client["NewsFul"]["articles"]  # type: ignore
    collection.insert_one(data.model_dump())  # type: ignore
    client.close()


def fetch_from_db_if_exists(
    uri: str,
    data: TextInputData,
) -> Union[FactCheckResponse, None]:
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
    FactCheckResponse
        The result of the fact check.
    bool
        Whether the data was found in the database.
    """

    url = data.url
    summary: str = data.content

    # check if connection is working
    client = MongoClient(uri)  # type: ignore
    collection = client["NewsFul"]["articles"]  # type: ignore
    assert client.admin.command("ping")["ok"] == 1  # type: ignore

    # fetch from database if exists
    res = collection.find_one({"url": url, "summary": summary})  # type: ignore
    client.close()

    if res is not None:
        return FactCheckResponse.model_validate(res)
    return None
