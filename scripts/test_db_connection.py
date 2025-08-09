import os
import pyodbc
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

DB_SERVER = os.getenv("DB_SERVER")
DB_DRIVER = os.getenv("DB_DRIVER")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_USERS = os.getenv("DB_USERS")
DB_INVENTARIO = os.getenv("DB_INVENTARIO")
DB_AUDITORIA = os.getenv("DB_AUDITORIA")

bases = {
    'DB_USERS': DB_USERS,
    'DB_INVENTARIO': DB_INVENTARIO,
    'DB_AUDITORIA': DB_AUDITORIA
}

def test_connection(database):
    print(f"\nProbando conexión a: {database}")
    try:
        conn_str = (
            f"DRIVER={{{DB_DRIVER}}};"
            f"SERVER={DB_SERVER};"
            f"DATABASE={database};"
            f"UID={DB_USERNAME};"
            f"PWD={DB_PASSWORD};"
            f"TrustServerCertificate=yes;"
        )
        safe_password = DB_PASSWORD if DB_PASSWORD else ''
        print(f"String de conexión: {conn_str.replace(safe_password, '******')}")
        conn = pyodbc.connect(conn_str, timeout=5)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        print(f"[CHECK] Conexión exitosa a {database}")
        conn.close()
    except Exception as e:
        print(f"[ERROR] Error conectando a {database}: {e}")

if __name__ == "__main__":
    for nombre, db in bases.items():
        if db:
            test_connection(db)
        else:
            print(f"[WARN] Variable {nombre} no definida en .env")
