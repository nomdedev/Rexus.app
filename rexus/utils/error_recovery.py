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
            logger.exception(f"Failed to export recovery log: {e}")
            # FIXME: Specify concrete exception types instead of generic Exceptionreturn False

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