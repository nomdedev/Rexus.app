"""
Gestor de Consultas SQL

Este módulo gestiona todas las consultas SQL desde archivos externos
para mejorar la seguridad y mantenibilidad del código.
"""

import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger(__name__)


class SQLQueryManager:
    """Gestor centralizado de consultas SQL desde archivos externos."""

    def __init__(self, sql_base_path: str = None):
        """
        Inicializa el gestor de consultas SQL.

        Args:
            sql_base_path: Ruta base donde se encuentran los archivos SQL
        """
        if sql_base_path is None:
            # Usar la estructura definida en CLAUDE.md: legacy_root/scripts/sql/
            current_dir = Path(__file__).parent.parent.parent
            self.sql_base_path = current_dir / "legacy_root" / "scripts" / "sql"
        else:
            self.sql_base_path = Path(sql_base_path)

        # Cache para consultas cargadas
        self._query_cache = {}

        # Verificar que existe la ruta base
        if not self.sql_base_path.exists():
            raise FileNotFoundError(
                f"Directorio SQL no encontrado: {self.sql_base_path}"
            )

    def get_query(self, module: str, query_name: str, **kwargs) -> str:
        """
        Obtiene una consulta SQL desde archivo.

        Args:
            module: Módulo (inventario, obras, mantenimiento, etc.)
            query_name: Nombre de la consulta (insert_producto, select_all, etc.)
            **kwargs: Parámetros para reemplazar en la consulta

        Returns:
            str: Consulta SQL formateada

        Raises:
            FileNotFoundError: Si no se encuentra el archivo SQL
        """
        # Crear clave de cache
        cache_key = f"{module}.{query_name}"

        # Verificar cache
        if cache_key not in self._query_cache:
            self._load_query(module, query_name)

        # Obtener consulta del cache
        query_template = self._query_cache[cache_key]

        # Reemplazar parámetros si se proporcionan
        if kwargs:
            try:
                return query_template.format(**kwargs)
            except KeyError as e:
                raise ValueError(f"Parámetro faltante en consulta {cache_key}: {e}")

        return query_template

    def _load_query(self, module: str, query_name: str):
        """
        Carga una consulta SQL desde archivo.

        Args:
            module: Módulo
            query_name: Nombre de la consulta
        """
        # Buscar archivo SQL en diferentes ubicaciones posibles
        possible_paths = [
            self.sql_base_path / module / f"{query_name}.sql",
            self.sql_base_path / f"{query_name}.sql",
            self.sql_base_path / "common" / f"{query_name}.sql",
        ]

        query_content = None
        used_path = None

        for path in possible_paths:
            if path.exists():
                used_path = path
                break

        if used_path is None:
            raise FileNotFoundError(
                f"Archivo SQL no encontrado: {query_name}.sql en módulo {module}. "
                f"Rutas buscadas: {[str(p) for p in possible_paths]}"
            )

        # Leer contenido del archivo
        try:
            with open(used_path, "r", encoding="utf-8") as f:
                query_content = f.read().strip()
        except Exception as e:
            raise RuntimeError(f"Error leyendo archivo SQL {used_path}: {e}")

        # Guardar en cache
        cache_key = f"{module}.{query_name}"
        self._query_cache[cache_key] = query_content

        print(f"[SQL_MANAGER] Consulta cargada: {cache_key} desde {used_path}")

    def execute_query(
        self, cursor, module: str, query_name: str, params: tuple = None, **kwargs
    ):
        """
        DEPRECATED: Direct query execution removed for security reasons.
        
        This method has been disabled to prevent arbitrary SQL code execution.
        Use parameterized queries directly in your models instead of loading
        external SQL files for execution.

        Args:
            cursor: Cursor de base de datos
            module: Módulo de la consulta
            query_name: Nombre de la consulta
            params: Parámetros para la consulta
            **kwargs: Parámetros de formateo para la consulta

        Returns:
            False - Method disabled for security
        """
        logger.error(f"SECURITY: Direct query execution disabled for {module}/{query_name}. Use parameterized queries instead.")
        return False

    def list_available_queries(self, module: str = None) -> Dict[str, list]:
        """
        Lista todas las consultas disponibles.

        Args:
            module: Módulo específico (opcional)

        Returns:
            Dict: Diccionario con módulos y sus consultas disponibles
        """
        available = {}

        if module:
            # Listar consultas de un módulo específico
            module_path = self.sql_base_path / module
            if module_path.exists():
                available[module] = [f.stem for f in module_path.glob("*.sql")]
        else:
            # Listar todas las consultas disponibles
            for item in self.sql_base_path.iterdir():
                if item.is_dir():
                    module_name = item.name
                    sql_files = [f.stem for f in item.glob("*.sql")]
                    if sql_files:
                        available[module_name] = sql_files
                elif item.suffix == ".sql":
                    # Archivos SQL en la raíz
                    if "root" not in available:
                        available["root"] = []
                    available["root"].append(item.stem)

        return available

    def validate_query_syntax(self, module: str, query_name: str) -> bool:
        """
        Valida la sintaxis básica de una consulta SQL.

        Args:
            module: Módulo
            query_name: Nombre de la consulta

        Returns:
            bool: True si la sintaxis parece válida
        """
        try:
            query = self.get_query(module, query_name)

            # Validaciones básicas
            query_upper = query.upper().strip()

            # Verificar que no esté vacía
            if not query_upper:
                return False

            # Verificar que sea una consulta SQL válida
            sql_keywords = [
                "SELECT",
                "INSERT",
                "UPDATE",
                "DELETE",
                "CREATE",
                "ALTER",
                "DROP",
            ]
            has_sql_keyword = any(
                query_upper.startswith(keyword) for keyword in sql_keywords
            )

            if not has_sql_keyword:
                return False

            # Verificar balanceado de paréntesis
            if query.count("(") != query.count(")"):
                return False

            return True

        except (AttributeError, TypeError, ValueError):
            return False

    def clear_cache(self):
        """Limpia el cache de consultas."""
        self._query_cache.clear()
        print("[SQL_MANAGER] Cache de consultas limpiado")

    def get_cache_info(self) -> Dict[str, Any]:
        """
        Obtiene información del cache.

        Returns:
            Dict: Información del cache
        """
        return {
            "cached_queries": list(self._query_cache.keys()),
            "cache_size": len(self._query_cache),
            "sql_base_path": str(self.sql_base_path),
        }


