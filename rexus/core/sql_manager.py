"""
Gestor de Consultas SQL

Sistema centralizado para cargar y gestionar todas las consultas SQL
desde archivos externos. Garantiza separación completa entre lógica
de negocio y consultas SQL.
"""


import logging
logger = logging.getLogger(__name__)

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
