import os
import sys
import traceback

import pyodbc
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Buscar primero en config/privado/.env, luego fallback a .env en raíz
PRIVADO_DOTENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config', 'privado', '.env'))
ROOT_DOTENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '.env'))
EXAMPLE_DOTENV_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'core', 'config.example.py'))

def cargar_variables_entorno():
    print("\n🔍 Verificando archivo .env en la raíz del proyecto...")
    if os.path.exists(ROOT_DOTENV_PATH):
        print(f"[CHECK] Archivo .env encontrado en: {ROOT_DOTENV_PATH}")
        load_dotenv(dotenv_path=ROOT_DOTENV_PATH, override=True)
        return ROOT_DOTENV_PATH
    else:
        print("[ERROR] No se encontró ningún archivo .env en la raíz!")
        return None

def detectar_driver_odbc():
    print("\n🔌 Detectando controladores ODBC disponibles...")
    drivers = pyodbc.drivers()
    if not drivers:
        print("[ERROR] No se encontraron controladores ODBC. Instale un controlador ODBC para SQL Server.")
        return None

    print(f"Controladores disponibles: {drivers}")

    if "ODBC Driver 18 for SQL Server" in drivers:
        print("[CHECK] Usando: ODBC Driver 18 for SQL Server")
        return "ODBC Driver 18 for SQL Server"
    elif "ODBC Driver 17 for SQL Server" in drivers:
        print("[CHECK] Usando: ODBC Driver 17 for SQL Server")
        return "ODBC Driver 17 for SQL Server"
    elif "SQL Server" in drivers:
        print("[WARN] Usando controlador antiguo: SQL Server (no recomendado)")
        return "SQL Server"
    else:
        print("[ERROR] No se encontró un controlador ODBC compatible para SQL Server")
        return drivers[0] if drivers else None


def verificar_conexion_bd(database_name):
    print(f"\n🔗 Verificando conexión a la base de datos: {database_name}")
    driver = detectar_driver_odbc()
    if not driver:
        return False

    DB_SERVER = os.getenv("DB_SERVER", "")
    DB_USERNAME = os.getenv("DB_USERNAME", "")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")

    if not DB_SERVER:
        print("[ERROR] No se ha configurado la variable DB_SERVER")
        return False

    print(f"Intentando conectar a: {DB_SERVER}, Base de datos: {database_name}")
    print(f"Usando credenciales: Usuario: {DB_USERNAME}, Contraseña: {'*' * len(DB_PASSWORD) if DB_PASSWORD else 'vacía'}")

    conn_str = (
        f"DRIVER={{{driver}}};"
        f"SERVER={DB_SERVER};"
        f"DATABASE={database_name};"
    )
    if DB_USERNAME and DB_PASSWORD:
        conn_str += f"UID={DB_USERNAME};PWD={DB_PASSWORD};"
    else:
        conn_str += "Trusted_Connection=yes;"
    conn_str += "TrustServerCertificate=yes;"

    try:
        conn = pyodbc.connect(conn_str, timeout=10)
        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        row = cursor.fetchone()
        if row:
            version = row[0]
            print(f"[CHECK] Conexión exitosa a SQL Server: {version[:60]}...")
        else:
            print("[CHECK] Conexión exitosa a SQL Server (versión no disponible)")

        cursor.execute("SELECT name FROM sys.databases WHERE name = ?", (database_name,))
        if cursor.fetchone():
            print(f"[CHECK] Base de datos '{database_name}' existe")
        else:
            print(f"[ERROR] La base de datos '{database_name}' no existe")

        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"[ERROR] Error de conexión: {e}")
        print("\nDetalles del error:")
        traceback.print_exc()
        return False

