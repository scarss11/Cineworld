from database import query
from werkzeug.security import generate_password_hash, check_password_hash

def get_by_correo(correo):
    return query("SELECT * FROM usuarios WHERE correo=%s AND activo=1", (correo,), fetchone=True)

def get_by_id(uid):
    return query("SELECT * FROM usuarios WHERE id=%s", (uid,), fetchone=True)

def create(documento, nombre, apellido, telefono, correo, password, rol='cliente'):
    hashed = generate_password_hash(password)
    query(
        "INSERT INTO usuarios (documento,nombre,apellido,telefono,correo,password,rol) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        (documento, nombre, apellido, telefono, correo, hashed, rol), commit=True
    )

def verify_password(correo, password):
    u = get_by_correo(correo)
    if u and check_password_hash(u['password'], password):
        return u
    return None

def get_all():
    return query("SELECT id,documento,nombre,apellido,correo,rol,activo,created_at FROM usuarios ORDER BY created_at DESC", fetchall=True)

def toggle_activo(uid):
    query("UPDATE usuarios SET activo = CASE WHEN activo=1 THEN 0 ELSE 1 END WHERE id=%s", (uid,), commit=True)
