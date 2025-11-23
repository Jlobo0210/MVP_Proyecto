import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # Configuración general de Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Configuración de SQL Server
    DB_SERVER = os.environ.get('DB_SERVER') or 'localhost\\SQLEXPRESS'
    DB_NAME = os.environ.get('DB_NAME') or 'BarberiaReservas'
    DB_USER = os.environ.get('DB_USER') or 'AdministradorBarberia'
    DB_PASSWORD = os.environ.get('DB_PASSWORD') or 'AdministradorBarberia10'

    # Connection string para pyodbc
    DB_CONNECTION_STRING = (
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={DB_SERVER};'
        f'DATABASE={DB_NAME};'
        f'UID={DB_USER};'
        f'PWD={DB_PASSWORD}'
    )
    
    # Configuración de sesiones
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hora en segundos
    
    # Configuración de paginación
    CITAS_PER_PAGE = 10
    SERVICIOS_PER_PAGE = 12