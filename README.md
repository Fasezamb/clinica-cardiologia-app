# 🏥 Sistema de Gestión Clínica - Cardiología

Sistema web desarrollado en Python con Streamlit para la gestión integral de una clínica de cardiología con 4 especialistas (adulto e infantil).

## 🌟 Características Principales

### Gestión de Pacientes
- ✅ Registro diferenciado de pacientes pediátricos y adultos
- ✅ Búsqueda y edición de información de pacientes
- ✅ Triaje con registro de constantes vitales
- ✅ Validación automática de signos vitales

### Sistema de Citas
- ✅ Agenda personalizada para cada uno de los 4 médicos
- ✅ Gestión de estados: Pendiente → Llegó → En Consulta → Completada
- ✅ Tracking de No-shows con estadísticas
- ✅ Visualización por calendario

### Historia Clínica Electrónica (HCE)

#### Módulo Pediátrico
- ✅ Cálculo automático de percentiles de peso y talla (OMS)
- ✅ Z-Scores valvulares (aórtico, pulmonar, mitral, tricúspide)
- ✅ Superficie corporal (fórmula Haycock)
- ✅ Estado del Ductus Arterioso
- ✅ Alertas automáticas para valores anormales

#### Módulo Adulto
- ✅ Registro de antecedentes (HTA, Diabetes, Tabaquismo)
- ✅ Perfil lipídico
- ✅ Cálculo de riesgo cardiovascular (SCORE y Framingham)
- ✅ Clasificación automática de riesgo (Bajo, Moderado, Alto, Muy Alto)
- ✅ Visualización con gauge charts

### Dashboard y Reportes
- ✅ Dashboard personalizado por médico
- ✅ Métricas de rendimiento (tasa de asistencia, No-shows)
- ✅ Gráficos interactivos con Plotly
- ✅ Estadísticas generales del sistema

### Seguridad
- ✅ Sistema de autenticación con bcrypt
- ✅ Roles diferenciados (admin, médico, recepción)
- ✅ Gestión de sesiones
- ✅ Base de datos protegida (.gitignore)

## 📋 Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/clinica-cardiologia-app.git
cd clinica-cardiologia-app
```

### 2. Crear entorno virtual (recomendado)

```bash
python -m venv venv

# En macOS/Linux:
source venv/bin/activate

# En Windows:
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

## 💻 Uso

### Iniciar la aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en tu navegador en `http://localhost:8501`

### Credenciales por defecto

**Administrador:**
- Usuario: `admin`
- Contraseña: `admin123`

**Recepción:**
- Usuario: `recepcion`
- Contraseña: `recepcion123`

**Médicos:**
- Usuario: `medico1`, `medico2`, `medico3`, `medico4`
- Contraseña: `medico123`

> ⚠️ **IMPORTANTE:** Cambia estas contraseñas antes de usar en producción.

## 📁 Estructura del Proyecto

```
clinica-cardiologia-app/
├── app.py                      # Aplicación principal
├── database.py                 # Gestión de base de datos
├── requirements.txt            # Dependencias
├── .gitignore                 # Archivos ignorados por git
├── .streamlit/
│   └── config.toml            # Configuración de Streamlit
├── modules/
│   ├── __init__.py
│   ├── admision.py            # Módulo de admisión de pacientes
│   ├── agenda.py              # Módulo de gestión de citas
│   ├── hce.py                 # Módulo de historia clínica
│   └── dashboard.py           # Módulo de dashboard
└── tests/
    ├── test_database.py       # Tests de base de datos
    └── test_calculations.py   # Tests de cálculos médicos
```

## 🗄️ Base de Datos

El sistema utiliza SQLite con las siguientes tablas:

- **pacientes**: Información de pacientes (pediátricos y adultos)
- **medicos**: Datos de los 4 especialistas
- **citas**: Agenda de citas con estados
- **hce_comun**: Historia clínica común (constantes vitales)
- **hce_infantil**: Datos específicos pediátricos
- **hce_adulto**: Datos específicos de adultos
- **usuarios**: Autenticación y roles

La base de datos se inicializa automáticamente al arrancar la aplicación.

## 🧪 Testing

```bash
# Instalar pytest
pip install pytest

# Ejecutar todos los tests
pytest tests/ -v

# Ejecutar tests específicos
pytest tests/test_database.py -v
pytest tests/test_calculations.py -v
```

## 🌐 Despliegue en Streamlit Cloud

### 1. Preparar el repositorio

Asegúrate de que tu código esté en un repositorio de GitHub (puede ser privado).

### 2. Configurar Streamlit Cloud

1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Conecta tu cuenta de GitHub
3. Selecciona el repositorio
4. Configura:
   - **Main file path**: `app.py`
   - **Python version**: 3.11

### 3. Deploy

Haz clic en "Deploy" y espera a que la aplicación esté lista.

> 📝 **Nota:** La base de datos SQLite se creará automáticamente en el servidor de Streamlit Cloud.

## ⚕️ Notas Médicas Importantes

> ⚠️ **ADVERTENCIA:** Los cálculos médicos implementados (Z-scores, percentiles, riesgo cardiovascular) utilizan fórmulas simplificadas para demostración. 

**Antes de usar en producción:**

1. **Z-Scores Valvulares**: Validar con tablas de referencia específicas por edad, sexo y superficie corporal
2. **Percentiles OMS**: Implementar tablas completas de la OMS por edad y sexo
3. **Riesgo Cardiovascular**: Usar las fórmulas completas de SCORE y Framingham con todos los factores
4. **Validación Médica**: Todos los cálculos deben ser revisados y aprobados por cardiólogos

## 🔒 Seguridad en Producción

Para uso con datos reales de pacientes:

- [ ] Implementar HTTPS
- [ ] Cifrar datos sensibles en la base de datos
- [ ] Configurar backups automáticos
- [ ] Implementar logs de auditoría
- [ ] Cumplir con normativas (HIPAA, GDPR, etc.)
- [ ] Cambiar todas las contraseñas por defecto
- [ ] Implementar autenticación de dos factores (2FA)

## 🛠️ Tecnologías Utilizadas

- **Framework**: Streamlit 1.31.0
- **Base de Datos**: SQLite3
- **Visualización**: Plotly 5.18.0
- **Seguridad**: bcrypt 4.1.2
- **Reportes**: ReportLab 4.0.9
- **Análisis**: Pandas 2.2.0

## 📞 Soporte

Para reportar problemas o sugerencias, por favor abre un issue en el repositorio de GitHub.

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

---

**Desarrollado para la gestión eficiente de clínicas de cardiología** ❤️
