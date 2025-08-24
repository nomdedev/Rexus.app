"""
Modelo de Notificaciones - Rexus.app v2.0.0

Maneja la lógica de negocio y acceso a datos para notificaciones.
"""

import logging
import datetime
import json
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class NotificacionesModel:
    """Modelo para el módulo de notificaciones."""
    
    def __init__(self, db_connection=None):
        """Inicializa el modelo de notificaciones."""
        self.db_connection = db_connection
        self.logger = logger
        
    def eliminar_notificacion(self, notificacion_id: int) -> bool:
        """
        Elimina una notificación del sistema.

        Args:
            notificacion_id: ID de la notificación

        Returns:
            bool: True si se eliminó exitosamente
        """
        try:
            if not self.db_connection:
                return False
                
            cursor = self.db_connection.cursor()
            cursor.execute("DELETE FROM notificaciones WHERE id = ?", (notificacion_id,))
            
            if cursor.rowcount > 0:
                self.db_connection.commit()
                self.logger.info(f"Notificación {notificacion_id} eliminada exitosamente")
                return True
            else:
                self.logger.warning(f"No se encontró notificación con ID {notificacion_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error eliminando notificación: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False

    def crear_notificacion(self, datos: Dict[str, Any]) -> Optional[int]:
        """Crea una nueva notificación."""
        try:
            if not self.db_connection:
                return None
                
            cursor = self.db_connection.cursor()
            cursor.execute("""
                INSERT INTO notificaciones (titulo, mensaje, tipo, usuario_id, fecha_creacion, leida)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                datos.get('titulo'),
                datos.get('mensaje'),
                datos.get('tipo', 'info'),
                datos.get('usuario_id'),
                datetime.datetime.now().isoformat(),
                False
            ))
            
            notificacion_id = cursor.lastrowid
            self.db_connection.commit()
            self.logger.info(f"Notificación creada exitosamente: {notificacion_id}")
            return notificacion_id
            
        except Exception as e:
            self.logger.error(f"Error creando notificación: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return None

    def marcar_como_leida(self, notificacion_id: int) -> bool:
        """Marca una notificación como leída."""
        try:
            if not self.db_connection:
                return False
                
            cursor = self.db_connection.cursor()
            cursor.execute("""
                UPDATE notificaciones 
                SET leida = ?, fecha_lectura = ?
                WHERE id = ?
            """, (True, datetime.datetime.now().isoformat(), notificacion_id))
            
            if cursor.rowcount > 0:
                self.db_connection.commit()
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Error marcando notificación como leída: {e}")
            if self.db_connection:
                self.db_connection.rollback()
            return False

    def obtener_notificaciones(self, usuario_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Obtiene las notificaciones."""
        try:
            if not self.db_connection:
                return []
                
            cursor = self.db_connection.cursor()
            
            if usuario_id:
                cursor.execute("""
                    SELECT id, titulo, mensaje, tipo, usuario_id, fecha_creacion, leida, fecha_lectura
                    FROM notificaciones 
                    WHERE usuario_id = ? OR usuario_id IS NULL
                    ORDER BY fecha_creacion DESC
                """, (usuario_id,))
            else:
                cursor.execute("""
                    SELECT id, titulo, mensaje, tipo, usuario_id, fecha_creacion, leida, fecha_lectura
                    FROM notificaciones 
                    ORDER BY fecha_creacion DESC
                """)
            
            notificaciones = []
            for row in cursor.fetchall():
                notificaciones.append({
                    'id': row[0],
                    'titulo': row[1],
                    'mensaje': row[2],
                    'tipo': row[3],
                    'usuario_id': row[4],
                    'fecha_creacion': row[5],
                    'leida': bool(row[6]),
                    'fecha_lectura': row[7]
                })
            
            return notificaciones
            
        except Exception as e:
            self.logger.error(f"Error obteniendo notificaciones: {e}")
            return []

    def obtener_notificaciones_no_leidas(self, usuario_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Obtiene las notificaciones no leídas."""
        try:
            if not self.db_connection:
                return []
                
            cursor = self.db_connection.cursor()
            
            if usuario_id:
                cursor.execute("""
                    SELECT id, titulo, mensaje, tipo, usuario_id, fecha_creacion
                    FROM notificaciones 
                    WHERE (usuario_id = ? OR usuario_id IS NULL) AND leida = ?
                    ORDER BY fecha_creacion DESC
                """, (usuario_id, False))
            else:
                cursor.execute("""
                    SELECT id, titulo, mensaje, tipo, usuario_id, fecha_creacion
                    FROM notificaciones 
                    WHERE leida = ?
                    ORDER BY fecha_creacion DESC
                """, (False,))
            
            notificaciones = []
            for row in cursor.fetchall():
                notificaciones.append({
                    'id': row[0],
                    'titulo': row[1],
                    'mensaje': row[2],
                    'tipo': row[3],
                    'usuario_id': row[4],
                    'fecha_creacion': row[5],
                    'leida': False
                })
            
            return notificaciones
            
        except Exception as e:
            self.logger.error(f"Error obteniendo notificaciones no leídas: {e}")
            return []

    def contar_no_leidas(self, usuario_id: Optional[int] = None) -> int:
        """Cuenta las notificaciones no leídas."""
        try:
            if not self.db_connection:
                return 0
                
            cursor = self.db_connection.cursor()
            
            if usuario_id:
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM notificaciones 
                    WHERE (usuario_id = ? OR usuario_id IS NULL) AND leida = ?
                """, (usuario_id, False))
            else:
                cursor.execute("SELECT COUNT(*) FROM notificaciones WHERE leida = ?", (False,))
            
            return cursor.fetchone()[0] or 0
            
        except Exception as e:
            self.logger.error(f"Error contando notificaciones no leídas: {e}")
            return 0
