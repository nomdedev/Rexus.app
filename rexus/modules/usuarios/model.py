
# Importar utilidades de sanitización
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string

# Definir data_sanitizer para compatibilidad
try:
    from rexus.utils.unified_sanitizer import unified_sanitizer
    data_sanitizer = unified_sanitizer
except ImportError:
    try:
        from rexus.utils.data_sanitizer import DataSanitizer
        data_sanitizer = DataSanitizer()
    except ImportError:
        data_sanitizer = None

from rexus.utils.sql_query_manager import SQLQueryManager

# Sistema de cache inteligente para optimizar consultas frecuentes
from rexus.utils.intelligent_cache import cached_query, invalidate_cache
from rexus.utils.unified_sanitizer import sanitize_string

# [LOCK] DB Authorization Check - Verify user permissions before DB operations
# Ensure all database operations are properly authorized
"""
Modelo de Usuarios - Rexus.app v2.0.0

Gestiona la autenticación, permisos y CRUD completo de usuarios.
Incluye utilidades de seguridad para prevenir SQL injection y XSS.

MIGRADO A SQL EXTERNO - Todas las consultas ahora usan SQLQueryManager
para prevenir inyección SQL y mejorar mantenibilidad.
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Importar sistema de logging centralizado
from rexus.utils.app_logger import get_logger, log_security, log_error, log_warning, log_info

# Configurar logger
logger = get_logger("usuarios.model")

# Importar utilidades de seguridad
try:
    # Agregar ruta src al path para imports de seguridad
    root_dir = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(root_dir))
    SECURITY_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Security utilities not available: {e}")
    SECURITY_AVAILABLE = False
    data_sanitizer = None

# Importar nueva utilidad de seguridad SQL
try:
    from rexus.utils.sql_security import SQLSecurityError, validate_table_name

    SQL_SECURITY_AVAILABLE = True
except ImportError:
    logger.warning("SQL security utilities not available in usuarios")
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
        # Validar conexión de base de datos
        if db_connection is None:
            logger.warning("UsuariosModel inicializado sin conexión a BD - usando modo limitado")
        else:
            # Validar que la conexión tenga los métodos necesarios
            try:
                if hasattr(db_connection, 'cursor') and hasattr(db_connection, 'commit'):
                    logger.info("Conexión BD válida en UsuariosModel")
                else:
                    logger.error("Conexión BD inválida - no tiene métodos cursor/commit")
                    db_connection = None
            except (AttributeError, TypeError, ConnectionError) as e:
                logger.error(f"Error validando conexión BD: {e}")
                db_connection = None
            
        self.db_connection = db_connection
        self.tabla_usuarios = "usuarios"
        self.tabla_roles = "roles"
        self.tabla_permisos = "permisos_usuario"
        self.tabla_sesiones = "sesiones_usuario"

        # Inicializar SQLQueryManager para consultas seguras
        self.sql_manager = SQLQueryManager()

        # Inicializar utilidades de seguridad
        self.security_available = SECURITY_AVAILABLE
        if self.security_available and data_sanitizer:
            self.data_sanitizer = data_sanitizer
            logger.info("OK [USUARIOS] Utilidades de seguridad cargadas")
        else:
            self.data_sanitizer = None
            logger.warning("WARNING [USUARIOS] Utilidades de seguridad no disponibles")

        # Inicializar gestores de submódulos (opcional)
        try:
            from rexus.modules.usuarios.submodules.profiles_manager import ProfilesManager
            self.profiles_manager = ProfilesManager(self)
        except ImportError:
            self.profiles_manager = None

        try:
            from rexus.modules.usuarios.submodules.permissions_manager import PermissionsManager
            self.permissions_manager = PermissionsManager(self)
        except ImportError:
            self.permissions_manager = None

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
                log_security("CRITICAL", f"Error de seguridad en usuarios: {str(e)}")
                # Fallback a verificación básica

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
                username_limpio = sanitize_string(username)
                email_limpio = sanitize_string(email)
            else:
                username_limpio = username.strip()
                email_limpio = email.strip()

            # Validar tabla
            self._validate_table_name(self.tabla_usuarios)

            # Validar conexión BD antes de crear cursor
            if not self.db_connection:
                logger.error("Conexión BD no disponible en validar_usuario_duplicado")
                return resultado
                
            cursor = self.db_connection.cursor()


            # Usar SQL externo para verificar username duplicado
            if id_usuario_actual:
                sql_username = self.sql_manager.get_query('usuarios', 'verificar_username_duplicado_edicion')
                cursor.execute(sql_username, {"username": username_limpio.lower(), "id": id_usuario_actual})
            else:
                sql_username = self.sql_manager.get_query('usuarios', 'verificar_username_duplicado')
                cursor.execute(sql_username, {"username": username_limpio.lower()})
            resultado["username_duplicado"] = cursor.fetchone()[0] > 0

            # Usar SQL externo para verificar email duplicado
            if id_usuario_actual:
                sql_email = self.sql_manager.get_query('usuarios', 'verificar_email_duplicado_edicion')
                cursor.execute(sql_email, {"email": email_limpio.lower(), "id": id_usuario_actual})
            else:
                sql_email = self.sql_manager.get_query('usuarios', 'verificar_email_duplicado')
                cursor.execute(sql_email, {"email": email_limpio.lower()})
            resultado["email_duplicado"] = cursor.fetchone()[0] > 0

            return resultado

        except Exception as e:
            logger.error(f"Error validando usuario duplicado: {e}", exc_info=True)
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
                username_limpio = sanitize_string(username)
            else:
                username_limpio = username.strip()

            cursor = self.db_connection.cursor()
            self._validate_table_name(self.tabla_usuarios)

            if exitoso:
                # Reset intentos fallidos si login exitoso
                query = self.sql_manager.get_query('usuarios', 'actualizar_acceso_exitoso')
                cursor.execute(query, (username_limpio.lower(),))
            else:
                # Incrementar intentos fallidos
                query = self.sql_manager.get_query('usuarios', 'incrementar_intentos_fallidos')
                cursor.execute(query, (username_limpio.lower(),))

            self.db_connection.commit()

        except Exception as e:
            logger.error(f"Error registrando intento login: {e}", exc_info=True)

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
                username_limpio = sanitize_string(username)
            else:
                username_limpio = username.strip()

            cursor = self.db_connection.cursor()
            self._validate_table_name(self.tabla_usuarios)

            # Verificar intentos fallidos y tiempo transcurrido
            query = self.sql_manager.get_query('usuarios', 'verificar_bloqueo_cuenta')

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
            logger.error(f"Error verificando cuenta bloqueada: {e}", exc_info=True)
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
                username_limpio = sanitize_string(username)
            else:
                username_limpio = username.strip()

            cursor = self.db_connection.cursor()
            self._validate_table_name(self.tabla_usuarios)

            query = self.sql_manager.get_query('usuarios', 'resetear_intentos_fallidos')
            cursor.execute(query, (username_limpio.lower(),))
            self.db_connection.commit()

            return cursor.rowcount > 0

        except Exception as e:
            logger.error(f"Error reseteando intentos login: {e}", exc_info=True)
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
        logger.info("Las tablas deben existir previamente en la base de datos")
        logger.info("Para crear las tablas, ejecutar: database/create_tables.sql")
        return

    def crear_usuarios_iniciales(self):
        """ELIMINADO: RIESGO DE SEGURIDAD CRÍTICO - No crear usuarios por defecto"""
        logger.error("SEGURIDAD CRÍTICA: No se crean usuarios automáticamente")
        logger.warning("Los usuarios deben ser creados manualmente por el administrador del sistema")
        logger.warning("Usar script create_admin_simple.py para crear usuario admin manualmente")
        return

    @cached_query(ttl=60)  # Cache por 1 minuto - consulta muy frecuente en autenticación
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

        # [LOCK] SANITIZACIÓN DE ENTRADA
        if self.security_available and self.data_sanitizer and nombre_usuario:
            # Sanitizar el nombre de usuario para prevenir inyecciones
            nombre_limpio = sanitize_string(nombre_usuario)
            if not nombre_limpio:
                return None
        else:
            nombre_limpio = nombre_usuario.strip() if nombre_usuario else ""

        try:
            cursor = self.db_connection.cursor()
            sql_select = self.sql_manager.get_query('usuarios', 'obtener_usuario_por_nombre')
            cursor.execute(sql_select, (nombre_limpio,))
            row = cursor.fetchone()
            logger.debug(f"obtener_usuario_por_nombre - Buscando usuario: {nombre_usuario}")
            logger.debug(f"obtener_usuario_por_nombre - Resultado row: {row}")
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
                logger.debug(f"obtener_usuario_por_nombre - Usuario dict: {usuario_dict}")
                return usuario_dict
            logger.debug("obtener_usuario_por_nombre - No se encontró el usuario")
            return None
        except Exception as e:
            logger.error(f"Error obteniendo usuario: {e}", exc_info=True)
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

        # [LOCK] SANITIZACIÓN DE ENTRADA
        if self.security_available and self.data_sanitizer and email:
            # Sanitizar el email para prevenir inyecciones
            email_limpio = sanitize_string(email)
            if not email_limpio:
                return None
        else:
            email_limpio = email.strip() if email else ""

        try:
            cursor = self.db_connection.cursor()
            sql_select = self.sql_manager.get_query('usuarios', 'obtener_usuario_por_email')
            cursor.execute(sql_select, (email_limpio,))
            row = cursor.fetchone()

            logger.debug(f"obtener_usuario_por_email - Buscando email: {email}")
            logger.debug(f"obtener_usuario_por_email - Resultado row: {row}")

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

                logger.debug(f"obtener_usuario_por_email - Usuario dict: {usuario_dict}")
                return usuario_dict

            logger.debug("obtener_usuario_por_email - No se encontró el usuario")
            return None

        except Exception as e:
            logger.error(f"Error obteniendo usuario por email: {e}", exc_info=True)
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

        # [LOCK] SANITIZACIÓN DE ENTRADA
        if self.security_available and self.data_sanitizer:
            username_limpio = sanitize_string(username)
            if not username_limpio:
                return True  # Si no se puede sanitizar, considerarlo como existente por seguridad
        else:
            username_limpio = username.strip() if username else ""

        try:
            cursor = self.db_connection.cursor()

            if excluir_usuario_id:
                sql_select = self.sql_manager.get_query('usuarios', 'count_username_duplicate_exclude')
                cursor.execute(sql_select, (username_limpio, excluir_usuario_id))
            else:
                sql_select = self.sql_manager.get_query('usuarios', 'count_username_duplicate')
                cursor.execute(sql_select, (username_limpio,))

            count = cursor.fetchone()[0]
            existe = count > 0

            logger.debug(f"verificar_unicidad_username - Username '{username}' existe: {existe}")
            return existe

        except Exception as e:
            logger.error(f"Error verificando unicidad de username: {e}", exc_info=True)
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

        # [LOCK] SANITIZACIÓN DE ENTRADA
        if self.security_available and self.data_sanitizer:
            email_limpio = sanitize_string(email)
            if not email_limpio:
                return True  # Si no se puede sanitizar, considerarlo como existente por seguridad
        else:
            email_limpio = email.strip() if email else ""

        try:
            cursor = self.db_connection.cursor()

            if excluir_usuario_id:
                sql_select = self.sql_manager.get_query('usuarios', 'count_email_duplicate_exclude')
                cursor.execute(sql_select, (email_limpio, excluir_usuario_id))
            else:
                sql_select = self.sql_manager.get_query('usuarios', 'count_email_duplicate')
                cursor.execute(sql_select, (email_limpio,))

            count = cursor.fetchone()[0]
            existe = count > 0

            logger.debug(f"verificar_unicidad_email - Email '{email}' existe: {existe}")
            return existe

        except Exception as e:
            logger.error(f"Error verificando unicidad de email: {e}", exc_info=True)
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

        # [LOCK] SANITIZACIÓN DE ENTRADA
        if self.security_available:
            username_limpio = sanitize_string(
                username, max_length=50
            )
            if not username_limpio:
                return True, 999  # Si no se puede sanitizar, bloquear por seguridad
        else:
            username_limpio = username

        try:
            cursor = self.db_connection.cursor()
            sql_select = self.sql_manager.get_query('usuarios', 'verificar_bloqueo_cuenta_detallado')
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
                except (ValueError, TypeError, AttributeError) as e:
                    # Si no se puede parsear, asumir que no está bloqueado
                    logger.warning(f"Error parseando fecha de bloqueo: {e}")
                    return False, 0

            ahora = datetime.now()
            if ahora >= bloqueado_hasta:
                # El bloqueo ha expirado, limpiar el bloqueo
                self._limpiar_bloqueo_usuario(username_limpio)
                return False, 0
            else:
                # Calcular tiempo restante en minutos
                tiempo_restante = int((bloqueado_hasta - ahora).total_seconds() / 60)
                log_security("WARNING", f"Usuario '{username}' bloqueado. Tiempo restante: {tiempo_restante} minutos", username)
                return True, tiempo_restante

        except Exception as e:
            logger.error(f"Error verificando bloqueo de usuario: {e}", exc_info=True)
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

        # [LOCK] SANITIZACIÓN DE ENTRADA
        if self.security_available:
            username_limpio = sanitize_string(
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
            cursor = self.db_connection.cursor()

            # Obtener intentos actuales
            sql_select = self.sql_manager.get_query('usuarios', 'obtener_intentos_fallidos')
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

                sql_update = self.sql_manager.get_query('usuarios', 'actualizar_bloqueo_usuario')
                cursor.execute(
                    sql_update,
(intentos_nuevos,
                        bloqueado_hasta,
                        username_limpio)
                )
                self.db_connection.commit()

                log_security("WARNING", f"Usuario '{username}' BLOQUEADO después de {intentos_nuevos} intentos fallidos", username)
                log_security("WARNING", f"Usuario bloqueado hasta: {bloqueado_hasta}")

                return True, intentos_nuevos, TIEMPO_BLOQUEO_MINUTOS
            else:
                # Solo incrementar contador
                sql_update = self.sql_manager.get_query('usuarios', 'actualizar_intentos_fallidos')
                cursor.execute(sql_update, (intentos_nuevos, username_limpio))
                self.db_connection.commit()

                log_security("WARNING", f"Intento fallido #{intentos_nuevos} para usuario '{username}'", username)

                return False, intentos_nuevos, 0

        except Exception as e:
            logger.error(f"Error incrementando intentos fallidos: {e}", exc_info=True)
            return True, 999, 999

    def limpiar_intentos_fallidos(self, username):
        """
        Limpia los intentos fallidos de un usuario después de un login exitoso.

        Args:
            username: Nombre de usuario
        """
        if not self.db_connection or not username:
            return

        # [LOCK] SANITIZACIÓN DE ENTRADA
        if self.security_available:
            username_limpio = sanitize_string(
                username, max_length=50
            )
            if not username_limpio:
                return
        else:
            username_limpio = username

        try:
            cursor = self.db_connection.cursor()
            sql_update = self.sql_manager.get_query('usuarios', 'limpiar_intentos_bloqueo')
            cursor.execute(sql_update, (username_limpio,))
            self.db_connection.commit()

            log_security("INFO", f"Intentos fallidos limpiados para usuario '{username}'", username)

        except Exception as e:
            logger.error(f"Error limpiando intentos fallidos: {e}", exc_info=True)

    def _limpiar_bloqueo_usuario(self, username):
        """
        Método interno para limpiar el bloqueo de un usuario cuando ha expirado.

        Args:
            username: Nombre de usuario (ya sanitizado)
        """
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.cursor()
            sql_update = self.sql_manager.get_query('usuarios', 'limpiar_intentos_bloqueo')
            cursor.execute(sql_update, (username,))
            self.db_connection.commit()

            log_security("INFO", f"Bloqueo expirado limpiado para usuario '{username}'", username)

        except Exception as e:
            logger.error(f"Error limpiando bloqueo expirado: {e}", exc_info=True)

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

    def autenticar_usuario_seguro(self,
username: str,
        password: str) -> Dict[str,
        Any]:
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
            logger.error(f"Error en autenticación segura: {e}", exc_info=True)
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
            # [LOCK] SANITIZACIÓN Y VALIDACIÓN DE DATOS
            if unified_sanitizer:
                # Usar sanitizador unificado refactorizado
                datos_limpios = unified_sanitizer.sanitize_dict(datos_usuario)
            elif self.security_available and self.data_sanitizer:
                # Fallback a sanitizador legacy
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
                        email_limpio = sanitize_string(
                            datos_limpios["email"]
                        )
                        if (
                            not email_limpio
                            or len(email_limpio) < 5
                            or "@" not in email_limpio
                        ):
                            return False, "Formato de email inválido"
                        datos_limpios["email"] = email_limpio
                    except (ValueError, AttributeError, TypeError) as e:
                        logger.warning(f"Error validando email: {e}")
                        return False, "Formato de email inválido"

                # Validar teléfono si se proporciona
                if datos_limpios.get("telefono"):
                    telefono_limpio = sanitize_string(
                        datos_limpios["telefono"]
                    )
                    datos_limpios["telefono"] = telefono_limpio

            else:
                # Sin utilidades de seguridad, usar datos originales con precaución
                datos_limpios = datos_usuario.copy()
                logger.warning("Creando usuario sin sanitización de seguridad")

            cursor = self.db_connection.cursor()

            # Verificar que el usuario no exista
            sql_count_usuario = self.sql_manager.get_query('usuarios', 'count_usuario_by_name')
            cursor.execute(sql_count_usuario, (datos_limpios["usuario"],))
            if cursor.fetchone()[0] > 0:
                return False, f"El usuario '{datos_limpios['usuario']}' ya existe"

            # Verificar que el email no exista
            if datos_limpios.get("email"):
                sql_count_email = self.sql_manager.get_query('usuarios', 'count_email_duplicate')
                cursor.execute(sql_count_email, (datos_limpios["email"],))
                if cursor.fetchone()[0] > 0:
                    return (
                        False,
                        f"El email '{datos_limpios['email']}' ya está registrado",
                    )

            # Hashear la contraseña
            password_hash = self._hashear_password(datos_limpios["password"])

            # Insertar usuario con datos sanitizados
            sql_insertar = self.sql_manager.get_query('usuarios', 'insertar_usuario')
            cursor.execute(
                sql_insertar,
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
            sql_ultimo_id = self.sql_manager.get_query('usuarios', 'obtener_ultimo_id')
            cursor.execute(sql_ultimo_id)
            usuario_id = cursor.fetchone()[0]

            # Asignar permisos por defecto
            permisos_defecto = datos_usuario.get("permisos", ["Configuración"])
            for modulo in permisos_defecto:
                sql_permiso = self.sql_manager.get_query('usuarios', 'insertar_permiso')
                cursor.execute(
                    sql_permiso,
                    (usuario_id, modulo, "leer"),
                )

            self.db_connection.commit()
            # Invalidar cache después de crear usuario
            self._invalidar_cache_usuarios()

            logger.info(f"Usuario '{datos_usuario['usuario']}' creado exitosamente")
            return True, f"Usuario '{datos_usuario['usuario']}' creado exitosamente"

        except Exception as e:
            logger.error(f"Error creando usuario: {e}", exc_info=True)
            if self.db_connection:
                self.db_connection.connection.rollback()
            return False, f"Error creando usuario: {str(e)}"

    @cached_query(ttl=120)  # Cache por 2 minutos - listado completo de usuarios
    def obtener_todos_usuarios(self) -> List[Dict[str, Any]]:
        """Obtiene todos los usuarios del sistema con permisos optimizados (sin consultas N+1)."""
        if not self.db_connection:
            return self._get_usuarios_demo()

        try:
            cursor = self.db_connection.cursor()

            # Query optimizada con JOIN para eliminar consultas N+1
            sql = self.sql_manager.get_query('usuarios', 'obtener_usuarios_con_permisos')
            cursor.execute(sql)

            # Procesar resultados agrupando permisos por usuario
            usuarios_dict = {}

            for row in cursor.fetchall():
                user_id = row[0]

                if user_id not in usuarios_dict:
                    # Primera vez que vemos este usuario
                    usuarios_dict[user_id] = {
                        "id": row[0],
                        "usuario": row[1],
                        "nombre_completo": row[2],
                        "email": row[3],
                        "telefono": row[4],
                        "rol": row[5],
                        "estado": row[6],
                        "fecha_creacion": row[7],
                        "ultimo_acceso": row[8],
                        "intentos_fallidos": row[9],
                        "permisos": []
                    }

                    # Agregar textos descriptivos
                    usuarios_dict[user_id]["rol_texto"] = self.ROLES.get(row[5], row[5])
                    usuarios_dict[user_id]["estado_texto"] = self.ESTADOS.get(row[6], row[6])

                # Agregar permiso si existe
                if row[10]:  # permiso no es NULL
                    usuarios_dict[user_id]["permisos"].append(row[10])

            # Convertir dict a lista manteniendo orden
            usuarios = list(usuarios_dict.values())
            return usuarios

        except Exception as e:
            logger.error(f"Error obteniendo usuarios optimizado: {e}", exc_info=True)
            return self._get_usuarios_demo()

    def buscar_usuarios(self, termino_busqueda: str) -> List[Dict[str, Any]]:
        """
        Busca usuarios por nombre, username o email.

        Args:
            termino_busqueda: Término de búsqueda

        Returns:
            Lista de usuarios que coinciden con la búsqueda
        """
        if not self.db_connection:
            # Si no hay conexión, buscar en datos demo
            usuarios_demo = self._get_usuarios_demo()
            termino_lower = termino_busqueda.lower()
            return [
                usuario for usuario in usuarios_demo
                if (termino_lower in usuario.get("nombre_completo", "").lower() or
                    termino_lower in usuario.get("usuario", "").lower() or
                    termino_lower in usuario.get("email", "").lower())
            ]

        try:
            cursor = self.db_connection.cursor()

            # Sanitizar término de búsqueda antes de usarlo
            termino_limpio = termino_busqueda.strip()[:50]  # Limitar longitud
            termino_parametrizado = f'%{termino_limpio.lower()}%'

            # Query optimizada con JOIN para eliminar consultas N+1 en búsqueda
            sql = self.sql_manager.get_query('usuarios', 'buscar_usuarios_con_permisos')
            cursor.execute(sql, (termino_parametrizado, termino_parametrizado, termino_parametrizado))

            # Procesar resultados agrupando permisos por usuario
            usuarios_dict = {}

            for row in cursor.fetchall():
                user_id = row[0]

                if user_id not in usuarios_dict:
                    # Primera vez que vemos este usuario
                    usuarios_dict[user_id] = {
                        "id": row[0],
                        "usuario": row[1],
                        "nombre_completo": row[2],
                        "email": row[3],
                        "telefono": row[4],
                        "rol": row[5],
                        "estado": row[6],
                        "fecha_creacion": row[7],
                        "ultimo_acceso": row[8],
                        "intentos_fallidos": row[9],
                        "permisos": []
                    }

                    # Agregar textos descriptivos
                    usuarios_dict[user_id]["rol_texto"] = self.ROLES.get(row[5], row[5])
                    usuarios_dict[user_id]["estado_texto"] = self.ESTADOS.get(row[6], row[6])

                # Agregar permiso si existe
                if row[10]:  # permiso no es NULL
                    usuarios_dict[user_id]["permisos"].append(row[10])

            # Convertir dict a lista manteniendo orden
            usuarios = list(usuarios_dict.values())
            return usuarios

        except Exception as e:
            logger.error(f"Error buscando usuarios optimizado: {e}", exc_info=True)
            return []

    def obtener_usuario_por_id(self, usuario_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un usuario por su ID."""
        if not self.db_connection:
            return None

        try:
            cursor = self.db_connection.cursor()
            sql_query = self.sql_manager.get_query('usuarios', 'obtener_usuario_por_id')
            cursor.execute(sql_query, (usuario_id,))

            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                usuario = dict(zip(columns, row))
                usuario["permisos"] = self.obtener_permisos_usuario(usuario_id)
                return usuario

            return None

        except Exception as e:
            logger.error(f"Error obteniendo usuario por ID: {e}", exc_info=True)
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
            cursor = self.db_connection.cursor()

            # Verificar que el usuario exista
            sql_count_id = self.sql_manager.get_query('usuarios', 'count_usuario_by_id')
            cursor.execute(sql_count_id, (usuario_id,))
            if cursor.fetchone()[0] == 0:
                return False, "Usuario no encontrado"

            # Actualizar datos básicos usando SQLQueryManager
            sql_update = self.sql_manager.get_query('usuarios', 'actualizar_datos_usuario')
            cursor.execute(sql_update, (
                datos_usuario["nombre_completo"],
                datos_usuario.get("email", ""),
                datos_usuario.get("telefono", ""),
                datos_usuario.get("rol", "USUARIO"),
                datos_usuario.get("estado", "ACTIVO"),
                usuario_id,
            ))

            # Actualizar contraseña si se proporciona
            if datos_usuario.get("password"):
                password_hash = self._hashear_password(datos_usuario["password"])
                sql_password = self.sql_manager.get_query('usuarios', 'actualizar_password_usuario')
                cursor.execute(sql_password, (password_hash, usuario_id))

            # Actualizar permisos
            if "permisos" in datos_usuario:
                cursor.execute(self.sql_manager.get_query("usuarios", "delete_usuarios_1"), params)

                for modulo in datos_usuario["permisos"]:
                    sql_permiso = self.sql_manager.get_query('usuarios', 'insertar_permiso')
                    cursor.execute(
                        sql_permiso,
                        (usuario_id, modulo, "leer,escribir"),
                    )

            self.db_connection.commit()
            return True, "Usuario actualizado exitosamente"

        except Exception as e:
            logger.error(f"Error actualizando usuario: {e}", exc_info=True)
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
            cursor = self.db_connection.cursor()

            # Verificar que el usuario exista
            sql_get_usuario = self.sql_manager.get_query('usuarios', 'obtener_usuario_by_id')
            cursor.execute(sql_get_usuario, (usuario_id,))
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

            # Cerrar sesiones activas usando SQLQueryManager
            sql_cerrar_sesiones = self.sql_manager.get_query('usuarios', 'cerrar_sesiones_usuario')
            cursor.execute(sql_cerrar_sesiones, (usuario_id,))

            self.db_connection.commit()
            return True, f"Usuario '{nombre_usuario}' eliminado exitosamente"

        except Exception as e:
            logger.error(f"Error eliminando usuario: {e}", exc_info=True)
            if self.db_connection:
                self.db_connection.connection.rollback()
            return False, f"Error eliminando usuario: {str(e)}"

    @cached_query(ttl=300)  # Cache por 5 minutos - permisos cambian poco frecuentemente
    def obtener_permisos_usuario(self, usuario_id: int) -> List[str]:
        """Obtiene los permisos de un usuario."""
        if not self.db_connection:
            return ["Configuración"]

        try:
            cursor = self.db_connection.cursor()
            sql_permisos = self.sql_manager.get_query('usuarios', 'obtener_permisos_usuario')
            cursor.execute(sql_permisos, (usuario_id,))

            return [row[0] for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"Error obteniendo permisos: {e}", exc_info=True)
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
            cursor = self.db_connection.cursor()

            # Verificar contraseña actual
            sql_get_password = self.sql_manager.get_query('usuarios', 'obtener_password_hash')
            cursor.execute(sql_get_password, (usuario_id,))
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

            self.db_connection.commit()
            return True, "Contraseña cambiada exitosamente"

        except Exception as e:
            logger.error(f"Error cambiando contraseña: {e}", exc_info=True)
            if self.db_connection:
                self.db_connection.connection.rollback()
            return False, f"Error cambiando contraseña: {str(e)}"

    def obtener_estadisticas_usuarios(self) -> Dict[str, Any]:
        """Obtiene estadísticas de usuarios."""
        if not self.db_connection:
            return self._get_estadisticas_demo()

        try:
            cursor = self.db_connection.cursor()

            stats = {}

            # Total de usuarios
            sql_count_activos = self.sql_manager.get_query('usuarios', 'count_usuarios_activos')
            cursor.execute(sql_count_activos)
            stats["total_usuarios"] = cursor.fetchone()[0]

            # Usuarios por estado usando SQLQueryManager
            sql_estado = self.sql_manager.get_query('usuarios', 'estadisticas_por_estado')
            cursor.execute(sql_estado)
            stats["por_estado"] = {row[0]: row[1] for row in cursor.fetchall()}

            # Usuarios por rol usando SQLQueryManager
            sql_rol = self.sql_manager.get_query('usuarios', 'estadisticas_por_rol')
            cursor.execute(sql_rol)
            stats["por_rol"] = {row[0]: row[1] for row in cursor.fetchall()}

            # Usuarios activos en el último mes usando SQLQueryManager
            sql_activos_mes = self.sql_manager.get_query('usuarios', 'usuarios_activos_ultimo_mes')
            cursor.execute(sql_activos_mes)
            stats["activos_mes"] = cursor.fetchone()[0]

            # Usuarios creados este mes usando SQLQueryManager
            sql_creados_mes = self.sql_manager.get_query('usuarios', 'usuarios_creados_este_mes')
            cursor.execute(sql_creados_mes)
            stats["creados_mes"] = cursor.fetchone()[0]

            return stats

        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}", exc_info=True)
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
            logger.error(f"Error obteniendo datos paginados: {e}")
            return [], 0

    def obtener_total_registros(self, filtros=None):
        """Obtiene el total de registros disponibles"""
        try:
            _, total = self.obtener_datos_paginados(offset=0,
                                                   limit=1,
                                                   filtros=filtros)
            return total
        except Exception as e:
            logger.error(f"Error obteniendo total de registros: {e}")
            return 0

    def _get_base_query(self):
        """Obtiene la query base para paginación usando SQL externo."""
        # White-list de tablas permitidas para paginación
        tabla_queries = {
            'usuarios': 'get_base_query_usuarios',
            'roles': 'get_base_query_roles',
            'permisos_usuario': 'get_base_query_permisos'
        }

        tabla_principal = getattr(self, "tabla_principal", "usuarios")
        if tabla_principal in tabla_queries:
            return self.sql_manager.get_query('usuarios', tabla_queries[tabla_principal])
        else:
            # Fallback seguro para tabla por defecto
            return self.sql_manager.get_query('usuarios', 'get_base_query_usuarios')

    def _get_count_query(self):
        """Obtiene la query de conteo usando SQL externo."""
        # White-list de tablas permitidas para conteo
        tabla_queries = {
            'usuarios': 'get_count_query_usuarios',
            'roles': 'get_count_query_roles',
            'permisos_usuario': 'get_count_query_permisos'
        }

        tabla_principal = getattr(self, "tabla_principal", "usuarios")
        if tabla_principal in tabla_queries:
            return self.sql_manager.get_query('usuarios', tabla_queries[tabla_principal])
        else:
            # Fallback seguro para tabla por defecto
            return self.sql_manager.get_query('usuarios', 'get_count_query_usuarios')

    def _row_to_dict(self, row, description):
        """Convierte una fila de base de datos a diccionario"""
        return {desc[0]: row[i] for i, desc in enumerate(description)}

    # === MÉTODOS DE GESTORES ESPECIALIZADOS ===

    def crear_sesion(self, usuario_id: int, username: str, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> Dict[str, Any]:
        """Crea una nueva sesión para un usuario."""
        if self.sessions_manager:
            return self.sessions_manager.crear_sesion(usuario_id,
username,
                ip_address,
                user_agent)
        return {'success': False, 'message': 'Gestor de sesiones no disponible'}

    def validar_sesion(self, session_id: str) -> Dict[str, Any]:
        """Valida si una sesión es válida."""
        if self.sessions_manager:
            return self.sessions_manager.validar_sesion(session_id)
        return {'valid': False, 'message': 'Gestor de sesiones no disponible'}

    def cerrar_sesion(self, session_id: str) -> Dict[str, Any]:
        """Cierra una sesión específica."""
        if self.sessions_manager:
            return self.sessions_manager.cerrar_sesion(session_id)
        return {'success': False, 'message': 'Gestor de sesiones no disponible'}

    def verificar_permiso_usuario(self,
usuario_id: int,
        modulo: str,
        accion: str) -> bool:
        """Verifica si un usuario tiene un permiso específico."""
        if self.permissions_manager:
            return self.permissions_manager.verificar_permiso_usuario(usuario_id, modulo, accion)
        return False

    def asignar_permiso_usuario(self,
usuario_id: int,
        modulo: str,
        accion: str) -> Dict[str,
        Any]:
        """Asigna un permiso específico a un usuario."""
        if self.permissions_manager:
            return self.permissions_manager.asignar_permiso_usuario(usuario_id, modulo, accion)
        return {'success': False, 'message': 'Gestor de permisos no disponible'}

    def cambiar_rol_usuario(self,
usuario_id: int,
        nuevo_rol: str) -> Dict[str,
        Any]:
        """Cambia el rol de un usuario."""
        if self.permissions_manager:
            return self.permissions_manager.cambiar_rol_usuario(usuario_id, nuevo_rol)
        return {'success': False, 'message': 'Gestor de permisos no disponible'}

    def obtener_todos_usuarios_con_gestores(self, incluir_inactivos: bool = False) -> List[Dict[str, Any]]:
        """Obtiene todos los usuarios usando el ProfilesManager."""
        if self.profiles_manager:
            return self.profiles_manager.obtener_todos_usuarios(incluir_inactivos)
        return self.obtener_todos_usuarios()

    def actualizar_usuario_con_gestores(self,
usuario_id: int,
        datos_actualizados: Dict[str,
        Any]) -> Dict[str,
        Any]:
        """Actualiza un usuario usando el ProfilesManager."""
        if self.profiles_manager:
            return self.profiles_manager.actualizar_usuario(usuario_id, datos_actualizados)
        success, message = self.actualizar_usuario(usuario_id, datos_actualizados)
        return {'success': success, 'message': message}

    def validar_fortaleza_password_segura(self, password: str) -> Dict[str, Any]:
        """Valida la fortaleza de una contraseña usando el AuthenticationManager."""
        if self.auth_manager:
            return self.auth_manager.validar_fortaleza_password(password)
        return self.validar_fortaleza_password(password)

    def obtener_estadisticas_completas(self) -> Dict[str, Any]:
        """Obtiene estadísticas completas del sistema de usuarios."""
        estadisticas = self.obtener_estadisticas_usuarios()

        # Agregar estadísticas de gestores especializados
        if self.sessions_manager:
            estadisticas['sesiones'] = self.sessions_manager.obtener_estadisticas_sesiones()

        if self.permissions_manager:
            estadisticas['permisos'] = self.permissions_manager.obtener_estadisticas_permisos()

        return estadisticas

    def _invalidar_cache_usuarios(self) -> None:
        """
        Invalida el cache de usuarios después de cambios.
        """
        try:
            # Invalidar cache de listados de usuarios
            invalidate_cache('obtener_todos_usuarios')
            invalidate_cache('obtener_usuario_por_nombre')
            invalidate_cache('obtener_permisos_usuario')
            logger.info("Cache invalidado después de cambios")
        except Exception as e:
            logger.warning(f"Error invalidando cache: {e}")

    def obtener_usuarios_con_permisos(self) -> Optional[List[Dict]]:
        """
        Obtiene todos los usuarios activos con sus permisos.
        
        Returns:
            Lista de usuarios con permisos o None en caso de error
        """
        try:
            if not self.db_connection:
                logger.warning("No hay conexión a BD - retornando datos demo")
                return self._get_usuarios_demo()
            
            return self.sql_manager.ejecutar_consulta_archivo(
                'sql/usuarios/obtener_usuarios_con_permisos.sql'
            )
            
        except Exception as e:
            logger.error(f"Error obteniendo usuarios con permisos: {e}")
            return None

    def obtener_usuarios_filtrados(self, filtros: Dict[str, Any]) -> Optional[List[Dict]]:
        """
        Obtiene usuarios aplicando filtros específicos.
        
        Args:
            filtros: Diccionario con filtros a aplicar
            
        Returns:
            Lista de usuarios filtrados o None en caso de error
        """
        try:
            logger.info(f"Aplicando filtros: {filtros}")
            
            if not self.db_connection:
                logger.error("No hay conexión a la base de datos")
                return []
            
            cursor = self.db_connection.cursor()
            
            # Query base
            query = """
                SELECT 
                    u.id, u.username, u.email, u.nombre_completo, u.departamento,
                    u.cargo, u.telefono, u.activo, u.fecha_creacion, u.ultimo_acceso,
                    ur.role_name as rol, u.estado
                FROM usuarios u
                LEFT JOIN user_roles ur ON u.id = ur.user_id
                WHERE 1=1
            """
            
            params = []
            
            # Aplicar filtros dinámicamente
            if filtros.get('busqueda'):
                query += """
                    AND (u.username LIKE ? OR u.email LIKE ? OR u.nombre_completo LIKE ? 
                         OR u.departamento LIKE ? OR u.cargo LIKE ?)
                """
                busqueda = f"%{filtros['busqueda']}%"
                params.extend([busqueda, busqueda, busqueda, busqueda, busqueda])
            
            if filtros.get('rol') and filtros['rol'] != 'Todos':
                query += " AND ur.role_name = ?"
                params.append(filtros['rol'])
            
            if filtros.get('estado') and filtros['estado'] != 'Todos':
                if filtros['estado'] == 'Activo':
                    query += " AND u.activo = 1"
                elif filtros['estado'] == 'Inactivo':
                    query += " AND u.activo = 0"
                elif filtros['estado'] in ['Suspendido', 'Bloqueado']:
                    query += " AND u.estado = ?"
                    params.append(filtros['estado'])
            
            if filtros.get('departamento') and filtros['departamento'] != 'Todos':
                query += " AND u.departamento = ?"
                params.append(filtros['departamento'])
            
            # Ordenar por fecha de creación descendente
            query += " ORDER BY u.fecha_creacion DESC"
            
            logger.debug(f"Ejecutando query con {len(params)} parámetros")
            cursor.execute(query, params)
            
            # Convertir resultados a diccionarios
            usuarios = []
            columns = [desc[0] for desc in cursor.description]
            
            for row in cursor.fetchall():
                usuario = dict(zip(columns, row))
                # Sanitizar datos de salida
                if data_sanitizer:
                    usuario = data_sanitizer.sanitize_dict(usuario)
                usuarios.append(usuario)
            
            logger.info(f"Filtrados {len(usuarios)} usuarios exitosamente")
            return usuarios
            
        except Exception as e:
            logger.error(f"Error filtrando usuarios: {e}", exc_info=True)
            return None
