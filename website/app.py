import json
from typing import Any

import matplotlib.pyplot as plt
import pymongo
import streamlit as st
from schema.Article import Article

st.set_page_config(
    page_title="Newsful",
    layout="centered",
    initial_sidebar_state="auto",
)


class NewsState:
    true_count: int = 0
    false_count: int = 0
    total_count: int = 0
    phishing_count: int = 0


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

st.write(  # type: ignore
    "This is a dashboard to view the information stored in the DataBase of the Newsful project."
)

data: list[Article] = get_data()
state = NewsState()
for article in data:
    if article.isPhishing:
        state.phishing_count += 1
    if article.label:
        state.true_count += 1
    else:
        state.false_count += 1
    state.total_count += 1

st.divider()

halves = st.columns(2)

with halves[0]:
    st.header("True vs False News")
    cols = st.columns(3)
    with cols[0]:
        st.metric(label="True News", value=state.true_count, delta=state.true_count, delta_color="normal")  # type: ignore
    with cols[1]:
        st.metric(label="False News", value=state.false_count, delta=state.false_count, delta_color="inverse")  # type: ignore
    with cols[2]:
        st.metric(label="Total News", value=state.total_count)  # type: ignore

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

st.divider()

halves = st.columns(2)

with halves[0]:
    # display the true and false counts in a pie chart
    fig, ax = plt.subplots()  # type: ignore
    ax.pie(  # type: ignore
        x=[state.phishing_count, state.total_count - state.phishing_count],
        labels=["Phishing", "Not Phishing"],
        autopct="%1.1f%%",
        colors=["red", "green"],
        startangle=90,
    )
    st.pyplot(fig)

with halves[1]:
    st.header("Phishing News")
    cols = st.columns(2)
    with cols[0]:
        st.metric(label="Phishing News", value=state.phishing_count, delta=state.phishing_count, delta_color="normal")  # type: ignore
    with cols[1]:
        st.metric(label="Total News", value=state.total_count)  # type: ignore

st.divider()


st.download_button(
    label="Download Data",
    data=json.dumps([article.model_dump_json() for article in data]),  # type: ignore
    file_name="data.json",
    mime="application/json",
)
