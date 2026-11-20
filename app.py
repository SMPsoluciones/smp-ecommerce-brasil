"""Olist · ¿Dónde compran los clientes y cuántos vuelven?  Caso de análisis de SMP Soluciones.

Correr:  python -m streamlit run app.py
Datos:   datos/clientes.csv.gz (se genera con preparar_datos.py)
"""
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import smp

st.set_page_config(page_title="Olist · SMP Soluciones", page_icon="📦", layout="wide",
                   initial_sidebar_state="collapsed")

ACENTO = "#F5B941"
lang = smp.idioma()
smp.estilos(ACENTO)

# ------------------------------------------------------------------ referencia por estado
# Nombre, centro aproximado (lat, lon) y población (IBGE, Censo 2022).
ESTADOS = {
    "AC": ("Acre", -9.0, -70.5, 830_018), "AL": ("Alagoas", -9.6, -36.6, 3_127_683),
    "AP": ("Amapá", 1.4, -51.8, 733_759), "AM": ("Amazonas", -4.2, -64.6, 3_941_613),
    "BA": ("Bahia", -12.5, -41.7, 14_141_626), "CE": ("Ceará", -5.2, -39.5, 8_794_957),
    "DF": ("Distrito Federal", -15.8, -47.9, 2_817_381), "ES": ("Espírito Santo", -19.6, -40.7, 3_833_712),
    "GO": ("Goiás", -16.0, -49.6, 7_056_495), "MA": ("Maranhão", -5.0, -45.3, 6_776_699),
    "MT": ("Mato Grosso", -12.9, -55.9, 3_658_649), "MS": ("Mato Grosso do Sul", -20.5, -54.8, 2_757_013),
    "MG": ("Minas Gerais", -18.5, -44.6, 20_539_989), "PA": ("Pará", -3.8, -52.5, 8_120_131),
    "PB": ("Paraíba", -7.1, -36.8, 3_974_687), "PR": ("Paraná", -24.6, -51.6, 11_444_380),
    "PE": ("Pernambuco", -8.4, -37.9, 9_058_931), "PI": ("Piauí", -7.7, -42.7, 3_271_199),
    "RJ": ("Rio de Janeiro", -22.3, -42.7, 16_054_524), "RN": ("Rio Grande do Norte", -5.8, -36.6, 3_302_729),
    "RS": ("Rio Grande do Sul", -29.7, -53.2, 10_882_965), "RO": ("Rondônia", -10.9, -62.8, 1_581_196),
    "RR": ("Roraima", 2.0, -61.4, 636_707), "SC": ("Santa Catarina", -27.3, -50.5, 7_610_361),
    "SP": ("São Paulo", -22.2, -48.7, 44_411_238), "SE": ("Sergipe", -10.6, -37.4, 2_210_004),
    "TO": ("Tocantins", -10.2, -48.3, 1_511_460),
}
REGIONES = ["Sudeste", "Sul", "Nordeste", "Centro-Oeste", "Norte"]
MIN_ESTADO = 300   # clientes mínimos para comparar la recompra entre estados

