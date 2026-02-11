"""
Sistema de Colas de Tareas - Rexus.app
Procesamiento asíncrono de tareas en background

Características:
- Colas en memoria o Redis
- Reintentos automáticos
- Prioridad de tareas
- Resultados persistentes
- Workers para procesamiento
"""

import json
import logging
import pickle
import queue
import threading
import time
import uuid
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, TypeVar
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')


class TaskStatus(Enum):
    """Estados de una tarea."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class TaskPriority(Enum):
    """Prioridades de tarea."""
    LOW = 3
    NORMAL = 2
    HIGH = 1
    CRITICAL = 0


@dataclass
class TaskResult:
    """Resultado de una tarea."""
    task_id: str
    status: TaskStatus
    result: Any = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    attempts: int = 0
    max_attempts: int = 3

    @property
    def duration_ms(self) -> Optional[float]:
        """Duración de la tarea en milisegundos."""
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            return delta.total_seconds() * 1000
        return None

    @property
    def is_finished(self) -> bool:
        """Si la tarea ha terminado (exitosa o fallidamente)."""
        return self.status in (TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED)


@dataclass(order=True)
class Task:
    """Tarea en cola."""
    priority: TaskPriority
    created_at: datetime = field(default_factory=datetime.now, compare=False)
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()), compare=False)
    func: Callable = field(default=None, compare=False)
    args: tuple = field(default_factory=tuple, compare=False)
    kwargs: dict = field(default_factory=dict, compare=False)
    max_attempts: int = 3
    timeout: int = 300  # segundos
    result: TaskResult = field(default=None, compare=False)

    def __post_init__(self):
        if self.result is None:
            self.result = TaskResult(
                task_id=self.task_id,
                status=TaskStatus.PENDING,
                max_attempts=self.max_attempts
            )


class QueueBackend(ABC):
    """Backend abstracto para colas."""

    @abstractmethod
    def push(self, task: Task) -> bool:
        """Agrega una tarea a la cola."""
        pass

    @abstractmethod
    def pop(self) -> Optional[Task]:
        """Obtiene la siguiente tarea de la cola."""
        pass

    @abstractmethod
    def peek(self) -> Optional[Task]:
        """Obtiene la siguiente tarea sin eliminarla."""
        pass

    @abstractmethod
    def size(self) -> int:
        """Tamaño de la cola."""
        pass

    @abstractmethod
    def clear(self):
        """Limpia la cola."""
        pass


class MemoryQueueBackend(QueueBackend):
    """Backend de cola en memoria."""

    def __init__(self):
        self._queue: queue.PriorityQueue = queue.PriorityQueue()
        self._tasks: Dict[str, Task] = {}
        self._lock = threading.Lock()

    def push(self, task: Task) -> bool:
        with self._lock:
            self._tasks[task.task_id] = task
            self._queue.put((task.priority, task.created_at.timestamp(), task))
            return True

    def pop(self) -> Optional[Task]:
        try:
            _, _, task = self._queue.get_nowait()
            with self._lock:
                if task.task_id in self._tasks:
                    del self._tasks[task.task_id]
            return task
        except queue.Empty:
            return None

    def peek(self) -> Optional[Task]:
        with self._lock:
            for task in self._tasks.values():
                if task.result.status == TaskStatus.PENDING:
                    return task
            return None

    def size(self) -> int:
        return self._queue.qsize()

    def clear(self):
        with self._lock]:
            self._queue = queue.PriorityQueue()
            self._tasks.clear()


class TaskQueue:
    """
    Gestor de cola de tareas.

    Permite ejecutar funciones en background con reintentos y prioridades.
    """

    def __init__(self,
                 backend: QueueBackend = None,
                 max_workers: int = 4,
                 worker_timeout: int = 300):
        """
        Inicializa la cola de tareas.

        Args:
            backend: Backend de cola (MemoryQueue por defecto)
            max_workers: Número máximo de workers
            worker_timeout: Timeout para cada tarea
        """
        self.backend = backend or MemoryQueueBackend()
        self.max_workers = max_workers
        self.worker_timeout = worker_timeout
        self._results: Dict[str, TaskResult] = {}
        self._workers: List[threading.Thread] = []
        self._running = False
        self._lock = threading.Lock()

    def enqueue(self,
                func: Callable,
                args: tuple = (),
                kwargs: dict = None,
                priority: TaskPriority = TaskPriority.NORMAL,
                max_attempts: int = 3,
                timeout: int = 300) -> str:
        """
        Agrega una tarea a la cola.

        Args:
            func: Función a ejecutar
            args: Argumentos posicionales
            kwargs: Argumentos nombrados
            priority: Prioridad de la tarea
            max_attempts: Máximo de reintentos
            timeout: Timeout en segundos

        Returns:
            ID de la tarea creada
        """
        task = Task(
            func=func,
            args=args,
            kwargs=kwargs or {},
            priority=priority,
            max_attempts=max_attempts,
            timeout=timeout
        )

        self.backend.push(task)
        self._results[task.task_id] = task.result

        logger.info(f"Task enqueued: {task.task_id} ({func.__name__})")

        return task.task_id

    def get_result(self, task_id: str, timeout: float = None) -> Optional[TaskResult]:
        """
        Obtiene el resultado de una tarea.

        Args:
            task_id: ID de la tarea
            timeout: Esperar hasta timeout segundos

        Returns:
            Resultado de la tarea o None si no existe
        """
        start_time = time.time()

        while True:
            with self._lock:
                result = self._results.get(task_id)

            if result is None:
                return None

            if result.is_finished:
                return result

            if timeout is not None:
                elapsed = time.time() - start_time
                if elapsed >= timeout:
                    return result

            time.sleep(0.1)

    def get_status(self, task_id: str) -> Optional[TaskStatus]:
        """Obtiene el estado de una tarea."""
        result = self._results.get(task_id)
        return result.status if result else None

    def cancel(self, task_id: str) -> bool:
        """
        Cancela una tarea pendiente.

        Args:
            task_id: ID de la tarea

        Returns:
            True si se canceló
        """
        with self._lock:
            result = self._results.get(task_id)
            if result and result.status == TaskStatus.PENDING:
                result.status = TaskStatus.CANCELLED
                return True
            return False

    def start(self):
        """Inicia los workers de procesamiento."""
        if self._running:
            return

        self._running = True

        for i in range(self.max_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f"TaskWorker-{i}",
                daemon=True
            )
            worker.start()
            self._workers.append(worker)

        logger.info(f"Started {self.max_workers} task workers")

    def stop(self):
        """Detiene los workers."""
        self._running = False

        for worker in self._workers:
            worker.join(timeout=5)

        self._workers.clear()
        logger.info("Stopped task workers")

    def _worker_loop(self):
        """Loop de procesamiento de tareas."""
        while self._running:
            task = self.backend.pop()

            if task is None:
                time.sleep(0.1)
                continue

            # Verificar si está cancelada
            result = self._results.get(task.task_id)
            if result.status == TaskStatus.CANCELLED:
                continue

            self._execute_task(task)

    def _execute_task(self, task: Task):
        """Ejecuta una tarea."""
        result = self._results.get(task.task_id)

        # Verificar reintentos
        if result.attempts >= result.max_attempts:
            result.status = TaskStatus.FAILED
            result.error = f"Max attempts ({result.max_attempts}) exceeded"
            result.completed_at = datetime.now()
            logger.error(f"Task failed after {result.attempts} attempts: {task.task_id}")
            return

        # Actualizar estado
        result.status = TaskStatus.RUNNING if result.attempts == 0 else TaskStatus.RETRYING
        result.started_at = datetime.now()
        result.attempts += 1

        logger.info(f"Executing task {task.task_id} (attempt {result.attempts}/{result.max_attempts})")

        try:
            # Ejecutar función
            func_result = task.func(*task.args, **task.kwargs)

            # Actualizar resultado exitoso
            result.status = TaskStatus.COMPLETED
            result.result = func_result
            result.completed_at = datetime.now()

            logger.info(f"Task completed: {task.task_id} in {result.duration_ms:.2f}ms")

        except Exception as e:
            error_msg = str(e)

            # Reintentar si es posible
            if result.attempts < result.max_attempts:
                result.status = TaskStatus.PENDING
                logger.warning(f"Task failed, retrying: {task.task_id} - {error_msg}")

                # Re-enqueue
                self.backend.push(task)

            else:
                result.status = TaskStatus.FAILED
                result.error = error_msg
                result.completed_at = datetime.now()

                logger.error(f"Task failed permanently: {task.task_id} - {error_msg}")

    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la cola."""
        with self._lock:
            total = len(self._results)
            pending = sum(1 for r in self._results.values() if r.status == TaskStatus.PENDING)
            running = sum(1 for r in self._results.values() if r.status == TaskStatus.RUNNING)
            completed = sum(1 for r in self._results.values() if r.status == TaskStatus.COMPLETED)
            failed = sum(1 for r in self._results.values() if r.status == TaskStatus.FAILED)

            return {
                'total_tasks': total,
                'pending': pending,
                'running': running,
                'completed': completed,
                'failed': failed,
                'queue_size': self.backend.size(),
                'workers': len(self._workers),
                'is_running': self._running
            }


