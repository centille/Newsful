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
    OPENAI_API_KEY=""
    GOOGLE_CSE_KEY=""
    TESSERACT_PATH=""
    ```

6. Run the API

    ```sh
    fastapi dev ./main.py # dev
    fastapi ./main.py     # production
    ```
