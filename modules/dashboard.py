"""
Módulo de Dashboard.
Panel de control personalizado para médicos con métricas y alertas clínicas.
"""

import streamlit as st
from datetime import datetime, date
import database as db
import plotly.graph_objects as go
import plotly.express as px


def show():
    """Función principal del módulo de dashboard."""
    user = st.session_state.user
    
    st.title("📊 Dashboard")
    
    # Dashboard específico para médicos
    if user['rol'] == 'medico' and user['medico_id']:
        mostrar_dashboard_medico(user['medico_id'])
    else:
        mostrar_dashboard_general()


def mostrar_dashboard_medico(medico_id: int):
    """Dashboard personalizado para médicos."""
    medico = db.get_medico(medico_id)
    
    st.subheader(f"Bienvenido, Dr(a). {medico['nombre']}")
    st.caption(f"{medico['especialidad']}")
    
    # Agenda del día
    st.markdown("---")
    st.subheader(f"📅 Agenda de Hoy - {datetime.now().strftime('%d/%m/%Y')}")
    
    citas_hoy = db.get_citas_by_medico_fecha(
        medico_id, 
        datetime.now().strftime('%Y-%m-%d')
    )
    
    if citas_hoy:
        # Resumen rápido
        col1, col2, col3, col4 = st.columns(4)
        
        total = len(citas_hoy)
        pendientes = sum(1 for c in citas_hoy if c['estado'] == 'Pendiente')
        en_consulta = sum(1 for c in citas_hoy if c['estado'] == 'En Consulta')
        completadas = sum(1 for c in citas_hoy if c['estado'] == 'Completada')
        
        with col1:
            st.metric("Total", total)
        with col2:
            st.metric("Pendientes", pendientes, delta=None)
        with col3:
            st.metric("En Consulta", en_consulta)
        with col4:
            st.metric("Completadas", completadas)
        
        # Lista de citas
        st.write("**Próximas Citas:**")
        for cita in citas_hoy[:5]:  # Mostrar solo las primeras 5
            hora = datetime.fromisoformat(cita['fecha_hora']).strftime('%H:%M')
            
            estado_emoji = {
                'Pendiente': '⚪',
                'Llegó': '🔵',
                'En Consulta': '🟢',
                'Completada': '✅',
                'No-show': '🔴'
            }
            
            col1, col2, col3 = st.columns([1, 3, 2])
            with col1:
                st.write(f"**{hora}**")
            with col2:
                st.write(f"{cita['paciente_nombre']}")
            with col3:
                st.write(f"{estado_emoji.get(cita['estado'], '⚪')} {cita['estado']}")
    else:
        st.info("No hay citas programadas para hoy")
    
    # Estadísticas del mes
    st.markdown("---")
    st.subheader("📈 Estadísticas del Mes")
    
    primer_dia_mes = date.today().replace(day=1).strftime('%Y-%m-%d')
    stats = db.get_noshow_stats(
        medico_id=medico_id,
        fecha_inicio=primer_dia_mes,
        fecha_fin=date.today().strftime('%Y-%m-%d')
    )
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Citas", stats['total_citas'])
    with col2:
        st.metric("Completadas", stats['total_completadas'])
    with col3:
        st.metric("No-shows", stats['total_noshows'])
    with col4:
        delta_color = "normal" if stats['tasa_asistencia'] >= 80 else "inverse"
        st.metric("Tasa Asistencia", f"{stats['tasa_asistencia']}%")
    
    # Gráfico de distribución
    if stats['total_citas'] > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart de estados
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
                hole=0.4
            )])
            
            fig.update_layout(
                title="Distribución de Estados",
                showlegend=True,
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Gauge de tasa de asistencia
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=stats['tasa_asistencia'],
                title={'text': "Tasa de Asistencia (%)"},
                delta={'reference': 85},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#228B22"},
                    'steps': [
                        {'range': [0, 60], 'color': "#FFCDD2"},
                        {'range': [60, 80], 'color': "#FFF9C4"},
                        {'range': [80, 100], 'color': "#E8F5E9"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 85
                    }
                }
            ))
            
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    # Alertas clínicas
    st.markdown("---")
    st.subheader("⚠️ Alertas Clínicas")
    
    # Aquí se podrían agregar consultas específicas para alertas
    # Por ejemplo: pacientes pediátricos con Z-scores anormales, adultos con riesgo alto, etc.
    st.info("Funcionalidad de alertas clínicas en desarrollo...")


def mostrar_dashboard_general():
    """Dashboard general para admin y recepción."""
    st.subheader("Vista General del Sistema")
    
    # Estadísticas generales
    pacientes = db.get_all_pacientes()
    medicos = db.get_all_medicos()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Pacientes", len(pacientes))
        pediatricos = sum(1 for p in pacientes if p['es_pediatrico'])
        st.caption(f"👶 {pediatricos} pediátricos | 👤 {len(pacientes) - pediatricos} adultos")
    
    with col2:
        st.metric("Médicos Activos", len(medicos))
    
    with col3:
        # Citas de hoy (todos los médicos)
        hoy = datetime.now().strftime('%Y-%m-%d')
        total_citas_hoy = 0
        for medico in medicos:
            citas = db.get_citas_by_medico_fecha(medico['id'], hoy)
            total_citas_hoy += len(citas)
        st.metric("Citas Hoy", total_citas_hoy)
    
    # Distribución de pacientes
    st.markdown("---")
    st.subheader("📊 Distribución de Pacientes")
    
    if pacientes:
        pediatricos = sum(1 for p in pacientes if p['es_pediatrico'])
        adultos = len(pacientes) - pediatricos
        
        fig = go.Figure(data=[go.Pie(
            labels=['Pediátricos', 'Adultos'],
            values=[pediatricos, adultos],
            marker=dict(colors=['#4169E1', '#32CD32']),
            hole=0.3
        )])
        
        fig.update_layout(
            title="Distribución por Tipo de Paciente",
            showlegend=True,
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Estadísticas por médico
    st.markdown("---")
    st.subheader("📈 Rendimiento por Médico (Mes Actual)")
    
    primer_dia_mes = date.today().replace(day=1).strftime('%Y-%m-%d')
    
    medicos_data = []
    for medico in medicos:
        stats = db.get_noshow_stats(
            medico_id=medico['id'],
            fecha_inicio=primer_dia_mes,
            fecha_fin=date.today().strftime('%Y-%m-%d')
        )
        medicos_data.append({
            'Médico': medico['nombre'],
            'Especialidad': medico['especialidad'],
            'Total Citas': stats['total_citas'],
            'Completadas': stats['total_completadas'],
            'No-shows': stats['total_noshows'],
            'Tasa Asistencia': stats['tasa_asistencia']
        })
    
    if medicos_data:
        import pandas as pd
        df = pd.DataFrame(medicos_data)
        
        # Tabla
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Gráfico de barras
        fig = px.bar(
            df,
            x='Médico',
            y='Tasa Asistencia',
            color='Especialidad',
            title='Tasa de Asistencia por Médico (%)',
            labels={'Tasa Asistencia': 'Tasa de Asistencia (%)'}
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
