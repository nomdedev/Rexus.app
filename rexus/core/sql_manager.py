"""
Gestor de Consultas SQL - Rexus.app v2.0.0

Sistema centralizado para cargar y gestionar todas las consultas SQL
desde archivos externos. Garantiza separación completa entre lógica
de negocio y consultas SQL con prevención de SQL injection.

Fecha: 24/08/2025
Objetivo: Gestión segura y centralizada de consultas SQL
"""

import logging
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from string import Template

# Importar logging
try:
    from ..utils.app_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class SQLQueryManager:
    """Gestor centralizado de consultas SQL para Rexus.app."""
    
    def __init__(self, sql_directory: str = "sql"):
        """
        Inicializa el gestor SQL.
        
        Args:
            sql_directory: Directorio donde están los archivos SQL
        """
        self.sql_directory = Path(sql_directory)
        self.queries: Dict[str, Dict[str, str]] = {}
        self.templates: Dict[str, Template] = {}
        self.loaded_modules: List[str] = []
        
        # Parámetros seguros permitidos para plantillas
        self.safe_parameters = {
            'table_name', 'column_name', 'order_by', 'limit', 'offset',
            'database_name', 'schema_name', 'index_name'
        }
        
        # Patrones peligrosos para validación
        self.dangerous_patterns = [
            r';\s*drop\s+table',
            r';\s*delete\s+from',
            r';\s*truncate\s+table',
            r';\s*alter\s+table',
            r'union\s+select',
            r'--\s*',
            r'/\*.*?\*/',
            r'xp_cmdshell',
            r'sp_executesql'
        ]
        
        logger.info("SQLQueryManager inicializado")
        
        # Cargar consultas automáticamente si existe el directorio
        if self.sql_directory.exists():
            self.load_all_queries()
    
    def load_all_queries(self) -> Dict[str, int]:
        """
        Carga todas las consultas SQL desde el directorio.
        
        Returns:
            Diccionario con estadísticas de carga por módulo
        """
        stats = {}
        
        if not self.sql_directory.exists():
            logger.warning(f"Directorio SQL no encontrado: {self.sql_directory}")
            return stats
        
        # Buscar archivos SQL
        sql_files = list(self.sql_directory.glob("*.sql"))
        
        for sql_file in sql_files:
            module_name = sql_file.stem
            try:
                loaded_count = self.load_module_queries(module_name)
                stats[module_name] = loaded_count
                logger.info(f"Módulo {module_name}: {loaded_count} consultas cargadas")
            except Exception as e:
                logger.error(f"Error cargando consultas de {module_name}: {e}")
                stats[module_name] = 0
        
        logger.info(f"Carga completa: {len(stats)} módulos, {sum(stats.values())} consultas totales")
        return stats
    
    def load_module_queries(self, module_name: str) -> int:
        """
        Carga consultas de un módulo específico.
        
        Args:
            module_name: Nombre del módulo
            
        Returns:
            Número de consultas cargadas
        """
        sql_file = self.sql_directory / f"{module_name}.sql"
        
        if not sql_file.exists():
            logger.warning(f"Archivo SQL no encontrado: {sql_file}")
            return 0
        
        try:
            with open(sql_file, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Parsear el contenido SQL
            queries = self._parse_sql_file(content)
            
            # Almacenar consultas del módulo
            if module_name not in self.queries:
                self.queries[module_name] = {}
            
            self.queries[module_name].update(queries)
            
            # Crear plantillas para consultas parametrizadas
            for query_name, query_sql in queries.items():
                template_key = f"{module_name}.{query_name}"
                self.templates[template_key] = Template(query_sql)
            
            if module_name not in self.loaded_modules:
                self.loaded_modules.append(module_name)
            
            return len(queries)
            
        except Exception as e:
            logger.error(f"Error cargando consultas de {module_name}: {e}")
            raise
    
    def _parse_sql_file(self, content: str) -> Dict[str, str]:
        """
        Parsea un archivo SQL para extraer consultas nombradas.
        
        Args:
            content: Contenido del archivo SQL
            
        Returns:
            Diccionario de consultas {nombre: sql}
        """
        queries = {}
        current_query = []
        current_name = None
        
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Ignorar líneas vacías y comentarios simples
            if not line or line.startswith('--'):
                continue
            
            # Detectar inicio de consulta nombrada: -- QUERY: nombre_consulta
            if line.startswith('-- QUERY:'):
                # Guardar consulta anterior si existe
                if current_name and current_query:
                    queries[current_name] = '\n'.join(current_query).strip()
                
                # Iniciar nueva consulta
                current_name = line.replace('-- QUERY:', '').strip()
                current_query = []
                continue
            
            # Acumular líneas de la consulta actual
            if current_name:
                current_query.append(line)
        
        # Guardar última consulta
        if current_name and current_query:
            queries[current_name] = '\n'.join(current_query).strip()
        
        # Si no hay consultas nombradas, usar todo el contenido como consulta por defecto
        if not queries and content.strip():
            queries['default'] = content.strip()
        
        return queries
    
    def get_query(self, module: str, query_name: str, **params) -> Optional[str]:
        """
        Obtiene una consulta SQL formateada.
        
        Args:
            module: Nombre del módulo
            query_name: Nombre de la consulta
            **params: Parámetros para la consulta
            
        Returns:
            Consulta SQL formateada o None si no existe
        """
        try:
            # Verificar que el módulo existe
            if module not in self.queries:
                logger.warning(f"Módulo SQL no encontrado: {module}")
                return None
            
            # Verificar que la consulta existe
            if query_name not in self.queries[module]:
                logger.warning(f"Consulta SQL no encontrada: {module}.{query_name}")
                return None
            
            # Obtener la consulta base
            base_query = self.queries[module][query_name]
            
            # Si no hay parámetros, devolver la consulta tal como está
            if not params:
                return base_query
            
            # Validar y sanitizar parámetros
            safe_params = self._validate_and_sanitize_params(params)
            
            # Aplicar parámetros usando plantillas seguras
            template_key = f"{module}.{query_name}"
            if template_key in self.templates:
                try:
                    formatted_query = self.templates[template_key].safe_substitute(**safe_params)
                    
                    # Validación final de seguridad
                    if self._is_query_safe(formatted_query):
                        return formatted_query
                    else:
                        logger.error(f"Consulta no segura detectada: {module}.{query_name}")
                        return None
                        
                except (KeyError, ValueError) as e:
                    logger.error(f"Error formateando consulta {module}.{query_name}: {e}")
                    return None
            
            return base_query
            
        except Exception as e:
            logger.error(f"Error obteniendo consulta {module}.{query_name}: {e}")
            return None
    
    def _validate_and_sanitize_params(self, params: Dict[str, Any]) -> Dict[str, str]:
        """
        Valida y sanitiza parámetros para consultas SQL.
        
        Args:
            params: Parámetros a validar
            
        Returns:
            Parámetros sanitizados
        """
        safe_params = {}
        
        for key, value in params.items():
            # Convertir a string
            str_value = str(value)
            
            # Sanitizar el valor
            sanitized_value = self._sanitize_sql_value(str_value)
            
            # Validar parámetros de estructura (nombres de tabla, columna, etc.)
            if key in self.safe_parameters:
                if self._is_valid_identifier(sanitized_value):
                    safe_params[key] = sanitized_value
                else:
                    logger.warning(f"Parámetro de estructura inválido: {key}={value}")
                    safe_params[key] = "INVALID"
            else:
                # Parámetros de datos (valores)
                safe_params[key] = sanitized_value
        
        return safe_params
    
    def _sanitize_sql_value(self, value: str) -> str:
        """
        Sanitiza un valor para uso en SQL.
        
        Args:
            value: Valor a sanitizar
            
        Returns:
            Valor sanitizado
        """
        if not isinstance(value, str):
            value = str(value)
        
        # Escapar comillas simples duplicándolas
        sanitized = value.replace("'", "''")
        
        # Remover o escapar caracteres peligrosos
        sanitized = sanitized.replace("\\", "\\\\")
        sanitized = sanitized.replace(";", "\\;")
        sanitized = sanitized.replace("--", "\\-\\-")
        
        return sanitized
    
    def _is_valid_identifier(self, identifier: str) -> bool:
        """
        Valida que un identificador SQL sea seguro.
        
        Args:
            identifier: Identificador a validar
            
        Returns:
            True si es válido
        """
        if not identifier:
            return False
        
        # Solo permitir letras, números y guiones bajos
        pattern = r'^[a-zA-Z_][a-zA-Z0-9_]*$'
        
        return bool(re.match(pattern, identifier)) and len(identifier) <= 64
    
    def _is_query_safe(self, query: str) -> bool:
        """
        Verifica que una consulta no contenga patrones peligrosos.
        
        Args:
            query: Consulta a verificar
            
        Returns:
            True si la consulta es segura
        """
        query_lower = query.lower()
        
        for pattern in self.dangerous_patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                logger.warning(f"Patrón peligroso detectado: {pattern}")
                return False
        
        return True
    
    def has_query(self, module: str, query_name: str) -> bool:
        """
        Verifica si existe una consulta específica.
        
        Args:
            module: Nombre del módulo
            query_name: Nombre de la consulta
            
        Returns:
            True si la consulta existe
        """
        return (module in self.queries and 
                query_name in self.queries[module])
    
    def list_modules(self) -> List[str]:
        """
        Lista todos los módulos cargados.
        
        Returns:
            Lista de nombres de módulos
        """
        return list(self.queries.keys())
    
    def list_queries(self, module: str) -> List[str]:
        """
        Lista todas las consultas de un módulo.
        
        Args:
            module: Nombre del módulo
            
        Returns:
            Lista de nombres de consultas
        """
        if module in self.queries:
            return list(self.queries[module].keys())
        return []
    
    def get_query_info(self, module: str, query_name: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene información detallada de una consulta.
        
        Args:
            module: Nombre del módulo
            query_name: Nombre de la consulta
            
        Returns:
            Información de la consulta
        """
        if not self.has_query(module, query_name):
            return None
        
        query_sql = self.queries[module][query_name]
        template_key = f"{module}.{query_name}"
        
        # Extraer parámetros de la consulta
        parameters = []
        if template_key in self.templates:
            # Buscar parámetros ${param} en la consulta
            param_pattern = r'\$\{(\w+)\}'
            parameters = list(set(re.findall(param_pattern, query_sql)))
        
        return {
            'module': module,
            'query_name': query_name,
            'sql': query_sql,
            'parameters': parameters,
            'length': len(query_sql),
            'has_template': template_key in self.templates
        }
    
    def validate_parameters(self, module: str, query_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida que los parámetros requeridos estén presentes.
        
        Args:
            module: Nombre del módulo
            query_name: Nombre de la consulta
            params: Parámetros proporcionados
            
        Returns:
            Resultado de la validación
        """
        result = {
            'valid': False,
            'missing_params': [],
            'extra_params': [],
            'message': ''
        }
        
        query_info = self.get_query_info(module, query_name)
        if not query_info:
            result['message'] = f"Consulta no encontrada: {module}.{query_name}"
            return result
        
        required_params = set(query_info['parameters'])
        provided_params = set(params.keys()) if params else set()
        
        result['missing_params'] = list(required_params - provided_params)
        result['extra_params'] = list(provided_params - required_params)
        
        if not result['missing_params']:
            result['valid'] = True
            result['message'] = 'Parámetros válidos'
        else:
            result['message'] = f"Parámetros faltantes: {', '.join(result['missing_params'])}"
        
        return result
    
    def reload_module(self, module_name: str) -> bool:
        """
        Recarga las consultas de un módulo específico.
        
        Args:
            module_name: Nombre del módulo a recargar
            
        Returns:
            True si la recarga fue exitosa
        """
        try:
            # Limpiar consultas existentes del módulo
            if module_name in self.queries:
                del self.queries[module_name]
            
            # Limpiar plantillas del módulo
            template_keys = [key for key in self.templates.keys() if key.startswith(f"{module_name}.")]
            for key in template_keys:
                del self.templates[key]
            
            # Recargar consultas
            loaded_count = self.load_module_queries(module_name)
            
            logger.info(f"Módulo {module_name} recargado: {loaded_count} consultas")
            return loaded_count > 0
            
        except Exception as e:
            logger.error(f"Error recargando módulo {module_name}: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del gestor SQL.
        
        Returns:
            Estadísticas del sistema
        """
        total_queries = sum(len(module_queries) for module_queries in self.queries.values())
        
        return {
            'modules_loaded': len(self.queries),
            'total_queries': total_queries,
            'templates_created': len(self.templates),
            'sql_directory': str(self.sql_directory),
            'modules': {
                module: len(queries) for module, queries in self.queries.items()
            }
        }


# Para compatibilidad con el código anterior
class SQLManager(SQLQueryManager):
    """Alias para compatibilidad con versiones anteriores."""
    pass


# Instancia global del gestor SQL
_sql_manager_instance = None


def get_sql_manager() -> SQLQueryManager:
    """Obtiene la instancia global del gestor SQL."""
    global _sql_manager_instance
    if _sql_manager_instance is None:
        _sql_manager_instance = SQLQueryManager()
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


def has_query(module: str, query_name: str) -> bool:
    """Función de conveniencia para verificar si existe una consulta."""
    return get_sql_manager().has_query(module, query_name)


def list_queries(module: str) -> List[str]:
    """Función de conveniencia para listar consultas de un módulo."""
    return get_sql_manager().list_queries(module)


def reload_sql_module(module_name: str) -> bool:
    """Función de conveniencia para recargar un módulo SQL."""
    return get_sql_manager().reload_module(module_name)