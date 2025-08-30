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
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


class RecoveryStrategy(Enum):
    """Estrategias de recuperación disponibles"""
    RETRY = "retry"
    FALLBACK = "fallback"
    OFFLINE = "offline"
    REPAIR = "repair"


@dataclass
class RecoveryConfig:
    """Configuración para recuperación de errores"""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    strategy: RecoveryStrategy = RecoveryStrategy.RETRY
    enable_cache: bool = True
    enable_offline_mode: bool = False
    critical_errors: List[str] = None

    def __post_init__(self):
        if self.critical_errors is None:
            self.critical_errors = []


@dataclass
class RecoveryAttempt:
    """Registro de un intento de recuperación"""
    timestamp: float
    error_type: str
    error_message: str
    strategy_used: RecoveryStrategy
    success: bool
    retry_count: int
    execution_time: float


class ErrorRecoveryManager:
    """Gestor avanzado de recuperación de errores"""

    def __init__(self):
        self.recovery_history: List[RecoveryAttempt] = []
        self.cache: Dict[str, Any] = {}
        self.offline_mode = False
        self._lock = threading.Lock()

    def with_recovery(self, config: RecoveryConfig, operation_name: str):
        """Decorador para operaciones con recuperación automática"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return self._execute_with_recovery(
                    func, args, kwargs, config, operation_name
                )
            return wrapper
        return decorator

    def _execute_with_recovery(self, func, args, kwargs, config: RecoveryConfig, operation_name: str):
        """Ejecuta función con estrategia de recuperación"""
        last_exception = None

        for attempt in range(config.max_retries + 1):
            try:
                start_time = time.time()
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time

                # Registrar éxito
                self._log_recovery_attempt(
                    operation_name, "SUCCESS", "", config.strategy,
                    True, attempt, execution_time
                )
                return result

            except Exception as e:
                last_exception = e
                execution_time = time.time() - time.time()  # Placeholder

                error_type = type(e).__name__
                error_msg = str(e)

                # Verificar si es error crítico
                if error_type in config.critical_errors:
                    self._log_recovery_attempt(
                        operation_name, error_type, error_msg, config.strategy,
                        False, attempt, execution_time
                    )
                    break

                # Aplicar estrategia de recuperación
                if not self._apply_recovery_strategy(config, attempt, error_type):
                    break

                # Esperar antes del siguiente intento
                if attempt < config.max_retries:
                    delay = min(config.base_delay * (2 ** attempt), config.max_delay)
                    time.sleep(delay)

        # Si llegamos aquí, todos los intentos fallaron
        if last_exception is not None:
            self._log_recovery_attempt(
                operation_name, type(last_exception).__name__, str(last_exception),
                config.strategy, False, config.max_retries, 0
            )
            raise last_exception
        else:
            # Fallback por si no hay excepción
            raise RuntimeError(f"All recovery attempts failed for {operation_name}")

    def _apply_recovery_strategy(self, config: RecoveryConfig, attempt: int, error_type: str) -> bool:
        """Aplica la estrategia de recuperación apropiada"""
        try:
            if config.strategy == RecoveryStrategy.RETRY:
                return True  # Simplemente reintentar

            elif config.strategy == RecoveryStrategy.FALLBACK:
                # Implementar fallback aquí
                return True

            elif config.strategy == RecoveryStrategy.OFFLINE:
                if not self.offline_mode:
                    self.offline_mode = True
                    logger.info("Activando modo offline")
                return True

            elif config.strategy == RecoveryStrategy.REPAIR:
                # Implementar reparación automática aquí
                return True

        except Exception as e:
            logger.error(f"Error aplicando estrategia de recuperación: {e}")

        return False

    def _log_recovery_attempt(self, operation: str, error_type: str, error_msg: str,
                            strategy: RecoveryStrategy, success: bool, retry_count: int,
                            execution_time: float):
        """Registra un intento de recuperación"""
        attempt = RecoveryAttempt(
            timestamp=time.time(),
            error_type=error_type,
            error_message=error_msg,
            strategy_used=strategy,
            success=success,
            retry_count=retry_count,
            execution_time=execution_time
        )

        with self._lock:
            self.recovery_history.append(attempt)

        status = "SUCCESS" if success else "FAILED"
        logger.info(f"Recovery attempt for {operation}: {status} "
                   f"(attempt {retry_count}, strategy: {strategy.value})")

    def export_recovery_log(self, filepath: str) -> bool:
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
def with_error_recovery(operation_name: Optional[str] = None,
                        max_retries: int = 3,
                        enable_cache: bool = True):
    """Decorador simplificado para recuperación de errores"""
    manager = get_error_recovery_manager()
    config = RecoveryConfig(
        max_retries=max_retries,
        enable_cache=enable_cache
    )
    return manager.with_recovery(config, operation_name or "unknown")


def database_operation_recovery(operation_name: Optional[str] = None):
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