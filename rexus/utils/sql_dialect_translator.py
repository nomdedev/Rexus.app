#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL Dialect Translator - Rexus.app
Traduce queries SQLite a SQL Server automáticamente
"""

import re
import logging
import string
from typing import Dict, Any, Optional

try:
    from rexus.utils.app_logger import get_logger
    logger = get_logger("sql.translator")
except ImportError:
    logger = logging.getLogger("sql.translator")

class SQLDialectTranslator:
    """Traductor de dialectos SQL para compatibilidad entre SQLite y SQL Server."""
    
    def __init__(self):
        self.sqlite_to_sqlserver_mappings = {
            # Verificación de tablas
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?": 
                "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE' AND TABLE_NAME=?",
            
            "SELECT sql FROM sqlite_master WHERE type='table' AND name=?":
                """SELECT 
                    'CREATE TABLE ' + TABLE_NAME + ' (' + 
                    STUFF((
                        SELECT ', ' + COLUMN_NAME + ' ' + DATA_TYPE + 
                        CASE 
                            WHEN CHARACTER_MAXIMUM_LENGTH IS NOT NULL 
                            THEN '(' + CAST(CHARACTER_MAXIMUM_LENGTH AS VARCHAR) + ')'
                            ELSE ''
                        END
                        FROM INFORMATION_SCHEMA.COLUMNS
                        WHERE TABLE_NAME = t.TABLE_NAME
                        FOR XML PATH('')
                    ), 1, 2, '') + ')' as sql
                FROM INFORMATION_SCHEMA.TABLES t 
                WHERE TABLE_TYPE='BASE TABLE' AND TABLE_NAME=?""",
            
            # Información de columnas
            "PRAGMA table_info":
                """SELECT 
                    ORDINAL_POSITION-1 as cid,
                    COLUMN_NAME as name, 
                    DATA_TYPE as type,
                    CASE WHEN IS_NULLABLE='NO' THEN 1 ELSE 0 END as [notnull],
                    COLUMN_DEFAULT as dflt_value,
                    CASE WHEN COLUMNPROPERTY(OBJECT_ID(TABLE_SCHEMA+'.'+TABLE_NAME), COLUMN_NAME, 'IsIdentity') = 1 THEN 1 ELSE 0 END as pk
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME""",
                
            # Creación de tablas con IF NOT EXISTS
            "CREATE TABLE IF NOT EXISTS": "IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='{table_name}' AND xtype='U') CREATE TABLE",
            
            # AUTOINCREMENT -> IDENTITY
            "AUTOINCREMENT": "IDENTITY(1,1)",
            "INTEGER PRIMARY KEY AUTOINCREMENT": "INT IDENTITY(1,1) PRIMARY KEY",
            
            # Tipos de datos
            "INTEGER": "INT",
            "TEXT": "NVARCHAR(MAX)",
            "REAL": "FLOAT",
            "BLOB": "VARBINARY(MAX)",
            "DATETIME DEFAULT CURRENT_TIMESTAMP": "DATETIME DEFAULT GETDATE()",
            "CURRENT_TIMESTAMP": "GETDATE()",
            
            # Operadores
            "||": "+",  # Concatenación
            "LIMIT": "TOP",
            
            # Funciones
            "LENGTH(": "LEN(",
            "SUBSTR(": "SUBSTRING(",
            "IFNULL(": "ISNULL(",
            "RANDOM()": "NEWID()",
            "datetime('now')": "GETDATE()",
            "date('now')": "CONVERT(DATE, GETDATE())",
        }
        
        self.table_existence_patterns = {
            "verificar_tabla_sqlite": self._generate_sqlserver_table_check,
            "verificar_tabla_existe": self._generate_sqlserver_table_check,
            "create_pedidos_table": self._generate_sqlserver_create_table,
            "create_pedidos_detalle_table": self._generate_sqlserver_create_table
        }
    
    def translate_query(self, query: str, query_name: str = None) -> str:
        """Traduce una query SQLite a SQL Server."""
        try:
            # Aplicar patrones específicos si se conoce el nombre de la query
            if query_name and query_name in self.table_existence_patterns:
                return self.table_existence_patterns[query_name](query)
            
            # Aplicar traducciones generales
            translated = query
            
            # Procesar traducciones de mapeo
            for sqlite_pattern, sqlserver_replacement in self.sqlite_to_sqlserver_mappings.items():
                if isinstance(sqlite_pattern, str) and sqlite_pattern in translated:
                    translated = translated.replace(sqlite_pattern, sqlserver_replacement)
            
            # Aplicar patrones con regex
            translated = self._apply_regex_patterns(translated)
            
            logger.debug(f"Query traducida: {query_name if query_name else 'unnamed'}")
            return translated
            
        except Exception as e:
            logger.error(f"Error traduciendo query {query_name}: {str(e)}")
            return query  # Retornar query original si falla la traducción
    
    def _apply_regex_patterns(self, query: str) -> str:
        """Aplica patrones regex para traducciones complejas."""
        
        # Convertir CREATE TABLE IF NOT EXISTS
        query = re.sub(
            r'CREATE TABLE IF NOT EXISTS\s+(\w+)',
            r"IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='\1' AND xtype='U') CREATE TABLE \1",
            query,
            flags=re.IGNORECASE
        )
        
        # Convertir LIMIT a TOP
        query = re.sub(
            r'SELECT\s+(.*?)\s+LIMIT\s+(\d+)',
            r'SELECT TOP \2 \1',
            query,
            flags=re.IGNORECASE
        )
        
        # Convertir concatenación con ||
        query = re.sub(
            r"(\w+)\s*\|\|\s*'([^']*)'",
            r"\1 + '\2'",
            query
        )
        
        # Convertir SUBSTR a SUBSTRING (ajustar parámetros)
        query = re.sub(
            r'SUBSTR\(([^,]+),\s*(\d+),\s*(\d+)\)',
            r'SUBSTRING(\1, \2, \3)',
            query
        )
        
        return query
    
    def _generate_sqlserver_table_check(self, original_query: str) -> str:
        """Genera query SQL Server para verificar existencia de tabla."""
        # Extraer nombre de tabla del query original
        table_match = re.search(r"WHERE.*?name\s*=\s*['\"]?(\w+)['\"]?", original_query, re.IGNORECASE)
        
        if table_match:
            table_name = table_match.group(1)
            return f"""
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE='BASE TABLE' 
            AND TABLE_NAME='{table_name}'
            """
        else:
            # Query genérica si no se puede extraer el nombre
            return """
            SELECT TABLE_NAME 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_TYPE='BASE TABLE' 
            AND TABLE_NAME=?
            """
    
    def _generate_sqlserver_create_table(self, original_query: str) -> str:
        """Convierte CREATE TABLE SQLite a SQL Server."""
        
        # Reemplazos básicos
        translated = original_query
        
        # IF NOT EXISTS - Corregir sintaxis SQL Server
        if 'IF NOT EXISTS' in translated.upper():
            table_match = re.search(r'CREATE TABLE IF NOT EXISTS\s+(\w+)', translated, re.IGNORECASE)
            if table_match:
                table_name = table_match.group(1)
                # Remover IF NOT EXISTS del CREATE TABLE
                translated = re.sub(r'CREATE TABLE IF NOT EXISTS\s+', 'CREATE TABLE ', translated, flags=re.IGNORECASE)
                # Validar nombre de tabla antes de usar
                if self._is_valid_table_name(table_name):
                    # Envolver en bloque condicional SQL Server
                    translated = f"""IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{table_name}')
