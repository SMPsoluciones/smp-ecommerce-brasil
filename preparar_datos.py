"""Genera datos/clientes.csv.gz a partir de ecommerceolist.db (tabla olist_customers_dataset).

En la tabla original cada fila es un pedido: customer_id cambia en cada compra y
customer_unique_id identifica a la persona. Aquí se arma una fila por persona:
- pedidos: cuántos customer_id (pedidos) tiene esa persona.
- ubicación "principal": la dirección (CEP, ciudad, estado) con más pedidos;
  si empata, la primera que aparece en la tabla.
- ubicaciones: en cuántas direcciones distintas compró.

Corrige un problema del origen: el prefijo de CEP se guardó como número y
perdió el cero inicial (01310 -> 1310). Se rellena a 5 dígitos.
Se corre una sola vez: python preparar_datos.py
"""
import sqlite3
from pathlib import Path

import pandas as pd

REGION = {
    "AC": "Norte", "AP": "Norte", "AM": "Norte", "PA": "Norte", "RO": "Norte", "RR": "Norte", "TO": "Norte",
    "AL": "Nordeste", "BA": "Nordeste", "CE": "Nordeste", "MA": "Nordeste", "PB": "Nordeste",
    "PE": "Nordeste", "PI": "Nordeste", "RN": "Nordeste", "SE": "Nordeste",
    "DF": "Centro-Oeste", "GO": "Centro-Oeste", "MT": "Centro-Oeste", "MS": "Centro-Oeste",
    "ES": "Sudeste", "MG": "Sudeste", "RJ": "Sudeste", "SP": "Sudeste",
    "PR": "Sul", "RS": "Sul", "SC": "Sul",
}

AQUI = Path(__file__).parent
with sqlite3.connect(AQUI / "ecommerceolist.db") as con:
    d = pd.read_sql("SELECT * FROM olist_customers_dataset", con)

d["cep"] = d["customer_zip_code_prefix"].astype(int).astype(str).str.zfill(5)
d["orden"] = range(len(d))
assert d["customer_id"].is_unique
assert set(d["customer_state"]) <= set(REGION)

# Dirección principal de cada persona
lugar = (d.groupby(["customer_unique_id", "cep", "customer_city", "customer_state"])
         .agg(n=("customer_id", "size"), primera=("orden", "min")).reset_index()
         .sort_values(["customer_unique_id", "n", "primera"], ascending=[True, False, True]))
ubicaciones = lugar.groupby("customer_unique_id").size().rename("ubicaciones")
principal = lugar.drop_duplicates("customer_unique_id").set_index("customer_unique_id")
pedidos = d.groupby("customer_unique_id").size().rename("pedidos")

c = (principal[["cep", "customer_city", "customer_state"]].join(pedidos).join(ubicaciones)
     .reset_index().rename(columns={"customer_unique_id": "cliente", "customer_city": "ciudad",
                                    "customer_state": "estado"}))
c["region"] = c["estado"].map(REGION)
c = c[["cliente", "pedidos", "ubicaciones", "region", "estado", "ciudad", "cep"]].sort_values("cliente")

assert c["pedidos"].sum() == len(d)
(AQUI / "datos").mkdir(exist_ok=True)
salida = AQUI / "datos" / "clientes.csv.gz"
c.to_csv(salida, index=False, compression="gzip")
print(f"{len(d)} pedidos · {len(c)} clientes · {(c.pedidos > 1).sum()} con más de un pedido · "
      f"{(c.ubicaciones > 1).sum()} con más de una dirección · CEP de 4 dígitos corregidos: "
      f"{(d.customer_zip_code_prefix.astype(str).str.len() < 5).sum()} · {salida.stat().st_size / 1e6:.1f} MB")
