from pathlib import Path

import streamlit as st

from app.classification.entrypoint import run
from app.dashboard.ui import show_history


st.title("Clasificacion de platos")
if st.button("Ejecutar clasificacion"):
    try:
        st.success(run(Path("source/food_categories.xlsx"), Path("source/just_eat_venues.json")))
    except Exception as error:
        st.error(str(error))
show_history("classification")
