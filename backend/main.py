import json
import os
import warnings
from datetime import datetime
from io import StringIO
from pprint import pprint

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain.agents import AgentType, initialize_agent, load_tools
from langchain.llms import OpenAI
from pymongo.mongo_client import MongoClient

from core import add_to_db, fetch_from_db_if_exists, summarize, to_english
from schemas import Article, FactCheckResponse, Health, ImageInputData, TextInputData

# FastAPI app
app = FastAPI(
    title="Newsful API",
    description="API for Newsful - a news summarization and fact checking app.",
    version="0.0.1",
)

# FastAPI CORS
app.add_middleware(
    CORSMiddleware,
    allow_methods=["*"],
    allow_origins=["*"],
    allow_headers=["*"],
)

# Load environment variables
load_dotenv()
URI = str(os.environ.get("URI"))
# Suppress warnings
warnings.filterwarnings("ignore")
# Global variables
DEBUG = True

# Initialize agent
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


@app.get("/api/health/")
def health() -> Health:
    """Health check endpoint."""

    db_is_working = False
    client = MongoClient(URI)
    if client.admin.command("ping")["ok"] == 1:
        client.close()
        if DEBUG:
            print("Pinged your deployment. You successfully connected to MongoDB!")
        db_is_working = True
        return Health(status="ok", database=db_is_working, status_code=200)
    raise Exception("Unable to connect to the database.")


@app.get("/api/summarize/")
def summarize_text(text: str):
    """Endpoint to summarize a news article."""
    summary = summarize(text)
    if DEBUG:
        pprint(summary, width=120)
    return {"summary": summary}


@app.post("/api/verify/text/")
async def verify_news(data: TextInputData) -> Article:
    """Endpoint to verify a news article."""

    data.content = summarize(to_english(data.content))
    fact_check, exists = fetch_from_db_if_exists(URI, data)
    if exists:
        if DEBUG:
            pprint(dict(fact_check), width=120)
        return fact_check

    response = agent.run(data.content + template)
    if DEBUG:
        print("Raw response:")
        pprint(response, width=120)
    l = response.find("{")
    r = response.find("}", l) if l != -1 else -1
    if l == -1 or r == -1:
        pprint("API response does not contain valid JSON.", width=120)
        raise Exception("API response does not contain valid JSON.")

    # clean
    response = response[l : r + 1].lower()
    if response.find('"label"') == -1 and response.find("label") != -1:
        response = response.replace("label", '"label"')
    if response.find('"response"') == -1 and response.find("response") != -1:
        response = response.replace("response", '"response"')
    fact_check_resp = FactCheckResponse(**json.load(StringIO(response)))
    if DEBUG:
        print("Filtered Response:")
        pprint(fact_check_resp, width=120)

    # assign to right variable
    fact_check.label = fact_check_resp.label
    fact_check.response = fact_check_resp.response

    fact_check = add_to_db(URI, fact_check)

    if DEBUG:
        file = f"./output/{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.json"
        fact_check_dict = dict(fact_check)
        json.dump(fact_check_dict, open(file, "w"), indent=4)
        pprint(fact_check_dict, width=120)

    return fact_check


@app.post("/api/verify/image/")
def image_check(data: ImageInputData):
    """Endpoint to check if an image is fake."""
    if DEBUG:
        pprint(dict(data))
    raise NotImplementedError("This endpoint is not implemented yet.")
