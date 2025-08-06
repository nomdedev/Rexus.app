from rexus.core.auth_decorators import (
    admin_required,
    auth_required,
    permission_required,
)
from rexus.core.auth_manager import admin_required, auth_required, manager_required

# 🔒 DB Authorization Check - Verify user permissions before DB operations
# Ensure all database operations are properly authorized
# DB Authorization Check
"""
Modelo de Usuarios - Rexus.app v2.0.0

Gestiona la autenticación, permisos y CRUD completo de usuarios.
Incluye utilidades de seguridad para prevenir SQL injection y XSS.
"""

import datetime
import hashlib
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Importar utilidades de seguridad
try:
    # Agregar ruta src al path para imports de seguridad
    root_dir = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(root_dir))

    from utils.data_sanitizer import DataSanitizer, data_sanitizer
    from utils.sql_security import SQLSecurityValidator

    SECURITY_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] Security utilities not available: {e}")
    SECURITY_AVAILABLE = False
    data_sanitizer = None

# Importar nueva utilidad de seguridad SQL
try:
    from rexus.utils.sql_security import SQLSecurityError, validate_table_name

    SQL_SECURITY_AVAILABLE = True
except ImportError:
    print("[WARNING] SQL security utilities not available in usuarios")
    SQL_SECURITY_AVAILABLE = False
    validate_table_name = None
    SQLSecurityError = Exception


