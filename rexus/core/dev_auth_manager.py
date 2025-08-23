"""
Gestor de Autenticación para Desarrollo - Rexus.app
            """


import logging
logger = logging.getLogger(__name__)

import os
import sys
                    """
        return (usuario == self.dev_user and password == self.dev_password)

    def get_mock_user_session(self) -> Dict[str, Any]:
        """
        Crea una sesión mock para desarrollo.

        Returns:
            Diccionario con datos de sesión simulada
        """
        return {
            'user_id': 1,
            'usuario': self.dev_user,
            'nombre_completo': 'Administrador de Desarrollo',
            'rol': 'admin',
            'permisos': ['all'],  # Permisos completos en desarrollo
            'session_token': 'dev_session_token',
            'is_dev_session': True,
            'login_time': 'development_mode'
        }


# Instancia global para desarrollo
dev_auth_manager = DevAuthManager()
