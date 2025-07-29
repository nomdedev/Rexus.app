#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para corregir problemas específicos en el archivo database.py
Este script busca mejorar el rendimiento, la seguridad y la estructura del código.
"""

import argparse
import logging
import os
import re
import sys
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def setup_argparse():
    parser = argparse.ArgumentParser(description="Corregir problemas en database.py")
    parser.add_argument("--apply", action="store_true", help="Aplicar las correcciones")
    return parser.parse_args()


def read_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        logger.error(f"Error al leer el archivo {file_path}: {e}")
        return None


def write_file(file_path, content):
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        return True
    except Exception as e:
        logger.error(f"Error al escribir el archivo {file_path}: {e}")
        return False


def make_backup(file_path):
    backup_path = f"{file_path}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
    try:
        content = read_file(file_path)
        if content:
            write_file(backup_path, content)
            logger.info(f"Backup creado en {backup_path}")
            return True
    except Exception as e:
        logger.error(f"Error al crear backup: {e}")
    return False


def fix_imports(content):
    """Corrige importaciones en database.py"""
    # Organizar imports estándar primero, luego los de terceros, luego los locales
    # Eliminar imports no utilizados

    imports = []

    # Asegurarse de que todos los imports necesarios estén presentes
    essential_imports = [
        "import os",
        "import logging",
        "import time",
        "from datetime import datetime",
        "import pyodbc",
        "from core.logger import Logger",
        "from core.config import DB_SERVER, DB_USERNAME, DB_PASSWORD",
    ]

    for imp in essential_imports:
        if imp not in content:
            imports.append(imp)

    # Si no se añadieron nuevos imports, no modificamos nada
    if not imports:
        return content

    # Añadimos los imports faltantes al inicio del archivo
    import_block = "\n".join(imports)
    if "import " in content[:200]:  # Verificar si ya hay imports al inicio
        # Insertar después de los imports existentes
        pattern = r"((?:import|from).*?\n)+"
        match = re.search(pattern, content)
        if match:
            end_pos = match.end()
            return content[:end_pos] + import_block + "\n" + content[end_pos:]

    # No hay imports, añadir al inicio
    return import_block + "\n\n" + content


def fix_connection_security(content):
    """Mejora la seguridad de las conexiones"""
    # Añade comprobación de SQL injection en parámetros
    # Mejora manejo de errores en conexiones

    # Verificar si ya está implementado el patrón de seguridad
    if "def sanitize_sql_param" not in content:
        # Añadir función para sanitizar parámetros SQL
        sanitize_function = """
def sanitize_sql_param(param):
    # Sanitiza parámetros SQL para prevenir inyección SQL
    if param is None:
        return None
    if isinstance(param, (int, float)):
        return param

    # Para strings, eliminar caracteres peligrosos
    if isinstance(param, str):
        # Eliminar comentarios SQL
        param = param.replace("--", "")
        # Escapar comillas
        param = param.replace("'", "''")
        # Eliminar terminaciones de sentencia
        param = param.replace(";", "")
    return param
"""
        # Insertar después de las funciones de conexión
        pos = content.find("def get_connection_string")
        if pos != -1:
            end_func = content.find("def ", pos + 10)
            if end_func != -1:
                return content[:end_func] + sanitize_function + content[end_func:]

    return content


def fix_connection_pooling(content):
    """Implementa connection pooling para mejor rendimiento"""
    # Si no existe un sistema de pooling de conexiones, lo añadimos
    if "class ConnectionPool" not in content:
        connection_pool_class = """
class ConnectionPool:
    # Implementa un pool de conexiones para mejorar rendimiento
    _instance = None
    _pools = {}

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = ConnectionPool()
        return cls._instance

    def get_connection(self, database):
        if database not in self._pools:
            self._pools[database] = []

        # Intentar obtener una conexión existente del pool
        if len(self._pools[database]) > 0:
            connection = self._pools[database].pop()
            try:
                # Verificar que la conexión sigue activa
                if connection.connection and not connection.connection.closed:
                    return connection
            except:
                pass  # Si hay error, continuamos para crear una nueva

        # Crear nueva conexión
        if database == "users":
            return UsuariosDatabaseConnection()
        elif database == "auditoria":
            return AuditoriaDatabaseConnection()
        else:
            return InventarioDatabaseConnection()

    def release_connection(self, connection):
        # Devolver la conexión al pool
        database = connection.database
        if database not in self._pools:
            self._pools[database] = []

        # Limitar el tamaño del pool
        if len(self._pools[database]) < 10:  # Máximo 10 conexiones por pool
            self._pools[database].append(connection)
"""
        # Insertar antes de la clase BaseDatabaseConnection
        pos = content.find("class BaseDatabaseConnection")
        if pos != -1:
            return content[:pos] + connection_pool_class + content[pos:]

    return content


def fix_transaction_management(content):
    """Mejora el manejo de transacciones"""
    # Buscar si la función transaction tiene problemas
    transaction_method = """
    def transaction(self, timeout=30, retries=2):
        # Context manager para transacciones seguras con timeout y reintentos.
        # Uso:
        #    with db.transaction(timeout=30, retries=2):
        #        ...
        return self.TransactionContext(self, timeout, retries)
