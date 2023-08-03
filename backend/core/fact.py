import json
import os
from datetime import datetime
from io import StringIO
from json import load
from pprint import pprint
from typing import List

from langchain.agents import AgentExecutor, AgentType, initialize_agent, load_tools  # type: ignore
from langchain.llms import OpenAI
from langchain.tools import BaseTool

from core.db import add_to_db, fetch_from_db_if_exists
from schemas import FactCheckResponse, TextInputData
from schemas.Article import Article


def fact_check_this(data: TextInputData, DEBUG: bool) -> FactCheckResponse:
    """Fact check the data."""
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


def fact_check_process(text_data: TextInputData, URI: str, DEBUG: bool) -> Article:
    fact_check, exists = fetch_from_db_if_exists(URI, text_data, DEBUG)
    if exists:
        if DEBUG:
            pprint(dict(fact_check), width=120)
        return fact_check

    fact_check_resp: FactCheckResponse = fact_check_this(text_data, DEBUG)
    if DEBUG:
        print("Filtered Response:")
        pprint(fact_check_resp, width=120)

    # assign to right variable
    fact_check.label = fact_check_resp.label
    fact_check.response = fact_check_resp.response

    fact_check: Article = add_to_db(URI, fact_check, DEBUG)

    if DEBUG:
        # check if "output" directory exists
        if not os.path.exists("./output"):
            os.mkdir("./output")

        file: str = f"./output/{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.json"
        fact_check_dict = dict(fact_check)
        pprint(fact_check_dict, width=120)
        json.dump(fact_check_dict, open(file, mode="w+"), indent=4)

    return fact_check