BEGIN
    {translated}
END"""
                else:
                    raise ValueError(f"Invalid table name: {table_name}")
        
        # Tipos de datos
        type_mappings = {
            r'\bINTEGER\b': 'INT',
            r'\bTEXT\b': 'NVARCHAR(MAX)',
            r'\bREAL\b': 'FLOAT',
            r'\bBLOB\b': 'VARBINARY(MAX)',
            r'\bAUTOINCREMENT\b': 'IDENTITY(1,1)',
            r'\bCURRENT_TIMESTAMP\b': 'GETDATE()',
        }
        
        for pattern, replacement in type_mappings.items():
            translated = re.sub(pattern, replacement, translated, flags=re.IGNORECASE)
        
        # Manejar PRIMARY KEY AUTOINCREMENT
        translated = re.sub(
            r'(\w+)\s+INTEGER\s+PRIMARY\s+KEY\s+IDENTITY\(1,1\)',
            r'\1 INT IDENTITY(1,1) PRIMARY KEY',
            translated,
            flags=re.IGNORECASE
        )
        
        return translated

    def _is_valid_table_name(self, table_name: str) -> bool:
        """
        Valida que el nombre de tabla sea seguro para prevenir SQL injection.
        
        Args:
            table_name: Nombre de tabla a validar
            
        Returns:
            True si el nombre es válido
        """
        if not table_name or not isinstance(table_name, str):
            return False
            
        # Solo permitir letras, números y guiones bajos
        allowed_chars = string.ascii_letters + string.digits + '_'
        if not all(c in allowed_chars for c in table_name):
            return False
            
        # No debe empezar con número
        if table_name[0].isdigit():
            return False
            
        # Longitud razonable
        if len(table_name) > 128:
            return False
            
        # Lista negra de palabras clave SQL
        sql_keywords = {'SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'EXEC', 'EXECUTE'}
        if table_name.upper() in sql_keywords:
            return False
            
        return True
    
    def translate_file_query(self, file_path: str) -> str:
        """Traduce una query desde archivo."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_query = f.read()
            
            # Extraer nombre del archivo para contexto
            file_name = file_path.split('/')[-1].replace('.sql', '') if '/' in file_path else file_path.split('\\')[-1].replace('.sql', '')
            
            return self.translate_query(original_query, file_name)
            
        except Exception as e:
            logger.error(f"Error leyendo archivo {file_path}: {str(e)}")
            return ""
    
    def detect_dialect(self, query: str) -> str:
        """Detecta el dialecto SQL de una query."""
        sqlite_indicators = [
            'sqlite_master',
            'PRAGMA',
            'AUTOINCREMENT',
            'datetime(\'now\')',
            'IFNULL(',
            'SUBSTR(',
            'LENGTH(',
            'RANDOM()'
        ]
        
        sqlserver_indicators = [
            'INFORMATION_SCHEMA',
            'GETDATE()',
            'IDENTITY(',
            'NVARCHAR',
            'VARBINARY',
            'sysobjects',
            'LEN(',
            'ISNULL(',
            'NEWID()'
        ]
        
        sqlite_score = sum(1 for indicator in sqlite_indicators if indicator in query)
        sqlserver_score = sum(1 for indicator in sqlserver_indicators if indicator in query)
        
        if sqlite_score > sqlserver_score:
            return 'sqlite'
        elif sqlserver_score > sqlite_score:
            return 'sqlserver'
        else:
            return 'unknown'
    
    def is_translation_needed(self, query: str) -> bool:
        """Determina si una query necesita traducción."""
        return self.detect_dialect(query) == 'sqlite'

# Instancia global del traductor
sql_translator = SQLDialectTranslator()

def translate_sqlite_to_sqlserver(query: str, query_name: str = None) -> str:
    """Función helper para traducir queries."""
    return sql_translator.translate_query(query, query_name)

def auto_translate_query(query: str, query_name: str = None) -> str:
    """Traduce automáticamente solo si es necesario."""
    if sql_translator.is_translation_needed(query):
        return sql_translator.translate_query(query, query_name)
    return query