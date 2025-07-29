import argparse
import datetime
import sys
from pathlib import Path

import pyodbc

# --- Corrección robusta del path para importar core ---
ROOT_PATH = Path(__file__).parent.parent.parent.resolve()
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))
from core.database import BaseDatabaseConnection, get_connection_string

# Importar las conexiones centralizadas y seguras
MIGRATIONS_DIR = Path(__file__).parent / "migraciones"


def log_migration(message, level="INFO"):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")


def run_migrations():
    # Verificar que existe el directorio
    if not MIGRATIONS_DIR.exists():
        log_migration(
            f"Directorio de migraciones no encontrado: {MIGRATIONS_DIR!s}", "ERROR"
        )
        return False

    # Obtener archivos SQL ordenados
    sql_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    if not sql_files:
        log_migration("No se encontraron scripts de migración.")
        return True

    # Lista de bases de datos permitidas
    bases_permitidas = ["inventario", "users", "auditoria"]

    # Ejecutar migraciones agrupadas por base de datos
    for base in bases_permitidas:
        log_migration(f"Procesando migraciones para base de datos: {base}")
        # Usar la función de conexión centralizada (segura)
        driver = BaseDatabaseConnection.detectar_driver_odbc()
        conn_string = get_connection_string(driver, base)

        try:
            conn = pyodbc.connect(conn_string)
            cursor = conn.cursor()

            # Filtrar archivos para esta base de datos
            base_sql_files = [f for f in sql_files if f"{base}_" in f.name]

            for sql_file in base_sql_files:
                migration_name = sql_file.name
                log_migration(f"Ejecutando migración: {migration_name}")

                # Leer y ejecutar el script de forma segura
                try:
                    with sql_file.open(encoding="utf-8") as f:
                        sql_content = f.read()

                    # Dividir por GO si hay batches
                    statements = sql_content.split("GO")
                    for statement in statements:
                        if statement.strip():
                            cursor.execute(statement)

                    conn.commit()
                    log_migration(
                        f"✓ Migración aplicada correctamente: {migration_name}"
                    )
                except pyodbc.Error as e:
                    conn.rollback()
                    log_migration(
                        f"✗ Error en migración {migration_name}: {e!r}", "ERROR"
                    )
                    raise
                except Exception as e:
                    conn.rollback()
                    log_migration(
                        f"✗ Error inesperado en migración {migration_name}: {e!r}",
                        "ERROR",
                    )
                    raise

            conn.close()
            log_migration(f"Completadas migraciones para {base}")

        except pyodbc.Error as e:
            log_migration(f"Error en base de datos {base}: {e!r}", "ERROR")
            return False
        except Exception as e:
            log_migration(f"Error inesperado en base de datos {base}: {e!r}", "ERROR")
            return False

    log_migration("Todas las migraciones aplicadas correctamente.")
    return True


if __name__ == "__main__":
    try:
        # Verificar argumentos de línea de comandos
        parser = argparse.ArgumentParser(
            description="Ejecuta migraciones de base de datos"
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Muestra las migraciones sin ejecutarlas",
        )
        parser.add_argument(
            "--base",
            choices=["all", "inventario", "users", "auditoria"],
            default="all",
            help="Especifica la base de datos para migrar",
        )
        args = parser.parse_args()

        if args.dry_run:
            log_migration(
                "Modo simulación (dry-run) - No se ejecutarán las migraciones realmente"
            )
            # Aquí podrías implementar la lógica para mostrar qué migraciones se ejecutarían
        else:
            success = run_migrations()
            if success:
                log_migration("Proceso de migración completado correctamente")
                sys.exit(0)
            else:
                log_migration("Proceso de migración falló", "ERROR")
                sys.exit(1)
    except Exception as e:
        log_migration(f"Error inesperado: {str(e)}", "ERROR")
        sys.exit(1)
