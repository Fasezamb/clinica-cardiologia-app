from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io
import base64
import streamlit as st
from datetime import datetime, date

def mostrar_pdf(pdf_bytes):
    """Muestra un PDF en pantalla usando un iframe."""
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    # Aumentamos el alto a 1200 para que se vea más como una hoja real
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="1200" type="application/pdf" style="border: 1px solid #ccc; border-radius: 8px;"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def _insertar_encabezado(Story, styles, medico, paciente, titulo_seccion, fecha_consulta):
    """Inserta el encabezado de la clínica y datos del paciente."""
    estilo_titulo = ParagraphStyle(
        'TituloClínica',
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        fontSize=16,
        spaceAfter=10
    )
    estilo_seccion = ParagraphStyle(
        'TituloSeccion',
        parent=styles['Heading2'],
        alignment=TA_CENTER,
        fontSize=14,
        spaceAfter=15,
        textColor=colors.darkblue
    )
    estilo_normal = styles["Normal"]
    
    Story.append(Paragraph("CLÍNICA CARDIOLOGÍA 'CardioCloud'", estilo_titulo))
    Story.append(Paragraph(f"Dr. {medico['nombre']} | {medico['especialidad']}", estilo_normal))
    Story.append(Paragraph(f"Email: {medico['email']}", estilo_normal))
    Story.append(Spacer(1, 10))
    Story.append(Paragraph("_" * 70, estilo_normal))
    Story.append(Spacer(1, 15))
    
    Story.append(Paragraph(titulo_seccion.upper(), estilo_seccion))
    
    datos_paciente = [
        [f"Paciente: {paciente['nombre']}", f"Fecha: {fecha_consulta}"],
        [f"ID Paciente: {paciente['id']}", f"Edad: {calcular_edad(paciente['fecha_nacimiento'])} años"]
    ]
    
    t_paciente = Table(datos_paciente, colWidths=[300, 200])
    t_paciente.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    Story.append(t_paciente)
    Story.append(Spacer(1, 15))

def _insertar_firma(Story, styles, medico):
    """Inserta la línea de firma al final de cada página."""
    estilo_normal = styles["Normal"]
    estilo_firma = ParagraphStyle('Firma', parent=estilo_normal, alignment=TA_CENTER)
    
    Story.append(Spacer(1, 40))
    Story.append(Paragraph("_" * 40, estilo_firma))
    Story.append(Paragraph(f"Dr. {medico['nombre']}", estilo_firma))
    Story.append(Paragraph(f"Cardiología - {medico['especialidad']}", estilo_firma))

