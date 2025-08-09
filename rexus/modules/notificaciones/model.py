"""
Modelo de Notificaciones - Rexus.app v2.0.0

Sistema completo de notificaciones y alertas del sistema.
Incluye utilidades de seguridad para prevenir SQL injection y XSS.
"""

import datetime
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from enum import Enum

from rexus.core.auth_manager import admin_required, auth_required, manager_required
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric

# Importar utilidades de seguridad
try:
    root_dir = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(root_dir))
    
        from utils.sql_security import SQLSecurityValidator
    
    SECURITY_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] Security utilities not available in notificaciones: {e}")
    SECURITY_AVAILABLE = False
    data_sanitizer = None

try:
    from rexus.utils.sql_security import SQLSecurityError, validate_table_name
    SQL_SECURITY_AVAILABLE = True
except ImportError:
    print("[WARNING] SQL security utilities not available in notificaciones")
    SQL_SECURITY_AVAILABLE = False
    validate_table_name = None
    SQLSecurityError = Exception


class TipoNotificacion(Enum):
    """Tipos de notificación disponibles"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    CRITICAL = "critical"


class EstadoNotificacion(Enum):
    """Estados de notificación"""
    PENDIENTE = "pendiente"
    LEIDA = "leida"
    ARCHIVADA = "archivada"


class PrioridadNotificacion(Enum):
    """Niveles de prioridad"""
    BAJA = 1
    MEDIA = 2
    ALTA = 3
    CRITICA = 4


class NotificacionesModel:
    """Modelo para gestionar notificaciones del sistema."""
    
    def __init__(self, db_connection=None):
        self.db_connection = db_connection
        self.tabla_notificaciones = "notificaciones"
        self.tabla_usuarios_notificaciones = "usuarios_notificaciones"
        self.tabla_plantillas = "plantillas_notificacion"
        
        # Inicializar utilidades de seguridad
        self.security_available = SECURITY_AVAILABLE
        if self.security_available:
            self.data_sanitizer = data_sanitizer
            self.sql_validator = SQLSecurityValidator()
            print("OK [NOTIFICACIONES] Utilidades de seguridad cargadas")
        else:
            self.data_sanitizer = None
            self.sql_validator = None
            print("WARNING [NOTIFICACIONES] Utilidades de seguridad no disponibles")
        
        self._verificar_tablas()

    def _verificar_tablas(self):
        """Verifica que las tablas necesarias existan."""
        if not self.db_connection:
            print("[WARNING] No hay conexión a BD - modo demo")
            return
        
        try:
            cursor = self.db_connection.cursor()
            
            # Verificar tabla principal de notificaciones
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='notificaciones' AND xtype='U')
                CREATE TABLE notificaciones (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    titulo NVARCHAR(200) NOT NULL,
                    mensaje NTEXT NOT NULL,
                    tipo NVARCHAR(20) DEFAULT 'info',
                    prioridad INT DEFAULT 2,
                    usuario_origen INT,
                    modulo_origen NVARCHAR(50),
                    fecha_creacion DATETIME DEFAULT GETDATE(),
                    fecha_expiracion DATETIME,
                    estado NVARCHAR(20) DEFAULT 'pendiente',
                    metadata NTEXT,
                    activa BIT DEFAULT 1
                )
            """)
            
            # Verificar tabla de notificaciones por usuario
            cursor.execute("""
                IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='usuarios_notificaciones' AND xtype='U')
                CREATE TABLE usuarios_notificaciones (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    notificacion_id INT,
                    usuario_id INT,
                    leida BIT DEFAULT 0,
                    fecha_lectura DATETIME,
                    archivada BIT DEFAULT 0,
                    fecha_archivado DATETIME,
                    FOREIGN KEY (notificacion_id) REFERENCES notificaciones(id)
                )
            """)
            
            self.db_connection.commit()
            print("OK [NOTIFICACIONES] Tablas verificadas/creadas")
            
        except Exception as e:
            print(f"[ERROR NOTIFICACIONES] Error verificando tablas: {str(e)}")

    @auth_required
    def crear_notificacion(self, titulo: str, mensaje: str, tipo: str = "info", 
                          prioridad: int = 2, usuario_destino: Optional[int] = None,
                          modulo_origen: str = None, metadata: Optional[Dict] = None,
                          fecha_expiracion: Optional[datetime.datetime] = None) -> bool:
        """
        Crea una nueva notificación.
        
        Args:
            titulo: Título de la notificación
            mensaje: Contenido del mensaje
            tipo: Tipo de notificación (info, warning, error, success, critical)
            prioridad: Nivel de prioridad (1-4)
            usuario_destino: ID del usuario destinatario (None = todos)
            modulo_origen: Módulo que genera la notificación
            metadata: Datos adicionales en JSON
            fecha_expiracion: Fecha de expiración
            
        Returns:
            bool: True si se creó exitosamente
        """
        if not self.db_connection:
            print("[WARNING] Sin BD - simulando creación de notificación")
            return True
            
        try:
            # Validar y sanitizar datos
            if self.data_sanitizer:
                titulo = self.data_sanitizer.sanitize_input(titulo)
                mensaje = self.data_sanitizer.sanitize_input(mensaje)
                if modulo_origen:
                    modulo_origen = self.data_sanitizer.sanitize_input(modulo_origen)
            
            cursor = self.db_connection.cursor()
            
            # Crear notificación principal
            query = """
                INSERT INTO notificaciones 
                (titulo, mensaje, tipo, prioridad, modulo_origen, fecha_expiracion, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            
            metadata_json = json.dumps(metadata) if metadata else None
            
            cursor.execute(query, (titulo, mensaje, tipo, prioridad, 
                                 modulo_origen, fecha_expiracion, metadata_json))
            
            notificacion_id = cursor.lastrowid
            
            # Si hay usuario específico, crear relación
            if usuario_destino:
                query_usuario = """
                    INSERT INTO usuarios_notificaciones (notificacion_id, usuario_id)
                    VALUES (?, ?)
                """
                cursor.execute(query_usuario, (notificacion_id, usuario_destino))
            
            self.db_connection.commit()
            print(f"OK [NOTIFICACIONES] Notificación creada: ID {notificacion_id}")
            return True
            
        except Exception as e:
            print(f"[ERROR NOTIFICACIONES] Error creando notificación: {str(e)}")
            if self.db_connection:
                self.db_connection.rollback()
            return False

    @auth_required
    def obtener_notificaciones_usuario(self, usuario_id: int, solo_no_leidas: bool = False,
                                     limite: int = 50, offset: int = 0) -> List[Dict]:
        """
        Obtiene las notificaciones de un usuario específico.
        
        Args:
            usuario_id: ID del usuario
            solo_no_leidas: Si obtener solo las no leídas
            limite: Máximo número de notificaciones
            offset: Desplazamiento para paginación
            
        Returns:
            List[Dict]: Lista de notificaciones
        """
        if not self.db_connection:
            return self._obtener_notificaciones_demo(usuario_id)
            
        try:
            cursor = self.db_connection.cursor()
            
            # Query base
            query = """
                SELECT n.id, n.titulo, n.mensaje, n.tipo, n.prioridad,
                       n.modulo_origen, n.fecha_creacion, n.fecha_expiracion,
                       un.leida, un.fecha_lectura, un.archivada
                FROM notificaciones n
                LEFT JOIN usuarios_notificaciones un ON n.id = un.notificacion_id
                WHERE (un.usuario_id = ? OR un.usuario_id IS NULL)
                AND n.activa = 1
                AND (n.fecha_expiracion IS NULL OR n.fecha_expiracion > GETDATE())
            """
            
            params = [usuario_id]
            
            if solo_no_leidas:
                query += " AND (un.leida = 0 OR un.leida IS NULL)"
                
            query += " ORDER BY n.prioridad DESC, n.fecha_creacion DESC"
            query += f" OFFSET {offset} ROWS FETCH NEXT {limite} ROWS ONLY"
            
            cursor.execute(query, params)
            resultados = cursor.fetchall()
            
            notificaciones = []
            for row in resultados:
                notificaciones.append({
                    'id': row[0],
                    'titulo': row[1],
                    'mensaje': row[2],
                    'tipo': row[3],
                    'prioridad': row[4],
                    'modulo_origen': row[5],
                    'fecha_creacion': row[6],
                    'fecha_expiracion': row[7],
                    'leida': row[8] or False,
                    'fecha_lectura': row[9],
                    'archivada': row[10] or False
                })
            
            return notificaciones
            
        except Exception as e:
            print(f"[ERROR NOTIFICACIONES] Error obteniendo notificaciones: {str(e)}")
            return []

    def _obtener_notificaciones_demo(self, usuario_id: int) -> List[Dict]:
        """Datos demo para cuando no hay BD."""
        return [
            {
                'id': 1,
                'titulo': 'Bienvenido a Rexus.app',
                'mensaje': 'Sistema iniciado correctamente',
                'tipo': 'success',
                'prioridad': 2,
                'modulo_origen': 'sistema',
                'fecha_creacion': datetime.datetime.now(),
                'fecha_expiracion': None,
                'leida': False,
                'fecha_lectura': None,
                'archivada': False
            }
        ]

    @auth_required
    def marcar_como_leida(self, notificacion_id: int, usuario_id: int) -> bool:
        """
        Marca una notificación como leída.
        
        Args:
            notificacion_id: ID de la notificación
            usuario_id: ID del usuario
            
        Returns:
            bool: True si se marcó exitosamente
        """
        if not self.db_connection:
            print("[WARNING] Sin BD - simulando marcar como leída")
            return True
            
        try:
            cursor = self.db_connection.cursor()
            
            # Actualizar o insertar relación usuario-notificación
            cursor.execute("""
                IF EXISTS (SELECT 1 FROM usuarios_notificaciones 
                          WHERE notificacion_id = ? AND usuario_id = ?)
                UPDATE usuarios_notificaciones 
                SET leida = 1, fecha_lectura = GETDATE()
                WHERE notificacion_id = ? AND usuario_id = ?
                ELSE
                INSERT INTO usuarios_notificaciones 
                (notificacion_id, usuario_id, leida, fecha_lectura)
                VALUES (?, ?, 1, GETDATE())
            """, (notificacion_id, usuario_id, notificacion_id, usuario_id,
                  notificacion_id, usuario_id))
            
            self.db_connection.commit()
            return True
            
        except Exception as e:
            print(f"[ERROR NOTIFICACIONES] Error marcando como leída: {str(e)}")
            if self.db_connection:
                self.db_connection.rollback()
            return False

    @auth_required
    def contar_no_leidas(self, usuario_id: int) -> int:
        """
        Cuenta las notificaciones no leídas de un usuario.
        
        Args:
            usuario_id: ID del usuario
            
        Returns:
            int: Número de notificaciones no leídas
        """
        if not self.db_connection:
            return 1  # Demo: siempre hay una notificación
            
        try:
            cursor = self.db_connection.cursor()
            
            cursor.execute("""
                SELECT COUNT(*)
                FROM notificaciones n
                LEFT JOIN usuarios_notificaciones un ON n.id = un.notificacion_id
                WHERE (un.usuario_id = ? OR un.usuario_id IS NULL)
                AND n.activa = 1
                AND (n.fecha_expiracion IS NULL OR n.fecha_expiracion > GETDATE())
                AND (un.leida = 0 OR un.leida IS NULL)
            """, (usuario_id,))
            
            result = cursor.fetchone()
            return result[0] if result else 0
            
        except Exception as e:
            print(f"[ERROR NOTIFICACIONES] Error contando no leídas: {str(e)}")
            return 0

    @admin_required
    def eliminar_notificacion(self, notificacion_id: int) -> bool:
        """
        Elimina una notificación del sistema.
        
        Args:
            notificacion_id: ID de la notificación
            
        Returns:
            bool: True si se eliminó exitosamente
        """
        if not self.db_connection:
            print("[WARNING] Sin BD - simulando eliminación")
            return True
            
        try:
            cursor = self.db_connection.cursor()
            
            # Marcar como inactiva en lugar de eliminar (soft delete)
            cursor.execute("""
                UPDATE notificaciones 
                SET activa = 0 
                WHERE id = ?
            """, (notificacion_id,))
            
            self.db_connection.commit()
            return True
            
        except Exception as e:
            print(f"[ERROR NOTIFICACIONES] Error eliminando notificación: {str(e)}")
            if self.db_connection:
                self.db_connection.rollback()
            return False

    @auth_required
    def crear_notificacion_sistema(self, evento: str, modulo: str, 
                                 detalles: Optional[Dict] = None) -> bool:
        """
        Crea notificaciones automáticas del sistema.
        
        Args:
            evento: Tipo de evento (error, alerta, info)
            modulo: Módulo que genera el evento
            detalles: Información adicional
            
        Returns:
            bool: True si se creó exitosamente
        """
        # Mapear eventos a notificaciones
        eventos_map = {
            'error_bd': {
                'titulo': 'Error de Base de Datos',
                'mensaje': f'Se detectó un error en el módulo {modulo}',
                'tipo': 'error',
                'prioridad': 4
            },
            'backup_completado': {
                'titulo': 'Backup Completado',
                'mensaje': 'El respaldo del sistema se completó exitosamente',
                'tipo': 'success',
                'prioridad': 2
            },
            'login_fallido': {
                'titulo': 'Intento de Login Fallido',
                'mensaje': f'Múltiples intentos fallidos desde {modulo}',
                'tipo': 'warning',
                'prioridad': 3
            },
            'sistema_iniciado': {
                'titulo': 'Sistema Iniciado',
                'mensaje': 'Rexus.app se ha iniciado correctamente',
                'tipo': 'info',
                'prioridad': 1
            }
        }
        
        if evento not in eventos_map:
            print(f"[WARNING] Evento desconocido: {evento}")
            return False
            
        config = eventos_map[evento]
        
        # Agregar detalles al mensaje si se proporcionan
        if detalles:
            config['mensaje'] += f" - Detalles: {json.dumps(detalles)}"
            
        return self.crear_notificacion(
            titulo=config['titulo'],
            mensaje=config['mensaje'],
            tipo=config['tipo'],
            prioridad=config['prioridad'],
            modulo_origen=modulo,
            metadata=detalles
        )