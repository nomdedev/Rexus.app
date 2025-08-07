"""
Modelo Refactorizado de Usuarios - Rexus.app

Orquestador modular que unifica todos los submódulos de usuarios.
Mantiene compatibilidad hacia atrás con la API existente.

Arquitectura modular:
- AutenticacionManager: Autenticación, validación de contraseñas, bloqueos
- UsuariosManager: CRUD de usuarios, permisos, gestión básica
- ConsultasManager: Búsquedas, estadísticas, paginación
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

# Imports de seguridad unificados
from rexus.core.auth_decorators import auth_required, permission_required

# Imports de submódulos
from .submodules.autenticacion_manager import AutenticacionManager
from .submodules.consultas_manager import ConsultasManager
from .submodules.usuarios_manager import UsuariosManager

# DataSanitizer unificado
try:
    from rexus.utils.data_sanitizer import DataSanitizer as _DataSanitizer

    DataSanitizer = _DataSanitizer
except ImportError:

    class DataSanitizer:
        def sanitize_string(self, text, max_length=None):
            return str(text) if text else ""

        def sanitize_integer(self, value, min_val=None, max_val=None):
            return int(value) if value else 0


class ModeloUsuariosRefactorizado:
    """
    Modelo refactorizado para gestión de usuarios.

    Delega operaciones a submódulos especializados mientras
    mantiene la interfaz compatible con el controlador existente.
    """

    def __init__(self, db_connection=None):
        """Inicializa el modelo con los submódulos especializados."""
        self.db_connection = db_connection
        self.data_sanitizer = DataSanitizer()

        # Inicializar submódulos especializados
        self.autenticacion_manager = AutenticacionManager(db_connection)
        self.usuarios_manager = UsuariosManager(db_connection)
        self.consultas_manager = ConsultasManager(db_connection)

    # ====== MÉTODOS DE COMPATIBILIDAD HACIA ATRÁS ======

    # Delegación a AutenticacionManager
    def autenticar_usuario_seguro(self, username: str, password: str) -> Dict[str, Any]:
        """Autentica un usuario de forma segura (método de compatibilidad)."""
        return self.autenticacion_manager.autenticar_usuario_seguro(username, password)

    def verificar_cuenta_bloqueada(self, username: str) -> bool:
        """Verifica si una cuenta está bloqueada (método de compatibilidad)."""
        return self.autenticacion_manager.verificar_cuenta_bloqueada(username)

    def registrar_intento_login(self, username: str, exitoso: bool = False) -> None:
        """Registra un intento de login (método de compatibilidad)."""
        return self.autenticacion_manager.registrar_intento_login(username, exitoso)

    def reset_intentos_login(self, username: str) -> bool:
        """Resetea intentos fallidos (método de compatibilidad)."""
        return self.autenticacion_manager.reset_intentos_login(username)

    def validar_fortaleza_password(self, password: str) -> Dict[str, Any]:
        """Valida fortaleza de contraseña (método de compatibilidad)."""
        return self.autenticacion_manager.validar_fortaleza_password(password)

    # Delegación a UsuariosManager
    @auth_required
    @permission_required("add_usuarios")
    def crear_usuario(
        self,
        username: str,
        email: str,
        password: str,
        rol: str = "usuario",
        activo: bool = True,
        datos_adicionales: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Crea un nuevo usuario (método de compatibilidad)."""
        return self.usuarios_manager.crear_usuario(
            username, email, password, rol, activo, datos_adicionales
        )

    @auth_required
    @permission_required("view_usuarios")
    def obtener_usuario_por_id(self, usuario_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene usuario por ID (método de compatibilidad)."""
        return self.usuarios_manager.obtener_usuario_por_id(usuario_id)

    @auth_required
    @permission_required("view_usuarios")
    def obtener_usuario_por_nombre(self, username: str) -> Optional[Dict[str, Any]]:
        """Obtiene usuario por nombre (método de compatibilidad)."""
        return self.usuarios_manager.obtener_usuario_por_nombre(username)

    @auth_required
    @permission_required("change_usuarios")
    def actualizar_usuario(
        self, usuario_id: int, datos_actualizacion: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Actualiza un usuario (método de compatibilidad)."""
        return self.usuarios_manager.actualizar_usuario(usuario_id, datos_actualizacion)

    @auth_required
    @permission_required("delete_usuarios")
    def eliminar_usuario(
        self, usuario_id: int, soft_delete: bool = True
    ) -> Dict[str, Any]:
        """Elimina un usuario (método de compatibilidad)."""
        return self.usuarios_manager.eliminar_usuario(usuario_id, soft_delete)

    def verificar_unicidad_username(
        self, username: str, excluir_usuario_id: Optional[int] = None
    ) -> bool:
        """Verifica unicidad de username (método de compatibilidad)."""
        return self.usuarios_manager.verificar_unicidad_username(
            username, excluir_usuario_id
        )

    def verificar_unicidad_email(
        self, email: str, excluir_usuario_id: Optional[int] = None
    ) -> bool:
        """Verifica unicidad de email (método de compatibilidad)."""
        return self.usuarios_manager.verificar_unicidad_email(email, excluir_usuario_id)

    @auth_required
    @permission_required("view_usuarios")
    def obtener_permisos_usuario(self, usuario_id: int) -> List[str]:
        """Obtiene permisos de usuario (método de compatibilidad)."""
        return self.usuarios_manager.obtener_permisos_usuario(usuario_id)

    # Delegación a ConsultasManager
    @auth_required
    @permission_required("view_usuarios")
    def obtener_todos_usuarios(
        self, incluir_inactivos: bool = False
    ) -> List[Dict[str, Any]]:
        """Obtiene todos los usuarios (método de compatibilidad)."""
        return self.consultas_manager.obtener_todos_usuarios(incluir_inactivos)

    @auth_required
    @permission_required("view_usuarios")
    def buscar_usuarios(self, termino_busqueda: str) -> List[Dict[str, Any]]:
        """Búsqueda de usuarios (método de compatibilidad)."""
        return self.consultas_manager.buscar_usuarios(termino_busqueda)

    @auth_required
    @permission_required("view_usuarios")
    def obtener_usuarios_paginados(
        self,
        page: int = 1,
        per_page: int = 20,
        filtros: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Obtiene usuarios paginados (método de compatibilidad)."""
        return self.consultas_manager.obtener_usuarios_paginados(
            page, per_page, filtros
        )

    @auth_required
    @permission_required("view_usuarios")
    def obtener_estadisticas_usuarios(self) -> Dict[str, Any]:
        """Obtiene estadísticas de usuarios (método de compatibilidad)."""
        return self.consultas_manager.obtener_estadisticas_usuarios()

    # ====== NUEVOS MÉTODOS MODULARIZADOS ======

    # Nuevos métodos de AutenticacionManager
    def cambiar_password_usuario(
        self, usuario_id: int, password_actual: str, password_nueva: str
    ) -> Dict[str, Any]:
        """Cambia la contraseña de un usuario con validaciones."""
        return self.autenticacion_manager.cambiar_password_usuario(
            usuario_id, password_actual, password_nueva
        )

    # Nuevos métodos de UsuariosManager
    @auth_required
    @permission_required("change_usuarios")
    def asignar_permiso_usuario(self, usuario_id: int, permiso: str) -> bool:
        """Asigna un permiso específico a un usuario."""
        return self.usuarios_manager.asignar_permiso_usuario(usuario_id, permiso)

    # Nuevos métodos de ConsultasManager
    @auth_required
    @permission_required("view_usuarios")
    def obtener_usuarios_por_rol(self, rol: str) -> List[Dict[str, Any]]:
        """Obtiene usuarios filtrados por rol específico."""
        return self.consultas_manager.obtener_usuarios_por_rol(rol)

    @auth_required
    @permission_required("view_usuarios")
    def obtener_actividad_usuario(
        self, usuario_id: int, dias: int = 30
    ) -> Dict[str, Any]:
        """Obtiene el historial de actividad de un usuario específico."""
        return self.consultas_manager.obtener_actividad_usuario(usuario_id, dias)

    @auth_required
    @permission_required("admin")
    def generar_reporte_seguridad(self) -> Dict[str, Any]:
        """Genera un reporte de seguridad del sistema de usuarios."""
        return self.consultas_manager.generar_reporte_seguridad()

    # ====== MÉTODOS DE ADMINISTRACIÓN ======

    def obtener_info_modular(self) -> Dict[str, Any]:
        """Obtiene información sobre la estructura modular."""
        return {
            "modelo": "ModeloUsuariosRefactorizado",
            "version": "2.0",
            "submodulos": [
                {
                    "nombre": "AutenticacionManager",
                    "responsabilidad": "Autenticación, validación de contraseñas, bloqueos",
                    "metodos_publicos": [
                        "autenticar_usuario_seguro",
                        "verificar_cuenta_bloqueada",
                        "registrar_intento_login",
                        "reset_intentos_login",
                        "validar_fortaleza_password",
                        "cambiar_password_usuario",
                    ],
                },
                {
                    "nombre": "UsuariosManager",
                    "responsabilidad": "CRUD de usuarios y gestión de permisos",
                    "metodos_publicos": [
                        "crear_usuario",
                        "obtener_usuario_por_id",
                        "obtener_usuario_por_nombre",
                        "actualizar_usuario",
                        "eliminar_usuario",
                        "verificar_unicidad_username",
                        "verificar_unicidad_email",
                        "obtener_permisos_usuario",
                        "asignar_permiso_usuario",
                    ],
                },
                {
                    "nombre": "ConsultasManager",
                    "responsabilidad": "Búsquedas, estadísticas y reportes",
                    "metodos_publicos": [
                        "obtener_todos_usuarios",
                        "buscar_usuarios",
                        "obtener_usuarios_paginados",
                        "obtener_estadisticas_usuarios",
                        "obtener_usuarios_por_rol",
                        "obtener_actividad_usuario",
                        "generar_reporte_seguridad",
                    ],
                },
            ],
            "caracteristicas": [
                "Compatibilidad hacia atrás completa",
                "Separación clara de responsabilidades",
                "SQL externalizado",
                "Seguridad unificada",
                "Validaciones robustas",
                "Autenticación segura",
                "Reportes y análisis",
                "Control de acceso granular",
            ],
        }

    def verificar_conectividad_modulos(self) -> Dict[str, bool]:
        """Verifica que todos los submódulos estén conectados correctamente."""
        return {
            "autenticacion_manager": self.autenticacion_manager is not None,
            "usuarios_manager": self.usuarios_manager is not None,
            "consultas_manager": self.consultas_manager is not None,
            "db_connection": self.db_connection is not None,
        }

    # ====== MÉTODOS LEGACY DEPRECADOS (para transición) ======

    def obtener_lista_usuarios(self) -> List[Dict[str, Any]]:
        """
        DEPRECADO: Usar obtener_todos_usuarios() o obtener_usuarios_paginados()
        """
        print(
            "⚠️  Método deprecado. Usar obtener_todos_usuarios() o obtener_usuarios_paginados()"
        )
        return self.obtener_todos_usuarios()

    def buscar_usuario(self, criterio: str) -> List[Dict[str, Any]]:
        """
        DEPRECADO: Usar buscar_usuarios()
        """
        print("⚠️  Método deprecado. Usar buscar_usuarios()")
        return self.buscar_usuarios(criterio)

    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        DEPRECADO: Usar obtener_estadisticas_usuarios()
        """
        print("⚠️  Método deprecado. Usar obtener_estadisticas_usuarios()")
        return self.obtener_estadisticas_usuarios()

    def validar_usuario_duplicado(self, username: str, email: str) -> Dict[str, bool]:
        """
        DEPRECADO: Usar verificar_unicidad_username() y verificar_unicidad_email() por separado
        """
        print(
            "⚠️  Método deprecado. Usar verificar_unicidad_username() y verificar_unicidad_email()"
        )
        return {
            "username_disponible": self.verificar_unicidad_username(username),
            "email_disponible": self.verificar_unicidad_email(email),
        }

    # Métodos compatibles con nombres legacy
    def obtener_datos_paginados(self, offset=0, limit=50, filtros=None):
        """Compatibilidad con método legacy."""
        page = (offset // limit) + 1 if limit > 0 else 1
        return self.obtener_usuarios_paginados(page, limit, filtros)

    def obtener_total_registros(self, filtros=None):
        """Compatibilidad con método legacy."""
        resultado = self.obtener_usuarios_paginados(1, 1, filtros)
        return resultado.get("total", 0)


# ====== FUNCIÓN DE MIGRACIÓN AUTOMÁTICA ======


def migrar_desde_modelo_legacy(modelo_legacy) -> ModeloUsuariosRefactorizado:
    """
    Migra automáticamente desde un modelo legacy al refactorizado.

    Args:
        modelo_legacy: Instancia del modelo anterior

    Returns:
        ModeloUsuariosRefactorizado: Nueva instancia con datos migrados
    """
    if hasattr(modelo_legacy, "db_connection"):
        return ModeloUsuariosRefactorizado(modelo_legacy.db_connection)
    else:
        return ModeloUsuariosRefactorizado()


# ====== ALIAS PARA COMPATIBILIDAD ======

# Permite usar el nombre anterior del modelo
UsuariosModel = ModeloUsuariosRefactorizado
