"""
Modelo Principal de Inventario Refactorizado - Rexus.app v2.0.0

Orquesta todos los submódulos especializados de inventario.
Proporciona una interfaz unificada para el controlador.

MEJORAS IMPLEMENTADAS:
- ✅ Módulo dividido en submódulos especializados
- ✅ Arquitectura modular y mantenible
- ✅ Imports unificados sin duplicados
- ✅ Delegación a gestores especializados
- ✅ Reducción drástica de líneas de código
"""

from typing import Any, Dict, List, Optional

# Imports de seguridad unificados
from rexus.core.auth_decorators import auth_required, permission_required

from .submodules.consultas_manager import ConsultasManager
from .submodules.movimientos_manager import MovimientosManager

# Imports de submódulos especializados
from .submodules.productos_manager import ProductosManager


class InventarioModelRefactorizado:
    """
    Modelo principal de inventario que orquesta submódulos especializados.

    Arquitectura modular:
    - ProductosManager: CRUD de productos, validaciones, QR
    - MovimientosManager: Movimientos de stock, auditoría
    - ConsultasManager: Búsquedas, paginación, estadísticas
    """

    def __init__(self, db_connection=None):
        """Inicializa el modelo con todos sus gestores especializados."""
        self.db_connection = db_connection

        # Inicializar gestores especializados
        self.productos = ProductosManager(db_connection)
        self.movimientos = MovimientosManager(db_connection)
        self.consultas = ConsultasManager(db_connection)

    # =========================================================================
    # DELEGACIÓN A PRODUCTOS MANAGER
    # =========================================================================

    @auth_required
    @permission_required("view_inventario")
    def obtener_producto_por_id(self, producto_id: int) -> Optional[Dict[str, Any]]:
        """Delega a ProductosManager."""
        return self.productos.obtener_producto_por_id(producto_id)

    @auth_required
    @permission_required("view_inventario")
    def obtener_producto_por_codigo(self, codigo: str) -> Optional[Dict[str, Any]]:
        """Delega a ProductosManager."""
        return self.productos.obtener_producto_por_codigo(codigo)

    @auth_required
    @permission_required("create_producto")
    def crear_producto(
        self, datos_producto: Dict[str, Any], usuario: str = "SISTEMA"
    ) -> Optional[int]:
        """Delega a ProductosManager."""
        return self.productos.crear_producto(datos_producto, usuario)

    @auth_required
    @permission_required("update_producto")
    def actualizar_producto(
        self, producto_id: int, datos_producto: Dict[str, Any], usuario: str = "SISTEMA"
    ) -> bool:
        """Delega a ProductosManager."""
        return self.productos.actualizar_producto(producto_id, datos_producto, usuario)

    def validar_stock_negativo(
        self, cantidad_nueva: float, producto_id: Optional[int] = None
    ) -> bool:
        """Delega a ProductosManager."""
        return self.productos.validar_stock_negativo(cantidad_nueva, producto_id)

    @auth_required
    @permission_required("view_inventario")
    def obtener_categorias(self) -> List[str]:
        """Delega a ProductosManager."""
        return self.productos.obtener_categorias()

    # =========================================================================
    # DELEGACIÓN A MOVIMIENTOS MANAGER
    # =========================================================================

    @auth_required
    @permission_required("create_movimiento")
    def registrar_movimiento(
        self,
        producto_id: int,
        tipo_movimiento: str,
        cantidad: float,
        observaciones: str = "",
        obra_id: Optional[int] = None,
        usuario: str = "SISTEMA",
    ) -> bool:
        """Delega a MovimientosManager."""
        return self.movimientos.registrar_movimiento(
            producto_id, tipo_movimiento, cantidad, observaciones, obra_id, usuario
        )

    @auth_required
    @permission_required("view_movimientos")
    def obtener_movimientos(
        self,
        producto_id: Optional[int] = None,
        tipo_movimiento: Optional[str] = None,
        fecha_desde=None,
        fecha_hasta=None,
        limite: int = 100,
    ) -> List[Dict[str, Any]]:
        """Delega a MovimientosManager."""
        return self.movimientos.obtener_movimientos(
            producto_id, tipo_movimiento, fecha_desde, fecha_hasta, limite
        )

    @auth_required
    @permission_required("view_reportes")
    def generar_reporte_movimientos(
        self, filtros: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Delega a MovimientosManager."""
        return self.movimientos.generar_reporte_movimientos(filtros)

    @auth_required
    @permission_required("view_stock_bajo")
    def obtener_productos_stock_bajo(self) -> List[Dict[str, Any]]:
        """Delega a MovimientosManager."""
        return self.movimientos.obtener_productos_stock_bajo()

    # =========================================================================
    # DELEGACIÓN A CONSULTAS MANAGER
    # =========================================================================

    @auth_required
    @permission_required("view_inventario")
    def obtener_productos_paginados(
        self,
        offset: int = 0,
        limit: int = 50,
        filtros: Optional[Dict[str, Any]] = None,
        orden: str = "descripcion ASC",
    ) -> Dict[str, Any]:
        """Delega a ConsultasManager."""
        return self.consultas.obtener_productos_paginados(offset, limit, filtros, orden)

    @auth_required
    @permission_required("view_inventario")
    def obtener_todos_productos(
        self, filtros: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Delega a ConsultasManager."""
        return self.consultas.obtener_todos_productos(filtros)

    @auth_required
    @permission_required("view_estadisticas")
    def obtener_estadisticas_inventario(self) -> Dict[str, Any]:
        """Delega a ConsultasManager."""
        return self.consultas.obtener_estadisticas_inventario()

    @auth_required
    @permission_required("view_inventario")
    def buscar_productos(
        self, termino_busqueda: str, limite: int = 20
    ) -> List[Dict[str, Any]]:
        """Delega a ConsultasManager."""
        return self.consultas.buscar_productos(termino_busqueda, limite)

    # =========================================================================
    # MÉTODOS DE COMPATIBILIDAD PARA EL CONTROLADOR EXISTENTE
    # =========================================================================

    def get_paginated_data(
        self, offset: int = 0, limit: int = 50, filtros=None
    ) -> Dict[str, Any]:
        """Método de compatibilidad para PaginatedTableMixin."""
        return self.obtener_productos_paginados(offset, limit, filtros)

    # =========================================================================
    # MÉTODOS DE UTILIDAD Y ADMINISTRACIÓN
    # =========================================================================

    def obtener_tipos_movimiento(self) -> Dict[str, str]:
        """Obtiene los tipos de movimiento disponibles."""
        return self.movimientos.TIPOS_MOVIMIENTO

    def validar_conexion(self) -> bool:
        """Valida que hay conexión a la base de datos."""
        return self.db_connection is not None

    def obtener_resumen_modular(self) -> Dict[str, Any]:
        """Obtiene resumen del estado de todos los submódulos."""
        return {
            "conexion_activa": self.validar_conexion(),
            "gestores_disponibles": {
                "productos": self.productos is not None,
                "movimientos": self.movimientos is not None,
                "consultas": self.consultas is not None,
            },
            "tipos_movimiento_disponibles": len(self.movimientos.TIPOS_MOVIMIENTO),
            "version": "2.0.0-refactorizado",
        }

    # =========================================================================
    # MÉTODOS ADICIONALES ESPECÍFICOS
    # =========================================================================

    @auth_required
    @permission_required("admin_inventario")
    def actualizar_qr_masivo(self) -> Dict[str, Any]:
        """Actualiza códigos QR de productos de forma masiva."""
        if not self.db_connection:
            return {"error": "Sin conexión a BD"}

        try:
            productos = self.obtener_todos_productos()
            actualizados = 0
            errores = 0

            for producto in productos:
                try:
                    # Generar nuevo QR si no existe
                    if not producto.get("qr_data"):
                        qr_generado = self.productos._generar_qr_code(
                            producto["codigo"]
                        )

                        # Actualizar producto con QR
                        datos_actualizacion = {"qr_data": qr_generado}
                        if self.actualizar_producto(
                            producto["id"], datos_actualizacion, "SISTEMA_QR"
                        ):
                            actualizados += 1
                        else:
                            errores += 1
                except Exception:
                    errores += 1

            return {
                "productos_procesados": len(productos),
                "actualizados": actualizados,
                "errores": errores,
                "exito": errores == 0,
            }

        except Exception as e:
            return {"error": f"Error en actualización masiva: {str(e)}"}


# =========================================================================
# ALIAS PARA COMPATIBILIDAD HACIA ATRÁS
# =========================================================================

# El controlador puede seguir usando 'InventarioModel'
InventarioModel = InventarioModelRefactorizado
