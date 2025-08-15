"""
Utilidades de seguridad SQL para Rexus.app

Proporciona funciones para prevenir SQL injection y validar consultas SQL
de manera segura.
"""

import re
from typing import List, Set


class SQLSecurityError(Exception):
    """Excepción lanzada cuando se detecta un problema de seguridad SQL."""


def validate_column_names(columns: str) -> bool:
    """Valida nombres de columnas para prevenir SQL injection."""
    if not columns or columns == "*":
        return True
    
    # Patrón para nombres válidos de columnas (alfanuméricos, underscore, punto)
    column_pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*(\.[a-zA-Z_][a-zA-Z0-9_]*)?$'
    
    # Dividir por comas y validar cada columna
    column_list = [col.strip() for col in columns.split(',')]
    
    for column in column_list:
        if not re.match(column_pattern, column):
            return False
    
    return True



# Lista blanca de tablas permitidas en el sistema
ALLOWED_TABLES: Set[str] = {
    # Módulo usuarios
    "usuarios",
    "roles",
    "permisos",
    "usuario_roles",
    "rol_permisos",
    # Módulo inventario
    "productos",
    "categorias",
    "stock",
    "movimientos_stock",
    "ubicaciones",
    "alertas_stock",
    "reservas",
    "transferencias",
    # Módulo obras
    "obras",
    "clientes",
    "presupuestos",
    "cronogramas",
    "actividades",
    "asignaciones",
    "materiales_obra",
    "estado_obra",
    # Módulo herrajes
    "herrajes",
    "tipos_herraje",
    "proveedores",
    "caracteristicas_herraje",
    "herrajes_stock",
    "herrajes_movimientos",
    # Módulo vidrios
    "vidrios",
    "tipos_vidrio",
    "medidas",
    "vidrios_stock",
    "cortes",
    "tratamientos",
    "calidades",
    # Módulo compras
    "compras",
    "pedidos",
    "proveedores_compras",
    "detalle_pedidos",
    "ordenes_compra",
    "recepciones",
    "facturas_compra",
    # Módulo mantenimiento
    "equipos",
    "herramientas",
    "mantenimientos",
    "programacion_mantenimiento",
    "tipos_mantenimiento",
    "estado_equipos",
    "historial_mantenimiento",
    # Módulo logística
    "transportes",
    "entregas",
    "detalle_entregas",
    "rutas",
    "conductores",
    "vehiculos",
    "costos_transporte",
    # Módulo administración
    "empleados",
    "departamentos",
    "cargos",
    "nominas",
    "asistencias",
    "contabilidad",
    "cuentas",
    "transacciones",
    "presupuestos_admin",
    # Módulo configuración
    "configuracion",
    "parametros_sistema",
    "configuracion_modulos",
    "logs_sistema",
    "backups",
    # Módulo auditoría
    "auditoria",
    "logs_acceso",
    "logs_operaciones",
    "logs_errores",
    "sesiones_usuario",
    "intentos_login",
    # Tablas del sistema
    "sysobjects",
    "information_schema",
    "sys",
}


def validate_table_name(table_name: str) -> str:
    """
    Valida que el nombre de tabla sea seguro y esté en la lista blanca.

    Args:
        table_name (str): Nombre de tabla a validar

    Returns:
        str: Nombre de tabla validado

    Raises:
        SQLSecurityError: Si el nombre de tabla no es válido o no está permitido
    """
    if not table_name:
        raise SQLSecurityError("Nombre de tabla vacío")

    # Eliminar espacios en blanco
    table_name = table_name.strip()

    # Verificar caracteres peligrosos
    dangerous_patterns = [
        r"[;'\"\-\-/\*\+]",  # Caracteres SQL peligrosos
        r"\b(DROP|DELETE|INSERT|UPDATE|ALTER|CREATE|EXEC|EXECUTE)\b",  # Comandos SQL
        r"\b(UNION|SELECT|WHERE|FROM)\b",  # Palabras clave SELECT
        r"[<>]",  # Caracteres HTML/XML
        r"\\\w+",  # Secuencias de escape
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, table_name, re.IGNORECASE):
            raise SQLSecurityError(f"Patrón peligroso detectado en tabla: {table_name}")

    # Verificar que solo contenga caracteres alfanuméricos y guiones bajos
    if not re.match(r"^[a-zA-Z0-9_]+$", table_name):
        raise SQLSecurityError(
            f"Nombre de tabla contiene caracteres no válidos: {table_name}"
        )

    # Verificar longitud razonable
    if len(table_name) > 64:
        raise SQLSecurityError(f"Nombre de tabla demasiado largo: {table_name}")

    # Verificar que esté en la lista blanca
    if table_name.lower() not in ALLOWED_TABLES:
        raise SQLSecurityError(f"Tabla no permitida: {table_name}")

    return table_name.lower()


