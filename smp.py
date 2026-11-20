"""Base visual común de los casos de análisis de SMP Soluciones.

La misma copia de este archivo vive en superstore-data, ecommerce_data y crypto-data.
Si cambias algo aquí, cópialo a las otras dos carpetas.
"""
from html import escape

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

# ------------------------------------------------------------------ colores
MARINO = "#03112C"      # fondo de SMP
SUPERFICIE = "#08193A"  # tarjetas y gráficos
SUPERFICIE_2 = "#0C2757"
TEXTO = "#F2F6FF"
SUAVE = "#C9D4E8"
TENUE = "#8696B4"
LINEA = "rgba(255,255,255,.09)"
AZUL_SMP = "#007BFD"

# Series de datos (validadas para daltonismo sobre el fondo marino)
SERIE = ["#3987e5", "#d95926", "#199e70"]
POSITIVO = "#3987e5"    # ganancia, legítimo, retenido
NEGATIVO = "#e66767"    # pérdida, fraude, riesgo
NEUTRO = "#3a4866"      # punto medio y "resto"
ESCALA_DIVERGENTE = [[0, "#c43d3d"], [0.25, "#e66767"], [0.5, NEUTRO], [0.75, "#5598e7"], [1, "#1c5cab"]]
ESCALA_AZUL = [[0, "#184f95"], [0.5, "#3987e5"], [1, "#9ec5f4"]]

FUENTE_TITULOS = "Sora"
FUENTE_CUERPO = "Manrope"
FUENTE_CIFRAS = "IBM Plex Mono"


# ------------------------------------------------------------------ idioma
def idioma():
    """Español por defecto; ?lang=en en el link abre en inglés."""
    lang = st.query_params.get("lang", "es")
    return "en" if lang == "en" else "es"


def selector_idioma(lang):
    elegido = st.segmented_control(
        "Idioma" if lang == "es" else "Language", ["ES", "EN"], default=lang.upper(), key="selector_idioma",
        label_visibility="collapsed",
    )
    if elegido and elegido.lower() != lang:
        if elegido == "EN":
            st.query_params["lang"] = "en"
        else:
            st.query_params.pop("lang", None)
        st.rerun()


# ------------------------------------------------------------------ formato
def _local(txt, lang):
    """1,234.5 -> 1.234,5 en español."""
    if lang != "es":
        return txt
    return txt.replace(",", "§").replace(".", ",").replace("§", ".")


def dinero(v, lang="es", decimales=0, moneda="$"):
    signo = "-" if v < 0 else ""
    v = abs(v)
    if v >= 1_000_000:
        txt = f"{moneda}{v / 1_000_000:,.2f}M"
    elif v >= 10_000:
        txt = f"{moneda}{v / 1_000:,.0f}K"
    else:
        txt = f"{moneda}{v:,.{decimales}f}"
    return signo + _local(txt, lang)


def numero(v, lang="es", decimales=0):
    return _local(f"{v:,.{decimales}f}", lang)


def pct(v, lang="es", decimales=1):
    return _local(f"{v:,.{decimales}f}%", lang)


