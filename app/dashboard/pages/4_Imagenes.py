from pathlib import Path

import streamlit as st

from app.dashboard.ui import show_history
from app.images.entrypoint import run


st.title("Extraccion desde imagenes")
if st.button("Ejecutar OCR"):
    try:
        st.success(run(Path("source/google_images.zip")))
    except Exception as error:
        st.error(str(error))
show_history("images")
