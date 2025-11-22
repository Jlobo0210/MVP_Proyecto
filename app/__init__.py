from flask import Flask
from config import Config
from datetime import timedelta


def create_app():
    """Crea y configura la aplicación Flask"""
    app = Flask(__name__)
    
    # Cargar configuración
    app.config.from_object(Config)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)
    
    # Registrar rutas
    from app.routes import main_bp, auth_bp, cliente_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(cliente_bp, url_prefix='/cliente')
    
    # Context processor para tener el usuario disponible en todos los templates
    from app.auth import get_current_user, is_authenticated
    
    @app.context_processor
    def inject_user():
        return {
            'current_user': get_current_user(),
            'is_authenticated': is_authenticated()
        }
    
    return app