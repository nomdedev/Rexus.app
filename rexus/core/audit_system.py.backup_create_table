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
import logging
import sqlite3
from typing import Optional, List, Dict, Any
from enum import Enum

# Sistema de logging
try:
    from ..utils.app_logger import get_logger
    audit_logger = get_logger(__name__)
except ImportError:
    import logging
    audit_logger = logging.getLogger(__name__)


class AuditEvent(Enum):
    """Tipos de eventos de auditoría."""
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAILED = "LOGIN_FAILED"
    LOGOUT = "LOGOUT"
    USER_CREATED = "USER_CREATED"
    USER_UPDATED = "USER_UPDATED"
    USER_DELETED = "USER_DELETED"
    ACCOUNT_LOCKED = "ACCOUNT_LOCKED"
    PERMISSION_GRANTED = "PERMISSION_GRANTED"
    PERMISSION_REVOKED = "PERMISSION_REVOKED"
    SENSITIVE_DATA_ACCESS = "SENSITIVE_DATA_ACCESS"
    SUSPICIOUS_ACTIVITY = "SUSPICIOUS_ACTIVITY"
    SYSTEM_ERROR = "SYSTEM_ERROR"
    SYSTEM_START = "SYSTEM_START"
    SYSTEM_STOP = "SYSTEM_STOP"


class AuditLevel(Enum):
    """Niveles de auditoría."""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    SECURITY = "SECURITY"


class AuditSystem:
    """Sistema de auditoría y logging de seguridad."""
    
    def __init__(self, db_connection=None):
        """Inicializa el sistema de auditoría."""
        self.db_connection = db_connection
        self._create_audit_table()
    
    def _create_audit_table(self):
        """Crea la tabla de auditoría si no existe."""
        if not self.db_connection:
            return
        
        try:
            cursor = self.db_connection.connection.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS auditoria_sistema (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    event_type TEXT NOT NULL,
                    level TEXT NOT NULL,
                    usuario_id INTEGER,
                    usuario_nombre TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    modulo TEXT,
                    accion TEXT,
                    detalles TEXT,
                    resultado TEXT,
                    session_id TEXT
                )
            """)
            self.db_connection.connection.commit()
        except sqlite3.Error as e:
            audit_logger.error(f"Error creando tabla de auditoría: {e}")
    
    def log_event(self, event_type: AuditEvent, level: AuditLevel, modulo: str, 
                  accion: str, resultado: str = None, **kwargs):
        """Registra un evento de auditoría."""
        try:
            # Preparar datos del evento
            event_data = {
                'event_type': event_type.value,
                'level': level.value,
                'modulo': modulo,
                'accion': accion,
                'resultado': resultado,
                'timestamp': datetime.datetime.now(),
                **kwargs
            }
            
            # Extraer campos específicos
            usuario_id = event_data.pop('usuario_id', None)
            usuario_nombre = event_data.pop('usuario_nombre', None)
            ip_address = event_data.pop('ip_address', None)
            user_agent = event_data.pop('user_agent', None)
            session_id = event_data.pop('session_id', None)
            
            # El resto va a detalles como JSON
            detalles = {k: v for k, v in event_data.items() 
                       if k not in ['event_type', 'level', 'modulo', 'accion', 'resultado', 'timestamp']}
            
            # Log local
            audit_logger.info(f"[AUDIT] {level.value} - {modulo}: {accion} - {resultado}")
            
            # Persistir en base de datos si está disponible
            if self.db_connection:
                self._persist_audit_event(
                    event_type=event_type.value,
                    level=level.value,
                    usuario_id=usuario_id,
                    usuario_nombre=usuario_nombre,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    modulo=modulo,
                    accion=accion,
                    detalles=json.dumps(detalles) if detalles else None,
                    resultado=resultado,
                    session_id=session_id
                )
                
        except Exception as e:
            audit_logger.exception(f"Error registrando evento de auditoría: {e}")
    
    def _persist_audit_event(self, **event_data):
        """Persiste evento en base de datos."""
        try:
            cursor = self.db_connection.connection.cursor()
            cursor.execute("""
                INSERT INTO auditoria_sistema 
                (event_type, level, usuario_id, usuario_nombre, ip_address, 
                 user_agent, modulo, accion, detalles, resultado, session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event_data.get('event_type'),
                event_data.get('level'),
                event_data.get('usuario_id'),
                event_data.get('usuario_nombre'),
                event_data.get('ip_address'),
                event_data.get('user_agent'),
                event_data.get('modulo'),
                event_data.get('accion'),
                event_data.get('detalles'),
                event_data.get('resultado'),
                event_data.get('session_id')
            ))
            self.db_connection.connection.commit()
        except sqlite3.Error as e:
            audit_logger.error(f"Error persistiendo evento: {e}")
    
    def log_login_success(self, usuario_id: int, usuario_nombre: str,
                         ip_address: str = None, user_agent: str = None,
                         session_id: str = None):
        """Registra un login exitoso."""
        self.log_event(
            event_type=AuditEvent.LOGIN_SUCCESS,
            level=AuditLevel.INFO,
            modulo="AUTENTICACION",
            accion=f"Login exitoso para usuario {usuario_nombre}",
            resultado="SUCCESS",
            usuario_id=usuario_id,
            usuario_nombre=usuario_nombre,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id
        )
    
    def log_login_failed(self, usuario_nombre: str, razon: str = None,
                        ip_address: str = None, user_agent: str = None):
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
                        audit_logger.warning(f"[WARNING AUDIT] Error parsing JSON details: {e}")
                        log_entry['detalles'] = str(log_entry['detalles'])
                logs.append(log_entry)

            return logs

        except (sqlite3.Error, AttributeError) as e:
            audit_logger.error(f"[ERROR] [AUDIT] Error obteniendo logs de auditoría: {e}", exc_info=True)
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

        except (sqlite3.Error, AttributeError, ValueError) as e:
            audit_logger.error(f"[ERROR] [AUDIT] Error obteniendo resumen de seguridad: {e}", exc_info=True)
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
