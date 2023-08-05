# Newsful Backend API

## About

This is the backend API for the Newsful Browser Plugin. It is a Python-FastAPI application that uses OpenAI's GPT-3, google serper connected using langchain to fact-check news articles. It also contains a knowledge graph with built-in phishing detection.

## Dependencies

- [Python 3](https://www.python.org/downloads/)
- [Poetry](https://python-poetry.org/docs/#installation)
- [OpenAI API Key](https://openai.com/) - $20 per month
- [Serper API Key](https://serper.dev/) - $0.3 per 1000 requests

## Installation

1. Clone the repository
2. Create a virtual environment with
```
$ python -m venv env
```
3. Activate the virtual environment with

  - for Linux:
```
$ source env/bin/activate
```
  - for Windows:
```
$ env\Scripts\activate.bat
```

4. Install dependencies

```
$ pip install poetry
$ poetry install
```

**Note**: If an error during greenlet installation, `pip install greenlet` first and then rerun `poetry install`.

5. Run the API

```
$ uvicorn main:app --host localhost --reload
```
