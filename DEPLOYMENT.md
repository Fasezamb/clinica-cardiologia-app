# 🚀 Guía de Despliegue - CardioCloud

## Acceso a la Aplicación

**URL de la aplicación:** [Se proporcionará después del despliegue]

**Credenciales de acceso:**
- Usuario: `admin`
- Contraseña: `admin123`

## Instrucciones para la Dra. Olivia

### Cómo Acceder
1. Abrir el navegador web (Chrome, Firefox, Safari, Edge)
2. Ir al URL proporcionado
3. Iniciar sesión con las credenciales arriba mencionadas

### Funcionalidades Disponibles

#### 📊 Dashboard
- Vista general de estadísticas de la clínica
- Métricas de pacientes y citas

#### 📅 Agenda (Citas)
- Programar nuevas citas
- Ver citas del día
- Gestionar estados de citas (Completada, No-show, Cancelada)

#### 🩺 Consulta Médica (HCE)
- Crear historias clínicas electrónicas
- Formularios diferenciados para pacientes pediátricos y adultos
- Generar reportes médicos en PDF

#### 🔍 Buscador Historial
- Buscar pacientes por nombre o ID
- Ver historial completo de consultas

#### ⚙️ Gestión de Médicos (Solo Admin)
- Agregar nuevos médicos al sistema
- Ver lista de médicos registrados

### Cómo Probar la Aplicación

1. **Crear un Paciente de Prueba**
   - Ir a "Consulta Médica (HCE)"
   - Seleccionar "Registrar Nuevo Paciente"
   - Llenar el formulario con datos de prueba

2. **Programar una Cita**
   - Ir a "Agenda (Citas)"
   - Seleccionar paciente, médico, fecha y hora
   - Guardar la cita

3. **Crear una Historia Clínica**
   - Ir a "Consulta Médica (HCE)"
   - Seleccionar el paciente
   - Llenar los datos de la consulta
   - Generar reporte PDF

4. **Buscar Historial**
   - Ir a "Buscador Historial"
   - Buscar el paciente creado
   - Ver el historial completo

## ⚠️ Limitaciones Importantes

### Datos Temporales
- **La base de datos se reinicia** cuando la aplicación se reinicia (por inactividad o actualización)
- Los datos ingresados **NO son permanentes**
- Para uso en producción, se requiere migración a base de datos externa (PostgreSQL)

### Archivos PDF
- Los reportes generados se almacenan temporalmente
- Se perderán al reiniciar la aplicación
- Para producción, se requiere almacenamiento persistente (AWS S3, Google Cloud Storage, etc.)

### Inactividad
- La aplicación se "duerme" después de ~15 minutos de inactividad
- Al acceder nuevamente, tomará ~30 segundos en "despertar"
- Esto es normal en Streamlit Community Cloud (plan gratuito)

## 💬 Cómo Dar Retroalimentación

Por favor, tomar nota de:

### Funcionalidad
- ✅ ¿Qué funciona bien?
- ❌ ¿Qué no funciona como esperado?
- 💡 ¿Qué funcionalidades faltan?

### Usabilidad
- ¿Es intuitiva la navegación?
- ¿Los formularios son claros?
- ¿Hay algo confuso o difícil de usar?

### Diseño
- ¿La interfaz es profesional?
- ¿Los colores y diseño son apropiados para uso médico?
- ¿Hay elementos visuales que mejorar?

### Datos Médicos
- ¿Los campos de datos son suficientes?
- ¿Falta algún campo importante?
- ¿Los reportes PDF contienen la información necesaria?

## 🔧 Soporte Técnico

Si encuentra algún problema:
1. Tomar captura de pantalla del error
2. Anotar qué estaba haciendo cuando ocurrió
3. Enviar la información al desarrollador

## 📋 Próximos Pasos (Post-Revisión)

Después de la revisión de la Dra. Olivia:
1. Implementar retroalimentación y mejoras
2. Migrar a base de datos PostgreSQL para persistencia
3. Configurar almacenamiento de archivos en la nube
4. Implementar autenticación más robusta
5. Agregar más funcionalidades según necesidades
6. Considerar cumplimiento con regulaciones de datos médicos (HIPAA, GDPR, etc.)