# ------------------------------------------------------------------ textos
T = {
    "es": dict(
        caso="Olist",
        eyebrow="Caso · E-commerce en Brasil · 2016–2018",
        titulo="¿Dónde compran los clientes de <em>Olist</em> y cuántos vuelven?",
        bajada="Olist conecta pequeñas tiendas con los grandes marketplaces de Brasil. "
               "Analizamos {pedidos} pedidos de {clientes} personas en {estados} estados para ver dónde está la demanda, "
               "dónde falta y cuántos clientes repiten.",
        f_region="Región", f_estado="Estado", todos="Todos los estados",
        regiones={"Sudeste": "Sudeste", "Sul": "Sur", "Nordeste": "Nordeste", "Centro-Oeste": "Centro-Oeste", "Norte": "Norte"},
        k_clientes="Clientes", k_recompra="Volvieron a comprar", k_alcance="Alcance", k_penet="Clientes por 100 mil hab.",
        n_clientes="personas distintas · {p} pedidos", n_recompra="{n} personas con 2 pedidos o más",
        n_alcance="estados · {c} ciudades · {z} prefijos de CEP", n_penet="promedio de Brasil: {r}",
        tabs=["Resumen", "Geografía", "Recompra", "Ciudades", "Logística", "Datos"],
        accion="Qué hacer",
        hz1_t="La demanda se concentra en {n} {unidad}",
        hz1_estados="estados", hz1_ciudades="ciudades",
        hz1_x="{lista} suman {c} personas. Tienen {pp} de la población de la selección, así que la demanda está "
              "{rel} concentrada que la gente.",
        hz1_x_c="{lista} suman {c} personas.",
        hz1_mas="más", hz1_igual="igual de", hz1_menos="menos",
        hz1_a="Concentrar inventario, envíos rápidos y pauta pagada en {top}: ahí la misma inversión llega a más clientes.",
        hz2_t="Solo {p} de los clientes volvió a comprar",
        hz2_x="{n1} de {n} personas hizo un único pedido en el período del dataset.",
        hz2_x_rango=" Entre estados con al menos {m} clientes, la tasa va de {min} en {emin} a {max} en {emax}.",
        hz2_x_parejo=" Es baja en todas partes: no es un problema de una región, es del recorrido después de la compra.",
        hz2_a="Armar un flujo de segunda compra (WhatsApp o email unos días después de la entrega, con un incentivo) "
              "y medir la tasa de recompra cada mes.",
        hz3_t="{estado} es el mercado con más espacio para crecer",
        hz3_x="Tiene {pob} millones de habitantes y {r} clientes por cada 100 mil, contra {rb} en Brasil. "
              "Al promedio nacional serían {extra} clientes más.",
        hz3_a="Probar una campaña en {estado} empezando por {ciudad}, su ciudad con más clientes, y medir el costo por cliente nuevo.",
        hz3_t_ok="Todos los estados elegidos superan el promedio de Brasil",
        hz3_x_ok="La selección tiene {r} clientes por cada 100 mil habitantes, contra {rb} en Brasil. "
                 "El más bajo de la selección, {estado}, tiene {re}.",
        hz3_t_uno="{estado} ya supera el promedio de Brasil",
        hz3_x_uno="Tiene {r} clientes por cada 100 mil habitantes, contra {rb} en Brasil.",
        hz3_a_ok="Aquí la prioridad es que los clientes actuales vuelvan, no salir a buscar más.",
        r_tit="Peso en clientes contra peso en población",
        r_txt="Si una barra azul supera a la naranja, esa zona compra más de lo que pesa en habitantes.",
        r_lect="<b>{alta}</b> tiene {pc} de los clientes con {pp} de la población. "
               "<b>{baja}</b> tiene {pc2} de los clientes con {pp2} de la población.",
        cuota_cli="Clientes", cuota_pob="Población", zona="Zona",
        g_mapa="Clientes por estado", g_mapa_txt="Cada círculo es un estado; el tamaño es la cantidad de clientes.",
        g_bar="Clientes por estado", g_pen="Clientes por cada 100 mil habitantes",
        g_pen_txt="Azul: por encima del promedio de Brasil. Rojo: por debajo. La línea marca el promedio.",
        g_lect="Los 3 primeros estados ({lista}) tienen {p3} de los clientes; los 5 primeros, {p5}. "
               "La penetración va de {max} cada 100 mil en {emax} a {min} en {emin}.",
        promedio="Promedio Brasil",
        clientes="Clientes", pedidos="Pedidos", poblacion="Población", cuota="Participación", penet="Por 100 mil hab.",
        estado="Estado", region="Región", ciudad="Ciudad", cep="Prefijo de CEP", recompra="Recompra",
        rc_tit="¿Cuántos pedidos hace cada persona?",
        rc_txt="Cada customer_id del origen es un pedido; aquí se cuentan pedidos por persona (customer_unique_id).",
        rc_dist="Personas según cantidad de pedidos", n_ped="Pedidos por persona", personas="Personas",
        rc_lect="<b>{p1}</b> de las personas hizo un solo pedido. De las {n2} que repitieron, {pp2} se quedó en dos pedidos.",
        rc_est="Recompra por estado", rc_est_txt="Estados con al menos {m} clientes en la selección. La línea marca el total.",
        rc_lect2="La diferencia entre el estado con más recompra y el de menos es de {d} puntos: "
                 "el problema no depende de dónde vive el cliente.",
        rc_lect2b="La diferencia entre el estado con más recompra ({emax}, {max}) y el de menos ({emin}, {min}) es de {d} puntos.",
        rc_nota="No hay fechas en esta tabla, así que no se puede medir abandono (churn); "
                "solo cuántas personas compraron más de una vez en el período.",
        total="Total",
        c_tit="Las ciudades con más clientes", c_txt="Las 15 primeras de la selección.",
        c_curva="Participación acumulada de las ciudades", c_curva_txt="Ciudades ordenadas de más a menos clientes.",
        c_rank="Ciudades (ordenadas)", acum="Acumulado",
        c_lect="La ciudad con más clientes, <b>{top}</b>, tiene {ptop} del total. Las 10 primeras reúnen {p10}. "
               "En el otro extremo, {nc} de las {total} ciudades ({pc}) tienen menos de 10 clientes.",
        l_tit="¿Qué tan concentrados están los puntos de entrega?",
        l_txt="El prefijo de CEP (5 dígitos) marca una zona de reparto. Contamos clientes por prefijo.",
        l_top="Los 15 prefijos de CEP con más clientes", l_curva="Qué parte de los clientes cubre cada parte de los prefijos",
        l_x="Prefijos de CEP, de más a menos clientes", l_y="Clientes cubiertos",
        l_lect="El 10% de los prefijos con más clientes ({n10} de {total}) cubre <b>{p10}</b> de los clientes, y la mitad de los "
               "clientes vive en {n50} prefijos. {ztop} ({ctop}) es el prefijo con más clientes.",
        x_tit="Los datos", x_txt="Resumen por estado con los filtros que elegiste.",
        x_bajar="Descargar resumen por estado (CSV)", x_bajar2="Descargar clientes (CSV)",
        x_metodo="Cómo se hizo",
        x_metodo_txt="- **Fuente:** Brazilian E-Commerce Public Dataset by Olist (Kaggle), tabla de clientes: "
                     "99.441 filas. Según la documentación del dataset, cubre pedidos de 2016 a 2018.\n"
                     "- **Pedidos y personas:** cada `customer_id` es un pedido (Olist le da uno nuevo en cada compra). "
                     "La persona es `customer_unique_id`: 96.096 personas. El tablero cuenta personas como clientes y "
                     "pedidos como pedidos; nunca los mezcla.\n"
                     "- **Recompra, no churn:** la tabla no tiene fechas, así que no se puede medir abandono. "
                     "Lo que se mide es la parte de personas con 2 pedidos o más.\n"
                     "- **Una dirección por persona:** 252 personas compraron desde más de una dirección (39 desde más de "
                     "un estado). A cada una se le asigna la dirección con más pedidos; todos sus pedidos cuentan ahí.\n"
                     "- **Limpieza:** el prefijo de CEP se guardó como número y perdió el cero inicial en 23.995 filas "
                     "(01310 aparecía como 1310); se rellenó a 5 dígitos. Los nombres de ciudad vienen en minúscula y sin "
                     "tildes; 163 nombres se repiten en más de un estado, así que las ciudades se cuentan por ciudad + estado.\n"
                     "- **Población:** IBGE, Censo 2022. Es posterior a los datos (2016–2018), así que la penetración "
                     "es una aproximación para comparar estados, no una cifra exacta.\n"
                     "- **Herramientas:** SQL (SQLite) para la exploración, pandas para el cálculo y Plotly para los gráficos.",
        sin_datos="No hay clientes con esa combinación de filtros.",
        fuente="Datos: Olist Brazilian E-Commerce (Kaggle) · Población: IBGE, Censo 2022",
    ),
    "en": dict(
        caso="Olist",
        eyebrow="Case · E-commerce in Brazil · 2016–2018",
        titulo="Where do <em>Olist</em> customers buy, and how many come back?",
        bajada="Olist connects small shops with Brazil's large marketplaces. "
               "We analyzed {pedidos} orders from {clientes} people in {estados} states to see where demand is, "
               "where it is missing and how many customers buy again.",
        f_region="Region", f_estado="State", todos="All states",
        regiones={"Sudeste": "Southeast", "Sul": "South", "Nordeste": "Northeast", "Centro-Oeste": "Center-West", "Norte": "North"},
        k_clientes="Customers", k_recompra="Bought again", k_alcance="Reach", k_penet="Customers per 100k people",
        n_clientes="distinct people · {p} orders", n_recompra="{n} people with 2 or more orders",
        n_alcance="states · {c} cities · {z} ZIP prefixes", n_penet="Brazil average: {r}",
        tabs=["Summary", "Geography", "Repeat buying", "Cities", "Logistics", "Data"],
        accion="What to do",
        hz1_t="Demand is concentrated in {n} {unidad}",
        hz1_estados="states", hz1_ciudades="cities",
        hz1_x="{lista} add up to {c} people. They hold {pp} of the selection's population, so demand is "
              "{rel} concentrated than people are.",
        hz1_x_c="{lista} add up to {c} people.",
        hz1_mas="more", hz1_igual="as", hz1_menos="less",
        hz1_a="Focus stock, fast shipping and paid ads on {top}: that is where the same spend reaches the most customers.",
        hz2_t="Only {p} of customers bought again",
        hz2_x="{n1} of {n} people placed a single order during the dataset period.",
        hz2_x_rango=" Across states with at least {m} customers, the rate goes from {min} in {emin} to {max} in {emax}.",
        hz2_x_parejo=" It is low everywhere: this is not a regional problem, it is about what happens after the purchase.",
        hz2_a="Build a second-purchase flow (WhatsApp or email a few days after delivery, with an incentive) "
              "and track the repeat rate every month.",
        hz3_t="{estado} is the market with the most room to grow",
        hz3_x="It has {pob} million people and {r} customers per 100k, versus {rb} across Brazil. "
              "At the national average it would have {extra} more customers.",
        hz3_a="Test a campaign in {estado}, starting with {ciudad}, its city with the most customers, and track cost per new customer.",
        hz3_t_ok="Every selected state is above the Brazil average",
        hz3_x_ok="The selection has {r} customers per 100k people, versus {rb} across Brazil. "
                 "The lowest in the selection, {estado}, has {re}.",
        hz3_t_uno="{estado} is already above the Brazil average",
        hz3_x_uno="It has {r} customers per 100k people, versus {rb} across Brazil.",
        hz3_a_ok="Here the priority is getting current customers to come back, not finding more.",
        r_tit="Share of customers versus share of population",
        r_txt="When the blue bar is taller than the orange one, that area buys more than its population weight.",
        r_lect="<b>{alta}</b> has {pc} of customers with {pp} of the population. "
               "<b>{baja}</b> has {pc2} of customers with {pp2} of the population.",
        cuota_cli="Customers", cuota_pob="Population", zona="Area",
        g_mapa="Customers by state", g_mapa_txt="Each circle is a state; its size is the number of customers.",
        g_bar="Customers by state", g_pen="Customers per 100k people",
        g_pen_txt="Blue: above the Brazil average. Red: below. The line marks the average.",
        g_lect="The top 3 states ({lista}) hold {p3} of customers; the top 5, {p5}. "
               "Penetration goes from {max} per 100k in {emax} to {min} in {emin}.",
        promedio="Brazil average",
        clientes="Customers", pedidos="Orders", poblacion="Population", cuota="Share", penet="Per 100k people",
        estado="State", region="Region", ciudad="City", cep="ZIP prefix", recompra="Repeat rate",
        rc_tit="How many orders does each person place?",
        rc_txt="Each customer_id in the source is one order; here we count orders per person (customer_unique_id).",
        rc_dist="People by number of orders", n_ped="Orders per person", personas="People",
        rc_lect="<b>{p1}</b> of people placed a single order. Of the {n2} who came back, {pp2} stopped at two orders.",
        rc_est="Repeat rate by state", rc_est_txt="States with at least {m} customers in the selection. The line marks the total.",
        rc_lect2="The gap between the state with the highest repeat rate and the lowest is {d} points: "
                 "the problem does not depend on where the customer lives.",
        rc_lect2b="The gap between the state with the highest repeat rate ({emax}, {max}) and the lowest ({emin}, {min}) is {d} points.",
        rc_nota="This table has no dates, so churn cannot be measured; "
                "only how many people bought more than once during the period.",
        total="Total",
        c_tit="Cities with the most customers", c_txt="Top 15 in the selection.",
        c_curva="Cumulative share of cities", c_curva_txt="Cities sorted from most to fewest customers.",
        c_rank="Cities (sorted)", acum="Cumulative",
        c_lect="The city with the most customers, <b>{top}</b>, has {ptop} of the total. The top 10 hold {p10}. "
               "At the other end, {nc} of the {total} cities ({pc}) have fewer than 10 customers.",
        l_tit="How concentrated are delivery points?",
        l_txt="The ZIP (CEP) prefix (5 digits) marks a delivery zone. We count customers per prefix.",
        l_top="The 15 ZIP prefixes with the most customers", l_curva="How many customers each share of prefixes covers",
        l_x="ZIP prefixes, from most to fewest customers", l_y="Customers covered",
        l_lect="The top 10% of prefixes ({n10} of {total}) cover <b>{p10}</b> of customers, and half of all customers "
               "live in {n50} prefixes. {ztop} ({ctop}) is the prefix with the most customers.",
        x_tit="The data", x_txt="Summary by state with the filters you chose.",
        x_bajar="Download state summary (CSV)", x_bajar2="Download customers (CSV)",
        x_metodo="How it was done",
        x_metodo_txt="- **Source:** Brazilian E-Commerce Public Dataset by Olist (Kaggle), customers table: "
                     "99,441 rows. According to the dataset documentation, it covers orders from 2016 to 2018.\n"
                     "- **Orders and people:** each `customer_id` is one order (Olist issues a new one per purchase). "
                     "The person is `customer_unique_id`: 96,096 people. The dashboard counts people as customers and "
                     "orders as orders; it never mixes them.\n"
                     "- **Repeat rate, not churn:** the table has no dates, so churn cannot be measured. "
                     "What we measure is the share of people with 2 or more orders.\n"
                     "- **One address per person:** 252 people bought from more than one address (39 from more than one "
                     "state). Each is assigned the address with the most orders; all their orders count there.\n"
                     "- **Cleaning:** the ZIP prefix was stored as a number and lost its leading zero in 23,995 rows "
                     "(01310 showed as 1310); it was padded back to 5 digits. City names come lowercase and without "
                     "accents; 163 names repeat across states, so cities are counted as city + state.\n"
                     "- **Population:** IBGE, 2022 Census. It postdates the data (2016–2018), so penetration is an "
                     "approximation for comparing states, not an exact figure.\n"
                     "- **Tools:** SQL (SQLite) for exploration, pandas for calculations and Plotly for charts.",
        sin_datos="No customers match that combination of filters.",
        fuente="Data: Olist Brazilian E-Commerce (Kaggle) · Population: IBGE, 2022 Census",
    ),
}[lang]

