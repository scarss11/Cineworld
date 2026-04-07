from database import query

def get_by_sala(sala_id):
    return query("SELECT * FROM asientos WHERE sala_id=%s ORDER BY fila, numero", (sala_id,), fetchall=True)

def get_ocupados_funcion(funcion_id):
    return query("""
        SELECT t.asiento_id FROM tickets t
        JOIN compras c ON c.id=t.compra_id
        WHERE c.funcion_id=%s AND c.estado='confirmada' AND t.estado='activo'
    """, (funcion_id,), fetchall=True)

def get_by_id(aid):
    return query("SELECT * FROM asientos WHERE id=%s", (aid,), fetchone=True)
