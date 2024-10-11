from typing import Union

import ujson
from pymongo import AsyncMongoClient
from pymongo.errors import PyMongoError

from schemas import FactCheckResponse, TextInputData


async def db_is_working(uri: str):
    """Checks if the database is working."""
    try:
        client = AsyncMongoClient(uri)  # type: ignore
        assert await client.admin.command("ping")["ok"] == 1  # type: ignore
        await client.close()
        return True
    except (PyMongoError, AssertionError):
        return False


async def add_to_db(uri: str, data: FactCheckResponse):
    """adds the Pydantic object to the mongo database"""

    try:
        # Add object to DB
        client = AsyncMongoClient(uri)  # type: ignore
        collection = client["newsful"]["articles"]  # type: ignore
        await collection.insert_one(ujson.loads(data.model_dump_json()))  # type: ignore
        await client.close()
    except PyMongoError:
        pass


async def fetch_from_db_if_exists(
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

    client = AsyncMongoClient(uri)  # type: ignore
    collection = client["newsful"]["articles"]  # type: ignore

    # fetch from database if exists
    res = await collection.find_one({"url": url, "summary": summary})  # type: ignore
    await client.close()

    if res is not None:
        return FactCheckResponse.model_validate(res)
    return None