p = lambda v, d=1: smp.pct(v, lang, d)      # noqa: E731
n = lambda v, d=0: smp.numero(v, lang, d)   # noqa: E731
REG = T["regiones"]


def lista_y(items):
    """'A, B y C' / 'A, B and C'."""
    items = list(items)
    y = " y " if lang == "es" else " and "
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + y + items[-1]


def nombre_ciudad(c):
    """'rio de janeiro' -> 'Rio de Janeiro', 'santa barbara d'oeste' -> 'Santa Barbara d'Oeste' (el origen no trae tildes)."""
    out = []
    for i, w in enumerate(c.split()):
        if i and w in {"de", "do", "da", "dos", "das", "e"}:
            out.append(w)
        elif w.startswith("d'") and len(w) > 2:
            out.append("d'" + w[2:].capitalize())
        else:
            out.append("-".join(x.capitalize() for x in w.split("-")))
    return " ".join(out)


# ------------------------------------------------------------------ datos
@st.cache_data
def cargar():
    d = pd.read_csv(Path(__file__).parent / "datos" / "clientes.csv.gz", dtype={"cep": str})
    d["ciudad_txt"] = d["ciudad"].map(nombre_ciudad) + " (" + d["estado"] + ")"
    return d


todo = cargar()
POB = pd.Series({k: v[3] for k, v in ESTADOS.items()})
TASA_BR = len(todo) / POB.sum() * 100_000
MAX_EST = todo["estado"].value_counts().max()   # escala fija de los círculos del mapa

