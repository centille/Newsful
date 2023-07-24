from core.db import add_to_db
from schemas import Article, FactCheckData, InputData


def fact_checker(collection, data: InputData) -> Article:
    """
    fact_checker checks the data against the database.

    Parameters
    ----------
    conn : sqlalchemy._engine.Connection
        The connection to the database.
    data : Data
        The data to be checked.

    Returns
    -------
    FactCheckData
        The result of the fact check.
    """
    url = data.url
    summary = data.content

    res = collection.find_one({"url": url, "summary": summary})
    if res:
        return Article(**res)

    result = FactCheckData(
        url=url,
        summary=summary,
        response="",
        confidence=0.0,
    )  # type: ignore

    return add_to_db(collection, result)
