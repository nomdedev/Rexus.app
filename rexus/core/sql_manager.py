"""
Gestor de Consultas SQL

Sistema centralizado para cargar y gestionar todas las consultas SQL
desde archivos externos. Garantiza separación completa entre lógica
de negocio y consultas SQL.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class SQLManager:
    """Gestor centralizado de consultas SQL externas."""

    def __init__(self, sql_base_path: str = None):
        """
        Inicializa el gestor de SQL.

        Args:
            sql_base_path: Ruta base donde están los archivos SQL
        """
        if sql_base_path is None:
            # Obtener ruta base del proyecto
            project_root = Path(__file__).parent.parent.parent
            sql_base_path = project_root / "sql"

        self.sql_base_path = Path(sql_base_path)
        self._queries_cache = {}
        self._load_all_queries()

    def _load_all_queries(self):
        """Carga todas las consultas SQL en memoria."""
        try:
            if not self.sql_base_path.exists():
                print(f"[WARNING] Directorio SQL no encontrado: {self.sql_base_path}")
                return

            # Cargar consultas por módulo
            for module_dir in self.sql_base_path.iterdir():
                if module_dir.is_dir():
                    module_name = module_dir.name
                    self._queries_cache[module_name] = {}

                    # Cargar archivos .sql del módulo
                    for sql_file in module_dir.glob("*.sql"):
                        query_name = sql_file.stem
                        try:
                            with open(sql_file, "r", encoding="utf-8") as f:
                                query_content = f.read().strip()
                                self._queries_cache[module_name][query_name] = (
                                    query_content
                                )
                                print(
                                    f"[SQL_MANAGER] Cargada consulta: {module_name}.{query_name}"
                                )
                        except Exception as e:
                            print(f"[ERROR] Error cargando {sql_file}: {e}")

            print(
                f"[SQL_MANAGER] Cargadas {sum(len(queries) for queries in self._queries_cache.values())} consultas"
            )

        except Exception as e:
            print(f"[ERROR SQL_MANAGER] Error cargando consultas: {e}")

    def get_query(self, module: str, query_name: str, **params) -> Optional[str]:
        """
        Obtiene una consulta SQL del módulo especificado.

        Args:
            module: Nombre del módulo (ej: 'mantenimiento', 'inventario')
            query_name: Nombre de la consulta (ej: 'obtener_equipos', 'crear_equipo')
            **params: Parámetros para reemplazar en la consulta (ej: table_name='equipos')

        Returns:
            Consulta SQL formateada o None si no se encuentra
        """
        try:
            if module not in self._queries_cache:
                print(f"[ERROR] Módulo SQL no encontrado: {module}")
                return None

            if query_name not in self._queries_cache[module]:
                print(f"[ERROR] Consulta SQL no encontrada: {module}.{query_name}")
                return None

            query = self._queries_cache[module][query_name]

            # Reemplazar parámetros de tabla si se proporcionan
            if params:
                try:
                    query = query.format(**params)
                except KeyError as e:
                    print(
                        f"[ERROR] Parámetro faltante en consulta {module}.{query_name}: {e}"
                    )
                    return None

            return query

        except Exception as e:
            print(f"[ERROR] Error obteniendo consulta {module}.{query_name}: {e}")
            return None

    def list_queries(self, module: str = None) -> Dict[str, Any]:
        """
        Lista todas las consultas disponibles.

        Args:
            module: Módulo específico a listar (opcional)

        Returns:
            Diccionario con las consultas disponibles
        """
        if module:
            return {module: list(self._queries_cache.get(module, {}).keys())}

        return {
            mod: list(queries.keys()) for mod, queries in self._queries_cache.items()
        }

    def reload_queries(self):
        """Recarga todas las consultas SQL."""
        self._queries_cache.clear()
        self._load_all_queries()

    def validate_query_params(self, query: str, required_params: list) -> bool:
        """
        Valida que una consulta tenga todos los parámetros requeridos.

        Args:
            query: Consulta SQL
            required_params: Lista de parámetros requeridos

        Returns:
            True si todos los parámetros están presentes
        """
        for param in required_params:
            if f"{{{param}}}" not in query:
                return False
        return True


# Instancia global del gestor SQL
_sql_manager_instance = None


def get_sql_manager() -> SQLManager:
    """Obtiene la instancia global del gestor SQL."""
    global _sql_manager_instance
    if _sql_manager_instance is None:
        _sql_manager_instance = SQLManager()
    return _sql_manager_instance


def get_query(module: str, query_name: str, **params) -> Optional[str]:
    """
    Función de conveniencia para obtener consultas SQL.

    Args:
        module: Nombre del módulo
        query_name: Nombre de la consulta
        **params: Parámetros para la consulta

    Returns:
        Consulta SQL formateada
    """
    return get_sql_manager().get_query(module, query_name, **params)