# ------------------------------------------------------------------ portada
smp.barra_superior(T["caso"], lang)
smp.cabecera(T["eyebrow"], T["titulo"],
             T["bajada"].format(pedidos=n(todo["pedidos"].sum()), clientes=n(len(todo)), estados=todo["estado"].nunique()))

c1, c2 = st.columns([1.5, 1.5])
with c1:
    regiones = st.pills(T["f_region"], REGIONES, selection_mode="multi", format_func=lambda r: REG[r], key="regiones")
with c2:
    opciones = sorted(ESTADOS, key=lambda e: ESTADOS[e][0])
    estados = st.multiselect(T["f_estado"], opciones, placeholder=T["todos"], key="estados",
                             format_func=lambda e: f"{e} · {ESTADOS[e][0]}")

d = todo
if regiones:
    d = d[d["region"].isin(regiones)]
if estados:
    d = d[d["estado"].isin(estados)]

if d.empty:
    st.info(T["sin_datos"])
    st.stop()

# ------------------------------------------------------------------ cálculos compartidos
total = len(d)
recompran = int((d["pedidos"] > 1).sum())
tasa_rec = recompran / total * 100

por_est = (d.groupby(["estado", "region"])
           .agg(clientes=("cliente", "size"), pedidos=("pedidos", "sum"), recompran=("pedidos", lambda s: (s > 1).sum()),
                ciudades=("ciudad_txt", "nunique"))
           .reset_index())
