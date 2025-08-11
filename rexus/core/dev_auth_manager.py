"""
Gestor de Autenticación para Desarrollo - Rexus.app
Auto-login con credenciales de desarrollo desde variables de entorno.
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

# Cargar variables de entorno para desarrollo
try:
    from dotenv import load_dotenv
    # Cargar archivo .env.development si existe
    env_file = Path('.env.development')
    if env_file.exists():
        load_dotenv(env_file)
        print(f"[DEV_AUTH] Configuración cargada desde {env_file}")
    else:
        print("[DEV_AUTH] Archivo .env.development no encontrado, usando variables del sistema")
except ImportError:
    print("[DEV_AUTH] python-dotenv no disponible, usando solo variables del sistema")


class DevAuthManager:
    """
    Gestor de autenticación para desarrollo con auto-login.
    """
    
    def __init__(self):
        from rexus.utils.env_manager import get_dev_credentials, get_secure_credential
        
        # Usar el gestor de entorno seguro
        dev_creds = get_dev_credentials()
        self.dev_user = dev_creds.get('user', 'admin')
        self.dev_password = get_secure_credential('REXUS_DEV_PASSWORD', 'dev_secure_2025')
        self.auto_login_enabled = dev_creds.get('auto_login', False)
        
        # No mostrar credenciales en logs por seguridad
        print(f"[DEV_AUTH] Auto-login: {'✅ Habilitado' if self.auto_login_enabled else '❌ Deshabilitado'}")
        print(f"[DEV_AUTH] Usuario: {self.dev_user[:2]}***")
    
    def get_dev_credentials(self) -> Dict[str, str]:
        """
        Obtiene las credenciales de desarrollo desde variables de entorno.
        
        Returns:
            Dict con usuario y contraseña para desarrollo
        """
        return {
            'usuario': self.dev_user,
            'password': self.dev_password
        }
    
    def is_auto_login_enabled(self) -> bool:
        """
        Verifica si el auto-login está habilitado.
        """
        return self.auto_login_enabled
    
    def should_skip_login_dialog(self) -> bool:
        """
        Determina si debe saltarse el diálogo de login en desarrollo.
        """
        # Solo saltar en modo desarrollo y si está habilitado
        is_dev_mode = (
            os.getenv('REXUS_ENV', 'development') == 'development' or
            '--dev' in sys.argv or
            os.getenv('HOTRELOAD_ENABLED', 'false').lower() == 'true'
        )
        
        return is_dev_mode and self.auto_login_enabled
    
    def validate_dev_credentials(self, usuario: str, password: str) -> bool:
        """
        Valida credenciales contra las configuradas para desarrollo.
        
        Args:
            usuario: Nombre de usuario
            password: Contraseña
            
        Returns:
            True si las credenciales coinciden
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