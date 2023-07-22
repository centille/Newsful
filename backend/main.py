import os
from pickle import load
from typing import Any, Dict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo.mongo_client import MongoClient
import json
from io import StringIO

from dotenv import load_dotenv
from langchain.agents import initialize_agent, load_tools
from langchain.llms import OpenAI
from langchain.utilities import GoogleSearchAPIWrapper
from core import fact_checker, summarize, to_english, wordopt

from schemas import Article, InputData

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
db = client["newsful"]
collection = db["articles"]

# Models
model_filename = "pickles/PA.pickle"
vectorizer_filename = "pickles/tfidf_vectorizer.pickle"
vectorizer = load(open(vectorizer_filename, "rb"))
model = load(open(model_filename, "rb"))

# Langchain model

load_dotenv()

llm = OpenAI(max_tokens=200, temperature=0)  # type: ignore
tools = load_tools(["google-serper"], llm=llm)
agent = initialize_agent(tools=tools, llm=llm, agent="zero-shot-react-description", verbose=True)  # type: ignore
template = """{news}. Yes or No?

Return answer in a json format containing "label" parameter ('true' or 'fake') to classify the news and "explanation" parameter.
"""
google_search = GoogleSearchAPIWrapper()  # type: ignore


@app.get("/api/health/")
def health() -> Dict[str, Any]:
    """Health check endpoint."""

    db_is_working = False
    try:
        client.admin.command("ping")
        print("Pinged your deployment. You successfully connected to MongoDB!")
        db_is_working = True
    except Exception as e:
        print("DIE THRASH")
        print(e)

    return {"status": "ok", "database": db_is_working, "status_code": 200}


@app.post("/api/verify/")
def verify_news(data: InputData) -> Article:
    """Endpoint to verify a news article."""

    data.content = to_english(data.content)
    data.content = summarize(data.content)
    fact_check = fact_checker(collection, data)

    response = agent.run(template.format(news=data.content))
    data_ = json.load(StringIO(response))
    fact_check.references = [x["link"] for x in google_search_tool(data.content)]  # type: ignore
    fact_check.response = data_["explanation"]
    fact_check.label = data_["label"]

    tfidf_x = vectorizer.transform([data.content])
    tfidf_x = wordopt(tfidf_x)
    fact_check.confidence = int(model._predict_proba_lr(tfidf_x)[0][1] * 100)
    return fact_check


@app.get("/api/summarize/")
def summarize_text(text: str):
    """Endpoint to summarize a news article."""

    return {"summary": summarize(text)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="localhost",
        port=8000,
        log_level="debug",
        use_colors=True,
    )
