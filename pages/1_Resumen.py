import streamlit as st

from utils import sidebar_con_filtros, mostrar_kpis,grafico_ventas_tiempo, grafico_profit_tiempo

st.set_page_config(
    page_title="Resumen - RetailDash",
    layout="wide"
)

df_side = sidebar_con_filtros()

st.title("📊 Resumen Ejecutivo")

mostrar_kpis(df_side)

st.divider()

st.subheader("Tendencias temporales")

col1 , col2 = st.columns(2)
with col1:
    st.plotly_chart(grafico_ventas_tiempo(df_side))
with col2:
    st.plotly_chart(grafico_profit_tiempo(df_side))
