import pydantic
import streamlit as st
from typing import Any
import pymongo
from schema.Article import Article
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Newsful",
    layout="centered",
    initial_sidebar_state="auto",
)


class NewsState:
    true_count: int = 0
    false_count: int = 0


@st.cache_data
def get_data() -> list[Article]:
    URI: str = st.secrets["MONGO_URI"]
    client = pymongo.MongoClient(URI)  # type: ignore
    collection = client["NewsFul"]["articles"]  # type: ignore
    data: list[dict[str, Any]] = list(collection.find())  # type: ignore
    client.close()
    articles: list[Article] = [Article(**article) for article in data]
    return articles


st.title("Newsful")
data: list[Article] = get_data()

state = NewsState()
for article in data:
    if article.label:
        state.true_count += 1
    else:
        state.false_count += 1

halves = st.columns(2)

with halves[0]:
    st.metric(label="True News", value=state.true_count, delta=state.true_count, delta_color="normal")  # type: ignore
    st.metric(label="False News", value=state.false_count, delta=state.false_count, delta_color="inverse")  # type: ignore
    st.metric(label="Total News", value=state.true_count + state.false_count)  # type: ignore

with halves[1]:
    # display the true and false counts in a pie chart
    fig, ax = plt.subplots()  # type: ignore
    ax.pie(  # type: ignore
        x=[state.true_count, state.false_count],
        labels=["True", "False"],
        autopct="%1.1f%%",
        colors=["green", "red"],
        startangle=90,
    )
    st.pyplot(fig)

if st.checkbox("Show raw data"):
    st.write([article.model_dump() for article in data])  # type: ignore
