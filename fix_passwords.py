"""
Script para actualizar passwords en Supabase con hash correcto.
Ejecutar una sola vez después del primer despliegue.

Uso:
  python fix_passwords.py
"""
from werkzeug.security import generate_password_hash
from database import query

usuarios = [
    ('admin@cineworld.com', 'Admin2025!'),
    ('ana.garcia@gmail.com', 'Cliente2025!'),
    ('luis.martinez@gmail.com', 'Cliente2025!'),
]

for correo, password in usuarios:
    hashed = generate_password_hash(password)
    query("UPDATE usuarios SET password=%s WHERE correo=%s", (hashed, correo), commit=True)
    print(f"✓ Password actualizado: {correo}")

print("\n¡Listo! Passwords actualizados correctamente.")
print("\nCredenciales de prueba:")
print("  Admin:   admin@cineworld.com / Admin2025!")
print("  Cliente: ana.garcia@gmail.com / Cliente2025!")
