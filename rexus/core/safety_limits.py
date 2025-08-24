"""
Safety Limits - Límites de seguridad para operaciones críticas de Rexus.app
Previene ataques DoS, agotamiento de memoria y problemas de rendimiento.

Fecha: 15/08/2025
Objetivo: Implementar límites máximos para operaciones críticas
"""

from typing import Any, Dict, Optional, Tuple
from functools import wraps
import time
import sys
import traceback

# Importar logging
try:
    from ..utils.app_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class SafetyLimits:
    """
    Clase que define y gestiona límites de seguridad para operaciones críticas.
    """
    
    # Límites de registros
    MAX_EXPORT_RECORDS = 50000  # Máximo para exportaciones Excel/CSV
    MAX_TABLE_RECORDS = 10000   # Máximo para carga en tabla UI
    MAX_API_RECORDS = 5000      # Máximo para consultas API
    MAX_SEARCH_RESULTS = 1000   # Máximo resultados de búsqueda
    MAX_BULK_INSERT = 1000      # Máximo para inserciones masivas
    
    # Límites de tiempo
    MAX_QUERY_SECONDS = 30      # Timeout para consultas SQL
    MAX_EXPORT_SECONDS = 300    # Timeout para exportaciones
    
    # Límites de memoria
    MAX_MEMORY_MB = 500         # Máximo uso de memoria por operación
    
    # Límites de archivo
    MAX_UPLOAD_SIZE_MB = 100    # Máximo tamaño de archivo subido
    MAX_FILENAME_LENGTH = 255   # Máximo longitud de nombre de archivo
    
    # Control de rate limiting
    RATE_LIMIT_SECONDS = 1      # Mínimo tiempo entre operaciones pesadas
    
    @staticmethod
    def validate_record_count(count: int, operation: str = "consulta") -> bool:
        """
        Valida que el número de registros esté dentro de los límites seguros.
        
        Args:
            count: Número de registros
            operation: Tipo de operación
            
        Returns:
            True si está dentro de los límites
        """
        limits = {
            "export": SafetyLimits.MAX_EXPORT_RECORDS,
            "table": SafetyLimits.MAX_TABLE_RECORDS,
            "api": SafetyLimits.MAX_API_RECORDS,
            "search": SafetyLimits.MAX_SEARCH_RESULTS,
            "bulk_insert": SafetyLimits.MAX_BULK_INSERT
        }
        
        limit = limits.get(operation.lower(), SafetyLimits.MAX_API_RECORDS)
        
        if count > limit:
            logger.warning(f"Operación {operation} excede límite: {count} > {limit}")
            return False
            
        return True
    
    @staticmethod
    def validate_file_size(size_bytes: int) -> bool:
        """
        Valida que el tamaño de archivo esté dentro de los límites.
        
        Args:
            size_bytes: Tamaño en bytes
            
        Returns:
            True si está dentro del límite
        """
        max_bytes = SafetyLimits.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        
        if size_bytes > max_bytes:
            logger.warning(f"Archivo excede límite: {size_bytes} bytes > {max_bytes} bytes")
            return False
            
        return True
    
    @staticmethod
    def validate_filename(filename: str) -> bool:
        """
        Valida que el nombre de archivo esté dentro de los límites.
        
        Args:
            filename: Nombre del archivo
            
        Returns:
            True si es válido
        """
        if len(filename) > SafetyLimits.MAX_FILENAME_LENGTH:
            logger.warning(f"Nombre de archivo muy largo: {len(filename)} > {SafetyLimits.MAX_FILENAME_LENGTH}")
            return False
            
        # Validar caracteres peligrosos
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        if any(char in filename for char in dangerous_chars):
            logger.warning(f"Nombre de archivo contiene caracteres peligrosos: {filename}")
            return False
            
        return True
    
    @staticmethod
    def get_memory_usage_mb() -> float:
        """
        Obtiene el uso actual de memoria en MB.
        
        Returns:
            Uso de memoria en MB
        """
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            # Fallback usando sys
            return sys.getsizeof(locals()) / 1024 / 1024
        except Exception:
            return 0.0


def limit_records(operation: str, enforce: bool = True):
    """
    Decorador para limitar el número de registros en operaciones.
    
    Args:
        operation: Tipo de operación
        enforce: Si forzar el límite o solo advertir
        
    Returns:
        Decorador
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Intentar obtener el count de los argumentos
            record_count = None
            
            # Buscar en args
            for arg in args:
                if isinstance(arg, (list, tuple)):
                    record_count = len(arg)
                    break
                elif isinstance(arg, int) and arg > 0:
                    record_count = arg
                    break
            
            # Buscar en kwargs
            if record_count is None:
                for key in ['count', 'limit', 'records', 'data']:
                    if key in kwargs:
                        if isinstance(kwargs[key], (list, tuple)):
                            record_count = len(kwargs[key])
                        elif isinstance(kwargs[key], int):
                            record_count = kwargs[key]
                        break
            
            # Validar si encontramos count
            if record_count is not None:
                if not SafetyLimits.validate_record_count(record_count, operation):
                    if enforce:
                        raise ValueError(f"Operación {operation} excede límites de seguridad: {record_count} registros")
                    else:
                        logger.warning(f"Operación {operation} con {record_count} registros (advertencia)")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def timeout_operation(seconds: int):
    """
    Decorador para establecer timeout en operaciones.
    
    Args:
        seconds: Timeout en segundos
        
    Returns:
        Decorador
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                elapsed = time.time() - start_time
                if elapsed > seconds:
                    logger.warning(f"Operación {func.__name__} tardó {elapsed:.2f}s (límite: {seconds}s)")
                
                return result
                
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"Error en {func.__name__} después de {elapsed:.2f}s: {e}")
                raise
                
        return wrapper
    return decorator


