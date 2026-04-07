from database import query

def get_all():
    return query("SELECT * FROM salas ORDER BY nombre", fetchall=True)

def get_by_id(sid):
    return query("SELECT * FROM salas WHERE id=%s", (sid,), fetchone=True)

def create(nombre, capacidad, tipo='Estandar'):
    query("INSERT INTO salas (nombre,capacidad,tipo) VALUES (%s,%s,%s)", (nombre, capacidad, tipo), commit=True)

def update(sid, nombre, capacidad, tipo):
    query("UPDATE salas SET nombre=%s,capacidad=%s,tipo=%s WHERE id=%s", (nombre, capacidad, tipo, sid), commit=True)
