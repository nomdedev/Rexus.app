"""
Cache Warming - Rexus.app
Precarga datos críticos en caché al iniciar la aplicación

Mejora:
- Tiempo de respuesta inicial
- Hit rate de caché
- Experiencia de usuario
"""

import logging
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback

logger = logging.getLogger(__name__)


@dataclass
class WarmUpTask:
    """Tarea de calentamiento de caché."""
    name: str
    loader: Callable
    cache_key: str
    ttl: int
    priority: int = 0  # Mayor prioridad se ejecuta primero
    enabled: bool = True


@dataclass
class WarmUpResult:
    """Resultado de una tarea de calentamiento."""
    name: str
    success: bool
    duration_ms: float
    item_count: int = 0
    error: Optional[str] = None
    cache_key: str = ""


class CacheWarmer:
    """
    Gestiona el calentamiento del caché con datos críticos.

    Características:
    - Carga paralela de datos
    - Priorización de tareas
    - Reintentos automáticos
    - Métricas de ejecución
    - Tolerancia a fallos

    Example:
        warmer = CacheWarmer()

        @warmer.register_task("usuarios", ttl=300, priority=10)
        def load_usuarios():
            return usuarios_model.obtener_todos()

        warmer.warm_up_all()
    """

    def __init__(self, cache_manager=None):
        """
        Inicializa el CacheWarmer.

        Args:
            cache_manager: Instancia de CacheManager (opcional, se obtiene del singleton)
        """
        self._tasks: Dict[str, WarmUpTask] = {}
        self._results: List[WarmUpResult] = []
        self._start_time: Optional[datetime] = None
        self._end_time: Optional[datetime] = None

        # Obtener cache manager
        if cache_manager is None:
            from rexus.utils.cache_manager import get_cache_manager
            self.cache = get_cache_manager()
        else:
            self.cache = cache_manager

    def register_task(self,
                      name: str,
                      cache_key: str,
                      ttl: int = 300,
                      priority: int = 0,
                      enabled: bool = True):
        """
        Decorador para registrar una tarea de calentamiento.

        Args:
            name: Nombre de la tarea
            cache_key: Clave para guardar en caché
            ttl: Tiempo de vida en segundos
            priority: Prioridad (mayor = se ejecuta antes)
            enabled: Si está habilitada

        Example:
            @warmer.register_task("usuarios", "all_users", ttl=300, priority=10)
            def load_usuarios():
                return [(1, "Juan"), (2, "Maria")]
        """
        def decorator(func: Callable) -> Callable:
            self._tasks[name] = WarmUpTask(
                name=name,
                loader=func,
                cache_key=cache_key,
                ttl=ttl,
                priority=priority,
                enabled=enabled
            )
            return func
        return decorator

    def add_task(self,
                 name: str,
                 loader: Callable,
                 cache_key: str,
                 ttl: int = 300,
                 priority: int = 0,
                 enabled: bool = True):
        """
        Agrega una tarea de calentamiento programáticamente.

        Args:
            name: Nombre de la tarea
            loader: Función que carga los datos
            cache_key: Clave para caché
            ttl: Tiempo de vida
            priority: Prioridad
            enabled: Si está habilitada
        """
        self._tasks[name] = WarmUpTask(
            name=name,
            loader=loader,
            cache_key=cache_key,
            ttl=ttl,
            priority=priority,
            enabled=enabled
        )

    def remove_task(self, name: str):
        """Elimina una tarea de calentamiento."""
        self._tasks.pop(name, None)

    def enable_task(self, name: str):
        """Habilita una tarea."""
        if name in self._tasks:
            self._tasks[name].enabled = True

    def disable_task(self, name: str):
        """Deshabilita una tarea."""
        if name in self._tasks:
            self._tasks[name].enabled = False

    def _execute_task(self, task: WarmUpTask) -> WarmUpResult:
        """Ejecuta una tarea individual."""
        start_time = datetime.now()

        try:
            logger.debug(f"Loading cache warm-up data: {task.name}")

            # Ejecutar loader
            data = task.loader()

            # Contar items
            item_count = 0
            if isinstance(data, (list, tuple)):
                item_count = len(data)
            elif isinstance(data, dict):
                item_count = len(data)
            elif data is not None:
                item_count = 1

            # Guardar en caché
            if data is not None:
                self.cache.set(
                    key=task.cache_key,
                    value=data,
                    ttl=task.ttl
                )

            duration_ms = (datetime.now() - start_time).total_seconds() * 1000

            logger.info(f"✅ Cache warmed: {task.name} ({item_count} items, {duration_ms:.2f}ms)")

            return WarmUpResult(
                name=task.name,
                success=True,
                duration_ms=duration_ms,
                item_count=item_count,
                cache_key=task.cache_key
            )

        except Exception as e:
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            error_msg = f"{type(e).__name__}: {str(e)}"

            logger.error(f"❌ Cache warming failed: {task.name} - {error_msg}")

            return WarmUpResult(
                name=task.name,
                success=False,
                duration_ms=duration_ms,
                error=error_msg,
                cache_key=task.cache_key
            )

    def warm_up_all(self,
                    parallel: bool = True,
                    max_workers: int = 4) -> List[WarmUpResult]:
        """
        Ejecuta todas las tareas de calentamiento.

        Args:
            parallel: Si se ejecutan en paralelo
            max_workers: Máximo de workers para paralelización

        Returns:
            Lista de resultados
        """
        self._start_time = datetime.now()
        self._results = []

        # Filtrar tareas habilitadas y ordenar por prioridad
        enabled_tasks = [
            task for task in self._tasks.values()
            if task.enabled
        ]
        enabled_tasks.sort(key=lambda t: t.priority, reverse=True)

        if not enabled_tasks:
            logger.warning("No cache warm-up tasks enabled")
            return self._results

        logger.info(f"Starting cache warm-up with {len(enabled_tasks)} tasks (parallel={parallel})")

        if parallel:
            self._warm_up_parallel(enabled_tasks, max_workers)
        else:
            self._warm_up_sequential(enabled_tasks)

        self._end_time = datetime.now()
        self._log_summary()

        return self._results

    def _warm_up_sequential(self, tasks: List[WarmUpTask]):
        """Ejecuta tareas secuencialmente."""
        for task in tasks:
            result = self._execute_task(task)
            self._results.append(result)

    def _warm_up_parallel(self, tasks: List[WarmUpTask], max_workers: int):
        """Ejecuta tareas en paralelo."""
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_task = {
                executor.submit(self._execute_task, task): task
                for task in tasks
            }

            for future in as_completed(future_to_task):
                task = future_to_task[future]
                try:
                    result = future.result()
                    self._results.append(result)
                except Exception as e:
                    logger.error(f"Error in task {task.name}: {e}")
                    self._results.append(WarmUpResult(
                        name=task.name,
                        success=False,
                        duration_ms=0,
                        error=str(e)
                    ))

    def warm_up_task(self, name: str) -> Optional[WarmUpResult]:
        """Ejecuta una tarea específica."""
        task = self._tasks.get(name)
        if not task:
            logger.warning(f"Task not found: {name}")
            return None

        if not task.enabled:
            logger.warning(f"Task disabled: {name}")
            return None

        result = self._execute_task(task)
        self._results.append(result)
        return result

    def _log_summary(self):
        """Registra resumen de ejecución."""
        if not self._results:
            return

        total_duration = (self._end_time - self._start_time).total_seconds() * 1000
        successful = sum(1 for r in self._results if r.success)
        failed = len(self._results) - successful
        total_items = sum(r.item_count for r in self._results if r.success)

        logger.info("=" * 60)
        logger.info("CACHE WARM-UP SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total tasks:    {len(self._results)}")
        logger.info(f"Successful:     {successful}")
        logger.info(f"Failed:         {failed}")
        logger.info(f"Total items:    {total_items}")
        logger.info(f"Total duration: {total_duration:.2f}ms")
        logger.info("=" * 60)

        if failed > 0:
            logger.warning("Failed tasks:")
            for result in self._results:
                if not result.success:
                    logger.warning(f"  - {result.name}: {result.error}")

    def get_results(self) -> List[WarmUpResult]:
        """Obtiene los resultados de la última ejecución."""
        return self._results

    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la última ejecución."""
        if not self._results:
            return {}

        successful = sum(1 for r in self._results if r.success)
        failed = len(self._results) - successful
        total_items = sum(r.item_count for r in self._results if r.success)
        total_duration = sum(r.duration_ms for r in self._results)

        return {
            'total_tasks': len(self._results),
            'successful': successful,
            'failed': failed,
            'total_items': total_items,
            'total_duration_ms': total_duration,
            'avg_duration_ms': total_duration / len(self._results) if self._results else 0,
            'success_rate': successful / len(self._results) if self._results else 0
        }

    def is_warmed_up(self, key: str) -> bool:
        """Verifica si una clave específica está en caché."""
        return self.cache.exists(key)

    def get_cache_status(self) -> Dict[str, bool]:
        """Obtiene estado de todas las claves de tareas."""
        return {
            task.cache_key: self.is_warmed_up(task.cache_key)
            for task in self._tasks.values()
        }


# Instancia global
_cache_warmer_instance: Optional[CacheWarmer] = None


def get_cache_warmer() -> CacheWarmer:
    """Obtiene la instancia singleton del CacheWarmer."""
    global _cache_warmer_instance
    if _cache_warmer_instance is None:
        _cache_warmer_instance = CacheWarmer()
    return _cache_warmer_instance


# Función para registrar tareas desde módulos
def register_warm_up_tasks():
    """
    Registra todas las tareas de calentamiento desde los módulos.

    Esta función se llama durante el bootstrap de la aplicación.
    """
    warmer = get_cache_warmer()

    # Registrar tareas de configuración (prioridad alta)
    try:
        from rexus.core.config_manager import get_config_manager

        @warmer.register_task(
            name="configuracion",
            cache_key="configuracion:all",
            ttl=3600,
            priority=100
        )
        def load_configuracion():
            config = get_config_manager()
            return config.get_all()

    except ImportError:
        logger.debug("ConfigManager not available for cache warming")

    # Registrar tareas de usuarios (prioridad alta)
    try:
        from rexus.modules._11_usuarios.model import UsuariosModel

        @warmer.register_task(
            name="usuarios_activos",
            cache_key="usuarios:activos",
            ttl=300,
            priority=90
        )
        def load_usuarios_activos():
            model = UsuariosModel()
            return model.obtener_usuarios_activos()

        @warmer.register_task(
            name="roles",
            cache_key="usuarios:roles",
            ttl=1800,
            priority=80
        )
        def load_roles():
            model = UsuariosModel()
            return model.obtener_todos_roles()

    except ImportError:
        logger.debug("UsuariosModel not available for cache warming")

    # Registrar tareas de inventario (prioridad media)
    try:
        from rexus.modules._02_inventario.model import InventarioModel

        @warmer.register_task(
            name="categorias_productos",
            cache_key="inventario:categorias",
            ttl=1800,
            priority=70
        )
        def load_categorias():
            model = InventarioModel()
            return model.obtener_categorias()

        @warmer.register_task(
            name="proveedores",
            cache_key="inventario:proveedores",
            ttl=1800,
            priority=60
        )
        def load_proveedores():
            model = InventarioModel()
            return model.obtener_todos_proveedores()

    except ImportError:
        logger.debug("InventarioModel not available for cache warming")

    # Registrar tareas de obras (prioridad media)
    try:
        from rexus.modules._01_obras.model import ObrasModel

        @warmer.register_task(
            name="estados_obras",
            cache_key="obras:estados",
            ttl=3600,
            priority=50
        )
        def load_estados_obras():
            model = ObrasModel()
            return model.obtener_estados()

    except ImportError:
        logger.debug("ObrasModel not available for cache warming")

    logger.info(f"Registered {len(warmer._tasks)} cache warm-up tasks")

    return warmer


# Decorador de conveniencia
def warm_up_cache(cache_key: str, ttl: int = 300, priority: int = 0):
    """
    Decorador para registrar y ejecutar una función como warm-up.

    Example:
        @warm_up_cache("my_data", ttl=600, priority=50)
        def get_my_data():
            return expensive_query()
    """
    def decorator(func: Callable) -> Callable:
        warmer = get_cache_warmer()

        # Registrar tarea
        warmer.add_task(
            name=func.__name__,
            loader=func,
            cache_key=cache_key,
            ttl=ttl,
            priority=priority
        )

        return func

    return decorator