# Instancia global del gestor
_sql_manager = None


def get_sql_manager() -> SQLQueryManager:
    """
    Obtiene la instancia global del gestor de consultas SQL.

    Returns:
        SQLQueryManager: Instancia del gestor
    """
    global _sql_manager
    if _sql_manager is None:
        _sql_manager = SQLQueryManager()
    return _sql_manager


def execute_sql_query(
    cursor, module: str, query_name: str, params: tuple = None, **kwargs
):
    """
    Función de conveniencia para ejecutar consultas SQL.

    Args:
        cursor: Cursor de base de datos
        module: Módulo de la consulta
        query_name: Nombre de la consulta
        params: Parámetros para la consulta
        **kwargs: Parámetros de formateo

    Returns:
        Resultado de la ejecución
    """
    manager = get_sql_manager()
    return manager.execute_query(cursor, module, query_name, params, **kwargs)


def get_sql_query(module: str, query_name: str, **kwargs) -> str:
    """
    Función de conveniencia para obtener consultas SQL.

    Args:
        module: Módulo de la consulta
        query_name: Nombre de la consulta
        **kwargs: Parámetros de formateo

    Returns:
        str: Consulta SQL formateada
    """
    manager = get_sql_manager()
    return manager.get_query(module, query_name, **kwargs)
