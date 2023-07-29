from core.postprocessors import archiveURL, get_confidence, get_top_google_results, is_credible, is_phishing
from schemas import Article


def add_to_db(collection, data: Article) -> Article:
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
        references=get_top_google_results(data.summary),
        isPhishing=is_phishing(data.url),
        isCredible=is_credible(data.url),
    )
    collection.insert_one(dict(db_data))
    return db_data
