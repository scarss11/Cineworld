from database import query
import random, string

def generar_codigo():
    return 'CW-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

def crear_compra(cliente_id, funcion_id, asientos_ids, precio_unitario):
    total = len(asientos_ids) * float(precio_unitario)
    from database import get_connection
    import psycopg2.extras
    conn = get_connection()
    try:
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            "INSERT INTO compras (cliente_id,funcion_id,total,estado) VALUES (%s,%s,%s,'confirmada') RETURNING id",
            (cliente_id, funcion_id, total)
        )
        compra_id = cur.fetchone()['id']
        for aid in asientos_ids:
            codigo = generar_codigo()
            cur.execute(
                "INSERT INTO tickets (compra_id,asiento_id,codigo,estado) VALUES (%s,%s,%s,'activo')",
                (compra_id, aid, codigo)
            )
        conn.commit()
        return compra_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_by_cliente(cliente_id):
    return query("""
        SELECT c.*, p.titulo, f.fecha, f.hora, s.nombre as sala_nombre,
               COUNT(t.id) as num_tickets
        FROM compras c
        JOIN funciones f ON f.id=c.funcion_id
        JOIN peliculas p ON p.id=f.pelicula_id
        JOIN salas s ON s.id=f.sala_id
        LEFT JOIN tickets t ON t.compra_id=c.id
        WHERE c.cliente_id=%s
        GROUP BY c.id, p.titulo, f.fecha, f.hora, s.nombre
        ORDER BY c.created_at DESC
    """, (cliente_id,), fetchall=True)

def get_tickets_by_cliente(cliente_id):
    return query("""
        SELECT t.*, a.fila, a.numero, p.titulo, f.fecha, f.hora,
               s.nombre as sala_nombre, c.total
        FROM tickets t
        JOIN compras c ON c.id=t.compra_id
        JOIN funciones f ON f.id=c.funcion_id
        JOIN peliculas p ON p.id=f.pelicula_id
        JOIN salas s ON s.id=f.sala_id
        JOIN asientos a ON a.id=t.asiento_id
        WHERE c.cliente_id=%s AND t.estado='activo'
        ORDER BY f.fecha, f.hora
    """, (cliente_id,), fetchall=True)

def get_all():
    return query("""
        SELECT c.*, u.nombre, u.apellido, u.correo, p.titulo,
               f.fecha, f.hora, s.nombre as sala_nombre,
               COUNT(t.id) as num_tickets
        FROM compras c
        JOIN usuarios u ON u.id=c.cliente_id
        JOIN funciones f ON f.id=c.funcion_id
        JOIN peliculas p ON p.id=f.pelicula_id
        JOIN salas s ON s.id=f.sala_id
        LEFT JOIN tickets t ON t.compra_id=c.id
        GROUP BY c.id, u.nombre, u.apellido, u.correo, p.titulo, f.fecha, f.hora, s.nombre
        ORDER BY c.created_at DESC
    """, fetchall=True)

def get_stats():
    hoy = query("""
        SELECT COALESCE(SUM(total),0) as ingresos_hoy, COUNT(*) as ventas_hoy
        FROM compras WHERE DATE(created_at)=CURRENT_DATE AND estado='confirmada'
    """, fetchone=True)
    tickets_hoy = query("""
        SELECT COUNT(*) as tickets_hoy FROM tickets t
        JOIN compras c ON c.id=t.compra_id
        WHERE DATE(c.created_at)=CURRENT_DATE AND c.estado='confirmada'
    """, fetchone=True)
    peliculas_activas = query("SELECT COUNT(*) as total FROM peliculas WHERE activa=1", fetchone=True)
    return {**dict(hoy), **dict(tickets_hoy), **dict(peliculas_activas)}

def get_ventas_por_pelicula():
    return query("""
        SELECT p.titulo, COUNT(t.id) as tickets, COALESCE(SUM(c.total),0) as ingresos
        FROM peliculas p
        LEFT JOIN funciones f ON f.pelicula_id=p.id
        LEFT JOIN compras c ON c.funcion_id=f.id AND c.estado='confirmada'
        LEFT JOIN tickets t ON t.compra_id=c.id
        GROUP BY p.id, p.titulo ORDER BY ingresos DESC
    """, fetchall=True)