# ------------------------------------------------------------------ estilos
def estilos(acento="#5CABFF"):
    st.markdown(
        f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@500;600;700&family=Manrope:wght@400;500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap');
:root {{
  --marino:{MARINO}; --sup:{SUPERFICIE}; --sup2:{SUPERFICIE_2}; --texto:{TEXTO}; --suave:{SUAVE};
  --tenue:{TENUE}; --linea:{LINEA}; --azul:{AZUL_SMP}; --acento:{acento};
  --pos:{POSITIVO}; --neg:{NEGATIVO};
  --titulos:'Sora','Segoe UI',system-ui,sans-serif; --cuerpo:'Manrope','Segoe UI',system-ui,sans-serif;
  --cifras:'IBM Plex Mono',ui-monospace,Consolas,monospace;
}}

/* ---------- base ---------- */
.stApp {{background: radial-gradient(1000px 480px at 85% -160px, color-mix(in srgb, var(--acento) 16%, transparent), transparent 70%), var(--marino);}}
.stApp, .stApp p, .stApp li, .stApp label, .stApp input, .stApp button, .stApp span {{font-family:var(--cuerpo);}}
.stApp h1, .stApp h2, .stApp h3, .stApp h4 {{font-family:var(--titulos); color:var(--texto); letter-spacing:-.01em;}}
[data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] * {{font-family:var(--cuerpo);}}
[data-testid="stHeader"] {{background:transparent; height:0;}}
[data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], [data-testid="stHeaderActionElements"] {{display:none;}}
[data-testid="stMainBlockContainer"] {{max-width:1180px; padding:2.2rem 1.25rem 3rem;}}
:focus-visible {{outline:2px solid var(--acento) !important; outline-offset:3px;}}

/* ---------- barra superior ---------- */
.barra {{display:flex; align-items:center; gap:.7rem; font:600 .74rem/1 var(--cifras); letter-spacing:.14em;
  text-transform:uppercase; color:var(--tenue); padding-top:.45rem;}}
.barra .logo {{display:inline-grid; place-items:center; width:30px; height:30px; border-radius:9px;
  background:linear-gradient(135deg, var(--azul), #0052D6); color:#fff; font:700 .72rem/1 var(--titulos); letter-spacing:0;}}
.barra b {{color:var(--suave); font-weight:600;}}

/* ---------- encabezado ---------- */
.cab {{margin:2.4rem 0 1.6rem; max-width:52rem;}}
.cab .eb {{font:600 .74rem/1 var(--cifras); letter-spacing:.16em; text-transform:uppercase; color:var(--acento);}}
.cab h1 {{font:700 clamp(2rem,4.6vw,3.3rem)/1.08 var(--titulos) !important; letter-spacing:-.03em !important;
  margin:.8rem 0 .9rem !important; padding:0 !important; text-wrap:balance;}}
.cab h1 em {{font-style:normal; color:var(--acento);}}
.cab p {{color:var(--suave); font-size:1.08rem; line-height:1.6; margin:0; max-width:44rem;}}

/* ---------- cifras clave ---------- */
.kpis {{display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:12px; margin:.4rem 0 1.4rem;}}
.kpi {{background:var(--sup); border:1px solid var(--linea); border-radius:16px; padding:16px 18px 15px;}}
.kpi small {{display:block; font:600 .68rem/1.2 var(--cifras); letter-spacing:.12em; text-transform:uppercase; color:var(--tenue);}}
.kpi b {{display:block; font:600 clamp(1.45rem,2.6vw,1.9rem)/1.1 var(--cifras); color:var(--texto); margin:.55rem 0 .35rem; white-space:nowrap;}}
.kpi span {{font-size:.86rem; color:var(--suave); line-height:1.4;}}
.kpi.neg b {{color:var(--neg);}}
.kpi.acento {{border-color:color-mix(in srgb, var(--acento) 45%, transparent);
  background:linear-gradient(180deg, color-mix(in srgb, var(--acento) 10%, var(--sup)), var(--sup));}}

/* ---------- hallazgos ---------- */
.hallazgos {{display:grid; grid-template-columns:repeat(auto-fit,minmax(290px,1fr)); gap:14px; margin:.6rem 0 1.2rem;}}
.hz {{background:var(--sup); border:1px solid var(--linea); border-radius:18px; padding:20px 20px 18px; display:grid; gap:.55rem; align-content:start;}}
.hz .n {{font:600 .7rem/1 var(--cifras); letter-spacing:.14em; text-transform:uppercase; color:var(--acento);}}
.hz .cifra {{font:600 2rem/1.05 var(--cifras); color:var(--texto);}}
.hz.neg .cifra {{color:var(--neg);}}
.hz h3 {{font:600 1.08rem/1.3 var(--titulos) !important; margin:0 !important; padding:0 !important;}}
.hz p {{color:var(--suave); font-size:.95rem; line-height:1.55; margin:0;}}
.hz .accion {{margin-top:.35rem; padding:10px 12px; border-radius:11px; background:rgba(0,123,253,.12);
  border:1px solid rgba(92,171,255,.3); color:var(--texto); font-size:.9rem; line-height:1.45;}}
.hz .accion b {{font:600 .66rem/1 var(--cifras); letter-spacing:.12em; text-transform:uppercase; color:#5CABFF; display:block; margin-bottom:5px;}}

/* ---------- secciones ---------- */
.sec {{margin:1.6rem 0 .6rem;}}
.sec h2 {{font:600 1.45rem/1.25 var(--titulos) !important; margin:0 0 .35rem !important; padding:0 !important;}}
.sec p {{color:var(--suave); margin:0; max-width:46rem; line-height:1.55;}}
.lectura {{border-left:3px solid var(--acento); padding:.35rem 0 .35rem 1rem; color:var(--suave); margin:.3rem 0 1.3rem; line-height:1.6; max-width:50rem;}}
.lectura b {{color:var(--texto);}}
.chip {{display:inline-block; font:600 .68rem/1 var(--cifras); letter-spacing:.1em; text-transform:uppercase;
  padding:5px 9px; border-radius:999px; border:1px solid var(--linea); color:var(--suave); margin-right:6px;}}

/* ---------- pestañas ---------- */
[data-testid="stTabs"] [data-baseweb="tab-list"] {{gap:4px; border-bottom:1px solid var(--linea); overflow-x:auto; scrollbar-width:none;}}
[data-testid="stTabs"] [data-baseweb="tab"] {{height:46px; padding:0 14px; background:transparent;}}
[data-testid="stTabs"] [data-baseweb="tab"] p {{font:600 .78rem/1 var(--cuerpo); letter-spacing:.1em; text-transform:uppercase; color:var(--tenue);}}
[data-testid="stTabs"] [data-baseweb="tab"]:hover p {{color:var(--texto);}}
[data-testid="stTabs"] [aria-selected="true"] p {{color:var(--texto);}}
[data-testid="stTabs"] [data-baseweb="tab-highlight"] {{background:var(--acento); height:2px;}}
[data-testid="stTabs"] [data-baseweb="tab-border"] {{display:none;}}

/* ---------- filtros ---------- */
.filtros-t {{font:600 .68rem/1 var(--cifras); letter-spacing:.14em; text-transform:uppercase; color:var(--tenue); margin:0 0 .4rem;}}
[data-testid="stWidgetLabel"] p {{font:600 .68rem/1.2 var(--cifras) !important; letter-spacing:.12em; text-transform:uppercase; color:var(--tenue) !important;}}
[data-testid*="stBaseButton-pills"], [data-testid*="stBaseButton-segmented_control"] {{border-radius:999px !important;}}
[data-testid="stBaseButton-pillsActive"], [data-testid="stBaseButton-segmented_controlActive"] {{
  background:color-mix(in srgb, var(--acento) 22%, transparent) !important; border-color:var(--acento) !important; color:var(--texto) !important;}}
[data-baseweb="select"] > div {{background:var(--sup) !important; border-color:var(--linea) !important; border-radius:12px !important;}}
[data-baseweb="tag"] {{background:color-mix(in srgb, var(--acento) 22%, transparent) !important; border-radius:8px !important;}}

/* ---------- gráficos y tablas ---------- */
[data-testid="stPlotlyChart"] {{background:var(--sup); border:1px solid var(--linea); border-radius:18px; overflow:hidden;}}
[data-testid="stDataFrame"] {{border:1px solid var(--linea); border-radius:14px; overflow:hidden;}}
[data-testid="stExpander"] details {{border:1px solid var(--linea) !important; border-radius:14px !important; background:var(--sup);}}
[data-testid="stDownloadButton"] button {{border-radius:999px !important;}}

/* ---------- pie ---------- */
.pie {{margin-top:3rem; padding-top:1.4rem; border-top:1px solid var(--linea); display:flex; flex-wrap:wrap; gap:.8rem 1.4rem;
  align-items:center; justify-content:space-between; color:var(--tenue); font-size:.88rem;}}
.pie b {{color:var(--suave);}}

@media (max-width:640px) {{
  [data-testid="stMainBlockContainer"] {{padding:1.2rem 1rem 2.5rem;}}
  .cab {{margin-top:1.6rem;}}
  .barra .sub {{display:none;}}
  .kpis {{grid-template-columns:repeat(2,minmax(0,1fr));}}
  .kpi b {{font-size:1.3rem;}}
}}
</style>
""",
        unsafe_allow_html=True,
    )
    _plantilla_plotly()


def _plantilla_plotly():
    t = go.layout.Template()
    t.layout = go.Layout(
        font=dict(family=f"{FUENTE_CUERPO}, Segoe UI, sans-serif", color=SUAVE, size=13),
        title=dict(font=dict(family=f"{FUENTE_TITULOS}, sans-serif", color=TEXTO, size=16), x=0.01, xanchor="left", y=0.97),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=SERIE,
        margin=dict(l=20, r=24, t=60, b=20),
        xaxis=dict(gridcolor="rgba(255,255,255,.06)", zerolinecolor="rgba(255,255,255,.22)", linecolor="rgba(255,255,255,.12)",
                   tickfont=dict(color=TENUE, size=12), title=dict(font=dict(color=TENUE, size=12)), automargin=True),
        yaxis=dict(gridcolor="rgba(255,255,255,.06)", zerolinecolor="rgba(255,255,255,.22)", linecolor="rgba(255,255,255,0)",
                   tickfont=dict(color=TENUE, size=12), title=dict(font=dict(color=TENUE, size=12)), automargin=True),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="right", x=1, font=dict(color=SUAVE, size=12), bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor=SUPERFICIE_2, bordercolor="rgba(255,255,255,.18)", font=dict(family=FUENTE_CUERPO, color=TEXTO, size=13)),
        bargap=0.28,
        coloraxis=dict(colorbar=dict(outlinewidth=0, tickfont=dict(color=TENUE), thickness=10)),
    )
    t.data.bar = [go.Bar(marker=dict(line=dict(width=0), cornerradius=4))]
    pio.templates["smp"] = t
    pio.templates.default = "smp"


CONFIG_GRAFICO = {"displayModeBar": False, "responsive": True}


def grafico(fig, lang="es", alto=420):
    # En español: punto para miles y coma para decimales también dentro de los gráficos
    fig.update_layout(height=alto, separators=",." if lang == "es" else ".,")
    st.plotly_chart(fig, width="stretch", config=CONFIG_GRAFICO)


# ------------------------------------------------------------------ piezas
def barra_superior(nombre_caso, lang):
    izq, der = st.columns([5, 1], vertical_alignment="center")
    with izq:
        sub = "Casos de análisis de datos" if lang == "es" else "Data analysis case studies"
        st.markdown(
            f'<div class="barra"><span class="logo">SMP</span><b>SMP Soluciones</b>'
            f'<span class="sub">· {escape(sub)} · {escape(nombre_caso)}</span></div>',
            unsafe_allow_html=True,
        )
    with der:
        selector_idioma(lang)


def cabecera(eyebrow, titulo_html, bajada):
    """titulo_html admite <em> para resaltar con el color del caso."""
    st.markdown(
        f'<header class="cab"><div class="eb">{escape(eyebrow)}</div><h1>{titulo_html}</h1><p>{bajada}</p></header>',
        unsafe_allow_html=True,
    )


def kpis(items):
    """items: lista de dicts con etiqueta, valor, nota y tono opcional ('neg' o 'acento')."""
    html = "".join(
        f'<div class="kpi {i.get("tono", "")}"><small>{escape(i["etiqueta"])}</small><b>{escape(i["valor"])}</b>'
        f'<span>{i.get("nota", "")}</span></div>'
        for i in items
    )
    st.markdown(f'<div class="kpis">{html}</div>', unsafe_allow_html=True)


def hallazgos(items, etiqueta_accion):
    """items: dicts con n, cifra, titulo, texto, accion y tono opcional."""
    html = "".join(
        f'<article class="hz {i.get("tono", "")}"><div class="n">{escape(i["n"])}</div>'
        f'<div class="cifra">{escape(i["cifra"])}</div><h3>{i["titulo"]}</h3><p>{i["texto"]}</p>'
        + (f'<div class="accion"><b>{escape(etiqueta_accion)}</b>{i["accion"]}</div>' if i.get("accion") else "")
        + "</article>"
        for i in items
    )
    st.markdown(f'<div class="hallazgos">{html}</div>', unsafe_allow_html=True)


def seccion(titulo, texto=""):
    st.markdown(f'<div class="sec"><h2>{titulo}</h2>' + (f"<p>{texto}</p>" if texto else "") + "</div>", unsafe_allow_html=True)


def lectura(texto_html):
    st.markdown(f'<div class="lectura">{texto_html}</div>', unsafe_allow_html=True)


def pie(lang, fuente_html, herramientas=("Python", "SQL", "pandas", "Plotly", "Streamlit")):
    chips = "".join(f'<span class="chip">{escape(h)}</span>' for h in herramientas)
    hecho = "Análisis y desarrollo" if lang == "es" else "Analysis and development"
    st.markdown(
        f'<footer class="pie"><div>{hecho}: <b>SMP Soluciones</b> · {fuente_html}</div><div>{chips}</div></footer>',
        unsafe_allow_html=True,
    )
