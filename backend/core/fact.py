import os
from typing import Literal, TypedDict
import asyncio

from bs4 import BeautifulSoup
from groq import AsyncGroq
import requests
import ujson
import instructor
from pydantic import BaseModel
from pymongo import AsyncMongoClient
from pymongo.typings import _DocumentType

from core.db import fetch_from_db_if_exists
from core.preprocessors import summarize
from core.postprocessors import archive_url, is_safe
from schemas.schemas import FactCheckLabel, FactCheckResponse, GPTFactCheckModel, TextInputData


class SearchResult(TypedDict):
    title: str
    link: str
    content: str


async def get_content(groq_client: AsyncGroq, url: str) -> str | None:
    """returns the content of given url"""
    try:
        with requests.get(url, timeout=15) as res:
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "html.parser")
            return await summarize(groq_client, soup.get_text())
    except requests.exceptions.RequestException:
        return None


async def get_url_content(groq_client: AsyncGroq, item: dict) -> SearchResult:
    content = await get_content(groq_client, str(item.get("link", "")))
    return {
        "title": item["title"],
        "link": item["link"],
        "content": content or item["snippet"],
    }


async def search_tool(groq_client: AsyncGroq, query: str, num_results: int = 3):
    """Tool to search via Google CSE"""
    api_key = os.getenv("GOOGLE_API_KEY", "")
    cx = os.getenv("GOOGLE_CSE_ID", "")
    base_url = "https://www.googleapis.com/customsearch/v1"
    url = f"{base_url}?key={api_key}&cx={cx}&q={query}&num={num_results}"
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    json = ujson.loads(resp.text)
    assert hasattr(resp, "items")
    res: list[SearchResult] = []
    tasks = [get_url_content(groq_client, item) for item in json["items"]]
    res.extend(await asyncio.gather(*tasks))
    return res


class SearchQuery(BaseModel):
    query: str


async def fact_check(groq_client: AsyncGroq, data: TextInputData) -> GPTFactCheckModel:
    """
    fact_check checks the data against the OpenAI API.

    Parameters
    ----------
    data : TextInputData
        The data to be checked.

    Returns
    -------
    FactCheckResponse
        The result of the fact check.
    """

    claim = data.content

    client = instructor.from_groq(groq_client)

    response = await client.chat.completions.create(
        model="llama-3.2-3b-preview",
        response_model=SearchQuery,
        messages=[
            {
                "role": "system",
                "content": "You are a fact-check researcher whose task is to search information to help in the fact checking. Frame an appropriate query to get the most appropriate results that will aid in the fact check",
            },
            {
                "role": "user",
                "content": claim,
            },
        ],
    )
    assert isinstance(response, SearchQuery)

    search_results = await search_tool(groq_client, response.query)

    # Send the search results back to GPT for analysis
    final_response = await client.chat.completions.create(
        model="deepseek-r1-distill-llama-70b",
        messages=[
            {
                "role": "system",
                "content": "I want you to act as a fact checker. You will be given a statement along with relevant search results and you are supposed to provide a fact check based on the search results. You need to classify the claim as 'correct', 'incorrect', or 'misleading' and provide the logical explanation along with the sources you used.",
            },
            {
                "role": "user",
                "content": f"Original statement: {claim}\n\nSearch results: {ujson.dumps(search_results, escape_forward_slashes=False)}",
            },
        ],
        response_model=GPTFactCheckModel,
    )
    assert isinstance(final_response, GPTFactCheckModel)
    return final_response


async def fact_check_process(
    groq_client: AsyncGroq,
    text_data: TextInputData,
    mongo_client: AsyncMongoClient[_DocumentType],
    dtype: Literal["image", "text"],
) -> tuple[FactCheckResponse, bool]:
    """
    fact_check_process checks the data against the OpenAI API.

    Parameters
    ----------
    text_data : TextInputData
        The data to be checked.
    URI : str
        The URI of the article.
    dtype : Literal["image", "text"]
        The type of data to be checked.

    Returns
    -------
    FactCheckResponse
        The result of the fact check.
    """
    fact_check_ = await fetch_from_db_if_exists(mongo_client, text_data)
    if fact_check_ is not None:
        return (fact_check_, True)

    fact_check_resp = await fact_check(groq_client, text_data)

    # assign to right variable
    fact_check_obj = FactCheckResponse(
        url=text_data.url,
        label=fact_check_resp.label,
        response=fact_check_resp.explanation,
        summary=text_data.content,
        references=fact_check_resp.sources,
        isSafe=is_safe(text_data.url) if text_data.url is not None else False,
        archive=None,
    )

    # Archive URL is news is false
    if fact_check_obj.label != FactCheckLabel.CORRECT and fact_check_obj.url is not None:
        fact_check_obj.archive = archive_url(fact_check_obj.url)

    return (fact_check_obj, False)
