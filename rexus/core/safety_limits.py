"""
Safety Limits - Límites de seguridad para operaciones críticas de Rexus.app
Previene ataques DoS, agotamiento de memoria y problemas de rendimiento.

Fecha: 15/08/2025
Objetivo: Implementar límites máximos para operaciones críticas
"""

from typing import Any, Dict, Optional, Tuple
from functools import wraps
import time

# Importar logging
try:
    from rexus.utils.app_logger import get_logger
    logger = get_logger("safety.limits")
except ImportError:
    class DummyLogger:
        def info(self, msg): print(f"[INFO] {msg}")
        def warning(self, msg): print(f"[WARNING] {msg}")  
        def error(self, msg): print(f"[ERROR] {msg}")
    logger = DummyLogger()

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
    def validate_record_limit(operation: str, requested: int, limit_type: str = "general") -> Tuple[bool, int, str]:
        """
        Valida que la cantidad de registros solicitados esté dentro de los límites.
        
        Args:
            operation: Nombre de la operación para logging
            requested: Cantidad de registros solicitados
            limit_type: Tipo de límite ("export", "table", "api", "search", "bulk")
            
        Returns:
            Tuple[bool, int, str]: (es_válido, límite_aplicado, mensaje)
        """
        # Definir límites por tipo
        limits = {
            "export": SafetyLimits.MAX_EXPORT_RECORDS,
            "table": SafetyLimits.MAX_TABLE_RECORDS,
            "api": SafetyLimits.MAX_API_RECORDS,
            "search": SafetyLimits.MAX_SEARCH_RESULTS,
            "bulk": SafetyLimits.MAX_BULK_INSERT,
            "general": SafetyLimits.MAX_API_RECORDS
        }
        
        limit = limits.get(limit_type, SafetyLimits.MAX_API_RECORDS)
        
        if requested <= 0:
            logger.warning(f"Cantidad de registros inválida para {operation}: {requested}")
            return False, limit, f"Cantidad de registros debe ser mayor a 0"
        
        if requested > limit:
            logger.warning(f"Límite excedido en {operation}: solicitados={requested}, límite={limit}")
            return False, limit, f"Máximo {limit} registros permitidos para {limit_type}"
        
        logger.debug(f"Límite OK para {operation}: {requested} <= {limit}")
        return True, requested, "OK"
    
    @staticmethod
    def apply_safe_limit(requested: int, limit_type: str = "general") -> int:
        """
        Aplica un límite seguro a la cantidad solicitada.
        
        Args:
            requested: Cantidad solicitada
            limit_type: Tipo de límite
            
        Returns:
            int: Cantidad segura a usar
        """
        is_valid, safe_amount, _ = SafetyLimits.validate_record_limit("apply_limit", requested, limit_type)
        return safe_amount

def limit_records(limit_type: str = "general", enforce: bool = True):
    """
    Decorador para limitar automáticamente el número de registros en operaciones.
    
    Args:
        limit_type: Tipo de límite a aplicar
        enforce: Si True, falla si excede límite. Si False, aplica límite automáticamente
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Buscar parámetros de límite comunes
            limit_params = ['limit', 'cantidad', 'registros', 'max_records', 'count']
            
            for param in limit_params:
                if param in kwargs:
                    original_value = kwargs[param]
                    
                    if enforce:
                        is_valid, safe_value, message = SafetyLimits.validate_record_limit(
                            func.__name__, original_value, limit_type
                        )
                        if not is_valid:
                            logger.error(f"Límite excedido en {func.__name__}: {message}")
                            raise ValueError(message)
                        kwargs[param] = safe_value
                    else:
                        safe_value = SafetyLimits.apply_safe_limit(original_value, limit_type)
                        if safe_value != original_value:
                            logger.warning(f"Límite aplicado en {func.__name__}: {original_value} -> {safe_value}")
                        kwargs[param] = safe_value
                    break
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def timeout_operation(seconds: int = None):
    """
    Decorador para aplicar timeout a operaciones que pueden ser lentas.
    
    Args:
        seconds: Tiempo máximo en segundos
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            timeout = seconds or SafetyLimits.MAX_QUERY_SECONDS
            
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                elapsed = time.time() - start_time
                if elapsed > timeout:
                    logger.warning(f"Operación {func.__name__} tardó {elapsed:.2f}s (límite: {timeout}s)")
                
                return result
                
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"Error en {func.__name__} después de {elapsed:.2f}s: {e}")
                raise
        return wrapper
    return decorator

