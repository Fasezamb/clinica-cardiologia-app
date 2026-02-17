import streamlit as st
from database import init_db, verify_login
from modules.hce import show as mostrar_hce
from modules.agenda import show as mostrar_agenda
from modules.busqueda import mostrar_buscador
from modules.admin import mostrar_gestion_medicos
from modules.dashboard import show as mostrar_dashboard

# 1. Configuración de página (Debe ser lo primero)
st.set_page_config(page_title="CardioCloud 4.0", layout="wide", page_icon="🩺")

# 2. Inicializar DB
init_db()

# --- GESTIÓN DE ESTADO DE SESIÓN ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.rol = ""
    st.session_state.user = {} 

# --- PANTALLA DE LOGIN ---
if not st.session_state.logged_in:
    st.title("🩺 Bienvenido a CardioCloud")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            user_input = st.text_input("Usuario")
            pw_input = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Iniciar Sesión", use_container_width=True)
            
            if submit:
                res = verify_login(user_input, pw_input)
                if res:
                    st.session_state.logged_in = True
                    st.session_state.username = res['username']
                    st.session_state.rol = str(res['rol']).strip().lower()
                    st.session_state.user = res
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
    
    with st.expander("ℹ️ Credenciales de prueba"):
        st.write("**Admin:** admin / admin123")
        # En producción o tras setup inicial, usar credenciales reales

else:
    # --- BARRA LATERAL ---
    st.sidebar.title("🩺 CardioCloud")
    st.sidebar.write(f"Usuario: **{st.session_state.username}**")
    st.sidebar.caption(f"Rol: {st.session_state.rol.upper()}")
    
    # 3. Menú dinámico
    menu = ["Dashboard", "Agenda (Citas)", "Consulta Médica (HCE)", "Buscador Historial"]

    
    # Admin menu
    if st.session_state.rol == "admin" or st.session_state.username.lower() == "admin":
        menu.append("Gestión de Médicos")
        
    opcion = st.sidebar.radio("Ir a:", menu)
    
    st.sidebar.divider()
    if st.sidebar.button("Cerrar Sesión", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.rol = ""
        st.session_state.user = {}
        st.rerun()

    # --- LÓGICA DE NAVEGACIÓN ---
    if opcion == "Dashboard":
        mostrar_dashboard()

    elif opcion == "Agenda (Citas)":
        mostrar_agenda()


    elif opcion == "Consulta Médica (HCE)":
        mostrar_hce()

    elif opcion == "Buscador Historial":
        mostrar_buscador()

    elif opcion == "Gestión de Médicos":
        mostrar_gestion_medicos()
