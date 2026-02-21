import sqlite3
import pandas as pd
from datetime import datetime, date

DB_NAME = 'clinica_cardiologia.db'

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Usuarios (Auth)
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE, 
                        password TEXT, 
                        rol TEXT)''')
                        
    # 2. Medicos
    cursor.execute('''CREATE TABLE IF NOT EXISTS medicos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT, 
                        especialidad TEXT, 
                        email TEXT, 
                        user_id INTEGER,
                        FOREIGN KEY(user_id) REFERENCES usuarios(id))''')
                        
    # 3. Pacientes
    cursor.execute('''CREATE TABLE IF NOT EXISTS pacientes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT,
                        fecha_nacimiento TEXT,
                        sexo TEXT,
                        es_pediatrico BOOLEAN,
                        contacto TEXT,
                        tutor_legal TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    # 4. Citas
    cursor.execute('''CREATE TABLE IF NOT EXISTS citas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        paciente_id INTEGER,
                        medico_id INTEGER,
                        fecha_hora TEXT,
                        estado TEXT DEFAULT 'Pendiente',
                        FOREIGN KEY(paciente_id) REFERENCES pacientes(id),
                        FOREIGN KEY(medico_id) REFERENCES medicos(id))''')

    # 5. HCE Comun (Triaje y Consulta General)
    cursor.execute('''CREATE TABLE IF NOT EXISTS hce_comun (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        paciente_id INTEGER,
                        medico_id INTEGER,
                        cita_id INTEGER,
                        fecha_consulta TEXT,
                        motivo_consulta TEXT,
                        diagnostico TEXT,
                        fc INTEGER,
                        ta_sistolica INTEGER,
                        ta_diastolica INTEGER,
                        sato2 REAL,
                        ef_general TEXT,
                        ef_cardio TEXT,
                        ef_respiratorio TEXT,
                        ef_otros TEXT,
                        ecg_hallazgos TEXT,
                        echo_hallazgos TEXT,
                        observaciones TEXT,
                        FOREIGN KEY(paciente_id) REFERENCES pacientes(id),
                        FOREIGN KEY(medico_id) REFERENCES medicos(id))''')
    
    # Asegurar que las columnas nuevas existan si la DB ya estaba creada
    columnas_nuevas = [
        ("diagnostico", "TEXT"),
        ("ef_general", "TEXT"),
        ("ef_cardio", "TEXT"),
        ("ef_respiratorio", "TEXT"),
        ("ef_otros", "TEXT"),
        ("ecg_hallazgos", "TEXT"),
        ("echo_hallazgos", "TEXT")
    ]
    for col_name, col_type in columnas_nuevas:
        try:
            cursor.execute(f"ALTER TABLE hce_comun ADD COLUMN {col_name} {col_type}")
        except:
            pass # Ya existe


    # 6. HCE Infantil
    cursor.execute('''CREATE TABLE IF NOT EXISTS hce_infantil (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        hce_comun_id INTEGER,
                        peso_kg REAL,
                        talla_cm REAL,
                        percentil_peso REAL,
                        percentil_talla REAL,
                        zscore_aortico REAL,
                        zscore_pulmonar REAL,
                        zscore_mitral REAL,
                        zscore_tricuspide REAL,
                        ductus_estado TEXT,
                        ductus_tamano_mm REAL,
                        FOREIGN KEY(hce_comun_id) REFERENCES hce_comun(id))''')

    # 7. HCE Adulto
    cursor.execute('''CREATE TABLE IF NOT EXISTS hce_adulto (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        hce_comun_id INTEGER,
                        tiene_hta BOOLEAN,
                        tiene_diabetes BOOLEAN,
                        tabaquismo TEXT,
                        colesterol_total REAL,
                        colesterol_hdl REAL,
                        riesgo_cardiovascular_score REAL,
                        riesgo_cardiovascular_framingham REAL,
                        clasificacion_riesgo TEXT,
                        FOREIGN KEY(hce_comun_id) REFERENCES hce_comun(id))''')

    # 8. Indicaciones de Examenes
    cursor.execute('''CREATE TABLE IF NOT EXISTS indicaciones_examenes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        hce_id INTEGER,
                        tipo_examen TEXT,
                        indicacion TEXT,
                        FOREIGN KEY(hce_id) REFERENCES hce_comun(id))''')

    # 9. Recetas Medicas
    cursor.execute('''CREATE TABLE IF NOT EXISTS recetas_medicas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        hce_id INTEGER,
                        medicamento TEXT,
                        dosis TEXT,
                        frecuencia TEXT,
                        duracion TEXT,
                        indicaciones_adicionales TEXT,
                        FOREIGN KEY(hce_id) REFERENCES hce_comun(id))''')

    # Default Admin
    cursor.execute("SELECT * FROM usuarios WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO usuarios (username, password, rol) VALUES (?, ?, ?)",
                       ('admin', 'admin123', 'admin'))
    
    conn.commit()
    conn.close()

