import os
from typing import Literal

import openai
import requests
import ujson
from pymongo import AsyncMongoClient
from pymongo.typings import _DocumentType

from core.db import fetch_from_db_if_exists  # type: ignore
from core.postprocessors import archive_url, is_safe
from schemas import FactCheckLabel, FactCheckResponse, GPTFactCheckModel, TextInputData


def search_tool(query: str, num_results: int = 3):
    """Tool to search via Google CSE"""
    api_key = os.getenv("GOOGLE_API_KEY", "")
    cx = os.getenv("GOOGLE_CSE_ID", "")
    base_url = "https://www.googleapis.com/customsearch/v1"
    url = f"{base_url}?key={api_key}&cx={cx}&q={query}&num={num_results}"
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    return resp.json()


async def fact_check_with_gpt(client: openai.AsyncOpenAI, data: TextInputData) -> GPTFactCheckModel:
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

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "I want you to act as a fact-check researcher. You will be given a claim and you have should search the information on Google to help in the fact checking.",
            },
            {
                "role": "user",
                "content": claim,
            },
        ],
        functions=[
            {
                "name": "google_search",
                "description": "Search Google for fact-checking information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "num_results": {"type": "integer", "default": 3},
                    },
                    "required": ["query"],
                },
            }
        ],
        function_call="auto",
    )

    # Process the response and perform the Google search if requested
    message = response.choices[0].message
    if message.function_call and message.function_call.name == "google_search":
        function_args = ujson.loads(message.function_call.arguments)
        search_results = search_tool(function_args["query"], function_args.get("num_results", 3))

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
            functions=[
                {
                    "name": "provide_fact_check",
                    "description": "Provide the fact check result",
                    "parameters": GPTFactCheckModel.model_json_schema(),
                }
            ],
            function_call={"name": "provide_fact_check"},
        )

        return GPTFactCheckModel.model_validate_json(final_response.choices[0].message.function_call.arguments)  # type: ignore
    # If no function was called, parse the response directly
    return GPTFactCheckModel.model_validate_json(message.content or "")


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
