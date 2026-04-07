from database import query

def get_all_activas():
    return query("SELECT * FROM peliculas WHERE activa=1 ORDER BY titulo", fetchall=True)

def get_all():
    return query("SELECT * FROM peliculas ORDER BY created_at DESC", fetchall=True)

def get_by_id(pid):
    return query("SELECT * FROM peliculas WHERE id=%s", (pid,), fetchone=True)

def create(titulo, genero, duracion, clasificacion, descripcion, imagen_url=''):
    query(
        "INSERT INTO peliculas (titulo,genero,duracion,clasificacion,descripcion,imagen_url) VALUES (%s,%s,%s,%s,%s,%s)",
        (titulo, genero, duracion, clasificacion, descripcion, imagen_url), commit=True
    )

def update(pid, titulo, genero, duracion, clasificacion, descripcion, imagen_url=''):
    query(
        "UPDATE peliculas SET titulo=%s,genero=%s,duracion=%s,clasificacion=%s,descripcion=%s,imagen_url=%s WHERE id=%s",
        (titulo, genero, duracion, clasificacion, descripcion, imagen_url, pid), commit=True
    )

def toggle_activa(pid):
    query("UPDATE peliculas SET activa = CASE WHEN activa=1 THEN 0 ELSE 1 END WHERE id=%s", (pid,), commit=True)
