import streamlit as st
from utils import sidebar_con_filtros, grafico_categoria_barras, grafico_margen_categoria, grafico_region_pie, grafico_region_barras, grafico_categoria_treemap,grafico_scatter_ventas_profit




st.set_page_config(
    page_title="Ventas - RetailDash",
    layout="wide"
)

df_side = sidebar_con_filtros()

st.title("Análisis de Ventas")
st.caption("Desglosa el rendimiento por categoria, region y la relacion ventas-ganancia.")
st.divider()

st.subheader("Ventas por Categoría")

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(grafico_categoria_barras(df_side),use_container_width=True)
with col2:
    st.plotly_chart(grafico_margen_categoria(df_side),use_container_width=True)

st.divider()

st.subheader("Ventas por Región")
col3, col4 = st.columns(2)
with col3:
    st.plotly_chart(grafico_region_pie(df_side),use_container_width=True)
with col4:
    st.plotly_chart(grafico_region_barras(df_side),use_container_width=True)


st.subheader("Composicion Categoria-Región")
st.plotly_chart(grafico_categoria_treemap(df_side),use_container_width=True)




