import streamlit as st

USUARIOS = {
    "admin": {"password": "admin123", "role": "admin", "name": "Administrador"},
    "user1": {"password": "user123", "role": "user", "name": "Usuario 1"},
    "user2": {"password": "user456", "role": "user", "name": "Usuario 2"}
}

def verificar_credenciales(usuario, password):
    if usuario in USUARIOS:
        obtener_password = USUARIOS[usuario]["password"]
        if password == obtener_password:
            return True
        return False

def show_login():
    _,col, _ = st.columns([1,1.5,1])
    with col:
        st.title("Iniciar Sesión")
        st.caption("Por favor, ingresa tus credenciales para acceder al dashboard.")
        st.divider()

        with st.form("login_form"):
            usuario = st.text_input("Usuario",placeholder="Ingresa tu usuario")
            password = st.text_input("Contraseña",placeholder="Ingresa tu contraseña",type="password")
            submit = st.form_submit_button("Ingresar",use_container_width=True)
        if submit:
            if not usuario or not password:
                st.error("Por favor, completa ambos campos.")

            elif verificar_credenciales(usuario, password):
                st.success("¡Inicio de sesión exitoso!")
                st.session_state.logged_in = True
                st.session_state.user_name = usuario
                st.session_state.user_role = USUARIOS[usuario]["role"]
                st.session_state.nombre = USUARIOS[usuario]["name"]
                st.success(f"Bienvenido, {st.session_state.nombre}!")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos. Inténtalo de nuevo.")