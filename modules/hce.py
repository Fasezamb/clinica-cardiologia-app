"""
Módulo de Historia Clínica Electrónica (HCE).
Formularios diferenciados para pacientes pediátricos y adultos con cálculos médicos automatizados.
"""

import streamlit as st
from datetime import datetime, date
import database as db
import math
import traceback


# ==================== Funciones de Cálculo Pediátrico ====================

def calcular_superficie_corporal(peso_kg: float, talla_cm: float) -> float:
    """Calcula la superficie corporal usando la fórmula de Haycock."""
    # SC (m²) = 0.024265 × peso^0.5378 × talla^0.3964
    sc = 0.024265 * (peso_kg ** 0.5378) * (talla_cm ** 0.3964)
    return round(sc, 3)


def calcular_zscore_valvular(diametro_mm: float, sc: float, tipo_valvula: str) -> float:
    """
    Calcula el Z-score de una válvula cardíaca basado en superficie corporal.
    Fórmula simplificada: Z = (Diámetro observado - Diámetro esperado) / DE
    
    Nota: Esta es una implementación simplificada. En producción se deben usar
    las tablas de referencia específicas por edad y superficie corporal.
    """
    # Valores de referencia aproximados (deben ser validados por cardiólogos)
    referencias = {
        'aortico': {'media': 15.0, 'de': 2.0},
        'pulmonar': {'media': 14.0, 'de': 2.0},
        'mitral': {'media': 18.0, 'de': 2.5},
        'tricuspide': {'media': 20.0, 'de': 3.0}
    }
    
    ref = referencias.get(tipo_valvula.lower(), {'media': 15.0, 'de': 2.0})
    
    # Ajustar por superficie corporal (aproximación)
    diametro_esperado = ref['media'] * math.sqrt(sc / 0.5)  # 0.5 m² es referencia
    zscore = (diametro_mm - diametro_esperado) / ref['de']
    
    return round(zscore, 2)


def calcular_percentil(valor: float, edad_meses: int, tipo: str, es_niño: bool) -> float:
    """
    Calcula el percentil de peso o talla según tablas OMS.
    
    Nota: Esta es una implementación simplificada. En producción se deben usar
    las tablas completas de la OMS por edad y sexo.
    """
    # Implementación simplificada - retorna un percentil aproximado
    # En producción, usar las tablas oficiales de la OMS
    
    if tipo == 'peso':
        # Aproximación muy básica
        if valor < 10:
            return 10
        elif valor < 15:
            return 25
        elif valor < 20:
            return 50
        elif valor < 25:
            return 75
        else:
            return 90
    else:  # talla
        if valor < 80:
            return 10
        elif valor < 95:
            return 25
        elif valor < 110:
            return 50
        elif valor < 125:
            return 75
        else:
            return 90


# ==================== Funciones de Cálculo Adulto ====================

def calcular_riesgo_score(edad: int, sexo: str, colesterol_total: float, 
                         colesterol_hdl: float, ta_sistolica: int, 
                         fumador: bool) -> float:
    """
    Calcula el riesgo cardiovascular según SCORE (European).
    
    Nota: Esta es una implementación simplificada. En producción se debe usar
    la tabla completa de SCORE con todos los factores de riesgo.
    """
    # Implementación simplificada
    riesgo = 0.0
    
    # Factor edad
    if edad >= 65:
        riesgo += 5.0
    elif edad >= 55:
        riesgo += 3.0
    elif edad >= 45:
        riesgo += 1.5
    
    # Factor sexo
    if sexo.lower() == 'masculino':
        riesgo += 1.0
    
    # Factor colesterol
    if colesterol_total > 240:
        riesgo += 2.0
    elif colesterol_total > 200:
        riesgo += 1.0
    
    if colesterol_hdl < 40:
        riesgo += 1.5
    
    # Factor presión arterial
    if ta_sistolica >= 160:
        riesgo += 2.0
    elif ta_sistolica >= 140:
        riesgo += 1.0
    
    # Factor tabaquismo
    if fumador:
        riesgo += 2.0
    
    return round(riesgo, 2)


