"""
Base Repository - Repositorio Abstracto

Proporciona la interfaz base para todos los repositorios con operaciones CRUD
y métodos comunes de acceso a datos.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, TypeVar, Generic
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')


@dataclass
class RepositoryConfig:
    """Configuración del repositorio."""
    table_name: str
    primary_key: str = 'id'
    soft_delete: bool = True
    timestamps: bool = True


class BaseRepository(ABC, Generic[T]):
    """
    Repositorio base abstracto con operaciones CRUD.

    Proporciona una interfaz estándar para acceder a datos, desacoplando
    la lógica de negocio de la implementación de base de datos.
    """

    def __init__(self, db_connection, sql_manager=None, config: RepositoryConfig = None):
        """
        Inicializa el repositorio.

        Args:
            db_connection: Conexión a la base de datos
            sql_manager: Gestor de consultas SQL (opcional)
            config: Configuración del repositorio
        """
        self.db_connection = db_connection
        self.sql_manager = sql_manager
        self.config = config or RepositoryConfig(table_name='tabla')
        self._logger = logger

    # ==================== CRUD BÁSICO ====================

    @abstractmethod
    def find_by_id(self, id: int) -> Optional[T]:
        """
        Busca una entidad por su ID.

        Args:
            id: ID de la entidad

        Returns:
            Entidad encontrada o None
        """
        pass

    @abstractmethod
    def find_all(self, filters: Dict[str, Any] = None, limit: int = None,
                 offset: int = None, order_by: str = None) -> List[T]:
        """
        Busca todas las entidades con filtros opcionales.

        Args:
            filters: Filtros a aplicar
            limit: Límite de resultados
            offset: Desplazamiento para paginación
            order_by: Campo para ordenar

        Returns:
            Lista de entidades
        """
        pass

    @abstractmethod
    def create(self, entity: T) -> T:
        """
        Crea una nueva entidad.

        Args:
            entity: Entidad a crear

        Returns:
            Entidad creada con ID asignado
        """
        pass

    @abstractmethod
    def update(self, entity: T) -> T:
        """
        Actualiza una entidad existente.

        Args:
            entity: Entidad a actualizar

        Returns:
            Entidad actualizada
        """
        pass

    @abstractmethod
    def delete(self, id: int) -> bool:
        """
        Elimina una entidad (soft delete si está configurado).

        Args:
            id: ID de la entidad a eliminar

        Returns:
            True si se eliminó correctamente
        """
        pass

    # ==================== MÉTODOS DE BÚSQUEDA ====================

    def find_one(self, filters: Dict[str, Any]) -> Optional[T]:
        """
        Busca una entidad que coincida con los filtros.

        Args:
            filters: Filtros a aplicar

        Returns:
            Primera entidad encontrada o None
        """
        results = self.find_all(filters=filters, limit=1)
        return results[0] if results else None

    def find_by_ids(self, ids: List[int]) -> List[T]:
        """
        Busca múltiples entidades por sus IDs.

        Args:
            ids: Lista de IDs

        Returns:
            Lista de entidades encontradas
        """
        if not ids:
            return []

        # Usar IN clause para eficiente búsqueda múltiple
        return self.find_all(filters={
            f"{self.config.primary_key}__in": ids
        })

    def exists(self, id: int) -> bool:
        """
        Verifica si existe una entidad por ID.

        Args:
            id: ID a verificar

        Returns:
            True si existe
        """
        return self.find_by_id(id) is not None

    def count(self, filters: Dict[str, Any] = None) -> int:
        """
        Cuenta entidades que coinciden con filtros.

        Args:
            filters: Filtros a aplicar (opcional)

        Returns:
            Número de entidades
        """
        # Implementación por defecto (puede ser sobreescrita)
        results = self.find_all(filters=filters)
        return len(results)

    # ==================== MÉTODOS DE BATCH ====================

    def create_many(self, entities: List[T]) -> List[T]:
        """
        Crea múltiples entidades en batch.

        Args:
            entities: Lista de entidades a crear

        Returns:
            Lista de entidades creadas
        """
        return [self.create(entity) for entity in entities]

    def update_many(self, entities: List[T]) -> List[T]:
        """
        Actualiza múltiples entidades en batch.

        Args:
            entities: Lista de entidades a actualizar

        Returns:
            Lista de entidades actualizadas
        """
        return [self.update(entity) for entity in entities]

    def delete_many(self, ids: List[int]) -> int:
        """
        Elimina múltiples entidades.

        Args:
            ids: Lista de IDs a eliminar

        Returns:
            Número de entidades eliminadas
        """
        count = 0
        for id in ids:
            if self.delete(id):
                count += 1
        return count

    # ==================== MÉTODOS DE UTILIDAD ====================

    def _execute_query(self, query: str, params: tuple = None) -> Any:
        """
        Ejecuta una query SQL y devuelve el cursor.

        Args:
            query: Query SQL a ejecutar
            params: Parámetros de la query

        Returns:
            Cursor con resultados
        """
        if not self.db_connection or not self.db_connection.connection:
            raise RuntimeError("No hay conexión a base de datos")

        cursor = self.db_connection.connection.cursor()
        cursor.execute(query, params or ())
        return cursor

    def _log_operation(self, operation: str, details: Dict[str, Any]):
        """
        Registra una operación del repositorio.

        Args:
            operation: Tipo de operación
            details: Detalles de la operación
        """
        log_details = {
            'table': self.config.table_name,
            'operation': operation,
            **details
        }
        self._logger.debug(f"Repository operation: {log_details}")

    def _validate_entity(self, entity: T) -> bool:
        """
        Valida una entidad antes de persistirla.

        Args:
            entity: Entidad a validar

        Returns:
            True si es válida
        """
        # Implementación por defecto (sobreescibir si necesario)
        return entity is not None
