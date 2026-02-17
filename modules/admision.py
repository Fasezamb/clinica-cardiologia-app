"""
Módulo de Admisión de Pacientes.
Permite registrar, buscar y editar pacientes, así como realizar triaje.
"""

import streamlit as st
from datetime import datetime, date
import database as db


def calcular_edad(fecha_nacimiento_str: str) -> int:
    """Calcula la edad a partir de la fecha de nacimiento."""
    fecha_nac = datetime.strptime(fecha_nacimiento_str, '%Y-%m-%d').date()
    hoy = date.today()
    edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
    return edad


def validar_constantes_vitales(fc: int, ta_sistolica: int, ta_diastolica: int, sato2: float) -> list:
    """Valida las constantes vitales y retorna alertas si hay valores anormales."""
    alertas = []
    
    # Frecuencia cardíaca
    if fc < 60:
        alertas.append("⚠️ Bradicardia (FC < 60)")
    elif fc > 100:
        alertas.append("⚠️ Taquicardia (FC > 100)")
    
    # Tensión arterial
    if ta_sistolica >= 140 or ta_diastolica >= 90:
        alertas.append("⚠️ Hipertensión (TA ≥ 140/90)")
    elif ta_sistolica < 90 or ta_diastolica < 60:
        alertas.append("⚠️ Hipotensión (TA < 90/60)")
    
    # Saturación de oxígeno
    if sato2 < 95:
        alertas.append("⚠️ Saturación de O2 baja (< 95%)")
    
    return alertas