por_est["nombre"] = por_est["estado"].map(lambda e: ESTADOS[e][0])
por_est["poblacion"] = por_est["estado"].map(POB)
por_est["cuota"] = por_est["clientes"] / total * 100
por_est["penet"] = por_est["clientes"] / por_est["poblacion"] * 100_000
por_est["recompra"] = por_est["recompran"] / por_est["clientes"] * 100
por_est = por_est.sort_values("clientes", ascending=False).reset_index(drop=True)
pob_sel = por_est["poblacion"].sum()
tasa_sel = total / pob_sel * 100_000

por_ciudad = (d.groupby("ciudad_txt").agg(clientes=("cliente", "size"), estado=("estado", "first"))
              .sort_values("clientes", ascending=False).reset_index())
por_ciudad["cuota"] = por_ciudad["clientes"] / total * 100

smp.kpis([
    dict(etiqueta=T["k_clientes"], valor=n(total), nota=T["n_clientes"].format(p=n(d["pedidos"].sum()))),
    dict(etiqueta=T["k_recompra"], valor=p(tasa_rec), tono="neg", nota=T["n_recompra"].format(n=n(recompran))),
    dict(etiqueta=T["k_alcance"], valor=n(len(por_est)),
         nota=T["n_alcance"].format(c=n(len(por_ciudad)), z=n(d["cep"].nunique()))),
    dict(etiqueta=T["k_penet"], valor=n(tasa_sel, 1), tono="acento", nota=T["n_penet"].format(r=n(TASA_BR, 1))),
])

tabs = st.tabs(T["tabs"])

# ------------------------------------------------------------------ 1. resumen
with tabs[0]:
    items = []

    # Hallazgo 1: concentración (por estado si hay más de 3; si no, por ciudad)
    if len(por_est) > 3:
        top = por_est.head(3)
        nombres, unidad, foco = top["estado"].tolist(), T["hz1_estados"], lista_y(top["nombre"])
        pob_top = top["poblacion"].sum() / pob_sel * 100
    else:
        top = por_ciudad.head(3)
        nombres, unidad, foco = top["ciudad_txt"].tolist(), T["hz1_ciudades"], lista_y(top["ciudad_txt"])
        pob_top = None
    cuota_top = top["clientes"].sum() / total * 100
    if len(top) >= 2 and cuota_top < 100:
        if pob_top is not None:
            ratio = cuota_top / pob_top
            rel = T["hz1_mas"] if ratio > 1.1 else T["hz1_menos"] if ratio < 0.9 else T["hz1_igual"]
            texto = T["hz1_x"].format(lista=lista_y(nombres), c=n(top["clientes"].sum()), pp=p(pob_top), rel=rel)
        else:
            texto = T["hz1_x_c"].format(lista=lista_y(nombres), c=n(top["clientes"].sum()))
        items.append(dict(cifra=p(cuota_top), titulo=T["hz1_t"].format(n=len(top), unidad=unidad, p=p(cuota_top)),
                          texto=texto, accion=T["hz1_a"].format(top=foco)))

    # Hallazgo 2: recompra
    texto = T["hz2_x"].format(n1=n(total - recompran), n=n(total))
    comparables = por_est[por_est["clientes"] >= MIN_ESTADO]
    if len(comparables) >= 2:
        lo, hi = comparables.loc[comparables["recompra"].idxmin()], comparables.loc[comparables["recompra"].idxmax()]
        texto += T["hz2_x_rango"].format(m=MIN_ESTADO, min=p(lo["recompra"]), emin=lo["nombre"],
                                         max=p(hi["recompra"]), emax=hi["nombre"])
        if len(comparables) >= 5 and hi["recompra"] - lo["recompra"] < 2 and hi["recompra"] < 10:
            texto += T["hz2_x_parejo"]
    items.append(dict(cifra=p(tasa_rec), tono="neg", titulo=T["hz2_t"].format(p=p(tasa_rec)), texto=texto, accion=T["hz2_a"]))

    # Hallazgo 3: el estado con más clientes "faltantes" frente al promedio de Brasil
    hueco = por_est.assign(extra=por_est["poblacion"] * TASA_BR / 100_000 - por_est["clientes"])
    hueco = hueco[hueco["extra"] >= 1].sort_values("extra", ascending=False)
    if not hueco.empty:
        h = hueco.iloc[0]
        ciudad_h = por_ciudad[por_ciudad["estado"] == h["estado"]].iloc[0]["ciudad_txt"]
        items.append(dict(cifra="+" + n(h["extra"]), titulo=T["hz3_t"].format(estado=h["nombre"]),
                          texto=T["hz3_x"].format(pob=n(h["poblacion"] / 1e6, 1), r=n(h["penet"], 1), rb=n(TASA_BR, 1), extra=n(h["extra"])),
                          accion=T["hz3_a"].format(estado=h["nombre"], ciudad=ciudad_h)))
    else:
        bajo = por_est.loc[por_est["penet"].idxmin()]
        if len(por_est) == 1:
            items.append(dict(cifra=n(tasa_sel, 1), titulo=T["hz3_t_uno"].format(estado=bajo["nombre"]),
                              texto=T["hz3_x_uno"].format(r=n(tasa_sel, 1), rb=n(TASA_BR, 1)), accion=T["hz3_a_ok"]))
        else:
            items.append(dict(cifra=n(tasa_sel, 1), titulo=T["hz3_t_ok"],
                              texto=T["hz3_x_ok"].format(r=n(tasa_sel, 1), rb=n(TASA_BR, 1), estado=bajo["nombre"], re=n(bajo["penet"], 1)),
                              accion=T["hz3_a_ok"]))

    for i, it in enumerate(items):
        it["n"] = f"0{i + 1}"
    smp.hallazgos(items, T["accion"])

    # Peso en clientes contra peso en población: por región, o por estado si hay una sola región
    if por_est["region"].nunique() > 1:
        z = por_est.groupby("region").agg(clientes=("clientes", "sum"), poblacion=("poblacion", "sum")).reset_index()
        z["zona"] = z["region"].map(REG)
    else:
        z = por_est[["nombre", "clientes", "poblacion"]].rename(columns={"nombre": "zona"})
    z["pc"] = z["clientes"] / z["clientes"].sum() * 100
    z["pp"] = z["poblacion"] / z["poblacion"].sum() * 100
    z["indice"] = z["pc"] / z["pp"]
    z = z.sort_values("pc", ascending=False)
    if len(z) >= 2:
        smp.seccion(T["r_tit"], T["r_txt"])
        fig = go.Figure()
        for col, nombre, color, cd in [("pc", T["cuota_cli"], smp.SERIE[0], "clientes"), ("pp", T["cuota_pob"], smp.SERIE[1], "poblacion")]:
            fig.add_bar(x=z["zona"], y=z[col], name=nombre, marker_color=color, customdata=z[[cd]],
                        text=[p(v, 0) for v in z[col]], textposition="outside", textfont=dict(color=smp.TEXTO),
                        hovertemplate=f"<b>%{{x}}</b><br>{nombre}: %{{y:.1f}}% (%{{customdata[0]:,.0f}})<extra></extra>")
        fig.update_layout(barmode="group", xaxis=dict(type="category"),
                          yaxis=dict(ticksuffix="%", range=[0, max(z["pc"].max(), z["pp"].max()) * 1.18]), margin=dict(t=40))
        smp.grafico(fig, lang, 380)
        alta, baja = z.loc[z["indice"].idxmax()], z.loc[z["indice"].idxmin()]
        smp.lectura(T["r_lect"].format(alta=alta["zona"], pc=p(alta["pc"]), pp=p(alta["pp"]),
                                       baja=baja["zona"], pc2=p(baja["pc"]), pp2=p(baja["pp"])))

