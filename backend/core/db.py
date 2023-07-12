def url_is_present(conn, url: str) -> bool:
    """
    url_is_present checks if the URL is present in the db

    Parameters
    ----------
    conn : _type_
        The Connection variable
    url : str
        the url

    Returns
    -------
    bool
        _description_
    """

    conn.execute("SELECT * FROM articles WHERE url = %s", (url,))
    return bool(conn.fetchone())
