import os
from datetime import datetime
from pprint import pprint
from typing import Literal

import ujson
from langchain.agents import AgentType, initialize_agent  # type: ignore
from langchain_core.tools import Tool
from langchain_google_community import GoogleSearchAPIWrapper  # type: ignore
from langchain_openai import ChatOpenAI

from core.db import add_to_db, fetch_from_db_if_exists
from core.postprocessors import archiveURL, get_top_google_results, is_safe
from core.preprocessors import is_government_related
from schemas import FactCheckLabel, FactCheckResponse, GPTFactCheckModel, TextInputData


async def fact_check_this(data: TextInputData) -> GPTFactCheckModel:
    """
    fact_check_this checks the data against the OpenAI API.

    Parameters
    ----------
    data : TextInputData
        The data to be checked.
    debug : bool
        Whether to print debug statements or not.

    Returns
    -------
    FactCheckResponse
        The result of the fact check.
    """
    llm = ChatOpenAI(
        model="gpt-4o",
        max_tokens=2000,
        temperature=0,
        model_kwargs={"response_format": {"type": "json_object"}},
    )
    search = GoogleSearchAPIWrapper()
    search_tool = Tool(
        name="google_search",
        description="useful for when you need to get results from fact check sites",
        func=search.run,
    )
    agent = initialize_agent(
        tools=[search_tool],
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
    )
    template = (
        data.content
        + """. Is this news true or false?
        Without any comment, return the result in the following JSON format {"label": bool, "explanation": str}"""
    )

    response: str = await agent.arun(template)

    lb = response.find("{")
    rb = response.rfind("}")
    response = response[lb : rb + 1]

    return GPTFactCheckModel.model_validate_json(response, strict=True)


async def fact_check_process(
    text_data: TextInputData, uri: str, dtype: Literal["image", "text"], debug: bool
) -> FactCheckResponse:
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
    debug : bool
        Whether to print debug statements or not.

    Returns
    -------
    FactCheckResponse
        The result of the fact check.
    """
    fact_check_ = fetch_from_db_if_exists(uri, text_data)
    if fact_check_ is not None:
        if debug:
            print("Found in DB:")
            pprint(fact_check_.model_dump(), width=120)
        return fact_check_

    if debug:
        print("Not found in DB. Fetching from API...")
    fact_check_resp = await fact_check_this(text_data)
    if debug:
        print("Filtered Response:")
        pprint(fact_check_resp, width=120)

    # assign to right variable
    fact_check = FactCheckResponse(
        label=fact_check_resp.label,
        response=fact_check_resp.explanation,
        summary=text_data.content,
        references=get_top_google_results(fact_check_resp.explanation),
        url=text_data.url,
        dataType=dtype,
        isGovernmentRelated=is_government_related(text_data.content),
        isSafe=is_safe(text_data.url) if text_data.url is not None else False,
        updatedAt=datetime.now().timestamp(),
        archive=None,
    )

    # Archive URL is news is false
    if fact_check.label != FactCheckLabel.CORRECT and fact_check.url is not None:
        fact_check.archive = archiveURL(fact_check.url, debug)

    add_to_db(uri, fact_check)

    if debug:
        os.makedirs("./output", exist_ok=True)

        file: str = f"./output/{str(datetime.now().timestamp()).replace('.', '-')}.json"
        fact_check_dict = dict(fact_check)
        pprint(fact_check_dict, width=120)
        ujson.dump(
            fact_check_dict,
            open(file, mode="w+", encoding="utf-8"),
            indent=4,
            allow_nan=False,
            reject_bytes=True,
            escape_forward_slashes=False,
        )

    return fact_check
