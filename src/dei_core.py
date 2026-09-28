"""Núcleo de cálculo del Digital Readiness Score (DRS) — Equipo 4 (Ciencia).

Este módulo lo usan tanto el notebook como el dashboard, de modo que ambos
producen exactamente los mismos números.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

FOCUS = "MEX"
COUNTRIES = {
    "MEX": "México",
    "USA": "Estados Unidos",
    "DEU": "Alemania",
    "CHN": "China",
    "JPN": "Japón",
}
ISO3 = list(COUNTRIES)

DIMENSIONS = [
    "Infraestructura y conectividad",
    "Acceso y uso",
    "Calidad y asequibilidad",
    "Actividad económica digital",
    "Capacidad tecnológica e innovación",
]

# direction: +1 = más es mejor ; -1 = más es peor (se invierte al normalizar)
INDICATORS = [
    dict(id="I1", col="fixed_broadband", short="Banda ancha fija",
         official_name="Fixed broadband subscriptions (per 100 people)",
         label="Suscripciones a banda ancha fija (por 100 hab.)",
         dimension=DIMENSIONS[0], unit="por 100 habitantes", direction=1, weight=0.10,
         c4="Connectivity", code="IT.NET.BBND.P2",
         organismo="ITU (World Telecommunication/ICT Indicators Database)",
         plataforma="World Bank Indicators API",
         link="https://data.worldbank.org/indicator/IT.NET.BBND.P2",
         definition="Suscripciones a acceso a Internet de alta velocidad de línea fija (>=256 kbit/s) por cada 100 personas."),
    dict(id="I2", col="secure_servers", short="Servidores seguros",
         official_name="Secure Internet servers (per 1 million people)",
         label="Servidores de Internet seguros (por millón de hab.)",
         dimension=DIMENSIONS[0], unit="por millón de habitantes", direction=1, weight=0.10,
         c4="Compute (proxy)", code="IT.NET.SECR.P6",
         organismo="Netcraft, compilado por el Banco Mundial",
         plataforma="World Bank Indicators API",
         link="https://data.worldbank.org/indicator/IT.NET.SECR.P6",
         definition="Servidores que usan tecnología de cifrado en transacciones de Internet, por millón de personas."),
    dict(id="I3", col="internet_users", short="Uso de Internet",
         official_name="Individuals using the Internet (% of population)",
         label="Personas que usan Internet (% de la población)",
         dimension=DIMENSIONS[1], unit="% de la población", direction=1, weight=0.15,
         c4="Connectivity", code="IT.NET.USER.ZS",
         organismo="ITU (World Telecommunication/ICT Indicators Database)",
         plataforma="World Bank Indicators API",
         link="https://data.worldbank.org/indicator/IT.NET.USER.ZS",
         definition="Porcentaje de la población que usó Internet (desde cualquier lugar) en los últimos 3 meses."),
    dict(id="I4", col="broadband_basket", short="Costo banda ancha (% INB pc)",
         official_name="Fixed-broadband basket as a percentage of GNI per capita (verificar nombre exacto en el archivo descargado)",
         label="Canasta de banda ancha fija (% del INB per cápita)",
         dimension=DIMENSIONS[2], unit="% del INB per cápita", direction=-1, weight=0.15,
         c4="Connectivity", code="ITU DataHub (descarga CSV)",
         organismo="ITU",
         plataforma="ITU DataHub (descarga manual de CSV oficial)",
         link="https://datahub.itu.int/",
         definition="Precio mensual de la canasta de banda ancha fija como porcentaje del ingreso nacional bruto per cápita. Mayor costo relativo = menor asequibilidad (se invierte)."),
    dict(id="I5", col="ict_services_exports", short="Exportaciones servicios TIC",
         official_name="ICT service exports (% of service exports, BoP)",
         label="Exportaciones de servicios TIC (% de exportaciones de servicios)",
         dimension=DIMENSIONS[3], unit="% de exportaciones de servicios", direction=1, weight=0.10,
         c4="Context/Competency (indirecto)", code="BX.GSR.CCIS.ZS",
         organismo="FMI (Balanza de Pagos), compilado por el Banco Mundial",
         plataforma="World Bank Indicators API",
         link="https://data.worldbank.org/indicator/BX.GSR.CCIS.ZS",
         definition="Servicios de informática, comunicaciones y servicios de información y computación, como % de las exportaciones de servicios."),
    dict(id="I6", col="ict_goods_exports", short="Exportaciones bienes TIC",
         official_name="ICT goods exports (% of total goods exports)",
         label="Exportaciones de bienes TIC (% de exportaciones de bienes)",
         dimension=DIMENSIONS[3], unit="% de exportaciones de bienes", direction=1, weight=0.10,
         c4="Compute (indirecto)", code="TX.VAL.ICTG.ZS.UN",
         organismo="Naciones Unidas (UN Comtrade), compilado por el Banco Mundial",
         plataforma="World Bank Indicators API",
         link="https://data.worldbank.org/indicator/TX.VAL.ICTG.ZS.UN",
         definition="Equipos de cómputo y periféricos, comunicaciones, electrónica de consumo, componentes y otros bienes TIC, como % de las exportaciones de bienes."),
    dict(id="I7", col="rd_expenditure", short="Gasto en I+D (% PIB)",
         official_name="Research and development expenditure (% of GDP)",
         label="Gasto en investigación y desarrollo (% del PIB)",
         dimension=DIMENSIONS[4], unit="% del PIB", direction=1, weight=0.15,
         c4="Competency", code="GB.XPD.RSDV.GD.ZS",
         organismo="UNESCO Institute for Statistics, compilado por el Banco Mundial",
         plataforma="World Bank Indicators API",
         link="https://data.worldbank.org/indicator/GB.XPD.RSDV.GD.ZS",
         definition="Gasto interno bruto en I+D (sector público y privado) como % del PIB."),
    dict(id="I8", col="patents_per_million", short="Patentes residentes /millón",
         official_name="Patent applications, residents (IP.PAT.RESD) por millón de habitantes (SP.POP.TOTL)",
         label="Solicitudes de patente de residentes (por millón de hab.)",
         dimension=DIMENSIONS[4], unit="solicitudes por millón de habitantes", direction=1, weight=0.15,
         c4="Competency", code="IP.PAT.RESD / SP.POP.TOTL",
         organismo="WIPO (patentes) y Banco Mundial (población)",
         plataforma="World Bank Indicators API (o WIPO IP Statistics Data Center si se coloca el CSV en data/raw)",
         link="https://data.worldbank.org/indicator/IP.PAT.RESD",
         definition="Solicitudes de patente presentadas por residentes de la economía ante su oficina nacional, normalizadas por población."),
]

COLS = [i["col"] for i in INDICATORS]
META = {i["col"]: i for i in INDICATORS}
ID2COL = {i["id"]: i["col"] for i in INDICATORS}


# ---------------------------------------------------------------- pesos / normalización
def weights(custom: dict | None = None) -> dict:
    """Pesos por columna, renormalizados para sumar exactamente 1."""
    base = {i["col"]: i["weight"] for i in INDICATORS}
    if custom:
        base.update(custom)
    tot = sum(base.values())
    return {k: v / tot for k, v in base.items()}


def normalize(values: pd.DataFrame) -> pd.DataFrame:
    """Min-max entre las cinco economías (0 = peor, 1 = mejor). Invierte los indicadores con direction=-1.
    Los NaN se conservan (dato no disponible != 0)."""
    out = pd.DataFrame(index=values.index)
    for ind in INDICATORS:
        s = values[ind["col"]].astype(float)
        lo, hi = s.min(), s.max()
        if pd.isna(lo) or hi == lo:
            n = s.where(s.isna(), 0.5)
        else:
            n = (s - lo) / (hi - lo)
        out[ind["col"]] = 1 - n if ind["direction"] < 0 else n
    return out


def compute_drs(values: pd.DataFrame, custom_weights: dict | None = None):
    """Devuelve (N, contribuciones, DRS 0-100, cobertura de pesos).
    Si un país no tiene un indicador, sus pesos se reponderan entre los disponibles y se reporta la cobertura."""
    w = weights(custom_weights)
    N = normalize(values)
    W = pd.DataFrame({c: w[c] for c in COLS}, index=N.index).where(N.notna(), 0.0)
    coverage = W.sum(axis=1)
    W = W.div(W.sum(axis=1), axis=0)
    contrib = N.fillna(0) * W * 100
    drs = contrib.sum(axis=1)
    return N, contrib, drs, coverage


def dimension_scores(N: pd.DataFrame, custom_weights: dict | None = None) -> pd.DataFrame:
    w = weights(custom_weights)
    out = {}
    for d in DIMENSIONS:
        cols = [i["col"] for i in INDICATORS if i["dimension"] == d]
        Wd = pd.DataFrame({c: w[c] for c in cols}, index=N.index).where(N[cols].notna(), 0.0)
        Wd = Wd.div(Wd.sum(axis=1).replace(0, np.nan), axis=0)
        out[d] = (N[cols].fillna(0) * Wd).sum(axis=1, min_count=1) * 100
    return pd.DataFrame(out)


def gap_vs_others(N: pd.DataFrame, focus: str = FOCUS) -> pd.Series:
    """Diferencia (en puntos 0-100) entre el país foco y el promedio de los demás."""
    return (N.loc[focus] - N.drop(focus).mean()) * 100


# ---------------------------------------------------------------- clustering
def cluster_profiles(N: pd.DataFrame, seed: int = 42):
    """K-means sobre indicadores normalizados (estandarizados). Elige k por silhouette (k=2..3).
    Solo usa indicadores completos para los cinco países."""
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score

    X = N.dropna(axis=1)
    if X.shape[1] < 2 or len(X) < 4:
        return None
    Z = (X - X.mean()) / X.std(ddof=0).replace(0, 1)
    best, sil = None, {}
    for k in range(2, min(3, len(X) - 1) + 1):
        km = KMeans(n_clusters=k, n_init=50, random_state=seed).fit(Z)
        s = silhouette_score(Z, km.labels_) if len(set(km.labels_)) > 1 else -1
        sil[k] = float(s)
        if best is None or s > best[0]:
            best = (s, k, km.labels_)
    _, k, raw = best
    # etiquetas estables: el grupo 1 es el que contiene al país foco / primer país
    order, mapping = [], {}
    for lab in raw:
        if lab not in mapping:
            mapping[lab] = len(mapping) + 1
    labels = pd.Series([mapping[l] for l in raw], index=X.index, name="grupo")
    centroids = X.groupby(labels).mean() * 100
    # PCA 2D (SVD)
    U, S, _ = np.linalg.svd(Z.values - Z.values.mean(axis=0), full_matrices=False)
    pcs = pd.DataFrame(U[:, :2] * S[:2], index=X.index, columns=["PC1", "PC2"])
    return dict(labels=labels, k=k, silhouettes=sil, centroids=centroids, pcs=pcs, used=list(X.columns))


# ---------------------------------------------------------------- texto
def _fmt(col: str, v: float) -> str:
    return "n.d." if pd.isna(v) else f"{v:,.2f} ({META[col]['unit']})"


def _join(items):
    items = list(items)
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " y " + items[-1]


def describe_ranking(drs, contrib, focus=FOCUS) -> str:
    order = drs.sort_values(ascending=False)
    lista = "; ".join(f"{i+1}. {COUNTRIES[c]} ({v:.1f})" for i, (c, v) in enumerate(order.items()))
    r = list(order.index).index(focus) + 1
    top = contrib.loc[focus].idxmax()
    return (f"Orden por DRS: {lista}. {COUNTRIES[focus]} ocupa el lugar {r} de {len(order)}; "
            f"la distancia entre el primero y el último es de {order.iloc[0]-order.iloc[-1]:.1f} puntos y el indicador que más "
            f"aporta al DRS de {COUNTRIES[focus]} es «{META[top]['short']}» ({contrib.loc[focus, top]:.1f} puntos).")


def describe_gap(N, focus=FOCUS) -> str:
    g = gap_vs_others(N, focus).dropna()
    pos = [f"{META[c]['short']} ({v:+.0f})" for c, v in g[g > 0].sort_values(ascending=False).items()]
    neg = [f"{META[c]['short']} ({v:+.0f})" for c, v in g[g < 0].sort_values().items()]
    t = f"Frente al promedio normalizado de las otras cuatro economías, {COUNTRIES[focus]} está por encima en: {_join(pos) if pos else 'ningún indicador'}; "
    t += f"y por debajo en: {_join(neg) if neg else 'ningún indicador'} (diferencias en puntos de la escala 0-100)."
    return t


def describe_profiles(dim, drs, focus=FOCUS) -> str:
    rd = drs.rank(ascending=False, method="min")[focus]
    notes = []
    for d in DIMENSIONS:
        rk = dim[d].rank(ascending=False, method="min")[focus]
        if pd.notna(rk) and abs(rk - rd) >= 2:
            notes.append(f"en «{d}» ocupa el lugar {int(rk)} (frente al {int(rd)} del DRS global)")
    if notes:
        return f"{COUNTRIES[focus]} muestra un perfil que el DRS promedia: " + _join(notes) + "."
    return f"El perfil dimensional de {COUNTRIES[focus]} es en general consistente con su posición global (lugar {int(rd)})."


def build_diagnosis(values, N, drs, focus=FOCUS) -> str:
    """Diagnóstico final (<= 250 palabras) construido a partir de los resultados calculados."""
    name = COUNTRIES[focus]
    order = drs.sort_values(ascending=False)
    n = len(order)
    r = list(order.index).index(focus) + 1
    others = order.drop(focus)
    ranks = N.rank(ascending=False, method="min")
    gap = gap_vs_others(N, focus).dropna()
    s_col, b_col = gap.idxmax(), gap.idxmin()
    d = ((N - N.loc[focus]) ** 2).sum(axis=1) ** 0.5
    near = d.drop(focus).idxmin()
    far = d.drop(focus).idxmax()
    diffs = (N.loc[focus] - N.loc[near]).abs().dropna()
    dif_col = diffs.idxmax()

    p1 = (f"1) {name} obtiene un DRS de {drs[focus]:.1f}/100 y ocupa el lugar {r} de {n} (rango de las otras cuatro: "
          f"{others.min():.1f}–{others.max():.1f}). El índice es relativo a este grupo, no absoluto.")
    p2 = (f"2) {'Principal fortaleza' if gap[s_col] > 0 else 'Posición relativa más favorable'}: {META[s_col]['short']} — {_fmt(s_col, values.loc[focus, s_col])}, lugar {int(ranks.loc[focus, s_col])} de {n} "
          f"({gap[s_col]:+.0f} puntos frente al promedio de los otros cuatro).")
    p3 = (f"3) Principal brecha: {META[b_col]['short']} — {_fmt(b_col, values.loc[focus, b_col])}, lugar {int(ranks.loc[focus, b_col])} de {n} "
          f"({gap[b_col]:+.0f} puntos).")
    p4 = (f"4) {COUNTRIES[near]} es el punto de comparación más útil: tiene el perfil más cercano al de {name} (distancia euclidiana mínima "
          f"en los indicadores normalizados) y la diferencia más grande con él está en «{META[dif_col]['short']}», por lo que es la brecha más accionable; "
          f"el contraste máximo es con {COUNTRIES[far]}.")
    p5 = ("5) Limitación principal: solo cinco economías y ocho indicadores; la normalización min-max depende de los extremos del grupo, "
          "varios indicadores son proxies (p. ej., servidores seguros como cómputo) y ninguno mide calidad del servicio, habilidades ni IA. "
          "Además, los años de observación pueden diferir entre indicadores (ver Source Log).")
    text = "\n\n".join([p1, p2, p3, p4, p5])
    assert len(text.split()) <= 250, f"Diagnóstico de {len(text.split())} palabras (>250)"
    return text


# ---------------------------------------------------------------- documentación
def build_data_dictionary() -> pd.DataFrame:
    rows = [
        dict(variable="iso3", tipo="texto", descripcion="Código ISO 3166-1 alfa-3 de la economía", unidad="—", fuente="ISO 3166", valores_faltantes="No aplica"),
        dict(variable="country", tipo="texto", descripcion="Nombre de la economía (español)", unidad="—", fuente="ISO 3166", valores_faltantes="No aplica"),
    ]
    for i in INDICATORS:
        rows.append(dict(variable=i["col"], tipo="numérico (float)",
                         descripcion=f'[{i["id"]} · {i["dimension"]}] {i["definition"]}',
                         unidad=i["unit"], fuente=f'{i["organismo"]} — vía {i["plataforma"]}',
                         valores_faltantes="Vacío (NaN) = dato no disponible; 0 = valor cero observado"))
        rows.append(dict(variable=f'{i["col"]}_year', tipo="entero (Int64)",
                         descripcion=f'Año de observación del indicador {i["id"]} para esa economía',
                         unidad="año", fuente="Mismo que el indicador", valores_faltantes="Vacío si el indicador no está disponible"))
    return pd.DataFrame(rows)


def build_source_log(years: dict | None = None, methods: dict | None = None, official: dict | None = None,
                     retrieved: str = "") -> pd.DataFrame:
    """years: {col: {iso3: year}}, methods: {col: texto sobre selección de año}, official: {col: (nombre, definición)} de la API."""
    rows = []
    for i in INDICATORS:
        yrs = ""
        if years and i["col"] in years:
            yrs = "; ".join(f"{k}:{'n.d.' if pd.isna(v) else int(v)}" for k, v in years[i["col"]].items())
        nombre, definicion = i["official_name"], i["definition"]
        if official and i["col"] in official:
            nombre, definicion = official[i["col"]]
        transf = ("Ninguna (valor original)" if i["id"] != "I8" else
                  "patentes_residentes / población_total × 1,000,000 (mismo año)")
        if i["id"] == "I4":
            transf = "Ninguna sobre el valor; en el DRS se invierte (menor costo = mejor)."
        rows.append(dict(
            id=i["id"], variable=i["col"], nombre_oficial=nombre, definicion=definicion, unidad=i["unit"],
            organismo_original=i["organismo"], plataforma_acceso=i["plataforma"], codigo_indicador=i["code"],
            liga_origen=i["link"], anio_observacion_por_pais=yrs or "se completa al ejecutar el notebook",
            criterio_de_anio=(methods or {}).get(i["col"], "se completa al ejecutar el notebook"),
            metodo_obtencion=("Descarga de CSV oficial y lectura programática con pandas" if i["id"] == "I4"
                              else "Consulta programática a la API v2 del Banco Mundial (JSON crudo guardado en data/raw/)"),
            transformacion=transf, dimension=i["dimension"], fecha_consulta=retrieved))
    return pd.DataFrame(rows)
