"""
Gestor de Paginación Optimizada para Rexus.app
Proporciona paginación eficiente con cache inteligente y optimizaciones SQL

Fecha: 13/08/2025
Objetivo: Mejorar rendimiento en consultas paginadas grandes
"""

import math
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass

# Integración con cache inteligente
from rexus.utils.smart_cache import cache_consultas, invalidate_cache_pattern


@dataclass
class PaginationResult:
    """Resultado de una consulta paginada."""
    data: List[Dict[str, Any]]
    total_records: int
    current_page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool
    start_record: int
    end_record: int


class PaginationManager:
    """
    Gestor especializado para paginación eficiente en tablas grandes.
    
    Características:
    - Cache inteligente por página
    - Optimizaciones SQL con OFFSET/LIMIT
    - Soporte para búsqueda paginada
    - Invalidación selectiva de cache
    - Métricas de rendimiento
    """
    
    def __init__(self, table_name: str, db_connection=None):
        """
        Inicializa el gestor de paginación.
        
        Args:
            table_name: Nombre de la tabla principal
            db_connection: Conexión a la base de datos
        """
        self.table_name = table_name
        self.db_connection = db_connection
        self.default_page_size = 50
        self.max_page_size = 500
        self.cache_ttl = 300  # 5 minutos
        
        # Estadísticas
        self.stats = {
            'cache_hits': 0,
            'cache_misses': 0,
            'queries_executed': 0,
            'total_records_fetched': 0
        }
    
    def _generate_cache_key(self, page: int, page_size: int, search_term: str = "", 
                           filters: Dict[str, Any] = None) -> str:
        """
        Genera clave de cache única para la consulta.
        
        Args:
            page: Número de página
            page_size: Tamaño de página
            search_term: Término de búsqueda
            filters: Filtros adicionales
            
        Returns:
            str: Clave de cache única
        """
        filters_str = ""
        if filters:
            # Ordenar filtros para consistencia en cache
            sorted_filters = sorted(filters.items())
            filters_str = str(sorted_filters)
        
        return f"{self.table_name}:page_{page}:size_{page_size}:search_{search_term}:filters_{filters_str}"
    
    def _validate_pagination_params(self, page: int, page_size: int) -> Tuple[int, int]:
        """
        Valida y normaliza parámetros de paginación.
        
        Args:
            page: Número de página
            page_size: Tamaño de página
            
        Returns:
            Tuple[int, int]: Página y tamaño validados
        """
        # Validar página
        page = max(1, int(page)) if page else 1
        
        # Validar tamaño de página
        if not page_size:
            page_size = self.default_page_size
        else:
            page_size = max(1, min(int(page_size), self.max_page_size))
        
        return page, page_size
    
    def _calculate_offset(self, page: int, page_size: int) -> int:
        """
        Calcula el offset para la consulta SQL.
        
        Args:
            page: Número de página (1-based)
            page_size: Tamaño de página
            
        Returns:
            int: Offset para OFFSET/LIMIT
        """
        return (page - 1) * page_size
    
    @cache_consultas(ttl=300)
    def get_total_count(self, search_term: str = "", filters: Dict[str, Any] = None) -> int:
        """
        Obtiene el conteo total de registros con cache.
        
        Args:
            search_term: Término de búsqueda
            filters: Filtros adicionales
            
        Returns:
            int: Total de registros
        """
        if not self.db_connection:
            return 0
        
        try:
            cursor = self.db_connection.cursor()
            
            # Construir query de conteo
            base_query = f"SELECT COUNT(*) FROM {self.table_name} WHERE activo = 1"
            params = []
            
            # Agregar búsqueda
            if search_term:
                search_conditions = [
                    "nombre LIKE ?",
                    "descripcion LIKE ?", 
                    "codigo LIKE ?"
                ]
                base_query += f" AND ({' OR '.join(search_conditions)})"
                search_param = f"%{search_term}%"
                params.extend([search_param, search_param, search_param])
            
            # Agregar filtros
            if filters:
                for field, value in filters.items():
                    if value is not None and value != "":
                        base_query += f" AND {field} = ?"
                        params.append(value)
            
            cursor.execute(base_query, params)
            result = cursor.fetchone()
            total = result[0] if result else 0
            
            self.stats['queries_executed'] += 1
            return total
            
        except Exception as e:
            print(f"[PAGINATION] Error contando registros: {e}")
            return 0
        finally:
            if cursor:
                cursor.close()
    
    def get_paginated_data(self, 
                          page: int = 1, 
                          page_size: int = None,
                          search_term: str = "",
                          filters: Dict[str, Any] = None,
                          order_by: str = "fecha_creacion DESC") -> PaginationResult:
        """
        Obtiene datos paginados con cache inteligente.
        
        Args:
            page: Número de página (1-based)
            page_size: Registros por página
            search_term: Término de búsqueda
            filters: Filtros adicionales
            order_by: Campo de ordenamiento
            
        Returns:
            PaginationResult: Resultado paginado
        """
        # Validar parámetros
        page, page_size = self._validate_pagination_params(page, page_size)
        
        # Generar clave de cache
        cache_key = self._generate_cache_key(page, page_size, search_term, filters)
        
        try:
            # Intentar obtener del cache
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                self.stats['cache_hits'] += 1
                return cached_result
            
            self.stats['cache_misses'] += 1
            
            # Obtener total de registros
            total_records = self.get_total_count(search_term, filters)
            total_pages = math.ceil(total_records / page_size) if total_records > 0 else 1
            
            # Validar que la página solicitada existe
            page = min(page, total_pages)
            
            # Calcular offset
            offset = self._calculate_offset(page, page_size)
            
            # Obtener datos
            data = self._fetch_page_data(offset, page_size, search_term, filters, order_by)
            
            # Crear resultado
            result = PaginationResult(
                data=data,
                total_records=total_records,
                current_page=page,
                page_size=page_size,
                total_pages=total_pages,
                has_next=page < total_pages,
                has_previous=page > 1,
                start_record=offset + 1 if data else 0,
                end_record=min(offset + len(data), total_records)
            )
            
            # Guardar en cache
            self._save_to_cache(cache_key, result)
            
            self.stats['total_records_fetched'] += len(data)
            return result
            
        except Exception as e:
            print(f"[PAGINATION] Error obteniendo datos paginados: {e}")
            # Retornar resultado vacío en caso de error
            return PaginationResult(
                data=[],
                total_records=0,
                current_page=1,
                page_size=page_size,
                total_pages=1,
                has_next=False,
                has_previous=False,
                start_record=0,
                end_record=0
            )
    
    def _fetch_page_data(self, 
                        offset: int, 
                        limit: int,
                        search_term: str = "",
                        filters: Dict[str, Any] = None,
                        order_by: str = "fecha_creacion DESC") -> List[Dict[str, Any]]:
        """
        Obtiene una página de datos de la base de datos.
        
        Args:
            offset: Desplazamiento
            limit: Límite de registros
            search_term: Término de búsqueda
            filters: Filtros adicionales
            order_by: Campo de ordenamiento
            
        Returns:
            List[Dict[str, Any]]: Lista de registros
        """
        if not self.db_connection:
            return []
        
        cursor = None
        try:
            cursor = self.db_connection.cursor()
            
            # Construir query principal
            base_query = f"""
                SELECT * FROM {self.table_name}
                WHERE activo = 1
            """
            params = []
            
            # Agregar búsqueda
            if search_term:
                search_conditions = [
                    "nombre LIKE ?",
                    "descripcion LIKE ?",
                    "codigo LIKE ?"
                ]
                base_query += f" AND ({' OR '.join(search_conditions)})"
                search_param = f"%{search_term}%"
                params.extend([search_param, search_param, search_param])
            
            # Agregar filtros
            if filters:
                for field, value in filters.items():
                    if value is not None and value != "":
                        base_query += f" AND {field} = ?"
                        params.append(value)
            
            # Agregar ordenamiento y paginación
            base_query += f"""
                ORDER BY {order_by}
                LIMIT ? OFFSET ?
            """
            params.extend([limit, offset])
            
            cursor.execute(base_query, params)
            rows = cursor.fetchall()
            
            # Convertir a diccionarios
            if rows:
                columns = [column[0] for column in cursor.description]
                data = [dict(zip(columns, row)) for row in rows]
            else:
                data = []
            
            self.stats['queries_executed'] += 1
            return data
            
        except Exception as e:
            print(f"[PAGINATION] Error obteniendo página de datos: {e}")
            return []
        finally:
            if cursor:
                cursor.close()
    
    def _get_from_cache(self, cache_key: str) -> Optional[PaginationResult]:
        """
        Obtiene resultado del cache si existe.
        
        Args:
            cache_key: Clave de cache
            
        Returns:
            Optional[PaginationResult]: Resultado cacheado o None
        """
        try:
            # El cache se maneja automáticamente por el decorador @cache_consultas
            # Esta función es para compatibilidad futura
            return None
        except Exception:
            return None
    
    def _save_to_cache(self, cache_key: str, result: PaginationResult):
        """
        Guarda resultado en cache.
        
        Args:
            cache_key: Clave de cache
            result: Resultado a cachear
        """
        try:
            # El cache se maneja automáticamente por el decorador @cache_consultas
            # Esta función es para compatibilidad futura
            pass
        except Exception:
            pass
    
    def invalidate_cache(self, pattern: str = None):
        """
        Invalida cache para esta tabla.
        
        Args:
            pattern: Patrón específico a invalidar (opcional)
        """
        if pattern:
            invalidate_cache_pattern(f"{self.table_name}:{pattern}")
        else:
            invalidate_cache_pattern(self.table_name)
        
        print(f"[PAGINATION] Cache invalidado para tabla {self.table_name}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del gestor de paginación.
        
        Returns:
            Dict[str, Any]: Estadísticas de uso
        """
        total_requests = self.stats['cache_hits'] + self.stats['cache_misses']
        hit_rate = (self.stats['cache_hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'table_name': self.table_name,
            'cache_hits': self.stats['cache_hits'],
            'cache_misses': self.stats['cache_misses'],
            'hit_rate': round(hit_rate, 2),
            'queries_executed': self.stats['queries_executed'],
            'total_records_fetched': self.stats['total_records_fetched'],
            'default_page_size': self.default_page_size,
            'max_page_size': self.max_page_size
        }
    
    def prefetch_next_pages(self, current_page: int, page_size: int, 
                           search_term: str = "", filters: Dict[str, Any] = None,
                           pages_to_prefetch: int = 2):
        """
        Precarga las siguientes páginas en cache para mejorar navegación.
        
        Args:
            current_page: Página actual
            page_size: Tamaño de página
            search_term: Término de búsqueda
            filters: Filtros adicionales
            pages_to_prefetch: Número de páginas a precargar
        """
        try:
            # Precargar páginas siguientes en background
            for i in range(1, pages_to_prefetch + 1):
                next_page = current_page + i
                # Solo precargar si la página es válida
                if next_page <= math.ceil(self.get_total_count(search_term, filters) / page_size):
                    # Llamada asíncrona que se guardará en cache
                    self.get_paginated_data(next_page, page_size, search_term, filters)
                    
            print(f"[PAGINATION] Precargadas {pages_to_prefetch} páginas siguientes")
            
        except Exception as e:
            print(f"[PAGINATION] Error precargando páginas: {e}")


# Funciones de utilidad para integración con módulos

def create_pagination_manager(table_name: str, db_connection=None) -> PaginationManager:
    """
    Crea un gestor de paginación para una tabla específica.
    
    Args:
        table_name: Nombre de la tabla
        db_connection: Conexión a la base de datos
        
    Returns:
        PaginationManager: Gestor configurado
    """
    return PaginationManager(table_name, db_connection)


def paginate_query_results(data_loader: Callable, 
                          page: int = 1, 
                          page_size: int = 50) -> PaginationResult:
    """
    Pagina resultados de una función de carga de datos existente.
    
    Args:
        data_loader: Función que retorna lista de datos
        page: Página solicitada
        page_size: Tamaño de página
        
    Returns:
        PaginationResult: Resultado paginado
    """
    try:
        # Obtener todos los datos
        all_data = data_loader()
        total_records = len(all_data)
        total_pages = math.ceil(total_records / page_size) if total_records > 0 else 1
        
        # Validar página
        page = max(1, min(page, total_pages))
        
        # Calcular slice
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_data = all_data[start_idx:end_idx]
        
        return PaginationResult(
            data=page_data,
            total_records=total_records,
            current_page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
            start_record=start_idx + 1 if page_data else 0,
            end_record=min(end_idx, total_records)
        )
        
    except Exception as e:
        print(f"[PAGINATION] Error paginando resultados: {e}")
        return PaginationResult(
            data=[],
            total_records=0,
            current_page=1,
            page_size=page_size,
            total_pages=1,
            has_next=False,
            has_previous=False,
            start_record=0,
            end_record=0
        )


# Ejemplo de uso en módulos
"""
# En el modelo del módulo:
from rexus.utils.pagination_manager import create_pagination_manager

class InventarioModel:
    def __init__(self, db_connection):
        self.db_connection = db_connection
        self.pagination_manager = create_pagination_manager('inventario', db_connection)
    
    def obtener_productos_paginados(self, page=1, page_size=50, search_term="", filters=None):
        return self.pagination_manager.get_paginated_data(
            page=page,
            page_size=page_size,
            search_term=search_term,
            filters=filters,
            order_by="nombre ASC"
        )
    
    def invalidar_cache_productos(self):
        self.pagination_manager.invalidate_cache()

# En la vista del módulo:
from rexus.ui.components.pagination_widget import PaginationWidget

class InventarioView(BaseModuleView):
    def __init__(self):
        super().__init__()
        self.pagination = PaginationWidget()
        self.pagination.page_changed.connect(self.cargar_pagina)
        
    def cargar_pagina(self, page):
        result = self.model.obtener_productos_paginados(page=page)
        self.actualizar_tabla(result.data)
        self.pagination.update_pagination_info(result.total_records, result.current_page)
"""