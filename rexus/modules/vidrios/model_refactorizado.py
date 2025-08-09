"""
Modelo Refactorizado de Vidrios - Rexus.app

Orquestador modular que unifica todos los submódulos de vidrios.
Mantiene compatibilidad hacia atrás con la API existente.

Arquitectura modular:
- ProductosManager: CRUD de vidrios y validaciones
- ObrasManager: Asignación de vidrios a obras
- ConsultasManager: Búsquedas, filtros y estadísticas
"""

from typing import Any, Dict, List, Optional

# Imports de seguridad unificados
from rexus.core.auth_decorators import auth_required, permission_required
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric

from .submodules.consultas_manager import ConsultasManager
from .submodules.obras_manager import ObrasManager

# Imports de submódulos
from .submodules.productos_manager import ProductosManager

# DataSanitizer unificado
try:
    from rexus.utils.unified_sanitizer import unified_sanitizer
    DataSanitizer = unified_sanitizer
except ImportError:
    class DataSanitizer:
        def sanitize_string(self, text):
            return str(text) if text else ""

        def sanitize_integer(self, value):
            return int(value) if value else 0


class ModeloVidriosRefactorizado:
    """
    Modelo refactorizado para gestión de vidrios.

    Delega operaciones a submódulos especializados mientras
    mantiene la interfaz compatible con el controlador existente.
    """

    def __init__(self, db_connection=None):
        """Inicializa el modelo con los submódulos especializados."""
        self.db_connection = db_connection
        self.sanitizer = DataSanitizer()

        # Inicializar submódulos especializados
        self.productos_manager = ProductosManager(db_connection)
        self.obras_manager = ObrasManager(db_connection)
        self.consultas_manager = ConsultasManager(db_connection)

    # ====== MÉTODOS DE COMPATIBILIDAD HACIA ATRÁS ======

    @auth_required
    @permission_required("view_inventario")
    def obtener_todos_vidrios(self) -> List[Dict[str, Any]]:
        """Obtiene todos los vidrios (método de compatibilidad)."""
        return self.consultas_manager.obtener_todos_vidrios()

    @auth_required
    @permission_required("view_inventario")
    def obtener_vidrio_por_id(self, vidrio_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un vidrio por ID (método de compatibilidad)."""
        return self.productos_manager.obtener_vidrio_por_id(vidrio_id)

    @auth_required
    @permission_required("create_inventario")
    def crear_vidrio(self, datos_vidrio: Dict[str, Any]) -> bool:
        """Crea un nuevo vidrio (método de compatibilidad)."""
        return self.productos_manager.crear_vidrio(datos_vidrio)

    @auth_required
    @permission_required("edit_inventario")
    def actualizar_vidrio(self, vidrio_id: int, datos_vidrio: Dict[str, Any]) -> bool:
        """Actualiza un vidrio (método de compatibilidad)."""
        return self.productos_manager.actualizar_vidrio(vidrio_id, datos_vidrio)

    @auth_required
    @permission_required("delete_inventario")
    def eliminar_vidrio(self, vidrio_id: int) -> bool:
        """Elimina un vidrio (método de compatibilidad)."""
        return self.productos_manager.eliminar_vidrio(vidrio_id)

    # ====== NUEVOS MÉTODOS MODULARIZADOS ======

    # Delegación a ProductosManager
    @auth_required
    @permission_required("edit_inventario")
    def actualizar_stock(self, vidrio_id: int, nuevo_stock: int) -> bool:
        """Actualiza el stock de un vidrio."""
        return self.productos_manager.actualizar_stock(vidrio_id, nuevo_stock)

    @auth_required
    @permission_required("edit_inventario")
    def actualizar_precio(self, vidrio_id: int, nuevo_precio: float) -> bool:
        """Actualiza el precio de un vidrio."""
        return self.productos_manager.actualizar_precio(vidrio_id, nuevo_precio)

    @auth_required
    @permission_required("view_inventario")
    def validar_disponibilidad(self, vidrio_id: int, cantidad_requerida: int) -> bool:
        """Valida si hay stock suficiente."""
        return self.productos_manager.validar_disponibilidad(
            vidrio_id, cantidad_requerida
        )

    def calcular_area_vidrio(self, ancho: float, alto: float) -> float:
        """Calcula el área de un vidrio."""
        return self.productos_manager.calcular_area_vidrio(ancho, alto)

    # Delegación a ObrasManager
    @auth_required
    @permission_required("edit_obras")
    def asignar_vidrio_obra(self, vidrio_id: int, obra_id: int, cantidad: int) -> bool:
        """Asigna vidrios a una obra."""
        return self.obras_manager.asignar_vidrio_obra(vidrio_id, obra_id, cantidad)

    @auth_required
    @permission_required("create_pedidos")
    def crear_pedido_obra(self, datos_pedido: Dict[str, Any]) -> Optional[int]:
        """Crea un pedido de vidrios para una obra."""
        return self.obras_manager.crear_pedido_obra(datos_pedido)

    @auth_required
    @permission_required("view_obras")
    def obtener_vidrios_obra(self, obra_id: int) -> List[Dict[str, Any]]:
        """Obtiene todos los vidrios asignados a una obra."""
        return self.obras_manager.obtener_vidrios_obra(obra_id)

    @auth_required
    @permission_required("view_obras")
    def obtener_resumen_obra(self, obra_id: int) -> Dict[str, Any]:
        """Obtiene resumen de vidrios de una obra."""
        return self.obras_manager.obtener_resumen_obra(obra_id)

    @auth_required
    @permission_required("edit_pedidos")
    def actualizar_estado_pedido(self, pedido_id: int, nuevo_estado: str) -> bool:
        """Actualiza el estado de un pedido."""
        return self.obras_manager.actualizar_estado_pedido(pedido_id, nuevo_estado)

    # Delegación a ConsultasManager
    @auth_required
    @permission_required("view_inventario")
    def buscar_vidrios(self, termino_busqueda: str) -> List[Dict[str, Any]]:
        """Búsqueda avanzada de vidrios."""
        return self.consultas_manager.buscar_vidrios(termino_busqueda)

    @auth_required
    @permission_required("view_inventario")
    def obtener_estadisticas_vidrios(self) -> Dict[str, Any]:
        """Obtiene estadísticas del inventario de vidrios."""
        return self.consultas_manager.obtener_estadisticas_vidrios()

    @auth_required
    @permission_required("view_inventario")
    def obtener_vidrios_paginados(
        self,
        page: int = 1,
        per_page: int = 20,
        filtros: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Obtiene vidrios con paginación."""
        return self.consultas_manager.obtener_vidrios_paginados(page, per_page, filtros)

    @auth_required
    @permission_required("view_inventario")
    def obtener_vidrios_stock_bajo(self) -> List[Dict[str, Any]]:
        """Obtiene vidrios con stock por debajo del mínimo."""
        return self.consultas_manager.obtener_vidrios_stock_bajo()

    @auth_required
    @permission_required("view_inventario")
    def obtener_reporte_proveedores(self) -> List[Dict[str, Any]]:
        """Genera reporte de vidrios por proveedor."""
        return self.consultas_manager.obtener_reporte_proveedores()

    # ====== MÉTODOS DE ADMINISTRACIÓN ======

    def obtener_info_modular(self) -> Dict[str, Any]:
        """Obtiene información sobre la estructura modular."""
        return {
            "modelo": "ModeloVidriosRefactorizado",
            "version": "2.0",
            "submodulos": [
                {
                    "nombre": "ProductosManager",
                    "responsabilidad": "CRUD de vidrios y validaciones",
                    "metodos_publicos": [
                        "obtener_vidrio_por_id",
                        "crear_vidrio",
                        "actualizar_vidrio",
                        "eliminar_vidrio",
                        "actualizar_stock",
                        "actualizar_precio",
                        "validar_disponibilidad",
                        "calcular_area_vidrio",
                    ],
                },
                {
                    "nombre": "ObrasManager",
                    "responsabilidad": "Asignación de vidrios a obras",
                    "metodos_publicos": [
                        "asignar_vidrio_obra",
                        "crear_pedido_obra",
                        "obtener_vidrios_obra",
                        "obtener_resumen_obra",
                        "actualizar_estado_pedido",
                    ],
                },
                {
                    "nombre": "ConsultasManager",
                    "responsabilidad": "Búsquedas, filtros y estadísticas",
                    "metodos_publicos": [
                        "obtener_todos_vidrios",
                        "buscar_vidrios",
                        "obtener_estadisticas_vidrios",
                        "obtener_vidrios_paginados",
                        "obtener_vidrios_stock_bajo",
                        "obtener_reporte_proveedores",
                    ],
                },
            ],
            "caracteristicas": [
                "Compatibilidad hacia atrás completa",
                "Separación clara de responsabilidades",
                "SQL externalizado",
                "Seguridad unificada",
                "Validaciones robustas",
            ],
        }

    def verificar_conectividad_modulos(self) -> Dict[str, bool]:
        """Verifica que todos los submódulos estén conectados correctamente."""
        return {
            "productos_manager": self.productos_manager is not None,
            "obras_manager": self.obras_manager is not None,
            "consultas_manager": self.consultas_manager is not None,
            "db_connection": self.db_connection is not None,
        }

    # ====== MÉTODOS LEGACY DEPRECADOS (para transición) ======

    def obtener_lista_vidrios(self) -> List[Dict[str, Any]]:
        """
        DEPRECADO: Usar obtener_todos_vidrios() o obtener_vidrios_paginados()
        """
        print(
            "[WARN]  Método deprecado. Usar obtener_todos_vidrios() o obtener_vidrios_paginados()"
        )
        return self.obtener_todos_vidrios()

    def buscar_vidrio(self, criterio: str) -> List[Dict[str, Any]]:
        """
        DEPRECADO: Usar buscar_vidrios()
        """
        print("[WARN]  Método deprecado. Usar buscar_vidrios()")
        return self.buscar_vidrios(criterio)

    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        DEPRECADO: Usar obtener_estadisticas_vidrios()
        """
        print("[WARN]  Método deprecado. Usar obtener_estadisticas_vidrios()")
        return self.obtener_estadisticas_vidrios()


# ====== FUNCIÓN DE MIGRACIÓN AUTOMÁTICA ======


def migrar_desde_modelo_legacy(modelo_legacy) -> ModeloVidriosRefactorizado:
    """
    Migra automáticamente desde un modelo legacy al refactorizado.

    Args:
        modelo_legacy: Instancia del modelo anterior

    Returns:
        ModeloVidriosRefactorizado: Nueva instancia con datos migrados
    """
    if hasattr(modelo_legacy, "db_connection"):
        return ModeloVidriosRefactorizado(modelo_legacy.db_connection)
    else:
        return ModeloVidriosRefactorizado()


# ====== ALIAS PARA COMPATIBILIDAD ======

# Permite usar el nombre anterior del modelo
ModeloVidrios = ModeloVidriosRefactorizado
