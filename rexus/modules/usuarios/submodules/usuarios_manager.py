"""
Submódulo de Gestión de Usuarios - Rexus.app

Gestiona CRUD completo de usuarios y administración de permisos.
Responsabilidades:
- Crear, leer, actualizar, eliminar usuarios
- Gestión de roles y permisos
- Validaciones de unicidad
- Administración de perfil de usuario
"""

import datetime
from typing import Any, Dict, List, Optional

# Imports de seguridad unificados
from rexus.core.auth_decorators import auth_required, permission_required
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string

# Sistema de logging centralizado
from rexus.utils.app_logger import get_logger, log_error, log_info, log_warning

# SQLQueryManager unificado
try:
    from rexus.core.sql_query_manager import SQLQueryManager
except ImportError:
    # Fallback al script loader
    from rexus.utils.sql_script_loader import sql_script_loader

    class SQLQueryManager:
        def __init__(self):
            self.sql_loader = sql_script_loader

        def get_query(self, path, filename):
            # Construir nombre del script sin extensión
            script_name = f"{path.replace('scripts/sql/', '')}/{filename}"
            return self.sql_loader.load_script(script_name)


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

        def sanitize_email(self, email):
            import re

            if not email:
                return ""
            # Validación básica de email
            pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            return email if re.match(pattern, email) else ""