# ------------------------------------------------------------------ 2. geografía
with tabs[1]:
    smp.seccion(T["g_mapa"], T["g_mapa_txt"])
    geo = por_est.assign(lat=por_est["estado"].map(lambda e: ESTADOS[e][1]), lon=por_est["estado"].map(lambda e: ESTADOS[e][2]))
    fig = go.Figure(go.Scattergeo(
        lat=geo["lat"], lon=geo["lon"], text=geo["estado"], mode="markers+text", textposition="middle center",
        textfont=dict(color=smp.TEXTO, size=10),
        marker=dict(size=geo["clientes"], sizemode="area", sizeref=2 * MAX_EST / 75 ** 2, sizemin=4,
                    color=smp.POSITIVO, opacity=0.75, line=dict(width=0)),
        customdata=geo[["nombre", "clientes", "cuota", "penet"]],
        hovertemplate=f"<b>%{{customdata[0]}}</b><br>{T['clientes']}: %{{customdata[1]:,.0f}}"
                      f"<br>{T['cuota']}: %{{customdata[2]:.1f}}%<br>{T['penet']}: %{{customdata[3]:.1f}}<extra></extra>",
    ))
    fig.update_geos(scope="south america", projection_type="mercator", lonaxis_range=[-75, -33], lataxis_range=[-34, 6],
                    bgcolor="rgba(0,0,0,0)", showframe=False, showcoastlines=False, showland=True, landcolor="#15274a",
                    showcountries=True, countrycolor="rgba(255,255,255,.12)", showlakes=False)
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
    smp.grafico(fig, lang, 520)

    a, b = st.columns(2)
    with a:
        e = por_est.sort_values("clientes")
        fig = go.Figure(go.Bar(
            y=e["estado"], x=e["clientes"], orientation="h", marker_color=smp.POSITIVO,
            text=[p(v) for v in e["cuota"]], textposition="outside", textfont=dict(color=smp.TEXTO),
            customdata=e[["nombre", "cuota", "pedidos"]],
            hovertemplate=f"<b>%{{customdata[0]}}</b><br>{T['clientes']}: %{{x:,.0f}} (%{{customdata[1]:.1f}}%)"
                          f"<br>{T['pedidos']}: %{{customdata[2]:,.0f}}<extra></extra>",
        ))
        fig.update_layout(title=T["g_bar"], xaxis=dict(range=[0, e["clientes"].max() * 1.22], tickformat="~s"),
                          yaxis=dict(type="category"), showlegend=False, bargap=0.2)
        smp.grafico(fig, lang, max(320, 24 * len(e) + 90))
    with b:
        e = por_est.sort_values("penet")
        fig = go.Figure(go.Bar(
            y=e["estado"], x=e["penet"], orientation="h",
            marker_color=[smp.POSITIVO if v >= TASA_BR else smp.NEGATIVO for v in e["penet"]],
            text=[n(v, 1) for v in e["penet"]], textposition="outside", textfont=dict(color=smp.TEXTO),
            customdata=e[["nombre", "clientes", "poblacion"]],
            hovertemplate=f"<b>%{{customdata[0]}}</b><br>{T['penet']}: %{{x:.1f}}<br>{T['clientes']}: %{{customdata[1]:,.0f}}"
                          f"<br>{T['poblacion']}: %{{customdata[2]:,.0f}}<extra></extra>",
        ))
        fig.add_vline(x=TASA_BR, line_color="rgba(255,255,255,.45)", line_dash="dot", line_width=1,
                      annotation_text=T["promedio"], annotation_font=dict(color=smp.TENUE, size=11),
                      annotation_position="top")
        fig.update_layout(title=T["g_pen"], xaxis=dict(range=[0, max(e["penet"].max(), TASA_BR) * 1.22]),
                          yaxis=dict(type="category"), showlegend=False, bargap=0.2)
        smp.grafico(fig, lang, max(320, 24 * len(e) + 90))
    st.caption(T["g_pen_txt"])
    if len(por_est) >= 5:
        hi, lo = por_est.loc[por_est["penet"].idxmax()], por_est.loc[por_est["penet"].idxmin()]
        smp.lectura(T["g_lect"].format(lista=lista_y(por_est.head(3)["estado"]), p3=p(por_est.head(3)["cuota"].sum()),
                                       p5=p(por_est.head(5)["cuota"].sum()), max=n(hi["penet"], 1), emax=hi["nombre"],
                                       min=n(lo["penet"], 1), emin=lo["nombre"]))

