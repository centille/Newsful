from core.preprocessors import isCredible, isPhishing
from core.utils import archiveURL
from schemas import Article


def add_to_db(collection, data: Article) -> Article:  # type: ignore
    """
    add_to_db adds the data to the database.

    Parameters
    ----------
    conn : pymongo Collection
        The connection to the database.
    data : Article
        The data to be added to the database.
    """

    db_data = Article(
        url=data.url,  # type: ignore
        summary=data.summary,  # type: ignore
        response=data.response,  # type: ignore
        confidence=data.confidence,  # type: ignore
        isPhishing=isPhishing(data.url),  # type: ignore
        isCredible=isCredible(data.url),  # type: ignore
        archive=archiveURL(data.url),  # type: ignore
    )
    collection.insert_one(dict(db_data))
    return db_data
