import json
from pathlib import Path

import streamlit as st

from app.dashboard.adapters.history import executions
from app.dashboard.adapters.insights import classification_summary, matching_summary


def show_matching_kpis() -> None:
    st.subheader("Indicadores")
    summary = matching_summary()
    if summary is None or summary["total"] == 0:
        st.info("Ejecuta matching para generar indicadores.")
        return
    coverage = 100 * summary["matched"] / summary["total"]
    columns = st.columns(4)
    columns[0].metric("Restaurantes enlazados", summary["matched"])
    columns[1].metric("Cobertura", f"{coverage:.1f}%")
    columns[2].metric("Ambiguos", summary["ambiguous"])
    columns[3].metric("Sin enlace", summary["unmatched"])
    st.caption("La cobertura usa restaurantes de Just Eat del ultimo pack de matching.")
    if summary["averageScore"] is not None:
        st.caption(f"Puntuacion media de las decisiones visibles: {summary['averageScore']:.1f}/100")


def show_classification_kpis() -> None:
    st.subheader("Indicadores")
    summary = classification_summary()
    if summary is None or summary["total"] == 0:
        st.info("Ejecuta matching y clasificacion para generar indicadores.")
        return
    coverage = 100 * summary["classified"] / summary["total"]
    columns = st.columns(4)
    columns[0].metric("Platos procesados", summary["total"])
    columns[1].metric("Clasificados", summary["classified"])
    columns[2].metric("Cobertura", f"{coverage:.1f}%")
    columns[3].metric("En revision", summary["review"])
    st.caption(f"Clasificaciones en categorias genericas: {summary['generic']}")
    if summary["categories"]:
        st.caption("La distribucion cuenta apariciones de platos en menus.")
        st.bar_chart(summary["categories"], x="category", y="dishes", horizontal=True,
                     x_label="Categoria", y_label="Apariciones")


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
                    st.dataframe(data, width="stretch", height=480)
                else:
                    st.json(data)
            except json.JSONDecodeError:
                st.caption("El artefacto no es JSON.")
