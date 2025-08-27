"""
Sistema de Autenticación Simple - Rexus.app v2.0.0

Sistema básico de autenticación que funciona con la estructura actual
"""


import logging
try:
    from ..utils.sql_query_manager import SQLQueryManager
except ImportError:
    # Fallback if import fails
    class DummySQLQueryManager:
        def get_query(self, module, query_name):
            return f"-- Query {query_name} not found"
    SQLQueryManager = DummySQLQueryManager

logger = logging.getLogger(__name__)

class AuthManager:
    
    def __init__(self, db_connection=None):
        self.db_connection = db_connection
        self.sql_manager = SQLQueryManager()
        self.allowed_fields = {
            'usuario': 'update_usuario_campo',
            'rol': 'update_rol',
            'nombre': 'update_nombre',
            'apellido': 'update_apellido',
            'email': 'update_email',
            'estado': 'update_activo'
        }
    
    def update_user_fields(self, updates_data, user_id):
        """Actualiza campos de usuario de forma segura."""
        try:
            if not self.db_connection:
                logger.error("No database connection available")
                return False
            
            cursor = self.db_connection.cursor()
            
            for field_name, field_value in updates_data.items():
                if field_name not in self.allowed_fields:
                    logger.warning(f"Field {field_name} not allowed for update")
                    continue
                    
                query_name = self.allowed_fields[field_name]
                query = self.sql_manager.get_query('usuarios', query_name)
                cursor.execute(query, (field_value, user_id))
            
            self.db_connection.commit()
            cursor.close()
            
            logger.info(f"User {user_id} updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error updating user fields: {e}")
            if self.db_connection:
                try:
                    self.db_connection.rollback()
                except Exception:
                    pass
            return False

# Instancia global del gestor de autenticación
_auth_manager = None

def get_auth_manager():
    """Obtiene la instancia global del gestor de autenticación"""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager()
    return _auth_manager

def reset_auth_manager():
    """Reinicia el gestor de autenticación"""
    global _auth_manager
    _auth_manager = None
