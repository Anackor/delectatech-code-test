import streamlit as st


st.set_page_config(page_title="Food Delivery processes", layout="wide")
page = st.navigation([
    st.Page("pages/1_Crawler.py", title="Crawler"),
    st.Page("pages/2_Matching.py", title="Matching"),
    st.Page("pages/3_Clasificacion.py", title="Clasificacion"),
    st.Page("pages/4_Imagenes.py", title="Imagenes"),
])
page.run()