# ------------------------------------------------------------------ 3. recompra
with tabs[2]:
    smp.seccion(T["rc_tit"], T["rc_txt"])
    grupos = d["pedidos"].clip(upper=5).value_counts().sort_index()
    etiquetas = [str(k) if k < 5 else "5+" for k in grupos.index]
    cuotas = grupos / total * 100
    a, b = st.columns([1.1, 1])
    with a:
        fig = go.Figure(go.Bar(
            x=etiquetas, y=grupos.values, marker_color=smp.POSITIVO,
            text=[f"{n(v)} · {p(c)}" for v, c in zip(grupos.values, cuotas.values)], textposition="outside",
            textfont=dict(color=smp.TEXTO), customdata=cuotas.values,
            hovertemplate=f"<b>%{{x}}</b> {T['pedidos'].lower()}<br>{T['personas']}: %{{y:,.0f}} (%{{customdata:.1f}}%)<extra></extra>",
        ))
        fig.update_layout(title=T["rc_dist"], xaxis=dict(type="category", title=T["n_ped"]),
                          yaxis=dict(title=T["personas"], range=[0, grupos.max() * 1.18], tickformat="~s"), showlegend=False)
        smp.grafico(fig, lang, 380)
    with b:
        comp = por_est[por_est["clientes"] >= MIN_ESTADO].sort_values("recompra")
        if len(comp) >= 2:
            fig = go.Figure(go.Bar(
                y=comp["estado"], x=comp["recompra"], orientation="h", marker_color=smp.POSITIVO,
                text=[p(v) for v in comp["recompra"]], textposition="outside", textfont=dict(color=smp.TEXTO),
                customdata=comp[["nombre", "clientes", "recompran"]],
                hovertemplate=f"<b>%{{customdata[0]}}</b><br>{T['recompra']}: %{{x:.1f}}%"
                              f"<br>{T['clientes']}: %{{customdata[1]:,.0f}}<br>{T['personas']} 2+: %{{customdata[2]:,.0f}}<extra></extra>",
            ))
            fig.add_vline(x=tasa_rec, line_color="rgba(255,255,255,.45)", line_dash="dot", line_width=1,
                          annotation_text=T["total"], annotation_font=dict(color=smp.TENUE, size=11), annotation_position="top")
            fig.update_layout(title=T["rc_est"], xaxis=dict(ticksuffix="%", range=[0, comp["recompra"].max() * 1.25]),
                              yaxis=dict(type="category"), showlegend=False, bargap=0.2)
            smp.grafico(fig, lang, max(380, 24 * len(comp) + 90))
            st.caption(T["rc_est_txt"].format(m=MIN_ESTADO))
    if recompran >= 20:
        smp.lectura(T["rc_lect"].format(p1=p(100 - tasa_rec), n2=n(recompran),
                                        pp2=p((d["pedidos"] == 2).sum() / recompran * 100)))
    if len(comp) >= 2:
        lo, hi = comp.iloc[0], comp.iloc[-1]
        dif = hi["recompra"] - lo["recompra"]
        clave = "rc_lect2" if len(comp) >= 5 and dif < 2 and hi["recompra"] < 10 else "rc_lect2b"
        smp.lectura(T[clave].format(d=n(dif, 1), emax=hi["nombre"], max=p(hi["recompra"]), emin=lo["nombre"], min=p(lo["recompra"])))
    st.caption(T["rc_nota"])

# ------------------------------------------------------------------ 4. ciudades
with tabs[3]:
    smp.seccion(T["c_tit"], T["c_txt"])
    top_c = por_ciudad.head(15).sort_values("clientes")
    fig = go.Figure(go.Bar(
        y=top_c["ciudad_txt"], x=top_c["clientes"], orientation="h", marker_color=smp.POSITIVO,
        text=[p(v) for v in top_c["cuota"]], textposition="outside", textfont=dict(color=smp.TEXTO),
        customdata=top_c[["cuota"]],
        hovertemplate=f"<b>%{{y}}</b><br>{T['clientes']}: %{{x:,.0f}}<br>{T['cuota']}: %{{customdata[0]:.1f}}%<extra></extra>",
    ))
    fig.update_layout(xaxis=dict(range=[0, top_c["clientes"].max() * 1.2], tickformat="~s"), yaxis=dict(type="category"),
                      showlegend=False, margin=dict(t=20), bargap=0.2)
    smp.grafico(fig, lang, max(300, 28 * len(top_c) + 60))

    smp.seccion(T["c_curva"], T["c_curva_txt"])
    curva = por_ciudad.head(50).copy()
    curva["acum"] = curva["clientes"].cumsum() / total * 100
    curva["rank"] = range(1, len(curva) + 1)
    fig = go.Figure(go.Scatter(
        x=curva["rank"], y=curva["acum"], mode="lines+markers", line=dict(color=smp.SERIE[0], width=2.5),
        marker=dict(size=5), customdata=curva[["ciudad_txt", "clientes"]],
        hovertemplate=f"#%{{x}} · <b>%{{customdata[0]}}</b><br>{T['clientes']}: %{{customdata[1]:,.0f}}"
                      f"<br>{T['acum']}: %{{y:.1f}}%<extra></extra>",
    ))
    fig.update_layout(xaxis=dict(title=T["c_rank"]), yaxis=dict(ticksuffix="%", range=[0, min(100, curva["acum"].max() * 1.1)]),
                      showlegend=False, margin=dict(t=20))
    smp.grafico(fig, lang, 340)
    chicas = int((por_ciudad["clientes"] < 10).sum())
    if len(por_ciudad) > 10:
        smp.lectura(T["c_lect"].format(top=por_ciudad.iloc[0]["ciudad_txt"], ptop=p(por_ciudad.iloc[0]["cuota"]),
                                       p10=p(por_ciudad.head(10)["cuota"].sum()), nc=n(chicas), total=n(len(por_ciudad)),
                                       pc=p(chicas / len(por_ciudad) * 100, 0)))

