import json
from pathlib import Path

import streamlit as st

from app.dashboard.adapters.history import executions


def show_history(use_case: str) -> None:
    history = executions(use_case)
    st.subheader("Ejecuciones")
    if not history:
        st.info("Todavia no hay ejecuciones de este proceso.")
        return
    labels = [f"{item['startedAt']:%Y-%m-%d %H:%M:%S} · {item['status']} · {item['id'][:8]}" for item in history]
    selected = history[labels.index(st.selectbox("Selecciona una ejecucion", labels))]
    st.json({"id": selected["id"], "status": selected["status"], "parameters": selected["parameters"],
             "metrics": selected["metrics"], "error": selected["error"]})
    if artifact := selected["artifact"]:
        path = Path(artifact["path"])
        if path.is_file():
            content = path.read_bytes()
            st.download_button("Descargar artefacto", content, file_name=artifact["name"])
            try:
                data = json.loads(content)
                if isinstance(data, list):
                    st.dataframe(data, use_container_width=True, height=480)
                else:
                    st.json(data)
            except json.JSONDecodeError:
                st.caption("El artefacto no es JSON.")
