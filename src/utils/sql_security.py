"""
Utilidades de Seguridad SQL para Rexus.app

Este módulo proporciona funciones y clases para prevenir vulnerabilidades
de SQL injection en todo el proyecto.
"""

import os
import re
from typing import Set, Dict, Any, List, Optional
from pathlib import Path


class SQLSecurityError(Exception):
    """Excepción personalizada para errores de seguridad SQL."""
    pass


class SQLSecurityValidator:
    """
    Validador de seguridad SQL que proporciona funciones para validar
    nombres de tablas, columnas y otros elementos SQL.
    """
    
    def __init__(self):
        """Inicializa el validador con las configuraciones por defecto."""
        # Definir todas las tablas permitidas en el sistema
        self._global_allowed_tables: Set[str] = {
            # Tablas principales
            "inventario_perfiles",
            "inventario",
            "herrajes", 
            "vidrios",
            "obras",
            "usuarios",
            "pedidos",
            "compras",
            
            # Tablas de relaciones
            "herrajes_obra",
            "vidrios_obra", 
            "pedidos_vidrios",
            "pedidos_herrajes",
            "obras_materiales",
            
            # Tablas de historial y auditoría
            "historial",
            "reserva_materiales",
            "movimientos_inventario",
            "auditoria_cambios",
            "log_acciones",
            
            # Tablas de configuración
            "configuracion_sistema",
            "permisos_usuario",
            "roles",
            "modulos_sistema",
            
            # Tablas de logística
            "transportes",
            "rutas_entrega",
            "proveedores",
            "clientes",
            
            # Tablas de administración
            "facturacion",
            "contabilidad",
            "recursos_humanos",
            "empleados",
            "departamentos",
            
            # Tablas de mantenimiento
            "mantenimiento_equipos",
            "calendario_mantenimiento",
            "reportes_incidencias",
        }
        
        # Patrones de nombres válidos (solo letras, números y guiones bajos)
        self._valid_identifier_pattern = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')
        
    def validate_table_name(self, table_name: str, allowed_tables: Optional[Set[str]] = None) -> str:
        """
        Valida que un nombre de tabla esté en la lista de tablas permitidas.
        
        Args:
            table_name: Nombre de la tabla a validar
            allowed_tables: Conjunto opcional de tablas permitidas. Si no se proporciona,
                          usa el conjunto global.
        
        Returns:
            str: El nombre de tabla validado
            
        Raises:
            SQLSecurityError: Si el nombre de tabla no está permitido
        """
        if not table_name:
            raise SQLSecurityError("Table name cannot be empty")
            
        # Usar tablas permitidas específicas o las globales
        permitted_tables = allowed_tables or self._global_allowed_tables
        
        # Verificar patrón de nombre válido
        if not self._valid_identifier_pattern.match(table_name):
            raise SQLSecurityError(
                f"Invalid table name pattern: '{table_name}'. "
                "Only letters, numbers and underscores are allowed."
            )
            
        # Verificar que la tabla esté en la lista permitida
        if table_name not in permitted_tables:
            raise SQLSecurityError(
                f"Table name '{table_name}' not allowed. "
                f"Permitted tables: {sorted(permitted_tables)}"
            )
            
        return table_name
    
    def validate_column_name(self, column_name: str) -> str:
        """
        Valida que un nombre de columna tenga un formato válido.
        
        Args:
            column_name: Nombre de la columna a validar
            
        Returns:
            str: El nombre de columna validado
            
        Raises:
            SQLSecurityError: Si el nombre de columna no es válido
        """
        if not column_name:
            raise SQLSecurityError("Column name cannot be empty")
            
        if not self._valid_identifier_pattern.match(column_name):
            raise SQLSecurityError(
                f"Invalid column name pattern: '{column_name}'. "
                "Only letters, numbers and underscores are allowed."
            )
            
        return column_name
    
    def validate_sql_identifier(self, identifier: str) -> str:
        """
        Valida que un identificador SQL (tabla, columna, etc.) sea seguro.
        
        Args:
            identifier: Identificador a validar
            
        Returns:
            str: El identificador validado
            
        Raises:
            SQLSecurityError: Si el identificador no es válido
        """
        if not identifier:
            raise SQLSecurityError("SQL identifier cannot be empty")
            
        if not self._valid_identifier_pattern.match(identifier):
            raise SQLSecurityError(
                f"Invalid SQL identifier: '{identifier}'. "
                "Only letters, numbers and underscores are allowed."
            )
            
        # Verificar que no contenga palabras reservadas peligrosas
        dangerous_keywords = {
            'drop', 'delete', 'truncate', 'alter', 'create', 
            'insert', 'update', 'exec', 'execute', 'union',
            'script', 'javascript', 'vbscript'
        }
        
        if identifier.lower() in dangerous_keywords:
            raise SQLSecurityError(
                f"SQL identifier '{identifier}' contains dangerous keyword"
            )
            
        return identifier
    
    def add_allowed_table(self, table_name: str) -> None:
        """
        Añade una nueva tabla a la lista de tablas permitidas globalmente.
        
        Args:
            table_name: Nombre de la tabla a añadir
        """
        validated_name = self.validate_sql_identifier(table_name)
        self._global_allowed_tables.add(validated_name)
    
    def get_allowed_tables(self) -> Set[str]:
        """
        Retorna el conjunto de tablas permitidas.
        
        Returns:
            Set[str]: Conjunto de nombres de tablas permitidas
        """
        return self._global_allowed_tables.copy()


