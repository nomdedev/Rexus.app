"""
Sistema de Auditoría y Logging de Seguridad - Rexus.app v2.0.0

FUNCIONALIDADES DE SEGURIDAD:
[CHECK] Auditoría completa de accesos al sistema
[CHECK] Logging de cambios críticos de usuarios
[CHECK] Registro de acciones sensibles con detalles
[CHECK] Detección de actividades sospechosas
[CHECK] Reportes de seguridad y compliance
"""

import datetime
import json
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


class AuditLevel(Enum):
    """Niveles de auditoría."""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    SECURITY = "SECURITY"


class AuditEvent(Enum):
    """Tipos de eventos auditables."""
    # Autenticación
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILED = "LOGIN_FAILED"
    LOGOUT = "LOGOUT"
    PASSWORD_CHANGED = "PASSWORD_CHANGED"
    ACCOUNT_LOCKED = "ACCOUNT_LOCKED"
    ACCOUNT_UNLOCKED = "ACCOUNT_UNLOCKED"

    # Gestión de usuarios
    USER_CREATED = "USER_CREATED"
    USER_UPDATED = "USER_UPDATED"
    USER_DELETED = "USER_DELETED"
    USER_ACTIVATED = "USER_ACTIVATED"
    USER_DEACTIVATED = "USER_DEACTIVATED"

    # Permisos y roles
    ROLE_ASSIGNED = "ROLE_ASSIGNED"
    ROLE_REMOVED = "ROLE_REMOVED"
    PERMISSION_GRANTED = "PERMISSION_GRANTED"
    PERMISSION_REVOKED = "PERMISSION_REVOKED"

    # Acceso a módulos
    MODULE_ACCESS = "MODULE_ACCESS"
    SENSITIVE_DATA_ACCESS = "SENSITIVE_DATA_ACCESS"
    ADMIN_PANEL_ACCESS = "ADMIN_PANEL_ACCESS"

    # Configuración del sistema
    CONFIG_CHANGED = "CONFIG_CHANGED"
    DATABASE_ACCESS = "DATABASE_ACCESS"
    BACKUP_CREATED = "BACKUP_CREATED"
    BACKUP_RESTORED = "BACKUP_RESTORED"

    # Seguridad
    SECURITY_VIOLATION = "SECURITY_VIOLATION"
    SUSPICIOUS_ACTIVITY = "SUSPICIOUS_ACTIVITY"
    BRUTE_FORCE_ATTEMPT = "BRUTE_FORCE_ATTEMPT"
    UNAUTHORIZED_ACCESS = "UNAUTHORIZED_ACCESS"


@dataclass
class AuditEntry:
    """Entrada de auditoría."""
    timestamp: datetime.datetime
    event_type: AuditEvent
    level: AuditLevel
    usuario_id: Optional[int]
    usuario_nombre: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    modulo: str
    accion: str
    detalles: Dict[str, Any]
    resultado: str  # "SUCCESS", "FAILED", "BLOCKED"
    session_id: Optional[str]


