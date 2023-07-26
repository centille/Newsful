from schemas import Article, InputData


def fact_checker(collection, data: InputData) -> Article:
    """
    fact_checker checks the data against the database.

    Parameters
    ----------
    conn : mongoDB Collection
        The MongoDB Collection to be used.
    data : Data
        The data to be checked.

    Returns
    -------
    Article
        The result of the fact check.
    """
    url = data.url
    summary = data.content

    res = collection.find_one({"url": url, "summary": summary})
    if res:
        return Article(**res)

    result = Article(
        url=url,
        summary=summary,
        response="",
    )

    return result
