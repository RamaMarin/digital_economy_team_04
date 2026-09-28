"""Dashboard de una sola página — Digital Readiness Score (Equipo 4 · Ciencia).
Ejecutar desde la raíz del proyecto:  streamlit run dashboard/app.py
Requiere haber corrido antes el notebook (genera data/processed/digital_economy_clean.csv)."""
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from dei_core import (COLS, COUNTRIES, DIMENSIONS, FOCUS, INDICATORS, META, build_diagnosis, cluster_profiles,
                      compute_drs, describe_gap, describe_profiles, describe_ranking, dimension_scores, weights)
from dei_plots import fig_clusters, fig_gap, fig_heatmap, fig_profiles, fig_ranking

st.set_page_config(page_title="Digital Readiness — Equipo 4", page_icon="📊", layout="wide")

CLEAN = ROOT / "data" / "processed" / "digital_economy_clean.csv"
if not CLEAN.exists():
    st.error("No se encontró data/processed/digital_economy_clean.csv. Ejecuta primero notebooks/Digital_Economy_Analysis.ipynb.")
    st.stop()

clean = pd.read_csv(CLEAN)
values = clean.set_index("iso3")[COLS]
year_cols = clean.set_index("iso3")[[f"{c}_year" for c in COLS]]

# ------------------------------------------------------------------ barra lateral: pesos
st.sidebar.header("Pesos del DRS")
st.sidebar.caption("Los pesos se renormalizan para sumar 1. Valores por defecto = los del notebook.")
if st.sidebar.button("Restablecer pesos"):
    for i in INDICATORS:
        st.session_state[f"w_{i['col']}"] = int(round(i["weight"] * 100))
raw_w = {}
for i in INDICATORS:
    raw_w[i["col"]] = st.sidebar.slider(f"{i['id']} · {i['short']}", 0, 40, int(round(i["weight"] * 100)), key=f"w_{i['col']}")
if sum(raw_w.values()) == 0:
    st.sidebar.error("Al menos un peso debe ser mayor que 0.")
    st.stop()
custom = {k: v / sum(raw_w.values()) for k, v in raw_w.items()}
st.sidebar.metric("Suma de pesos (normalizada)", f"{sum(custom.values()):.2f}")

N, contrib, drs, coverage = compute_drs(values, custom)
dim = dimension_scores(N, custom)
order = drs.sort_values(ascending=False)

# ------------------------------------------------------------------ encabezado y KPIs
st.title("Digital Readiness Score — México vs. EE. UU., Alemania, China y Japón")
st.caption("Equipo 4 · Sector Ciencia · Digital Economy Intelligence Lab. Índice **relativo** al grupo de cinco economías (min-max, 0–100).")

k = st.columns(5)
rk = list(order.index).index(FOCUS) + 1
k[0].metric("DRS México", f"{drs[FOCUS]:.1f}", f"lugar {rk} de {len(order)}", delta_color="off")
for col, (iso, v) in zip(k[1:], [(c, drs[c]) for c in order.index if c != FOCUS]):
    col.metric(COUNTRIES[iso], f"{v:.1f}", f"{v - drs[FOCUS]:+.1f} vs. México", delta_color="off")

# ------------------------------------------------------------------ gráficos
c1, c2 = st.columns(2)
with c1:
    st.plotly_chart(fig_ranking(contrib, drs))
    st.caption(describe_ranking(drs, contrib))
with c2:
    st.plotly_chart(fig_gap(N))
    st.caption(describe_gap(N))

c3, c4 = st.columns(2)
with c3:
    st.plotly_chart(fig_profiles(dim))
    st.caption(describe_profiles(dim, drs))
with c4:
    st.plotly_chart(fig_heatmap(N, values))
    st.caption("Texto = valor observado; color = posición normalizada (el costo de la canasta está invertido).")

cl = cluster_profiles(N)
if cl:
    with st.expander("Perfiles digitales (clustering exploratorio, n = 5)", expanded=False):
        st.plotly_chart(fig_clusters(cl, drs))
        for g in sorted(cl["labels"].unique()):
            st.write(f"**Grupo {g}:** " + ", ".join(COUNTRIES[c] for c in cl["labels"][cl["labels"] == g].index))

# ------------------------------------------------------------------ diagnóstico
st.subheader("Diagnóstico final")
st.markdown(build_diagnosis(values, N, drs).replace("\n\n", "\n\n"))
if custom != weights():
    st.info("El diagnóstico se recalcula con los pesos actuales de la barra lateral.")

# ------------------------------------------------------------------ trazabilidad
with st.expander("Datos, fuentes y años de observación"):
    show = values.rename(index=COUNTRIES).rename(columns={i["col"]: f"{i['id']} {i['short']}" for i in INDICATORS})
    st.dataframe(show)
    st.write("**Años de observación**")
    st.dataframe(year_cols.rename(index=COUNTRIES).rename(columns={f"{i['col']}_year": i["id"] for i in INDICATORS}))
    log = ROOT / "source_log.csv"
    if log.exists():
        st.write("**Source Log**")
        st.dataframe(pd.read_csv(log)[["id", "nombre_oficial", "unidad", "organismo_original", "plataforma_acceso", "codigo_indicador", "liga_origen"]])
st.caption("Limitaciones: 5 economías y 8 indicadores; DRS relativo y sensible a extremos; sin medición de calidad del servicio, cómputo ni contexto para IA.")
