import streamlit as st
import pandas as pd
from database import search_pacientes, get_hce_by_paciente

def mostrar_buscador():
    st.header("🔍 Buscador de Pacientes e Historial")
    query = st.text_input("Buscar por Nombre o DNI")
    
    if query:
        resultados = search_pacientes(query)
        if resultados:
            df_pacientes = pd.DataFrame(resultados)
            st.subheader("Pacientes Encontrados")
            st.dataframe(df_pacientes, use_container_width=True)
            
            # Seleccionar paciente para ver historial
            paciente_id = st.selectbox("Seleccione ID para ver historial detallado", df_pacientes['id'])
            
            if st.button("Ver Historial"):
                historial = get_hce_by_paciente(paciente_id)
                if historial:
                    st.write("### Consultas Anteriores")
                    st.table(pd.DataFrame(historial)[['fecha_consulta', 'motivo_consulta', 'fc', 'ta_sistolica']])
                else:
                    st.warning("Este paciente aún no tiene consultas registradas.")
        else:
            st.error("No se encontraron resultados.")
