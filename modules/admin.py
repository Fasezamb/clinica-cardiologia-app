import streamlit as st
import database as db
import pandas as pd

def mostrar_gestion_medicos():
    st.title("👨‍⚕️ Gestión de Médicos")
    
    tab1, tab2 = st.tabs(["Listado de Médicos", "Registrar Nuevo Médico"])
    
    with tab1:
        st.subheader("Médicos Registrados")
        medicos = db.get_all_medicos()
        
        if medicos:
            df = pd.DataFrame(medicos)
            # Renombrar columnas para mostrar
            df = df.rename(columns={
                'nombre': 'Nombre',
                'especialidad': 'Especialidad',
                'email': 'Email',
                'id': 'ID'
            })
            st.dataframe(df[['ID', 'Nombre', 'Especialidad', 'Email']], use_container_width=True, hide_index=True)
        else:
            st.info("No hay médicos registrados aún.")
            
    with tab2:
        st.subheader("Registrar Nuevo Médico")
        
        with st.form("form_medico"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre Completo *")
                especialidad = st.text_input("Especialidad *")
                email = st.text_input("Email *")
            
            with col2:
                username = st.text_input("Usuario (Login) *")
                password = st.text_input("Contraseña (Login) *", type="password")
                
            submitted = st.form_submit_button("Guardar Médico", use_container_width=True)
            
            if submitted:
                if not (nombre and especialidad and email and username and password):
                    st.error("Todos los campos son obligatorios")
                else:
                    if db.create_medico_con_usuario(nombre, especialidad, email, username, password):
                        st.success(f"✅ Médico {nombre} registrado exitosamente")
                        st.balloons()
                    else:
                        st.error("Error al registrar: El usuario ya existe o hubo un problema en la base de datos")
