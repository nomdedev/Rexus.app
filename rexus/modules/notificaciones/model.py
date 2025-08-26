"""
Modelo de Notificaciones - Rexus.app v2.0.0

Maneja la lógica de negocio y acceso a datos para notificaciones.
"""

import logging
import datetime
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

# SQLQueryManager unificado
try:
    from rexus.core.sql_query_manager import SQLQueryManager
except ImportError:
    from rexus.utils.sql_script_loader import sql_script_loader
    
    class SQLQueryManager:
        def __init__(self):
            self.sql_loader = sql_script_loader

        def get_query(self, path, filename):
            script_name = filename
            return self.sql_loader.load_script(script_name)

class NotificacionesModel:
    """Modelo para el módulo de notificaciones."""
    
    def __init__(self, db_connection=None):
        """Inicializa el modelo de notificaciones."""
        self.db_connection = db_connection
        self.sql_manager = SQLQueryManager()
        self.sql_path = 'notificaciones'
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
            query = self.sql_manager.get_query(self.sql_path, 'delete_notificacion_by_id')
            cursor.execute(query, {'notificacion_id': notificacion_id})
            
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
            query = self.sql_manager.get_query(self.sql_path, 'insert_notificacion')
            cursor.execute(query, {
                'titulo': datos.get('titulo'),
                'mensaje': datos.get('mensaje'),
                'tipo': datos.get('tipo', 'info'),
                'usuario_id': datos.get('usuario_id'),
                'fecha_creacion': datetime.datetime.now().isoformat(),
                'leida': False
            })
            
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
            query = self.sql_manager.get_query(self.sql_path, 'update_marcar_leida')
            cursor.execute(query, {
                'leida': True,
                'fecha_lectura': datetime.datetime.now().isoformat(),
                'notificacion_id': notificacion_id
            })
            
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
                query = self.sql_manager.get_query(self.sql_path, 'select_notificaciones_by_usuario')
                cursor.execute(query, {'usuario_id': usuario_id})
            else:
                query = self.sql_manager.get_query(self.sql_path, 'select_notificaciones_all')
                cursor.execute(query)
            
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
                query = self.sql_manager.get_query(self.sql_path, 'select_notificaciones_no_leidas_by_usuario')
                cursor.execute(query, {'usuario_id': usuario_id, 'leida': False})
            else:
                query = self.sql_manager.get_query(self.sql_path, 'select_notificaciones_no_leidas_all')
                cursor.execute(query, {'leida': False})
            
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
                query = self.sql_manager.get_query(self.sql_path, 'count_no_leidas_by_usuario')
                cursor.execute(query, {'usuario_id': usuario_id, 'leida': False})
            else:
                query = self.sql_manager.get_query(self.sql_path, 'count_no_leidas_all')
                cursor.execute(query, {'leida': False})
            
            return cursor.fetchone()[0] or 0
            
        except Exception as e:
            self.logger.error(f"Error contando notificaciones no leídas: {e}")
            return 0