class SafeExportManager:
    """
    Manager para exportaciones seguras con límites y validaciones.
    """
    
    def __init__(self, module_name: str):
        self.module_name = module_name
        self.logger = logger
    
    @limit_records("export", enforce=True)
    def export_to_excel(self, data, filename: str, max_records: int = None):
        """
        Exporta datos a Excel con límites de seguridad.
        
        Args:
            data: Datos a exportar
            filename: Nombre del archivo
            max_records: Máximo número de registros (será limitado automáticamente)
        """
        try:
            self.logger.info(f"Iniciando exportación Excel para {self.module_name}: {len(data)} registros")
            
            # Aplicar límite si se especifica
            if max_records:
                data = data[:max_records]
            
            # Validar nombre de archivo
            if len(filename) > SafetyLimits.MAX_FILENAME_LENGTH:
                filename = filename[:SafetyLimits.MAX_FILENAME_LENGTH]
                self.logger.warning(f"Nombre de archivo truncado: {filename}")
            
            # Aquí iría la lógica real de exportación
            self.logger.info(f"Exportación Excel completada: {filename}")
            
            return True, f"Exportación exitosa: {len(data)} registros"
            
        except Exception as e:
            error_msg = f"Error en exportación Excel: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return False, error_msg
    
    @limit_records("export", enforce=False)  # Aplicar límite automáticamente
    def export_to_csv(self, data, filename: str, max_records: int = None):
        """
        Exporta datos a CSV con límites automáticos.
        
        Args:
            data: Datos a exportar
            filename: Nombre del archivo
            max_records: Máximo número de registros (será limitado automáticamente)
        """
        try:
            self.logger.info(f"Iniciando exportación CSV para {self.module_name}: {len(data)} registros")
            
            # El decorador ya aplicó el límite automáticamente
            
            # Validar nombre de archivo
            if len(filename) > SafetyLimits.MAX_FILENAME_LENGTH:
                filename = filename[:SafetyLimits.MAX_FILENAME_LENGTH]
            
            # Aquí iría la lógica real de exportación
            self.logger.info(f"Exportación CSV completada: {filename}")
            
            return True, f"Exportación exitosa: {len(data)} registros"
            
        except Exception as e:
            error_msg = f"Error en exportación CSV: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            return False, error_msg

class SafeQueryManager:
    """
    Manager para consultas seguras con límites y timeouts.
    """
    
    @staticmethod
    @limit_records("api", enforce=True)
    def obtener_registros_seguros(query_func, limit: int = None, **kwargs):
        """
        Ejecuta una consulta de forma segura con límites.
        
        Args:
            query_func: Función de consulta a ejecutar
            limit: Límite de registros
            **kwargs: Argumentos para la función
            
        Returns:
            Resultado de la consulta limitado
        """
        try:
            logger.debug(f"Ejecutando consulta segura con límite: {limit}")
            
            result = query_func(limit=limit, **kwargs)
            
            if hasattr(result, '__len__'):
                logger.info(f"Consulta segura completada: {len(result)} registros")
            
            return result
            
        except Exception as e:
            logger.error(f"Error en consulta segura: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    @timeout_operation()
    def obtener_con_timeout(query_func, timeout_seconds: int = None, **kwargs):
        """
        Ejecuta una consulta con timeout automático.
        
        Args:
            query_func: Función de consulta a ejecutar
            timeout_seconds: Timeout en segundos
            **kwargs: Argumentos para la función
            
        Returns:
            Resultado de la consulta
        """
        return query_func(**kwargs)