def calcular_riesgo_framingham(edad: int, sexo: str, colesterol_total: float,
                               colesterol_hdl: float, ta_sistolica: int,
                               fumador: bool, diabetes: bool) -> float:
    """
    Calcula el riesgo cardiovascular según Framingham.
    
    Nota: Esta es una implementación simplificada. En producción se debe usar
    la fórmula completa de Framingham.
    """
    # Implementación simplificada similar a SCORE
    riesgo = calcular_riesgo_score(edad, sexo, colesterol_total, colesterol_hdl, 
                                   ta_sistolica, fumador)
    
    # Factor diabetes (específico de Framingham)
    if diabetes:
        riesgo += 2.5
    
    return round(riesgo, 2)


def clasificar_riesgo(riesgo: float) -> str:
    """Clasifica el nivel de riesgo cardiovascular."""
    if riesgo < 5:
        return "Bajo"
    elif riesgo < 10:
        return "Moderado"
    elif riesgo < 20:
        return "Alto"
    else:
        return "Muy Alto"


def get_color_riesgo(clasificacion: str) -> str:
    """Retorna el color asociado a cada nivel de riesgo."""
    colores = {
        'Bajo': '#32CD32',      # Verde
        'Moderado': '#FFD700',  # Amarillo
        'Alto': '#FF8C00',      # Naranja
        'Muy Alto': '#DC143C'   # Rojo
    }
    return colores.get(clasificacion, '#808080')


# ==================== Función Principal ====================

