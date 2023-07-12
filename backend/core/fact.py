from core.db import url_is_present
import schemas


def fact_checker(conn, data: schemas.Data) -> schemas.FactCheckData:
    url = data.url
    summary = data.content

    if url_is_present(conn, data.url):
        pass
    else:
        pass

    return schemas.FactCheckData(
        url=url,
        summary=summary,
        response="",
        confidence=0.0,
    )
