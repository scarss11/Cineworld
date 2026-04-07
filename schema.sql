-- ═══════════════════════════════════════════════════
--  CineWorld — Schema completo para Supabase
--  Ejecutar en: Supabase > SQL Editor
-- ═══════════════════════════════════════════════════

-- Usuarios del sistema
CREATE TABLE IF NOT EXISTS usuarios (
  id SERIAL PRIMARY KEY,
  documento VARCHAR(15) UNIQUE NOT NULL,
  nombre VARCHAR(80) NOT NULL,
  apellido VARCHAR(80) NOT NULL,
  telefono VARCHAR(20),
  correo VARCHAR(100) UNIQUE NOT NULL,
  password VARCHAR(255) NOT NULL,
  rol VARCHAR(20) NOT NULL CHECK (rol IN ('cliente','admin')),
  activo SMALLINT DEFAULT 1,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Películas
CREATE TABLE IF NOT EXISTS peliculas (
  id SERIAL PRIMARY KEY,
  titulo VARCHAR(150) NOT NULL,
  genero VARCHAR(80),
  duracion INT,
  clasificacion VARCHAR(10),
  descripcion TEXT,
  imagen_url VARCHAR(255),
  activa SMALLINT DEFAULT 1,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Salas del cine
CREATE TABLE IF NOT EXISTS salas (
  id SERIAL PRIMARY KEY,
  nombre VARCHAR(50) NOT NULL,
  capacidad INT NOT NULL,
  tipo VARCHAR(30) DEFAULT 'Estandar'
);

-- Funciones (película + sala + fecha/hora)
CREATE TABLE IF NOT EXISTS funciones (
  id SERIAL PRIMARY KEY,
  pelicula_id INT NOT NULL REFERENCES peliculas(id),
  sala_id INT NOT NULL REFERENCES salas(id),
  fecha DATE NOT NULL,
  hora TIME NOT NULL,
  precio DECIMAL(10,2) NOT NULL,
  activa SMALLINT DEFAULT 1
);

-- Asientos por sala
CREATE TABLE IF NOT EXISTS asientos (
  id SERIAL PRIMARY KEY,
  sala_id INT NOT NULL REFERENCES salas(id),
  fila VARCHAR(5) NOT NULL,
  numero INT NOT NULL
);

-- Compras
CREATE TABLE IF NOT EXISTS compras (
  id SERIAL PRIMARY KEY,
  cliente_id INT NOT NULL REFERENCES usuarios(id),
  funcion_id INT NOT NULL REFERENCES funciones(id),
  total DECIMAL(10,2) NOT NULL,
  estado VARCHAR(20) DEFAULT 'confirmada' CHECK (estado IN ('confirmada','cancelada')),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Tickets (uno por asiento)
CREATE TABLE IF NOT EXISTS tickets (
  id SERIAL PRIMARY KEY,
  compra_id INT NOT NULL REFERENCES compras(id),
  asiento_id INT NOT NULL REFERENCES asientos(id),
  codigo VARCHAR(20) UNIQUE NOT NULL,
  estado VARCHAR(20) DEFAULT 'activo' CHECK (estado IN ('activo','usado','cancelado'))
);

-- ═══════════════════════════════════════════════════
--  Datos de prueba
-- ═══════════════════════════════════════════════════

-- Usuarios (passwords se actualizan con fix_passwords.py)
INSERT INTO usuarios (documento, nombre, apellido, correo, password, rol) VALUES
  ('1000000001', 'Carlos', 'Admin',    'admin@cineworld.com',         'temporal', 'admin'),
  ('2000000001', 'Ana',    'García',   'ana.garcia@gmail.com',        'temporal', 'cliente'),
  ('2000000002', 'Luis',   'Martínez', 'luis.martinez@gmail.com',     'temporal', 'cliente')
ON CONFLICT DO NOTHING;

-- Películas
INSERT INTO peliculas (titulo, genero, duracion, clasificacion, descripcion, imagen_url) VALUES
  ('Dune: Parte Dos',   'Ciencia Ficción', 167, 'PG-13', 'La épica continuación de la saga de Paul Atreides en Arrakis.',
   'https://image.tmdb.org/t/p/w500/8b8R8l88Qje9dn9OE8PY05Nxl1X.jpg'),
  ('Kung Fu Panda 4',   'Animación',        94, 'G',     'Po regresa en una nueva y emocionante aventura.',
   'https://image.tmdb.org/t/p/w500/wkZNPIiPnkLGRxnFdLOdvuP2U4Z.jpg'),
  ('Godzilla vs Kong',  'Acción',          115, 'PG-13', 'Dos titanes se enfrentan en una batalla épica.',
   'https://image.tmdb.org/t/p/w500/pgqgaUx1cJb5oZQQ5v0tNARCeBp.jpg'),
  ('Oppenheimer',       'Drama',           180, 'R',     'La historia del creador de la bomba atómica.',
   'https://image.tmdb.org/t/p/w500/8Gxv8gSFCU0XGDykEGv7zR1n2ua.jpg')
ON CONFLICT DO NOTHING;

-- Salas
INSERT INTO salas (nombre, capacidad, tipo) VALUES
  ('Sala 1',    120, 'Estandar'),
  ('Sala 2',     80, 'VIP'),
  ('Sala IMAX', 200, 'IMAX')
ON CONFLICT DO NOTHING;

-- Asientos Sala 1 (10 filas × 12 asientos)
DO $$
DECLARE
  sala_id INT;
  filas TEXT[] := ARRAY['A','B','C','D','E','F','G','H','I','J'];
  fila TEXT;
  num INT;
BEGIN
  SELECT id INTO sala_id FROM salas WHERE nombre = 'Sala 1' LIMIT 1;
  IF sala_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM asientos WHERE sala_id = sala_id LIMIT 1) THEN
    FOREACH fila IN ARRAY filas LOOP
      FOR num IN 1..12 LOOP
        INSERT INTO asientos (sala_id, fila, numero) VALUES (sala_id, fila, num);
      END LOOP;
    END LOOP;
  END IF;
END $$;

-- Asientos Sala 2 (8 filas × 10 asientos)
DO $$
DECLARE
  sala_id INT;
  filas TEXT[] := ARRAY['A','B','C','D','E','F','G','H'];
  fila TEXT;
  num INT;
BEGIN
  SELECT id INTO sala_id FROM salas WHERE nombre = 'Sala 2' LIMIT 1;
  IF sala_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM asientos WHERE sala_id = sala_id LIMIT 1) THEN
    FOREACH fila IN ARRAY filas LOOP
      FOR num IN 1..10 LOOP
        INSERT INTO asientos (sala_id, fila, numero) VALUES (sala_id, fila, num);
      END LOOP;
    END LOOP;
  END IF;
END $$;

-- Funciones de prueba (ajusta las fechas si es necesario)
INSERT INTO funciones (pelicula_id, sala_id, fecha, hora, precio)
SELECT p.id, s.id, CURRENT_DATE + 1, '15:00', 18000
FROM peliculas p, salas s WHERE p.titulo = 'Dune: Parte Dos' AND s.nombre = 'Sala IMAX'
ON CONFLICT DO NOTHING;

INSERT INTO funciones (pelicula_id, sala_id, fecha, hora, precio)
SELECT p.id, s.id, CURRENT_DATE + 1, '18:30', 15000
FROM peliculas p, salas s WHERE p.titulo = 'Kung Fu Panda 4' AND s.nombre = 'Sala 1'
ON CONFLICT DO NOTHING;

INSERT INTO funciones (pelicula_id, sala_id, fecha, hora, precio)
SELECT p.id, s.id, CURRENT_DATE + 1, '20:00', 22000
FROM peliculas p, salas s WHERE p.titulo = 'Oppenheimer' AND s.nombre = 'Sala 2'
ON CONFLICT DO NOTHING;

INSERT INTO funciones (pelicula_id, sala_id, fecha, hora, precio)
SELECT p.id, s.id, CURRENT_DATE + 2, '16:00', 18000
FROM peliculas p, salas s WHERE p.titulo = 'Godzilla vs Kong' AND s.nombre = 'Sala 1'
ON CONFLICT DO NOTHING;
