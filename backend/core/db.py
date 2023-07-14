from core.preprocessors import isCredible, isPhishing
from core.utils import archiveURL
from schemas import FactCheckData


def add_to_db(conn, data: FactCheckData) -> None:
    """
    add_to_db adds the data to the database.

    Parameters
    ----------
    conn : sqlalchemy._engine.Connection
        The connection to the database.
    data : FactCheckData
        The data to be added to the database.
    """

    conn.execute(
        "CREATE TABLE IF NOT EXISTS articles (url TEXT, response TEXT, confidence REAL, isPhishing BOOLEAN, isCredible BOOLEAN, archive TEXT, lastUpdated TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
    )
    conn.execute(
        "INSERT INTO articles(url, content, response, confidence, isPhishing, isCredible, archive) VALUES(%s, %s, %s, %s, %s, %s)",
        (
            data.url,
            data.summary,
            data.response,
            data.confidence,
            isPhishing(data.url),
            isCredible(data.url),
            archiveURL(data.url),
        ),
    )
    conn.commit()
