import json
import os
from datetime import datetime
from io import StringIO
from json import load
from pprint import pprint
from typing import List, Literal

from langchain.agents import AgentExecutor, AgentType, initialize_agent, load_tools  # type: ignore
from langchain.llms import OpenAI
from langchain.tools import BaseTool

from core.db import add_to_db, fetch_from_db_if_exists
from core.postprocessors import (
    archiveURL,
    get_confidence,
    get_top_google_results,
    is_credible,
    is_phishing,
)
from core.preprocessors import is_government_related
from schemas import FactCheckResponse, TextInputData, ChatTextInputData, ChatReply
from schemas.Article import Article


def fact_check_this(data: TextInputData, DEBUG: bool) -> FactCheckResponse:
    """
    fact_check_this checks the data against the OpenAI API.

    Parameters
    ----------
    data : TextInputData
        The data to be checked.
    DEBUG : bool
        Whether to print debug statements or not.

    Returns
    -------
    FactCheckResponse
        The result of the fact check.
    """
    llm = OpenAI(
        max_tokens=200,
        temperature=0,
        client=None,
        model="text-davinci-003",
        frequency_penalty=1,
        presence_penalty=0,
        top_p=1,
    )
    tools: List[BaseTool] = load_tools(["google-serper"], llm=llm)
    agent: AgentExecutor = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
    )
    template = """. Is this news true or false?
        Without any comment, return the result in the following JSON format {"label": bool, "response": str}
    """

    response: str = agent.run(data.content + template)

    if DEBUG:
        print("Raw response:")
        pprint(response, width=120)

    l: int = response.find("{")
    r: int = response.find("}", l) if l != -1 else -1
    if l == -1 or r == -1:
        print("API response does not contain valid JSON.")
        raise Exception("API response does not contain valid JSON.")

    # clean
    response = response[l : r + 1].lower()
    if response.find('"label"') <= 0 and response.find("label") >= 0:
        response = response.replace("label", '"label"')
    if response.find('"response"') <= 0 and response.find("response") >= 0:
        response = response.replace("response", '"response"')

    if DEBUG:
        print("Cleaned response:")
        pprint(response, width=120)

    return FactCheckResponse(**load(StringIO(response)))


def fact_check_process(text_data: TextInputData, URI: str, dtype: Literal["image", "text"], DEBUG: bool) -> Article:
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
    DEBUG : bool
        Whether to print debug statements or not.

    Returns
    -------
    Article
        The result of the fact check.
    """
    fact_check, exists = fetch_from_db_if_exists(URI, text_data, dtype, DEBUG)
    if exists:
        if DEBUG:
            print("Found in DB:")
            pprint(dict(fact_check), width=120)
        return fact_check

    if DEBUG:
        print("Not found in DB. Fetching from API...")
    fact_check_resp: FactCheckResponse = fact_check_this(text_data, DEBUG)
    if DEBUG:
        print("Filtered Response:")
        pprint(fact_check_resp, width=120)

    # assign to right variable
    fact_check.label = fact_check_resp.label
    fact_check.response = fact_check_resp.response
    fact_check.isGovernmentRelated = is_government_related(text_data.content)
    fact_check.confidence = get_confidence(fact_check.summary, DEBUG)
    fact_check.references = get_top_google_results(fact_check.summary, DEBUG)
    fact_check.isPhishing = is_phishing(fact_check.url, DEBUG)
    fact_check.isCredible = is_credible(fact_check.url, fact_check.isPhishing, DEBUG)

    # Archive URL is news is false
    if not fact_check.label:
        fact_check.archive = archiveURL(fact_check.url, DEBUG)

    fact_check: Article = add_to_db(URI, fact_check, DEBUG)

    if DEBUG:
        # check if "output" directory exists
        if not os.path.exists("./output"):
            os.mkdir("./output")

        file: str = f"./output/{str(datetime.now().timestamp()).replace('.', '-')}.json"
        fact_check_dict = dict(fact_check)
        pprint(fact_check_dict, width=120)
        json.dump(fact_check_dict, open(file, mode="w+"), indent=4)

    return fact_check


def fact_check_this_chat(data: ChatTextInputData, DEBUG: bool) -> ChatReply:
    llm = OpenAI(
        max_tokens=200,
        temperature=0,
        client=None,
        model="text-davinci-003",
        frequency_penalty=1,
        presence_penalty=0,
        top_p=1,
    )
    tools: List[BaseTool] = load_tools(["google-serper"], llm=llm)
    agent: AgentExecutor = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
    )
    template = """. Is this news true or false?
        Without any comment, return the result in the following JSON format {"label": bool, "response": str}
    """

    response: str = agent.run(data.content + template)

    if DEBUG:
        print("Raw response:")
        pprint(response, width=120)

    l: int = response.find("{")
    r: int = response.find("}", l) if l != -1 else -1
    if l == -1 or r == -1:
        print("API response does not contain valid JSON.")
        raise Exception("API response does not contain valid JSON.")

    # clean
    response = response[l : r + 1].lower()
    if response.find('"label"') <= 0 and response.find("label") >= 0:
        response = response.replace("label", '"label"')
    if response.find('"response"') <= 0 and response.find("response") >= 0:
        response = response.replace("response", '"response"')

    if DEBUG:
        print("Cleaned response:")
        pprint(response, width=120)

    fact_check = FactCheckResponse(**load(StringIO(response)))

    reply = ChatReply(label=True)  # type: ignore
    reply.label = fact_check.label
    reply.response = fact_check.response
    reply.references = get_top_google_results(data.content, DEBUG=DEBUG)

    pprint(dict(reply), width=120)
    return reply


def fact_check_chat(text_data: ChatTextInputData, dtype: Literal["image", "text"], DEBUG: bool) -> ChatReply:
    fact_check_response: ChatReply = fact_check_this_chat(text_data, DEBUG)
    return fact_check_response
