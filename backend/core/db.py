from core.preprocessors import isCredible, isPhishing
from core.utils import archiveURL
from schemas import FactCheckData
from schemas.Articles import Article


def add_to_db(collection, data: FactCheckData) -> None:
    """
    add_to_db adds the data to the database.

    Parameters
    ----------
    conn : pymongo Collection
        The connection to the database.
    data : FactCheckData
        The data to be added to the database.
    """

    db_data = Article(
        url=data.url,
        content=data.summary,
        response=data.response,
        confidence=data.confidence,
        isPhishing=isPhishing(data.url),
        isCredible=isCredible(data.url),
        archive=archiveURL(data.url),
    )
    collection.insert_one(dict(db_data))
