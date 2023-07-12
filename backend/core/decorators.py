def clean_text(text: str) -> str:
    import re

    text = re.sub(r"\n", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()
