import os
from typing import Literal

import instructor
import openai
import requests
import ujson
from pydantic import BaseModel
from pymongo import AsyncMongoClient
from pymongo.typings import _DocumentType

from core.db import fetch_from_db_if_exists  # type: ignore
from core.postprocessors import archive_url, is_safe
from schemas import FactCheckLabel, FactCheckResponse, GPTFactCheckModel, TextInputData


def search_tool(query: str, num_results: int = 5):
    """Tool to search via Google CSE"""
    api_key = os.getenv("GOOGLE_API_KEY", "")
    cx = os.getenv("GOOGLE_CSE_ID", "")
    base_url = "https://www.googleapis.com/customsearch/v1"
    url = f"{base_url}?key={api_key}&cx={cx}&q={query}&num={num_results}"
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    return resp.json()


class SearchQuery(BaseModel):
    query: str


async def fact_check_with_gpt(oai_client: openai.AsyncOpenAI, data: TextInputData) -> GPTFactCheckModel:
    """
    fact_check_with_gpt checks the data against the OpenAI API.

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

    client = instructor.from_openai(oai_client)

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        response_model=SearchQuery,
        messages=[
            {
                "role": "system",
                "content": "I want you to act as a fact-check researcher. You will be given a claim and you have should search the information on a custom search engine to help in the fact checking. Frame a query using the least words possible and return only the query.",
            },
            {
                "role": "user",
                "content": claim,
            },
        ],
    )
    assert isinstance(response, SearchQuery)

    search_results = search_tool(response.query)

    # Send the search results back to GPT for analysis
    final_response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "I want you to act as a fact checker. You will be given a statement along with relevant search results and you are supposed to provide a fact check based on them. You need to classify the claim as correct, incorrect, or misleading and provide the logical explanation along with the sources you used.",
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
    client: openai.AsyncOpenAI,
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

    fact_check_resp = await fact_check_with_gpt(client, text_data)

    # assign to right variable
    fact_check = FactCheckResponse(
        url=text_data.url,
        dataType=dtype,
        label=fact_check_resp.label,
        response=fact_check_resp.explanation,
        summary=text_data.content,
        references=fact_check_resp.sources,
        isSafe=is_safe(text_data.url) if text_data.url is not None else False,
        archive=None,
    )

    # Archive URL is news is false
    if fact_check.label != FactCheckLabel.CORRECT and fact_check.url is not None:
        fact_check.archive = archive_url(fact_check.url)

    return (fact_check, False)
