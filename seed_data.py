import pyodbc
from config import Config
from werkzeug.security import generate_password_hash
from datetime import time

def get_connection():
    return pyodbc.connect(Config.DB_CONNECTION_STRING)

def limpiar_y_resetear_database():
    """Borra todos los datos y resetea los contadores IDENTITY"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        print("🗑️  Limpiando base de datos...")
        
        # Borrar datos en orden (respetando foreign keys)
        tablas = [
            'Notificaciones',
            'Pagos', 
            'Resenas',
            'Citas',
            'Horarios_Barberos',
            'Servicios',
            'Barberos',
            'Barberias',
            'Usuarios'
        ]
        
        for tabla in tablas:
            cursor.execute(f"DELETE FROM {tabla}")
            print(f"  ✓ {tabla} limpiada")
        
        conn.commit()
        
        # Resetear contadores IDENTITY
        print("\n🔄 Reseteando contadores de IDs...")
        
        for tabla in tablas:
            cursor.execute(f"DBCC CHECKIDENT ('{tabla}', RESEED, 0)")
            print(f"  ✓ {tabla} reseteada")
        
        conn.commit()
        print("\n✅ Base de datos limpia y lista para datos nuevos\n")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error al limpiar: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def seed_database():
    """Llena la base de datos con datos de prueba"""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        print("=" * 60)
        print("🌱 INICIANDO SEED DE BASE DE DATOS")
        print("=" * 60)
        
        # === LIMPIAR Y RESETEAR PRIMERO ===
        limpiar_y_resetear_database()
        
        # Reconectar después del reset
        conn = get_connection()
        cursor = conn.cursor()
        
        # === OBTENER IDs DE ROLES Y CATEGORÍAS ===
        print("📋 Obteniendo roles y categorías del sistema...")
        
        cursor.execute("SELECT id FROM Roles WHERE nombre = 'Admin'")
        admin_rol_id = cursor.fetchone()[0]
        
        cursor.execute("SELECT id FROM Roles WHERE nombre = 'Propietario'")
        propietario_rol_id = cursor.fetchone()[0]
        
        cursor.execute("SELECT id FROM Roles WHERE nombre = 'Barbero'")
        barbero_rol_id = cursor.fetchone()[0]
        
        cursor.execute("SELECT id FROM Roles WHERE nombre = 'Cliente'")
        cliente_rol_id = cursor.fetchone()[0]
        
        cursor.execute("SELECT id FROM Categorias_Servicios WHERE nombre = 'Cortes'")
        cat_cortes_id = cursor.fetchone()[0]
        
        cursor.execute("SELECT id FROM Categorias_Servicios WHERE nombre = 'Barba'")
        cat_barba_id = cursor.fetchone()[0]
        
        cursor.execute("SELECT id FROM Categorias_Servicios WHERE nombre = 'Paquetes'")
        cat_paquetes_id = cursor.fetchone()[0]
        
        print("  ✓ Roles y categorías obtenidos\n")
        
        # === CREAR USUARIOS ===
        print("👥 Creando usuarios...")
        
        password_hash = generate_password_hash("password123")
        
        # Admin
        cursor.execute("""
            INSERT INTO Usuarios (email, password_hash, nombre, apellido, telefono, rol_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ('admin@barberia.com', password_hash, 'Admin', 'Sistema', '3001234567', admin_rol_id))
        cursor.execute("SELECT @@IDENTITY")
        admin_id = cursor.fetchone()[0]
        print(f"  ✓ Admin creado (ID: {admin_id})")
        
        # Propietarios
        cursor.execute("""
            INSERT INTO Usuarios (email, password_hash, nombre, apellido, telefono, rol_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ('carlos.mendez@gmail.com', password_hash, 'Carlos', 'Méndez', '3009876543', propietario_rol_id))
        cursor.execute("SELECT @@IDENTITY")
        propietario1_id = cursor.fetchone()[0]
        print(f"  ✓ Propietario 1 creado (ID: {propietario1_id})")
        
        cursor.execute("""
            INSERT INTO Usuarios (email, password_hash, nombre, apellido, telefono, rol_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ('maria.lopez@gmail.com', password_hash, 'María', 'López', '3015556789', propietario_rol_id))
        cursor.execute("SELECT @@IDENTITY")
        propietario2_id = cursor.fetchone()[0]
        print(f"  ✓ Propietario 2 creado (ID: {propietario2_id})")
        
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
            user_id = cursor.fetchone()[0]
            barberos_ids.append(user_id)
            print(f"  ✓ Barbero: {nombre} (ID: {user_id})")
        
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
        
        print(f"  ✓ {len(clientes_ids)} clientes creados\n")
        conn.commit()
        
        # === CREAR BARBERÍAS ===
        print("💈 Creando barberías...")
        
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
            'Barbería tradicional con un ambiente acogedor y profesional, reconocida por su dedicación al detalle y más de dos décadas ofreciendo cortes clásicos y modernos para cada cliente.',
            time(9, 0),
            time(19, 0),
            propietario1_id
        ))
        cursor.execute("SELECT @@IDENTITY")
        barberia1_id = cursor.fetchone()[0]
        print(f"  ✓ BarberShop El Clásico (ID: {barberia1_id})")
        
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
            'Estudio de barbería moderna, especializado en cortes de tendencia, diseños personalizados y color profesional para quienes buscan un estilo fresco y distintivo.',
            time(10, 0),
            time(20, 0),
            propietario2_id
        ))
        cursor.execute("SELECT @@IDENTITY")
        barberia2_id = cursor.fetchone()[0]
        print(f"  ✓ Modern Cuts Studio (ID: {barberia2_id})\n")
        
        conn.commit()
        
        # === CREAR BARBEROS EN BARBERÍAS ===
        print("✂️  Asignando barberos a barberías...")
        
        cursor.execute("""
            INSERT INTO Barberos (usuario_id, barberia_id, especialidad, años_experiencia, 
                                 comision_porcentaje, calificacion_promedio)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (barberos_ids[0], barberia1_id, 'Cortes clásicos y barba', 8, 40.00, 4.8))
        cursor.execute("SELECT @@IDENTITY")
        barbero1_id = cursor.fetchone()[0]
        print(f"  ✓ Juan Pérez → BarberShop El Clásico (Barbero ID: {barbero1_id})")
        
        cursor.execute("""
            INSERT INTO Barberos (usuario_id, barberia_id, especialidad, años_experiencia, 
                                 comision_porcentaje, calificacion_promedio)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (barberos_ids[1], barberia1_id, 'Fade y diseños', 5, 35.00, 4.5))
        cursor.execute("SELECT @@IDENTITY")
        barbero2_id = cursor.fetchone()[0]
        print(f"  ✓ Pedro Gómez → BarberShop El Clásico (Barbero ID: {barbero2_id})")
        
        cursor.execute("""
            INSERT INTO Barberos (usuario_id, barberia_id, especialidad, años_experiencia, 
                                 comision_porcentaje, calificacion_promedio)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (barberos_ids[2], barberia2_id, 'Cortes modernos y color', 6, 45.00, 4.9))
        cursor.execute("SELECT @@IDENTITY")
        barbero3_id = cursor.fetchone()[0]
        print(f"  ✓ Luis Rodríguez → Modern Cuts Studio (Barbero ID: {barbero3_id})")
        
        cursor.execute("""
            INSERT INTO Barberos (usuario_id, barberia_id, especialidad, años_experiencia, 
                                 comision_porcentaje, calificacion_promedio)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (barberos_ids[3], barberia2_id, 'Estilos de tendencia', 4, 40.00, 4.7))
        cursor.execute("SELECT @@IDENTITY")
        barbero4_id = cursor.fetchone()[0]
        print(f"  ✓ Andrés Martínez → Modern Cuts Studio (Barbero ID: {barbero4_id})\n")
        
        conn.commit()
        
        # === CREAR SERVICIOS ===
        print("💇 Creando servicios...")
        
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
        
        print(f"  ✓ {len(servicios_barberia1)} servicios para BarberShop El Clásico")
        
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
        
        print(f"  ✓ {len(servicios_barberia2)} servicios para Modern Cuts Studio\n")
        conn.commit()
        
        # === CREAR HORARIOS DE BARBEROS ===
        print("📅 Creando horarios de barberos...")
        
        barberos_registrados = [barbero1_id, barbero2_id, barbero3_id, barbero4_id]
        
        for barbero_id in barberos_registrados:
            # Lunes a Viernes (días 2-6)
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
        
        print(f"  ✓ Horarios creados para {len(barberos_registrados)} barberos\n")
        conn.commit()
        
        # === RESUMEN ===
        print("=" * 60)
        print("✅ ¡SEED COMPLETADO EXITOSAMENTE!")
        print("=" * 60)
        print("\n📊 RESUMEN:")
        print(f"   • Barbería 1 (ID: {barberia1_id}): BarberShop El Clásico")
        print(f"   • Barbería 2 (ID: {barberia2_id}): Modern Cuts Studio")
        print(f"   • Total usuarios: {len(barberos_ids) + len(clientes_ids) + 3}")
        print(f"   • Total servicios: {len(servicios_barberia1) + len(servicios_barberia2)}")
        print("\n" + "=" * 60)
        print("🔑 CREDENCIALES DE PRUEBA:")
        print("=" * 60)
        print("\n👨‍💼 ADMIN:")
        print("   📧 Email: admin@barberia.com")
        print("   🔒 Password: password123")
        print("\n🏪 PROPIETARIOS:")
        print("   📧 carlos.mendez@gmail.com")
        print("   📧 maria.lopez@gmail.com")
        print("   🔒 Password: password123")
        print("\n✂️  BARBEROS:")
        print("   📧 juan.perez@gmail.com")
        print("   📧 pedro.gomez@gmail.com")
        print("   📧 luis.rodriguez@gmail.com")
        print("   📧 andres.martinez@gmail.com")
        print("   🔒 Password: password123")
        print("\n👤 CLIENTES:")
        print("   📧 cliente1@gmail.com a cliente5@gmail.com")
        print("   🔒 Password: password123")
        print("\n" + "=" * 60)
        print("⚠️  IMPORTANTE: Todos los IDs han sido reseteados.")
        print("    Todas las máquinas tendrán los mismos IDs.")
        print("=" * 60 + "\n")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error durante el seed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("  SISTEMA DE SEED - BARBERBOOK")
    print("=" * 60)
    print("\nEste script limpiará TODA la base de datos y creará")
    print("datos de prueba desde cero con IDs consistentes.\n")
    
    respuesta = input("¿Deseas continuar? (s/n): ")
    
    if respuesta.lower() == 's':
        seed_database()
    else:
        print("\n❌ Operación cancelada.\n")