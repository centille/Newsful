import os
from datetime import datetime
from io import StringIO
from json import load
from pprint import pprint
from typing import List, Literal

import ujson
from langchain.agents import AgentExecutor, AgentType, initialize_agent  # type: ignore
from langchain.tools import BaseTool
from langchain_community.agent_toolkits.load_tools import load_tools  # type: ignore
from langchain_openai import ChatOpenAI

from core.db import add_to_db, fetch_from_db_if_exists
from core.postprocessors import archiveURL, get_top_google_results, is_safe
from core.preprocessors import is_government_related
from schemas import FactCheckResponse, TextInputData
from schemas.Article import Article


def fact_check_this(data: TextInputData, debug: bool) -> FactCheckResponse:
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
    tools: List[BaseTool] = load_tools(["google-serper"], llm=llm)
    agent: AgentExecutor = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
    )
    template = (
        data.content
        + """. Is this news true or false?
        Without any comment, return the result in the following JSON format {"label": bool, "response": str}"""
    )

    if debug:
        print("Template: ")
        pprint(template, width=120)

    response: str = agent.run(template)

    if debug:
        print("Raw response:")
        pprint(response, width=120)

    lb: int = response.find("{")
    rb: int = response.find("}", lb) if lb != -1 else -1
    if lb == -1 or rb == -1:
        if debug:
            print("API response does not contain valid JSON.")
        label = "true" in response.lower()
        response = '{"label": ' + str(label).lower() + ', "response": "' + response + '"}'
    else:
        # clean
        response = response[lb : rb + 1].lower()
        if response.find('"label"') <= 0 and response.find("label") >= 0:
            response = response.replace("label", '"label"')
        if response.find('"response"') <= 0 and response.find("response") >= 0:
            response = response.replace("response", '"response"')

    if debug:
        print("Cleaned response:")
        pprint(response, width=120)

    return FactCheckResponse(**load(StringIO(response)))


def fact_check_process(text_data: TextInputData, URI: str, dtype: Literal["image", "text"], debug: bool) -> Article:
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
    Article
        The result of the fact check.
    """
    fact_check, exists = fetch_from_db_if_exists(URI, text_data, dtype, debug)
    if exists:
        if debug:
            print("Found in DB:")
            pprint(dict(fact_check), width=120)
        return fact_check

    if debug:
        print("Not found in DB. Fetching from API...")
    fact_check_resp: FactCheckResponse = fact_check_this(text_data, debug)
    if debug:
        print("Filtered Response:")
        pprint(fact_check_resp, width=120)

    # assign to right variable
    fact_check.label = fact_check_resp.label
    fact_check.response = fact_check_resp.response
    fact_check.isGovernmentRelated = is_government_related(text_data.content)
    fact_check.references = get_top_google_results(fact_check.summary, debug)
    fact_check.isSafe = is_safe(fact_check.url, debug)

    # Archive URL is news is false
    if not fact_check.label:
        fact_check.archive = archiveURL(fact_check.url, debug)

    fact_check: Article = add_to_db(URI, fact_check, debug)

    if debug:
        # check if "output" directory exists
        if not os.path.exists("./output"):
            os.mkdir("./output")

        file: str = f"./output/{str(datetime.now().timestamp()).replace('.', '-')}.json"
        fact_check_dict = dict(fact_check)
        pprint(fact_check_dict, width=120)
        ujson.dump(fact_check_dict, open(file, mode="w+", encoding="utf-8"), indent=4)

    return fact_check