def sanitize_sql_parameter(value: str) -> str:
    """
    Sanitiza un parámetro SQL eliminando caracteres peligrosos.

    Args:
        value (str): Valor a sanitizar

    Returns:
        str: Valor sanitizado
    """
    if not isinstance(value, str):
        return str(value)

    # Eliminar caracteres peligrosos
    dangerous_chars = ["'", '"', ";", "--", "/*", "*/", "\\", "<", ">"]
    sanitized = value

    for char in dangerous_chars:
        sanitized = sanitized.replace(char, "")

    return sanitized.strip()


def build_safe_query(template: str, table_name: str, **kwargs) -> str:
    """
    Construye una consulta SQL segura usando plantillas.

    Args:
        template (str): Plantilla de consulta con marcadores de posición
        table_name (str): Nombre de tabla a validar
        **kwargs: Parámetros adicionales para la plantilla

    Returns:
        str: Consulta SQL segura

    Raises:
        SQLSecurityError: Si hay problemas de seguridad
    """
    # Validar nombre de tabla
    safe_table = validate_table_name(table_name)

    # Sanitizar parámetros adicionales
    safe_params = {}
    for key, value in kwargs.items():
        if isinstance(value, str):
            safe_params[key] = sanitize_sql_parameter(value)
        else:
            safe_params[key] = value

    try:
        # Construir consulta segura
        safe_query = template.format(table=safe_table, **safe_params)
        return safe_query
    except KeyError as e:
        raise SQLSecurityError(f"Parámetro faltante en plantilla: {e}")


class SQLQueryBuilder:
    """Constructor de consultas SQL seguras."""

    @staticmethod
    def select(
        table_name: str, columns: List[str] = None, where_clause: str = None
    ) -> str:
        """
        Construye una consulta SELECT segura.

        Args:
            table_name (str): Nombre de tabla
            columns (List[str]): Lista de columnas (opcional, * si es None)
            where_clause (str): Cláusula WHERE (opcional)

        Returns:
            str: Consulta SELECT segura
        """
        safe_table = validate_table_name(table_name)

        if columns:
            # Validar nombres de columnas
            safe_columns = []
            for col in columns:
                if not re.match(r"^[a-zA-Z0-9_]+$", col):
                    raise SQLSecurityError(f"Nombre de columna no válido: {col}")
                safe_columns.append(col)
            columns_str = ", ".join(safe_columns)
        else:
            columns_str = "*"

        query = f"SELECT {columns_str} FROM [{safe_table}]"

        if where_clause:
            # Validar cláusula WHERE básica (sin parámetros dinámicos)
            if any(
                dangerous in where_clause.upper()
                for dangerous in ["DROP", "DELETE", "INSERT", "UPDATE"]
            ):
                raise SQLSecurityError("Cláusula WHERE contiene comandos peligrosos")
            query += f" WHERE {where_clause}"

        return query

    @staticmethod
    def insert(table_name: str, columns: List[str]) -> str:
        """
        Construye una consulta INSERT segura con placeholders.

        Args:
            table_name (str): Nombre de tabla
            columns (List[str]): Lista de columnas

        Returns:
            str: Consulta INSERT segura con placeholders
        """
        safe_table = validate_table_name(table_name)

        # Validar nombres de columnas
        safe_columns = []
        for col in columns:
            if not re.match(r"^[a-zA-Z0-9_]+$", col):
                raise SQLSecurityError(f"Nombre de columna no válido: {col}")
            safe_columns.append(col)

        columns_str = ", ".join(safe_columns)
        placeholders = ", ".join(["?" for _ in safe_columns])

        return f"INSERT INTO [{safe_table}] ({columns_str}) VALUES ({placeholders})"

    @staticmethod
    def update(
        table_name: str, columns: List[str], where_condition: str = "id = ?"
    ) -> str:
        """
        Construye una consulta UPDATE segura con placeholders.

        Args:
            table_name (str): Nombre de tabla
            columns (List[str]): Lista de columnas a actualizar
            where_condition (str): Condición WHERE con placeholder

        Returns:
            str: Consulta UPDATE segura con placeholders
        """
        safe_table = validate_table_name(table_name)

        # Validar nombres de columnas
        safe_columns = []
        for col in columns:
            if not re.match(r"^[a-zA-Z0-9_]+$", col):
                raise SQLSecurityError(f"Nombre de columna no válido: {col}")
            safe_columns.append(f"{col} = ?")

        set_clause = ", ".join(safe_columns)

        return f"UPDATE [{safe_table}] SET {set_clause} WHERE {where_condition}"

    @staticmethod
    def delete(table_name: str, where_condition: str = "id = ?") -> str:
        """
        Construye una consulta DELETE segura con placeholders.

        Args:
            table_name (str): Nombre de tabla
            where_condition (str): Condición WHERE con placeholder

        Returns:
            str: Consulta DELETE segura con placeholders
        """
        safe_table = validate_table_name(table_name)
        return f"DELETE FROM [{safe_table}] WHERE {where_condition}"