def show():
    """Función principal del módulo de admisión."""
    st.title("📋 Admisión de Pacientes")
    
    # Tabs para diferentes funcionalidades
    tab1, tab2, tab3 = st.tabs(["Registrar Paciente", "Buscar Paciente", "Triaje"])
    
    # ==================== TAB 1: Registrar Paciente ====================
    with tab1:
        st.subheader("Nuevo Paciente")
        
        with st.form("registro_paciente"):
            col1, col2 = st.columns(2)
            
            with col1:
                nombre = st.text_input("Nombre Completo *", placeholder="Ej: Juan Pérez García")
                fecha_nacimiento = st.date_input(
                    "Fecha de Nacimiento *",
                    min_value=date(1900, 1, 1),
                    max_value=date.today()
                )
                contacto = st.text_input("Teléfono de Contacto *", placeholder="Ej: 555-1234")
            
            with col2:
                es_pediatrico = st.checkbox("¿Es paciente pediátrico? (< 18 años)")
                
                # Mostrar campo de tutor legal solo si es pediátrico
                tutor_legal = None
                if es_pediatrico:
                    tutor_legal = st.text_input(
                        "Nombre del Tutor Legal *",
                        placeholder="Ej: María Pérez"
                    )
                    st.info("👶 Paciente pediátrico - Se requiere tutor legal")
            
            submitted = st.form_submit_button("💾 Guardar Paciente", use_container_width=True)
            
            if submitted:
                # Validaciones
                if not nombre or not contacto:
                    st.error("Por favor complete todos los campos obligatorios (*)")
                elif es_pediatrico and not tutor_legal:
                    st.error("Debe ingresar el nombre del tutor legal para pacientes pediátricos")
                else:
                    # Validar edad vs checkbox pediátrico
                    edad = calcular_edad(fecha_nacimiento.strftime('%Y-%m-%d'))
                    
                    if edad < 18 and not es_pediatrico:
                        st.warning(f"El paciente tiene {edad} años. ¿Desea marcarlo como pediátrico?")
                    elif edad >= 18 and es_pediatrico:
                        st.warning(f"El paciente tiene {edad} años. ¿Está seguro que es pediátrico?")
                    
                    # Crear paciente
                    try:
                        paciente_id = db.create_paciente(
                            nombre=nombre,
                            fecha_nacimiento=fecha_nacimiento.strftime('%Y-%m-%d'),
                            es_pediatrico=es_pediatrico,
                            contacto=contacto,
                            tutor_legal=tutor_legal
                        )
                        st.success(f"✅ Paciente registrado exitosamente (ID: {paciente_id})")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Error al registrar paciente: {str(e)}")
    
    # ==================== TAB 2: Buscar Paciente ====================
    with tab2:
        st.subheader("Buscar y Editar Pacientes")
        
        # Barra de búsqueda
        col1, col2 = st.columns([3, 1])
        with col1:
            query = st.text_input("🔍 Buscar por nombre o ID", placeholder="Ingrese nombre o ID del paciente")
        with col2:
            buscar = st.button("Buscar", use_container_width=True)
        
        # Mostrar todos los pacientes si no hay búsqueda
        if query and buscar:
            pacientes = db.search_pacientes(query)
        else:
            pacientes = db.get_all_pacientes()
        
        if pacientes:
            st.write(f"**{len(pacientes)} paciente(s) encontrado(s)**")
            
            for paciente in pacientes:
                edad = calcular_edad(paciente['fecha_nacimiento'])
                tipo = "👶 Pediátrico" if paciente['es_pediatrico'] else "👤 Adulto"
                
                with st.expander(f"{paciente['nombre']} - {edad} años - {tipo}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**ID:** {paciente['id']}")
                        st.write(f"**Nombre:** {paciente['nombre']}")
                        st.write(f"**Fecha de Nacimiento:** {paciente['fecha_nacimiento']}")
                        st.write(f"**Edad:** {edad} años")
                    
                    with col2:
                        st.write(f"**Tipo:** {tipo}")
                        st.write(f"**Contacto:** {paciente['contacto']}")
                        if paciente['tutor_legal']:
                            st.write(f"**Tutor Legal:** {paciente['tutor_legal']}")
                        st.write(f"**Registrado:** {paciente['created_at']}")
                    
                    # Botón para editar (funcionalidad básica)
                    if st.button(f"✏️ Editar", key=f"edit_{paciente['id']}"):
                        st.info("Funcionalidad de edición en desarrollo...")
        else:
            st.info("No se encontraron pacientes")
    
    # ==================== TAB 3: Triaje ====================
    with tab3:
        st.subheader("Triaje - Constantes Vitales")
        st.write("Registre las constantes vitales del paciente antes de la consulta")
        
        # Seleccionar paciente
        pacientes = db.get_all_pacientes()
        if not pacientes:
            st.warning("No hay pacientes registrados. Por favor registre un paciente primero.")
            return
        
        pacientes_dict = {f"{p['nombre']} (ID: {p['id']})": p['id'] for p in pacientes}
        paciente_seleccionado = st.selectbox("Seleccionar Paciente", list(pacientes_dict.keys()))
        
        if paciente_seleccionado:
            paciente_id = pacientes_dict[paciente_seleccionado]
            paciente = db.get_paciente(paciente_id)
            
            # Mostrar información del paciente
            edad = calcular_edad(paciente['fecha_nacimiento'])
            tipo = "Pediátrico" if paciente['es_pediatrico'] else "Adulto"
            st.info(f"👤 **{paciente['nombre']}** - {edad} años - {tipo}")
            
            with st.form("triaje_form"):
                st.write("**Constantes Vitales**")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fc = st.number_input("Frecuencia Cardíaca (FC)", min_value=30, max_value=200, value=75)
                    ta_sistolica = st.number_input("TA Sistólica (mmHg)", min_value=50, max_value=250, value=120)
                
                with col2:
                    ta_diastolica = st.number_input("TA Diastólica (mmHg)", min_value=30, max_value=150, value=80)
                    sato2 = st.number_input("Saturación O2 (%)", min_value=70.0, max_value=100.0, value=98.0, step=0.1)
                
                motivo = st.text_area("Motivo de Consulta (opcional)", placeholder="Ej: Control de rutina")
                
                guardar_triaje = st.form_submit_button("💾 Guardar Triaje", use_container_width=True)
                
                if guardar_triaje:
                    # Validar constantes vitales
                    alertas = validar_constantes_vitales(fc, ta_sistolica, ta_diastolica, sato2)
                    
                    if alertas:
                        st.warning("**Alertas detectadas:**")
                        for alerta in alertas:
                            st.write(alerta)
                    
                    # Guardar en HCE común (sin asignar a cita aún)
                    try:
                        # Obtener médico actual si está logueado
                        medico_id = st.session_state.user.get('medico_id', 1)  # Default a médico 1 si no hay
                        
                        hce_id = db.create_hce_comun(
                            paciente_id=paciente_id,
                            medico_id=medico_id,
                            fecha_consulta=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            motivo_consulta=motivo if motivo else "Triaje",
                            fc=fc,
                            ta_sistolica=ta_sistolica,
                            ta_diastolica=ta_diastolica,
                            sato2=sato2,
                            cita_id=None,
                            observaciones="Registro de triaje"
                        )
                        st.success(f"✅ Triaje guardado exitosamente (ID: {hce_id})")
                        
                        if alertas:
                            st.info("⚠️ Se recomienda evaluación médica inmediata")
                    except Exception as e:
                        st.error(f"Error al guardar triaje: {str(e)}")
