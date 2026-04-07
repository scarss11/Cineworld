"""
CineWorld — Inicializador de base de datos local (SQLite)
Ejecutar una sola vez: python init_db.py
"""
import sqlite3, os
from datetime import date, timedelta
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), 'cineworld.db')

# Si ya existe, preguntar si reiniciar
if os.path.exists(DB_PATH):
    resp = input("cineworld.db ya existe. ¿Reiniciar? (s/N): ").strip().lower()
    if resp == 's':
        os.remove(DB_PATH)
        print("✓ BD anterior eliminada.")
    else:
        print("Sin cambios. Saliendo.")
        exit()

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.executescript("""
CREATE TABLE IF NOT EXISTS usuarios (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  documento TEXT UNIQUE NOT NULL,
  nombre TEXT NOT NULL,
  apellido TEXT NOT NULL,
  telefono TEXT,
  correo TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  rol TEXT NOT NULL CHECK (rol IN ('cliente','admin')),
  activo INTEGER DEFAULT 1,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS peliculas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  titulo TEXT NOT NULL,
  genero TEXT,
  duracion INTEGER,
  clasificacion TEXT,
  descripcion TEXT,
  imagen_url TEXT,
  activa INTEGER DEFAULT 1,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS salas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nombre TEXT NOT NULL,
  capacidad INTEGER NOT NULL,
  tipo TEXT DEFAULT 'Estandar'
);

CREATE TABLE IF NOT EXISTS funciones (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  pelicula_id INTEGER NOT NULL REFERENCES peliculas(id),
  sala_id INTEGER NOT NULL REFERENCES salas(id),
  fecha TEXT NOT NULL,
  hora TEXT NOT NULL,
  precio REAL NOT NULL,
  activa INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS asientos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  sala_id INTEGER NOT NULL REFERENCES salas(id),
  fila TEXT NOT NULL,
  numero INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS compras (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  cliente_id INTEGER NOT NULL REFERENCES usuarios(id),
  funcion_id INTEGER NOT NULL REFERENCES funciones(id),
  total REAL NOT NULL,
  estado TEXT DEFAULT 'confirmada',
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS tickets (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  compra_id INTEGER NOT NULL REFERENCES compras(id),
  asiento_id INTEGER NOT NULL REFERENCES asientos(id),
  codigo TEXT UNIQUE NOT NULL,
  estado TEXT DEFAULT 'activo'
);
""")

# ── Usuarios ─────────────────────────────────────────
cur.execute(
    "INSERT OR IGNORE INTO usuarios (documento,nombre,apellido,correo,password,rol) VALUES (?,?,?,?,?,?)",
    ('1000000001','Carlos','Admin','admin@cineworld.com', generate_password_hash('Admin2025!'), 'admin')
)
cur.execute(
    "INSERT OR IGNORE INTO usuarios (documento,nombre,apellido,correo,password,rol) VALUES (?,?,?,?,?,?)",
    ('2000000001','Ana','García','ana@cineworld.com', generate_password_hash('Cliente2025!'), 'cliente')
)
cur.execute(
    "INSERT OR IGNORE INTO usuarios (documento,nombre,apellido,correo,password,rol) VALUES (?,?,?,?,?,?)",
    ('2000000002','Luis','Martínez','luis@cineworld.com', generate_password_hash('Cliente2025!'), 'cliente')
)

# ── Películas ─────────────────────────────────────────
peliculas = [
    ('Dune: Parte Dos','Ciencia Ficción',167,'PG-13',
     'La épica continuación de la saga de Paul Atreides en el planeta Arrakis.',
     'https://image.tmdb.org/t/p/w500/8b8R8l88Qje9dn9OE8PY05Nxl1X.jpg'),
    ('Kung Fu Panda 4','Animación',94,'G',
     'Po regresa en una nueva y emocionante aventura junto a un nuevo compañero.',
     'https://image.tmdb.org/t/p/w500/wkZNPIiPnkLGRxnFdLOdvuP2U4Z.jpg'),
    ('Oppenheimer','Drama',180,'R',
     'La historia del físico J. Robert Oppenheimer y el desarrollo de la bomba atómica.',
     'https://image.tmdb.org/t/p/w500/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg'),
    ('Godzilla vs Kong','Acción',115,'PG-13',
     'Dos titanes legendarios se enfrentan en una batalla que sacudirá al mundo.',
     'https://image.tmdb.org/t/p/w500/pgqgaUx1cJb5oZQQ5v0tNARCeBp.jpg'),
]
for p in peliculas:
    cur.execute(
        "INSERT OR IGNORE INTO peliculas (titulo,genero,duracion,clasificacion,descripcion,imagen_url) VALUES (?,?,?,?,?,?)", p
    )

# ── Salas ─────────────────────────────────────────────
cur.execute("INSERT INTO salas (nombre,capacidad,tipo) VALUES ('Sala 1',120,'Estandar')")
cur.execute("INSERT INTO salas (nombre,capacidad,tipo) VALUES ('Sala 2',80,'VIP')")
cur.execute("INSERT INTO salas (nombre,capacidad,tipo) VALUES ('Sala IMAX',200,'IMAX')")
conn.commit()

# ── Asientos ──────────────────────────────────────────
# Sala 1: 10 filas × 12 columnas
for fila in 'ABCDEFGHIJ':
    for num in range(1, 13):
        cur.execute("INSERT INTO asientos (sala_id,fila,numero) VALUES (1,?,?)", (fila, num))

# Sala 2 VIP: 8 filas × 10 columnas
for fila in 'ABCDEFGH':
    for num in range(1, 11):
        cur.execute("INSERT INTO asientos (sala_id,fila,numero) VALUES (2,?,?)", (fila, num))

# Sala IMAX: 10 filas × 20 columnas
for fila in 'ABCDEFGHIJ':
    for num in range(1, 21):
        cur.execute("INSERT INTO asientos (sala_id,fila,numero) VALUES (3,?,?)", (fila, num))

conn.commit()

# ── Funciones ─────────────────────────────────────────
manana = (date.today() + timedelta(days=1)).isoformat()
pasado = (date.today() + timedelta(days=2)).isoformat()
tres   = (date.today() + timedelta(days=3)).isoformat()

funciones = [
    (1, 3, manana, '14:00', 18000),
    (1, 3, manana, '17:30', 18000),
    (1, 3, manana, '21:00', 18000),
    (2, 1, manana, '15:00', 15000),
    (2, 1, manana, '18:00', 15000),
    (3, 2, manana, '20:00', 22000),
    (4, 1, manana, '16:00', 15000),
    (1, 1, pasado, '15:00', 18000),
    (2, 2, pasado, '17:00', 15000),
    (3, 3, pasado, '19:30', 22000),
    (4, 2, tres,   '20:00', 15000),
]
for f in funciones:
    cur.execute(
        "INSERT INTO funciones (pelicula_id,sala_id,fecha,hora,precio) VALUES (?,?,?,?,?)", f
    )

conn.commit()
conn.close()

print("✓ Base de datos creada: cineworld.db")
print(f"  → {len(peliculas)} películas")
print(f"  → 3 salas (Estándar, VIP, IMAX)")
print(f"  → {10*12 + 8*10 + 10*20} asientos en total")
print(f"  → {len(funciones)} funciones programadas")
print()
print("Credenciales de acceso:")
print("  Admin:   admin@cineworld.com  /  Admin2025!")
print("  Cliente: ana@cineworld.com    /  Cliente2025!")
print()
print("Ejecuta ahora: python app.py")