"""

    if transaction_method.strip() in content:
        # La función ya está bien implementada
        return content

    # Buscar y reemplazar la implementación existente si tiene problemas
    pattern = r"def transaction\(self, timeout=\d+, retries=\d+\):.*?return.*?TransactionContext\(.*?\)"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        return content.replace(match.group(0), transaction_method)

    return content


def fix_resource_management(content):
    """Mejora el manejo de recursos (conexiones, cursores)"""
    # Añadir cierre adecuado de recursos

    # Verificar si ya implementa correctamente __enter__ y __exit__
    if (
        "def __enter__(self)" in content
        and "def __exit__(self, exc_type, exc_val, exc_tb)" in content
    ):
        # Ya tiene implementación de context manager
        return content

    # Añadir métodos de context manager a BaseDatabaseConnection
    context_methods = """
    def __enter__(self):
        # Context manager para usar 'with' con conexiones
        if not self.connection:
            self.conectar()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Cierra la conexión al salir del bloque 'with'
        if exc_type:
            # Si hubo excepción, hacer rollback
            try:
                if self.connection and not self.connection.autocommit:
                    self.connection.rollback()
            except:
                pass
        self.cerrar_conexion()
"""

    # Buscar el final de la clase BaseDatabaseConnection
    class_end = content.find("class InventarioDatabaseConnection")
    if class_end == -1:
        # Si no encuentra la siguiente clase, buscar el final del archivo
        class_end = len(content)

    # Encontrar la última definición de método en BaseDatabaseConnection
    last_method = content.rfind("def ", 0, class_end)
    if last_method != -1:
        # Encontrar el final de este método
        method_end = content.find("class ", last_method)
        if method_end == -1 or method_end > class_end:
            method_end = class_end

        # Buscar la última línea no vacía antes de la siguiente clase o función
        pos = method_end - 1
        while pos > 0 and content[pos].isspace():
            pos -= 1

        # Insertar los métodos de context manager
        return content[: pos + 1] + context_methods + content[pos + 1 :]

    return content


def fix_error_handling(content):
    """Mejora el manejo de errores"""
    # Buscar patrones de manejo de errores inconsistentes
    # Y reemplazarlos por un enfoque más centralizado

    # Si no usa un enfoque centralizado para errores de base de datos
    if "def handle_database_error" not in content:
        error_handler = """
    def handle_database_error(self, error, operacion=""):
        # Manejo centralizado de errores de base de datos
        error_msg = f"Error en operación de BD {operacion}: {str(error)}"
        self.logger.error(error_msg)

        if isinstance(error, pyodbc.OperationalError):
            self.logger.log_error_popup(
                DB_CONN_ERROR_DETAIL + str(error)
            )
        elif isinstance(error, pyodbc.IntegrityError):
            self.logger.log_error_popup(
                "Error de integridad de base de datos: " + str(error)
            )
        elif isinstance(error, pyodbc.DataError):
            self.logger.log_error_popup(
                "Error de datos en base de datos: " + str(error)
            )
        else:
            self.logger.log_error_popup(
                DB_QUERY_ERROR_DETAIL + str(error)
            )
"""
        # Insertar después de la función cerrar_conexion
        pos = content.find("def cerrar_conexion")
        if pos != -1:
            end_func = content.find("def ", pos + 10)
            if end_func != -1:
                return content[:end_func] + error_handler + content[end_func:]

    return content


def fix_database_py(file_path, apply_changes=False):
    content = read_file(file_path)
    if not content:
        logger.error(f"No se pudo leer el archivo {file_path}")
        return

    original_content = content

    # Aplicar correcciones
    content = fix_imports(content)
    content = fix_connection_security(content)
    content = fix_connection_pooling(content)
    content = fix_transaction_management(content)
    content = fix_resource_management(content)
    content = fix_error_handling(content)

    # Verificar si se realizaron cambios
    if content != original_content:
        logger.info("Se encontraron problemas que necesitan ser corregidos.")

        if apply_changes:
            # Hacer backup antes de aplicar cambios
            if make_backup(file_path):
                # Aplicar cambios
                if write_file(file_path, content):
                    logger.info(f"Se han aplicado las correcciones a {file_path}")
                else:
                    logger.error(
                        f"No se pudieron aplicar las correcciones a {file_path}"
                    )
        else:
            logger.info("Ejecuta con --apply para aplicar las correcciones.")
    else:
        logger.info("No se encontraron problemas que necesiten ser corregidos.")


def main():
    args = setup_argparse()

    # Buscar el archivo database.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(current_dir, "../.."))
    database_py = os.path.join(root_dir, "core", "database.py")

    if not os.path.exists(database_py):
        logger.error(f"No se encontró el archivo {database_py}")
        return

    # Corregir el archivo
    fix_database_py(database_py, args.apply)


if __name__ == "__main__":
    main()
