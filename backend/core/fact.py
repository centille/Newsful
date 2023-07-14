from core.db import add_to_db
from schemas import Data, FactCheckData


def fact_checker(conn, data: Data) -> FactCheckData:
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

    conn.execute("SELECT * FROM articles WHERE url = %s and 
    res = conn.fetchone()
    if bool(res):
        return FactCheckData(
            url=url,
            summary=summary,
            response=str(res[1]),
            confidence=float(res[2]),
        )

    result = FactCheckData(
        url=url,
        summary=summary,
        response="",
        confidence=0.0,
    )

    add_to_db(conn, result)

    return result