# Instancia global
_task_queue_instance: Optional[TaskQueue] = None


def get_task_queue() -> TaskQueue:
    """Obtiene la instancia singleton del TaskQueue."""
    global _task_queue_instance
    if _task_queue_instance is None:
        _task_queue_instance = TaskQueue()
        _task_queue_instance.start()
    return _task_queue_instance


# Decorador para ejecutar en background
def background_task(priority: TaskPriority = TaskPriority.NORMAL,
                    max_attempts: int = 3,
                    timeout: int = 300):
    """
    Decorador para ejecutar una función en background.

    Args:
        priority: Prioridad de la tarea
        max_attempts: Máximo de reintentos
        timeout: Timeout en segundos

    Example:
        @background_task(priority=TaskPriority.HIGH)
        def enviar_email(email, mensaje):
            # Envía email en background
            pass

        # Uso
        task_id = enviar_email("user@example.com", "Hola!")
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> str:
            queue = get_task_queue()
            return queue.enqueue(
                func=func,
                args=args,
                kwargs=kwargs,
                priority=priority,
                max_attempts=max_attempts,
                timeout=timeout
            )

        # Agregar método para obtener resultado
        wrapper.get_result = lambda task_id: get_task_queue().get_result(task_id)

        return wrapper

    return decorator


# Función para ejecutar una tarea en background
def run_in_background(func: Callable,
                      args: tuple = (),
                      kwargs: dict = None,
                      priority: TaskPriority = TaskPriority.NORMAL) -> str:
    """
    Ejecuta una función en background.

    Args:
        func: Función a ejecutar
        args: Argumentos posicionales
        kwargs: Argumentos nombrados
        priority: Prioridad

    Returns:
        ID de la tarea
    """
    queue = get_task_queue()
    return queue.enqueue(
        func=func,
        args=args,
        kwargs=kwargs or {},
        priority=priority
    )
