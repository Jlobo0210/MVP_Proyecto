import pyodbc
from config import Config
from contextlib import contextmanager

# --- FUNCIONES HELPER PARA CONEXIÓN ---

def get_connection():
    """Obtiene una conexión a la base de datos"""
    try:
        conn = pyodbc.connect(Config.DB_CONNECTION_STRING)
        return conn
    except pyodbc.Error as e:
        print(f"Error conectando a la base de datos: {e}")
        raise


@contextmanager
def get_db_cursor(commit=False):
    """
    Context manager para manejar conexiones y cursores automáticamente
    
    Uso:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM Usuarios")
            results = cursor.fetchall()
    
    Para INSERT/UPDATE/DELETE usar commit=True:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("INSERT INTO ...")
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        if commit:
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


# --- FUNCIONES DE USUARIOS ---

def crear_usuario(email, password_hash, nombre, apellido, telefono, rol_id):
    """Crea un nuevo usuario en la base de datos"""
    query = """
        INSERT INTO Usuarios (email, password_hash, nombre, apellido, telefono, rol_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(query, (email, password_hash, nombre, apellido, telefono, rol_id))
        # Obtener el ID del usuario recién creado
        cursor.execute("SELECT @@IDENTITY AS id")
        user_id = cursor.fetchone()[0]
        return user_id


def obtener_usuario_por_email(email):
    """Obtiene un usuario por su email"""
    query = """
        SELECT u.id, u.email, u.password_hash, u.nombre, u.apellido, 
               u.telefono, u.foto_perfil, u.rol_id, u.activo, 
               u.fecha_registro, u.ultimo_acceso, r.nombre as rol_nombre
        FROM Usuarios u
        INNER JOIN Roles r ON u.rol_id = r.id
        WHERE u.email = ?
    """
    with get_db_cursor() as cursor:
        cursor.execute(query, (email,))
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'email': row[1],
                'password_hash': row[2],
                'nombre': row[3],
                'apellido': row[4],
                'telefono': row[5],
                'foto_perfil': row[6],
                'rol_id': row[7],
                'activo': row[8],
                'fecha_registro': row[9],
                'ultimo_acceso': row[10],
                'rol_nombre': row[11]
            }
        return None


def obtener_usuario_por_id(user_id):
    """Obtiene un usuario por su ID"""
    query = """
        SELECT u.id, u.email, u.password_hash, u.nombre, u.apellido, 
               u.telefono, u.foto_perfil, u.rol_id, u.activo, 
               u.fecha_registro, u.ultimo_acceso, r.nombre as rol_nombre
        FROM Usuarios u
        INNER JOIN Roles r ON u.rol_id = r.id
        WHERE u.id = ?
    """
    with get_db_cursor() as cursor:
        cursor.execute(query, (user_id,))
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'email': row[1],
                'password_hash': row[2],
                'nombre': row[3],
                'apellido': row[4],
                'telefono': row[5],
                'foto_perfil': row[6],
                'rol_id': row[7],
                'activo': row[8],
                'fecha_registro': row[9],
                'ultimo_acceso': row[10],
                'rol_nombre': row[11]
            }
        return None


def actualizar_ultimo_acceso(user_id):
    """Actualiza la fecha de último acceso del usuario"""
    query = "UPDATE Usuarios SET ultimo_acceso = GETDATE() WHERE id = ?"
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(query, (user_id,))


# --- FUNCIONES DE ROLES ---

def obtener_rol_por_nombre(nombre_rol):
    """Obtiene un rol por su nombre"""
    query = "SELECT id, nombre, descripcion FROM Roles WHERE nombre = ?"
    with get_db_cursor() as cursor:
        cursor.execute(query, (nombre_rol,))
        row = cursor.fetchone()
        if row:
            return {'id': row[0], 'nombre': row[1], 'descripcion': row[2]}
        return None


# --- FUNCIONES DE BARBERÍAS ---

