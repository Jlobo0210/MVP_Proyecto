from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.database import *
from app.auth import *
from datetime import datetime, timedelta, date, time as datetime_time

# === BLUEPRINTS ===

main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)
cliente_bp = Blueprint('cliente', __name__)


# ============================================
# RUTAS PÚBLICAS (Main Blueprint)
# ============================================

@main_bp.route('/')
def index():
    """Página principal - Landing page"""
    barberias = obtener_barberias_activas()
    return render_template('index.html', barberias=barberias)


@main_bp.route('/barberia/<int:barberia_id>')
def ver_barberia(barberia_id):
    """Ver detalles de una barbería específica"""
    barberia = obtener_barberia_por_id(barberia_id)
    if not barberia:
        flash('Barbería no encontrada', 'danger')
        return redirect(url_for('main.index'))
    
    servicios = obtener_servicios_por_barberia(barberia_id)
    barberos = obtener_barberos_por_barberia(barberia_id)
    
    return render_template('barberia.html', 
                         barberia=barberia, 
                         servicios=servicios,
                         barberos=barberos)


# ============================================
# RUTAS DE AUTENTICACIÓN (Auth Blueprint)
# ============================================

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login de usuarios"""
    if is_authenticated():
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = obtener_usuario_por_email(email)
        
        if user and verify_password(user['password_hash'], password):
            if not user['activo']:
                flash('Tu cuenta está inactiva. Contacta al administrador.', 'danger')
                return redirect(url_for('auth.login'))
            
            login_user(user)
            flash(f'¡Bienvenido {user["nombre"]}!', 'success')
            
            # Redirigir según el rol
            if user['rol_nombre'] == 'Admin':
                return redirect(url_for('main.index'))  # TODO: crear dashboard admin
            elif user['rol_nombre'] == 'Cliente':
                return redirect(url_for('cliente.dashboard'))
            elif user['rol_nombre'] == 'Barbero':
                return redirect(url_for('main.index'))  # TODO: crear dashboard barbero
            elif user['rol_nombre'] == 'Propietario':
                return redirect(url_for('main.index'))  # TODO: crear dashboard propietario
            else:
                return redirect(url_for('main.index'))
        else:
            flash('Email o contraseña incorrectos', 'danger')
    
    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registro de nuevos usuarios (solo clientes)"""
    if is_authenticated():
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        telefono = request.form.get('telefono')
        
        # Validaciones
        if password != password_confirm:
            flash('Las contraseñas no coinciden', 'danger')
            return redirect(url_for('auth.register'))
        
        # Verificar si el email ya existe
        existing_user = obtener_usuario_por_email(email)
        if existing_user:
            flash('El email ya está registrado', 'danger')
            return redirect(url_for('auth.register'))
        
        # Obtener el rol de cliente
        rol_cliente = obtener_rol_por_nombre('Cliente')
        
        # Crear el usuario
        try:
            password_hash = hash_password(password)
            user_id = crear_usuario(email, password_hash, nombre, apellido, telefono, rol_cliente['id'])
            
            flash('¡Registro exitoso! Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Error al crear usuario: {str(e)}', 'danger')
            return redirect(url_for('auth.register'))
    
    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Cerrar sesión"""
    logout_user()
    flash('Sesión cerrada exitosamente', 'info')
    return redirect(url_for('main.index'))


# ============================================
# RUTAS DE CLIENTE (Cliente Blueprint)
# ============================================

@cliente_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard del cliente - Ver sus citas"""
    user = get_current_user()
    citas = obtener_citas_por_cliente(user['id'])
    
    # Separar citas próximas y pasadas
    hoy = date.today()
    citas_proximas = [c for c in citas if c['fecha'] >= hoy and c['estado'] in ['Pendiente', 'Confirmada']]
    citas_pasadas = [c for c in citas if c['fecha'] < hoy or c['estado'] in ['Completada', 'Cancelada', 'No Show']]
    
    return render_template('cliente/dashboard.html', 
                         citas_proximas=citas_proximas,
                         citas_pasadas=citas_pasadas)


@cliente_bp.route('/reservar/<int:barberia_id>', methods=['GET', 'POST'])
@login_required
def reservar(barberia_id):
    """Página para hacer una reserva"""
    barberia = obtener_barberia_por_id(barberia_id)
    if not barberia:
        flash('Barbería no encontrada', 'danger')
        return redirect(url_for('main.index'))
    
    servicios = obtener_servicios_por_barberia(barberia_id)
    barberos = obtener_barberos_por_barberia(barberia_id)
    
    if request.method == 'POST':
        servicio_id = request.form.get('servicio_id')
        barbero_id = request.form.get('barbero_id')
        fecha_str = request.form.get('fecha')
        hora_str = request.form.get('hora')
        notas = request.form.get('notas', '')
        
        try:
            # Parsear fecha y hora
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
            hora_inicio = datetime.strptime(hora_str, '%H:%M').time()
            
            # Obtener servicio para calcular duración
            servicio = obtener_servicio_por_id(int(servicio_id))
            
            # Calcular hora de fin
            hora_inicio_dt = datetime.combine(date.today(), hora_inicio)
            hora_fin_dt = hora_inicio_dt + timedelta(minutes=servicio['duracion_minutos'])
            hora_fin = hora_fin_dt.time()
            
            # Crear la cita
            user = get_current_user()
            cita_id = crear_cita(
                cliente_id=user['id'],
                barbero_id=int(barbero_id),
                servicio_id=int(servicio_id),
                fecha=fecha,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                precio_final=servicio['precio'],
                notas_cliente=notas if notas else None
            )
            
            flash('¡Cita reservada exitosamente!', 'success')
            return redirect(url_for('cliente.dashboard'))
            
        except Exception as e:
            flash(f'Error al crear la cita: {str(e)}', 'danger')
            return redirect(url_for('cliente.reservar', barberia_id=barberia_id))
    
    return render_template('cliente/reservar.html',
                         barberia=barberia,
                         servicios=servicios,
                         barberos=barberos)


@cliente_bp.route('/horarios-disponibles')
@login_required
def horarios_disponibles():
    """API endpoint para obtener horarios disponibles de un barbero en una fecha"""
    barbero_id = request.args.get('barbero_id', type=int)
    fecha_str = request.args.get('fecha')
    
    if not barbero_id or not fecha_str:
        return {'error': 'Faltan parámetros'}, 400
    
    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        slots_info = obtener_slots_disponibles(barbero_id, fecha)
        
        if not slots_info:
            return {'disponibles': []}
        
        # Generar slots cada 30 minutos
        slots_disponibles = []
        hora_actual = datetime.combine(fecha, slots_info['horario_inicio'])
        hora_fin = datetime.combine(fecha, slots_info['horario_fin'])
        
        while hora_actual < hora_fin:
            hora_slot = hora_actual.time()
            
            # Verificar si está ocupado
            esta_ocupado = False
            for ocupado_inicio, ocupado_fin in slots_info['citas_ocupadas']:
                if ocupado_inicio <= hora_slot < ocupado_fin:
                    esta_ocupado = True
                    break
            
            if not esta_ocupado:
                slots_disponibles.append(hora_slot.strftime('%H:%M'))
            
            hora_actual += timedelta(minutes=30)
        
        return {'disponibles': slots_disponibles}
        
    except Exception as e:
        return {'error': str(e)}, 500


@cliente_bp.route('/perfil')
@login_required
def perfil():
    """Perfil del cliente"""
    user = get_current_user()
    return render_template('cliente/perfil.html', user=user)


# ============================================
# MANEJADORES DE ERRORES
# ============================================

@main_bp.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404


@main_bp.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500