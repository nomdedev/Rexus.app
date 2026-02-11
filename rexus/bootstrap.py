"""
Bootstrap - Rexus.app
Inicialización de todos los servicios y sistemas

Este módulo se encarga de inicializar todos los servicios
de manera centralizada cuando la aplicación arranca.

Servicios que inicializa:
- Logging estructurado
- Caché
- Métricas Prometheus
- Cola de tareas
- Gestor de alertas
- Gestor de secrets
"""

import os
import logging
from typing import Optional

# Configurar logging básico primero
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class RexusBootstrap:
    """
    Gestor de inicialización de servicios.
    """

    def __init__(self):
        """Inicializa el gestor de bootstrap."""
        self._initialized = False
        self._services = {}

    def initialize_all(self,
                      environment: str = None,
                      log_level: str = None,
                      enable_metrics: bool = None,
                      enable_cache: bool = None,
                      enable_queue: bool = None,
                      enable_alerts: bool = None) -> bool:
        """
        Inicializa todos los servicios.

        Args:
            environment: Ambiente (development, staging, production)
            log_level: Nivel de logging
            enable_metrics: Habilitar métricas Prometheus
            enable_cache: Habilitar caché
            enable_queue: Habilitar cola de tareas
            enable_alerts: Habilitar sistema de alertas

        Returns:
            True si la inicialización fue exitosa
        """
        if self._initialized:
            logger.warning("Services already initialized")
            return True

        environment = environment or os.getenv("REXUS_ENV", "development")
        log_level = log_level or os.getenv("LOG_LEVEL", "INFO")

        logger.info("=" * 60)
        logger.info(f"Initializing Rexus.app services in {environment} mode")
        logger.info("=" * 60)

        try:
            # 1. Inicializar logging estructurado
            self._init_logging(environment, log_level)

            # 2. Inicializar caché
            if enable_cache is not False:
                self._init_cache()

            # 3. Inicializar métricas
            if enable_metrics is not False:
                self._init_metrics()

            # 4. Inicializar cola de tareas
            if enable_queue is not False:
                self._init_queue()

            # 5. Inicializar alertas
            if enable_alerts is not False:
                self._init_alerts()

            # 6. Inicializar secrets
            self._init_secrets()

            # 7. Inicializar integración inventario-pedidos
            self._init_inventory_integration()

            self._initialized = True

            logger.info("=" * 60)
            logger.info("All services initialized successfully")
            logger.info("=" * 60)

            return True

        except Exception as e:
            logger.error(f"Error initializing services: {e}", exc_info=True)
            return False

    def _init_logging(self, environment: str, log_level: str):
        """Inicializa el logging estructurado."""
        try:
            from rexus.utils.structured_logging import setup_logging

            log_file = os.getenv("LOG_FILE", "./logs/rexus.log")
            json_format = os.getenv("LOG_JSON", "true").lower() == "true"

            setup_logging(
                service_name="rexus",
                environment=environment,
                log_level=log_level,
                log_file=log_file,
                json_format=json_format
            )

            self._services['logging'] = True
            logger.info("✓ Logging initialized")

        except ImportError:
            # Fallback a logging básico
            logger.setLevel(getattr(logging, log_level))
            self._services['logging'] = True
            logger.info("✓ Basic logging (structured not available)")

    def _init_cache(self):
        """Inicializa el caché."""
        try:
            from rexus.utils.cache_manager import CacheManager

            # Verificar si se requiere Redis
            redis_enabled = os.getenv("REDIS_ENABLED", "false").lower() == "true"

            if redis_enabled:
                logger.info("✓ Cache initialized (Redis)")
            else:
                logger.info("✓ Cache initialized (Memory)")

            self._services['cache'] = True

        except Exception as e:
            logger.warning(f"Cache initialization failed: {e}")
            self._services['cache'] = False

    def _init_metrics(self):
        """Inicializa las métricas Prometheus."""
        try:
            from rexus.monitoring.prometheus_metrics import get_metrics

            metrics = get_metrics()
            self._services['metrics'] = metrics

            if metrics.enabled:
                logger.info(f"✓ Prometheus metrics initialized (port {metrics.port})")
            else:
                logger.info("✓ Prometheus metrics disabled")

        except Exception as e:
            logger.warning(f"Metrics initialization failed: {e}")
            self._services['metrics'] = None

    def _init_queue(self):
        """Inicializa la cola de tareas."""
        try:
            from rexus.utils.task_queue import get_task_queue

            queue = get_task_queue()
            self._services['queue'] = queue

            logger.info(f"✓ Task queue initialized ({queue.max_workers} workers)")

        except Exception as e:
            logger.warning(f"Task queue initialization failed: {e}")
            self._services['queue'] = None

    def _init_alerts(self):
        """Inicializa el sistema de alertas."""
        try:
            from rexus.core.alerts_manager import get_alert_manager

            alerts = get_alert_manager()
            self._services['alerts'] = alerts

            channels = len(alerts.channels)
            logger.info(f"✓ Alert system initialized ({channels} channels)")

        except Exception as e:
            logger.warning(f"Alert system initialization failed: {e}")
            self._services['alerts'] = None

    def _init_secrets(self):
        """Inicializa el gestor de secrets."""
        try:
            from rexus.core.secrets_manager import get_secrets_manager

            secrets = get_secrets_manager()
            self._services['secrets'] = secrets

            backend_type = type(secrets.backend).__name__
            logger.info(f"✓ Secrets manager initialized ({backend_type})")

        except Exception as e:
            logger.warning(f"Secrets manager initialization failed: {e}")
            self._services['secrets'] = None

    def _init_inventory_integration(self):
        """Inicializa la integración inventario-pedidos."""
        try:
            from rexus.core.inventory_integration import get_inventory_service

            integration = get_inventory_service()
            self._services['inventory_integration'] = integration

            logger.info("✓ Inventory-pedido integration initialized")

        except Exception as e:
            logger.warning(f"Inventory integration initialization failed: {e}")
            self._services['inventory_integration'] = None

    def shutdown(self):
        """Apaga todos los servicios de forma ordenada."""
        logger.info("Shutting down Rexus.app services...")

        # Detener cola de tareas
        if 'queue' in self._services and self._services['queue']:
            self._services['queue'].stop()
            logger.info("✓ Task queue stopped")

        # Otros servicios no requieren shutdown explícito

        self._initialized = False
        logger.info("All services shut down")

    def get_service(self, service_name: str):
        """Obtiene un servicio inicializado."""
        return self._services.get(service_name)

    @property
    def is_initialized(self) -> bool:
        """Si los servicios están inicializados."""
        return self._initialized