def obtener_barberias_activas():
    """Obtiene todas las barberías activas"""
    query = """
        SELECT b.id, b.nombre, b.direccion, b.ciudad, b.telefono, 
               b.email, b.logo, b.descripcion, b.hora_apertura, b.hora_cierre,
               u.nombre + ' ' + u.apellido as propietario
        FROM Barberias b
        INNER JOIN Usuarios u ON b.propietario_id = u.id
        WHERE b.activo = 1
        ORDER BY b.nombre
    """
    with get_db_cursor() as cursor:
        cursor.execute(query)
        rows = cursor.fetchall()
        barberias = []
        for row in rows:
            barberias.append({
                'id': row[0],
                'nombre': row[1],
                'direccion': row[2],
                'ciudad': row[3],
                'telefono': row[4],
                'email': row[5],
                'logo': row[6],
                'descripcion': row[7],
                'hora_apertura': row[8],
                'hora_cierre': row[9],
                'propietario': row[10]
            })
        return barberias


def obtener_barberia_por_id(barberia_id):
    """Obtiene una barbería por su ID"""
    query = """
        SELECT b.id, b.nombre, b.direccion, b.ciudad, b.telefono, 
               b.email, b.logo, b.descripcion, b.hora_apertura, b.hora_cierre,
               b.propietario_id
        FROM Barberias b
        WHERE b.id = ? AND b.activo = 1
    """
    with get_db_cursor() as cursor:
        cursor.execute(query, (barberia_id,))
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'nombre': row[1],
                'direccion': row[2],
                'ciudad': row[3],
                'telefono': row[4],
                'email': row[5],
                'logo': row[6],
                'descripcion': row[7],
                'hora_apertura': row[8],
                'hora_cierre': row[9],
                'propietario_id': row[10]
            }
        return None


# --- FUNCIONES DE SERVICIOS ---

def obtener_servicios_por_barberia(barberia_id):
    """Obtiene todos los servicios activos de una barbería"""
    query = """
        SELECT s.id, s.nombre, s.descripcion, s.precio, s.duracion_minutos,
               s.imagen, c.nombre as categoria, c.icono
        FROM Servicios s
        INNER JOIN Categorias_Servicios c ON s.categoria_id = c.id
        WHERE s.barberia_id = ? AND s.activo = 1
        ORDER BY c.orden, s.nombre
    """
    with get_db_cursor() as cursor:
        cursor.execute(query, (barberia_id,))
        rows = cursor.fetchall()
        servicios = []
        for row in rows:
            servicios.append({
                'id': row[0],
                'nombre': row[1],
                'descripcion': row[2],
                'precio': float(row[3]),
                'duracion_minutos': row[4],
                'imagen': row[5],
                'categoria': row[6],
                'icono': row[7]
            })
        return servicios


def obtener_servicio_por_id(servicio_id):
    """Obtiene un servicio por su ID"""
    query = """
        SELECT s.id, s.barberia_id, s.nombre, s.descripcion, s.precio, 
               s.duracion_minutos, s.imagen
        FROM Servicios s
        WHERE s.id = ? AND s.activo = 1
    """
    with get_db_cursor() as cursor:
        cursor.execute(query, (servicio_id,))
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'barberia_id': row[1],
                'nombre': row[2],
                'descripcion': row[3],
                'precio': float(row[4]),
                'duracion_minutos': row[5],
                'imagen': row[6]
            }
        return None


# --- FUNCIONES DE BARBEROS ---

def obtener_barberos_por_barberia(barberia_id):
    """Obtiene todos los barberos activos de una barbería"""
    query = """
        SELECT b.id, u.nombre, u.apellido, u.foto_perfil,
               b.especialidad, b.años_experiencia, b.calificacion_promedio,
               b.total_servicios
        FROM Barberos b
        INNER JOIN Usuarios u ON b.usuario_id = u.id
        WHERE b.barberia_id = ? AND b.activo = 1
        ORDER BY b.calificacion_promedio DESC
    """
    with get_db_cursor() as cursor:
        cursor.execute(query, (barberia_id,))
        rows = cursor.fetchall()
        barberos = []
        for row in rows:
            barberos.append({
                'id': row[0],
                'nombre': row[1],
                'apellido': row[2],
                'foto_perfil': row[3],
                'especialidad': row[4],
                'años_experiencia': row[5],
                'calificacion_promedio': float(row[6]) if row[6] else 0,
                'total_servicios': row[7]
            })
        return barberos


# --- FUNCIONES DE CITAS ---