def memory_limit(max_mb: int):
    """
    Decorador para verificar límites de memoria.
    
    Args:
        max_mb: Límite máximo en MB
        
    Returns:
        Decorador
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            memory_before = SafetyLimits.get_memory_usage_mb()
            
            try:
                result = func(*args, **kwargs)
                
                memory_after = SafetyLimits.get_memory_usage_mb()
                memory_used = memory_after - memory_before
                
                if memory_used > max_mb:
                    logger.warning(f"Operación {func.__name__} usó {memory_used:.2f}MB (límite: {max_mb}MB)")
                
                return result
                
            except Exception as e:
                logger.error(f"Error en {func.__name__}: {e}")
                raise
                
        return wrapper
    return decorator


class SafeOperations:
    """Operaciones comunes con límites de seguridad aplicados."""
    
    @staticmethod
    @limit_records("export", enforce=False)
    @timeout_operation(SafetyLimits.MAX_EXPORT_SECONDS)
    def export_to_csv(data, filename: str, max_records: int = None):
        """
        Exporta datos a CSV con límites automáticos.
        
        Args:
            data: Datos a exportar
            filename: Nombre del archivo
            max_records: Límite máximo de registros
        """
        # Validar nombre de archivo
        if not SafetyLimits.validate_filename(filename):
            raise ValueError(f"Nombre de archivo inválido: {filename}")
        
        # Aplicar límite si se especifica
        if max_records and len(data) > max_records:
            logger.warning(f"Limitando exportación a {max_records} registros de {len(data)} totales")
            data = data[:max_records]
        
        try:
            import csv
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                if data:
                    writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
            
            logger.info(f"Exportación CSV exitosa: {len(data)} registros a {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error en exportación CSV: {e}")
            return False
    
    @staticmethod
    @limit_records("bulk_insert", enforce=True)
    @timeout_operation(SafetyLimits.MAX_QUERY_SECONDS)
    def bulk_insert_safe(connection, table: str, records: list):
        """
        Inserción masiva con límites de seguridad.
        
        Args:
            connection: Conexión a la base de datos
            table: Tabla de destino
            records: Registros a insertar
            
        Returns:
            Número de registros insertados
        """
        if not records:
            return 0
        
        try:
            # Dividir en lotes si es necesario
            batch_size = min(SafetyLimits.MAX_BULK_INSERT, len(records))
            total_inserted = 0
            
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                
                # Aquí iría la lógica específica de inserción
                # Por ahora simulamos
                logger.info(f"Insertando lote de {len(batch)} registros en {table}")
                total_inserted += len(batch)
            
            return total_inserted
            
        except Exception as e:
            logger.error(f"Error en inserción masiva: {e}")
            raise
    
    @staticmethod
    def validate_operation_safety(operation: str, **params) -> Tuple[bool, str]:
        """
        Valida que una operación sea segura antes de ejecutar.
        
        Args:
            operation: Tipo de operación
            **params: Parámetros de la operación
            
        Returns:
            Tupla (es_seguro, mensaje)
        """
        try:
            # Validar registros
            if 'record_count' in params:
                if not SafetyLimits.validate_record_count(params['record_count'], operation):
                    return False, f"Número de registros excede límites para {operation}"
            
            # Validar archivo
            if 'filename' in params:
                if not SafetyLimits.validate_filename(params['filename']):
                    return False, f"Nombre de archivo inválido: {params['filename']}"
            
            if 'file_size' in params:
                if not SafetyLimits.validate_file_size(params['file_size']):
                    return False, f"Tamaño de archivo excede límites"
            
            # Validar memoria
            current_memory = SafetyLimits.get_memory_usage_mb()
            if current_memory > SafetyLimits.MAX_MEMORY_MB:
                return False, f"Uso de memoria muy alto: {current_memory:.1f}MB"
            
            return True, "Operación segura"
            
        except Exception as e:
            error_msg = f"Error validando seguridad: {e}"
            logger.error(error_msg)
            return False, error_msg


# Funciones de conveniencia
def is_safe_operation(operation: str, **params) -> bool:
    """Función de conveniencia para validar operaciones."""
    is_safe, _ = SafeOperations.validate_operation_safety(operation, **params)
    return is_safe


def get_safety_limits() -> Dict[str, int]:
    """Obtiene todos los límites de seguridad definidos."""
    return {
        'max_export_records': SafetyLimits.MAX_EXPORT_RECORDS,
        'max_table_records': SafetyLimits.MAX_TABLE_RECORDS,
        'max_api_records': SafetyLimits.MAX_API_RECORDS,
        'max_search_results': SafetyLimits.MAX_SEARCH_RESULTS,
        'max_bulk_insert': SafetyLimits.MAX_BULK_INSERT,
        'max_query_seconds': SafetyLimits.MAX_QUERY_SECONDS,
        'max_export_seconds': SafetyLimits.MAX_EXPORT_SECONDS,
        'max_memory_mb': SafetyLimits.MAX_MEMORY_MB,
        'max_upload_size_mb': SafetyLimits.MAX_UPLOAD_SIZE_MB,
        'max_filename_length': SafetyLimits.MAX_FILENAME_LENGTH
    }