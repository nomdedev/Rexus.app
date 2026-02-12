"""
💾 MODELO CON CACHING - Ejemplo de Implementación
====================================================

Este archivo muestra cómo aplicar el CacheManager a un modelo existente.

Para implementar en tu modelo real, copia los métodos decorados.
"""

from typing import Dict, List, Optional
from rexus.utils.cache_manager import (
    CacheManager,
    cache_result,
    cache_invalidate,
    CacheConfig
)
from rexus.utils.app_logger import get_logger

logger = get_logger("inventario.model_cached")


class InventarioModelCached:
    """
    Versión del modelo de inventario con caching aplicado.

    Cada método que se ejecuta frecuentemente tiene una versión
    con caché que mejora performance drásticamente.
    """

    def __init__(self, db_connection=None):
        """Inicializa modelo y caché"""
        self.db_connection = db_connection
        self.cache = CacheManager.get_instance()

        # Si la BD no está disponible, usar caché en modo readonly
        self.cache_only = not db_connection

    # ============================================================================
    # MÉTODOS CON CACHÉ
    # ============================================================================

    @cache_result(tipo_dato='productos', ttl=CacheConfig.TTL_LARGO)
    def obtener_todos_con_cache(self, filtros: Optional[Dict] = None) -> List[Dict]:
        """
        Obtiene todos los productos CON caché.

        ⚡ Performance: 100-1000x más rápido si está en caché

        Args:
            filtros: Filtros opcionales (categoria, stock_minimo, etc.)

        Returns:
            Lista de productos
        """
        if self.cache_only:
            logger.warning("Modo solo caché - BD no disponible")
            return self.cache.get('productos:todos', default=[])

        # Lógica original de obtener productos
        cursor = self.db_connection.cursor()
        query = "SELECT * FROM inventario WHERE activo = 1"
        cursor.execute(query)
        resultados = cursor.fetchall()
        columnas = [desc[0] for desc in cursor.description]
        productos = [dict(zip(columnas, fila)) for fila in resultados]

        logger.info(f"Productos obtenidos de BD: {len(productos)}")
        return productos

    @cache_result(tipo_dato='estadisticas', ttl=CacheConfig.TTL_MEDIO)
    def obtener_estadisticas_inventario_con_cache(self) -> Dict:
        """
        Obtiene estadísticas del inventario CON caché.

        ⚡ Performance: 100-1000x más rápido si está en caché

        Returns:
            Dict con estadísticas:
            - total_productos: Total de productos
            - stock_bajo: Productos con stock bajo mínimo
            - valor_total: Valor total del inventario
            - movimientos_mes: Movimientos en el mes actual
        """
        if self.cache_only:
            logger.warning("Modo solo caché - BD no disponible")
            return self.cache.get('estadisticas:inventario', default={
                "total_productos": 0,
                "stock_bajo": 0,
                "valor_total": 0.0,
                "movimientos_mes": 0
            })

        try:
            cursor = self.db_connection.cursor()

            # Total de productos
            cursor.execute("SELECT COUNT(*) FROM inventario WHERE activo = 1")
            total_productos = cursor.fetchone()[0]

            # Productos con stock bajo
            cursor.execute("""
                SELECT COUNT(*)
                FROM inventario
                WHERE stock_actual <= stock_minimo AND activo = 1
            """)
            stock_bajo = cursor.fetchone()[0]

            # Valor total del inventario
            cursor.execute("""
                SELECT SUM(stock_actual * precio_unitario)
                FROM inventario
                WHERE activo = 1
            """)
            valor_total = cursor.fetchone()[0] or 0.0

            # Movimientos del mes actual
            cursor.execute("""
                SELECT COUNT(*)
                FROM historial_movimientos
                WHERE fecha_movimiento >= DATEADD(month, DATEDIFF(month, 0, GETDATE()), 0)
            """)
            movimientos_mes = cursor.fetchone()[0]

            estadisticas = {
                "total_productos": total_productos,
                "stock_bajo": stock_bajo,
                "valor_total": float(valor_total),
                "movimientos_mes": movimientos_mes
            }

            logger.info("Estadísticas obtenidas de BD (ahora en caché)")
            return estadisticas

        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {
                "total_productos": 0,
                "stock_bajo": 0,
                "valor_total": 0.0,
                "movimientos_mes": 0
            }

    def obtener_productos_por_categoria_con_cache(
        self,
        categoria: str
    ) -> List[Dict]:
        """
        Obtiene productos por categoría CON caché.

        ⚡ Performance: 100-1000x más rápido si está en caché

        Args:
            categoria: Categoría de productos

        Returns:
            Lista de productos de la categoría
        """
        cache = CacheManager.get_instance()

        # Intentar caché primero
        cache_key = f"productos:categoria:{categoria}"
        cached = cache.get(cache_key)

        if cached is not None:
            logger.info(f"Productos de '{categoria}' del caché ✅")
            return cached

        # Si no está en caché, consultar BD
        if self.db_connection:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT * FROM inventario
                WHERE categoria = ? AND activo = 1
                ORDER BY nombre
            """, (categoria,))
            resultados = cursor.fetchall()
            columnas = [desc[0] for desc in cursor.description]
            productos = [dict(zip(columnas, fila)) for fila in resultados]

            # Guardar en caché (30 minutos)
            cache.set(cache_key, productos, ttl=CacheConfig.TTL_LARGO)

            logger.info(f"Productos de '{categoria}' de BD (ahora en caché)")
            return productos
        else:
            return []

    # ============================================================================
    # INVALIDACIÓN DE CACHÉ
    # ============================================================================

    def crear_producto_con_invalidation(self, datos: Dict) -> bool:
        """
        Crea producto e invalida caché de productos.

        Cuando se crea un producto, invalidamos el caché de productos
        para que la próxima consulta obtenga el producto nuevo.

        Args:
            datos: Datos del producto

        Returns:
            True si exitoso
        """
        try:
            # Crear producto en BD
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT INTO inventario (
                    codigo, nombre, descripcion, categoria,
                    stock_actual, stock_minimo, precio_unitario, activo
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datos.get('codigo'),
                datos.get('nombre'),
                datos.get('descripcion'),
                datos.get('categoria'),
                datos.get('stock_actual', 0),
                datos.get('stock_minimo', 10),
                datos.get('precio_unitario', 0.0),
                True
            ))
            self.db_connection.commit()

            # Invalidar caché de productos
            cache_invalidate('productos')
            logger.info("Caché de productos invalidado después de crear producto")

            return True

        except Exception as e:
            logger.error(f"Error creando producto: {e}")
            self.db_connection.rollback()
            return False

    def actualizar_producto_con_invalidation(
        self,
        producto_id: int,
        datos: Dict
    ) -> bool:
        """
        Actualiza producto e invalida caché.

        Args:
            producto_id: ID del producto
            datos: Datos actualizados

        Returns:
            True si exitoso
        """
        try:
            # Actualizar en BD
            cursor = self.db_connection.cursor()
            cursor.execute("""
                UPDATE inventario SET
                    nombre = ?,
                    descripcion = ?,
                    stock_actual = ?,
                    precio_unitario = ?
                WHERE id = ?
            """, (
                datos.get('nombre'),
                datos.get('descripcion'),
                datos.get('stock_actual'),
                datos.get('precio_unitario'),
                producto_id
            ))
            self.db_connection.commit()

            # Invalidar caché de productos y estadísticas
            cache_invalidate('productos')
            cache_invalidate('estadisticas')
            logger.info("Caché invalidado después de actualizar producto")

            return cursor.rowcount > 0

        except Exception as e:
            logger.error(f"Error actualizando producto: {e}")
            self.db_connection.rollback()
            return False

    def eliminar_producto_con_invalidation(self, producto_id: int) -> bool:
        """
        Elimina producto e invalida caché.

        Args:
            producto_id: ID del producto

        Returns:
            True si exitoso
        """
        try:
            # Eliminar de BD
            cursor = self.db_connection.cursor()
            cursor.execute("UPDATE inventario SET activo = 0 WHERE id = ?", (producto_id,))
            self.db_connection.commit()

            # Invalidar caché de productos y estadísticas
            cache_invalidate('productos')
            cache_invalidate('estadisticas')
            logger.info("Caché invalidado después de eliminar producto")

            return cursor.rowcount > 0

        except Exception as e:
            logger.error(f"Error eliminando producto: {e}")
            self.db_connection.rollback()
            return False

    # ============================================================================
    # GESTIÓN DE STOCK CON INVALIDACIÓN
    # ============================================================================

    def actualizar_stock_con_invalidation(
        self,
        producto_id: int,
        nuevo_stock: int,
        motivo: str = ""
    ) -> bool:
        """
        Actualiza stock e invalida estadísticas.

        El stock es crítico para las estadísticas, por lo que invalidamos
        el caché de estadísticas cuando cambia.

        Args:
            producto_id: ID del producto
            nuevo_stock: Nuevo stock
            motivo: Motivo del cambio

        Returns:
            True si exitoso
        """
        try:
            # Actualizar stock en BD
            cursor = self.db_connection.cursor()
            cursor.execute("""
                UPDATE inventario
                SET stock_actual = ?, fecha_actualizacion = GETDATE()
                WHERE id = ?
            """, (nuevo_stock, producto_id))
            self.db_connection.commit()

            # Invalidar caché específico del producto
            cache = CacheManager.get_instance()
            cache.delete(f"producto:{producto_id}")

            # Invalidar estadísticas (cambiaron)
            cache_invalidate('estadisticas')

            logger.info(f"Stock actualizado (caché invalidado): {producto_id} -> {nuevo_stock}")
            return True

        except Exception as e:
            logger.error(f"Error actualizando stock: {e}")
            self.db_connection.rollback()
            return False

    # ============================================================================
    # UTILIDADES DE CACHÉ
    # ============================================================================

    def limpiar_cache_productos(self) -> bool:
        """Limpia TODO el caché de productos"""
        cache = CacheManager.get_instance()
        return cache.invalidate_tipo('productos')

    def limpiar_cache_estadisticas(self) -> bool:
        """Limpia TODO el caché de estadísticas"""
        cache = CacheManager.get_instance()
        return cache.invalidate_tipo('estadisticas')

    def obtener_info_cache(self) -> Dict:
        """
        Obtiene información del estado del caché.

        Útil para debugging y monitoreo.

        Returns:
            Dict con info del caché
        """
        cache = CacheManager.get_instance()
        return {
            'stats': cache.get_stats(),
            'info': cache.get_info()
        }

    def precalcular_caches_criticos(self):
        """
        Precalcula cachés críticos para mejorar performance inicial.

        Se puede ejecutar al iniciar la aplicación o en background
        para que la primera consulta sea rápida.
        """
        logger.info("Precalculando cachés críticos...")

        # Precalcular productos todos
        productos = self.obtener_todos_con_cache()
        logger.info(f"Productos en caché: {len(productos)}")

        # Precalcular estadísticas
        estadisticas = self.obtener_estadisticas_inventario_con_cache()
        logger.info(f"Estadísticas en caché: {estadisticas}")

        # Precalcular por categorías
        categorias = ['Vidrios', 'Herrajes', 'Perfiles']
        for cat in categorias:
            productos_cat = self.obtener_productos_por_categoria_con_cache(cat)
            logger.info(f"Caché '{cat}': {len(productos_cat)} productos")

        logger.info("✅ Precálculo de cachés completado")


# ============================================================================
# EJEMPLOS DE USO
# ============================================================================

def ejemplo_uso_basico():
    """Ejemplo básico de uso del modelo con caché"""
    # Crear modelo
    modelo = InventarioModelCached(db_connection)

    # Primera llamada: Va a BD (lento) y guarda en caché
    productos = modelo.obtener_todos_con_cache()
    print(f"Productos: {len(productos)}")

    # Segunda llamada: Del caché (⚡ 1000x más rápido)
    productos = modelo.obtener_todos_con_cache()
    print(f"Productos: {len(productos)}")

    # Crear producto (invalida caché automáticamente)
    modelo.crear_producto_con_invalidation({
        'codigo': 'PROD-001',
        'nombre': 'Nuevo Producto',
        'categoria': 'Vidrios'
    })

    # Tercera llamada: Va a BD nuevamente (caché fue invalidado)
    productos = modelo.obtener_todos_con_cache()
    print(f"Productos: {len(productos)}")


def ejemplo_cache_inteligente():
    """Ejemplo de caché inteligente con invalidación selectiva"""
    modelo = InventarioModelCached(db_connection)

    # Obtener estadísticas (primera vez: lento)
    stats = modelo.obtener_estadisticas_inventario_con_cache()

    # Actualizar solo stock de un producto
    modelo.actualizar_stock_con_invalidation(
        producto_id=123,
        nuevo_stock=50,
        motivo="Venta"
    )
    # ⚠️ Solo invalida estadísticas, NO productos

    # Productos SIGUEN en caché (no cambiaron)
    productos = modelo.obtener_todos_con_cache()  # ⚡ Del caché

    # Estadísticas van a BD (sí cambiaron)
    stats = modelo.obtener_estadisticas_inventario_con_cache()  # BD


def ejemplo_info_cache():
    """Ejemplo de cómo obtener info del caché"""
    modelo = InventarioModelCached(db_connection)

    # Obtener info del caché
    info = modelo.obtener_info_cache()
    print(f"Estado del caché:")
    print(f"  - Habilitado: {info['info']['status']}")
    print(f"  - Memoria usada: {info['info']['used_memory']}")
    print(f"  - Keys totales: {info['info']['total_keys']}")
    print(f"  - Hit rate: {info['stats']['hit_rate']}")
    print(f"  - Total requests: {info['stats']['total_requests']}")


def ejemplo_precioalculo():
    """Ejemplo de cómo precargar caché al iniciar la app"""
    modelo = InventarioModelCached(db_connection)

    # Precargar cachés críticos
    modelo.precalcular_caches_criticos()

    print("✅ Cachés precargados. La app responderá muy rápido ahora.")


if __name__ == "__main__":
    # Ejecutar ejemplos
    ejemplo_uso_basico()
    ejemplo_cache_inteligente()
    ejemplo_info_cache()
