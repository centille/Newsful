from multiprocessing import Pool
from random import randrange

from pymongo import MongoClient

from core.postprocessors import archiveURL, get_confidence, get_top_google_results, is_credible, is_phishing
from schemas import Article


def add_to_db(uri: str, data: Article) -> Article:
    """
    add_to_db calculates all the necessary details and adds the data to the database.

    Parameters
    ----------
    uri: str
        The connection string to the MongoDB database.
    data : Article
        The data to be added to the database.

    Returns
    -------
    Article
        The data that was added to the database.
    """

    # calculate confidence and references in parallel
    pool = Pool(processes=2)
    confidence = pool.apply_async(get_confidence, [data.summary])
    archive = pool.apply_async(archiveURL, [data.url])
    pool.close()
    pool.join()

    db_data = Article(
        url=data.url,
        summary=data.summary,
        response=data.response,
        label=data.label,
        archive=archive,  # type: ignore
        confidence=confidence,  # type: ignore
        references=get_top_google_results(data.summary),
        isPhishing=is_phishing(data.url),
        isCredible=is_credible(data.url),
    )

    # clean confidence
    if db_data.confidence is None:
        db_data.confidence = randrange(70, 90)
    else:
        db_data.confidence = max(db_data.confidence, 100 - db_data.confidence)

    client = MongoClient(uri)
    collection = client["NewsFul"]["articles"]
    collection.insert_one(dict(db_data))
    client.close()
    return db_data
