import base64
import plotly.express as px  # type: ignore
import pymongo
import streamlit as st
from core.auth import hash_password, check_password
from schema import Article, ArticleDict, DisplayDict
import sqlite3 as sql
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
import pandas as pd  # type: ignore
from datetime import datetime

st.set_page_config(
    page_title="Newsful",
    layout="centered",
)


def put_gif(file_path: str, width: int):
    file_ = open(file_path, "rb")
    contents = file_.read()
    data_url = base64.b64encode(contents).decode("utf-8")
    file_.close()

    st.markdown(
        f'<img src="data:image/gif;base64,{data_url}" alt="cat gif" width="{width}">',
        unsafe_allow_html=True,
    )


if "LOGIN" not in st.session_state or st.session_state["LOGIN"] is False:
    st.title("Newsful", anchor="title")
    st.markdown(
        """
    <style>
        #title {
            font-size: 72px;
            color: #4b4bf4;
            text-align: center;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )
    login_tab, register_tab = st.tabs(["Login", "Register"])

    with register_tab:
        cols = st.columns(2)
        with cols[0]:
            put_gif("./assets/login.gif", width=250)
        with cols[1]:
            with st.form("register-form", clear_on_submit=True):
                st.subheader("Register")
                username: str = st.text_input("Username", max_chars=25)
                password: str = st.text_input("Password", type="password")
                confirm_password: str = st.text_input(
                    "Confirm Password", type="password"
                )
                if st.form_submit_button("Register"):
                    # hash password and create salt
                    if password != confirm_password:
                        st.error("Passwords do not match. Please try again.")
                    elif len(username) < 4:
                        st.error("Username must be at least 4 characters long.")
                    elif len(password) < 8:
                        st.error("Password must be at least 8 characters long.")
                    elif not any(char.isdigit() for char in password):
                        st.error("Password must contain at least one digit.")
                    elif not any(char.isupper() for char in password):
                        st.error("Password must contain at least one uppercase letter.")
                    elif not any(char.islower() for char in password):
                        st.error("Password must contain at least one lowercase letter.")
                    else:
                        hashed_password, salt = hash_password(password)
                        # store username, hashed_password and salt in db
                        db = sql.connect("./users.db")
                        cursor = db.cursor()
                        cursor.execute(
                            "CREATE TABLE IF NOT EXISTS users (username TEXT, hashed_password TEXT, salt TEXT)"
                        )
                        cursor.execute(
                            "INSERT INTO users VALUES (?, ?, ?)",
                            (username, hashed_password, salt),
                        )
                        db.commit()
                        db.close()
                        st.success("Registered successfully. Please login to continue.")
    with login_tab:
        cols = st.columns(2)
        with cols[0]:
            put_gif("./assets/login.gif", width=250)

        with cols[1]:
            with st.form("login-form", clear_on_submit=True):
                st.subheader("Login")
                username = st.text_input("Username", max_chars=25)
                password = st.text_input("Password", type="password")
                if st.form_submit_button("Login"):
                    db = sql.connect("./users.db")
                    cursor = db.cursor()
                    cursor.execute("SELECT * FROM users WHERE username=?", (username,))
                    user = cursor.fetchone()
                    db.close()
                    if user is None:
                        st.error("User does not exist. Please register.")
                    else:
                        hashed_password, salt = user[1], user[2]
                        if check_password(password, hashed_password, salt):
                            st.success("Logged in successfully.")
                            st.session_state["LOGIN"] = True
                            st.session_state["USERNAME"] = username
                            st.experimental_rerun()
                        else:
                            st.error("Incorrect password. Please try again.")

if "LOGIN" in st.session_state and st.session_state["LOGIN"] is True:

    class NewsState:
        overall_total_count: int = 0
        overall_true_count: int = 0
        overall_false_count: int = 0
        govt_total_count: int = 0
        govt_true_count: int = 0
        govt_false_count: int = 0
        non_govt_total_count: int = 0
        non_govt_true_count: int = 0
        non_govt_false_count: int = 0

    @st.cache_data
    def get_data() -> list[Article]:
        URI: str = st.secrets["MONGO_URI"]
        client = pymongo.MongoClient(URI)  # type: ignore
        collection = client["NewsFul"]["articles"]  # type: ignore
        data: ArticleDict = list(collection.find())  # type: ignore
        client.close()
        articles: list[Article] = [Article(**article) for article in data]  # type: ignore
        return articles

    st.header(f"Hello {st.session_state['USERNAME']}!")
    st.subheader("Welcome to the Newsful Dashboard!")

    st.write(  # type: ignore
        "This is a dashboard to view the information stored in the DataBase of the Newsful project."
    )

    data: list[Article] = get_data()
    state = NewsState()
    display_data: list[DisplayDict] = []
    for article in data:
        state.overall_total_count += 1
        if article.label:
            state.overall_true_count += 1
        else:
            state.overall_false_count += 1
        if article.isGovernmentRelated:
            state.govt_total_count += 1
            if article.label:
                state.govt_true_count += 1
            else:
                state.govt_false_count += 1
        else:
            state.non_govt_total_count += 1
            if article.label:
                state.non_govt_true_count += 1
            else:
                state.non_govt_false_count += 1
        display_data.append(article.display_dict())

    st.divider()

    st.header("Daily Stats")
    st.write(
        f"These are the number of fact checks done on **{datetime.today().strftime('%d %B %Y')}**."
    )
    with st.sidebar:
        st.title("Newsful", anchor="sidebar-title")
        st.markdown(
            """
            <style>
                #sidebar-title {
                    margin-top: 0;
                    padding-top: 0;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

    st.plotly_chart(  # type: ignore
        px.pie(  # type: ignore
            values=[state.overall_true_count, state.overall_false_count],
            names=["True", "False"],
        ),
        use_container_width=True,
    )
    thirds = st.columns(3)
    with thirds[0]:
        st.metric(
            "Total News",
            state.overall_total_count,
            delta=state.overall_total_count,
            delta_color="off",
        )
    with thirds[1]:
        st.metric(
            "True News",
            state.overall_true_count,
            delta=state.overall_true_count,
            delta_color="normal",
        )
    with thirds[2]:
        st.metric(
            "False News",
            state.overall_false_count,
            delta=state.overall_false_count,
            delta_color="inverse",
        )
    st.caption("**NOTE:** These stats are updated every 24 hours.")

    st.divider()

    st.header("Data")
    cellstyle_jscode = JsCode(
        """
        function(params) {
            if (params.value == true) {
                return {
                    'color': 'green',
                    'backgroundColor': 'lightgreen'
                }
            } else {
                return {
                    'color': 'red',
                    'backgroundColor': 'pink'
                }
            }
        };
        """
    )

    df = pd.DataFrame(display_data)
    # isSafe = not isPhishing and isCredible
    df["isSafe"] = ~df["isPhishing"] & df["isCredible"]
    df.drop(columns=["isPhishing", "isCredible"], inplace=True)
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_column("label", cellStyle=cellstyle_jscode)
    gb.configure_column("isSafe", cellStyle=cellstyle_jscode)
    gb.configure_grid_options(domLayout="normal")
    gridOptions = gb.build()
    AgGrid(
        df,
        gridOptions=gridOptions,
        width="100%",
        allow_unsafe_jscode=True,  # Set it to True to allow jsfunction to be injected
    )

    st.download_button(
        label="Download Data as CSV",
        data=df.to_csv().encode("utf-8"),
        file_name="data.csv",
        mime="text/csv",
    )

    st.divider()

    if st.button("logout"):
        del st.session_state["LOGIN"]
        st.experimental_rerun()