class UsuariosModel:
    """Modelo para gestión completa de usuarios y autenticación."""

    # Configuración de seguridad avanzada
    MAX_LOGIN_ATTEMPTS = 3  # Máximo de intentos de login
    LOCKOUT_DURATION = 900  # 15 minutos en segundos
    MIN_PASSWORD_LENGTH = 8
    PASSWORD_COMPLEXITY_RULES = {
        "uppercase": True,
        "lowercase": True,
        "digits": True,
        "special_chars": True,
    }

    # Roles disponibles
    ROLES = {
        "ADMIN": "Administrador",
        "SUPERVISOR": "Supervisor",
        "OPERADOR": "Operador",
        "USUARIO": "Usuario",
        "INVITADO": "Invitado",
    }

    # Estados de usuario
    ESTADOS = {
        "ACTIVO": "Activo",
        "INACTIVO": "Inactivo",
        "SUSPENDIDO": "Suspendido",
        "BLOQUEADO": "Bloqueado",
    }

    # Módulos del sistema
    MODULOS_SISTEMA = [
        "Obras",
        "Inventario",
        "Herrajes",
        "Pedidos",
        "Compras",
        "Logística",
        "Vidrios",
        "Mantenimiento",
        "Contabilidad",
        "Auditoría",
        "Usuarios",
        "Configuración",
        "Dashboard",
    ]

    def __init__(self, db_connection=None):
        self.db_connection = db_connection
        self.tabla_usuarios = "usuarios"
        self.tabla_roles = "roles"
        self.tabla_permisos = "permisos_usuario"
        self.tabla_sesiones = "sesiones_usuario"

        # Inicializar utilidades de seguridad
        self.security_available = SECURITY_AVAILABLE
        if self.security_available and data_sanitizer:
            self.data_sanitizer = data_sanitizer
            print("OK [USUARIOS] Utilidades de seguridad cargadas")
        else:
            self.data_sanitizer = None
            print("WARNING [USUARIOS] Utilidades de seguridad no disponibles")

        # Las tablas deben existir previamente - no crear desde la aplicación

    def _validate_table_name(self, table_name: str) -> str:
        """
        Valida el nombre de tabla para prevenir SQL injection.

        Args:
            table_name: Nombre de la tabla a validar

        Returns:
            str: Nombre de tabla validado

        Raises:
            Exception: Si el nombre no es válido o contiene caracteres peligrosos
        """
        if SQL_SECURITY_AVAILABLE and validate_table_name:
            try:
                return validate_table_name(table_name)
            except SQLSecurityError as e:
                print(f"[ERROR SEGURIDAD USUARIOS] {str(e)}")
                # Fallback a verificación básica
                pass

        # Verificación básica si la utilidad no está disponible
        if not table_name or not isinstance(table_name, str):
            raise ValueError("Nombre de tabla inválido")

        # Eliminar espacios en blanco
        table_name = table_name.strip()

        # Verificar que solo contenga caracteres alfanuméricos y guiones bajos
        if not all(c.isalnum() or c == "_" for c in table_name):
            raise ValueError(
                f"Nombre de tabla contiene caracteres no válidos: {table_name}"
            )

        # Verificar longitud razonable
        if len(table_name) > 64:
            raise ValueError(f"Nombre de tabla demasiado largo: {table_name}")

        return table_name.lower()

    def validar_usuario_duplicado(
        self, username: str, email: str, id_usuario_actual: Optional[int] = None
    ) -> Dict[str, bool]:
        """
        Valida si existe un usuario duplicado por username o email.

        Args:
            username: Nombre de usuario a verificar
            email: Email a verificar
            id_usuario_actual: ID del usuario actual (para edición)

        Returns:
            Dict[str, bool]: {"username_duplicado": bool, "email_duplicado": bool}
        """
        resultado = {"username_duplicado": False, "email_duplicado": False}

        if not self.db_connection:
            return resultado

        try:
            # Sanitizar datos
            if self.data_sanitizer:
                username_limpio = self.data_sanitizer.sanitize_string(username)
                email_limpio = self.data_sanitizer.sanitize_string(email)
            else:
                username_limpio = username.strip()
                email_limpio = email.strip()

            # Validar tabla
            tabla_validada = self._validate_table_name(self.tabla_usuarios)

            cursor = self.db_connection.cursor()

            # Verificar username duplicado
            if id_usuario_actual:
                query_username = """
                    SELECT COUNT(*) FROM usuarios 
                    WHERE LOWER(username) = ? AND id != ?
                """
                cursor.execute(
                    query_username, (username_limpio.lower(), id_usuario_actual)
                )
            else:
                query_username = """
                    SELECT COUNT(*) FROM usuarios 
                    WHERE LOWER(username) = ?
                """
                cursor.execute(query_username, (username_limpio.lower(),))

            resultado["username_duplicado"] = cursor.fetchone()[0] > 0

            # Verificar email duplicado
            if id_usuario_actual:
                query_email = (
                    "SELECT COUNT(*) FROM ["
                    + tabla_validada
                    + "] WHERE LOWER(email) = ? AND id != ?"
                )
                cursor.execute(query_email, (email_limpio.lower(), id_usuario_actual))
            else:
                query_email = (
                    "SELECT COUNT(*) FROM ["
                    + tabla_validada
                    + "] WHERE LOWER(email) = ?"
                )
                cursor.execute(query_email, (email_limpio.lower(),))

            resultado["email_duplicado"] = cursor.fetchone()[0] > 0

            return resultado

        except Exception as e:
            print(f"[ERROR USUARIOS] Error validando usuario duplicado: {e}")
            return resultado

    def registrar_intento_login(self, username: str, exitoso: bool = False) -> None:
        """
        Registra un intento de login y actualiza el contador de intentos fallidos.

        Args:
            username: Nombre de usuario
            exitoso: Si el login fue exitoso
        """
        if not self.db_connection:
            return

        try:
            # Sanitizar username
            if self.data_sanitizer:
                username_limpio = self.data_sanitizer.sanitize_string(username)
            else:
                username_limpio = username.strip()

            cursor = self.db_connection.cursor()
            tabla_validada = self._validate_table_name(self.tabla_usuarios)

            if exitoso:
                # Reset intentos fallidos si login exitoso
                query = f"UPDATE [{tabla_validada}] SET intentos_fallidos = 0, ultimo_acceso = GETDATE() WHERE LOWER(username) = ?"
                cursor.execute(query, (username_limpio.lower(),))
            else:
                # Incrementar intentos fallidos
                query = f"""
                UPDATE [{tabla_validada}] 
                SET intentos_fallidos = ISNULL(intentos_fallidos, 0) + 1,
                    ultimo_intento_fallido = GETDATE()
                WHERE LOWER(username) = ?
                """
                cursor.execute(query, (username_limpio.lower(),))

            self.db_connection.commit()

        except Exception as e:
            print(f"[ERROR USUARIOS] Error registrando intento login: {e}")

    def verificar_cuenta_bloqueada(self, username: str) -> bool:
        """
        Verifica si una cuenta está bloqueada por exceso de intentos fallidos.

        Args:
            username: Nombre de usuario a verificar

        Returns:
            bool: True si la cuenta está bloqueada
        """
        if not self.db_connection:
            return False

        try:
            # Sanitizar username
            if self.data_sanitizer:
                username_limpio = self.data_sanitizer.sanitize_string(username)
            else:
                username_limpio = username.strip()

            cursor = self.db_connection.cursor()
            tabla_validada = self._validate_table_name(self.tabla_usuarios)

            # Verificar intentos fallidos y tiempo transcurrido
            query = f"""
            SELECT 
                ISNULL(intentos_fallidos, 0) as intentos,
                ultimo_intento_fallido,
                CASE 
                    WHEN ultimo_intento_fallido IS NULL THEN 1
                    WHEN DATEDIFF(SECOND, ultimo_intento_fallido, GETDATE()) > ?
                    THEN 1
                    ELSE 0
                END as tiempo_expirado
            FROM [{tabla_validada}] 
            WHERE LOWER(username) = ?
            """

            cursor.execute(query, (self.LOCKOUT_DURATION, username_limpio.lower()))
            resultado = cursor.fetchone()

            if not resultado:
                return False

            intentos, ultimo_intento, tiempo_expirado = resultado

            # Si el tiempo de bloqueo ha expirado, reset intentos
            if tiempo_expirado and intentos >= self.MAX_LOGIN_ATTEMPTS:
                self.reset_intentos_login(username)
                return False

            # Cuenta bloqueada si excede intentos máximos
            return intentos >= self.MAX_LOGIN_ATTEMPTS

        except Exception as e:
            print(f"[ERROR USUARIOS] Error verificando cuenta bloqueada: {e}")
            return False

    def reset_intentos_login(self, username: str) -> bool:
        """
        Resetea los intentos de login de un usuario.

        Args:
            username: Nombre de usuario

        Returns:
            bool: True si se reseteo correctamente
        """
        if not self.db_connection:
            return False

        try:
            # Sanitizar username
            if self.data_sanitizer:
                username_limpio = self.data_sanitizer.sanitize_string(username)
            else:
                username_limpio = username.strip()

            cursor = self.db_connection.cursor()
            tabla_validada = self._validate_table_name(self.tabla_usuarios)

            query = f"UPDATE [{tabla_validada}] SET intentos_fallidos = 0 WHERE LOWER(username) = ?"
            cursor.execute(query, (username_limpio.lower(),))
            self.db_connection.commit()

            return cursor.rowcount > 0

        except Exception as e:
            print(f"[ERROR USUARIOS] Error reseteando intentos login: {e}")
            return False

    def validar_fortaleza_password(self, password: str) -> Dict[str, Any]:
        """
        Valida la fortaleza de una contraseña según las reglas de seguridad.

        Args:
            password: Contraseña a validar

        Returns:
            Dict con el resultado de la validación
        """
        resultado = {"valida": True, "errores": [], "puntuacion": 0}

        if not password:
            resultado["valida"] = False
            resultado["errores"].append("La contraseña es requerida")
            return resultado

        # Longitud mínima
        if len(password) < self.MIN_PASSWORD_LENGTH:
            resultado["valida"] = False
            resultado["errores"].append(
                f"La contraseña debe tener al menos {self.MIN_PASSWORD_LENGTH} caracteres"
            )
        else:
            resultado["puntuacion"] += 1

        # Verificar mayúsculas
        if self.PASSWORD_COMPLEXITY_RULES["uppercase"]:
            if not any(c.isupper() for c in password):
                resultado["valida"] = False
                resultado["errores"].append(
                    "La contraseña debe contener al menos una letra mayúscula"
                )
            else:
                resultado["puntuacion"] += 1

        # Verificar minúsculas
        if self.PASSWORD_COMPLEXITY_RULES["lowercase"]:
            if not any(c.islower() for c in password):
                resultado["valida"] = False
                resultado["errores"].append(
                    "La contraseña debe contener al menos una letra minúscula"
                )
            else:
                resultado["puntuacion"] += 1

        # Verificar dígitos
        if self.PASSWORD_COMPLEXITY_RULES["digits"]:
            if not any(c.isdigit() for c in password):
                resultado["valida"] = False
                resultado["errores"].append(
                    "La contraseña debe contener al menos un número"
                )
            else:
                resultado["puntuacion"] += 1

        # Verificar caracteres especiales
        if self.PASSWORD_COMPLEXITY_RULES["special_chars"]:
            special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            if not any(c in special_chars for c in password):
                resultado["valida"] = False
                resultado["errores"].append(
                    "La contraseña debe contener al menos un carácter especial"
                )
            else:
                resultado["puntuacion"] += 1

        # Puntuación adicional por longitud
        if len(password) >= 12:
            resultado["puntuacion"] += 1
        if len(password) >= 16:
            resultado["puntuacion"] += 1

        return resultado

    def _crear_tablas_si_no_existen(self):
        """
        ELIMINADO: Las tablas deben existir previamente en la base de datos.
        No es responsabilidad de la aplicación crear el esquema de BD.

        Para crear las tablas, ejecutar el script: database/create_tables.sql
        """
        print("ℹ️  [USUARIOS] Las tablas deben existir previamente en la base de datos")
        print("   Para crear las tablas, ejecutar: database/create_tables.sql")
        return

    def crear_usuarios_iniciales(self):
        """ELIMINADO: RIESGO DE SEGURIDAD CRÍTICO - No crear usuarios por defecto"""
        print("❌ SEGURIDAD CRÍTICA: No se crean usuarios automáticamente")
        print(
            "   Los usuarios deben ser creados manualmente por el administrador del sistema"
        )
        print(
            "   Usar script create_admin_simple.py para crear usuario admin manualmente"
        )
        return

    def obtener_usuario_por_nombre(self, nombre_usuario):
        """
        Obtiene un usuario por su nombre con sanitización de entrada.

        Args:
            nombre_usuario: Nombre del usuario a buscar

        Returns:
            Dict con datos del usuario o None si no existe
        """
        if not self.db_connection:
            return None

        # 🔒 SANITIZACIÓN DE ENTRADA
        if self.security_available and self.data_sanitizer and nombre_usuario:
            # Sanitizar el nombre de usuario para prevenir inyecciones
            nombre_limpio = self.data_sanitizer.sanitize_string(nombre_usuario)
            if not nombre_limpio:
                return None
        else:
            nombre_limpio = nombre_usuario.strip() if nombre_usuario else ""

        try:
            cursor = self.db_connection.connection.cursor()
            sql_select = """
            SELECT id, usuario, password_hash, nombre_completo, email, telefono, rol, estado,
                   fecha_creacion, fecha_modificacion, ultimo_acceso, intentos_fallidos, bloqueado_hasta, avatar, configuracion_personal, activo
            FROM usuarios WHERE usuario = ?
            """
            cursor.execute(sql_select, (nombre_limpio,))
            row = cursor.fetchone()
            print(
                f"[DEBUG obtener_usuario_por_nombre] Buscando usuario: {nombre_usuario}"
            )
            print(f"[DEBUG obtener_usuario_por_nombre] Resultado row: {row}")
            if row:
                columns = [desc[0] for desc in cursor.description]
                usuario_dict = dict(zip(columns, row))
                # Definir todas las claves esperadas y asignar None si falta
                claves_esperadas = [
                    "id",
                    "usuario",
                    "password_hash",
                    "nombre_completo",
                    "email",
                    "telefono",
                    "rol",
                    "estado",
                    "fecha_creacion",
                    "fecha_modificacion",
                    "ultimo_acceso",
                    "intentos_fallidos",
                    "bloqueado_hasta",
                    "avatar",
                    "configuracion_personal",
                    "activo",
                ]
                for clave in claves_esperadas:
                    if clave not in usuario_dict:
                        usuario_dict[clave] = None
                print(
                    f"[DEBUG obtener_usuario_por_nombre] Usuario dict: {usuario_dict}"
                )
                return usuario_dict
            print("[DEBUG obtener_usuario_por_nombre] No se encontró el usuario.")
            return None
        except Exception as e:
            print(f"[ERROR USUARIOS] Error obteniendo usuario: {e}")
            # Si hay error, devolver un dict vacío con todas las claves esperadas en None
            claves_esperadas = [
                "id",
                "usuario",
                "password_hash",
                "nombre_completo",
                "email",
                "telefono",
                "rol",
                "estado",
                "fecha_creacion",
                "fecha_modificacion",
                "ultimo_acceso",
                "intentos_fallidos",
                "bloqueado_hasta",
                "avatar",
                "configuracion_personal",
                "activo",
            ]
            return {clave: None for clave in claves_esperadas}

    def obtener_usuario_por_email(self, email):
        """
        Obtiene un usuario por su email con sanitización de entrada.

        Args:
            email: Email del usuario a buscar

        Returns:
            Dict con datos del usuario o None si no existe
        """
        if not self.db_connection:
            return None

        # 🔒 SANITIZACIÓN DE ENTRADA
        if self.security_available and self.data_sanitizer and email:
            # Sanitizar el email para prevenir inyecciones
            email_limpio = self.data_sanitizer.sanitize_string(email)
            if not email_limpio:
                return None
        else:
            email_limpio = email.strip() if email else ""

        try:
            cursor = self.db_connection.connection.cursor()
            sql_select = """
            SELECT id, usuario, password_hash, nombre_completo, email, telefono, rol, estado,
                   fecha_creacion, fecha_modificacion, ultimo_acceso, intentos_fallidos, bloqueado_hasta, avatar, configuracion_personal, activo
            FROM usuarios WHERE email = ?
            """
            cursor.execute(sql_select, (email_limpio,))
            row = cursor.fetchone()

            print(f"[DEBUG obtener_usuario_por_email] Buscando email: {email}")
            print(f"[DEBUG obtener_usuario_por_email] Resultado row: {row}")

            if row:
                columns = [desc[0] for desc in cursor.description]
                usuario_dict = dict(zip(columns, row))

                # Definir todas las claves esperadas y asignar None si falta
                claves_esperadas = [
                    "id",
                    "usuario",
                    "password_hash",
                    "nombre_completo",
                    "email",
                    "telefono",
                    "rol",
                    "estado",
                    "fecha_creacion",
                    "fecha_modificacion",
                    "ultimo_acceso",
                    "intentos_fallidos",
                    "bloqueado_hasta",
                    "avatar",
                    "configuracion_personal",
                    "activo",
                ]

                for clave in claves_esperadas:
                    if clave not in usuario_dict:
                        usuario_dict[clave] = None

                print(f"[DEBUG obtener_usuario_por_email] Usuario dict: {usuario_dict}")
                return usuario_dict

            print("[DEBUG obtener_usuario_por_email] No se encontró el usuario.")
            return None

        except Exception as e:
            print(f"[ERROR USUARIOS] Error obteniendo usuario por email: {e}")
            # Si hay error, devolver None
            return None

    def verificar_unicidad_username(self, username, excluir_usuario_id=None):
        """
        Verifica si un nombre de usuario ya existe en la base de datos.

        Args:
            username: Nombre de usuario a verificar
            excluir_usuario_id: ID de usuario a excluir de la búsqueda (para actualizaciones)

        Returns:
            bool: True si el username ya existe, False si está disponible
        """
        if not self.db_connection or not username:
            return False

        # 🔒 SANITIZACIÓN DE ENTRADA
        if self.security_available and self.data_sanitizer:
            username_limpio = self.data_sanitizer.sanitize_string(username)
            if not username_limpio:
                return True  # Si no se puede sanitizar, considerarlo como existente por seguridad
        else:
            username_limpio = username.strip() if username else ""

        try:
            cursor = self.db_connection.connection.cursor()

            if excluir_usuario_id:
                sql_select = (
                    "SELECT COUNT(*) FROM usuarios WHERE usuario = ? AND id != ?"
                )
                cursor.execute(sql_select, (username_limpio, excluir_usuario_id))
            else:
                sql_select = "SELECT COUNT(*) FROM usuarios WHERE usuario = ?"
                cursor.execute(sql_select, (username_limpio,))

            count = cursor.fetchone()[0]
            existe = count > 0

            print(
                f"[DEBUG verificar_unicidad_username] Username '{username}' existe: {existe}"
            )
            return existe

        except Exception as e:
            print(f"[ERROR USUARIOS] Error verificando unicidad de username: {e}")
            return True  # En caso de error, considerarlo como existente por seguridad

    def verificar_unicidad_email(self, email, excluir_usuario_id=None):
        """
        Verifica si un email ya existe en la base de datos.

        Args:
            email: Email a verificar
            excluir_usuario_id: ID de usuario a excluir de la búsqueda (para actualizaciones)

        Returns:
            bool: True si el email ya existe, False si está disponible
        """
        if not self.db_connection or not email:
            return False

        # 🔒 SANITIZACIÓN DE ENTRADA
        if self.security_available and self.data_sanitizer:
            email_limpio = self.data_sanitizer.sanitize_string(email)
            if not email_limpio:
                return True  # Si no se puede sanitizar, considerarlo como existente por seguridad
        else:
            email_limpio = email.strip() if email else ""

        try:
            cursor = self.db_connection.connection.cursor()

            if excluir_usuario_id:
                sql_select = "SELECT COUNT(*) FROM usuarios WHERE email = ? AND id != ?"
                cursor.execute(sql_select, (email_limpio, excluir_usuario_id))
            else:
                sql_select = "SELECT COUNT(*) FROM usuarios WHERE email = ?"
                cursor.execute(sql_select, (email_limpio,))

            count = cursor.fetchone()[0]
            existe = count > 0

            print(f"[DEBUG verificar_unicidad_email] Email '{email}' existe: {existe}")
            return existe

        except Exception as e:
            print(f"[ERROR USUARIOS] Error verificando unicidad de email: {e}")
            return True  # En caso de error, considerarlo como existente por seguridad

    def verificar_usuario_bloqueado(self, username):
        """
        Verifica si un usuario está bloqueado por exceso de intentos fallidos.

        Args:
            username: Nombre de usuario a verificar

        Returns:
            tuple: (bloqueado: bool, tiempo_restante: int en minutos)
        """
        if not self.db_connection or not username:
            return False, 0

        # 🔒 SANITIZACIÓN DE ENTRADA
        if self.security_available:
            username_limpio = self.data_sanitizer.sanitize_string(
                username, max_length=50
            )
            if not username_limpio:
                return True, 999  # Si no se puede sanitizar, bloquear por seguridad
        else:
            username_limpio = username

        try:
            cursor = self.db_connection.connection.cursor()
            sql_select = """
            SELECT intentos_fallidos, bloqueado_hasta 
            FROM usuarios 
            WHERE usuario = ?
            """
            cursor.execute(sql_select, (username_limpio,))
            row = cursor.fetchone()

            if not row:
                return False, 0  # Usuario no existe

            intentos_fallidos, bloqueado_hasta = row

            # Si no hay fecha de bloqueo, no está bloqueado
            if not bloqueado_hasta:
                return False, 0

            # Verificar si el tiempo de bloqueo ha expirado
            from datetime import datetime

            if isinstance(bloqueado_hasta, str):
                # Convertir string a datetime si es necesario
                try:
                    bloqueado_hasta = datetime.fromisoformat(
                        bloqueado_hasta.replace("Z", "+00:00")
                    )
                except Exception:
                    # Si no se puede parsear, asumir que no está bloqueado
                    return False, 0

            ahora = datetime.now()
            if ahora >= bloqueado_hasta:
                # El bloqueo ha expirado, limpiar el bloqueo
                self._limpiar_bloqueo_usuario(username_limpio)
                return False, 0
            else:
                # Calcular tiempo restante en minutos
                tiempo_restante = int((bloqueado_hasta - ahora).total_seconds() / 60)
                print(
                    f"[SECURITY] Usuario '{username}' bloqueado. Tiempo restante: {tiempo_restante} minutos"
                )
                return True, tiempo_restante

        except Exception as e:
            print(f"[ERROR USUARIOS] Error verificando bloqueo de usuario: {e}")
            return True, 999  # En caso de error, bloquear por seguridad

    def incrementar_intentos_fallidos(self, username):
        """
        Incrementa el contador de intentos fallidos para un usuario y lo bloquea si es necesario.

        Args:
            username: Nombre de usuario

        Returns:
            tuple: (bloqueado: bool, intentos_actuales: int, tiempo_bloqueo: int en minutos)
        """
        if not self.db_connection or not username:
            return False, 0, 0

        # 🔒 SANITIZACIÓN DE ENTRADA
        if self.security_available:
            username_limpio = self.data_sanitizer.sanitize_string(
                username, max_length=50
            )
            if not username_limpio:
                return True, 999, 999
        else:
            username_limpio = username

        # Configuración de bloqueo
        MAX_INTENTOS = 3  # Máximo de intentos permitidos
        TIEMPO_BLOQUEO_MINUTOS = 15  # Tiempo de bloqueo en minutos

        try:
            cursor = self.db_connection.connection.cursor()

            # Obtener intentos actuales
            sql_select = "SELECT intentos_fallidos FROM usuarios WHERE usuario = ?"
            cursor.execute(sql_select, (username_limpio,))
            row = cursor.fetchone()

            if not row:
                return False, 0, 0  # Usuario no existe

            intentos_actuales = row[0] or 0
            intentos_nuevos = intentos_actuales + 1

            if intentos_nuevos >= MAX_INTENTOS:
                # Bloquear usuario
                from datetime import datetime, timedelta

                bloqueado_hasta = datetime.now() + timedelta(
                    minutes=TIEMPO_BLOQUEO_MINUTOS
                )

                sql_update = """
                UPDATE usuarios 
                SET intentos_fallidos = ?, bloqueado_hasta = ? 
                WHERE usuario = ?
                """
                cursor.execute(
                    sql_update, (intentos_nuevos, bloqueado_hasta, username_limpio)
                )
                self.db_connection.connection.commit()

                print(
                    f"🔒 [SECURITY] Usuario '{username}' BLOQUEADO después de {intentos_nuevos} intentos fallidos"
                )
                print(f"🔒 [SECURITY] Bloqueo hasta: {bloqueado_hasta}")

                return True, intentos_nuevos, TIEMPO_BLOQUEO_MINUTOS
            else:
                # Solo incrementar contador
                sql_update = (
                    "UPDATE usuarios SET intentos_fallidos = ? WHERE usuario = ?"
                )
                cursor.execute(sql_update, (intentos_nuevos, username_limpio))
                self.db_connection.connection.commit()

                print(
                    f"⚠️ [SECURITY] Intento fallido #{intentos_nuevos} para usuario '{username}'"
                )

                return False, intentos_nuevos, 0

        except Exception as e:
            print(f"[ERROR USUARIOS] Error incrementando intentos fallidos: {e}")
            return True, 999, 999

    def limpiar_intentos_fallidos(self, username):
        """
        Limpia los intentos fallidos de un usuario después de un login exitoso.

        Args:
            username: Nombre de usuario
        """
        if not self.db_connection or not username:
            return

        # 🔒 SANITIZACIÓN DE ENTRADA
        if self.security_available:
            username_limpio = self.data_sanitizer.sanitize_string(
                username, max_length=50
            )
            if not username_limpio:
                return
        else:
            username_limpio = username

        try:
            cursor = self.db_connection.connection.cursor()
            sql_update = """
            UPDATE usuarios 
            SET intentos_fallidos = 0, bloqueado_hasta = NULL 
            WHERE usuario = ?
            """
            cursor.execute(sql_update, (username_limpio,))
            self.db_connection.connection.commit()

            print(
                f"✅ [SECURITY] Intentos fallidos limpiados para usuario '{username}'"
            )

        except Exception as e:
            print(f"[ERROR USUARIOS] Error limpiando intentos fallidos: {e}")

    def _limpiar_bloqueo_usuario(self, username):
        """
        Método interno para limpiar el bloqueo de un usuario cuando ha expirado.

        Args:
            username: Nombre de usuario (ya sanitizado)
        """
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.connection.cursor()
            sql_update = """
            UPDATE usuarios 
            SET intentos_fallidos = 0, bloqueado_hasta = NULL 
            WHERE usuario = ?
            """
            cursor.execute(sql_update, (username,))
            self.db_connection.connection.commit()

            print(f"✅ [SECURITY] Bloqueo expirado limpiado para usuario '{username}'")

        except Exception as e:
            print(f"[ERROR USUARIOS] Error limpiando bloqueo expirado: {e}")

    def obtener_modulos_permitidos(self, usuario_data):
        """Obtiene los módulos permitidos para un usuario."""
        if not usuario_data or not isinstance(usuario_data, dict):
            return ["Configuración"]

        permisos = usuario_data.get("permisos_modulos", "")

        if permisos == "ALL":
            return [
                "Obras",
                "Inventario",
                "Herrajes",
                "Compras / Pedidos",
                "Logística",
                "Vidrios",
                "Mantenimiento",
                "Producción",
                "Contabilidad",
                "Auditoría",
                "Usuarios",
                "Configuración",
            ]
        elif permisos:
            return [m.strip() for m in permisos.split(",")]
        else:
            return ["Configuración"]

    def autenticar_usuario_seguro(self, username: str, password: str) -> Dict[str, Any]:
        """
        Autentica un usuario con todas las validaciones de seguridad avanzadas.

        Args:
            username: Nombre de usuario
            password: Contraseña en texto plano

        Returns:
            Dict con resultado de la autenticación:
            {
                'success': bool,
                'user_data': dict | None,
                'message': str,
                'blocked_until': datetime | None,
                'attempts_remaining': int
            }
        """
        resultado = {
            "success": False,
            "user_data": None,
            "message": "",
            "blocked_until": None,
            "attempts_remaining": 0,
        }

        if not username or not password:
            resultado["message"] = "Usuario y contraseña son requeridos"
            return resultado

        try:
            # 1. Verificar si la cuenta está bloqueada
            if self.verificar_cuenta_bloqueada(username):
                resultado["message"] = (
                    f"Cuenta bloqueada por exceso de intentos fallidos. Intente después de {self.LOCKOUT_DURATION // 60} minutos"
                )
                return resultado

            # 2. Obtener datos del usuario
            usuario_data = self.obtener_usuario_por_nombre(username)

            if not usuario_data:
                # Registrar intento fallido para prevenir enumeración de usuarios
                self.registrar_intento_login(username, exitoso=False)
                resultado["message"] = "Credenciales inválidas"
                return resultado

            # 3. Verificar estado de la cuenta
            if not usuario_data.get("activo", True):
                resultado["message"] = "Cuenta desactivada"
                return resultado

            # 4. Verificar contraseña
            password_hash_almacenado = usuario_data.get("password_hash", "")
            if not password_hash_almacenado or not self._verificar_password(
                password, password_hash_almacenado
            ):
                # Registrar intento fallido
                self.registrar_intento_login(username, exitoso=False)

                # Calcular intentos restantes
                intentos_actuales = (usuario_data.get("intentos_fallidos") or 0) + 1
                intentos_restantes = max(0, self.MAX_LOGIN_ATTEMPTS - intentos_actuales)

                resultado["attempts_remaining"] = intentos_restantes

                if intentos_restantes <= 0:
                    resultado["message"] = (
                        f"Cuenta bloqueada por exceso de intentos. Intente después de {self.LOCKOUT_DURATION // 60} minutos"
                    )
                else:
                    resultado["message"] = (
                        f"Credenciales inválidas. {intentos_restantes} intentos restantes"
                    )

                return resultado

            # 5. Login exitoso - limpiar intentos fallidos
            self.registrar_intento_login(username, exitoso=True)

            # 6. Preparar datos del usuario para la sesión (sin password_hash)
            user_session_data = usuario_data.copy()
            user_session_data.pop("password_hash", None)

            resultado.update(
                {
                    "success": True,
                    "user_data": user_session_data,
                    "message": "Autenticación exitosa",
                    "attempts_remaining": self.MAX_LOGIN_ATTEMPTS,
                }
            )

            return resultado

        except Exception as e:
            print(f"[ERROR USUARIOS] Error en autenticación segura: {e}")
            resultado["message"] = "Error interno en la autenticación"
            return resultado

    def crear_usuario(
        self,
        datos_usuario: Dict[str, Any],
    ) -> Tuple[bool, str]:
        """
        Crea un nuevo usuario en el sistema con validación y sanitización completa.

        Args:
            datos_usuario: Diccionario con los datos del usuario

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        if not self.db_connection:
            return False, "Sin conexión a la base de datos"

        try:
            # 🔒 SANITIZACIÓN Y VALIDACIÓN DE DATOS
            if self.security_available and self.data_sanitizer:
                # Sanitizar todos los datos de entrada
                datos_limpios = self.data_sanitizer.sanitize_dict(datos_usuario)

                # Validaciones específicas
                if not datos_limpios.get("usuario"):
                    return False, "El nombre de usuario es requerido"
                if not datos_limpios.get("password"):
                    return False, "La contraseña es requerida"
                if not datos_limpios.get("nombre_completo"):
                    return False, "El nombre completo es requerido"

                # Validar formato de email si se proporciona
                if datos_limpios.get("email"):
                    try:
                        email_limpio = self.data_sanitizer.sanitize_string(
                            datos_limpios["email"]
                        )
                        if (
                            not email_limpio
                            or len(email_limpio) < 5
                            or "@" not in email_limpio
                        ):
                            return False, "Formato de email inválido"
                        datos_limpios["email"] = email_limpio
                    except Exception:
                        return False, "Formato de email inválido"

                # Validar teléfono si se proporciona
                if datos_limpios.get("telefono"):
                    telefono_limpio = self.data_sanitizer.sanitize_string(
                        datos_limpios["telefono"]
                    )
                    datos_limpios["telefono"] = telefono_limpio

            else:
                # Sin utilidades de seguridad, usar datos originales con precaución
                datos_limpios = datos_usuario.copy()
                print(
                    "WARNING [USUARIOS] Creando usuario sin sanitización de seguridad"
                )

            cursor = self.db_connection.connection.cursor()

            # Verificar que el usuario no exista
            cursor.execute(
                "SELECT COUNT(*) FROM usuarios WHERE usuario = ?",
                (datos_limpios["usuario"],),
            )
            if cursor.fetchone()[0] > 0:
                return False, f"El usuario '{datos_limpios['usuario']}' ya existe"

            # Verificar que el email no exista
            if datos_limpios.get("email"):
                cursor.execute(
                    "SELECT COUNT(*) FROM usuarios WHERE email = ?",
                    (datos_limpios["email"],),
                )
                if cursor.fetchone()[0] > 0:
                    return (
                        False,
                        f"El email '{datos_limpios['email']}' ya está registrado",
                    )

            # Hashear la contraseña
            password_hash = self._hashear_password(datos_limpios["password"])

            # Insertar usuario con datos sanitizados
            cursor.execute(
                """
                INSERT INTO usuarios 
                (usuario, password_hash, nombre_completo, email, telefono, rol, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    datos_limpios["usuario"],
                    password_hash,
                    datos_limpios["nombre_completo"],
                    datos_limpios.get("email", ""),
                    datos_limpios.get("telefono", ""),
                    datos_limpios.get("rol", "USUARIO"),
                    datos_limpios.get("estado", "ACTIVO"),
                ),
            )

            # Obtener ID del usuario creado
            cursor.execute("SELECT @@IDENTITY")
            usuario_id = cursor.fetchone()[0]

            # Asignar permisos por defecto
            permisos_defecto = datos_usuario.get("permisos", ["Configuración"])
            for modulo in permisos_defecto:
                cursor.execute(
                    """
                    INSERT INTO permisos_usuario (usuario_id, modulo, permisos)
                    VALUES (?, ?, ?)
                """,
                    (usuario_id, modulo, "leer"),
                )

            self.db_connection.connection.commit()
            print(
                f"[USUARIOS] Usuario '{datos_usuario['usuario']}' creado exitosamente"
            )
            return True, f"Usuario '{datos_usuario['usuario']}' creado exitosamente"

        except Exception as e:
            print(f"[ERROR USUARIOS] Error creando usuario: {e}")
            if self.db_connection:
                self.db_connection.connection.rollback()
            return False, f"Error creando usuario: {str(e)}"

    def obtener_todos_usuarios(self) -> List[Dict[str, Any]]:
        """Obtiene todos los usuarios del sistema."""
        if not self.db_connection:
            return self._get_usuarios_demo()

        try:
            cursor = self.db_connection.connection.cursor()
            cursor.execute("""
                SELECT id, usuario, nombre_completo, email, telefono, rol, estado,
                       fecha_creacion, ultimo_acceso, intentos_fallidos
                FROM usuarios
                WHERE activo = 1
                ORDER BY nombre_completo
            """)

            columns = [desc[0] for desc in cursor.description]
            usuarios = []

            for row in cursor.fetchall():
                usuario = dict(zip(columns, row))
                usuario["rol_texto"] = self.ROLES.get(usuario["rol"], usuario["rol"])
                usuario["estado_texto"] = self.ESTADOS.get(
                    usuario["estado"], usuario["estado"]
                )

                # Obtener permisos
                usuario["permisos"] = self.obtener_permisos_usuario(usuario["id"])
                usuarios.append(usuario)

            return usuarios

        except Exception as e:
            print(f"[ERROR USUARIOS] Error obteniendo usuarios: {e}")
            return self._get_usuarios_demo()

    def obtener_usuario_por_id(self, usuario_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un usuario por su ID."""
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.connection.cursor()
            cursor.execute(
                """
                SELECT id, usuario, nombre_completo, email, telefono, rol, estado,
                       fecha_creacion, fecha_modificacion, ultimo_acceso, intentos_fallidos,
                       bloqueado_hasta, avatar, configuracion_personal
                FROM usuarios
                WHERE id = ? AND activo = 1
            """,
                (usuario_id,),
            )

            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                usuario = dict(zip(columns, row))
                usuario["permisos"] = self.obtener_permisos_usuario(usuario_id)
                return usuario

            return None

        except Exception as e:
            print(f"[ERROR USUARIOS] Error obteniendo usuario por ID: {e}")
            return None

    def actualizar_usuario(
        self,
        usuario_id: int,
        datos_usuario: Dict[str, Any],
    ) -> Tuple[bool, str]:
        """
        Actualiza los datos de un usuario.

        Args:
            usuario_id: ID del usuario a actualizar
            datos_usuario: Nuevos datos del usuario

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        if not self.db_connection:
            return False, "Sin conexión a la base de datos"

        try:
            cursor = self.db_connection.connection.cursor()

            # Verificar que el usuario exista
            cursor.execute(
                "SELECT COUNT(*) FROM usuarios WHERE id = ?",
                (usuario_id,),
            )
            if cursor.fetchone()[0] == 0:
                return False, "Usuario no encontrado"

            # Actualizar datos básicos
            cursor.execute(
                """
                UPDATE usuarios
                SET nombre_completo = ?, email = ?, telefono = ?, rol = ?, estado = ?,
                    fecha_modificacion = GETDATE()
                WHERE id = ?
            """,
                (
                    datos_usuario["nombre_completo"],
                    datos_usuario.get("email", ""),
                    datos_usuario.get("telefono", ""),
                    datos_usuario.get("rol", "USUARIO"),
                    datos_usuario.get("estado", "ACTIVO"),
                    usuario_id,
                ),
            )

            # Actualizar contraseña si se proporciona
            if datos_usuario.get("password"):
                password_hash = self._hashear_password(datos_usuario["password"])
                cursor.execute(
                    """
                    UPDATE usuarios
                    SET password_hash = ?, intentos_fallidos = 0, bloqueado_hasta = NULL
                    WHERE id = ?
                """,
                    (password_hash, usuario_id),
                )

            # Actualizar permisos
            if "permisos" in datos_usuario:
                cursor.execute(
                    "DELETE FROM permisos_usuario WHERE usuario_id = ?",
                    (usuario_id,),
                )

                for modulo in datos_usuario["permisos"]:
                    cursor.execute(
                        """
                        INSERT INTO permisos_usuario (usuario_id, modulo, permisos)
                        VALUES (?, ?, ?)
                    """,
                        (usuario_id, modulo, "leer,escribir"),
                    )

            self.db_connection.connection.commit()
            return True, "Usuario actualizado exitosamente"

        except Exception as e:
            print(f"[ERROR USUARIOS] Error actualizando usuario: {e}")
            if self.db_connection:
                self.db_connection.connection.rollback()
            return False, f"Error actualizando usuario: {str(e)}"

    def eliminar_usuario(
        self,
        usuario_id: int,
    ) -> Tuple[bool, str]:
        """
        Elimina un usuario del sistema (eliminación lógica).

        Args:
            usuario_id: ID del usuario a eliminar

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        if not self.db_connection:
            return False, "Sin conexión a la base de datos"

        try:
            cursor = self.db_connection.connection.cursor()

            # Verificar que el usuario exista
            cursor.execute("SELECT usuario FROM usuarios WHERE id = ?", (usuario_id,))
            row = cursor.fetchone()
            if not row:
                return False, "Usuario no encontrado"

            nombre_usuario = row[0]

            # No permitir eliminar el usuario admin
            if nombre_usuario == "admin":
                return False, "No se puede eliminar el usuario administrador"

            # Eliminación lógica
            cursor.execute(
                """
                UPDATE usuarios
                SET activo = 0, estado = 'INACTIVO', fecha_modificacion = GETDATE()
                WHERE id = ?
            """,
                (usuario_id,),
            )

            # Cerrar sesiones activas
            cursor.execute(
                """
                UPDATE sesiones_usuario
                SET activa = 0, fecha_fin = GETDATE()
                WHERE usuario_id = ? AND activa = 1
            """,
                (usuario_id,),
            )

            self.db_connection.connection.commit()
            return True, f"Usuario '{nombre_usuario}' eliminado exitosamente"

        except Exception as e:
            print(f"[ERROR USUARIOS] Error eliminando usuario: {e}")
            if self.db_connection:
                self.db_connection.connection.rollback()
            return False, f"Error eliminando usuario: {str(e)}"

    def obtener_permisos_usuario(self, usuario_id: int) -> List[str]:
        """Obtiene los permisos de un usuario."""
        if not self.db_connection:
            return ["Configuración"]

        try:
            cursor = self.db_connection.connection.cursor()
            cursor.execute(
                """
                SELECT modulo FROM permisos_usuario
                WHERE usuario_id = ?
            """,
                (usuario_id,),
            )

            return [row[0] for row in cursor.fetchall()]

        except Exception as e:
            print(f"[ERROR USUARIOS] Error obteniendo permisos: {e}")
            return ["Configuración"]

    def cambiar_password(
        self,
        usuario_id: int,
        password_actual: str,
        password_nueva: str,
    ) -> Tuple[bool, str]:
        """
        Cambia la contraseña de un usuario.

        Args:
            usuario_id: ID del usuario
            password_actual: Contraseña actual
            password_nueva: Nueva contraseña

        Returns:
            Tuple[bool, str]: (éxito, mensaje)
        """
        if not self.db_connection:
            return False, "Sin conexión a la base de datos"

        try:
            cursor = self.db_connection.connection.cursor()

            # Verificar contraseña actual
            cursor.execute(
                "SELECT password_hash FROM usuarios WHERE id = ?",
                (usuario_id,),
            )
            row = cursor.fetchone()
            if not row:
                return False, "Usuario no encontrado"

            if not self._verificar_password(password_actual, row[0]):
                return False, "Contraseña actual incorrecta"

            # Actualizar contraseña
            nueva_hash = self._hashear_password(password_nueva)
            cursor.execute(
                """
                UPDATE usuarios
                SET password_hash = ?, intentos_fallidos = 0, bloqueado_hasta = NULL,
                    fecha_modificacion = GETDATE()
                WHERE id = ?
            """,
                (nueva_hash, usuario_id),
            )

            self.db_connection.connection.commit()
            return True, "Contraseña cambiada exitosamente"

        except Exception as e:
            print(f"[ERROR USUARIOS] Error cambiando contraseña: {e}")
            if self.db_connection:
                self.db_connection.connection.rollback()
            return False, f"Error cambiando contraseña: {str(e)}"

    def obtener_estadisticas_usuarios(self) -> Dict[str, Any]:
        """Obtiene estadísticas de usuarios."""
        if not self.db_connection:
            return self._get_estadisticas_demo()

        try:
            cursor = self.db_connection.connection.cursor()

            stats = {}

            # Total de usuarios
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE activo = 1")
            stats["total_usuarios"] = cursor.fetchone()[0]

            # Usuarios por estado
            cursor.execute("""
                SELECT estado, COUNT(*) 
                FROM usuarios 
                WHERE activo = 1
                GROUP BY estado
            """)
            stats["por_estado"] = {row[0]: row[1] for row in cursor.fetchall()}

            # Usuarios por rol
            cursor.execute("""
                SELECT rol, COUNT(*) 
                FROM usuarios 
                WHERE activo = 1
                GROUP BY rol
            """)
            stats["por_rol"] = {row[0]: row[1] for row in cursor.fetchall()}

            # Usuarios activos en el último mes
            cursor.execute("""
                SELECT COUNT(*) FROM usuarios
                WHERE activo = 1 AND ultimo_acceso >= DATEADD(MONTH, -1, GETDATE())
            """)
            stats["activos_mes"] = cursor.fetchone()[0]

            # Usuarios creados este mes
            cursor.execute("""
                SELECT COUNT(*) FROM usuarios
                WHERE activo = 1 AND MONTH(fecha_creacion) = MONTH(GETDATE()) 
                AND YEAR(fecha_creacion) = YEAR(GETDATE())
            """)
            stats["creados_mes"] = cursor.fetchone()[0]

            return stats

        except Exception as e:
            print(f"[ERROR USUARIOS] Error obteniendo estadísticas: {e}")
            return self._get_estadisticas_demo()

    def _hashear_password(self, password: str) -> str:
        """Hashea una contraseña usando sistema seguro."""
        from rexus.utils.password_security import hash_password_secure

        return hash_password_secure(password)

    def _verificar_password(self, password: str, hash_almacenado: str) -> bool:
        """Verifica una contraseña contra su hash usando sistema seguro."""
        from rexus.utils.password_security import verify_password_secure

        return verify_password_secure(password, hash_almacenado)

    def _get_usuarios_demo(self) -> List[Dict[str, Any]]:
        """Datos demo cuando no hay conexión a BD."""
        return [
            {
                "id": 1,
                "usuario": "admin",
                "nombre_completo": "Administrador Sistema",
                "email": "admin@rexus.app",
                "telefono": "+1234567890",
                "rol": "ADMIN",
                "rol_texto": "Administrador",
                "estado": "ACTIVO",
                "estado_texto": "Activo",
                "fecha_creacion": "2025-01-01",
                "ultimo_acceso": "2025-01-15",
                "intentos_fallidos": 0,
                "permisos": self.MODULOS_SISTEMA,
            },
            {
                "id": 2,
                "usuario": "supervisor",
                "nombre_completo": "Supervisor General",
                "email": "supervisor@rexus.app",
                "telefono": "+1234567891",
                "rol": "SUPERVISOR",
                "rol_texto": "Supervisor",
                "estado": "ACTIVO",
                "estado_texto": "Activo",
                "fecha_creacion": "2025-01-02",
                "ultimo_acceso": "2025-01-14",
                "intentos_fallidos": 0,
                "permisos": ["Obras", "Inventario", "Pedidos", "Dashboard"],
            },
        ]

    def _get_estadisticas_demo(self) -> Dict[str, Any]:
        """Estadísticas demo cuando no hay conexión a BD."""
        return {
            "total_usuarios": 12,
            "por_estado": {
                "ACTIVO": 10,
                "INACTIVO": 2,
                "SUSPENDIDO": 0,
                "BLOQUEADO": 0,
            },
            "por_rol": {"ADMIN": 1, "SUPERVISOR": 2, "OPERADOR": 5, "USUARIO": 4},
            "activos_mes": 8,
            "creados_mes": 2,
        }

    def obtener_datos_paginados(self, offset=0, limit=50, filtros=None):
        """
        Obtiene datos paginados de la tabla principal

        Args:
            offset: Número de registros a saltar
            limit: Número máximo de registros a devolver
            filtros: Filtros adicionales a aplicar

        Returns:
            tuple: (datos, total_registros)
        """
        try:
            if not self.db_connection:
                return [], 0

            cursor = self.db_connection.cursor()

            # Query base
            base_query = self._get_base_query()
            count_query = self._get_count_query()

            # Aplicar filtros si existen
            where_clause = ""
            params = []

            if filtros:
                where_conditions = []
                for campo, valor in filtros.items():
                    if valor:
                        where_conditions.append(f"{campo} LIKE ?")
                        params.append(f"%{valor}%")

                if where_conditions:
                    where_clause = " WHERE " + " AND ".join(where_conditions)

            # Obtener total de registros
            full_count_query = count_query + where_clause
            cursor.execute(full_count_query, params)
            total_registros = cursor.fetchone()[0]

            # Obtener datos paginados
            paginated_query = f"{base_query}{where_clause} ORDER BY id DESC OFFSET ? ROWS FETCH NEXT ? ROWS ONLY"
            cursor.execute(paginated_query, params + [offset, limit])

            datos = []
            for row in cursor.fetchall():
                datos.append(self._row_to_dict(row, cursor.description))

            return datos, total_registros

        except Exception as e:
            print(f"[ERROR] Error obteniendo datos paginados: {e}")
            return [], 0

    def obtener_total_registros(self, filtros=None):
        """Obtiene el total de registros disponibles"""
        try:
            _, total = self.obtener_datos_paginados(offset=0, limit=1, filtros=filtros)
            return total
        except Exception as e:
            print(f"[ERROR] Error obteniendo total de registros: {e}")
            return 0

    def _get_base_query(self):
        """Obtiene la query base para paginación (debe ser implementado por cada modelo)"""
        # Esta es una implementación genérica
        tabla_principal = getattr(self, "tabla_principal", "tabla_principal")
        return f"SELECT * FROM {tabla_principal}"

    def _get_count_query(self):
        """Obtiene la query de conteo (debe ser implementado por cada modelo)"""
        tabla_principal = getattr(self, "tabla_principal", "tabla_principal")
        return f"SELECT COUNT(*) FROM {tabla_principal}"

    def _row_to_dict(self, row, description):
        """Convierte una fila de base de datos a diccionario"""
        return {desc[0]: row[i] for i, desc in enumerate(description)}
