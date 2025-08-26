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
            script_name = f
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
            self.    def obtener_usuario_por_nombre(self, username: str) -> Optional[Dict[str, Any]]:
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
            self.            self.            self.
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
            self.    def asignar_permiso_usuario(self, usuario_id: int, permiso: str) -> bool:
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