# ------------------------------------------------------------------ 5. logística
with tabs[4]:
    smp.seccion(T["l_tit"], T["l_txt"])
    por_cep = (d.groupby("cep").agg(clientes=("cliente", "size"),
                                    ciudad=("ciudad_txt", lambda s: s.value_counts().index[0]))
               .sort_values("clientes", ascending=False).reset_index())
    por_cep["cuota"] = por_cep["clientes"] / total * 100
    top_z = por_cep.head(15)
    fig = go.Figure(go.Bar(
        x=top_z["cep"], y=top_z["clientes"], marker_color=smp.SERIE[2],
        text=[n(v) for v in top_z["clientes"]], textposition="outside", textfont=dict(color=smp.TEXTO),
        customdata=top_z[["ciudad", "cuota"]],
        hovertemplate=f"<b>{T['cep']} %{{x}}</b> · %{{customdata[0]}}<br>{T['clientes']}: %{{y:,.0f}}"
                      f"<br>{T['cuota']}: %{{customdata[1]:.2f}}%<extra></extra>",
    ))
    fig.update_layout(title=T["l_top"], xaxis=dict(type="category", title=T["cep"]),
                      yaxis=dict(title=T["clientes"], range=[0, top_z["clientes"].max() * 1.2]), showlegend=False)
    smp.grafico(fig, lang, 380)

    lor = por_cep[["clientes"]].copy()
    lor["x"] = (pd.Series(range(1, len(lor) + 1)) / len(lor) * 100).values
    lor["y"] = lor["clientes"].cumsum() / total * 100
    if len(lor) > 400:   # submuestra para que el gráfico pese poco; la curva se ve igual
        paso = len(lor) // 400
        lor = pd.concat([lor.iloc[::paso], lor.iloc[[-1]]])
    fig = go.Figure(go.Scatter(
        x=lor["x"], y=lor["y"], mode="lines", line=dict(color=smp.SERIE[0], width=2.5),
        hovertemplate=f"{T['l_x']}: %{{x:.1f}}%<br>{T['l_y']}: %{{y:.1f}}%<extra></extra>",
    ))
    fig.update_layout(title=T["l_curva"], xaxis=dict(title=T["l_x"], ticksuffix="%", range=[0, 100]),
                      yaxis=dict(title=T["l_y"], ticksuffix="%", range=[0, 102]), showlegend=False)
    smp.grafico(fig, lang, 360)
    n10 = max(1, round(len(por_cep) * 0.1))
    n50 = int((por_cep["clientes"].cumsum() < total / 2).sum()) + 1
    if len(por_cep) >= 20:
        smp.lectura(T["l_lect"].format(n10=n(n10), total=n(len(por_cep)), p10=p(por_cep.head(n10)["cuota"].sum()), n50=n(n50),
                                       ztop=por_cep.iloc[0]["cep"], ctop=por_cep.iloc[0]["ciudad"]))

# ------------------------------------------------------------------ 6. datos
with tabs[5]:
    smp.seccion(T["x_tit"], T["x_txt"])
    vista = por_est.assign(region=por_est["region"].map(REG))[
        ["estado", "nombre", "region", "clientes", "pedidos", "cuota", "recompra", "poblacion", "penet", "ciudades"]]
    st.dataframe(vista, hide_index=True, width="stretch", height=420,
                 column_config={
                     "estado": "UF", "nombre": T["estado"], "region": T["region"],
                     "clientes": st.column_config.NumberColumn(T["clientes"], format="localized"),
                     "pedidos": st.column_config.NumberColumn(T["pedidos"], format="localized"),
                     "cuota": st.column_config.NumberColumn(T["cuota"], format="%.1f%%"),
                     "recompra": st.column_config.NumberColumn(T["recompra"], format="%.1f%%"),
                     "poblacion": st.column_config.NumberColumn(T["poblacion"], format="localized"),
                     "penet": st.column_config.NumberColumn(T["penet"], format="%.1f"),
                     "ciudades": st.column_config.NumberColumn("Ciudades" if lang == "es" else "Cities", format="localized"),
                 })
    a, b = st.columns(2)
    with a:
        st.download_button(T["x_bajar"], vista.to_csv(index=False).encode("utf-8"), "olist_estados.csv", "text/csv")
    with b:
        st.download_button(T["x_bajar2"], d.drop(columns="ciudad_txt").to_csv(index=False).encode("utf-8"),
                           "olist_clientes.csv", "text/csv")
    with st.expander(T["x_metodo"]):
        st.markdown(T["x_metodo_txt"])

smp.pie(lang, T["fuente"])