class AuditSystem:
    """Sistema centralizado de auditoría y logging de seguridad."""

    def __init__(self, db_connection=None):
        self.db_connection = db_connection
        self._crear_tabla_auditoria()

    def _crear_tabla_auditoria(self):
        """Crea la tabla de auditoría si no existe."""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.connection.cursor()

            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='auditoria_sistema' AND xtype='U')
                CREATE TABLE auditoria_sistema (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    timestamp DATETIME NOT NULL DEFAULT GETDATE(),
                    event_type NVARCHAR(50) NOT NULL,
                    level NVARCHAR(20) NOT NULL,
                    usuario_id INT NULL,
                    usuario_nombre NVARCHAR(100) NULL,
                    ip_address NVARCHAR(45) NULL,
                    user_agent NVARCHAR(500) NULL,
                    modulo NVARCHAR(50) NOT NULL,
                    accion NVARCHAR(100) NOT NULL,
                    detalles NTEXT NULL,
                    resultado NVARCHAR(20) NOT NULL,
                    session_id NVARCHAR(100) NULL,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                )
            """)

            # Índices para consultas eficientes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_auditoria_timestamp ON auditoria_sistema(timestamp)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_auditoria_usuario ON auditoria_sistema(usuario_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_auditoria_event_type ON auditoria_sistema(event_type)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_auditoria_level ON auditoria_sistema(level)
            """)

            self.db_connection.connection.commit()
            print("[CHECK] [AUDIT] Tabla de auditoría creada/verificada")

        except Exception as e:
            print(f"[ERROR] [AUDIT] Error creando tabla de auditoría: {e}")
            if self.db_connection:
                self.db_connection.connection.rollback()

    def log_event(self,
                  event_type: AuditEvent,
                  level: AuditLevel,
                  modulo: str,
                  accion: str,
                  resultado: str = "SUCCESS",
                  usuario_id: Optional[int] = None,
                  usuario_nombre: Optional[str] = None,
                  ip_address: Optional[str] = None,
                  user_agent: Optional[str] = None,
                  session_id: Optional[str] = None,
                  **detalles) -> bool:
        """
        Registra un evento de auditoría.

        Args:
            event_type: Tipo de evento (AuditEvent)
            level: Nivel de auditoría (AuditLevel)
            modulo: Módulo donde ocurrió el evento
            accion: Descripción de la acción realizada
            resultado: Resultado de la acción ("SUCCESS", "FAILED", "BLOCKED")
            usuario_id: ID del usuario (si aplica)
            usuario_nombre: Nombre del usuario (si aplica)
            ip_address: Dirección IP del cliente
            user_agent: User agent del cliente
            session_id: ID de sesión
            **detalles: Detalles adicionales del evento
        """
        try:
            # Log a consola siempre
            timestamp = datetime.datetime.now()
            detalles_json = json.dumps(detalles, default=str, ensure_ascii=False)

            print(f"[SEARCH] [AUDIT {level.value}] {timestamp} | {event_type.value} | "
                  f"Usuario: {usuario_nombre or 'Sistema'} | Módulo: {modulo} | "
                  f"Acción: {accion} | Resultado: {resultado}")

            if level in [AuditLevel.CRITICAL, AuditLevel.SECURITY]:
                print(f"[WARN] [AUDIT CRÍTICO] Detalles: {detalles_json}")

            # Guardar en base de datos si está disponible
            if self.db_connection:
                cursor = self.db_connection.connection.cursor()

                cursor.execute("""
                    INSERT INTO auditoria_sistema
                    (timestamp, event_type, level, usuario_id, usuario_nombre,
                     ip_address, user_agent, modulo, accion, detalles, resultado, session_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    timestamp,
                    event_type.value,
                    level.value,
                    usuario_id,
                    usuario_nombre,
                    ip_address,
                    user_agent,
                    modulo,
                    accion,
                    detalles_json,
                    resultado,
                    session_id
                ))

                self.db_connection.connection.commit()

            return True

        except Exception as e:
            print(f"[ERROR] [AUDIT] Error registrando evento de auditoría: {e}")
            return False

    def log_login_success(self, usuario_id: int, usuario_nombre: str,
                          ip_address: str = None, user_agent: str = None,
                          session_id: str = None):
        """Registra un login exitoso."""
        self.log_event(
            event_type=AuditEvent.LOGIN_SUCCESS,
            level=AuditLevel.INFO,
            modulo="AUTENTICACION",
            accion=f"Login exitoso de usuario {usuario_nombre}",
            resultado="SUCCESS",
            usuario_id=usuario_id,
            usuario_nombre=usuario_nombre,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id
        )

    def log_login_failed(self, usuario_nombre: str, ip_address: str = None,
                         user_agent: str = None, razon: str = "Credenciales incorrectas"):
        """Registra un intento de login fallido."""
        self.log_event(
            event_type=AuditEvent.LOGIN_FAILED,
            level=AuditLevel.WARNING,
            modulo="AUTENTICACION",
            accion=f"Intento de login fallido para usuario {usuario_nombre}",
            resultado="FAILED",
            usuario_nombre=usuario_nombre,
            ip_address=ip_address,
            user_agent=user_agent,
            razon=razon
        )

    def log_account_locked(self, usuario_nombre: str, intentos: int,
                           ip_address: str = None):
        """Registra el bloqueo de una cuenta."""
        self.log_event(
            event_type=AuditEvent.ACCOUNT_LOCKED,
            level=AuditLevel.CRITICAL,
            modulo="SEGURIDAD",
            accion=f"Cuenta bloqueada: {usuario_nombre}",
            resultado="BLOCKED",
            usuario_nombre=usuario_nombre,
            ip_address=ip_address,
            intentos_fallidos=intentos,
            motivo="Múltiples intentos de login fallidos"
        )

    def log_user_created(self, admin_id: int, admin_nombre: str,
                         nuevo_usuario: str, rol: str):
        """Registra la creación de un usuario."""
        self.log_event(
            event_type=AuditEvent.USER_CREATED,
            level=AuditLevel.CRITICAL,
            modulo="USUARIOS",
            accion=f"Usuario creado: {nuevo_usuario}",
            resultado="SUCCESS",
            usuario_id=admin_id,
            usuario_nombre=admin_nombre,
            nuevo_usuario=nuevo_usuario,
            rol_asignado=rol
        )

    def log_user_updated(self, admin_id: int, admin_nombre: str,
                         usuario_modificado: str, cambios: Dict[str, Any]):
        """Registra la modificación de un usuario."""
        self.log_event(
            event_type=AuditEvent.USER_UPDATED,
            level=AuditLevel.CRITICAL,
            modulo="USUARIOS",
            accion=f"Usuario modificado: {usuario_modificado}",
            resultado="SUCCESS",
            usuario_id=admin_id,
            usuario_nombre=admin_nombre,
            usuario_modificado=usuario_modificado,
            cambios_realizados=cambios
        )

    def log_permission_changed(self, admin_id: int, admin_nombre: str,
                               usuario_afectado: str, accion: str,
                               permisos: List[str]):
        """Registra cambios en permisos."""
        self.log_event(
            event_type=AuditEvent.PERMISSION_GRANTED if "grant" in accion.lower() else AuditEvent.PERMISSION_REVOKED,
            level=AuditLevel.CRITICAL,
            modulo="PERMISOS",
            accion=f"Permisos modificados para {usuario_afectado}",
            resultado="SUCCESS",
            usuario_id=admin_id,
            usuario_nombre=admin_nombre,
            usuario_afectado=usuario_afectado,
            accion_realizada=accion,
            permisos_modificados=permisos
        )

    def log_sensitive_access(self, usuario_id: int, usuario_nombre: str,
                             modulo: str, recurso: str, session_id: str = None):
        """Registra acceso a datos sensibles."""
        self.log_event(
            event_type=AuditEvent.SENSITIVE_DATA_ACCESS,
            level=AuditLevel.SECURITY,
            modulo=modulo,
            accion=f"Acceso a recurso sensible: {recurso}",
            resultado="SUCCESS",
            usuario_id=usuario_id,
            usuario_nombre=usuario_nombre,
            session_id=session_id,
            recurso_accedido=recurso
        )

    def log_suspicious_activity(self, descripcion: str, ip_address: str = None,
                                usuario_nombre: str = None, detalles: Dict = None):
        """Registra actividad sospechosa."""
        self.log_event(
            event_type=AuditEvent.SUSPICIOUS_ACTIVITY,
            level=AuditLevel.CRITICAL,
            modulo="SEGURIDAD",
            accion=f"Actividad sospechosa detectada: {descripcion}",
            resultado="BLOCKED",
            usuario_nombre=usuario_nombre,
            ip_address=ip_address,
            **(detalles or {})
        )

    def get_audit_logs(self,
                       usuario_id: Optional[int] = None,
                       event_type: Optional[AuditEvent] = None,
                       level: Optional[AuditLevel] = None,
                       modulo: Optional[str] = None,
                       fecha_inicio: Optional[datetime.datetime] = None,
                       fecha_fin: Optional[datetime.datetime] = None,
                       limit: int = 100) -> List[Dict]:
        """
        Obtiene logs de auditoría con filtros.

        Returns:
            Lista de entries de auditoría
        """
        if not self.db_connection:
            return []

        try:
            cursor = self.db_connection.connection.cursor()

            # Construir query con filtros
            where_clauses = []
            params = []

            if usuario_id:
                where_clauses.append("usuario_id = ?")
                params.append(usuario_id)

            if event_type:
                where_clauses.append("event_type = ?")
                params.append(event_type.value)

            if level:
                where_clauses.append("level = ?")
                params.append(level.value)

            if modulo:
                where_clauses.append("modulo = ?")
                params.append(modulo)

            if fecha_inicio:
                where_clauses.append("timestamp >= ?")
                params.append(fecha_inicio)

            if fecha_fin:
                where_clauses.append("timestamp <= ?")
                params.append(fecha_fin)

            where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

            query = f"""
                SELECT TOP {limit}
                    id, timestamp, event_type, level, usuario_id, usuario_nombre,
                    ip_address, user_agent, modulo, accion, detalles, resultado, session_id
                FROM auditoria_sistema
                WHERE {where_sql}
                ORDER BY timestamp DESC
            """

            cursor.execute(query, params)

            logs = []
            columns = [desc[0] for desc in cursor.description]

            for row in cursor.fetchall():
                log_entry = dict(zip(columns, row))
                # Parsear detalles JSON
                if log_entry.get('detalles'):
                    try:
                        log_entry['detalles'] = json.loads(log_entry['detalles'])
                    except (json.JSONDecodeError, TypeError) as e:
                        print(f"[WARNING AUDIT] Error parsing JSON details: {e}")
                        log_entry['detalles'] = str(log_entry['detalles'])
                logs.append(log_entry)

            return logs

        except Exception as e:
            print(f"[ERROR] [AUDIT] Error obteniendo logs de auditoría: {e}")
            return []

    def get_security_summary(self, dias: int = 30) -> Dict[str, Any]:
        """
        Obtiene un resumen de eventos de seguridad de los últimos días.

        Returns:
            Diccionario con estadísticas de seguridad
        """
        if not self.db_connection:
            return {}

        try:
            cursor = self.db_connection.connection.cursor()
            fecha_inicio = datetime.datetime.now() - datetime.timedelta(days=dias)

            # Contar eventos por tipo
            cursor.execute("""
                SELECT event_type, COUNT(*) as total
                FROM auditoria_sistema
                WHERE timestamp >= ?
                GROUP BY event_type
                ORDER BY total DESC
            """, (fecha_inicio,))

            eventos_por_tipo = {row[0]: row[1] for row in cursor.fetchall()}

            # Eventos críticos
            cursor.execute("""
                SELECT COUNT(*) as total
                FROM auditoria_sistema
                WHERE timestamp >= ? AND level IN ('CRITICAL', 'SECURITY')
            """, (fecha_inicio,))

            eventos_criticos = cursor.fetchone()[0]

            # Intentos de login fallidos
            cursor.execute("""
                SELECT COUNT(*) as total
                FROM auditoria_sistema
                WHERE timestamp >= ? AND event_type = 'LOGIN_FAILED'
            """, (fecha_inicio,))

            login_fallidos = cursor.fetchone()[0]

            # Cuentas bloqueadas
            cursor.execute("""
                SELECT COUNT(*) as total
                FROM auditoria_sistema
                WHERE timestamp >= ? AND event_type = 'ACCOUNT_LOCKED'
            """, (fecha_inicio,))

            cuentas_bloqueadas = cursor.fetchone()[0]

            return {
                "periodo_dias": dias,
                "eventos_por_tipo": eventos_por_tipo,
                "eventos_criticos": eventos_criticos,
                "login_fallidos": login_fallidos,
                "cuentas_bloqueadas": cuentas_bloqueadas,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": datetime.datetime.now()
            }

        except Exception as e:
            print(f"[ERROR] [AUDIT] Error obteniendo resumen de seguridad: {e}")
            return {}


# Instancia global del sistema de auditoría
_audit_system = None


def get_audit_system() -> AuditSystem:
    """Obtiene la instancia global del sistema de auditoría."""
    return _audit_system


def init_audit_system(db_connection) -> AuditSystem:
    """Inicializa el sistema de auditoría."""
    global _audit_system
    _audit_system = AuditSystem(db_connection)
    return _audit_system
