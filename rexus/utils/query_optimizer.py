#!/usr/bin/env python3
"""
Optimizador de Consultas - Rexus.app

Proporciona herramientas para optimizar consultas SQL y eliminar problemas N+1.
Incluye técnicas de batching, prefetch, y caching de consultas.

Fecha: 15/08/2025
Componente: Rendimiento - Optimización de Consultas
"""

import time
import threading
from functools import wraps
from collections import defaultdict, OrderedDict
from typing import Any, Dict, List, Optional, Tuple, Union, Callable
from datetime import datetime, timedelta

# Importar logging centralizado
try:
    from rexus.utils.app_logger import get_logger
    logger = get_logger("query_optimizer")
except ImportError:
    import logging
    logger = logging.getLogger("query_optimizer")


class QueryBatcher:
    """
    Agrupador de consultas para eliminar problemas N+1.
    Recolecta múltiples consultas similares y las ejecuta en batch.
    """

    def __init__(self, batch_size: int = 100, flush_interval: float = 0.1):
        """
        Inicializa el batcher.
        
        Args:
            batch_size: Número máximo de elementos por batch
            flush_interval: Intervalo en segundos para flush automático
        """
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self._batches = defaultdict(list)
        self._batch_callbacks = defaultdict(list)
        self._last_flush = time.time()
        self._lock = threading.Lock()

    def add_query(self, query_key: str, query_data: Any, callback: Callable):
        """
        Agrega una consulta al batch.
        
        Args:
            query_key: Clave que identifica el tipo de consulta
            query_data: Datos de la consulta (parámetros)
            callback: Función a llamar con el resultado
        """
        with self._lock:
            self._batches[query_key].append(query_data)
            self._batch_callbacks[query_key].append(callback)
            
            # Flush automático si alcanza el tamaño máximo
            if len(self._batches[query_key]) >= self.batch_size:
                self._flush_batch(query_key)
            
            # Flush automático por tiempo
            elif time.time() - self._last_flush > self.flush_interval:
                self.flush_all()

    def _flush_batch(self, query_key: str):
        """Ejecuta un batch específico."""
        if query_key not in self._batches or not self._batches[query_key]:
            return

        batch_data = self._batches[query_key]
        batch_callbacks = self._batch_callbacks[query_key]
        
        # Limpiar batches
        self._batches[query_key] = []
        self._batch_callbacks[query_key] = []
        
        try:
            # Ejecutar consulta optimizada
            results = self._execute_batch_query(query_key, batch_data)
            
            # Distribuir resultados a callbacks
            for callback, result in zip(batch_callbacks, results):
                callback(result)
                
        except Exception as e:
            logger.error(f"Error ejecutando batch {query_key}: {e}")
            # Notificar error a todos los callbacks
            for callback in batch_callbacks:
                callback(None)

    def _execute_batch_query(self, query_key: str, batch_data: List[Any]) -> List[Any]:
        """
        Ejecuta una consulta en batch. Debe ser implementado por subclases.
        
        Args:
            query_key: Tipo de consulta
            batch_data: Lista de parámetros de consulta
        
        Returns:
            List[Any]: Lista de resultados correspondientes
        """
        raise NotImplementedError("Subclases deben implementar _execute_batch_query")

    def flush_all(self):
        """Ejecuta todos los batches pendientes."""
        with self._lock:
            for query_key in list(self._batches.keys()):
                if self._batches[query_key]:
                    self._flush_batch(query_key)
            self._last_flush = time.time()