def show():
    """Función principal del módulo de HCE."""
    st.title("📝 Historia Clínica Electrónica")
    
    # Seleccionar paciente
    pacientes = db.get_all_pacientes()
    if not pacientes:
        st.warning("No hay pacientes registrados. Por favor registre un paciente primero.")
        return
    
    # Pacientes en espera (UX Improvement)
    citas_hoy = db.get_citas_by_medico_fecha(st.session_state.user.get('medico_id', 1), date.today().strftime('%Y-%m-%d'))
    pacientes_esperando = [c for c in citas_hoy if c['estado'] == 'Llegó']
    
    if pacientes_esperando:
        st.info(f"💡 **Pacientes en Sala de Espera ({len(pacientes_esperando)}):** " + 
                ", ".join([f"{c['paciente_nombre']}" for c in pacientes_esperando]))
    
    pacientes_dict = {f"{p['nombre']} (ID: {p['id']})": p for p in pacientes}
    paciente_seleccionado = st.selectbox("Seleccionar Paciente", list(pacientes_dict.keys()))
    
    if not paciente_seleccionado:
        return
    
    paciente = pacientes_dict[paciente_seleccionado]
    
    # Calcular edad
    fecha_nac = datetime.strptime(paciente['fecha_nacimiento'], '%Y-%m-%d').date()
    edad = (date.today() - fecha_nac).days // 365
    edad_meses = (date.today() - fecha_nac).days // 30
    
    # Mostrar información del paciente
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**Paciente:** {paciente['nombre']}")
    with col2:
        tipo = "👶 Pediátrico" if paciente['es_pediatrico'] else "👤 Adulto"
        st.info(f"**Tipo:** {tipo}")
    with col3:
        st.info(f"**Edad:** {edad} años")
    
    # Mostrar historial previo
    with st.expander("📋 Ver Historial de Consultas"):
        historial = db.get_hce_by_paciente(paciente['id'])
        if historial:
            for registro in historial:
                fecha = datetime.fromisoformat(registro['fecha_consulta']).strftime('%d/%m/%Y %H:%M')
                st.write(f"**{fecha}** - Dr. {registro['medico_nombre']}")
                st.write(f"Motivo: {registro['motivo_consulta']}")
                st.write(f"FC: {registro['fc']} | TA: {registro['ta_sistolica']}/{registro['ta_diastolica']} | SatO2: {registro['sato2']}%")
                st.divider()
        else:
            st.info("No hay consultas previas registradas")
    
    st.markdown("---")
    st.subheader("Nueva Consulta")
    
    # Formulario dinámico con Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🩺 Consulta & Triaje", "🧪 Órdenes Externas", "🏁 Diagnóstico y Récipes", "📂 Historial de Informes"])
    
    sexo = paciente.get('sexo', 'Masculino') # Default value

    
    with tab1:
        st.write("### Paso 2: Evaluación Clínica & Triaje")
        
        # Triaje (Signos Vitales)
        st.subheader("1. Triaje (Signos Vitales)")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            fc = st.number_input("FC (lpm)", min_value=30, max_value=200, value=75)
        with col2:
            ta_sistolica = st.number_input("TA Sistólica", min_value=50, max_value=250, value=120)
        with col3:
            ta_diastolica = st.number_input("TA Diastólica", min_value=30, max_value=150, value=80)
        with col4:
            sato2 = st.number_input("SatO2 (%)", min_value=70.0, max_value=100.0, value=98.0, step=0.1)
        
        # Motivo e Historia
        st.subheader("2. Historia Clínica")
        motivo_consulta = st.text_area("Motivo de Consulta *", placeholder="Ej: Control de rutina, dolor torácico...")
        observaciones = st.text_area("Antecedentes y Evolución actual", placeholder="Detalles de la historia clínica...")

        # Examen Físico
        st.subheader("3. Examen Físico")
        col_ef1, col_ef2 = st.columns(2)
        with col_ef1:
            ef_general = st.text_area("Aspecto General", placeholder="Fascie, hidratación, etc.")
            ef_cardio = st.text_area("Aparato Cardiovascular", placeholder="Ruidos cardíacos, soplos, pulsos...")
        with col_ef2:
            ef_respiratorio = st.text_area("Aparato Respiratorio", placeholder="Murmullo vesicular, ruidos agregados...")
            ef_otros = st.text_area("Otros Hallazgos", placeholder="Abdomen, extremidades, etc.")
        
        # Estudios en Consultorio
        st.subheader("4. Estudios en Consultorio (ECG/Echo)")
        col_ecg, col_echo = st.columns(2)
        with col_ecg:
            ecg_hallazgos = st.text_area("Hallazgos Electrocardiograma (ECG)", placeholder="Ritmo, eje, PR, QRS, QT...")
        with col_echo:
            echo_hallazgos = st.text_area("Hallazgos Ecosonograma", placeholder="Función ventricular, válvulas, pericardio...")

        # Datos específicos (Pediátrico / Adulto) - Mantenidos para cálculos
        if paciente['es_pediatrico']:
            st.divider()
            st.write("#### 👶 Cálculos Pediátricos")
            
            col1, col2 = st.columns(2)
            with col1:
                peso_kg = st.number_input("Peso (kg)", min_value=1.0, max_value=100.0, value=15.0, step=0.1)
            with col2:
                talla_cm = st.number_input("Talla (cm)", min_value=30.0, max_value=200.0, value=100.0, step=0.5)
            
            sc = calcular_superficie_corporal(peso_kg, talla_cm)
            percentil_peso = calcular_percentil(peso_kg, edad_meses, 'peso', True)
            percentil_talla = calcular_percentil(talla_cm, edad_meses, 'talla', True)
            
            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("Superficie Corporal", f"{sc} m²")
            col_m2.metric("Percentil Peso", f"P{percentil_peso}")
            col_m3.metric("Percentil Talla", f"P{percentil_talla}")
            
            # Z-Scores simplificados
            st.write("**Z-Scores Valvulares**")
            col1, col2, col3, col4 = st.columns(4)
            with col1: diam_aortico = st.number_input("Aórtico", value=15.0)
            with col2: diam_pulmonar = st.number_input("Pulmonar", value=14.0)
            with col3: diam_mitral = st.number_input("Mitral", value=18.0)
            with col4: diam_tricuspide = st.number_input("Tricúspide", value=20.0)
            
            zscore_aortico = calcular_zscore_valvular(diam_aortico, sc, 'aortico')
            zscore_pulmonar = calcular_zscore_valvular(diam_pulmonar, sc, 'pulmonar')
            zscore_mitral = calcular_zscore_valvular(diam_mitral, sc, 'mitral')
            zscore_tricuspide = calcular_zscore_valvular(diam_tricuspide, sc, 'tricuspide')
            
            ductus_estado = st.selectbox("Ductus Arterioso", ["Cerrado", "Abierto", "Restrictivo"])
            ductus_tamaño_mm = st.number_input("Tamaño Ductus (mm)", value=0.0) if ductus_estado != "Cerrado" else None
        else:
            st.divider()
            st.write("#### 👤 Riesgo Cardiovascular (Adulto)")
            col1, col2, col3 = st.columns(3)
            with col1: tiene_hta = st.checkbox("Hipertensión Arterial")
            with col2: tiene_diabetes = st.checkbox("Diabetes Mellitus")
            with col3: tabaquismo = st.radio("Tabaquismo", ["No", "Activo", "Ex-fumador"], horizontal=True)
            
            # Sexo (Necesario para riesgo cardiovascular)
            sex_index = 0 if paciente.get('sexo') == 'Masculino' else 1 if paciente.get('sexo') == 'Femenino' else 0
            sexo = st.radio("Sexo", ["Masculino", "Femenino"], index=sex_index, horizontal=True)
            
            col1, col2 = st.columns(2)
            with col1: colesterol_total = st.number_input("Colesterol Total", value=200.0)
            with col2: colesterol_hdl = st.number_input("HDL", value=50.0)
            
            riesgo_score = calcular_riesgo_score(edad, sexo, colesterol_total, colesterol_hdl, ta_sistolica, tabaquismo=="Activo")
            riesgo_framingham = calcular_riesgo_framingham(edad, sexo, colesterol_total, colesterol_hdl, ta_sistolica, tabaquismo=="Activo", tiene_diabetes)
            clasificacion = clasificar_riesgo(riesgo_score)
            st.metric("Riesgo SCORE", f"{riesgo_score}%", help=f"Clasificación: {clasificacion}")

    with tab2:
        st.write("### Paso 3: Órdenes Médicas (Exámenes Externos)")
        st.info("Solicitud de laboratorios, rayos X y otros estudios complementarios.")
        
        examenes_comunes = ["Laboratorio Completo", "Perfil Lipídico", "RX Tórax", "Prueba de Esfuerzo", "MAPA 24h", "RNM Cardíaca"]
        examenes_selec = st.multiselect("Seleccionar Exámenes Externos", examenes_comunes)
        
        examenes_data = []
        for examen in examenes_selec:
            indicacion = st.text_input(f"Indicaciones para {examen}", key=f"ext_ind_{examen}")
            examenes_data.append({'tipo_examen': examen, 'indicacion': indicacion})
            
        otro_examen_ext = st.checkbox("Otro estudio externo")
        if otro_examen_ext:
            otro_tipo = st.text_input("Nombre del estudio adicional")
            otra_ind = st.text_input("Indicaciones adicionales")
            if otro_tipo:
                examenes_data.append({'tipo_examen': otro_tipo, 'indicacion': otra_ind})

    with tab3:
        st.write("### Paso 4: Diagnóstico y Récipes")
        
        st.subheader("1. Conclusión Médica")
        diagnostico = st.text_area("Diagnóstico Final / Presuntivo *", placeholder="Ej: Hipertensión Arterial Grado I, Arritmia Sinusal...")
        
        st.divider()
        st.subheader("2. Prescripción de Medicamentos (Récipes)")
        num_recetas = st.number_input("Número de medicamentos a prescribir", min_value=0, max_value=12, value=1)
        recetas_data = []
        
        for i in range(int(num_recetas)):
            with st.expander(f"Medicamento {i+1}", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    med = st.text_input("Nombre del Medicamento", key=f"rx_med_{i}")
                    dosis = st.text_input("Dosis (Ej: 50mg, 1 tab)", key=f"rx_dosis_{i}")
                with col2:
                    freq = st.text_input("Frecuencia (Ej: Cada 12h, Diaria)", key=f"rx_freq_{i}")
                    dur = st.text_input("Duración (Ej: 30 días, Permanente)", key=f"rx_dur_{i}")
                adicional = st.text_input("Indicaciones al paciente", key=f"rx_adic_{i}")
                
                if med:
                    recetas_data.append({
                        'medicamento': med, 'dosis': dosis, 'frecuencia': freq,
                        'duracion': dur, 'indicaciones_adicionales': adicional
                    })
        
        st.divider()
        st.write("### Finalizar Consulta")
        submitted = st.button("💾 GUARDAR CONSULTA Y GENERAR DOCUMENTOS", use_container_width=True, type="primary")

    with tab4:
        st.write("### 📂 Historial de Informes PDF")
        st.info("Aquí puede ver y descargar los informes generados previamente para este paciente.")
        
        import os
        reports_dir = "medical_reports"
        if os.path.exists(reports_dir):
            # Buscar archivos que contengan el nombre del paciente
            # El formato es Informe_Nombre_Apellido_Fecha.pdf
            nombre_busqueda = paciente['nombre'].replace(' ', '_')
            archivos = [f for f in os.listdir(reports_dir) if f.startswith(f"Informe_{nombre_busqueda}") and f.endswith(".pdf")]
            archivos.sort(reverse=True) # Los más nuevos primero
            
            if archivos:
                for arc in archivos:
                    col_name, col_dl, col_view = st.columns([2, 1, 1])
                    with col_name:
                        st.write(f"📄 {arc}")
                    with col_dl:
                        with open(os.path.join(reports_dir, arc), "rb") as f:
                            st.download_button(
                                label="⬇️ Descargar",
                                data=f.read(),
                                file_name=arc,
                                mime="application/pdf",
                                key=f"btn_dl_{arc}"
                            )
                    with col_view:
                        if st.button("👁️ Vista Previa", key=f"btn_v_{arc}"):
                            with open(os.path.join(reports_dir, arc), "rb") as f:
                                from modules.reportes import mostrar_pdf
                                mostrar_pdf(f.read())
                    st.divider()
            else:
                st.write("No se encontraron informes guardados para este paciente.")
        else:
            st.write("Aún no se han generado informes médicos.")
        
    if submitted:
        if not motivo_consulta:
            st.error("El motivo de consulta es obligatorio")
        else:
            try:
                # Obtener médico actual
                usuario_actual = st.session_state.user
                medico_id = usuario_actual.get('medico_id')
                
                if not medico_id:
                     # Fallback for admin or testing without linked doctor
                     # Try to find a default doctor or use ID 1
                     medico_id = 1
                
                fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                # 1. Guardar HCE común
                hce_comun_id = db.create_hce_comun(
                    paciente_id=paciente['id'],
                    medico_id=medico_id,
                    fecha_consulta=fecha_actual,
                    motivo_consulta=motivo_consulta,
                    diagnostico=diagnostico,
                    fc=fc,
                    ta_sistolica=ta_sistolica,
                    ta_diastolica=ta_diastolica,
                    sato2=sato2,
                    ef_general=ef_general,
                    ef_cardio=ef_cardio,
                    ef_respiratorio=ef_respiratorio,
                    ef_otros=ef_otros,
                    ecg_hallazgos=ecg_hallazgos,
                    echo_hallazgos=echo_hallazgos,
                    observaciones=observaciones
                )
                
                # 2. Guardar datos específicos
                hce_detalle = {}
                hce_tipo = ''
                
                if paciente['es_pediatrico']:
                    hce_tipo = 'infantil'
                    hce_detalle = {
                        'peso_kg': peso_kg, 'talla_cm': talla_cm,
                        'percentil_peso': percentil_peso, 'percentil_talla': percentil_talla,
                        'zscore_aortico': zscore_aortico, 'zscore_pulmonar': zscore_pulmonar,
                        'zscore_mitral': zscore_mitral, 'zscore_tricuspide': zscore_tricuspide,
                        'ductus_estado': ductus_estado, 'ductus_tamaño_mm': ductus_tamaño_mm
                    }
                    db.create_hce_infantil(hce_comun_id=hce_comun_id, **hce_detalle)
                else:
                    hce_tipo = 'adulto'
                    hce_detalle = {
                        'tiene_hta': tiene_hta, 'tiene_diabetes': tiene_diabetes,
                        'tabaquismo': tabaquismo, 'colesterol_total': colesterol_total,
                        'colesterol_hdl': colesterol_hdl, 'riesgo_cardiovascular_score': riesgo_score,
                        'riesgo_cardiovascular_framingham': riesgo_framingham, 'clasificacion_riesgo': clasificacion
                    }
                    db.create_hce_adulto(hce_comun_id=hce_comun_id, **hce_detalle)
                    # Actualizar sexo del paciente en la tabla principal si cambió o no existía
                    db.update_paciente_sexo(paciente['id'], sexo)
                
                # 3. Guardar Exámenes
                for ex in examenes_data:
                    db.create_indicacion_examen(hce_comun_id, ex['tipo_examen'], ex['indicacion'])
                    
                # 4. Guardar Recetas
                for rx in recetas_data:
                    db.create_receta(hce_comun_id, rx['medicamento'], rx['dosis'], rx['frecuencia'], rx['duracion'], rx['indicaciones_adicionales'])
                
                st.success("✅ Consulta guardada exitosamente")
                
                # 5. Generar PDF
                from modules.reportes import generar_pdf_consulta
                
                # Recuperar datos completos del médico para el reporte
                medico_data = db.get_medico(medico_id)
                if not medico_data:
                    medico_data = {'nombre': 'Médico General', 'especialidad': 'Cardiología', 'email': ''}
                    
                consulta_data = {
                    'fecha_consulta': fecha_actual,
                    'motivo_consulta': motivo_consulta,
                    'diagnostico': diagnostico,
                    'fc': fc, 'ta_sistolica': ta_sistolica, 'ta_diastolica': ta_diastolica, 'sato2': sato2,
                    'ef_general': ef_general, 'ef_cardio': ef_cardio, 'ef_respiratorio': ef_respiratorio, 'ef_otros': ef_otros,
                    'ecg_hallazgos': ecg_hallazgos, 'echo_hallazgos': echo_hallazgos,
                    'observaciones': observaciones
                }
                
                pdf_file = generar_pdf_consulta(
                    paciente=paciente,
                    medico=medico_data,
                    consulta=consulta_data,
                    hce_detalle=hce_detalle,
                    hce_tipo=hce_tipo,
                    indicaciones=examenes_data,
                    recetas=recetas_data
                )
                
                # --- GUARDAR COPIA EN SERVIDOR ---
                # Importamos os dinámicamente o nos aseguramos que esté al inicio
                import os
                reports_dir = "medical_reports"
                if not os.path.exists(reports_dir):
                    os.makedirs(reports_dir)
                
                filename = f"Informe_{paciente['nombre'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                filepath = os.path.join(reports_dir, filename)
                
                with open(filepath, "wb") as f:
                    f.write(pdf_file.getbuffer())
                
                st.download_button(
                    label="📄 Descargar Informe Médico (PDF)",
                    data=pdf_file.getvalue(),
                    file_name=filename,
                    mime="application/pdf"
                )
                
                st.info(f"💾 Copia guardada en el servidor: `{filepath}`")
                
                # --- VISTA PREVIA INMEDIATA ---
                st.write("### 👁️ Vista Previa del Informe")
                from modules.reportes import mostrar_pdf
                mostrar_pdf(pdf_file.getvalue())
                
            except Exception as e:
                st.error(f"Error al guardar consulta: {str(e)}")
                st.error(traceback.format_exc())
