# Team04_DigitalEconomy — Digital Economy Intelligence Lab (Actividad 2 · Parte I)

**Equipo 4 · Sector Ciencia · Diagnóstico comparativo de economía digital**

## 1. ¿Qué es este proyecto?

Diagnóstico comparativo de la preparación de 5 economías (México, Estados Unidos, Alemania, China, Japón) para participar, generar y capturar valor en la economía digital. El país foco es **México**, obligatorio para el diagnóstico de brechas.

**Pregunta guía:** ¿qué tan preparada está cada economía para participar, generar y capturar valor en la economía digital, y cuáles son las fortalezas y brechas de México?

**Fuentes de datos oficiales:** ITU DataHub, Banco Mundial API (WDI), UN Comtrade, WIPO IP Statistics, UNESCO-UIS. **Cero datos sintéticos**; `NaN` = dato no disponible, nunca se confunde con 0.

---

## 2. Objetivo

Construir un **Digital Readiness Score (DRS)** relativizado al grupo de 5 economías usando exactamente 8 indicadores oficiales, y a partir de ahí diagnosticar la posición de México en términos de infraestructura, acceso, asequibilidad, actividad digital y capacidad tecnológica/innovación.

### Distribución de indicadores (8 en total):

- **2 infraestructura/conectividad** (I1, I2)
- **1 acceso/uso** (I3)
- **1 calidad/asequibilidad** (I4, invertido)
- **2 actividad económica digital** (I5, I6)
- **2 capacidad tecnológica/innovación** (I7, I8) — **30% peso** por ser sector Ciencia

### Fórmula DRS:

`DRS = w1·I1 + w2·I2 + ... + w8·I8`, con **suma de pesos = 1**

- **Normalización min‑máx** entre las 5 economías (0 = peor, 1 = mejor)
- **I4 invertido**: `I4_norm = 1 − (x − mín)/(máx − mín)` (mayor costo relativo = menor asequibilidad = peor)
- **Sentido**: +1 = más es mejor; −1 = más es peor (solo I4)
- **Pesos por defecto:** I1(0.10) + I2(0.10) + I3(0.15) + I4(0.15) + I5(0.10) + I6(0.10) + I7(0.15) + I8(0.15) = 1.00
- **Sensibilidad:** también se prueba con pesos iguales, sin I6, y z-score

**El DRS es relativo** al grupo de 5 países; **no interpretar** como nivel absoluto. Se incluye análisis de sensibilidad.

---

## 3. Los 8 indicadores (con detalle)

| ID | Indicador | Dimensión | Unidad | ¿Qué mide realmente? | Código WB/OT | Fuente oficial |
|---|---|---|---|---|---|---|
| **I1** | Suscripciones banda ancha fija /100 hab. | Infraestructura | por 100 hab. | ¿Tiene el país la infraestructura física de red? | `IT.NET.BBND.P2` | ITU (World Telecommunication/ICT Indicators Database) vía Banco Mundial |
| **I2** | Servidores de Internet seguros /millón hab. | Infraestructura | por millón | Proxy débil de capacidad de cómputo/servidores con cifrado | `IT.NET.SECR.P6` | Netcraft, compilado por el Banco Mundial |
| **I3** | Personas que usan Internet, % pob. | Acceso/uso | % de población | ¿La población efectivamente está conectada? | `IT.NET.USER.ZS` | ITU vía Banco Mundial |
| **I4** | Canasta banda ancha fija, % INB pc | Calidad/asequibilidad | % INB (invertido) | ¿La banda ancha es asequible? (mayor costo = peor, se invierte en normalización) | Datos ITU DataHub (CSV descargado) | ITU DataHub — descarga manual de CSV oficial |
| **I5** | Exportaciones de servicios TIC, % de servicios | Actividad digital | % exportaciones servicios | ¿Vende el país servicios digitales al mundo? | `BX.GSR.CCIS.ZS` | FMI (Balanza de Pagos), compilado por el Banco Mundial |
| **I6** | Exportaciones de bienes TIC, % de bienes | Actividad digital | % exportaciones bienes | ¿Exporta el country equipos de tecnología? (puede reflejar ensamblaje/maquila) | `TX.VAL.ICTG.ZS.UN` | Naciones Unidas (UN Comtrade), compilado por el Banco Mundial |
| **I7** | Gasto en I+D, % PIB | Capacidad/innovación | % PIB | ¿Invierte el país en generar conocimiento nuevo? | `GB.XPD.RSDV.GD.ZS` | UNESCO Institute for Statistics, compilado por el Banco Mundial |
| **I8** | Patentes de residentes por millón hab. | Capacidad/innovación | solicitudes/millón | ¿Genera el país propiedad intelectual? | `IP.PAT.RESD / SP.POP.TOTL` | WIPO (patentes) + Banco Mundial (población) |

