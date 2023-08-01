from json import load
from io import StringIO

from langchain.agents import AgentType, initialize_agent, load_tools
from langchain.llms import OpenAI

from schemas import FactCheckResponse, TextInputData


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
    tools = load_tools(["google-serper"], llm=llm)
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
    )
    template = """. Is this news true or false?
        Without any comment, return the result in the following JSON format {"label": bool, "response": str}
    """

    response = agent.run(data.content + template)

    if DEBUG:
        from pprint import pprint

        print("Raw response:")
        pprint(response, width=120)

    l = response.find("{")
    r = response.find("}", l) if l != -1 else -1
    if l == -1 or r == -1:
        print("API response does not contain valid JSON.")
        raise Exception("API response does not contain valid JSON.")

    # clean
    response = response[l : r + 1].lower()
    if response.find('"label"') <= 0 and response.find("label") >= 0:
        response = response.replace("label", '"label"')
    if response.find('"response"') <= 0 and response.find("response") >= 0:
        response = response.replace("response", '"response"')

    return FactCheckResponse(**load(StringIO(response)))
