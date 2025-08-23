"""
Sistema de Autenticación Simple - Rexus.app v2.0.0

Sistema básico de autenticación que funciona con la estructura actual
"""


import logging
logger = logging.getLogger(__name__)

                    allowed_fields = {
            'usuario': 'UPDATE usuarios SET usuario = ? WHERE id = ?',
            'rol': 'UPDATE usuarios SET rol = ? WHERE id = ?',
            'nombre': 'UPDATE usuarios SET nombre = ? WHERE id = ?',
            'apellido': 'UPDATE usuarios SET apellido = ? WHERE id = ?',
            'email': 'UPDATE usuarios SET email = ? WHERE id = ?',
            'estado': 'UPDATE usuarios SET estado = ? WHERE id = ?'
        }

        for field_name, field_value in updates_data.items():
            if field_name not in allowed_fields:
                continue
                
            query = allowed_fields[field_name]
            result = self.db_connection.execute_non_query(query, (field_value, user_id))
            if not result:
                return False

        return True

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
