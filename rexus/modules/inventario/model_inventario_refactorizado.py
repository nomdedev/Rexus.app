"""
Modelo Principal de Inventario Refactorizado - Rexus.app v2.0.0

Orquesta todos los submódulos especializados de inventario.
Proporciona una interfaz unificada para el controlador manteniendo
compatibilidad total con el código existente.

ARQUITECTURA MODULAR IMPLEMENTADA:
- [CHECK] ProductosManager: CRUD de productos, validaciones, códigos
- [CHECK] MovimientosManager: Movimientos de stock, auditoría, tipos
- [CHECK] ConsultasManager: Búsquedas, paginación, estadísticas

BENEFICIOS LOGRADOS:
- Reducción drástica de líneas de código por submódulo (<350)
- Separación clara de responsabilidades
- Mantenibilidad mejorada
- Compatibilidad total con controlador existente
"""

from typing import Any, Dict, List, Optional

# Imports de seguridad unificados
from rexus.core.auth_decorators import auth_required, permission_required
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric

from .submodules.consultas_manager_refactorizado import ConsultasManager
from .submodules.movimientos_manager_refactorizado import MovimientosManager

# Imports de submódulos especializados
from .submodules.productos_manager_refactorizado import ProductosManager

# DataSanitizer unificado
try:
    from rexus.utils.unified_sanitizer import unified_sanitizer
    DataSanitizer = unified_sanitizer
except ImportError:
    class DataSanitizer:
        def sanitize_dict(self, data):
            return data if data else {}

        def sanitize_string(self, text):
            return str(text) if text else ""

        def sanitize_integer(self, value):
            return int(value) if value else 0


