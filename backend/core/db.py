from core.preprocessors import isCredible, isPhishing
from core.utils import archiveURL
from schemas import Article, FactCheckData


def add_to_db(collection, data: FactCheckData) -> Article:
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
        summary=data.summary,
        response=data.response,
        confidence=data.confidence,
        isPhishing=isPhishing(data.url),
        isCredible=isCredible(data.url),
        archive=archiveURL(data.url),
    )
    collection.insert_one(dict(db_data))
    return db_data