def crear_cita(cliente_id, barbero_id, servicio_id, fecha, hora_inicio, hora_fin, precio_final, notas_cliente=None):
    """Crea una nueva cita"""
    query = """
        INSERT INTO Citas (cliente_id, barbero_id, servicio_id, fecha, 
                          hora_inicio, hora_fin, estado_id, precio_final, notas_cliente)
        VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
    """
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(query, (cliente_id, barbero_id, servicio_id, fecha, 
                              hora_inicio, hora_fin, precio_final, notas_cliente))
        cursor.execute("SELECT @@IDENTITY AS id")
        cita_id = cursor.fetchone()[0]
        return cita_id


def obtener_citas_por_cliente(cliente_id):
    """Obtiene todas las citas de un cliente"""
    query = """
        SELECT c.id, c.fecha, c.hora_inicio, c.hora_fin,
               s.nombre as servicio, s.precio,
               u.nombre + ' ' + u.apellido as barbero,
               bar.nombre as barberia,
               e.nombre as estado, e.color as estado_color
        FROM Citas c
        INNER JOIN Servicios s ON c.servicio_id = s.id
        INNER JOIN Barberos b ON c.barbero_id = b.id
        INNER JOIN Usuarios u ON b.usuario_id = u.id
        INNER JOIN Barberias bar ON s.barberia_id = bar.id
        INNER JOIN Estados_Citas e ON c.estado_id = e.id
        WHERE c.cliente_id = ?
        ORDER BY c.fecha DESC, c.hora_inicio DESC
    """
    with get_db_cursor() as cursor:
        cursor.execute(query, (cliente_id,))
        rows = cursor.fetchall()
        citas = []
        for row in rows:
            citas.append({
                'id': row[0],
                'fecha': row[1],
                'hora_inicio': row[2],
                'hora_fin': row[3],
                'servicio': row[4],
                'precio': float(row[5]),
                'barbero': row[6],
                'barberia': row[7],
                'estado': row[8],
                'estado_color': row[9]
            })
        return citas


def obtener_slots_disponibles(barbero_id, fecha):
    """Obtiene los horarios disponibles de un barbero en una fecha específica"""
    # Primero obtenemos el horario del barbero para ese día
    dia_semana_query = "SELECT DATEPART(WEEKDAY, ?)"
    
    with get_db_cursor() as cursor:
        cursor.execute(dia_semana_query, (fecha,))
        dia_semana = cursor.fetchone()[0]
        
        # Obtener horario del barbero
        horario_query = """
            SELECT hora_inicio, hora_fin
            FROM Horarios_Barberos
            WHERE barbero_id = ? AND dia_semana = ? AND activo = 1
        """
        cursor.execute(horario_query, (barbero_id, dia_semana))
        horario = cursor.fetchone()
        
        if not horario:
            return []
        
        # Obtener citas ya reservadas
        citas_query = """
            SELECT hora_inicio, hora_fin
            FROM Citas
            WHERE barbero_id = ? AND fecha = ? AND estado_id IN (1, 2)
            ORDER BY hora_inicio
        """
        cursor.execute(citas_query, (barbero_id, fecha))
        citas_ocupadas = cursor.fetchall()
        
        return {
            'horario_inicio': horario[0],
            'horario_fin': horario[1],
            'citas_ocupadas': [(cita[0], cita[1]) for cita in citas_ocupadas]
        }


# --- FUNCIONES DE ESTADÍSTICAS ---

def obtener_estadisticas_barbero(barbero_id):
    """Obtiene estadísticas de un barbero"""
    query = """
        SELECT 
            COUNT(*) as total_citas,
            SUM(CASE WHEN estado_id = 3 THEN 1 ELSE 0 END) as completadas,
            AVG(CASE WHEN estado_id = 3 THEN precio_final ELSE NULL END) as ingreso_promedio
        FROM Citas
        WHERE barbero_id = ?
    """
    with get_db_cursor() as cursor:
        cursor.execute(query, (barbero_id,))
        row = cursor.fetchone()
        if row:
            return {
                'total_citas': row[0],
                'completadas': row[1],
                'ingreso_promedio': float(row[2]) if row[2] else 0
            }
        return None