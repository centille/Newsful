# Newsful Backend API

## About

This is the backend API for the Newsful Browser Plugin. It is a Python-FastAPI application that uses OpenAI's GPT-4o, Google Programmable Search Engine connected using langchain to fact-check news articles. It also contains a knowledge graph with built-in phishing detection.

## Dependencies

- [Python 3](https://www.python.org/downloads/)
- [Poetry](https://python-poetry.org/docs/#installation)
- [OpenAI API Key](https://openai.com/)
- [MongoDB](https://www.mongodb.com/)
- [Tesseract-OCR](https://github.com/tesseract-ocr/tesseract)
- [Google CSE](https://programmablesearchengine.google.com/about/)

## Installation

1. Clone the repository

   ```
    git clone https://github.com/centille/Newsful/
    ```
   
2. Navigate to the backend

    ```sh
    cd ./backend
    ```

3. Install dependencies

    ```sh
    pip install poetry && poetry install
    ```

4. Set environment variables

    ```env
    OPENAI_API_KEY="" # https://platform.openai.com/account/api-keys
    GOOGLE_CSE_ID=""  # https://cse.google.com/cse
    GOOGLE_API_KEY="" # https://developers.google.com/custom-search/v1/introduction
    TESSERACT_PATH="" # https://github.com/tesseract-ocr/tesseract
    MONGO_URI=""      # https://www.mongodb.com
    ENV="dev"         # dev or prod
    ```

5. Run the API

    ```sh
    fastapi dev ./main.py # dev
    fastapi ./main.py     # production
    ```