def generar_pdf_consulta(paciente, medico, consulta, hce_detalle, hce_tipo, indicaciones, recetas):
    """
    Genera un informe médico en PDF con 2 hojas: 
    H1: Informe Médico (Clínico)
    H2: Récipe e Indicaciones
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=50, leftMargin=50,
                            topMargin=50, bottomMargin=50)

    Story = []
    styles = getSampleStyleSheet()
    estilo_normal = styles["Normal"]
    estilo_negrita = ParagraphStyle('Negrita', parent=estilo_normal, fontName='Helvetica-Bold')
    estilo_subtitulo = ParagraphStyle('Sub', parent=styles['Heading3'], textColor=colors.darkblue)
    
    try:
        fecha_obj = datetime.strptime(consulta['fecha_consulta'], '%Y-%m-%d %H:%M:%S')
    except ValueError:
        fecha_obj = datetime.now()
    fecha_consulta = fecha_obj.strftime('%d/%m/%Y')

    # --- HOJA 1: INFORME MÉDICO ---
    _insertar_encabezado(Story, styles, medico, paciente, "Informe Médico de Cardiología", fecha_consulta)
    
    # Signos Vitales
    Story.append(Paragraph("Evaluación Inicial (Triaje)", estilo_subtitulo))
    vitals_data = [
        ["FC", "TA Sistólica", "TA Diastólica", "SatO2"],
        [f"{consulta['fc']} lpm", f"{consulta['ta_sistolica']} mmHg", f"{consulta['ta_diastolica']} mmHg", f"{consulta['sato2']}%"]
    ]
    t_v = Table(vitals_data, colWidths=[100, 100, 100, 100])
    t_v.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.grey), ('BACKGROUND', (0,0), (-1,0), colors.whitesmoke), ('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    Story.append(t_v)
    Story.append(Spacer(1, 15))

    # Evolución e Historia
    Story.append(Paragraph("Resumen Clínico y Evolución", estilo_subtitulo))
    Story.append(Paragraph(f"<b>Motivo de Consulta:</b> {consulta['motivo_consulta']}", estilo_normal))
    Story.append(Paragraph(f"<b>Antecedentes/Evolución:</b> {consulta['observaciones']}", estilo_normal))
    Story.append(Spacer(1, 10))

    # Examen Físico
    Story.append(Paragraph("Examen Físico", estilo_subtitulo))
    ef_data = [
        [Paragraph("<b>Aspecto General:</b>", estilo_normal), Paragraph(consulta.get('ef_general', 'N/A'), estilo_normal)],
        [Paragraph("<b>Cardiovascular:</b>", estilo_normal), Paragraph(consulta.get('ef_cardio', 'N/A'), estilo_normal)],
        [Paragraph("<b>Respiratorio:</b>", estilo_normal), Paragraph(consulta.get('ef_respiratorio', 'N/A'), estilo_normal)],
        [Paragraph("<b>Otros:</b>", estilo_normal), Paragraph(consulta.get('ef_otros', 'N/A'), estilo_normal)]
    ]
    t_ef = Table(ef_data, colWidths=[120, 330])
    t_ef.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('BOTTOMPADDING', (0,0), (-1,-1), 4)]))
    Story.append(t_ef)
    Story.append(Spacer(1, 10))

    # Estudios en Consultorio
    Story.append(Paragraph("Estudios en Consultorio", estilo_subtitulo))
    Story.append(Paragraph(f"<b>Hallazgos ECG:</b> {consulta.get('ecg_hallazgos', 'No realizado')}", estilo_normal))
    Story.append(Paragraph(f"<b>Hallazgos Ecosonograma:</b> {consulta.get('echo_hallazgos', 'No realizado')}", estilo_normal))
    
    if hce_tipo == 'infantil':
        Story.append(Spacer(1, 10))
        Story.append(Paragraph(f"<b>Z-Scores Pediátricos:</b> Ao: {hce_detalle['zscore_aortico']}, Pul: {hce_detalle['zscore_pulmonar']}, Mit: {hce_detalle['zscore_mitral']}", estilo_normal))

    Story.append(Spacer(1, 15))
    # Diagnóstico Final
    Story.append(Paragraph("Diagnóstico Clínico", estilo_subtitulo))
    Story.append(Paragraph(f"{consulta.get('diagnostico', 'No especificado')}", estilo_normal))
    Story.append(Spacer(1, 10))

    _insertar_firma(Story, styles, medico)

    # --- HOJA 2: RÉCIPE E INDICACIONES ---
    Story.append(PageBreak())
    _insertar_encabezado(Story, styles, medico, paciente, "Récipe Médico e Indicaciones", fecha_consulta)
    
    # RÉCIPE MÉDICO (Farmacia) e INDICACIONES (Paciente)
    if recetas:
        # 1. RÉCIPE (Medicamentos y Dosis)
        Story.append(Paragraph("RÉCIPE MÉDICO (Uso Farmacia)", estilo_subtitulo))
        Story.append(Spacer(1, 5))
        for rx in recetas:
            Story.append(Paragraph(f"• <b>{rx['medicamento']}</b> - {rx['dosis']}", estilo_normal))
        
        Story.append(Spacer(1, 20))
        
        # 2. INDICACIONES (Uso Paciente)
        Story.append(Paragraph("INDICACIONES DE TRATAMIENTO", estilo_subtitulo))
        Story.append(Spacer(1, 5))
        for rx in recetas:
            txt_ind = f"• <b>{rx['medicamento']}</b>: {rx['frecuencia']} por {rx['duracion']}"
            Story.append(Paragraph(txt_ind, estilo_normal))
            if rx['indicaciones_adicionales']:
                Story.append(Paragraph(f"&nbsp;&nbsp;&nbsp;<i>Nota: {rx['indicaciones_adicionales']}</i>", estilo_normal))
            Story.append(Spacer(1, 6))
    else:
        Story.append(Paragraph("No se prescribieron medicamentos en esta consulta.", estilo_normal))

    
    # Exámenes Externos
    if indicaciones:
        Story.append(Spacer(1, 20))
        Story.append(Paragraph("Órdenes para Estudios Externos", estilo_subtitulo))
        for ind in indicaciones:
            Story.append(Paragraph(f"• <b>{ind['tipo_examen']}</b>: {ind['indicacion']}", estilo_normal))
            Story.append(Spacer(1, 6))

    _insertar_firma(Story, styles, medico)

    doc.build(Story)
    buffer.seek(0)
    return buffer

def calcular_edad(fecha_nacimiento_str: str) -> int:
    """Helper simple para calcular edad en reporte."""
    try:
        fecha_nac = datetime.strptime(fecha_nacimiento_str, '%Y-%m-%d').date()
        hoy = date.today()
        return hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
    except:
        return 0

