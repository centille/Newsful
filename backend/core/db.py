from core.preprocessors import archiveURL, get_confidence, get_top_5_google_results, isCredible, isPhishing
from schemas import Article


async def add_to_db(collection, data: Article) -> Article:
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
        url=data.url,
        summary=data.summary,
        response=data.response,
        label=data.label,
        archive=archiveURL(data.url),
        confidence=get_confidence(data.summary),
        references=get_top_5_google_results(data.summary),
        isPhishing=isPhishing(data.url),
        isCredible=isCredible(data.url),
    )
    collection.insert_one(dict(db_data))
    return db_data
