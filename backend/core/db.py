from typing import Union

import ujson
from pymongo import AsyncMongoClient
from pymongo.errors import PyMongoError

from schemas import FactCheckResponse, TextInputData


async def db_is_working(client: AsyncMongoClient):
    """Checks if the database is working."""

    try:
        return (await client["newsful"].command("ping"))["ok"] == 1  # type: ignore
    except PyMongoError:
        return False


async def add_to_db(client: AsyncMongoClient, data: FactCheckResponse):
    """adds the Pydantic object to the mongo database"""

    try:
        # Add object to DB
        collection = client["newsful"]["articles"]  # type: ignore
        await collection.insert_one(ujson.loads(data.model_dump_json()))  # type: ignore
    except PyMongoError:
        pass


async def fetch_from_db_if_exists(
    client: AsyncMongoClient,
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

    try:
        summary: str = data.content

        collection = client["newsful"]["articles"]  # type: ignore

        # fetch from database if exists
        res = await collection.find_one({"summary": summary})  # type: ignore

        if res is not None:
            return FactCheckResponse.model_validate(res)
        return None
    except PyMongoError:
        return None
