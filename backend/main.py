import json
import os
from datetime import datetime
from io import StringIO
from typing import Dict, List

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain import PromptTemplate
from langchain.agents import AgentType, initialize_agent, load_tools
from langchain.llms import OpenAI
from langchain.utilities import GoogleSearchAPIWrapper
from pymongo.mongo_client import MongoClient
import uvicorn

from core import fact_checker, get_polarity, summarize, to_english, add_to_db
from core.utils import get_top_5_google_results
from schemas import Article, Health, InputData

# from pprint import pprint


load_dotenv()

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

# MongoDB
uri = str(os.environ.get("URI"))
client = MongoClient(uri)
db = client["NewsFul"]
collection = db["articles"]

# Langchain model

load_dotenv()

llm = OpenAI(max_tokens=200, temperature=0.2)  # type: ignore
tools = load_tools(["google-serper"], llm=llm)
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)  # type: ignore
template = PromptTemplate.from_template(
    template="""{news}. Yes or No?

Return answer in json format containing "label" (bool) to classify the news and "explanation" (str) parameter. Expecting property name enclosed in double quotes.
"""
)


@app.get("/api/health/")
def health() -> Health:
    """Health check endpoint."""

    db_is_working = False
    try:
        client.admin.command("ping")
        print("Pinged your deployment. You successfully connected to MongoDB!")
        db_is_working = True
    except Exception as e:
        print("Unable to connect to the database.")
        exit()
    return Health(status="ok", database=db_is_working, status_code=200)


@app.post("/api/verify/")
def verify_news(data: InputData) -> Article:
    """Endpoint to verify a news article."""

    data.content = to_english(data.content)
    data.content = summarize(data.content)
    fact_check = fact_checker(collection, data)

    response = agent.run(template.format(news=data.content))
    # pprint(response, width=120)
    try:
        data_ = json.load(StringIO(response))
    except Exception as e:
        data_ = {
            "explanation": response,
            "label": (get_polarity(response) / get_polarity(data.content)) > 0,
        }
        print("Exception: ", e)
    fact_check.label = data_["label"]
    fact_check.response = data_["explanation"]
    if fact_check.references is not None and len(fact_check.references) == 0:
        fact_check.references = get_top_5_google_results(data.content)
        add_to_db(collection, fact_check)
    file = f"./output/{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.json"
    json.dump(dict(fact_check), open(file, "w"), indent=4)
    # pprint(dict(fact_check), width=120)
    return fact_check


@app.get("/api/summarize/")
def summarize_text(text: str):
    """Endpoint to summarize a news article."""

    return {"summary": summarize(text)}


# if __name__ == "__main__":
#     uvicorn.run(app=app, host="localhost", port=8000, use_colors=True)
