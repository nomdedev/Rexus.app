"""
Producto Service - Servicio de Lógica de Negocio de Productos

Coordina operaciones de productos aplicando reglas de negocio
y validaciones.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from rexus.services.base import BaseService, ServiceResult, ValidationError
from rexus.repositories.inventario.productos_repository import ProductoRepository

logger = logging.getLogger(__name__)


class ProductoService(BaseService):
    """
    Servicio para gestión de productos de inventario.

    Aplica reglas de negocio como:
    - Validación de stock mínimo
    - Control de precios
    - Gestión de categorías
    - Notificaciones de stock bajo
    """

    REQUIRED_FIELDS = ['descripcion', 'categoria', 'precio_unitario']
    MIN_STOCK_DEFAULT = 10
    MAX_DESC_LENGTH = 200
    MAX_CATEGORIA_LENGTH = 50

    def __init__(self, db_connection, sql_manager=None, cache_manager=None):
        super().__init__(
            repository=ProductoRepository(db_connection, sql_manager),
            cache_manager=cache_manager
        )

    # ==================== OPERACIONES PRINCIPALES ====================

    def create_producto(self, producto_data: Dict[str, Any]) -> ServiceResult:
        """
        Crea un nuevo producto con validaciones.

        Args:
            producto_data: Datos del producto

        Returns:
            ServiceResult con el producto creado o errores de validación
        """
        # Validaciones
        validation_errors = self._validate_producto(producto_data)
        if validation_errors:
            return self.create_result(
                success=False,
                error="Errores de validación",
                validation_errors=[e.__dict__ for e in validation_errors]
            )

        # Aplicar valores por defecto
        producto_data['stock_actual'] = producto_data.get('stock_actual', 0)
        producto_data['stock_minimo'] = producto_data.get('stock_minimo', self.MIN_STOCK_DEFAULT)

        # Crear producto
        try:
            producto = self.repository.create(producto_data)
            self._log_operation('create_producto', {'producto_id': producto['id']})

            # Invalidar caché
            self._cache_invalidate_pattern('productos:*')

            return self.create_result(success=True, data=producto)
        except Exception as e:
            self._log_error('create_producto', e, {'producto_data': producto_data})
            return self.create_result(success=False, error=str(e))

    def update_producto(self, producto_id: int, producto_data: Dict[str, Any]) -> ServiceResult:
        """
        Actualiza un producto existente.

        Args:
            producto_id: ID del producto
            producto_data: Datos a actualizar

        Returns:
            ServiceResult con el producto actualizado
        """
        # Verificar que existe
        producto = self.repository.find_by_id(producto_id)
        if not producto:
            return self.create_result(
                success=False,
                error=f"Producto con ID {producto_id} no encontrado"
            )

        # Validaciones parciales (solo campos presentes)
        validation_errors = self._validate_producto_update(producto_data)
        if validation_errors:
            return self.create_result(
                success=False,
                error="Errores de validación",
                validation_errors=[e.__dict__ for e in validation_errors]
            )

        # Actualizar
        try:
            producto_data['id'] = producto_id
            producto_actualizado = self.repository.update(producto_data)
            self._log_operation('update_producto', {'producto_id': producto_id})

            # Invalidar caché
            self._cache_invalidate_pattern('productos:*')
            self._cache_delete(f'producto:{producto_id}')

            return self.create_result(success=True, data=producto_actualizado)
        except Exception as e:
            self._log_error('update_producto', e, {'producto_id': producto_id})
            return self.create_result(success=False, error=str(e))

    def delete_producto(self, producto_id: int) -> ServiceResult:
        """
        Elimina un producto (soft delete).

        Args:
            producto_id: ID del producto

        Returns:
            ServiceResult indicando éxito o fallo
        """
        try:
            deleted = self.repository.delete(producto_id)
            if not deleted:
                return self.create_result(
                    success=False,
                    error=f"Producto con ID {producto_id} no encontrado"
                )

            self._log_operation('delete_producto', {'producto_id': producto_id})

            # Invalidar caché
            self._cache_invalidate_pattern('productos:*')
            self._cache_delete(f'producto:{producto_id}')

            return self.create_result(success=True, data={'deleted': True})
        except Exception as e:
            self._log_error('delete_producto', e, {'producto_id': producto_id})
            return self.create_result(success=False, error=str(e))

    def get_producto(self, producto_id: int, use_cache: bool = True) -> ServiceResult:
        """
        Obtiene un producto por ID.

        Args:
            producto_id: ID del producto
            use_cache: Si usar caché

        Returns:
            ServiceResult con el producto
        """
        # Intentar caché primero
        if use_cache:
            cached = self._cache_get(f'producto:{producto_id}')
            if cached:
                return self.create_result(success=True, data=cached)

        # Buscar en BD
        try:
            producto = self.repository.find_by_id(producto_id)
            if not producto:
                return self.create_result(
                    success=False,
                    error=f"Producto con ID {producto_id} no encontrado"
                )

            # Guardar en caché
            if use_cache:
                self._cache_set(f'producto:{producto_id}', producto, ttl=3600)

            return self.create_result(success=True, data=producto)
        except Exception as e:
            self._log_error('get_producto', e, {'producto_id': producto_id})
            return self.create_result(success=False, error=str(e))

    def list_productos(self, filters: Dict[str, Any] = None,
                      categoria: str = None, low_stock: bool = False,
                      limit: int = None, offset: int = None) -> ServiceResult:
        """
        Lista productos con filtros opcionales.

        Args:
            filters: Filtros generales
            categoria: Filtrar por categoría
            low_stock: Solo productos con stock bajo
            limit: Límite de resultados
            offset: Desplazamiento

        Returns:
            ServiceResult con la lista de productos
        """
        try:
            # Construir filtros
            query_filters = filters or {}
            if categoria:
                query_filters['categoria'] = categoria
            if low_stock:
                query_filters['stock_bajo'] = True

            productos = self.repository.find_all(
                filters=query_filters,
                limit=limit,
                offset=offset
            )

            return self.create_result(
                success=True,
                data=productos,
                count=len(productos)
            )
        except Exception as e:
            self._log_error('list_productos', e)
            return self.create_result(success=False, error=str(e))

    # ==================== OPERACIONES ESPECIALIZADAS ====================

    def adjust_stock(self, producto_id: int, cantidad: int,
                    motivo: str = None) -> ServiceResult:
        """
        Ajusta el stock de un producto.

        Args:
            producto_id: ID del producto
            cantidad: Cantidad a ajustar (positiva o negativa)
            motivo: Motivo del ajuste

        Returns:
            ServiceResult con el resultado
        """
        # Validaciones
        errors = self.validate_numeric(
            cantidad,
            min_value=-10000,
            max_value=10000,
            field_name="cantidad"
        )
        if errors:
            return self.create_result(
                success=False,
                error="Cantidad inválida",
                validation_errors=[e.__dict__ for e in errors]
            )

        try:
            updated = self.repository.update_stock(producto_id, cantidad)
            if not updated:
                return self.create_result(
                    success=False,
                    error=f"Producto con ID {producto_id} no encontrado"
                )

            # Verificar stock bajo después del ajuste
            producto = self.repository.find_by_id(producto_id)
            is_low_stock = producto['stock_actual'] <= producto['stock_minimo']

            self._log_operation('adjust_stock', {
                'producto_id': producto_id,
                'cantidad': cantidad,
                'motivo': motivo,
                'nuevo_stock': producto['stock_actual'],
                'stock_bajo': is_low_stock
            })

            # Invalidar caché
            self._cache_delete(f'producto:{producto_id}')
            self._cache_invalidate_pattern('productos:*')

            result_data = {
                'producto_id': producto_id,
                'stock_actual': producto['stock_actual'],
                'stock_bajo': is_low_stock
            }

            return self.create_result(success=True, data=result_data)
        except Exception as e:
            self._log_error('adjust_stock', e, {'producto_id': producto_id, 'cantidad': cantidad})
            return self.create_result(success=False, error=str(e))

    def get_estadisticas(self, use_cache: bool = True) -> ServiceResult:
        """
        Obtiene estadísticas del inventario.

        Args:
            use_cache: Si usar caché

        Returns:
            ServiceResult con estadísticas
        """
        # Intentar caché
        if use_cache:
            cached = self._cache_get('inventario:estadisticas')
            if cached:
                return self.create_result(success=True, data=cached)

        try:
            stats = self.repository.get_statistics()

            # Agregar productos con stock bajo
            productos_bajo_stock = self.repository.find_low_stock()
            stats['productos_bajo_stock'] = productos_bajo_stock

            # Guardar en caché (TTL: 5 minutos)
            if use_cache:
                self._cache_set('inventario:estadisticas', stats, ttl=300)

            return self.create_result(success=True, data=stats)
        except Exception as e:
            self._log_error('get_estadisticas', e)
            return self.create_result(success=False, error=str(e))

    # ==================== VALIDACIONES ====================

    def _validate_producto(self, producto_data: Dict[str, Any]) -> List[ValidationError]:
        """Valida un producto completo."""
        errors = []

        # Campos requeridos
        errors.extend(self.validate_required(producto_data, self.REQUIRED_FIELDS))

        # Descripción
        if 'descripcion' in producto_data:
            errors.extend(self.validate_length(
                producto_data['descripcion'],
                min_length=3,
                max_length=self.MAX_DESC_LENGTH,
                field_name='descripcion'
            ))

        # Categoría
        if 'categoria' in producto_data:
            errors.extend(self.validate_length(
                producto_data['categoria'],
                min_length=2,
                max_length=self.MAX_CATEGORIA_LENGTH,
                field_name='categoria'
            ))

        # Precio
        if 'precio_unitario' in producto_data:
            errors.extend(self.validate_numeric(
                producto_data['precio_unitario'],
                min_value=0.01,
                max_value=1000000,
                field_name='precio_unitario'
            ))

        # Stock
        if 'stock_actual' in producto_data:
            errors.extend(self.validate_numeric(
                producto_data['stock_actual'],
                min_value=0,
                max_value=100000,
                field_name='stock_actual'
            ))

        if 'stock_minimo' in producto_data:
            errors.extend(self.validate_numeric(
                producto_data['stock_minimo'],
                min_value=0,
                max_value=10000,
                field_name='stock_minimo'
            ))

        return errors

    def _validate_producto_update(self, producto_data: Dict[str, Any]) -> List[ValidationError]:
        """Valida datos de actualización (validaciones parciales)."""
        errors = []

        # Solo validar campos presentes
        if 'descripcion' in producto_data:
            errors.extend(self.validate_length(
                producto_data['descripcion'],
                min_length=3,
                max_length=self.MAX_DESC_LENGTH,
                field_name='descripcion'
            ))

        if 'categoria' in producto_data:
            errors.extend(self.validate_length(
                producto_data['categoria'],
                min_length=2,
                max_length=self.MAX_CATEGORIA_LENGTH,
                field_name='categoria'
            ))

        if 'precio_unitario' in producto_data:
            errors.extend(self.validate_numeric(
                producto_data['precio_unitario'],
                min_value=0.01,
                max_value=1000000,
                field_name='precio_unitario'
            ))

        if 'stock_actual' in producto_data:
            errors.extend(self.validate_numeric(
                producto_data['stock_actual'],
                min_value=0,
                max_value=100000,
                field_name='stock_actual'
            ))

        if 'stock_minimo' in producto_data:
            errors.extend(self.validate_numeric(
                producto_data['stock_minimo'],
                min_value=0,
                max_value=10000,
                field_name='stock_minimo'
            ))

        return errors
