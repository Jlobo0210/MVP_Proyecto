from config import Config
import pyodbc

try:
    print("Intentando conectar a SQL Server...")
    print(f"Connection String: {Config.DB_CONNECTION_STRING}")
    
    conn = pyodbc.connect(Config.DB_CONNECTION_STRING)
    print("✓ Conexión exitosa!")
    
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Usuarios")
    count = cursor.fetchone()[0]
    print(f"✓ Hay {count} usuarios en la base de datos")
    
    cursor.close()
    conn.close()
    
except pyodbc.Error as e:
    print(f"✗ Error de conexión: {e}")