# Funciones de conveniencia
def get_allowed_tables() -> Set[str]:
    """Retorna el conjunto de tablas permitidas."""
    return ALLOWED_TABLES.copy()


def add_allowed_table(table_name: str) -> None:
    """
    Agrega una tabla a la lista de tablas permitidas.

    Args:
        table_name (str): Nombre de tabla a agregar
    """
    if not re.match(r"^[a-zA-Z0-9_]+$", table_name):
        raise SQLSecurityError(f"Nombre de tabla no válido: {table_name}")

    ALLOWED_TABLES.add(table_name.lower())


def remove_allowed_table(table_name: str) -> None:
    """
    Remueve una tabla de la lista de tablas permitidas.

    Args:
        table_name (str): Nombre de tabla a remover
    """
    ALLOWED_TABLES.discard(table_name.lower())


class SQLSecurityValidator:
    """Validador de seguridad SQL."""

    @staticmethod
    def validate_query(query: str) -> bool:
        """Valida una consulta SQL por seguridad."""
        if not query or not isinstance(query, str):
            return False

        # Verificar patrones peligrosos
        dangerous_patterns = [
            r';\s*(drop|delete|truncate|alter)',
            r'union\s+select',
            r'exec\s*\(',
            r'sp_\w+',
            r'xp_\w+'
        ]

        query_lower = query.lower()
        for pattern in dangerous_patterns:
            if re.search(pattern, query_lower):
                return False

        return True

    @staticmethod
    def sanitize_input(input_value: str) -> str:
        """Sanitiza entrada de usuario."""
        if not isinstance(input_value, str):
            return str(input_value)

        # Escapar comillas y caracteres peligrosos
        sanitized = input_value.replace("'", "''")
        sanitized = re.sub(r'[;\-\-\/\*]', '', sanitized)

        return sanitized


class SecureSQLBuilder:
    """Constructor seguro de consultas SQL."""

    def __init__(self):
        self.query_parts = []
        self.parameters = []

    def select(self, columns: str = "*"):
        """Agrega SELECT a la consulta."""
        if not validate_column_names(columns):
            raise SQLSecurityError(f"Nombres de columnas inválidos: {columns}")

        self.query_parts.append(f"SELECT {columns}")
        return self

    def from_table(self, table: str):
        """Agrega FROM a la consulta."""
        if not validate_table_name(table):
            raise SQLSecurityError(f"Nombre de tabla inválido: {table}")

        self.query_parts.append(f"FROM {table}")
        return self

    def where(self, condition: str, *params):
        """Agrega WHERE con parámetros seguros."""
        self.query_parts.append(f"WHERE {condition}")
        self.parameters.extend(params)
        return self

    def build(self) -> tuple:
        """Construye la consulta final."""
        query = " ".join(self.query_parts)
        return query, tuple(self.parameters)