**Notas sobre cada indicador:**

- **I1:** Suscripciones a acceso a Internet de alta velocidad de línea fija (>=256 kbit/s). Incluye cable modem, DSL, fibra, satélite, inalámbrico fijo. Excluye móviles.
- **I2:** Servidores que usan tecnología de cifrado en transacciones de Internet, por millón de personas. Es un **proxy** de capacidad de cómputo; no mide capacidad instalada real de centros de datos o GPU.
- **I3:** Porcentaje de la población que usó Internet (desde cualquier lugar) en los últimos 3 meses. Mide adopción, no calidad ni tipo de uso.
- **I4:** Precio mensual de la canasta de banda ancha fija (5GB) como porcentaje del ingreso nacional bruto per cápita. **Invertido** al normalizar: menor costo = mejor posición. Datos costosos (como México) quedan mejor después de la inversión.
- **I5:** Servicios de informática, comunicaciones y servicios de información y computación, como % de las exportaciones de servicios. Captura de valor externo mediante servicios digitales.
- **I6:** Equipos de cómputo y periféricos, comunicaciones, electrónica de consumo, componentes y otros bienes TIC, como % de las exportaciones de bienes. **Puede reflejar ensamblaje (valor agregado bajo) más que innovación propia.** Peso bajo (10%) a propósito.
- **I7:** Gasto interno bruto en I+D (sector público y privado) como % del PIB. Mide **esfuerzo insumo**, no resultados (patentes, publicaciones).
- **I8:** Solicitudes de patente presentadas por residentes de la economía ante su oficina normalizadas por población. Mide **capacidad de generar conocimiento protegible**.

---

## 4. ¿Cómo se calcula el DRS? (metodología resumida)

1. **Adquisición:** API v2 del Banco Mundial para I1‑I3, I5‑I8; CSV ITU DataHub para I4. Cada respuesta cruda se guarda sin modificar en `data/raw/wb_<COD>.json` y `data/raw/itu_fixed_broadband_basket.csv`.
2. **Selección de año:** año común más reciente con las 5 economías (≥2018). Si no hay año común, último dato por país y se reporta el desfase. **Nada se imputa.** NaN ≠ 0.
3. **Preparación:** revisión de faltantes, tipos, rangos (0–100), negativos, extremos (>3× mediana). Decisiones documentadas en el notebook.
4. **Normalización min‑máx** entre las 5 economías. I4 invertido.
5. **DRS = Σ wi · Ii_norm · 100.** Si un país falta un indicador, sus pesos se reponderan y se reporta cobertura.
6. **Resultados:** `data/processed/digital_economy_clean.csv` (5 × 8 + columnas `*_year`), `source_log.csv`, `data_dictionary.csv`, `drs_results.csv`, `diagnosis.txt`.

**Años observados (con datos reales):** I1‑I3, I5‑I6 (2024), I4 (2025), I7 (2023), I8 (2021). Hay dispersión de años; se reporta en la columna `*_year` y en el Source Log.

---

## 5. Resultados con datos reales