class DatabaseQueryBatcher(QueryBatcher):
    """Batcher específico para consultas de base de datos."""

    def __init__(self, db_connection, batch_size: int = 100, flush_interval: float = 0.1):
        """
        Inicializa el batcher de base de datos.
        
        Args:
            db_connection: Conexión a la base de datos
            batch_size: Tamaño máximo de batch
            flush_interval: Intervalo de flush automático
        """
        super().__init__(batch_size, flush_interval)
        self.db_connection = db_connection
        
        # Registrar consultas optimizables
        self._query_optimizers = {
            'get_by_ids': self._optimize_get_by_ids,
            'count_relations': self._optimize_count_relations,
            'get_relations': self._optimize_get_relations,
            'exists_check': self._optimize_exists_checks,
        }

    def _execute_batch_query(self, query_key: str, batch_data: List[Any]) -> List[Any]:
        """Ejecuta consulta en batch usando optimizadores específicos."""
        optimizer = self._query_optimizers.get(query_key)
        if optimizer:
            return optimizer(batch_data)
        else:
            logger.warning(f"No hay optimizador para query_key: {query_key}")
            return [None] * len(batch_data)

    def _optimize_get_by_ids(self, batch_data: List[Dict]) -> List[Any]:
        """
        Optimiza consultas get_by_id usando IN clause.
        
        Args:
            batch_data: Lista de {'table': str, 'id': int, 'columns': str}
        
        Returns:
            List[Any]: Resultados correspondientes
        """
        results = []
        
        # Agrupar por tabla y columnas
        grouped = defaultdict(list)
        for i, item in enumerate(batch_data):
            key = (item['table'], item.get('columns', '*'))
            grouped[key].append((i, item['id']))
        
        # Ejecutar consulta optimizada para cada grupo
        result_map = {}
        
        for (table, columns), items in grouped.items():
            indices, ids = zip(*items)
            
            # Crear consulta IN
            placeholders = ','.join(['?'] * len(ids))
            query = f"SELECT {columns} FROM {table} WHERE id IN ({placeholders})"
            
            try:
                cursor = self.db_connection.cursor()
                cursor.execute(query, ids)
                rows = cursor.fetchall()
                
                # Mapear resultados por ID
                for row in rows:
                    result_map[row[0]] = row  # Asumiendo que ID es la primera columna
                
            except Exception as e:
                logger.error(f"Error en batch query para {table}: {e}")
        
        # Organizar resultados en el orden original
        for i, item in enumerate(batch_data):
            results.append(result_map.get(item['id']))
        
        return results

    def _optimize_count_relations(self, batch_data: List[Dict]) -> List[int]:
        """
        Optimiza consultas de conteo de relaciones.
        
        Args:
            batch_data: Lista de {'table': str, 'foreign_key': str, 'parent_id': int}
        
        Returns:
            List[int]: Conteos correspondientes
        """
        results = []
        
        # Agrupar por tabla y foreign_key
        grouped = defaultdict(list)
        for i, item in enumerate(batch_data):
            key = (item['table'], item['foreign_key'])
            grouped[key].append((i, item['parent_id']))
        
        result_map = {}
        
        for (table, foreign_key), items in grouped.items():
            indices, parent_ids = zip(*items)
            
            # Crear consulta de conteo agrupado
            placeholders = ','.join(['?'] * len(parent_ids))
            query = f"""
                SELECT {foreign_key}, COUNT(*) 
                FROM {table} 
                WHERE {foreign_key} IN ({placeholders})
                GROUP BY {foreign_key}
            """
            
            try:
                cursor = self.db_connection.cursor()
                cursor.execute(query, parent_ids)
                rows = cursor.fetchall()
                
                # Mapear resultados
                for parent_id, count in rows:
                    result_map[parent_id] = count
                
            except Exception as e:
                logger.error(f"Error en count batch para {table}: {e}")
        
        # Organizar resultados (0 si no hay coincidencias)
        for i, item in enumerate(batch_data):
            results.append(result_map.get(item['parent_id'], 0))
        
        return results

    def _optimize_get_relations(self, batch_data: List[Dict]) -> List[List]:
        """
        Optimiza consultas para obtener relaciones múltiples.
        
        Args:
            batch_data: Lista de {'table': str, 'foreign_key': str, 'parent_id': int, 'columns': str}
        
        Returns:
            List[List]: Listas de registros relacionados
        """
        results = []
        
        # Agrupar por tabla, foreign_key y columnas
        grouped = defaultdict(list)
        for i, item in enumerate(batch_data):
            key = (item['table'], item['foreign_key'], item.get('columns', '*'))
            grouped[key].append((i, item['parent_id']))
        
        result_map = defaultdict(list)
        
        for (table, foreign_key, columns), items in grouped.items():
            indices, parent_ids = zip(*items)
            
            # Crear consulta IN para relaciones
            placeholders = ','.join(['?'] * len(parent_ids))
            query = f"""
                SELECT {foreign_key}, {columns}
                FROM {table} 
                WHERE {foreign_key} IN ({placeholders})
                ORDER BY {foreign_key}
            """
            
            try:
                cursor = self.db_connection.cursor()
                cursor.execute(query, parent_ids)
                rows = cursor.fetchall()
                
                # Agrupar resultados por parent_id
                for row in rows:
                    parent_id = row[0]
                    record = row[1:] if len(row) > 1 else row
                    result_map[parent_id].append(record)
                
            except Exception as e:
                logger.error(f"Error en relations batch para {table}: {e}")
        
        # Organizar resultados
        for i, item in enumerate(batch_data):
            results.append(result_map.get(item['parent_id'], []))
        
        return results

    def _optimize_exists_checks(self, batch_data: List[Dict]) -> List[bool]:
        """
        Optimiza verificaciones de existencia.
        
        Args:
            batch_data: Lista de {'table': str, 'column': str, 'value': Any}
        
        Returns:
            List[bool]: Resultados de existencia
        """
        results = []
        
        # Agrupar por tabla y columna
        grouped = defaultdict(list)
        for i, item in enumerate(batch_data):
            key = (item['table'], item['column'])
            grouped[key].append((i, item['value']))
        
        result_map = {}
        
        for (table, column), items in grouped.items():
            indices, values = zip(*items)
            
            # Crear consulta EXISTS optimizada
            placeholders = ','.join(['?'] * len(values))
            query = f"""
                SELECT DISTINCT {column}
                FROM {table} 
                WHERE {column} IN ({placeholders})
            """
            
            try:
                cursor = self.db_connection.cursor()
                cursor.execute(query, values)
                existing_values = {row[0] for row in cursor.fetchall()}
                
                # Mapear existencia
                for value in values:
                    result_map[value] = value in existing_values
                
            except Exception as e:
                logger.error(f"Error en exists batch para {table}: {e}")
        
        # Organizar resultados
        for i, item in enumerate(batch_data):
            results.append(result_map.get(item['value'], False))
        
        return results