class SecureSQLBuilder:
    """
    Constructor de consultas SQL seguras que utiliza validación de nombres
    y preparación de parámetros.
    """
    
    def __init__(self, validator: Optional[SQLSecurityValidator] = None):
        """
        Inicializa el constructor SQL seguro.
        
        Args:
            validator: Validador de seguridad SQL. Si no se proporciona, crea uno nuevo.
        """
        self.validator = validator or SQLSecurityValidator()
    
    def build_select_query(
        self, 
        table_name: str, 
        columns: Optional[List[str]] = None,
        where_conditions: Optional[List[str]] = None,
        order_by: Optional[str] = None,
        allowed_tables: Optional[Set[str]] = None
    ) -> str:
        """
        Construye una consulta SELECT segura.
        
        Args:
            table_name: Nombre de la tabla
            columns: Lista de columnas a seleccionar. Si es None, selecciona todas (*)
            where_conditions: Lista de condiciones WHERE (deben usar parámetros ?)
            order_by: Columna para ORDER BY
            allowed_tables: Tablas permitidas para esta consulta
            
        Returns:
            str: Consulta SQL segura
        """
        # Validar nombre de tabla
        safe_table = self.validator.validate_table_name(table_name, allowed_tables)
        
        # Construir lista de columnas
        if columns:
            safe_columns = [self.validator.validate_column_name(col) for col in columns]
            columns_str = ", ".join(safe_columns)
        else:
            columns_str = "*"
        
        # Construir consulta base
        query = f"SELECT {columns_str} FROM {safe_table}"
        
        # Añadir condiciones WHERE si existen
        if where_conditions:
            query += " WHERE " + " AND ".join(where_conditions)
        
        # Añadir ORDER BY si existe
        if order_by:
            safe_order_by = self.validator.validate_column_name(order_by)
            query += f" ORDER BY {safe_order_by}"
            
        return query
    
    def build_insert_query(
        self,
        table_name: str,
        columns: List[str],
        allowed_tables: Optional[Set[str]] = None
    ) -> str:
        """
        Construye una consulta INSERT segura.
        
        Args:
            table_name: Nombre de la tabla
            columns: Lista de columnas para el INSERT
            allowed_tables: Tablas permitidas para esta consulta
            
        Returns:
            str: Consulta SQL segura
        """
        # Validar nombre de tabla
        safe_table = self.validator.validate_table_name(table_name, allowed_tables)
        
        # Validar nombres de columnas
        safe_columns = [self.validator.validate_column_name(col) for col in columns]
        
        # Crear placeholders para parámetros
        placeholders = ", ".join(["?" for _ in columns])
        columns_str = ", ".join(safe_columns)
        
        return f"INSERT INTO {safe_table} ({columns_str}) VALUES ({placeholders})"
    
    def build_update_query(
        self,
        table_name: str,
        set_columns: List[str],
        where_conditions: List[str],
        allowed_tables: Optional[Set[str]] = None
    ) -> str:
        """
        Construye una consulta UPDATE segura.
        
        Args:
            table_name: Nombre de la tabla
            set_columns: Lista de columnas para SET (deben usar ? para valores)
            where_conditions: Lista de condiciones WHERE (deben usar parámetros ?)
            allowed_tables: Tablas permitidas para esta consulta
            
        Returns:
            str: Consulta SQL segura
        """
        # Validar nombre de tabla
        safe_table = self.validator.validate_table_name(table_name, allowed_tables)
        
        # Construir SET clauses (asumiendo que ya incluyen = ?)
        set_str = ", ".join(set_columns)
        where_str = " AND ".join(where_conditions)
        
        return f"UPDATE {safe_table} SET {set_str} WHERE {where_str}"


def load_sql_script(script_path: str) -> str:
    """
    Carga un script SQL desde un archivo externo de forma segura.
    
    Args:
        script_path: Ruta al archivo SQL
        
    Returns:
        str: Contenido del script SQL
        
    Raises:
        SQLSecurityError: Si el archivo no existe o no se puede leer
    """
    try:
        # Convertir a Path para manejo seguro de rutas
        path = Path(script_path)
        
        # Verificar que el archivo existe y es un archivo
        if not path.exists():
            raise SQLSecurityError(f"SQL script not found: {script_path}")
            
        if not path.is_file():
            raise SQLSecurityError(f"Path is not a file: {script_path}")
            
        # Verificar extensión
        if path.suffix.lower() not in ['.sql', '.txt']:
            raise SQLSecurityError(f"Invalid file extension: {path.suffix}")
            
        # Leer archivo
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if not content.strip():
            raise SQLSecurityError(f"SQL script is empty: {script_path}")
            
        return content
        
    except Exception as e:
        if isinstance(e, SQLSecurityError):
            raise
        raise SQLSecurityError(f"Error reading SQL script {script_path}: {e}")


# Instancia global del validador para uso en todo el proyecto
global_sql_validator = SQLSecurityValidator()
global_sql_builder = SecureSQLBuilder(global_sql_validator)


def validate_table_name(table_name: str, allowed_tables: Optional[Set[str]] = None) -> str:
    """
    Función de conveniencia para validar nombres de tablas.
    
    Args:
        table_name: Nombre de la tabla a validar
        allowed_tables: Conjunto opcional de tablas permitidas
        
    Returns:
        str: Nombre de tabla validado
    """
    return global_sql_validator.validate_table_name(table_name, allowed_tables)


def validate_column_name(column_name: str) -> str:
    """
    Función de conveniencia para validar nombres de columnas.
    
    Args:
        column_name: Nombre de la columna a validar
        
    Returns:
        str: Nombre de columna validado
    """
    return global_sql_validator.validate_column_name(column_name)