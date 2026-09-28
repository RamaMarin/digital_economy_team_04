"""Visualizaciones (Plotly) compartidas por el notebook y el dashboard."""
from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
import plotly.express as px

from dei_core import COUNTRIES, DIMENSIONS, FOCUS, INDICATORS, META, COLS, gap_vs_others

COLORS = {"MEX": "#1B9E77", "USA": "#377EB8", "DEU": "#7F7F7F", "CHN": "#E41A1C", "JPN": "#FF7F00"}
_QUAL = px.colors.qualitative.Safe + px.colors.qualitative.Set2


def _lab(i):
    return f'{i["id"]} {i["short"]}'


def fig_ranking(contrib, drs, height=420):
    order = list(drs.sort_values().index)
    fig = go.Figure()
    for k, ind in enumerate(INDICATORS):
        fig.add_bar(y=[COUNTRIES[c] for c in order], x=[contrib.loc[c, ind["col"]] for c in order], orientation="h",
                    name=_lab(ind), marker_color=_QUAL[k % len(_QUAL)],
                    hovertemplate="%{y}<br>" + _lab(ind) + ": %{x:.1f} pts<extra></extra>")
    for c in order:
        fig.add_annotation(x=drs[c], y=COUNTRIES[c], text=f"<b>{drs[c]:.1f}</b>", showarrow=False, xanchor="left", xshift=6)
    fig.update_layout(barmode="stack", height=height, title="Ranking DRS y aporte de cada indicador",
                      xaxis=dict(title="Puntos del DRS (0–100)", range=[0, max(drs.max() * 1.12, 10)]),
                      legend=dict(orientation="h", y=-0.28, font=dict(size=10)), margin=dict(l=10, r=10, t=50, b=10))
    return fig


def fig_gap(N, focus=FOCUS, height=420):
    g = gap_vs_others(N, focus)
    labs = [_lab(i) for i in INDICATORS]
    vals = [g[i["col"]] for i in INDICATORS]
    fig = go.Figure(go.Bar(x=vals, y=labs, orientation="h",
                           marker_color=["#1B9E77" if (v == v and v >= 0) else "#D95F02" for v in vals],
                           text=[("n.d." if v != v else f"{v:+.0f}") for v in vals], textposition="outside"))
    fig.update_yaxes(autorange="reversed")
    fig.update_layout(height=height, title=f"{COUNTRIES[focus]} vs. promedio de las otras cuatro economías",
                      xaxis_title="Diferencia en puntos normalizados (0–100)", margin=dict(l=10, r=30, t=50, b=10))
    fig.add_vline(x=0, line_width=1, line_color="#444")
    return fig


def fig_profiles(dim, height=440):
    short = {"Infraestructura y conectividad": "Infraestructura", "Acceso y uso": "Acceso y uso",
             "Calidad y asequibilidad": "Asequibilidad", "Actividad económica digital": "Actividad digital",
             "Capacidad tecnológica e innovación": "Capacidad e innovación"}
    theta = [short[d] for d in DIMENSIONS]
    fig = go.Figure()
    for c in dim.index:
        r = [dim.loc[c, d] for d in DIMENSIONS]
        fig.add_trace(go.Scatterpolar(r=r + r[:1], theta=theta + theta[:1], name=COUNTRIES[c], fill="toself" if c == FOCUS else None,
                                      opacity=0.9 if c == FOCUS else 0.75,
                                      line=dict(color=COLORS.get(c), width=4 if c == FOCUS else 2)))
    fig.update_layout(height=height, title="Perfil digital por dimensión (0–100)", polar=dict(radialaxis=dict(range=[0, 100])),
                      legend=dict(orientation="h", y=-0.1), margin=dict(l=40, r=40, t=60, b=10))
    return fig


def fig_heatmap(N, values, height=380):
    labs = [_lab(i) for i in INDICATORS]
    z = [[N.loc[c, i["col"]] * 100 for i in INDICATORS] for c in N.index]
    txt = [[("n.d." if values.loc[c, i["col"]] != values.loc[c, i["col"]] else f'{values.loc[c, i["col"]]:,.1f}')
            for i in INDICATORS] for c in N.index]
    fig = go.Figure(go.Heatmap(z=z, x=labs, y=[COUNTRIES[c] for c in N.index], text=txt, texttemplate="%{text}",
                               colorscale="RdYlGn", zmin=0, zmax=100, colorbar=dict(title="Norm.")))
    fig.update_layout(height=height, title="Valores observados (texto) y posición normalizada (color; el costo está invertido)",
                      margin=dict(l=10, r=10, t=50, b=10))
    fig.update_xaxes(tickangle=-30)
    return fig


def fig_clusters(res, drs, height=400):
    pcs, lab = res["pcs"], res["labels"]
    fig = go.Figure()
    for g in sorted(lab.unique()):
        idx = lab[lab == g].index
        fig.add_trace(go.Scatter(x=pcs.loc[idx, "PC1"], y=pcs.loc[idx, "PC2"], mode="markers+text", name=f"Grupo {g}",
                                 text=[f"{COUNTRIES[c]}<br>DRS {drs[c]:.0f}" for c in idx], textposition="top center",
                                 marker=dict(size=16, line=dict(width=2, color="#222"))))
    fig.update_layout(height=height, title=f"Perfiles digitales (K-means, k={res['k']}) en 2 componentes principales",
                      xaxis_title="PC1", yaxis_title="PC2", margin=dict(l=10, r=10, t=50, b=10))
    return fig
