from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask import session, redirect, url_for, flash
from app.database import obtener_usuario_por_id, actualizar_ultimo_acceso


def hash_password(password):
    """Genera un hash seguro de la contraseña"""
    return generate_password_hash(password)


def verify_password(password_hash, password):
    """Verifica que la contraseña coincida con el hash"""
    return check_password_hash(password_hash, password)


def login_user(user):
    """Guarda el usuario en la sesión"""
    session['user_id'] = user['id']
    session['user_email'] = user['email']
    session['user_nombre'] = user['nombre']
    session['user_apellido'] = user['apellido']
    session['user_rol'] = user['rol_nombre']
    session.permanent = True
    
    # Actualizar último acceso
    actualizar_ultimo_acceso(user['id'])


def logout_user():
    """Elimina el usuario de la sesión"""
    session.clear()


def get_current_user():
    """Obtiene el usuario actual desde la sesión"""
    user_id = session.get('user_id')
    if user_id:
        return obtener_usuario_por_id(user_id)
    return None


def is_authenticated():
    """Verifica si hay un usuario autenticado"""
    return 'user_id' in session


# --- DECORADORES PARA PROTEGER RUTAS ---

def login_required(f):
    """Decorador para rutas que requieren autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            flash('Por favor inicia sesión para acceder a esta página.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*roles):
    """Decorador para rutas que requieren roles específicos"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not is_authenticated():
                flash('Por favor inicia sesión para acceder a esta página.', 'warning')
                return redirect(url_for('auth.login'))
            
            user = get_current_user()
            if user['rol_nombre'] not in roles:
                flash('No tienes permisos para acceder a esta página.', 'danger')
                return redirect(url_for('main.index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """Decorador para rutas que solo puede acceder el administrador"""
    return role_required('Admin')(f)


def propietario_required(f):
    """Decorador para rutas de propietarios"""
    return role_required('Admin', 'Propietario')(f)


def barbero_required(f):
    """Decorador para rutas de barberos"""
    return role_required('Admin', 'Barbero')(f)


def cliente_required(f):
    """Decorador para rutas de clientes"""
    return role_required('Cliente')(f)