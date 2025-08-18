"""
Advanced Error Recovery System for Rexus.app v2.0.0
Sistema avanzado de recuperación de errores

Funcionalidades:
- Recuperación automática de conexiones perdidas
- Retry inteligente con backoff exponencial
- Fallback a operaciones en modo offline
- Auto-reparación de estructuras corruptas
- Logging detallado de errores y recuperaciones
"""

import time
import threading
import functools
import sqlite3
from typing import Any, Callable, Dict, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from rexus.utils.app_logger import get_logger

logger = get_logger(__name__)

class RecoveryStrategy(Enum):
    """Estrategias de recuperación disponibles"""
    RETRY = "retry"
    FALLBACK = "fallback"
    CACHE = "cache"
    OFFLINE = "offline"
    SKIP = "skip"

@dataclass
class RecoveryConfig:
    """Configuración para recuperación de errores"""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    backoff_factor: float = 2.0
    strategy: RecoveryStrategy = RecoveryStrategy.RETRY
    enable_cache: bool = True
    cache_duration: int = 300  # 5 minutes
    enable_offline_mode: bool = True
    critical_errors: List[str] = None

    def __post_init__(self):
        if self.critical_errors is None:
            self.critical_errors = [
                'ConnectionError',
                'DatabaseError', 
                'TimeoutError',
                'FileNotFoundError',
                'PermissionError'
            ]

@dataclass
class RecoveryAttempt:
    """Registro de intento de recuperación"""
    timestamp: datetime
    error_type: str
    error_message: str
    strategy_used: RecoveryStrategy
    success: bool
    retry_count: int
    execution_time: float