class QueryCache:
    """Cache inteligente para consultas con TTL y invalidación."""

    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        """
        Inicializa el cache de consultas.
        
        Args:
            max_size: Tamaño máximo del cache
            default_ttl: TTL por defecto en segundos
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache = OrderedDict()
        self._timestamps = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        """Obtiene un valor del cache si no ha expirado."""
        with self._lock:
            if key not in self._cache:
                return None
            
            # Verificar TTL
            if self._is_expired(key):
                self._remove(key)
                return None
            
            # Mover al final (LRU)
            value = self._cache.pop(key)
            self._cache[key] = value
            
            return value

    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Almacena un valor en el cache."""
        with self._lock:
            # Usar TTL por defecto si no se especifica
            if ttl is None:
                ttl = self.default_ttl
            
            # Remover si ya existe
            if key in self._cache:
                self._remove(key)
            
            # Verificar límite de tamaño
            while len(self._cache) >= self.max_size:
                oldest_key = next(iter(self._cache))
                self._remove(oldest_key)
            
            # Agregar nuevo valor
            self._cache[key] = value
            self._timestamps[key] = {
                'created': time.time(),
                'ttl': ttl
            }

    def invalidate(self, pattern: str = None):
        """Invalida entradas del cache por patrón."""
        with self._lock:
            if pattern is None:
                # Limpiar todo
                self._cache.clear()
                self._timestamps.clear()
            else:
                # Limpiar por patrón
                keys_to_remove = []
                for key in self._cache:
                    if pattern in key:
                        keys_to_remove.append(key)
                
                for key in keys_to_remove:
                    self._remove(key)

    def _is_expired(self, key: str) -> bool:
        """Verifica si una entrada ha expirado."""
        if key not in self._timestamps:
            return True
        
        timestamp_data = self._timestamps[key]
        created = timestamp_data['created']
        ttl = timestamp_data['ttl']
        
        return time.time() - created > ttl

    def _remove(self, key: str):
        """Remueve una entrada del cache."""
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)

    def cleanup_expired(self):
        """Limpia entradas expiradas."""
        with self._lock:
            expired_keys = []
            for key in self._cache:
                if self._is_expired(key):
                    expired_keys.append(key)
            
            for key in expired_keys:
                self._remove(key)

    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del cache."""
        with self._lock:
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'default_ttl': self.default_ttl,
            }


class QueryOptimizer:
    """Optimizador principal que combina batching y caching."""

    def __init__(self, db_connection, cache_size: int = 1000, 
                 batch_size: int = 100, default_ttl: int = 300):
        """
        Inicializa el optimizador.
        
        Args:
            db_connection: Conexión a la base de datos
            cache_size: Tamaño del cache
            batch_size: Tamaño de los batches
            default_ttl: TTL por defecto del cache
        """
        self.db_connection = db_connection
        self.cache = QueryCache(cache_size, default_ttl)
        self.batcher = DatabaseQueryBatcher(db_connection, batch_size)
        
        # Estadísticas
        self._stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'batched_queries': 0,
            'individual_queries': 0,
        }

    def get_by_id(self, table: str, id_value: int, columns: str = '*', 
                  use_cache: bool = True, ttl: Optional[int] = None) -> Optional[Any]:
        """
        Obtiene un registro por ID con optimizaciones.
        
        Args:
            table: Nombre de la tabla
            id_value: ID del registro
            columns: Columnas a seleccionar
            use_cache: Si usar cache
            ttl: TTL específico para cache
        
        Returns:
            Optional[Any]: Registro encontrado o None
        """
        cache_key = f"get_by_id:{table}:{id_value}:{columns}"
        
        # Intentar obtener del cache
        if use_cache:
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                self._stats['cache_hits'] += 1
                return cached_result
            self._stats['cache_misses'] += 1
        
        # Ejecutar consulta individual
        query = f"SELECT {columns} FROM {table} WHERE id = ?"
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(query, (id_value,))
            result = cursor.fetchone()
            
            # Almacenar en cache
            if use_cache and result is not None:
                self.cache.set(cache_key, result, ttl)
            
            self._stats['individual_queries'] += 1
            return result
            
        except Exception as e:
            logger.error(f"Error en get_by_id para {table}:{id_value}: {e}")
            return None

    def get_by_ids_batched(self, table: str, id_values: List[int], 
                          columns: str = '*') -> Dict[int, Any]:
        """
        Obtiene múltiples registros por ID usando batching.
        
        Args:
            table: Nombre de la tabla
            id_values: Lista de IDs
            columns: Columnas a seleccionar
        
        Returns:
            Dict[int, Any]: Mapeo de ID a registro
        """
        if not id_values:
            return {}
        
        # Crear consulta IN optimizada
        placeholders = ','.join(['?'] * len(id_values))
        query = f"SELECT {columns} FROM {table} WHERE id IN ({placeholders})"
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(query, id_values)
            rows = cursor.fetchall()
            
            # Crear mapeo (asumiendo que ID es la primera columna)
            result_map = {}
            for row in rows:
                result_map[row[0]] = row
            
            self._stats['batched_queries'] += 1
            logger.debug(f"Batch query ejecutada para {len(id_values)} IDs en {table}")
            
            return result_map
            
        except Exception as e:
            logger.error(f"Error en get_by_ids_batched para {table}: {e}")
            return {}

    def count_relations(self, table: str, foreign_key: str, 
                       parent_ids: List[int]) -> Dict[int, int]:
        """
        Cuenta relaciones para múltiples padres usando batching.
        
        Args:
            table: Tabla de relaciones
            foreign_key: Clave foránea
            parent_ids: IDs de los padres
        
        Returns:
            Dict[int, int]: Mapeo de parent_id a conteo
        """
        if not parent_ids:
            return {}
        
        placeholders = ','.join(['?'] * len(parent_ids))
        query = f"""
            SELECT {foreign_key}, COUNT(*) 
            FROM {table} 
            WHERE {foreign_key} IN ({placeholders})
            GROUP BY {foreign_key}
        """
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(query, parent_ids)
            rows = cursor.fetchall()
            
            # Crear mapeo con 0 por defecto
            result_map = {pid: 0 for pid in parent_ids}
            for parent_id, count in rows:
                result_map[parent_id] = count
            
            self._stats['batched_queries'] += 1
            return result_map
            
        except Exception as e:
            logger.error(f"Error en count_relations para {table}: {e}")
            return {pid: 0 for pid in parent_ids}

    def invalidate_cache(self, pattern: str = None):
        """Invalida entradas del cache."""
        self.cache.invalidate(pattern)
        logger.debug(f"Cache invalidado con patrón: {pattern}")

    def get_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del optimizador."""
        cache_stats = self.cache.get_stats()
        
        total_queries = self._stats['cache_hits'] + self._stats['cache_misses']
        cache_hit_rate = (self._stats['cache_hits'] / total_queries * 100) if total_queries > 0 else 0
        
        return {
            'cache': cache_stats,
            'queries': self._stats.copy(),
            'cache_hit_rate': f"{cache_hit_rate:.1f}%",
        }

    def cleanup(self):
        """Limpia recursos y cache expirado."""
        self.cache.cleanup_expired()
        self.batcher.flush_all()


