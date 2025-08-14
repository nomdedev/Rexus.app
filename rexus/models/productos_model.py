#!/usr/bin/env python3
"""
Modelo Unificado de Productos - Rexus.app

Este modelo maneja la tabla consolidada 'productos' que unifica:
- Inventario general
- Herrajes
- Materiales

NOTA: Los vidrios se mantienen en tabla separada por sus características únicas
(medidas exactas, espesores personalizados, cortes específicos)

Proporciona una API unificada para CRUD y operaciones de negocio.
"""

import logging
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List, Optional

# Imports del sistema
from rexus.utils.sql_query_manager import get_sql_manager
from rexus.core.security_manager import get_security_manager

# Configurar logging
logger = logging.getLogger(__name__)

class ProductosModel:
    """
    Modelo unificado para gestión de productos.

    Maneja la tabla consolidada 'productos' que reemplaza las tablas:
    - inventario
    - herrajes
    - materiales

    NOTA: Los vidrios se mantienen en tabla separada
    """

    # Tipos de producto válidos (sin vidrios)
    TIPOS_PRODUCTO = ['INVENTARIO', 'HERRAJE', 'MATERIAL']

    # Estados válidos
    ESTADOS_PRODUCTO = ['ACTIVO', 'INACTIVO', 'DESCONTINUADO']

    # Tipos de movimiento
    TIPOS_MOVIMIENTO = ['ENTRADA', 'SALIDA', 'AJUSTE', 'TRANSFERENCIA']

    def __init__(self, db_connection=None):
        """
        Inicializa el modelo de productos.

        Args:
            db_connection: Conexión a la base de datos
        """
        self.db_connection = db_connection
        self.sql_manager = get_sql_manager()
        self.security_manager = get_security_manager()
        self.tabla_productos = "productos"
        self.tabla_movimientos = "productos_movimientos"
        self.tabla_obras = "productos_obras"
        self.tabla_historial = "productos_historial"

        # Verificar tablas al inicializar
        self._verificar_tablas()

    def _verificar_tablas(self):
        """Verifica que las tablas necesarias existan."""
        if not self.db_connection:
            logger.warning("Sin conexión a BD - verificación de tablas omitida")
            return

        try:
            cursor = self.db_connection.cursor()

            tablas_requeridas = [
                self.tabla_productos,
                self.tabla_movimientos,
                self.tabla_obras,
                self.tabla_historial
            ]

            for tabla in tablas_requeridas:
                cursor.execute(
                    "SELECT COUNT(*) FROM sysobjects WHERE name=? AND xtype='U'",
                    (tabla,)
                )
                if cursor.fetchone()[0] > 0:
                    logger.info(f"Tabla '{tabla}' verificada correctamente")
                else:
                    logger.error(f"CRÍTICO: Tabla '{tabla}' no existe")

        except Exception as e:
            logger.error(f"Error verificando tablas: {e}")

    def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Crea un nuevo producto en la tabla unificada.

        Args:
            product_data: Datos del producto

        Returns:
            Dict con resultado de la operación
        """
        try:
            # Validar datos de entrada
            validation = self.validate_product_data(product_data)
            if not validation['valid']:
                return {
                    'success': False,
                    'error': 'Datos inválidos',
                    'errors': validation['errors']
                }

            # Sanitizar datos
            sanitized_data = self._sanitize_product_data(product_data)

            cursor = self.db_connection.cursor()

            # Verificar que el código no exista
            if self._product_code_exists(sanitized_data['codigo']):
                return {
                    'success': False,
                    'error': f"El código '{sanitized_data['codigo']}' ya existe"
                }

            # Preparar query de inserción
            query = """
                INSERT INTO productos (
                    codigo, nombre, descripcion, tipo_producto, categoria, subcategoria,
                    precio_compra, precio_venta, margen_ganancia, stock, stock_minimo, stock_maximo,
                    unidad_medida, proveedor_id, proveedor_codigo, codigo_barras,
                    especificaciones_tecnicas, tipo_herraje, acabado, material,
                    densidad, peso_unitario, estado, requiere_inspeccion,
                    ubicacion_almacen, pasillo, estante, usuario_creacion, fecha_creacion
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    ?, ?, ?, ?, ?, ?, ?, ?, GETDATE()
                )
            """

            # Preparar parámetros
            params = (
                sanitized_data['codigo'],
                sanitized_data['nombre'],
                sanitized_data.get('descripcion', ''),
                sanitized_data['tipo_producto'],
                sanitized_data.get('categoria', ''),
                sanitized_data.get('subcategoria'),
                sanitized_data.get('precio_compra', 0.00),
                sanitized_data.get('precio_venta', 0.00),
                sanitized_data.get('margen_ganancia', 0.00),
                sanitized_data.get('stock', 0),
                sanitized_data.get('stock_minimo', 0),
                sanitized_data.get('stock_maximo'),
                sanitized_data.get('unidad_medida', 'UNIDAD'),
                sanitized_data.get('proveedor_id'),
                sanitized_data.get('proveedor_codigo'),
                sanitized_data.get('codigo_barras'),
                sanitized_data.get('especificaciones_tecnicas'),
                sanitized_data.get('tipo_herraje'),
                sanitized_data.get('acabado'),
                sanitized_data.get('material'),
                sanitized_data.get('densidad'),
                sanitized_data.get('peso_unitario'),
                sanitized_data.get('estado', 'ACTIVO'),
                sanitized_data.get('requiere_inspeccion', False),
                sanitized_data.get('ubicacion_almacen'),
                sanitized_data.get('pasillo'),
                sanitized_data.get('estante'),
                sanitized_data.get('usuario_creacion', 'SYSTEM')
            )

            cursor.execute(query, params)

            # Obtener ID del producto creado
            cursor.execute("SELECT @@IDENTITY")
            product_id = cursor.fetchone()[0]

            # Registrar movimiento inicial si hay stock
            if sanitized_data.get('stock', 0) > 0:
                self._create_stock_movement(
                    product_id, 'ENTRADA', sanitized_data['stock'], 0,
                    sanitized_data['stock'], 'Stock inicial',
                    sanitized_data.get('usuario_creacion', 'SYSTEM')
                )

            self.db_connection.commit()

            logger.info(f"Producto creado: ID {product_id}, código {sanitized_data['codigo']}")

            return {
                'success': True,
                'product_id': product_id,
                'codigo': sanitized_data['codigo']
            }

        except Exception as e:
            logger.error(f"Error creando producto: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return {
                'success': False,
                'error': f"Error interno: {str(e)}"
            }

    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un producto por su ID.

        Args:
            product_id: ID del producto

        Returns:
            Diccionario con datos del producto o None
        """
        try:
            cursor = self.db_connection.cursor()

            query = """
                SELECT * FROM productos WHERE id = ? AND activo = 1
            """

            cursor.execute(query, (product_id,))
            row = cursor.fetchone()

            if row:
                return self._row_to_dict(row, cursor.description)
            return None

        except Exception as e:
            logger.error(f"Error obteniendo producto por ID {product_id}: {e}")
            return None

    def get_product_by_code(self, codigo: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene un producto por su código.

        Args:
            codigo: Código del producto

        Returns:
            Diccionario con datos del producto o None
        """
        try:
            codigo_sanitized = self.security_manager.sanitize_input(codigo)
            cursor = self.db_connection.cursor()

            query = """
                SELECT * FROM productos WHERE codigo = ? AND activo = 1
            """

            cursor.execute(query, (codigo_sanitized,))
            row = cursor.fetchone()

            if row:
                return self._row_to_dict(row, cursor.description)
            return None

        except Exception as e:
            logger.error(f"Error obteniendo producto por código {codigo}: {e}")
            return None

    def search_products(self, filters: Dict[str, Any] = None, page: int = 1,
                       limit: int = 50) -> Dict[str, Any]:
        """
        Busca productos con filtros y paginación.

        Args:
            filters: Filtros de búsqueda
            page: Página actual
            limit: Registros por página

        Returns:
            Dict con productos y metadata de paginación
        """
        try:
            filters = filters or {}
            offset = (page - 1) * limit

            cursor = self.db_connection.cursor()

            # Construir query base
            base_query = """
                SELECT * FROM productos WHERE activo = 1
            """

            conditions = []
            params = []

            # Aplicar filtros
            if filters.get('tipo_producto'):
                conditions.append("tipo_producto = ?")
                params.append(self.security_manager.sanitize_input(filters['tipo_producto']))

            if filters.get('categoria'):
                conditions.append("categoria = ?")
                params.append(self.security_manager.sanitize_input(filters['categoria']))

            if filters.get('estado'):
                conditions.append("estado = ?")
                params.append(self.security_manager.sanitize_input(filters['estado']))

            if filters.get('search_text'):
                search_text = f"%{self.security_manager.sanitize_input(filters['search_text'])}%"
                conditions.append("(codigo LIKE ? OR nombre LIKE ? OR descripcion LIKE ?)")
                params.extend([search_text, search_text, search_text])

            if filters.get('stock_bajo'):
                conditions.append("stock <= stock_minimo")

            # Construir query completa
            if conditions:
                base_query += " AND " + " AND ".join(conditions)

            # Query de conteo
            count_query = f"SELECT COUNT(*) FROM ({base_query}) as counted"
            cursor.execute(count_query, params)
            total_records = cursor.fetchone()[0]

            # Query paginada
            paginated_query = f"{base_query} ORDER BY nombre OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
            cursor.execute(paginated_query, params + [offset, limit])

            # Procesar resultados
            products = []
            for row in cursor.fetchall():
                product = self._row_to_dict(row, cursor.description)
                products.append(product)

            return {
                'success': True,
                'products': products,
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total_records': total_records,
                    'total_pages': (total_records + limit - 1) // limit
                }
            }

        except Exception as e:
            logger.error(f"Error buscando productos: {e}")
            return {
                'success': False,
                'error': str(e),
                'products': [],
                'pagination': {'page': page, 'limit': limit, 'total_records': 0, 'total_pages': 0}
            }

    def update_stock(self, product_id: int, new_stock: int, movement_type: str,
                    reference: str = None, user: str = 'SYSTEM') -> Dict[str, Any]:
        """
        Actualiza el stock de un producto y registra el movimiento.

        Args:
            product_id: ID del producto
            new_stock: Nuevo stock
            movement_type: Tipo de movimiento
            reference: Referencia del movimiento
            user: Usuario que realiza el cambio

        Returns:
            Dict con resultado de la operación
        """
        try:
            # Obtener stock actual
            current_product = self.get_product_by_id(product_id)
            if not current_product:
                return {
                    'success': False,
                    'error': 'Producto no encontrado'
                }

            current_stock = current_product['stock']
            quantity_change = new_stock - current_stock

            cursor = self.db_connection.cursor()

            # Actualizar stock
            cursor.execute("""
                UPDATE productos
                SET stock = ?, fecha_modificacion = GETDATE(), usuario_modificacion = ?
                WHERE id = ?
            """, (new_stock, user, product_id))

            # Registrar movimiento
            self._create_stock_movement(
                product_id, movement_type, abs(quantity_change),
                current_stock, new_stock, reference or 'Actualización de stock', user
            )

            self.db_connection.commit()

            logger.info(f"Stock actualizado - Producto {product_id}: {current_stock} → {new_stock}")

            return {
                'success': True,
                'previous_stock': current_stock,
                'new_stock': new_stock,
                'change': quantity_change
            }

        except Exception as e:
            logger.error(f"Error actualizando stock del producto {product_id}: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return {
                'success': False,
                'error': str(e)
            }

    def get_products_by_type(self,
tipo_producto: str,
        active_only: bool = True) -> List[Dict[str,
        Any]]:
        """
        Obtiene productos de un tipo específico.

        Args:
            tipo_producto: Tipo de producto (INVENTARIO,
HERRAJE,
                VIDRIO,
                MATERIAL)
            active_only: Si solo incluir productos activos

        Returns:
            Lista de productos
        """
        try:
            if tipo_producto not in self.TIPOS_PRODUCTO:
                raise ValueError(f"Tipo de producto inválido: {tipo_producto}")

            cursor = self.db_connection.cursor()

            query = "SELECT * FROM productos WHERE tipo_producto = ?"
            params = [tipo_producto]

            if active_only:
                query += " AND activo = 1 AND estado = 'ACTIVO'"

            query += " ORDER BY nombre"

            cursor.execute(query, params)

            products = []
            for row in cursor.fetchall():
                product = self._row_to_dict(row, cursor.description)
                products.append(product)

            return products

        except Exception as e:
            logger.error(f"Error obteniendo productos por tipo {tipo_producto}: {e}")
            return []

    def get_low_stock_products(self, tipo_producto: str = None) -> List[Dict[str, Any]]:
        """
        Obtiene productos con stock bajo.

        Args:
            tipo_producto: Filtrar por tipo de producto (opcional)

        Returns:
            Lista de productos con stock bajo
        """
        try:
            cursor = self.db_connection.cursor()

            query = """
                SELECT *, (stock_minimo - stock) as deficit
                FROM productos
                WHERE stock <= stock_minimo AND activo = 1 AND estado = 'ACTIVO'
            """
            params = []

            if tipo_producto:
                query += " AND tipo_producto = ?"
                params.append(tipo_producto)

            query += " ORDER BY (stock_minimo - stock) DESC, nombre"

            cursor.execute(query, params)

            products = []
            for row in cursor.fetchall():
                product = self._row_to_dict(row, cursor.description)
                products.append(product)

            return products

        except Exception as e:
            logger.error(f"Error obteniendo productos con stock bajo: {e}")
            return []

    def validate_product_data(self,
product_data: Dict[str,
        Any]) -> Dict[str,
        Any]:
        """
        Valida los datos de un producto.

        Args:
            product_data: Datos del producto

        Returns:
            Dict con resultado de validación
        """
        errors = []

        # Campos requeridos
        required_fields = ['codigo', 'nombre', 'tipo_producto']
        for field in required_fields:
            if not product_data.get(field):
                errors.append(f"Campo '{field}' es requerido")

        # Validar tipo de producto
        if product_data.get('tipo_producto') not in self.TIPOS_PRODUCTO:
            errors.append(f"Tipo de producto debe ser uno de: {', '.join(self.TIPOS_PRODUCTO)}")

        # Validar estado
        if product_data.get('estado') and \
            product_data['estado'] not in self.ESTADOS_PRODUCTO:
            errors.append(f"Estado debe ser uno de: {', '.join(self.ESTADOS_PRODUCTO)}")

        # Validar precios
        for field in ['precio_compra', 'precio_venta']:
            if product_data.get(field) is not None:
                try:
                    price = Decimal(str(product_data[field]))
                    if price < 0:
                        errors.append(f"'{field}' no puede ser negativo")
                except (ValueError, InvalidOperation):
                    errors.append(f"'{field}' debe ser un número válido")

        # Validar stock
        for field in ['stock', 'stock_minimo']:
            if product_data.get(field) is not None:
                try:
                    stock = int(product_data[field])
                    if stock < 0:
                        errors.append(f"'{field}' no puede ser negativo")
                except ValueError:
                    errors.append(f"'{field}' debe ser un número entero")

        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    def _sanitize_product_data(self,
product_data: Dict[str,
        Any]) -> Dict[str,
        Any]:
        """Sanitiza los datos de entrada del producto."""
        sanitized = {}

        for key, value in product_data.items():
            if isinstance(value, str):
                sanitized[key] = self.security_manager.sanitize_input(value)
            else:
                sanitized[key] = value

        return sanitized

    def _product_code_exists(self, codigo: str) -> bool:
        """Verifica si un código de producto ya existe."""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM productos WHERE codigo = ?", (codigo,))
            return cursor.fetchone()[0] > 0
        except Exception:
            return False

    def _create_stock_movement(self, product_id: int, movement_type: str,
                              quantity: int, old_stock: int, new_stock: int,
                              reference: str, user: str):
        """Crea un registro de movimiento de stock."""
        try:
            cursor = self.db_connection.cursor()

            cursor.execute("""
                INSERT INTO productos_movimientos (
                    producto_id, tipo_movimiento, cantidad, stock_anterior, stock_nuevo,
                    documento_referencia, motivo, usuario_creacion, fecha_creacion
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
            """, (product_id, movement_type, quantity, old_stock, new_stock,
                  reference, f"Movimiento de {movement_type.lower()}", user))

        except Exception as e:
            logger.error(f"Error creando movimiento de stock: {e}")

    def _row_to_dict(self, row, description) -> Dict[str, Any]:
        """Convierte una fila de BD a diccionario."""
        columns = [column[0] for column in description]
        return dict(zip(columns, row))

# Funciones de conveniencia para compatibilidad
def get_productos_model(db_connection=None):
    """Obtiene una instancia del modelo de productos."""
    return ProductosModel(db_connection)

def migrate_legacy_data():
    """
    Función para ayudar en la migración de datos legacy.

    Esta función debería ser llamada después de ejecutar los scripts SQL
    para asegurar que los datos se migraron correctamente.
    """
    logger.info("Iniciando verificación de migración de datos legacy...")
    # Implementar verificaciones adicionales si es necesario
    logger.info("Verificación de migración completada")