class ErrorRecoveryManager:
    """Gestor avanzado de recuperación de errores"""
    
    def __init__(self, config: RecoveryConfig = None):
        self.config = config or RecoveryConfig()
        self.recovery_history: List[RecoveryAttempt] = []
        self.cache = {}
        self.cache_timestamps = {}
        self.offline_data = {}
        self.connection_pool = {}
        self.lock = threading.Lock()
        
        # Contadores de estadísticas
        self.total_errors = 0
        self.successful_recoveries = 0
        self.failed_recoveries = 0
        
        logger.info("Error Recovery Manager initialized")
    
    def with_recovery(self, 
                     recovery_config: RecoveryConfig = None,
                     operation_name: str = "unknown"):
        """
        Decorador para aplicar recuperación automática de errores
        """
        config = recovery_config or self.config
        
        def decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                return self._execute_with_recovery(
                    func, args, kwargs, config, operation_name
                )
            return wrapper
        return decorator
    
    def _execute_with_recovery(self, 
                              func: Callable, 
                              args: tuple, 
                              kwargs: dict,
                              config: RecoveryConfig,
                              operation_name: str) -> Any:
        """Ejecuta función con recuperación automática"""
        
        last_exception = None
        start_time = time.time()
        
        for attempt in range(config.max_retries + 1):
            try:
                # Verificar cache primero si está habilitado
                if config.enable_cache and attempt == 0:
                    cached_result = self._get_cached_result(operation_name, args, kwargs)
                    if cached_result is not None:
                        return cached_result
                
                # Ejecutar función original
                result = func(*args, **kwargs)
                
                # Guardar en cache si fue exitoso
                if config.enable_cache:
                    self._cache_result(operation_name, args, kwargs, result)
                
                # Registrar recuperación exitosa si hubo intentos previos
                if attempt > 0:
                    execution_time = time.time() - start_time
                    self._record_recovery_attempt(
                        operation_name,
                        str(last_exception.__class__.__name__),
                        str(last_exception),
                        RecoveryStrategy.RETRY,
                        True,
                        attempt,
                        execution_time
                    )
                    self.successful_recoveries += 1
                    logger.info(f"Recovery successful for {operation_name} after {attempt} attempts")
                
                return result
                
            except Exception as e:
                last_exception = e
                self.total_errors += 1
                
                error_type = e.__class__.__name__
                is_critical = error_type in config.critical_errors
                
                logger.warning(f"Error in {operation_name} (attempt {attempt + 1}): {error_type} - {e}")
                
                # Si es el último intento o error no crítico, aplicar estrategias de fallback
                if attempt == config.max_retries:
                    execution_time = time.time() - start_time
                    
                    # Intentar estrategias de fallback
                    fallback_result = self._try_fallback_strategies(
                        operation_name, args, kwargs, config, e
                    )
                    
                    if fallback_result is not None:
                        self._record_recovery_attempt(
                            operation_name,
                            error_type,
                            str(e),
                            RecoveryStrategy.FALLBACK,
                            True,
                            attempt + 1,
                            execution_time
                        )
                        self.successful_recoveries += 1
                        return fallback_result
                    
                    # Fallback falló - registrar error final
                    self._record_recovery_attempt(
                        operation_name,
                        error_type,
                        str(e),
                        RecoveryStrategy.RETRY,
                        False,
                        attempt + 1,
                        execution_time
                    )
                    self.failed_recoveries += 1
                    logger.error(f"All recovery attempts failed for {operation_name}: {e}")
                    raise e
                
                # Aplicar backoff exponencial antes del siguiente intento
                if attempt < config.max_retries:
                    delay = min(
                        config.base_delay * (config.backoff_factor ** attempt),
                        config.max_delay
                    )
                    logger.info(f"Retrying {operation_name} in {delay:.1f}s (attempt {attempt + 2})")
                    time.sleep(delay)
        
        # No debería llegar aquí nunca
        raise last_exception
    
    def _try_fallback_strategies(self,
                               operation_name: str,
                               args: tuple,
                               kwargs: dict,
                               config: RecoveryConfig,
                               original_error: Exception) -> Any:
        """Intenta estrategias de fallback"""
        
        # 1. Intentar resultado cacheado aunque esté vencido
        cached_result = self._get_cached_result(operation_name, args, kwargs, ignore_expiry=True)
        if cached_result is not None:
            logger.info(f"Using expired cache for {operation_name} as fallback")
            return cached_result
        
        # 2. Intentar modo offline si está disponible
        if config.enable_offline_mode:
            offline_result = self._get_offline_data(operation_name, args, kwargs)
            if offline_result is not None:
                logger.info(f"Using offline data for {operation_name} as fallback")
                return offline_result
        
        # 3. Intentar reparación automática para errores de base de datos
        if isinstance(original_error, (sqlite3.DatabaseError, sqlite3.OperationalError)):
            repair_result = self._attempt_database_repair(operation_name, args, kwargs)
            if repair_result is not None:
                logger.info(f"Database repair successful for {operation_name}")
                return repair_result
        
        # 4. Devolver datos por defecto si están disponibles
        default_result = self._get_default_result(operation_name)
        if default_result is not None:
            logger.info(f"Using default result for {operation_name} as fallback")
            return default_result
        
        return None
    
    def _get_cached_result(self, 
                          operation_name: str, 
                          args: tuple, 
                          kwargs: dict,
                          ignore_expiry: bool = False) -> Any:
        """Obtiene resultado del cache"""
        cache_key = self._generate_cache_key(operation_name, args, kwargs)
        
        with self.lock:
            if cache_key not in self.cache:
                return None
            
            if not ignore_expiry:
                cached_time = self.cache_timestamps.get(cache_key)
                if cached_time:
                    age = time.time() - cached_time
                    if age > self.config.cache_duration:
                        # Cache vencido
                        del self.cache[cache_key]
                        del self.cache_timestamps[cache_key]
                        return None
            
            return self.cache[cache_key]
    
    def _cache_result(self, 
                     operation_name: str, 
                     args: tuple, 
                     kwargs: dict, 
                     result: Any):
        """Guarda resultado en cache"""
        cache_key = self._generate_cache_key(operation_name, args, kwargs)
        
        with self.lock:
            self.cache[cache_key] = result
            self.cache_timestamps[cache_key] = time.time()
            
            # Limitar tamaño del cache
            if len(self.cache) > 1000:
                oldest_key = min(self.cache_timestamps.keys(), 
                               key=self.cache_timestamps.get)
                del self.cache[oldest_key]
                del self.cache_timestamps[oldest_key]
    
    def _get_offline_data(self, operation_name: str, args: tuple, kwargs: dict) -> Any:
        """Obtiene datos offline como fallback"""
        offline_key = self._generate_cache_key(operation_name, args, kwargs)
        return self.offline_data.get(offline_key)
    
    def _attempt_database_repair(self, operation_name: str, args: tuple, kwargs: dict) -> Any:
        """Intenta reparar problemas de base de datos"""
        try:
            # Intentar reconexión de base de datos
            from rexus.core.database import get_inventario_connection, get_users_connection
            
            logger.info("Attempting database connection recovery...")
            
            # Renovar conexiones
            inv_conn = get_inventario_connection()
            users_conn = get_users_connection()
            
            if inv_conn and users_conn:
                logger.info("Database connections restored successfully")
                return {}  # Resultado vacío pero válido para continuar
            
        except Exception as e:
            logger.error(f"Database repair failed: {e}")
        
        return None
    
    def _get_default_result(self, operation_name: str) -> Any:
        """Obtiene resultado por defecto para operaciones conocidas"""
        defaults = {
            'obtener_usuario': {'id': -1, 'nombre': 'Usuario Offline', 'rol': 'guest'},
            'obtener_datos': [],
            'verificar_conexion': False,
            'obtener_estadisticas': {'total': 0, 'activos': 0}
        }
        
        for pattern, default in defaults.items():
            if pattern in operation_name.lower():
                return default
        
        return None
    
    def _generate_cache_key(self, operation_name: str, args: tuple, kwargs: dict) -> str:
        """Genera clave única para cache"""
        return f"{operation_name}:{hash((args, tuple(sorted(kwargs.items()))))}"
    
    def _record_recovery_attempt(self,
                               operation_name: str,
                               error_type: str,
                               error_message: str,
                               strategy: RecoveryStrategy,
                               success: bool,
                               retry_count: int,
                               execution_time: float):
        """Registra intento de recuperación para análisis"""
        attempt = RecoveryAttempt(
            timestamp=datetime.now(),
            error_type=error_type,
            error_message=error_message[:200],  # Truncar mensajes largos
            strategy_used=strategy,
            success=success,
            retry_count=retry_count,
            execution_time=execution_time
        )
        
        with self.lock:
            self.recovery_history.append(attempt)
            
            # Mantener solo los últimos 1000 registros
            if len(self.recovery_history) > 1000:
                self.recovery_history = self.recovery_history[-1000:]
    
    def get_recovery_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de recuperación"""
        with self.lock:
            total_attempts = len(self.recovery_history)
            if total_attempts == 0:
                return {
                    'total_errors': 0,
                    'success_rate': 100.0,
                    'avg_recovery_time': 0.0,
                    'most_common_errors': [],
                    'recovery_trends': []
                }
            
            successful = sum(1 for attempt in self.recovery_history if attempt.success)
            success_rate = (successful / total_attempts) * 100
            
            avg_recovery_time = sum(
                attempt.execution_time for attempt in self.recovery_history
            ) / total_attempts
            
            # Errores más comunes
            error_counts = {}
            for attempt in self.recovery_history:
                error_counts[attempt.error_type] = error_counts.get(attempt.error_type, 0) + 1
            
            most_common = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            return {
                'total_errors': self.total_errors,
                'total_recovery_attempts': total_attempts,
                'successful_recoveries': self.successful_recoveries,
                'failed_recoveries': self.failed_recoveries,
                'success_rate': success_rate,
                'avg_recovery_time': avg_recovery_time,
                'most_common_errors': most_common,
                'cache_size': len(self.cache),
                'offline_data_size': len(self.offline_data)
            }
    
    def clear_cache(self):
        """Limpia el cache de recuperación"""
        with self.lock:
            self.cache.clear()
            self.cache_timestamps.clear()
            logger.info("Recovery cache cleared")
    
    def export_recovery_log(self, filepath: str):
        """Exporta log de recuperación para análisis"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("timestamp,error_type,error_message,strategy,success,retry_count,execution_time\n")
                for attempt in self.recovery_history:
                    f.write(f"{attempt.timestamp},{attempt.error_type},"
                           f'"{attempt.error_message}",{attempt.strategy_used.value},'
                           f"{attempt.success},{attempt.retry_count},{attempt.execution_time}\n")
            
            logger.info(f"Recovery log exported to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to export recovery log: {e}")
            return False

# Instancia global del gestor de recuperación
_error_recovery_manager = None

def get_error_recovery_manager() -> ErrorRecoveryManager:
    """Obtiene la instancia global del gestor de recuperación"""
    global _error_recovery_manager
    if _error_recovery_manager is None:
        _error_recovery_manager = ErrorRecoveryManager()
    return _error_recovery_manager

# Decoradores de conveniencia
def with_error_recovery(operation_name: str = None, 
                       max_retries: int = 3,
                       enable_cache: bool = True):
    """Decorador simplificado para recuperación de errores"""
    manager = get_error_recovery_manager()
    config = RecoveryConfig(
        max_retries=max_retries,
        enable_cache=enable_cache
    )
    return manager.with_recovery(config, operation_name or "unknown")

def database_operation_recovery(operation_name: str = None):
    """Decorador especializado para operaciones de base de datos"""
    manager = get_error_recovery_manager()
    config = RecoveryConfig(
        max_retries=3,
        base_delay=2.0,
        strategy=RecoveryStrategy.RETRY,
        enable_cache=True,
        enable_offline_mode=True,
        critical_errors=['DatabaseError', 'OperationalError', 'ConnectionError']
    )
    return manager.with_recovery(config, operation_name or "database_operation")