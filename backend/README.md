# Newsful Backend API

## About

This is the backend API for the Newsful Browser Plugin. It is a Python-FastAPI application that uses OpenAI's GPT-4o, Google Programmable Search Engine connected using langchain to fact-check news articles. It also contains a knowledge graph with built-in phishing detection.

## Dependencies

- [Python 3](https://www.python.org/downloads/)
- [Poetry](https://python-poetry.org/docs/#installation)
- [OpenAI API Key](https://openai.com/) - $20 per month
- [Serper API Key](https://serper.dev/) - $0.3 per 1000 requests

## Installation

1. Clone the repository
2. Create a virtual environment with

    ```sh
    python -m venv env
    ```

3. Activate the virtual environment with

    - for Linux:

        ```sh
        source env/bin/activate
        ```

    - for Windows:

        ```sh
        ./env/Scripts/activate.bat
        ```

4. Install dependencies

    ```sh
    pip install poetry # via pip
    poetry install     # via poetry
    ```

5. Set environment variables

    ```env
    OPENAI_API_KEY="" # https://platform.openai.com/account/api-keys
    GOOGLE_CSE_ID=""  # https://cse.google.com/cse
    GOOGLE_API_KEY="" # https://developers.google.com/custom-search/v1/introduction
    TESSERACT_PATH="" # https://github.com/tesseract-ocr/tesseract
    MONGO_URI=""      # https://www.mongodb.com
    ENV="dev"         # dev or prod
    ```

6. Run the API

    ```sh
    fastapi dev ./main.py # dev
    fastapi ./main.py     # production
    ```