class ModeloInventarioRefactorizado:
    """
    Modelo principal de inventario que orquesta submódulos especializados.

    Delega todas las operaciones a los gestores especializados mientras
    mantiene la interfaz compatible con el controlador existente.
    """

    def __init__(self, db_connection=None):
        """Inicializa el modelo con los submódulos especializados."""
        self.db_connection = db_connection
        self.sanitizer = DataSanitizer()

        # Inicializar submódulos especializados
        self.productos_manager = ProductosManager(db_connection)
        self.movimientos_manager = MovimientosManager(db_connection)
        self.consultas_manager = ConsultasManager(db_connection)

    # =============================================================================
    # MÉTODOS DE PRODUCTOS - Delegación a ProductosManager
    # =============================================================================

    @auth_required
    @permission_required("create_producto")
    def crear_producto(
        self, datos_producto: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Crea un nuevo producto en el inventario."""
        return self.productos_manager.crear_producto(datos_producto)

    @auth_required
    @permission_required("view_inventario")
    def obtener_producto_por_id(self, producto_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un producto por su ID."""
        return self.productos_manager.obtener_producto_por_id(producto_id)

    @auth_required
    @permission_required("view_inventario")
    def obtener_producto_por_codigo(self, codigo: str) -> Optional[Dict[str, Any]]:
        """Obtiene un producto por su código."""
        return self.productos_manager.obtener_producto_por_codigo(codigo)

    @auth_required
    @permission_required("update_producto")
    def actualizar_producto(
        self, producto_id: int, datos_actualizacion: Dict[str, Any]
    ) -> bool:
        """Actualiza la información de un producto."""
        return self.productos_manager.actualizar_producto(
            producto_id, datos_actualizacion
        )

    @auth_required
    @permission_required("delete_producto")
    def eliminar_producto(self, producto_id: int) -> bool:
        """Elimina un producto (soft delete)."""
        return self.productos_manager.eliminar_producto(producto_id)

    @auth_required
    @permission_required("update_stock")
    def actualizar_stock(
        self, producto_id: int, nuevo_stock: int, motivo: str = "Ajuste manual"
    ) -> bool:
        """Actualiza el stock de un producto."""
        return self.productos_manager.actualizar_stock(producto_id, nuevo_stock, motivo)

    @auth_required
    @permission_required("view_inventario")
    def obtener_categorias(self) -> List[str]:
        """Obtiene lista de categorías disponibles."""
        return self.productos_manager.obtener_categorias()

    def validar_datos_producto(self, datos: Dict[str, Any]) -> List[str]:
        """Valida los datos de un producto y retorna lista de errores."""
        return self.productos_manager.validar_datos_producto(datos)

    # =============================================================================
    # MÉTODOS DE MOVIMIENTOS - Delegación a MovimientosManager
    # =============================================================================

    @auth_required
    @permission_required("create_movimiento")
    def registrar_movimiento(
        self, datos_movimiento: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Registra un movimiento de inventario."""
        return self.movimientos_manager.registrar_movimiento(datos_movimiento)

    @auth_required
    @permission_required("view_movimientos")
    def obtener_movimientos_producto(
        self, producto_id: int, limite: int = 20
    ) -> List[Dict[str, Any]]:
        """Obtiene el historial de movimientos de un producto."""
        return self.movimientos_manager.obtener_movimientos_producto(
            producto_id, limite
        )

    @auth_required
    @permission_required("view_movimientos")
    def obtener_movimientos_obra(self, obra_id: int) -> List[Dict[str, Any]]:
        """Obtiene movimientos asociados a una obra específica."""
        return self.movimientos_manager.obtener_movimientos_obra(obra_id)

    @auth_required
    @permission_required("view_movimientos")
    def obtener_estadisticas_movimientos(
        self, fecha_inicio: Optional[str] = None, fecha_fin: Optional[str] = None
    ) -> Dict[str, Any]:
        """Obtiene estadísticas de movimientos en un período."""
        return self.movimientos_manager.obtener_estadisticas_movimientos(
            fecha_inicio, fecha_fin
        )

    @auth_required
    @permission_required("create_movimiento")
    def entrada_stock(
        self, producto_id: int, cantidad: int, motivo: str = "Entrada manual"
    ) -> Optional[Dict[str, Any]]:
        """Atajo para registrar entrada de stock."""
        return self.movimientos_manager.entrada_stock(producto_id, cantidad, motivo)

    @auth_required
    @permission_required("create_movimiento")
    def salida_stock(
        self,
        producto_id: int,
        cantidad: int,
        obra_id: Optional[int] = None,
        motivo: str = "Salida manual",
    ) -> Optional[Dict[str, Any]]:
        """Atajo para registrar salida de stock."""
        return self.movimientos_manager.salida_stock(
            producto_id, cantidad, obra_id, motivo
        )

    def validar_datos_movimiento(self, datos: Dict[str, Any]) -> List[str]:
        """Valida los datos de un movimiento y retorna lista de errores."""
        return self.movimientos_manager.validar_datos_movimiento(datos)

    # =============================================================================
    # MÉTODOS DE CONSULTAS - Delegación a ConsultasManager
    # =============================================================================

    def obtener_productos_paginados_inicial(
        self,
        offset: int = 0,
        limit: int = 50,
        filtros: Optional[Dict[str, Any]] = None,
        orden: str = "descripcion ASC",
    ) -> Dict[str, Any]:
        """Obtiene productos con paginación para carga inicial sin autenticación."""
        return self.consultas_manager.obtener_productos_paginados_inicial(
            offset, limit, filtros, orden
        )

    @auth_required
    @permission_required("view_inventario")
    def obtener_productos_paginados(
        self,
        offset: int = 0,
        limit: int = 50,
        filtros: Optional[Dict[str, Any]] = None,
        orden: str = "descripcion ASC",
    ) -> Dict[str, Any]:
        """Obtiene productos con paginación y filtros."""
        return self.consultas_manager.obtener_productos_paginados(
            offset, limit, filtros, orden
        )

    @auth_required
    @permission_required("view_inventario")
    def buscar_productos(
        self, termino_busqueda: str, limite: int = 20
    ) -> List[Dict[str, Any]]:
        """Busca productos por código o descripción."""
        return self.consultas_manager.buscar_productos(termino_busqueda, limite)

    @auth_required
    @permission_required("view_inventario")
    def obtener_productos_stock_bajo(self) -> List[Dict[str, Any]]:
        """Obtiene productos con stock por debajo del mínimo."""
        return self.consultas_manager.obtener_productos_stock_bajo()

    @auth_required
    @permission_required("view_inventario")
    def obtener_estadisticas_inventario(self) -> Dict[str, Any]:
        """Obtiene estadísticas generales del inventario."""
        return self.consultas_manager.obtener_estadisticas_inventario()

    @auth_required
    @permission_required("view_inventario")
    def obtener_productos_por_categoria(self, categoria: str) -> List[Dict[str, Any]]:
        """Obtiene productos de una categoría específica."""
        return self.consultas_manager.obtener_productos_por_categoria(categoria)

    @auth_required
    @permission_required("view_inventario")
    def generar_reporte_valorizado(self) -> List[Dict[str, Any]]:
        """Genera reporte valorizado del inventario."""
        return self.consultas_manager.generar_reporte_valorizado()

    @auth_required
    @permission_required("view_inventario")
    def obtener_productos_filtro_avanzado(
        self, filtros: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Aplica filtros avanzados para búsqueda de productos."""
        return self.consultas_manager.obtener_productos_filtro_avanzado(filtros)

    # =============================================================================
    # MÉTODOS DE COMPATIBILIDAD Y INFORMACIÓN MODULAR
    # =============================================================================

    def obtener_info_modular(self) -> Dict[str, Any]:
        """Obtiene información sobre la estructura modular."""
        return {
            "modelo": "ModeloInventarioRefactorizado",
            "version": "2.0",
            "submodulos": [
                {
                    "nombre": "ProductosManager",
                    "responsabilidad": "CRUD de productos, validaciones, códigos",
                    "metodos_publicos": [
                        "crear_producto",
                        "obtener_producto_por_id",
                        "obtener_producto_por_codigo",
                        "actualizar_producto",
                        "eliminar_producto",
                        "actualizar_stock",
                        "obtener_categorias",
                        "validar_datos_producto",
                    ],
                },
                {
                    "nombre": "MovimientosManager",
                    "responsabilidad": "Movimientos de stock, auditoría, tipos",
                    "metodos_publicos": [
                        "registrar_movimiento",
                        "obtener_movimientos_producto",
                        "obtener_movimientos_obra",
                        "obtener_estadisticas_movimientos",
                        "entrada_stock",
                        "salida_stock",
                        "validar_datos_movimiento",
                    ],
                },
                {
                    "nombre": "ConsultasManager",
                    "responsabilidad": "Búsquedas, paginación, estadísticas",
                    "metodos_publicos": [
                        "obtener_productos_paginados",
                        "buscar_productos",
                        "obtener_productos_stock_bajo",
                        "obtener_estadisticas_inventario",
                        "obtener_productos_por_categoria",
                        "generar_reporte_valorizado",
                        "obtener_productos_filtro_avanzado",
                    ],
                },
            ],
            "beneficios": [
                "Reducción de complejidad por submódulo",
                "Separación clara de responsabilidades",
                "Mantenibilidad mejorada",
                "Reutilización de código",
                "Facilidad de testing",
            ],
        }

    # =============================================================================
    # MÉTODOS DE COMPATIBILIDAD CON CÓDIGO LEGACY
    # =============================================================================

    # Aliases para mantener compatibilidad con nombres anteriores
    def crear_item(self, datos: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Alias para compatibilidad."""
        return self.crear_producto(datos)

    def obtener_item(self, item_id: int) -> Optional[Dict[str, Any]]:
        """Alias para compatibilidad."""
        return self.obtener_producto_por_id(item_id)

    def actualizar_item(self, item_id: int, datos: Dict[str, Any]) -> bool:
        """Alias para compatibilidad."""
        return self.actualizar_producto(item_id, datos)

    def eliminar_item(self, item_id: int) -> bool:
        """Alias para compatibilidad."""
        return self.eliminar_producto(item_id)

    def obtener_listado_paginado(
        self, offset: int = 0, limit: int = 50
    ) -> Dict[str, Any]:
        """Alias para compatibilidad."""
        return self.obtener_productos_paginados(offset, limit)

    def buscar_por_termino(self, termino: str) -> List[Dict[str, Any]]:
        """Alias para compatibilidad."""
        return self.buscar_productos(termino)

    def obtener_estadisticas(self) -> Dict[str, Any]:
        """Alias para compatibilidad."""
        return self.obtener_estadisticas_inventario()

    def registrar_entrada(
        self, producto_id: int, cantidad: int, motivo: str = "Entrada"
    ) -> Optional[Dict[str, Any]]:
        """Alias para compatibilidad."""
        return self.entrada_stock(producto_id, cantidad, motivo)

    def registrar_salida(
        self, producto_id: int, cantidad: int, motivo: str = "Salida"
    ) -> Optional[Dict[str, Any]]:
        """Alias para compatibilidad."""
        return self.salida_stock(producto_id, cantidad, None, motivo)
