from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_session import Session
from functools import wraps
import os
import models.usuarios as usuarios_model
import models.peliculas as peliculas_model
import models.funciones as funciones_model
import models.asientos as asientos_model
import models.compras as compras_model
import models.salas as salas_model

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'cineworld-local-secret-2025')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
Session(app)

# ─── HEADERS NO-CACHE ───────────────────────────────────────────────
@app.after_request
def no_cache(response):
    path = request.path
    if any(path.startswith(p) for p in ['/cliente', '/admin', '/api', '/dashboard']):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

# ─── DECORADORES ────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def rol_required(rol):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            if session.get('rol') != rol:
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated
    return decorator

# ─── LANDING ────────────────────────────────────────────────────────
@app.route('/')
def index():
    peliculas = peliculas_model.get_all_activas()
    salas = salas_model.get_all()
    return render_template('landing.html', peliculas=peliculas, salas=salas)

@app.route('/cartelera')
def cartelera():
    peliculas = peliculas_model.get_all_activas()
    generos = list(set(p['genero'] for p in peliculas if p['genero']))
    return render_template('pages/cartelera.html', peliculas=peliculas, generos=generos)

@app.route('/salas')
def salas_page():
    salas = salas_model.get_all()
    return render_template('pages/salas.html', salas=salas)

@app.route('/contacto')
def contacto():
    return render_template('pages/contacto.html')

# ─── AUTH ────────────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form.get('correo', '').strip()
        password = request.form.get('password', '')
        user = usuarios_model.verify_password(correo, password)
        if user:
            session['user_id'] = user['id']
            session['nombre'] = user['nombre']
            session['rol'] = user['rol']
            if user['rol'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('cliente_dashboard'))
        flash('Credenciales incorrectas', 'error')
    return render_template('auth/login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        try:
            usuarios_model.create(
                request.form['documento'], request.form['nombre'],
                request.form['apellido'], request.form.get('telefono', ''),
                request.form['correo'], request.form['password']
            )
            flash('Cuenta creada exitosamente. Inicia sesión.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Error al crear cuenta. El correo o documento ya existe.', 'error')
    return render_template('auth/registro.html')

@app.route('/logout')
def logout():
    session.clear()
    return render_template('auth/logged_out.html')

# ─── CLIENTE ────────────────────────────────────────────────────────
@app.route('/cliente/dashboard')
@rol_required('cliente')
def cliente_dashboard():
    peliculas = peliculas_model.get_all_activas()
    return render_template('cliente/dashboard.html', peliculas=peliculas)

@app.route('/cliente/pelicula/<int:pid>')
@rol_required('cliente')
def seleccionar_funcion(pid):
    pelicula = peliculas_model.get_by_id(pid)
    funciones = funciones_model.get_by_pelicula(pid)
    return render_template('cliente/seleccionar_funcion.html', pelicula=pelicula, funciones=funciones)

@app.route('/cliente/funcion/<int:fid>/asientos')
@rol_required('cliente')
def seleccionar_asientos(fid):
    funcion = funciones_model.get_by_id(fid)
    asientos = asientos_model.get_by_sala(funcion['sala_id'])
    ocupados_raw = asientos_model.get_ocupados_funcion(fid)
    ocupados = [r['asiento_id'] for r in ocupados_raw]
    return render_template('cliente/seleccionar_asientos.html',
                           funcion=funcion, asientos=asientos, ocupados=ocupados)

@app.route('/cliente/comprar', methods=['POST'])
@rol_required('cliente')
def comprar():
    fid = int(request.form['funcion_id'])
    asientos_ids = request.form.getlist('asientos[]')
    if not asientos_ids:
        flash('Selecciona al menos un asiento', 'error')
        return redirect(url_for('seleccionar_asientos', fid=fid))
    funcion = funciones_model.get_by_id(fid)
    compra_id = compras_model.crear_compra(session['user_id'], fid, [int(a) for a in asientos_ids], funcion['precio'])
    flash(f'¡Compra confirmada! #{compra_id}', 'success')
    return redirect(url_for('mis_tickets'))

@app.route('/cliente/tickets')
@rol_required('cliente')
def mis_tickets():
    tickets = compras_model.get_tickets_by_cliente(session['user_id'])
    return render_template('cliente/mis_tickets.html', tickets=tickets)

@app.route('/cliente/historial')
@rol_required('cliente')
def historial():
    compras = compras_model.get_by_cliente(session['user_id'])
    return render_template('cliente/historial.html', compras=compras)

@app.route('/cliente/perfil')
@rol_required('cliente')
def perfil():
    user = usuarios_model.get_by_id(session['user_id'])
    return render_template('cliente/perfil.html', user=user)

# ─── ADMIN ──────────────────────────────────────────────────────────
@app.route('/admin/dashboard')
@rol_required('admin')
def admin_dashboard():
    stats = compras_model.get_stats()
    return render_template('admin/dashboard.html', stats=stats)

@app.route('/admin/peliculas', methods=['GET', 'POST'])
@rol_required('admin')
def admin_peliculas():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            peliculas_model.create(
                request.form['titulo'], request.form['genero'],
                request.form['duracion'], request.form['clasificacion'],
                request.form['descripcion'], request.form.get('imagen_url', '')
            )
        elif action == 'update':
            peliculas_model.update(
                request.form['id'], request.form['titulo'], request.form['genero'],
                request.form['duracion'], request.form['clasificacion'],
                request.form['descripcion'], request.form.get('imagen_url', '')
            )
        elif action == 'toggle':
            peliculas_model.toggle_activa(request.form['id'])
        return redirect(url_for('admin_peliculas'))
    peliculas = peliculas_model.get_all()
    return render_template('admin/peliculas.html', peliculas=peliculas)

@app.route('/admin/funciones', methods=['GET', 'POST'])
@rol_required('admin')
def admin_funciones():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            funciones_model.create(
                request.form['pelicula_id'], request.form['sala_id'],
                request.form['fecha'], request.form['hora'], request.form['precio']
            )
        elif action == 'toggle':
            funciones_model.toggle_activa(request.form['id'])
        return redirect(url_for('admin_funciones'))
    funciones = funciones_model.get_all()
    peliculas = peliculas_model.get_all_activas()
    salas = salas_model.get_all()
    return render_template('admin/funciones.html', funciones=funciones, peliculas=peliculas, salas=salas)

@app.route('/admin/salas', methods=['GET', 'POST'])
@rol_required('admin')
def admin_salas():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create':
            salas_model.create(request.form['nombre'], request.form['capacidad'], request.form['tipo'])
        elif action == 'update':
            salas_model.update(request.form['id'], request.form['nombre'], request.form['capacidad'], request.form['tipo'])
        return redirect(url_for('admin_salas'))
    salas = salas_model.get_all()
    return render_template('admin/salas.html', salas=salas)

@app.route('/admin/compras')
@rol_required('admin')
def admin_compras():
    compras = compras_model.get_all()
    return render_template('admin/compras.html', compras=compras)

@app.route('/admin/reportes')
@rol_required('admin')
def admin_reportes():
    ventas = compras_model.get_ventas_por_pelicula()
    return render_template('admin/reportes.html', ventas=ventas)

@app.route('/admin/usuarios', methods=['GET', 'POST'])
@rol_required('admin')
def admin_usuarios():
    if request.method == 'POST':
        usuarios_model.toggle_activo(request.form['id'])
        return redirect(url_for('admin_usuarios'))
    users = usuarios_model.get_all()
    return render_template('admin/usuarios.html', users=users)

if __name__ == '__main__':
    app.run(debug=True)
