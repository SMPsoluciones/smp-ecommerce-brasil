# Olist · ¿Dónde compran los clientes y cuántos vuelven?

Caso de análisis de **SMP Soluciones**. Un tablero en Streamlit que mira la base de clientes de Olist
(e-commerce en Brasil, 2016–2018): dónde está la demanda, en qué estados falta frente a su población,
qué ciudades y prefijos de CEP concentran a los clientes y cuántas personas vuelven a comprar.
Español por defecto; inglés con `?lang=en` en el link.

## Cómo correrlo

```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

`datos/clientes.csv.gz` ya viene generado. Para rehacerlo desde la base original (no se publica, pesa 118 MB):

```bash
python preparar_datos.py
```

## Datos

- **Fuente:** Brazilian E-Commerce Public Dataset by Olist (Kaggle), tabla `olist_customers_dataset` (99.441 filas).
- Cada `customer_id` es un **pedido**; la persona es `customer_unique_id` (96.096 personas). El tablero cuenta personas como clientes.
- La tabla no tiene fechas: se mide **recompra** (personas con 2 pedidos o más), no abandono.
- El prefijo de CEP perdió el cero inicial en 23.995 filas; se rellenó a 5 dígitos.
- Población por estado: IBGE, Censo 2022 (aproximación para comparar estados).

## Archivos

| Archivo | Qué es |
|---|---|
| `app.py` | El tablero |
| `smp.py` | Base visual compartida de los casos de SMP (no editar aquí sin copiarlo a los otros casos) |
| `preparar_datos.py` | Lee `ecommerceolist.db` y genera `datos/clientes.csv.gz` (una fila por persona) |
| `datos/clientes.csv.gz` | Datos que usa el tablero (~2,6 MB) |
| `.streamlit/config.toml` | Tema |
| `requirements.txt` | Dependencias |
| `ecommerceolist_dashboard_*.py`, `ecommerce_olist_queries.sql` | Versiones anteriores y consultas SQL originales (referencia) |