**Posiciones DRS (de mejor a peor, con pesos por defecto):**

1. China — **75.7**
2. Alemania — **64.1**
3. Estados Unidos — **69.2**
4. Japón — **52.2**
5. México — **4.7** (último lugar)

**Brecha principal de México:** **Gasto en I+D** (−91 puntos frente al promedio de las otras cuatro economías). México ocupa el lugar 5° de 5 en este indicador.

**Fortalea relativa de México:** **Exportaciones de bienes TIC** (lugar 2° del grupo, +11 pts frente al promedio). Es el indicador donde México tiene mejor posición relativa.

**Principales fortalezas por país:**

- **China:** lidera en I+D (patentes y gasto relativo) y exportaciones de bienes TIC.
- **Alemania:** fuerte en infraestructura (banda ancha, servidores) y I+D.
- **Estados Unidos:** destaca en exportaciones de servicios TIC y patentes.
- **Japón:** buena infraestructura y uso de Internet, pero menor I+D relativa.
- **México:** única fortaleza relativa en I6 (exportaciones bienes TIC); brechas grandes en I7 (I+D) e I4 (costo de banda ancha).

**Diagnóstico final** (126 palabras, bajo el límite de 250): Ver `diagnosis.txt` generado automáticamente. Texto cubre: posición relativa, fortaleza principal, brecha principal, punto de comparación útil y limitaciones del modelo.

---

## 6. Probar el dashboard

`streamlit run dashboard/app.py` (desde la raíz del proyecto)

Interfaz de una sola página con:

- **Barra lateral:** sliders 0‑40 por cada indicador (se renormalizan para sumar 1). Botón "Restablecer pesos".
- **KPIs:** DRS actual, posición de cada país (5 columnas).
- **Gráficos:**
  1. **Ranking DRS y aporte de cada indicador** (barras apiladas).
  2. **Brecha México vs. promedio de las otras 4 economías** (barras horizontales con cero central).
  3. **Radar de 5 dimensiones** (Infraestructura, Acceso, Asequibilidad, Actividad digital, Capacidad innovación).
  4. **Heatmap valores/posición** (color = posición normalizada; I4 ya considera que menor costo es mejor).
- **Expander "Perfiles digitales (clustering exploratorio, n = 5):** K‑means sobre indicadores normalizados y estandarizados, k=2..3 por silhouette, PCA 2D. Se declara que n=5 es exploratorio.
- **Diagnóstico recalculado en vivo** según los pesos de la barra lateral.
- **Expander "Datos, fuentes y años de observación":** muestra el dataframe limpio, años por indicador y source_log.csv.

**Notas de uso:**

- Si aún no existe `data/processed/digital_economy_clean.csv`, el dashboard muestra error claro.
- Los sliders permiten hacer **análisis de sensibilidad**: "¿cómo cambia el ranking si valoramos más la innovación (I7+I8)?".
- El diagnóstico, ranking y gráficos se actualizan automáticamente al mover los sliders.
- Los pesos se renormalizan siempre; la suma mostrada debe ser 1.00.

---

## 7. Estructura de carpetas y entregables

```
Team04_DigitalEconomy/
│
├── data/raw/                # Respuestas originales de APIs/CSV (NUNCA se editan)
│   ├── wb_*.json            # 7 respuestas del Banco Mundial (códigos I1‑I8 + población)
│   ├── itu_fixed_broadband_basket.csv  # CSV ITU DataHub (indicador I4)
│   └── .gitkeep
│
├── data/processed/          # Archivos generados por el notebook
│   ├── digital_economy_clean.csv  # 5 economías × 8 indicadores + columnas *_year
│   ├── drs_results.csv        # Normalizados, aportes por indicador, dimensiones, DRS (0‑100)
│   ├── diagnosis.txt          # Diagnóstico final ≤ 250 palabras (generado con assert)
│   └── .gitkeep
│
├── notebooks/
│   └── Digital_Economy_Analysis.ipynb  # Ejecutado con outputs reales (datos, cálculos, diagnósticos)
│
├── dashboard/
│   └── app.py  # Streamlit, una sola página (sliders, KPIs, 4 gráficos, clustering, diagnóstico)
│
├── source_log.csv  # Trazabilidad completa: organismo, indicador, código, año por país, método de obtención
├── data_dictionary.csv  # Diccionario completo de variables (tipo, descripción, unidad, fuente, valores faltantes)
│
└── README.md  # Este archivo (explicación del proyecto, indicadores, metodología, resultados)
```

