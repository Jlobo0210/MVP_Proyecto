import pyodbc
from config import Config
from werkzeug.security import generate_password_hash
from datetime import time

def get_connection():
    return pyodbc.connect(Config.DB_CONNECTION_STRING)

def seed_database():
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        print("🌱 Iniciando seed de datos...")
        
        # === 1. VERIFICAR SI YA HAY DATOS ===
        cursor.execute("SELECT COUNT(*) FROM Usuarios")
        if cursor.fetchone()[0] > 0:
            print("⚠️  Ya hay datos en la base de datos.")
            respuesta = input("¿Deseas borrar todo y empezar de nuevo? (s/n): ")
            if respuesta.lower() != 's':
                print("❌ Operación cancelada.")
                return
            
            # Borrar datos existentes (en orden por foreign keys)
            print("🗑️  Borrando datos existentes...")
            cursor.execute("DELETE FROM Notificaciones")
            cursor.execute("DELETE FROM Pagos")
            cursor.execute("DELETE FROM Resenas")
            cursor.execute("DELETE FROM Citas")
            cursor.execute("DELETE FROM Horarios_Barberos")
            cursor.execute("DELETE FROM Servicios")
            cursor.execute("DELETE FROM Barberos")
            cursor.execute("DELETE FROM Barberias")
            cursor.execute("DELETE FROM Usuarios")
            conn.commit()
            print("✓ Datos borrados")
        
        # === 2. OBTENER IDs DE ROLES Y CATEGORÍAS (ya insertados por el schema) ===
        cursor.execute("SELECT id FROM Roles WHERE nombre = 'Admin'")
        admin_rol_id = cursor.fetchone()[0]
        
        cursor.execute("SELECT id FROM Roles WHERE nombre = 'Propietario'")
        propietario_rol_id = cursor.fetchone()[0]
        
        cursor.execute("SELECT id FROM Roles WHERE nombre = 'Barbero'")
        barbero_rol_id = cursor.fetchone()[0]
        
        cursor.execute("SELECT id FROM Roles WHERE nombre = 'Cliente'")
        cliente_rol_id = cursor.fetchone()[0]
        
        # Obtener IDs de categorías de servicios
        cursor.execute("SELECT id FROM Categorias_Servicios WHERE nombre = 'Cortes'")
        cat_cortes_id = cursor.fetchone()[0]
        
        cursor.execute("SELECT id FROM Categorias_Servicios WHERE nombre = 'Barba'")
        cat_barba_id = cursor.fetchone()[0]
        
        cursor.execute("SELECT id FROM Categorias_Servicios WHERE nombre = 'Paquetes'")
        cat_paquetes_id = cursor.fetchone()[0]
        
        print("✓ Roles y categorías obtenidos")
        
        # === 3. CREAR USUARIOS ===
        print("\n👥 Creando usuarios...")
        
        # Contraseña por defecto para todos: "password123"
        password_hash = generate_password_hash("password123")
        
        # Usuario Admin
        cursor.execute("""
            INSERT INTO Usuarios (email, password_hash, nombre, apellido, telefono, rol_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ('admin@barberia.com', password_hash, 'Admin', 'Sistema', '3001234567', admin_rol_id))
        cursor.execute("SELECT @@IDENTITY")
        admin_id = cursor.fetchone()[0]
        print(f"  ✓ Admin creado: admin@barberia.com / password123")
        
        # Propietario 1
        cursor.execute("""
            INSERT INTO Usuarios (email, password_hash, nombre, apellido, telefono, rol_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ('carlos.mendez@gmail.com', password_hash, 'Carlos', 'Méndez', '3009876543', propietario_rol_id))
        cursor.execute("SELECT @@IDENTITY")
        propietario1_id = cursor.fetchone()[0]
        print(f"  ✓ Propietario 1: carlos.mendez@gmail.com / password123")
        
        # Propietario 2
        cursor.execute("""
            INSERT INTO Usuarios (email, password_hash, nombre, apellido, telefono, rol_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ('maria.lopez@gmail.com', password_hash, 'María', 'López', '3015556789', propietario_rol_id))
        cursor.execute("SELECT @@IDENTITY")
        propietario2_id = cursor.fetchone()[0]
        print(f"  ✓ Propietario 2: maria.lopez@gmail.com / password123")
        
        # Barberos
        barberos_data = [
            ('juan.perez@gmail.com', 'Juan', 'Pérez', '3201234567'),
            ('pedro.gomez@gmail.com', 'Pedro', 'Gómez', '3107654321'),
            ('luis.rodriguez@gmail.com', 'Luis', 'Rodríguez', '3159876543'),
            ('andres.martinez@gmail.com', 'Andrés', 'Martínez', '3186543210')
        ]
        
        barberos_ids = []
        for email, nombre, apellido, telefono in barberos_data:
            cursor.execute("""
                INSERT INTO Usuarios (email, password_hash, nombre, apellido, telefono, rol_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (email, password_hash, nombre, apellido, telefono, barbero_rol_id))
            cursor.execute("SELECT @@IDENTITY")
            barberos_ids.append(cursor.fetchone()[0])
            print(f"  ✓ Barbero: {email} / password123")
        
        # Clientes
        clientes_data = [
            ('cliente1@gmail.com', 'Sofía', 'García', '3221234567'),
            ('cliente2@gmail.com', 'Miguel', 'Torres', '3112345678'),
            ('cliente3@gmail.com', 'Laura', 'Ramírez', '3003456789'),
            ('cliente4@gmail.com', 'David', 'Hernández', '3144567890'),
            ('cliente5@gmail.com', 'Ana', 'Jiménez', '3055678901')
        ]
        
        clientes_ids = []
        for email, nombre, apellido, telefono in clientes_data:
            cursor.execute("""
                INSERT INTO Usuarios (email, password_hash, nombre, apellido, telefono, rol_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (email, password_hash, nombre, apellido, telefono, cliente_rol_id))
            cursor.execute("SELECT @@IDENTITY")
            clientes_ids.append(cursor.fetchone()[0])
        print(f"  ✓ {len(clientes_ids)} clientes creados")
        
        conn.commit()
        
        # === 4. CREAR BARBERÍAS ===
        print("\n💈 Creando barberías...")
        
        cursor.execute("""
            INSERT INTO Barberias (nombre, direccion, ciudad, telefono, email, descripcion, 
                                  hora_apertura, hora_cierre, propietario_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'BarberShop El Clásico',
            'Calle 100 #15-20',
            'Bogotá',
            '6011234567',
            'contacto@elclasico.com',
            'Barbería tradicional con más de 20 años de experiencia. Especialistas en cortes clásicos y modernos.',
            time(9, 0),
            time(19, 0),
            propietario1_id
        ))
        cursor.execute("SELECT @@IDENTITY")
        barberia1_id = cursor.fetchone()[0]
        print("  ✓ BarberShop El Clásico")
        
        cursor.execute("""
            INSERT INTO Barberias (nombre, direccion, ciudad, telefono, email, descripcion, 
                                  hora_apertura, hora_cierre, propietario_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            'Modern Cuts Studio',
            'Carrera 15 #85-40',
            'Bogotá',
            '6017654321',
            'info@moderncuts.com',
            'Estudio de barbería moderna. Cortes de tendencia, diseños y color.',
            time(10, 0),
            time(20, 0),
            propietario2_id
        ))
        cursor.execute("SELECT @@IDENTITY")
        barberia2_id = cursor.fetchone()[0]
        print("  ✓ Modern Cuts Studio")
        
        conn.commit()
        
        # === 5. CREAR BARBEROS EN BARBERÍAS ===
        print("\n✂️  Asignando barberos a barberías...")
        
        # Barberos para Barbería 1
        cursor.execute("""
            INSERT INTO Barberos (usuario_id, barberia_id, especialidad, años_experiencia, 
                                 comision_porcentaje, calificacion_promedio)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (barberos_ids[0], barberia1_id, 'Cortes clásicos y barba', 8, 40.00, 4.8))
        cursor.execute("SELECT @@IDENTITY")
        barbero1_id = cursor.fetchone()[0]
        
        cursor.execute("""
            INSERT INTO Barberos (usuario_id, barberia_id, especialidad, años_experiencia, 
                                 comision_porcentaje, calificacion_promedio)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (barberos_ids[1], barberia1_id, 'Fade y diseños', 5, 35.00, 4.5))
        cursor.execute("SELECT @@IDENTITY")
        barbero2_id = cursor.fetchone()[0]
        
        # Barberos para Barbería 2
        cursor.execute("""
            INSERT INTO Barberos (usuario_id, barberia_id, especialidad, años_experiencia, 
                                 comision_porcentaje, calificacion_promedio)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (barberos_ids[2], barberia2_id, 'Cortes modernos y color', 6, 45.00, 4.9))
        cursor.execute("SELECT @@IDENTITY")
        barbero3_id = cursor.fetchone()[0]
        
        cursor.execute("""
            INSERT INTO Barberos (usuario_id, barberia_id, especialidad, años_experiencia, 
                                 comision_porcentaje, calificacion_promedio)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (barberos_ids[3], barberia2_id, 'Estilos de tendencia', 4, 40.00, 4.7))
        cursor.execute("SELECT @@IDENTITY")
        barbero4_id = cursor.fetchone()[0]
        
        print("  ✓ 4 barberos asignados")
        conn.commit()
        
        # === 6. CREAR SERVICIOS ===
        print("\n💇 Creando servicios...")
        
        servicios_barberia1 = [
            ('Corte Clásico', 'Corte tradicional con tijera y máquina', 25000, 30, cat_cortes_id),
            ('Corte Moderno', 'Corte de tendencia, incluye diseño básico', 30000, 40, cat_cortes_id),
            ('Corte Fade', 'Degradado profesional con acabado perfecto', 35000, 45, cat_cortes_id),
            ('Arreglo de Barba', 'Perfilado y recorte de barba', 15000, 20, cat_barba_id),
            ('Barba Completa', 'Arreglo de barba con toalla caliente y aceites', 25000, 30, cat_barba_id),
            ('Combo Corte + Barba', 'Corte de cabello y arreglo de barba', 40000, 50, cat_paquetes_id)
        ]
        
        for nombre, desc, precio, duracion, categoria in servicios_barberia1:
            cursor.execute("""
                INSERT INTO Servicios (barberia_id, categoria_id, nombre, descripcion, 
                                      precio, duracion_minutos)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (barberia1_id, categoria, nombre, desc, precio, duracion))
        
        servicios_barberia2 = [
            ('Corte Premium', 'Corte personalizado con técnicas modernas', 40000, 45, cat_cortes_id),
            ('Diseño Artístico', 'Diseños creativos y personalizados', 35000, 40, cat_cortes_id),
            ('Tinte de Barba', 'Coloración profesional de barba', 30000, 35, cat_barba_id),
            ('Spa Capilar', 'Tratamiento completo con masaje', 50000, 60, cat_paquetes_id),
            ('Paquete VIP', 'Corte + Barba + Spa', 80000, 90, cat_paquetes_id)
        ]
        
        for nombre, desc, precio, duracion, categoria in servicios_barberia2:
            cursor.execute("""
                INSERT INTO Servicios (barberia_id, categoria_id, nombre, descripcion, 
                                      precio, duracion_minutos)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (barberia2_id, categoria, nombre, desc, precio, duracion))
        
        print(f"  ✓ {len(servicios_barberia1) + len(servicios_barberia2)} servicios creados")
        conn.commit()
        
        # === 7. CREAR HORARIOS DE BARBEROS ===
        print("\n📅 Creando horarios de barberos...")
        
        # Horarios para todos los barberos (Lunes a Sábado: 9am-6pm)
        barberos_registrados = [barbero1_id, barbero2_id, barbero3_id, barbero4_id]
        
        for barbero_id in barberos_registrados:
            # Lunes a Viernes (días 2-6 en SQL Server DATEPART)
            for dia in range(2, 7):
                cursor.execute("""
                    INSERT INTO Horarios_Barberos (barbero_id, dia_semana, hora_inicio, hora_fin)
                    VALUES (?, ?, ?, ?)
                """, (barbero_id, dia, time(9, 0), time(18, 0)))
            
            # Sábado (día 7)
            cursor.execute("""
                INSERT INTO Horarios_Barberos (barbero_id, dia_semana, hora_inicio, hora_fin)
                VALUES (?, ?, ?, ?)
            """, (barbero_id, 7, time(10, 0), time(16, 0)))
        
        print("  ✓ Horarios creados para todos los barberos")
        conn.commit()
        
        print("\n✅ ¡SEED COMPLETADO EXITOSAMENTE!")
        print("\n" + "="*50)
        print("CREDENCIALES DE PRUEBA:")
        print("="*50)
        print("\n👨‍💼 Admin:")
        print("   Email: admin@barberia.com")
        print("   Password: password123")
        print("\n🏪 Propietarios:")
        print("   Email: carlos.mendez@gmail.com")
        print("   Email: maria.lopez@gmail.com")
        print("   Password: password123")
        print("\n✂️  Barberos:")
        print("   Email: juan.perez@gmail.com")
        print("   Email: pedro.gomez@gmail.com")
        print("   Email: luis.rodriguez@gmail.com")
        print("   Email: andres.martinez@gmail.com")
        print("   Password: password123")
        print("\n👤 Clientes:")
        print("   Email: cliente1@gmail.com hasta cliente5@gmail.com")
        print("   Password: password123")
        print("="*50)
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error durante el seed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        cursor.close()
        conn.close()

def reiniciar_database():
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        print("🗑️  Borrando todos los datos de la base de datos...")
        
        cursor.execute("DELETE FROM Notificaciones")
        cursor.execute("DELETE FROM Pagos")
        cursor.execute("DELETE FROM Resenas")
        cursor.execute("DELETE FROM Citas")
        cursor.execute("DELETE FROM Horarios_Barberos")
        cursor.execute("DELETE FROM Servicios")
        cursor.execute("DELETE FROM Barberos")
        cursor.execute("DELETE FROM Barberias")
        cursor.execute("DELETE FROM Usuarios")
        
        conn.commit()
        print("✓ Base de datos reiniciada exitosamente.")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error al reiniciar la base de datos: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    respuesta = input("Llenar la base de datos con datos de prueba o borrar la seed: 1/2 ")
    if respuesta == '1':
        seed_database()
    elif respuesta == '2':
        reiniciar_database()