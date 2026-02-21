"""
Módulo de Agenda y Gestión de Citas.
Permite crear, visualizar y gestionar citas para los 4 médicos.
"""

import streamlit as st
from datetime import datetime, date, timedelta
import database as db
import pandas as pd


def get_color_estado(estado: str) -> str:
    """Retorna el color asociado a cada estado de cita."""
    colores = {
        'Pendiente': '#808080',  # Gris
        'Llegó': '#4169E1',      # Azul
        'En Consulta': '#32CD32', # Verde
        'Completada': '#228B22',  # Verde oscuro
        'No-show': '#DC143C'      # Rojo
    }
    return colores.get(estado, '#808080')


def show():
    """Función principal del módulo de agenda."""
    st.title("📅 Agenda de Citas")
    
    # Tabs para diferentes funcionalidades
    tab1, tab2, tab3 = st.tabs(["Ver Agenda", "Nueva Cita", "Estadísticas"])
    
    # ==================== TAB 1: Ver Agenda ====================
    with tab1:
        st.subheader("Agenda del Día")
        
        # Selectores
        col1, col2 = st.columns(2)
        
        with col1:
            medicos = db.get_all_medicos()
            if not medicos:
                st.warning("No hay médicos registrados en el sistema.")
                st.stop()
                
            medicos_dict = {f"{m['nombre']} - {m['especialidad']}": m['id'] for m in medicos}
            medico_seleccionado = st.selectbox("Seleccionar Médico", list(medicos_dict.keys()))
            medico_id = medicos_dict[medico_seleccionado]
        
        with col2:
            fecha_seleccionada = st.date_input("Fecha", value=date.today())
        
        # Obtener citas del día
        citas = db.get_citas_by_medico_fecha(medico_id, fecha_seleccionada.strftime('%Y-%m-%d'))
        
        if citas:
            st.write(f"**{len(citas)} cita(s) programada(s)**")
            
            # Crear DataFrame para mejor visualización
            for cita in citas:
                hora = datetime.fromisoformat(cita['fecha_hora']).strftime('%H:%M')
                color = get_color_estado(cita['estado'])
                
                with st.container():
                    col1, col2, col3, col4 = st.columns([1, 2, 2, 3])
                    
                    with col1:
                        st.markdown(f"### {hora}")
                    
                    with col2:
                        st.write(f"**{cita['paciente_nombre']}**")
                        st.caption(f"ID Paciente: {cita['paciente_id']}")
                    
                    with col3:
                        st.markdown(f"<span style='color:{color}; font-weight:bold;'>● {cita['estado']}</span>", 
                                  unsafe_allow_html=True)
                    
                    with col4:
                        # Botones de acción según el estado
                        if cita['estado'] == 'Pendiente':
                            if st.button("✅ Marcar Llegada", key=f"llegada_{cita['id']}"):
                                db.update_estado_cita(cita['id'], 'Llegó')
                                st.rerun()
                        
                        elif cita['estado'] == 'Llegó':
                            if st.button("🩺 Iniciar Consulta", key=f"consulta_{cita['id']}"):
                                db.update_estado_cita(cita['id'], 'En Consulta')
                                st.rerun()
                        
                        elif cita['estado'] == 'En Consulta':
                            if st.button("✔️ Finalizar", key=f"finalizar_{cita['id']}"):
                                db.update_estado_cita(cita['id'], 'Completada')
                                st.success("Cita completada")
                                st.rerun()
                        
                        # Opción de marcar No-show siempre disponible
                        if cita['estado'] not in ['Completada', 'No-show']:
                            if st.button("❌ No-show", key=f"noshow_{cita['id']}"):
                                db.update_estado_cita(cita['id'], 'No-show')
                                st.rerun()
                    
                    st.divider()
        else:
            st.info("No hay citas programadas para esta fecha")
    
    # ==================== TAB 2: Nueva Cita ====================
    with tab2:
        st.subheader("Agendar Nueva Cita")
        
        with st.form("nueva_cita"):
            # Seleccionar paciente
            pacientes = db.get_all_pacientes()
            if not pacientes:
                st.warning("No hay pacientes registrados. Por favor registre un paciente primero.")
                st.form_submit_button("Guardar", disabled=True)
                return
            
            pacientes_dict = {f"{p['nombre']} (ID: {p['id']})": p['id'] for p in pacientes}
            paciente_seleccionado = st.selectbox("Paciente *", list(pacientes_dict.keys()))
            paciente_id = pacientes_dict[paciente_seleccionado]
            
            # Seleccionar médico
            medicos = db.get_all_medicos()
            medicos_dict = {f"{m['nombre']} - {m['especialidad']}": m['id'] for m in medicos}
            medico_seleccionado = st.selectbox("Médico *", list(medicos_dict.keys()))
            medico_id = medicos_dict[medico_seleccionado]
            
            # Fecha y hora
            col1, col2 = st.columns(2)
            with col1:
                fecha_cita = st.date_input("Fecha *", min_value=date.today())
            with col2:
                hora_cita = st.time_input("Hora *", value=datetime.now().time())
            
            submitted = st.form_submit_button("📅 Agendar Cita", use_container_width=True)
            
            if submitted:
                # Combinar fecha y hora
                fecha_hora = datetime.combine(fecha_cita, hora_cita).strftime('%Y-%m-%d %H:%M:%S')
                
                # Verificar si ya existe una cita en ese horario
                citas_existentes = db.get_citas_by_medico_fecha(medico_id, fecha_cita.strftime('%Y-%m-%d'))
                conflicto = False
                
                for cita in citas_existentes:
                    if cita['fecha_hora'] == fecha_hora:
                        conflicto = True
                        break
                
                if conflicto:
                    st.error("⚠️ Ya existe una cita para este médico en este horario")
                else:
                    try:
                        cita_id = db.create_cita(paciente_id, medico_id, fecha_hora)
                        st.success(f"✅ Cita agendada exitosamente (ID: {cita_id})")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error al agendar cita: {str(e)}")
    
    # ==================== TAB 3: Estadísticas ====================
    with tab3:
        st.subheader("📊 Estadísticas de No-shows")
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        
        with col1:
            medicos = db.get_all_medicos()
            medicos_opciones = ["Todos"] + [f"{m['nombre']}" for m in medicos]
            medico_filtro = st.selectbox("Médico", medicos_opciones)
        
        with col2:
            fecha_inicio = st.date_input("Desde", value=date.today().replace(day=1))
        
        with col3:
            fecha_fin = st.date_input("Hasta", value=date.today())
        
        # Obtener ID del médico si no es "Todos"
        medico_id_filtro = None
        if medico_filtro != "Todos":
            for m in medicos:
                if m['nombre'] == medico_filtro:
                    medico_id_filtro = m['id']
                    break
        
        # Obtener estadísticas
        stats = db.get_noshow_stats(
            medico_id=medico_id_filtro,
            fecha_inicio=fecha_inicio.strftime('%Y-%m-%d'),
            fecha_fin=fecha_fin.strftime('%Y-%m-%d')
        )
        
        # Mostrar métricas
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Citas", stats['total_citas'])
        
        with col2:
            st.metric("Completadas", stats['total_completadas'])
        
        with col3:
            st.metric("No-shows", stats['total_noshows'])
        
        with col4:
            st.metric("Tasa de Asistencia", f"{stats['tasa_asistencia']}%")
        
        # Gráfico de distribución (si hay datos)
        if stats['total_citas'] > 0:
            st.markdown("---")
            st.subheader("Distribución de Estados")
            
            # Crear datos para el gráfico
            import plotly.graph_objects as go
            
            labels = ['Completadas', 'No-shows', 'Otras']
            values = [
                stats['total_completadas'],
                stats['total_noshows'],
                stats['total_citas'] - stats['total_completadas'] - stats['total_noshows']
            ]
            colors = ['#228B22', '#DC143C', '#808080']
            
            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                marker=dict(colors=colors),
                hole=0.3
            )])
            
            fig.update_layout(
                title="Distribución de Estados de Citas",
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Estadísticas por médico
        if medico_filtro == "Todos":
            st.markdown("---")
            st.subheader("Estadísticas por Médico")
            
            medicos_stats = []
            for medico in medicos:
                stats_medico = db.get_noshow_stats(
                    medico_id=medico['id'],
                    fecha_inicio=fecha_inicio.strftime('%Y-%m-%d'),
                    fecha_fin=fecha_fin.strftime('%Y-%m-%d')
                )
                medicos_stats.append({
                    'Médico': medico['nombre'],
                    'Especialidad': medico['especialidad'],
                    'Total Citas': stats_medico['total_citas'],
                    'Completadas': stats_medico['total_completadas'],
                    'No-shows': stats_medico['total_noshows'],
                    'Tasa Asistencia': f"{stats_medico['tasa_asistencia']}%"
                })
            
            df = pd.DataFrame(medicos_stats)
            st.dataframe(df, use_container_width=True, hide_index=True)
