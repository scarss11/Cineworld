from database import query

def get_activas():
    return query("""
        SELECT f.*, p.titulo, p.genero, p.clasificacion, p.imagen_url, p.duracion,
               s.nombre as sala_nombre, s.tipo as sala_tipo
        FROM funciones f
        JOIN peliculas p ON p.id=f.pelicula_id
        JOIN salas s ON s.id=f.sala_id
        WHERE f.activa=1 AND f.fecha >= CURRENT_DATE
        ORDER BY f.fecha, f.hora
    """, fetchall=True)

def get_by_pelicula(pelicula_id):
    return query("""
        SELECT f.*, s.nombre as sala_nombre, s.tipo as sala_tipo
        FROM funciones f
        JOIN salas s ON s.id=f.sala_id
        WHERE f.pelicula_id=%s AND f.activa=1 AND f.fecha >= CURRENT_DATE
        ORDER BY f.fecha, f.hora
    """, (pelicula_id,), fetchall=True)

def get_by_id(fid):
    return query("""
        SELECT f.*, p.titulo, p.imagen_url, p.duracion, p.clasificacion,
               s.nombre as sala_nombre, s.tipo as sala_tipo, s.capacidad
        FROM funciones f
        JOIN peliculas p ON p.id=f.pelicula_id
        JOIN salas s ON s.id=f.sala_id
        WHERE f.id=%s
    """, (fid,), fetchone=True)

def get_all():
    return query("""
        SELECT f.*, p.titulo, s.nombre as sala_nombre
        FROM funciones f
        JOIN peliculas p ON p.id=f.pelicula_id
        JOIN salas s ON s.id=f.sala_id
        ORDER BY f.fecha DESC, f.hora DESC
    """, fetchall=True)

def create(pelicula_id, sala_id, fecha, hora, precio):
    query(
        "INSERT INTO funciones (pelicula_id,sala_id,fecha,hora,precio) VALUES (%s,%s,%s,%s,%s)",
        (pelicula_id, sala_id, fecha, hora, precio), commit=True
    )

def toggle_activa(fid):
    query("UPDATE funciones SET activa = CASE WHEN activa=1 THEN 0 ELSE 1 END WHERE id=%s", (fid,), commit=True)
