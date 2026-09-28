from pathlib import Path

import streamlit as st

from app.dashboard.ui import show_history, show_matching_kpis
from app.matching.entrypoint import run


st.title("Matching de restaurantes")
with st.form("matching"):
    size = st.number_input("Tamano del pack", min_value=1, max_value=200, value=50)
    seed = st.number_input("Semilla", min_value=0, value=0)
    submitted = st.form_submit_button("Ejecutar matching")
if submitted:
    try:
        st.success(run(size, seed, Path("source/just_eat_venues.json"), Path("source/google_venues.json")))
    except Exception as error:
        st.error(str(error))
show_matching_kpis()
show_history("matching")
