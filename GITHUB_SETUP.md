# 🚀 Pasos para Crear el Repositorio en GitHub y Desplegar

## Paso 1: Crear Repositorio en GitHub

1. **Ir a GitHub**
   - Abrir navegador y ir a: https://github.com
   - Iniciar sesión con tu cuenta

2. **Crear Nuevo Repositorio**
   - Click en el botón **"+"** en la esquina superior derecha
   - Seleccionar **"New repository"**

3. **Configurar el Repositorio**
   - **Repository name:** `clinica-cardiologia-app`
   - **Description:** "Sistema de Gestión para Clínica de Cardiología - CardioCloud"
   - **Visibilidad:** 
     - ✅ **Private** (recomendado para datos médicos)
     - ⚠️ Public (solo si no hay datos sensibles)
   - **NO marcar** "Initialize this repository with a README" (ya tenemos archivos)
   - Click en **"Create repository"**

4. **Copiar el URL del Repositorio**
   - GitHub mostrará instrucciones
   - Copiar el URL que aparece (formato: `https://github.com/tu-usuario/clinica-cardiologia-app.git`)

## Paso 2: Conectar Repositorio Local con GitHub

Ejecutar estos comandos en la terminal (desde la carpeta del proyecto):

\`\`\`bash
# Configurar tu nombre y email (solo la primera vez)
git config --global user.name "Tu Nombre"
git config --global user.email "tu-email@ejemplo.com"

# Conectar con GitHub (reemplazar URL con el tuyo)
git remote add origin https://github.com/TU-USUARIO/clinica-cardiologia-app.git

# Subir el código a GitHub
git branch -M main
git push -u origin main
\`\`\`

## Paso 3: Desplegar en Streamlit Cloud

1. **Ir a Streamlit Cloud**
   - Abrir: https://share.streamlit.io
   - Click en **"Sign in"** o **"Get started"**

2. **Conectar con GitHub**
   - Autorizar a Streamlit Cloud para acceder a tus repositorios
   - Permitir acceso cuando GitHub lo solicite

3. **Crear Nueva App**
   - Click en **"New app"**
   - Seleccionar:
     - **Repository:** `clinica-cardiologia-app`
     - **Branch:** `main`
     - **Main file path:** `app.py`
   - **App URL:** Elegir un nombre único (ej: `cardiocloud-demo`)

4. **Configuración Avanzada (Opcional)**
   - Click en "Advanced settings"
   - **Python version:** 3.9 o superior
   - Dejar lo demás por defecto

5. **Deploy!**
   - Click en **"Deploy!"**
   - Esperar 2-5 minutos mientras se despliega

## Paso 4: Verificar el Despliegue

1. **Esperar a que termine**
   - Verás logs en tiempo real
   - Cuando termine dirá "Your app is live!"

2. **Probar la Aplicación**
   - Click en el URL de tu app
   - Debería abrir la pantalla de login
   - Iniciar sesión con: `admin` / `admin123`

3. **Verificar Funcionalidades**
   - ✅ Dashboard carga correctamente
   - ✅ Puedes crear pacientes
   - ✅ Puedes programar citas
   - ✅ Puedes crear consultas médicas
   - ✅ Los PDFs se generan correctamente

## Paso 5: Compartir con la Dra. Olivia

1. **Copiar el URL**
   - Formato: `https://cardiocloud-demo.streamlit.app`

2. **Enviar Información**
   - URL de la aplicación
   - Credenciales: `admin` / `admin123`
   - Adjuntar el archivo `DEPLOYMENT.md` con instrucciones

3. **Mensaje de Ejemplo**
   \`\`\`
   Hola Dra. Olivia,
   
   La aplicación CardioCloud está lista para su revisión.
   
   🔗 URL: https://cardiocloud-demo.streamlit.app
   👤 Usuario: admin
   🔑 Contraseña: admin123
   
   Adjunto encontrará instrucciones detalladas de uso.
   
   Por favor, tome nota de cualquier comentario o sugerencia.
   
   Saludos,
   [Tu nombre]
   \`\`\`

## ⚠️ Notas Importantes

- **Primera carga:** La app puede tardar ~30 segundos en cargar la primera vez
- **Inactividad:** Si no se usa por 15 minutos, se "duerme" y tarda ~30 segundos en despertar
- **Datos temporales:** Los datos se pierden al reiniciar la app (esto es normal para la demo)
- **Actualizaciones:** Cada vez que hagas `git push`, la app se redesplegará automáticamente

## 🔧 Solución de Problemas

### Error: "Module not found"
- Verificar que `requirements.txt` esté correcto
- Redeployar la app desde Streamlit Cloud

### Error: "Database locked"
- Normal en Streamlit Cloud
- Refrescar la página

### La app no carga
- Verificar logs en Streamlit Cloud
- Buscar errores en rojo
- Contactar soporte si persiste

## 📞 Soporte

Si tienes problemas:
1. Revisar logs en Streamlit Cloud (botón "Manage app" → "Logs")
2. Verificar que todos los archivos estén en GitHub
3. Consultar documentación: https://docs.streamlit.io/streamlit-community-cloud
