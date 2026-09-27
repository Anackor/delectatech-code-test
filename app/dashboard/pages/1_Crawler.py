import streamlit as st

from app.crawler.entrypoint import run
from app.dashboard.ui import show_history


st.title("Crawler de Just Eat")
with st.form("crawler"):
    url = st.text_input("URL publica del menu")
    timeout = st.number_input("Timeout (segundos)", min_value=1, max_value=120, value=30)
    submitted = st.form_submit_button("Ejecutar crawler")
if submitted:
    try:
        st.success(run(url, timeout))
    except Exception as error:
        st.error(str(error))
show_history("crawler")
