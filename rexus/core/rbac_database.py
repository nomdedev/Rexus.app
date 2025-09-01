"""
Sistema RBAC en Base de Datos - Rexus.app

Sistema completo de control de acceso basado en roles que utiliza la base de datos
para gestionar usuarios, roles, permisos y políticas de acceso de manera granular.

Este sistema permite:
- Gestión jerárquica de roles
- Permisos granulares por recurso y acción
- Políticas de acceso dinámicas
- Auditoría completa de accesos
- Herencia de permisos entre roles

Author: Rexus Development Team
Date: 2025-08-11
Version: 1.0.0
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum

try:
    from rexus.utils.secure_logger import log_security_event
except ImportError:
    def log_security_event(event_type, details, severity="INFO"):
        print(f"SECURITY LOG [{severity}] {event_type}: {details}")


class PermissionAction(Enum):
    """Acciones disponibles para permisos."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    MANAGE = "manage"
    ADMIN = "admin"


class AccessResult(Enum):
    """Resultado de verificación de acceso."""
    GRANTED = "granted"
    DENIED = "denied"
    CONDITIONAL = "conditional"


@dataclass
class Role:
    """Clase que representa un rol del sistema."""
    id: int
    name: str
    description: str
    parent_id: Optional[int] = None
    is_active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class Permission:
    """Clase que representa un permiso específico."""
    id: int
    resource: str
    action: str
    description: str
    is_active: bool = True
    created_at: Optional[str] = None


@dataclass
class Policy:
    """Clase que representa una política de acceso."""
    id: int
    name: str
    resource_pattern: str
    conditions: Dict[str, Any]
    effect: str  # ALLOW, DENY
    priority: int = 0
    is_active: bool = True