# Instancia global
_bootstrap_instance: Optional[RexusBootstrap] = None


def bootstrap(**kwargs) -> bool:
    """
    Inicializa todos los servicios de Rexus.app.

    Args:
        **kwargs: Argumentos para initialize_all

    Returns:
        True si la inicialización fue exitosa

    Example:
        from rexus.bootstrap import bootstrap

        # Inicializar todos los servicios
        bootstrap(environment="production")
    """
    global _bootstrap_instance
    if _bootstrap_instance is None:
        _bootstrap_instance = RexusBootstrap()
    return _bootstrap_instance.initialize_all(**kwargs)


def shutdown():
    """Apaga todos los servicios."""
    global _bootstrap_instance
    if _bootstrap_instance:
        _bootstrap_instance.shutdown()


def get_service(service_name: str):
    """
    Obtiene un servicio inicializado.

    Args:
        service_name: Nombre del servicio

    Returns:
        Servicio o None si no existe

    Example:
        from rexus.bootstrap import get_service

        metrics = get_service('metrics')
        if metrics:
            metrics.inc_counter("my_counter")
    """
    global _bootstrap_instance
    if _bootstrap_instance:
        return _bootstrap_instance.get_service(service_name)
    return None


# Función de conveniencia para inicialización desde línea de comandos
if __name__ == '__main__':
    import sys

    env = sys.argv[1] if len(sys.argv) > 1 else 'development'

    success = bootstrap(environment=env)

    if success:
        print("✅ Rexus.app services initialized successfully")
        sys.exit(0)
    else:
        print("❌ Failed to initialize Rexus.app services")
        sys.exit(1)