# --- AUTH & USERS ---

def verify_login(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT u.id, u.username, u.rol, m.id FROM usuarios u LEFT JOIN medicos m ON u.id = m.user_id WHERE u.username=? AND u.password=?", 
                   (username, password))
    row = cursor.fetchone()
    conn.close()
    if row:
        # row: id, username, rol, medico_id
        return {'user_id': row[0], 'username': row[1], 'rol': row[2], 'medico_id': row[3]}
    return None

def create_medico_con_usuario(nombre, especialidad, email, username, password):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO usuarios (username, password, rol) VALUES (?, ?, ?)", 
                       (username, password, 'medico'))
        user_id = cursor.lastrowid
        cursor.execute("INSERT INTO medicos (nombre, especialidad, email, user_id) VALUES (?, ?, ?, ?)", 
                       (nombre, especialidad, email, user_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error creating medico: {e}")
        return False
    finally:
        conn.close()

def get_all_medicos():
    conn = get_connection()
    # Usamos pandas id possible but list of dicts is safer for portability
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, especialidad, email FROM medicos")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_medico(id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM medicos WHERE id=?", (id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

# --- PACIENTES ---

def create_paciente(nombre, fecha_nacimiento, es_pediatrico, contacto, tutor_legal):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO pacientes (nombre, fecha_nacimiento, es_pediatrico, contacto, tutor_legal)
                      VALUES (?, ?, ?, ?, ?)''', 
                   (nombre, fecha_nacimiento, es_pediatrico, contacto, tutor_legal))
    id_paciente = cursor.lastrowid
    conn.commit()
    conn.close()
    return id_paciente

def get_all_pacientes():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pacientes ORDER BY nombre")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_paciente(id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pacientes WHERE id=?", (id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def search_pacientes(query):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # Buscar por nombre o ID
    sql = "SELECT * FROM pacientes WHERE nombre LIKE ? OR CAST(id AS TEXT) LIKE ?"
    param = f"%{query}%"
    cursor.execute(sql, (param, param))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# --- CITAS ---

def update_paciente_sexo(paciente_id, sexo):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE pacientes SET sexo = ? WHERE id = ?", (sexo, paciente_id))
    conn.commit()
    conn.close()

def update_paciente_registro(paciente_id, fecha_nacimiento, es_pediatrico, contacto, tutor_legal, sexo):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''UPDATE pacientes 
                      SET fecha_nacimiento = ?, es_pediatrico = ?, contacto = ?, tutor_legal = ?, sexo = ?
                      WHERE id = ?''', 
                   (fecha_nacimiento, es_pediatrico, contacto, tutor_legal, sexo, paciente_id))
    conn.commit()
    conn.close()

def create_cita(paciente_id, medico_id, fecha_hora):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO citas (paciente_id, medico_id, fecha_hora, estado) VALUES (?, ?, ?, 'Pendiente')",
                   (paciente_id, medico_id, fecha_hora))
    id_cita = cursor.lastrowid
    conn.commit()
    conn.close()
    return id_cita

def get_citas_by_medico_fecha(medico_id, fecha_str):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = '''SELECT c.id, c.fecha_hora, c.estado, c.paciente_id, p.nombre as paciente_nombre 
               FROM citas c 
               JOIN pacientes p ON c.paciente_id = p.id
               WHERE c.medico_id = ? AND date(c.fecha_hora) = ?
               ORDER BY c.fecha_hora'''
    
    cursor.execute(query, (medico_id, fecha_str))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_estado_cita(cita_id, nuevo_estado):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE citas SET estado = ? WHERE id = ?", (nuevo_estado, cita_id))
    conn.commit()
    conn.close()

def get_noshow_stats(medico_id, fecha_inicio, fecha_fin):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check date format to match sqlite (YYYY-MM-DD)
    # Incoming dates are likely strings or date objects. 
    # Calling code in agenda.py does .strftime('%Y-%m-%d'), so we get strings.
    
    base_query = "SELECT count(*), estado FROM citas WHERE date(fecha_hora) BETWEEN ? AND ?"
    params = [fecha_inicio, fecha_fin]
    
    if medico_id:
        base_query += " AND medico_id = ?"
        params.append(medico_id)
        
    base_query += " GROUP BY estado"
    
    cursor.execute(base_query, params)
    rows = cursor.fetchall()
    conn.close()
    
    stats = {
        'total_citas': 0,
        'total_completadas': 0,
        'total_noshows': 0,
        'tasa_asistencia': 0
    }
    
    for count, estado in rows:
        stats['total_citas'] += count
        if estado == 'Completada':
            stats['total_completadas'] = count
        elif estado == 'No-show':
            stats['total_noshows'] = count
            
    if stats['total_citas'] > 0:
        stats['tasa_asistencia'] = round(((stats['total_citas'] - stats['total_noshows']) / stats['total_citas']) * 100, 1)
        
    return stats

# --- HCE (HISTORIA CLINICA) ---

def create_hce_comun(paciente_id, medico_id, fecha_consulta, motivo_consulta, fc, ta_sistolica, ta_diastolica, sato2, observaciones, diagnostico=None, ef_general=None, ef_cardio=None, ef_respiratorio=None, ef_otros=None, ecg_hallazgos=None, echo_hallazgos=None, cita_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO hce_comun 
                      (paciente_id, medico_id, cita_id, fecha_consulta, motivo_consulta, diagnostico, fc, ta_sistolica, ta_diastolica, sato2, ef_general, ef_cardio, ef_respiratorio, ef_otros, ecg_hallazgos, echo_hallazgos, observaciones)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (paciente_id, medico_id, cita_id, fecha_consulta, motivo_consulta, diagnostico, fc, ta_sistolica, ta_diastolica, sato2, ef_general, ef_cardio, ef_respiratorio, ef_otros, ecg_hallazgos, echo_hallazgos, observaciones))
    hce_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return hce_id

def create_hce_infantil(hce_comun_id, peso_kg, talla_cm, percentil_peso, percentil_talla, zscore_aortico, zscore_pulmonar, zscore_mitral, zscore_tricuspide, ductus_estado, ductus_tamaño_mm):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO hce_infantil
                      (hce_comun_id, peso_kg, talla_cm, percentil_peso, percentil_talla, zscore_aortico, zscore_pulmonar, zscore_mitral, zscore_tricuspide, ductus_estado, ductus_tamano_mm)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (hce_comun_id, peso_kg, talla_cm, percentil_peso, percentil_talla, zscore_aortico, zscore_pulmonar, zscore_mitral, zscore_tricuspide, ductus_estado, ductus_tamaño_mm))
    conn.commit()
    conn.close()