@dataclass
class AccessAttempt:
    """Clase que representa un intento de acceso."""
    user_id: int
    resource: str
    action: str
    result: AccessResult
    timestamp: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class RBACDatabase:
    """
    Sistema de control de acceso basado en roles con respaldo en base de datos.

    Proporciona funcionalidad completa de RBAC incluyendo gestión de usuarios,
    roles, permisos, políticas y auditoría de accesos.
    """

    def __init__(self, db_path: str = "rbac.db"):
        """
        Inicializa el sistema RBAC con base de datos.

        Args:
            db_path: Ruta al archivo de base de datos SQLite
        """
        self.db_path = db_path
        self.permission_cache = {}
        self.cache_timeout = timedelta(minutes=15)
        self.last_cache_update = datetime.min

        # Inicializar base de datos
        self._initialize_database()
        self._create_default_roles()

        log_security_event(
            "RBAC_SYSTEM_INITIALIZED",
            {"database_path": db_path},
            "INFO"
        )

    @contextmanager
    def _get_db_connection(self):
        """Context manager para conexiones de base de datos."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _initialize_database(self):
        """Inicializa las tablas necesarias para RBAC."""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()

            # Tabla de roles
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rbac_roles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    description TEXT,
                    parent_id INTEGER,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (parent_id) REFERENCES rbac_roles (id)
                )
            """)

            # Tabla de permisos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rbac_permissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    resource TEXT NOT NULL,
                    action TEXT NOT NULL,
                    description TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(resource, action)
                )
            """)

            # Tabla de asignación de roles a usuarios
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rbac_user_roles (
                    user_id INTEGER NOT NULL,
                    role_id INTEGER NOT NULL,
                    granted_by INTEGER,
                    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    PRIMARY KEY (user_id, role_id),
                    FOREIGN KEY (role_id) REFERENCES rbac_roles (id),
                    FOREIGN KEY (granted_by) REFERENCES usuarios (id)
                )
            """)

            # Tabla de asignación de permisos a roles
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rbac_role_permissions (
                    role_id INTEGER NOT NULL,
                    permission_id INTEGER NOT NULL,
                    granted_by INTEGER,
                    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1,
                    PRIMARY KEY (role_id, permission_id),
                    FOREIGN KEY (role_id) REFERENCES rbac_roles (id),
                    FOREIGN KEY (permission_id) REFERENCES rbac_permissions (id),
                    FOREIGN KEY (granted_by) REFERENCES usuarios (id)
                )
            """)

            # Tabla de políticas de acceso
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rbac_policies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    resource_pattern TEXT NOT NULL,
                    conditions TEXT, -- JSON
                    effect TEXT NOT NULL CHECK (effect IN ('ALLOW', 'DENY')),
                    priority INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by INTEGER,
                    FOREIGN KEY (created_by) REFERENCES usuarios (id)
                )
            """)

            # Tabla de auditoría de accesos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rbac_access_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    resource TEXT NOT NULL,
                    action TEXT NOT NULL,
                    result TEXT NOT NULL CHECK (result IN ('GRANTED', 'DENIED', 'CONDITIONAL')),
                    ip_address TEXT,
                    user_agent TEXT,
                    details TEXT, -- JSON
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES usuarios (id)
                )
            """)

            # Índices para optimización
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_roles ON rbac_user_roles (user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_role_permissions ON rbac_role_permissions (role_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_access_log_user ON rbac_access_log (user_id, timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_access_log_resource ON rbac_access_log (resource, timestamp)")

            conn.commit()

    def _create_default_roles(self):
        """Crea roles por defecto del sistema."""
        default_roles = [
            ("super_admin", "Administrador del sistema con acceso completo", None),
            ("admin", "Administrador con permisos de gestión", 1),
            ("manager", "Gestor con permisos limitados", 2),
            ("user", "Usuario estándar con permisos básicos", 3),
            ("viewer", "Solo lectura sin modificaciones", 4)
        ]

        with self._get_db_connection() as conn:
            cursor = conn.cursor()

            for name, description, parent_id in default_roles:
                cursor.execute(
                    "INSERT OR IGNORE INTO rbac_roles (name, description, parent_id) VALUES (?, ?, ?)",
                    (name, description, parent_id)
                )

            conn.commit()

        # Crear permisos por defecto
        self._create_default_permissions()

    def _create_default_permissions(self):
        """Crea permisos por defecto para recursos del sistema."""
        default_permissions = [
            ("system", "admin", "Administración completa del sistema"),
            ("users", "create", "Crear nuevos usuarios"),
            ("users", "read", "Ver información de usuarios"),
            ("users", "update", "Actualizar información de usuarios"),
            ("users", "delete", "Eliminar usuarios"),
            ("roles", "manage", "Gestionar roles y permisos"),
            ("inventario", "create", "Crear productos en inventario"),
            ("inventario", "read", "Ver inventario"),
            ("inventario", "update", "Actualizar inventario"),
            ("inventario", "delete", "Eliminar productos del inventario"),
            ("obras", "create", "Crear nuevas obras"),
            ("obras", "read", "Ver obras"),
            ("obras", "update", "Actualizar obras"),
            ("obras", "delete", "Eliminar obras"),
            ("compras", "create", "Crear compras"),
            ("compras", "read", "Ver compras"),
            ("compras", "update", "Actualizar compras"),
            ("pedidos", "create", "Crear pedidos"),
            ("pedidos", "read", "Ver pedidos"),
            ("pedidos", "update", "Actualizar pedidos"),
            ("reports", "read", "Ver reportes"),
            ("reports", "generate", "Generar reportes"),
            ("audit", "read", "Ver logs de auditoría")
        ]

        with self._get_db_connection() as conn:
            cursor = conn.cursor()

            for resource, action, description in default_permissions:
                cursor.execute(
                    "INSERT OR IGNORE INTO rbac_permissions (resource, action, description) VALUES (?, ?, ?)",
                    (resource, action, description)
                )

            conn.commit()

    def create_role(self,
name: str,
        description: str,
        parent_id: Optional[int] = None) -> int:
        """
        Crea un nuevo rol en el sistema.

        Args:
            name: Nombre único del rol
            description: Descripción del rol
            parent_id: ID del rol padre para herencia

        Returns:
            ID del rol creado
        """
        with self._get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO rbac_roles (name, description, parent_id) VALUES (?, ?, ?)",
                (name, description, parent_id)
            )

            role_id = cursor.lastrowid
            conn.commit()

            log_security_event(
                "ROLE_CREATED",
                {"role_id": role_id, "name": name, "parent_id": parent_id},
                "INFO"
            )

            return role_id

    def create_permission(self,
resource: str,
        action: str,
        description: str = "") -> int:
        """
        Crea un nuevo permiso en el sistema.

        Args:
            resource: Recurso al que aplica el permiso
            action: Acción permitida sobre el recurso
            description: Descripción del permiso

        Returns:
            ID del permiso creado
        """
        with self._get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO rbac_permissions (resource, action, description) VALUES (?, ?, ?)",
                (resource, action, description)
            )

            permission_id = cursor.lastrowid
            conn.commit()

            log_security_event(
                "PERMISSION_CREATED",
                {"permission_id": permission_id, "resource": resource, "action": action},
                "INFO"
            )

            return permission_id

    def assign_role_to_user(self, user_id: int, role_id: int, granted_by: int,
                           expires_at: Optional[str] = None) -> bool:
        """
        Asigna un rol a un usuario.

        Args:
            user_id: ID del usuario
            role_id: ID del rol a asignar
            granted_by: ID del usuario que otorga el rol
            expires_at: Fecha de expiración opcional

        Returns:
            True si se asignó correctamente
        """
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """INSERT OR REPLACE INTO rbac_user_roles
                       (user_id, role_id, granted_by, expires_at)
                       VALUES (?, ?, ?, ?)""",
                    (user_id, role_id, granted_by, expires_at)
                )

                conn.commit()

                log_security_event(
                    "ROLE_ASSIGNED",
                    {"user_id": user_id, "role_id": role_id, "granted_by": granted_by},
                    "INFO"
                )

                # Limpiar caché para este usuario
                self._clear_user_cache(user_id)

                return True

        except Exception as e:
            log_security_event(
                "ROLE_ASSIGNMENT_FAILED",
                {"user_id": user_id, "role_id": role_id, "error": str(e)},
                "ERROR"
            )
            return False

    def assign_permission_to_role(self,
role_id: int,
        permission_id: int,
        granted_by: int) -> bool:
        """
        Asigna un permiso a un rol.

        Args:
            role_id: ID del rol
            permission_id: ID del permiso
            granted_by: ID del usuario que otorga el permiso

        Returns:
            True si se asignó correctamente
        """
        try:
            with self._get_db_connection() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    """INSERT OR REPLACE INTO rbac_role_permissions
                       (role_id, permission_id, granted_by)
                       VALUES (?, ?, ?)""",
                    (role_id, permission_id, granted_by)
                )

                conn.commit()

                log_security_event(
                    "PERMISSION_ASSIGNED",
                    {"role_id": role_id, "permission_id": permission_id, "granted_by": granted_by},
                    "INFO"
                )

                # Limpiar caché relacionado
                self._clear_role_cache(role_id)

                return True

        except Exception as e:
            log_security_event(
                "PERMISSION_ASSIGNMENT_FAILED",
                {"role_id": role_id, "permission_id": permission_id, "error": str(e)},
                "ERROR"
            )
            return False

    def check_access(self, user_id: int, resource: str, action: str,
                    context: Optional[Dict[str, Any]] = None) -> Tuple[AccessResult, str]:
        """
        Verifica si un usuario tiene acceso a un recurso y acción específicos.

        Args:
            user_id: ID del usuario
            resource: Recurso solicitado
            action: Acción solicitada
            context: Contexto adicional para verificación

        Returns:
            Tupla con resultado del acceso y mensaje explicativo
        """
        try:
            # 1. Verificar permisos directos y heredados
            has_permission = self._check_user_permissions(user_id, resource, action)

            # 2. Verificar políticas de acceso
            policy_result = self._check_access_policies(user_id,
resource,
                action,
                context)

            # 3. Determinar resultado final
            if policy_result == AccessResult.DENIED:
                result = AccessResult.DENIED
                message = "Acceso denegado por política del sistema"
            elif has_permission:
                result = AccessResult.GRANTED
                message = "Acceso concedido"
            else:
                result = AccessResult.DENIED
                message = "Usuario no tiene permisos suficientes"

            # 4. Registrar intento de acceso
            self._log_access_attempt(user_id,
resource,
                action,
                result,
                context)

            return result, message

        except Exception as e:
            log_security_event(
                "ACCESS_CHECK_ERROR",
                {"user_id": user_id,
"resource": resource,
                    "action": action,
                    "error": str(e)},
                "ERROR"
            )

            return AccessResult.DENIED, "Error interno del sistema"

    def _check_user_permissions(self,
user_id: int,
        resource: str,
        action: str) -> bool:
        """Verifica si el usuario tiene permisos directos o heredados."""
        # Verificar caché
        cache_key = f"{user_id}:{resource}:{action}"
        if self._is_cache_valid() and cache_key in self.permission_cache:
            return self.permission_cache[cache_key]

        with self._get_db_connection() as conn:
            cursor = conn.cursor()

            # Query compleja que incluye herencia de roles
            cursor.execute("""
                WITH RECURSIVE role_hierarchy AS (
                    -- Roles directos del usuario
                    SELECT r.id, r.name, r.parent_id, 0 as level
                    FROM rbac_roles r
                    JOIN rbac_user_roles ur ON r.id = ur.role_id
                    WHERE ur.user_id = ?
                      AND ur.is_active = 1
                      AND (ur.expires_at IS NULL OR ur.expires_at > datetime('now'))
                      AND r.is_active = 1

                    UNION ALL

                    -- Roles heredados
                    SELECT r.id, r.name, r.parent_id, rh.level + 1
                    FROM rbac_roles r
                    JOIN role_hierarchy rh ON r.id = rh.parent_id
                    WHERE r.is_active = 1
                )
                SELECT DISTINCT p.resource, p.action
                FROM rbac_permissions p
                JOIN rbac_role_permissions rp ON p.id = rp.permission_id
                JOIN role_hierarchy rh ON rp.role_id = rh.id
                WHERE p.resource = ? AND p.action = ?
                  AND p.is_active = 1 AND rp.is_active = 1
            """, (user_id, resource, action))

            result = cursor.fetchone() is not None

            # Actualizar caché
            self.permission_cache[cache_key] = result

            return result

    def _check_access_policies(self, user_id: int, resource: str, action: str,
                              context: Optional[Dict[str, Any]] = None) -> AccessResult:
        """Verifica políticas de acceso específicas."""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT name, resource_pattern, conditions, effect, priority
                FROM rbac_policies
                WHERE is_active = 1
                ORDER BY priority DESC, id ASC
            """)

            policies = cursor.fetchall()

            for policy in policies:
                if self._policy_matches(policy, resource, action, context):
                    if policy['effect'] == 'DENY':
                        return AccessResult.DENIED
                    elif policy['effect'] == 'ALLOW':
                        return AccessResult.GRANTED

            return AccessResult.CONDITIONAL

    def _policy_matches(self, policy, resource: str, action: str,
                       context: Optional[Dict[str, Any]] = None) -> bool:
        """Verifica si una política aplica al recurso y contexto."""
        import re

        # Verificar patrón de recurso
        pattern = policy['resource_pattern'].replace('*', '.*')
        if not re.match(pattern, resource):
            return False

        # Verificar condiciones adicionales
        if policy['conditions']:
            try:
                conditions = json.loads(policy['conditions'])

                # Verificar condiciones de acción
                if 'actions' in conditions:
                    if action not in conditions['actions']:
                        return False

                # Verificar condiciones de contexto
                if context and 'context' in conditions:
                    for key, value in conditions['context'].items():
                        if key not in context or context[key] != value:
                            return False

            except json.JSONDecodeError:
                return False

        return True

    def _log_access_attempt(self, user_id: int, resource: str, action: str,
                           result: AccessResult, context: Optional[Dict[str, Any]] = None):
        """Registra intento de acceso en el log de auditoría."""
        try:
            details = {}
            if context:
                details.update(context)

            with self._get_db_connection() as conn:
                cursor = conn.cursor()

                cursor.execute("""
                    INSERT INTO rbac_access_log
                    (user_id, resource, action, result, details)
                    VALUES (?, ?, ?, ?, ?)
                """,
(user_id,
                    resource,
                    action,
                    result.value,
                    json.dumps(details)))

                conn.commit()

        except Exception as e:
            log_security_event(
                "ACCESS_LOG_ERROR",
                {"user_id": user_id, "error": str(e)},
                "ERROR"
            )

    def get_user_roles(self, user_id: int) -> List[Role]:
        """Obtiene todos los roles asignados a un usuario."""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT r.id, r.name, r.description, r.parent_id, r.is_active,
                       r.created_at, r.updated_at
                FROM rbac_roles r
                JOIN rbac_user_roles ur ON r.id = ur.role_id
                WHERE ur.user_id = ?
                  AND ur.is_active = 1
                  AND (ur.expires_at IS NULL OR ur.expires_at > datetime('now'))
                  AND r.is_active = 1
                ORDER BY r.name
            """, (user_id,))

            return [Role(**dict(row)) for row in cursor.fetchall()]

    def get_role_permissions(self, role_id: int) -> List[Permission]:
        """Obtiene todos los permisos asignados a un rol."""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT p.id, p.resource, p.action, p.description, p.is_active, p.created_at
                FROM rbac_permissions p
                JOIN rbac_role_permissions rp ON p.id = rp.permission_id
                WHERE rp.role_id = ? AND rp.is_active = 1 AND p.is_active = 1
                ORDER BY p.resource, p.action
            """, (role_id,))

            return [Permission(**dict(row)) for row in cursor.fetchall()]

    def get_access_statistics(self, user_id: Optional[int] = None,
                            days: int = 30) -> Dict[str, Any]:
        """Obtiene estadísticas de acceso del sistema."""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()

            # Construir query segura con parámetros
            if user_id:
                count_query = """
                    SELECT COUNT(*) FROM rbac_access_log
                    WHERE timestamp > datetime('now', '-{} days')
                    AND user_id = ?
                """.format(days)
                params = [user_id]
            else:
                count_query = """
                    SELECT COUNT(*) FROM rbac_access_log
                    WHERE timestamp > datetime('now', '-{} days')
                """.format(days)
                params = []

            # Total de accesos
            cursor.execute(count_query, params)
            total_accesses = cursor.fetchone()[0]

            # Accesos por resultado
            if user_id:
                result_query = """
                    SELECT result, COUNT(*)
                    FROM rbac_access_log
                    WHERE timestamp > datetime('now', '-{} days')
                    AND user_id = ?
                    GROUP BY result
                """.format(days)
            else:
                result_query = """
                    SELECT result, COUNT(*)
                    FROM rbac_access_log
                    WHERE timestamp > datetime('now', '-{} days')
                    GROUP BY result
                """.format(days)
            
            cursor.execute(result_query, params)

            access_by_result = dict(cursor.fetchall())

            # Recursos más accedidos
            cursor.execute(f"""
                SELECT resource, COUNT(*) as count
                {base_query} {user_filter}
                GROUP BY resource
                ORDER BY count DESC
                LIMIT 10
            """, params)

            top_resources = dict(cursor.fetchall())

            return {
                "total_accesses": total_accesses,
                "access_by_result": access_by_result,
                "top_resources": top_resources,
                "period_days": days
            }

    def _is_cache_valid(self) -> bool:
        """Verifica si el caché de permisos sigue siendo válido."""
        return datetime.now() - self.last_cache_update < self.cache_timeout

    def _clear_user_cache(self, user_id: int):
        """Limpia el caché de permisos para un usuario específico."""
        keys_to_remove = [key for key in self.permission_cache.keys()
                         if key.startswith(f"{user_id}:")]
        for key in keys_to_remove:
            del self.permission_cache[key]

    def _clear_role_cache(self, role_id: int):
        """Limpia el caché relacionado con un rol."""
        # En una implementación más sofisticada, esto requeriría mapeo de roles a usuarios
        self.permission_cache.clear()
        self.last_cache_update = datetime.min

    def cleanup_expired_assignments(self) -> int:
        """Limpia asignaciones de roles expiradas."""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE rbac_user_roles
                SET is_active = 0
                WHERE expires_at IS NOT NULL
                  AND expires_at <= datetime('now')
                  AND is_active = 1
            """)

            expired_count = cursor.rowcount
            conn.commit()

            if expired_count > 0:
                log_security_event(
                    "ROLE_ASSIGNMENTS_EXPIRED",
                    {"expired_count": expired_count},
                    "INFO"
                )

            return expired_count


# Instancia global del sistema RBAC
_rbac_system: Optional[RBACDatabase] = None


def init_rbac_system(db_path: str = "rbac.db") -> RBACDatabase:
    """Inicializa el sistema RBAC global."""
    global _rbac_system
    _rbac_system = RBACDatabase(db_path)
    return _rbac_system


def get_rbac_system() -> RBACDatabase:
    """Obtiene la instancia global del sistema RBAC."""
    if _rbac_system is None:
        raise RuntimeError("Sistema RBAC no está inicializado. Llame a init_rbac_system() primero.")
    return _rbac_system


def check_permission(user_id: int, resource: str, action: str,
                    context: Optional[Dict[str, Any]] = None) -> bool:
    """Función de conveniencia para verificar permisos."""
    rbac = get_rbac_system()
    result, _ = rbac.check_access(user_id, resource, action, context)
    return result == AccessResult.GRANTED


def require_permission(resource: str, action: str):
    """Decorador que requiere permisos específicos para ejecutar una función."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Esto requeriría contexto de usuario actual
            # En una implementación real, se obtendría del contexto de sesión
            user_id = kwargs.get('current_user_id')
            if not user_id:
                raise PermissionError("No se pudo determinar el usuario actual")

            if not check_permission(user_id, resource, action):
                raise PermissionError(f"Acceso denegado para {resource}:{action}")

            return func(*args, **kwargs)
        return wrapper
    return decorator
