"""
Modelo Refactorizado de Obras - Rexus.app

Orquestador modular que unifica todos los submódulos de obras.
Mantiene compatibilidad hacia atrás con la API existente.

Arquitectura modular:
- ProyectosManager: CRUD de obras y gestión de proyectos
- RecursosManager: Asignación de materiales y personal
- ConsultasManager: Búsquedas, filtros y estadísticas
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

# Imports de seguridad unificados
from rexus.core.auth_decorators import auth_required, permission_required
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric

from .submodules.consultas_manager import ConsultasManager

# Imports de submódulos
from .submodules.proyectos_manager import ProyectosManager
from .submodules.recursos_manager import RecursosManager

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

        def sanitize_integer(self, value, min_val=None, max_val=None):
            return int(value) if value else 0


class ModeloObrasRefactorizado:
    """
    Modelo refactorizado para gestión de obras.

    Delega operaciones a submódulos especializados mientras
    mantiene la interfaz compatible con el controlador existente.
    """

    def __init__(self, db_connection=None):
        """Inicializa el modelo con los submódulos especializados."""
        self.db_connection = db_connection
        self.sanitizer = DataSanitizer()

        # Inicializar submódulos especializados
        self.proyectos_manager = ProyectosManager(db_connection)
        self.recursos_manager = RecursosManager(db_connection)
        self.consultas_manager = ConsultasManager(db_connection)

    # ====== MÉTODOS DE COMPATIBILIDAD HACIA ATRÁS ======

    @auth_required
    @permission_required("view_obras")
    def obtener_todas_obras(self) -> List[Dict[str, Any]]:
        """Obtiene todas las obras (método de compatibilidad)."""
        return self.consultas_manager.obtener_todas_obras()

    @auth_required
    @permission_required("view_obras")
    def obtener_obra_por_id(self, obra_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene una obra por ID (método de compatibilidad)."""
        return self.proyectos_manager.obtener_obra_por_id(obra_id)

    @auth_required
    @permission_required("add_obras")
    def crear_obra(self, datos_obra: Dict[str, Any]) -> bool:
        """Crea una nueva obra (método de compatibilidad)."""
        return self.proyectos_manager.crear_obra(datos_obra)

    @auth_required
    @permission_required("change_obras")
    def actualizar_obra(self, obra_id: int, datos_obra: Dict[str, Any]) -> bool:
        """Actualiza una obra (método de compatibilidad)."""
        return self.proyectos_manager.actualizar_obra(obra_id, datos_obra)

    @auth_required
    @permission_required("delete_obras")
    def eliminar_obra(self, obra_id: int) -> bool:
        """Elimina una obra (método de compatibilidad)."""
        return self.proyectos_manager.eliminar_obra(obra_id)

    # ====== NUEVOS MÉTODOS MODULARIZADOS ======

    # Delegación a ProyectosManager
    @auth_required
    @permission_required("change_obras")
    def cambiar_estado_obra(self, obra_id: int, nuevo_estado: str) -> bool:
        """Cambia el estado de una obra."""
        return self.proyectos_manager.cambiar_estado_obra(obra_id, nuevo_estado)

    @auth_required
    @permission_required("view_obras")
    def obtener_estados_disponibles(self) -> List[str]:
        """Obtiene los estados de obra disponibles."""
        return self.proyectos_manager.obtener_estados_disponibles()

    @auth_required
    @permission_required("view_obras")
    def calcular_progreso_obra(self, obra_id: int) -> float:
        """Calcula el porcentaje de progreso de una obra."""
        return self.proyectos_manager.calcular_progreso_obra(obra_id)

    # Delegación a RecursosManager
    @auth_required
    @permission_required("edit_obras")
    def asignar_material_obra(
        self,
        obra_id: int,
        material_id: int,
        cantidad: int,
        tipo_material: str = "vidrio",
    ) -> bool:
        """Asigna material a una obra."""
        return self.recursos_manager.asignar_material_obra(
            obra_id, material_id, cantidad, tipo_material
        )

    @auth_required
    @permission_required("view_obras")
    def obtener_materiales_obra(self, obra_id: int) -> List[Dict[str, Any]]:
        """Obtiene materiales asignados a una obra."""
        return self.recursos_manager.obtener_materiales_obra(obra_id)

    @auth_required
    @permission_required("edit_obras")
    def liberar_material_obra(
        self, obra_id: int, material_id: int, cantidad: int
    ) -> bool:
        """Libera material de una obra."""
        return self.recursos_manager.liberar_material_obra(
            obra_id, material_id, cantidad
        )

    @auth_required
    @permission_required("edit_obras")
    def asignar_personal_obra(
        self,
        obra_id: int,
        personal_id: int,
        rol: str,
        fecha_inicio: Optional[datetime] = None,
    ) -> bool:
        """Asigna personal a una obra."""
        return self.recursos_manager.asignar_personal_obra(
            obra_id, personal_id, rol, fecha_inicio
        )

    @auth_required
    @permission_required("view_obras")
    def obtener_resumen_recursos(self, obra_id: int) -> Dict[str, Any]:
        """Obtiene resumen de recursos de una obra."""
        return self.recursos_manager.obtener_resumen_recursos(obra_id)

    # Delegación a ConsultasManager
    @auth_required
    @permission_required("view_obras")
    def buscar_obras(self, termino_busqueda: str) -> List[Dict[str, Any]]:
        """Búsqueda avanzada de obras."""
        return self.consultas_manager.buscar_obras(termino_busqueda)

    @auth_required
    @permission_required("view_obras")
    def obtener_estadisticas_obras(self) -> Dict[str, Any]:
        """Obtiene estadísticas del sistema de obras."""
        return self.consultas_manager.obtener_estadisticas_obras()

    @auth_required
    @permission_required("view_obras")
    def obtener_obras_paginadas(
        self,
        page: int = 1,
        per_page: int = 20,
        filtros: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Obtiene obras con paginación."""
        return self.consultas_manager.obtener_obras_paginadas(page, per_page, filtros)

    @auth_required
    @permission_required("view_obras")
    def obtener_obras_vencidas(self) -> List[Dict[str, Any]]:
        """Obtiene obras que han superado su fecha de finalización."""
        return self.consultas_manager.obtener_obras_vencidas()

    @auth_required
    @permission_required("view_obras")
    def obtener_reporte_productividad(
        self,
        fecha_inicio: Optional[datetime] = None,
        fecha_fin: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Genera reporte de productividad."""
        return self.consultas_manager.obtener_reporte_productividad(
            fecha_inicio, fecha_fin
        )

    # ====== MÉTODOS DE ADMINISTRACIÓN ======

    def obtener_info_modular(self) -> Dict[str, Any]:
        """Obtiene información sobre la estructura modular."""
        return {
            "modelo": "ModeloObrasRefactorizado",
            "version": "2.0",
            "submodulos": [
                {
                    "nombre": "ProyectosManager",
                    "responsabilidad": "CRUD de obras y gestión de proyectos",
                    "metodos_publicos": [
                        "obtener_obra_por_id",
                        "crear_obra",
                        "actualizar_obra",
                        "eliminar_obra",
                        "cambiar_estado_obra",
                        "obtener_estados_disponibles",
                        "calcular_progreso_obra",
                    ],
                },
                {
                    "nombre": "RecursosManager",
                    "responsabilidad": "Gestión de materiales y personal",
                    "metodos_publicos": [
                        "asignar_material_obra",
                        "obtener_materiales_obra",
                        "liberar_material_obra",
                        "asignar_personal_obra",
                        "obtener_resumen_recursos",
                    ],
                },
                {
                    "nombre": "ConsultasManager",
                    "responsabilidad": "Búsquedas, filtros y estadísticas",
                    "metodos_publicos": [
                        "obtener_todas_obras",
                        "buscar_obras",
                        "obtener_estadisticas_obras",
                        "obtener_obras_paginadas",
                        "obtener_obras_vencidas",
                        "obtener_reporte_productividad",
                    ],
                },
            ],
            "caracteristicas": [
                "Compatibilidad hacia atrás completa",
                "Separación clara de responsabilidades",
                "SQL externalizado",
                "Seguridad unificada",
                "Validaciones robustas",
                "Gestión de recursos integrada",
            ],
        }

    def verificar_conectividad_modulos(self) -> Dict[str, bool]:
        """Verifica que todos los submódulos estén conectados correctamente."""
        return {
            "proyectos_manager": self.proyectos_manager is not None,
            "recursos_manager": self.recursos_manager is not None,
            "consultas_manager": self.consultas_manager is not None,
            "db_connection": self.db_connection is not None,
        }

    # ====== MÉTODOS LEGACY DEPRECADOS (para transición) ======

    def obtener_lista_obras(self) -> List[Dict[str, Any]]:
        """
        DEPRECADO: Usar obtener_todas_obras() o obtener_obras_paginadas()
        """
        print(
            "⚠️  Método deprecado. Usar obtener_todas_obras() o obtener_obras_paginadas()"
        )
        return self.obtener_todas_obras()

    def buscar_obra(self, criterio: str) -> List[Dict[str, Any]]:
        """
        DEPRECADO: Usar buscar_obras()
        """
        print("⚠️  Método deprecado. Usar buscar_obras()")
        return self.buscar_obras(criterio)

    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        DEPRECADO: Usar obtener_estadisticas_obras()
        """
        print("⚠️  Método deprecado. Usar obtener_estadisticas_obras()")
        return self.obtener_estadisticas_obras()


# ====== FUNCIÓN DE MIGRACIÓN AUTOMÁTICA ======


def migrar_desde_modelo_legacy(modelo_legacy) -> ModeloObrasRefactorizado:
    """
    Migra automáticamente desde un modelo legacy al refactorizado.

    Args:
        modelo_legacy: Instancia del modelo anterior

    Returns:
        ModeloObrasRefactorizado: Nueva instancia con datos migrados
    """
    if hasattr(modelo_legacy, "db_connection"):
        return ModeloObrasRefactorizado(modelo_legacy.db_connection)
    else:
        return ModeloObrasRefactorizado()


# ====== ALIAS PARA COMPATIBILIDAD ======

# Permite usar el nombre anterior del modelo
ModeloObras = ModeloObrasRefactorizado
