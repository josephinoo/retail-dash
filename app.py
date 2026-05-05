import streamlit as st
from auth import show_login

st.set_page_config(
    page_title="RetailDash",
    layout="wide",
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_role = None
    st.session_state.user_name = None
    st.session_state.nombre = None

dashboard_pages = [
    st.Page(page="pages/1_Resumen.py",title="Resumen",icon="📊"),
    st.Page(page="pages/2_Ventas.py",title="Ventas",icon="💰"),
    st.Page(page="pages/3_Geografico.py",title="Geográfico",icon="🌍"),
    st.Page(page="pages/4_Datos.py",title="Datos",icon="📈"),
]

if not st.session_state.logged_in:
    pg = st.navigation([st.Page(show_login,title="Login")],position="hidden")
    pg.run()
else:
    pg = st.navigation(dashboard_pages)
    pg.run()
   