# Decorador para optimización automática
def optimize_query(use_cache: bool = True, ttl: Optional[int] = None, 
                  batch_key: Optional[str] = None):
    """
    Decorador para optimización automática de consultas.
    
    Args:
        use_cache: Si usar cache
        ttl: TTL específico para cache
        batch_key: Clave para agrupamiento en batches
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Extraer optimizador del contexto (debe ser inyectado)
            optimizer = getattr(wrapper, '_optimizer', None)
            if not optimizer:
                # Sin optimizador - ejecutar función normal
                return func(*args, **kwargs)
            
            # Generar clave de cache
            cache_key = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            
            # Intentar obtener del cache
            if use_cache:
                cached_result = optimizer.cache.get(cache_key)
                if cached_result is not None:
                    return cached_result
            
            # Ejecutar función original
            result = func(*args, **kwargs)
            
            # Almacenar en cache
            if use_cache and result is not None:
                optimizer.cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


# Función de utilidad para configurar optimizador
def setup_query_optimizer(db_connection, **kwargs) -> QueryOptimizer:
    """
    Configura y retorna un optimizador de consultas.
    
    Args:
        db_connection: Conexión a la base de datos
        **kwargs: Argumentos adicionales para el optimizador
    
    Returns:
        QueryOptimizer: Optimizador configurado
    """
    optimizer = QueryOptimizer(db_connection, **kwargs)
    logger.info("Query optimizer configurado exitosamente")
    return optimizer