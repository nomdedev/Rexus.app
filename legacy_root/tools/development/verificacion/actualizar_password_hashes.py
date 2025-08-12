"""
Script para actualizar los hashes de contraseña de todos los usuarios en la base de datos SQL Server.
Si la contraseña está en texto plano, la convierte a SHA-256 y actualiza el campo password_hash.

- Si el campo password_hash ya es un hash SHA-256 válido, lo deja igual.
- Si el campo password_hash es texto plano, lo hashea y actualiza.

Requiere: pyodbc
"""

import hashlib
import re

import pyodbc

# Configura tu conexión aquí
SERVER = "localhost"  # Cambia por tu servidor
DATABASE = "users"  # Cambia por tu base de datos
USER = "sa"  # Cambia por tu usuario
PASSWORD = "mps.1887"  # Cambia por tu contraseña
DRIVER = "ODBC Driver 17 for SQL Server"

# Regex para detectar hash SHA-256
SHA256_REGEX = re.compile(r"^[a-fA-F0-9]{64}$")


def is_sha256(s):
    return bool(SHA256_REGEX.match(s))


def main():
    conn_str = f"DRIVER={{{DRIVER}}};SERVER={SERVER};DATABASE={DATABASE};UID={USER};PWD={PASSWORD}"
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    cursor.execute("SELECT id, usuario, password_hash FROM usuarios")
    users = cursor.fetchall()

    for user in users:
        user_id, username, pwd = user
        if not is_sha256(pwd):
            new_hash = hashlib.sha256(pwd.encode()).hexdigest()
            print(f"Actualizando usuario {username}: {pwd} -> {new_hash}")
            cursor.execute(
                "UPDATE usuarios SET password_hash = ? WHERE id = ?",
                (new_hash, user_id),
            )
    conn.commit()
    print("Actualización completada.")
    conn.close()


if __name__ == "__main__":
    main()