class UsuariosManager:
    """Gestor especializado para CRUD y administración de usuarios."""

    def __init__(self, db_connection=None):
        """Inicializa el gestor de usuarios."""
        self.db_connection = db_connection
        self.sql_manager = SQLQueryManager()
        self.sanitizer = DataSanitizer()
        self.sql_path = "scripts/sql/usuarios/gestion"
        self.logger = get_logger("usuarios.usuarios_manager")

    def _validate_table_name(self, table_name: str) -> str:
        """Valida nombre de tabla contra lista blanca."""
        import re

        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", table_name):
            raise ValueError(f"Nombre de tabla inválido: {table_name}")

        tablas_permitidas = {
            "usuarios",
            "permisos_usuario",
            "roles_usuario",
            "modulos_usuario",
        }
        if table_name not in tablas_permitidas:
            raise ValueError(f"Tabla no permitida: {table_name}")
        return table_name

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
        """
        Crea un nuevo usuario con validaciones completas.

        Args:
            username: Nombre de usuario único
            email: Email único
            password: Contraseña (será hasheada)
            rol: Rol del usuario
            activo: Si el usuario está activo
            datos_adicionales: Datos opcionales adicionales

        Returns:
            Dict con resultado de la operación
        """
        if not self.db_connection:
            return {"success": False, "error": "Sin conexión a base de datos"}

        try:
            # Sanitizar datos de entrada
            username_safe = sanitize_string(username, max_length=50)
            email_safe = self.sanitizer.sanitize_email(email)
            rol_safe = sanitize_string(rol, max_length=20)

            if not username_safe or not email_safe or not password:
                return {"success": False, "error": "Datos requeridos incompletos"}

            # Validar unicidad
            if not self.verificar_unicidad_username(username_safe):
                return {"success": False, "error": "El nombre de usuario ya existe"}

            if not self.verificar_unicidad_email(email_safe):
                return {"success": False, "error": "El email ya está registrado"}

            cursor = self.db_connection.cursor()

            # Generar hash de contraseña
            salt = self._generar_salt()
            password_hash = self._hash_password(password, salt)

            # Preparar datos del usuario
            datos_usuario = {
                "username": username_safe,
                "email": email_safe,
                "password_hash": password_hash,
                "salt": salt,
                "rol": rol_safe,
                "activo": activo,
                "fecha_creacion": datetime.datetime.now(),
                "ultimo_acceso": None,
            }

            # Agregar datos adicionales si se proporcionan
            if datos_adicionales:
                datos_usuario.update(
                    {
                        "nombre": sanitize_string(
                            datos_adicionales.get("nombre", "")
                        ),
                        "apellido": sanitize_string(
                            datos_adicionales.get("apellido", "")
                        ),
                        "telefono": sanitize_string(
                            datos_adicionales.get("telefono", "")
                        ),
                    }
                )

            # Insertar usuario
            query = self.sql_manager.get_query(self.sql_path, "crear_usuario")
            cursor.execute(
                query,
                (
                    datos_usuario["username"],
                    datos_usuario["email"],
                    datos_usuario["password_hash"],
                    datos_usuario["salt"],
                    datos_usuario["rol"],
                    datos_usuario["activo"],
                    datos_usuario["fecha_creacion"],
                    datos_usuario.get("nombre", ""),
                    datos_usuario.get("apellido", ""),
                    datos_usuario.get("telefono", ""),
                ),
            )

            usuario_id = cursor.lastrowid
            self.db_connection.commit()

            return {
                "success": True,
                "usuario_id": usuario_id,
                "mensaje": "Usuario creado exitosamente",
            }

        except Exception as e:
            if self.db_connection:
                self.db_connection.rollback()
            self.logger.error(f"Error creando usuario: {str(e)}", exc_info=True)
            return {"success": False, "error": "Error interno del sistema"}

    @auth_required
    @permission_required("view_usuarios")
    def obtener_usuario_por_id(self, usuario_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un usuario específico por ID."""
        if not self.db_connection or not usuario_id:
            return None

        try:
            usuario_id_safe = self.sanitizer.sanitize_integer(
                usuario_id, min_val=1
            )
            cursor = self.db_connection.cursor()

            query = self.sql_manager.get_query(self.sql_path, "obtener_usuario_por_id")
            cursor.execute(query, (usuario_id_safe,))

            row = cursor.fetchone()
            if not row:
                return None

            columns = [desc[0] for desc in cursor.description]
            usuario = dict(zip(columns, row))

            # Agregar permisos del usuario
            usuario["permisos"] = self.obtener_permisos_usuario(usuario_id_safe)

            # Limpiar datos sensibles
            if "password_hash" in usuario:
                del usuario["password_hash"]
            if "salt" in usuario:
                del usuario["salt"]

            return usuario

        except Exception as e:
            self.logger.error(f"Error obteniendo usuario: {str(e)}", exc_info=True)
            return None

    @auth_required
    @permission_required("view_usuarios")
    def obtener_usuario_por_nombre(self, username: str) -> Optional[Dict[str, Any]]:
        """Obtiene un usuario por nombre de usuario."""
        if not self.db_connection or not username:
            return None

        try:
            username_safe = sanitize_string(username)
            cursor = self.db_connection.cursor()

            query = self.sql_manager.get_query(
                self.sql_path, "obtener_usuario_por_nombre"
            )
            cursor.execute(query, (username_safe,))

            row = cursor.fetchone()
            if not row:
                return None

            columns = [desc[0] for desc in cursor.description]
            usuario = dict(zip(columns, row))

            # Limpiar datos sensibles para uso general
            if "password_hash" in usuario:
                del usuario["password_hash"]
            if "salt" in usuario:
                del usuario["salt"]

            return usuario

        except Exception as e:
            self.logger.error(f"Error obteniendo usuario por nombre: {str(e)}", exc_info=True)
            return None

    @auth_required
    @permission_required("change_usuarios")
    def actualizar_usuario(
        self, usuario_id: int, datos_actualizacion: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Actualiza un usuario existente."""
        if not self.db_connection or not usuario_id:
            return {"success": False, "error": "Parámetros inválidos"}

        try:
            usuario_id_safe = self.sanitizer.sanitize_integer(
                usuario_id, min_val=1
            )

            # Verificar que el usuario existe
            usuario_existente = self.obtener_usuario_por_id(usuario_id_safe)
            if not usuario_existente:
                return {"success": False, "error": "Usuario no encontrado"}

            cursor = self.db_connection.cursor()

            # Preparar campos a actualizar
            campos_actualizacion = {}

            if "email" in datos_actualizacion:
                email_safe = self.sanitizer.sanitize_email(
                    datos_actualizacion["email"]
                )
                if email_safe and self.verificar_unicidad_email(
                    email_safe, usuario_id_safe
                ):
                    campos_actualizacion["email"] = email_safe
                else:
                    return {"success": False, "error": "Email inválido o ya existe"}

            if "rol" in datos_actualizacion:
                campos_actualizacion["rol"] = sanitize_string(
                    datos_actualizacion["rol"], max_length=20
                )

            if "activo" in datos_actualizacion:
                campos_actualizacion["activo"] = bool(datos_actualizacion["activo"])

            if "nombre" in datos_actualizacion:
                campos_actualizacion["nombre"] = sanitize_string(
                    datos_actualizacion["nombre"], max_length=100
                )

            if "apellido" in datos_actualizacion:
                campos_actualizacion["apellido"] = sanitize_string(
                    datos_actualizacion["apellido"], max_length=100
                )

            if "telefono" in datos_actualizacion:
                campos_actualizacion["telefono"] = sanitize_string(
                    datos_actualizacion["telefono"], max_length=20
                )

            if not campos_actualizacion:
                return {
                    "success": False,
                    "error": "No hay campos válidos para actualizar",
                }

            # Agregar fecha de modificación
            campos_actualizacion["fecha_modificacion"] = datetime.datetime.now()

            # Construir query dinámicamente de forma segura
            set_clause = ", ".join(
                [f"{campo} = %s" for campo in campos_actualizacion.keys()]
            )
        # FIXED: SQL Injection vulnerability
            query = "UPDATE usuarios SET ? WHERE id = %s", (set_clause,)

            valores = list(campos_actualizacion.values()) + [usuario_id_safe]
            cursor.execute(query, valores)

            self.db_connection.commit()

            return {
                "success": True,
                "mensaje": "Usuario actualizado exitosamente",
                "campos_actualizados": list(campos_actualizacion.keys()),
            }

        except Exception as e:
            if self.db_connection:
                self.db_connection.rollback()
            self.logger.error(f"Error actualizando usuario: {str(e)}", exc_info=True)
            return {"success": False, "error": "Error interno del sistema"}

    @auth_required
    @permission_required("delete_usuarios")
    def eliminar_usuario(
        self, usuario_id: int, soft_delete: bool = True
    ) -> Dict[str, Any]:
        """Elimina un usuario (soft delete por defecto)."""
        if not self.db_connection or not usuario_id:
            return {"success": False, "error": "Parámetros inválidos"}

        try:
            usuario_id_safe = self.sanitizer.sanitize_integer(
                usuario_id, min_val=1
            )

            # Verificar que el usuario existe
            usuario_existente = self.obtener_usuario_por_id(usuario_id_safe)
            if not usuario_existente:
                return {"success": False, "error": "Usuario no encontrado"}

            cursor = self.db_connection.cursor()

            if soft_delete:
                # Soft delete - marcar como inactivo
                query = self.sql_manager.get_query(self.sql_path, "soft_delete_usuario")
                cursor.execute(query,
(False,
                    datetime.datetime.now(),
                    usuario_id_safe))
            else:
                # Hard delete - eliminar completamente
                query = self.sql_manager.get_query(self.sql_path, "hard_delete_usuario")
                cursor.execute(query, (usuario_id_safe,))

            self.db_connection.commit()

            return {
                "success": True,
                "mensaje": f"Usuario {'desactivado' if soft_delete else 'eliminado'} exitosamente",
            }

        except Exception as e:
            if self.db_connection:
                self.db_connection.rollback()
            self.logger.error(f"Error eliminando usuario: {str(e)}", exc_info=True)
            return {"success": False, "error": "Error interno del sistema"}

    def verificar_unicidad_username(
        self, username: str, excluir_usuario_id: Optional[int] = None
    ) -> bool:
        """Verifica si un nombre de usuario es único."""
        if not self.db_connection or not username:
            return False

        try:
            username_safe = sanitize_string(username)
            cursor = self.db_connection.cursor()

            if excluir_usuario_id:
                query = self.sql_manager.get_query(
                    self.sql_path, "verificar_unicidad_username_excluir"
                )
                cursor.execute(query, (username_safe, excluir_usuario_id))
            else:
                query = self.sql_manager.get_query(
                    self.sql_path, "verificar_unicidad_username"
                )
                cursor.execute(query, (username_safe,))

            result = cursor.fetchone()
            return (result[0] if result else 0) == 0

        except Exception as e:
            self.logger.error(f"Error verificando unicidad username: {str(e)}", exc_info=True)
            return False

    def verificar_unicidad_email(
        self, email: str, excluir_usuario_id: Optional[int] = None
    ) -> bool:
        """Verifica si un email es único."""
        if not self.db_connection or not email:
            return False

        try:
            email_safe = self.sanitizer.sanitize_email(email)
            if not email_safe:
                return False

            cursor = self.db_connection.cursor()

            if excluir_usuario_id:
                query = self.sql_manager.get_query(
                    self.sql_path, "verificar_unicidad_email_excluir"
                )
                cursor.execute(query, (email_safe, excluir_usuario_id))
            else:
                query = self.sql_manager.get_query(
                    self.sql_path, "verificar_unicidad_email"
                )
                cursor.execute(query, (email_safe,))

            result = cursor.fetchone()
            return (result[0] if result else 0) == 0

        except Exception as e:
            self.logger.error(f"Error verificando unicidad email: {str(e)}", exc_info=True)
            return False

    @auth_required
    @permission_required("view_usuarios")
    def obtener_permisos_usuario(self, usuario_id: int) -> List[str]:
        """Obtiene la lista de permisos de un usuario."""
        if not self.db_connection or not usuario_id:
            return []

        try:
            usuario_id_safe = self.sanitizer.sanitize_integer(
                usuario_id, min_val=1
            )
            cursor = self.db_connection.cursor()

            query = self.sql_manager.get_query(
                self.sql_path, "obtener_permisos_usuario"
            )
            cursor.execute(query, (usuario_id_safe,))

            permisos = []
            for row in cursor.fetchall():
                permisos.append(row[0])  # Primer columna es el permiso

            return permisos

        except Exception as e:
            self.logger.error(f"Error obteniendo permisos: {str(e)}", exc_info=True)
            return []

    @auth_required
    @permission_required("change_usuarios")
    def asignar_permiso_usuario(self, usuario_id: int, permiso: str) -> bool:
        """Asigna un permiso específico a un usuario."""
        if not self.db_connection or not usuario_id or not permiso:
            return False

        try:
            usuario_id_safe = self.sanitizer.sanitize_integer(
                usuario_id, min_val=1
            )
            permiso_safe = sanitize_string(permiso, max_length=50)

            cursor = self.db_connection.cursor()

            query = self.sql_manager.get_query(self.sql_path, "asignar_permiso_usuario")
            cursor.execute(
                query,
(usuario_id_safe,
                    permiso_safe,
                    datetime.datetime.now())
            )

            self.db_connection.commit()
            return cursor.rowcount > 0

        except Exception as e:
            if self.db_connection:
                self.db_connection.rollback()
            self.logger.error(f"Error asignando permiso: {str(e)}", exc_info=True)
            return False

    def _hash_password(self, password: str, salt: str) -> str:
        """Genera hash de contraseña con salt."""
        import hashlib

        return hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
        ).hex()

    def _generar_salt(self) -> str:
        """Genera un salt aleatorio."""
        import secrets

        return secrets.token_hex(32)