def create_hce_adulto(hce_comun_id, tiene_hta, tiene_diabetes, tabaquismo, colesterol_total, colesterol_hdl, riesgo_cardiovascular_score, riesgo_cardiovascular_framingham, clasificacion_riesgo):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO hce_adulto
                      (hce_comun_id, tiene_hta, tiene_diabetes, tabaquismo, colesterol_total, colesterol_hdl, riesgo_cardiovascular_score, riesgo_cardiovascular_framingham, clasificacion_riesgo)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (hce_comun_id, tiene_hta, tiene_diabetes, tabaquismo, colesterol_total, colesterol_hdl, riesgo_cardiovascular_score, riesgo_cardiovascular_framingham, clasificacion_riesgo))
    conn.commit()
    conn.close()

def get_hce_by_paciente(paciente_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    query = '''SELECT h.*, m.nombre as medico_nombre 
               FROM hce_comun h
               LEFT JOIN medicos m ON h.medico_id = m.id
               WHERE h.paciente_id = ?
               ORDER BY h.fecha_consulta DESC'''
               
    cursor.execute(query, (paciente_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# --- INDICACIONES Y RECETAS ---

def create_indicacion_examen(hce_id, tipo_examen, indicacion):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO indicaciones_examenes (hce_id, tipo_examen, indicacion) VALUES (?, ?, ?)",
                   (hce_id, tipo_examen, indicacion))
    conn.commit()
    conn.close()

def get_indicaciones_by_hce(hce_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM indicaciones_examenes WHERE hce_id=?", (hce_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def create_receta(hce_id, medicamento, dosis, frecuencia, duracion, indicaciones_adicionales):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO recetas_medicas 
                      (hce_id, medicamento, dosis, frecuencia, duracion, indicaciones_adicionales)
                      VALUES (?, ?, ?, ?, ?, ?)''',
                   (hce_id, medicamento, dosis, frecuencia, duracion, indicaciones_adicionales))
    conn.commit()
    conn.close()

def get_recetas_by_hce(hce_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recetas_medicas WHERE hce_id=?", (hce_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
