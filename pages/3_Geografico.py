import streamlit as st
from utils import sidebar_con_filtros, grafico_mapa_regiones, fmt_money

st.set_page_config(page_title="Geografico | RetailDash", layout="wide", initial_sidebar_state="collapsed")

df = sidebar_con_filtros()

st.title("Mapa Geografico de Ventas")
st.caption("Distribucion espacial de ventas y ganancias en EE.UU. por region.")
st.divider()

# ── Mapa interactivo ──────────────────────────────────────────────────────────
st.plotly_chart(grafico_mapa_regiones(df), use_container_width=True)

st.divider()

# ── Tabla resumen por region ──────────────────────────────────────────────────
st.subheader("Resumen por Region")

reg_resumen = (
    df.groupby("Region")
    .agg(
        Ventas=("Sales", "sum"),
        Ganancia=("Profit", "sum"),
        Unidades=("Quantity", "sum"),
        Registros=("Sales", "count"),
    )
    .reset_index()
    .sort_values("Ventas", ascending=False)
)

reg_resumen["Margen (%)"] = (reg_resumen["Ganancia"] / reg_resumen["Ventas"] * 100).round(1)
reg_resumen["Ventas"]    = reg_resumen["Ventas"].apply(fmt_money)
reg_resumen["Ganancia"]  = reg_resumen["Ganancia"].apply(fmt_money)

st.dataframe(
    reg_resumen,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Region":     st.column_config.TextColumn("Region"),
        "Ventas":     st.column_config.TextColumn("Ventas"),
        "Ganancia":   st.column_config.TextColumn("Ganancia"),
        "Unidades":   st.column_config.NumberColumn("Unidades", format="%d"),
        "Registros":  st.column_config.NumberColumn("Registros", format="%d"),
        "Margen (%)": st.column_config.ProgressColumn(
            "Margen (%)", format="%.1f%%", min_value=0, max_value=100
        ),
    },
)