import streamlit as st

from app.dashboard.ui import show_history
from app.images.entrypoint import run_uploads


st.title("Extraccion desde imagenes")
uploads = st.file_uploader("Imagenes", type=("jpg", "jpeg", "png", "webp"), accept_multiple_files=True)
if st.button("Ejecutar OCR", disabled=not uploads):
    try:
        st.success(run_uploads((upload.name, upload.getvalue()) for upload in uploads))
    except Exception as error:
        st.error(str(error))
show_history("images")