def reparar_configuracion():
    print("\n🔧 Intentando reparar la configuración...")

    # 1. Verificar que existe config.example.py para usar como base
    if not os.path.exists(EXAMPLE_DOTENV_PATH):
        print("[ERROR] No se encontró archivo de ejemplo config.example.py")
        return False

    # 2. Crear .env en ubicación adecuada si no existe
    dotenv_path = PRIVADO_DOTENV_PATH  # Preferimos usar la ubicación privada

    if not os.path.exists(os.path.dirname(dotenv_path)):
        try:
            os.makedirs(os.path.dirname(dotenv_path))
            print(f"[CHECK] Directorio creado: {os.path.dirname(dotenv_path)}")
        except Exception as e:
            print(f"[ERROR] Error al crear directorio: {e}")
            dotenv_path = ROOT_DOTENV_PATH

    # 3. Si no existe .env, crear uno con valores predeterminados
    if not os.path.exists(dotenv_path):
        try:
            with open(dotenv_path, 'w') as f:
                f.write("""# Archivo de configuración de Base de Datos
DB_SERVER=localhost\\SQLEXPRESS
DB_SERVER_ALTERNATE=localhost
DB_USERNAME=sa
DB_PASSWORD=sa123
DB_PORT=1433
DB_DEFAULT_DATABASE=inventario
DB_TIMEOUT=10
DB_MAX_RETRIES=3

# Configuración general
DEBUG_MODE=True
FILE_STORAGE_PATH=./storage
DEFAULT_LANGUAGE=es
DEFAULT_TIMEZONE=UTC-3
NOTIFICATIONS_ENABLED=True
""")
            print(f"[CHECK] Archivo .env creado en: {dotenv_path}")
            print("[WARN] IMPORTANTE: Edite el archivo .env con los valores correctos de su servidor de base de datos")
            return True
        except Exception as e:
            print(f"[ERROR] Error al crear archivo .env: {e}")
            return False
    else:
        print(f"ℹ️ El archivo .env ya existe en: {dotenv_path}")
        print("[WARN] Considere revisar y actualizar los valores de conexión manualmente")
        return False

def sugerir_soluciones(problema):
    print("\n💡 Sugerencias para solucionar el problema:")

    if problema == "driver":
        print("""
1. Instale el controlador ODBC para SQL Server:
   - Para Windows: Microsoft ODBC Driver 17/18 for SQL Server
   - Para Linux: https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server
2. Reinicie la aplicación después de instalar el controlador
""")
    elif problema == "conexion":
        print("""
1. Verifique que el servidor SQL Server esté en funcionamiento
2. Compruebe el nombre del servidor y puerto en el archivo .env
3. Asegúrese de que el firewall permita conexiones al puerto SQL Server (1433 por defecto)
4. Verifique las credenciales de usuario/contraseña
5. Active los protocolos TCP/IP en SQL Server Configuration Manager
6. Reinicie el servicio SQL Server después de hacer cambios
""")
    elif problema == "basedatos":
        print("""
1. Verifique que la base de datos 'inventario' existe en el servidor SQL
2. Si no existe, cree la base de datos ejecutando los scripts en /scripts/db/
3. Asegúrese de que el usuario tiene permisos para acceder a esta base de datos
""")

    print("""
Para actualizar la configuración de conexión:
1. Edite el archivo .env en la carpeta config/privado/ o en la raíz del proyecto
2. Actualice los valores de DB_SERVER, DB_USERNAME, DB_PASSWORD, etc.
3. Reinicie la aplicación
""")

if __name__ == "__main__":
    print("🔎 DIAGNÓSTICO DE CONEXIÓN A BASE DE DATOS")
    print("=" * 60)

    # 1. Verificar archivos de configuración
    config_path = cargar_variables_entorno()

    # 2. Verificar driver ODBC
    driver = detectar_driver_odbc()
    if not driver or "SQL Server" not in driver:
        sugerir_soluciones("driver")

    # 3. Probar conexión a ambas bases
    exito_inventario = verificar_conexion_bd(os.getenv("DB_INVENTARIO", "inventario"))
    exito_users = verificar_conexion_bd(os.getenv("DB_USERS", "users"))

    if not exito_inventario or not exito_users:
        if not config_path:
            reparar_configuracion()
        sugerir_soluciones("conexion")

    print("\n🏁 Diagnóstico finalizado")