---

## 8. Requisitos para reproducir el proyecto

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   # pandas>=2.0, numpy>=1.24, requests>=2.31, plotly>=5.20,
   # scikit-learn>=1.3, streamlit>=1.35, jupyter, nbformat
   ```

2. **Descargar datos reales (paso indispensable):**
   - Entrar a [ITU DataHub](https://datahub.itu.int/), buscar el indicador **"Fixed-broadband basket as a percentage of GNI per capita"**.
   - Descargar para las 5 economías (todos los años) en formato CSV.
   - Guardar **sin editar** como `data/raw/itu_fixed_broadband_basket.csv`.
   - *(Opcional)* Descargar de **WIPO IP Statistics Data Center** las solicitudes de patente de residentes y guardar como `data/raw/wipo_patents_residents.csv`. Si no existe, el notebook usa la serie WIPO servida por el Banco Mundial.

3. **Ejecutar el notebook completo:**
   ```bash
   jupyter nbconvert --to notebook --execute --inplace notebooks/Digital_Economy_Analysis.ipynb
   ```
   - Se ejecuta desde `notebooks/` o la raíz.
   - En la primera corrida con datos reales pueden aparecer errores por formato de CSV; se deben ajustar los candidatos de columnas si `load_generic_csv` no los reconoce.
   - Si algún código WB no devuelve datos, ajustar en `dei_core.INDICATORS`.
   - Si un país (p. ej. China) no tiene un indicador dentro de la ventana, queda NaN y el DRS repondera; se reporta sin imputar.

4. **Generar los entregables:** el notebook crea automáticamente:
   - `data/processed/digital_economy_clean.csv`
   - `source_log.csv` (con años, fecha y nombres oficiales de la API)
   - `data_dictionary.csv`
   - `drs_results.csv`
   - `diagnosis.txt`

5. **Probar el dashboard:**
   ```bash
   streamlit run dashboard/app.py
   ```
   - Debe verse en una sola pantalla razonable.
   - Revisar que no haya errores y pulir diseño si hace falta.

---

## 9. Reglas y advertencias clave (imperdibles)

- **No hay datos sintéticos** ni completados a mano. Un valor no disponible queda vacío (`NaN`) y **nunca** se confunde con cero.
- **Desfases de años** entre indicadores deben reportarse (columnas `*_year` y sección 2 del notebook). **Nada se imputa.**
- **DRS relativo** al grupo de 5 economías: **no interpretarlo** como nivel absoluto; la sensibilidad está incluida.
- **I6 (bienes TIC)** puede reflejar ensamblaje/maquila (relevante para México) y **no captura de valor**; peso bajo (10%) a propósito.
- **I2** es un proxy débil de Compute; **no hay indicador de calidad del servicio** (velocidad/latencia): se declara, no se fuerza.
- Con **n=5**, clustering y correlaciones son **exploratorios**.
- **Ningún archivo de `data/raw/` se edita jamás.** Quedarán los JSON/CSV originales sin tocar.
- **Mínimo 3 visualizaciones**, cada una con las preguntas: *"¿Qué observo? / ¿Qué significa? / ¿Qué no puedo concluir?".
- **Diagnóstico final ≤ 250 palabras** con `assert` de verificación de longitud.
- **Pesos suman 1.00**; capacidad tecnológica pesa 30% por ser el sector Ciencia.

---
