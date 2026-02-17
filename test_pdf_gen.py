
import sys
import os
# Add current directory to path so imports work
sys.path.append(os.getcwd())

from modules.reportes import generar_pdf_consulta
from datetime import datetime

# Dummy data
paciente = {
    'id': 1,
    'nombre': 'Test Patient',
    'fecha_nacimiento': '1980-01-01',
    'contacto': '555-1234'
}
medico = {
    'nombre': 'Dr. Test',
    'especialidad': 'Cardiology',
    'email': 'test@test.com'
}
consulta = {
    'fecha_consulta': '2023-10-27 10:00:00',
    'motivo_consulta': 'Routine Checkup',
    'fc': 80,
    'ta_sistolica': 120,
    'ta_diastolica': 80,
    'sato2': 98,
    'observaciones': 'None'
}
hce_detalle = {'clasificacion_riesgo': 'Low'}
hce_tipo = 'adulto'
indicaciones = [{'tipo_examen': 'ECG', 'indicacion': 'Routine'}]
recetas = [{'medicamento': 'Aspirin', 'dosis': '100mg', 'frecuencia': 'Daily', 'duracion': 'Forever', 'indicaciones_adicionales': ''}]

try:
    pdf_buffer = generar_pdf_consulta(paciente, medico, consulta, hce_detalle, hce_tipo, indicaciones, recetas)
    print("PDF Generated Successfully")
    # Optional: write to file to check
    with open("test_output.pdf", "wb") as f:
        f.write(pdf_buffer.getbuffer())
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
