import instructor
from deep_translator.google import GoogleTranslator  # type: ignore
from groq import AsyncGroq
from pydantic import BaseModel, Field


class GPTGeneratedSummary(BaseModel):
    """The model for summarization"""

    summary: str = Field(None, description="The summary of the article")


def to_english(text: str) -> str:  # type: ignore
    """translates text to english if it is not already in english."""
    text = " ".join(text.split()).rstrip(".")
    translator = GoogleTranslator(source="auto", target="en")  # type: ignore
    text = translator.translate(text)  # type: ignore
    return text


async def summarize(client: AsyncGroq, text: str) -> str:
    """summarizes the text via Groq."""
    if len(text) <= 200:
        return text
    try:
        # client_ = instructor.from_openai(client)
        client_ = instructor.from_groq(client)
        response = await client_.chat.completions.create(
            model="llama-3.1-8b-instant",
            response_model=GPTGeneratedSummary,
            messages=[
                {
                    "role": "system",
                    "content": "Generate a concise summary in the language of the article. ",
                },
                {
                    "role": "user",
                    "content": f"Summarize the following text in a concise way:\n{text}",
                },
            ],
        )
        assert isinstance(response, GPTGeneratedSummary)
        return response.summary
    except AssertionError:
        return text
