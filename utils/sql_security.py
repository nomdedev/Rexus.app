"""SQL Security Utilities"""

import re
import logging

class SQLSecurityError(Exception):
    pass

class SQLSecurityValidator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        self.dangerous_keywords = [
            'DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'EXEC', 'EXECUTE',
            'UNION', 'SCRIPT', 'JAVASCRIPT', 'VBSCRIPT'
        ]
        
        self.injection_patterns = [
            r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)',
            r'(--|\#|/\*|\*/)',
            r'(\b(OR|AND)\s+\d+\s*=\s*\d+)',
            r'(\'\s*(OR|AND)\s*\')',
            r'(\;)',
        ]
    
    def validate_query(self, query):
        if not isinstance(query, str):
            return False
        
        query_upper = query.upper()
        
        for keyword in self.dangerous_keywords:
            if keyword in query_upper:
                self.logger.warning(f"Palabra clave peligrosa detectada: {keyword}")
                return False
        
        for pattern in self.injection_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                self.logger.warning(f"Patrón de inyección SQL detectado: {pattern}")
                return False
        
        return True
    
    def sanitize_table_name(self, table_name):
        if not isinstance(table_name, str):
            raise SQLSecurityError("Nombre de tabla debe ser string")
        
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table_name):
            raise SQLSecurityError(f"Nombre de tabla inválido: {table_name}")
        
        return table_name
    
    def sanitize_column_name(self, column_name):
        if not isinstance(column_name, str):
            raise SQLSecurityError("Nombre de columna debe ser string")
        
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', column_name):
            raise SQLSecurityError(f"Nombre de columna inválido: {column_name}")
        
        return column_name

class SecureSQLBuilder:
    def __init__(self):
        self.validator = SQLSecurityValidator()
        self.ALLOWED_TABLES = set()
        self.logger = logging.getLogger(__name__)
    
    def add_allowed_table(self, table_name):
        try:
            clean_name = self.validator.sanitize_table_name(table_name)
            self.ALLOWED_TABLES.add(clean_name)
        except SQLSecurityError as e:
            self.logger.error(f"Error agregando tabla permitida: {e}")
    
    def build_select(self, table, columns="*", where_clause="", params=None):
        clean_table = self.validator.sanitize_table_name(table)
        if clean_table not in self.ALLOWED_TABLES:
            raise SQLSecurityError(f"Tabla no permitida: {table}")
        
        if columns != "*":
            if isinstance(columns, list):
                columns = ", ".join([self.validator.sanitize_column_name(col) for col in columns])
            else:
                columns = self.validator.sanitize_column_name(columns)
        
        query = f"SELECT {columns} FROM {clean_table}"
        
        if where_clause:
            query += f" WHERE {where_clause}"
        
        return query, params or []

def validate_table_name(table_name):
    validator = SQLSecurityValidator()
    return validator.sanitize_table_name(table_name)

sql_validator = SQLSecurityValidator()
sql_builder = SecureSQLBuilder()

default_tables = [
    'usuarios', 'administracion', 'auditoria', 'compras', 'configuracion',
    'herrajes', 'inventario', 'logistica', 'mantenimiento', 'obras', 
    'pedidos', 'vidrios'
]

for table in default_tables:
    sql_builder.add_allowed_table(table)