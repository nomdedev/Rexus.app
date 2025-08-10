"""
Mock Database para Desarrollo - Rexus.app
Sistema de autenticación local que no requiere SQL Server
"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any


class DevDatabaseMock:
    """
    Mock de base de datos para desarrollo.
    Almacena usuarios en un archivo JSON local.
    """
    
    def __init__(self):
        self.db_file = Path('.dev_users.json')
        self.users_db = self._load_users_db()
    
    def _load_users_db(self) -> Dict[str, Dict]:
        """Carga o crea la base de datos de usuarios de desarrollo."""
        if self.db_file.exists():
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # Crear usuarios por defecto
        default_users = {
            'admin': {
                'password': 'admin',  # En producción sería hasheado
                'nombre_completo': 'Administrador de Desarrollo',
                'rol': 'admin',
                'permisos': ['all'],
                'activo': True
            },
            'usuario': {
                'password': 'usuario',
                'nombre_completo': 'Usuario de Desarrollo',
                'rol': 'user',
                'permisos': ['read', 'write'],
                'activo': True
            },
            'test': {
                'password': 'test',
                'nombre_completo': 'Usuario de Pruebas',
                'rol': 'test',
                'permisos': ['read'],
                'activo': True
            }
        }
        
        self._save_users_db(default_users)
        return default_users
    
    def _save_users_db(self, users_data: Dict):
        """Guarda la base de datos de usuarios."""
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(users_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[DEV_DB] Error guardando usuarios: {e}")
    
    def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Autentica un usuario.
        
        Args:
            username: Nombre de usuario
            password: Contraseña
            
        Returns:
            Diccionario con datos del usuario si es válido, None si no
        """
        user_data = self.users_db.get(username)
        
        if not user_data:
            print(f"[DEV_DB] Usuario '{username}' no encontrado")
            return None
        
        if not user_data.get('activo', False):
            print(f"[DEV_DB] Usuario '{username}' está inactivo")
            return None
            
        if user_data.get('password') != password:
            print(f"[DEV_DB] Contraseña incorrecta para '{username}'")
            return None
        
        # Autenticación exitosa
        session_data = {
            'user_id': hash(username),  # Simular ID
            'usuario': username,
            'nombre_completo': user_data.get('nombre_completo', username),
            'rol': user_data.get('rol', 'user'),
            'permisos': user_data.get('permisos', []),
            'session_token': f'dev_token_{username}',
            'is_dev_session': True,
            'login_time': 'development_mode'
        }
        
        print(f"[DEV_DB] Autenticación exitosa: {username} ({user_data.get('rol', 'user')})")
        return session_data
    
    def is_available(self) -> bool:
        """Verifica si el sistema está disponible."""
        return True
    
    def get_available_users(self) -> list:
        """Retorna lista de usuarios disponibles para desarrollo."""
        return [
            {'username': user, 'rol': data.get('rol', 'user'), 'activo': data.get('activo', False)}
            for user, data in self.users_db.items()
            if data.get('activo', False)
        ]


# Instancia global para desarrollo
dev_db_mock = DevDatabaseMock()


def get_dev_authentication_method():
    """
    Retorna el método de autenticación para desarrollo.
    
    Returns:
        función que acepta (username, password) y retorna user_data o None
    """
    return dev_db_mock.authenticate


def is_dev_mode() -> bool:
    """Detecta si está en modo desarrollo."""
    return (
        '--dev' in os.sys.argv or
        os.getenv('REXUS_ENV') == 'development' or
        os.getenv('REXUS_DEV_AUTO_LOGIN', '').lower() == 'true' or
        os.getenv('HOTRELOAD_ENABLED', '').lower() == 'true'
    )


def setup_dev_authentication():
    """Configura autenticación para desarrollo."""
    if is_dev_mode():
        print(f"[DEV_DB] Sistema de autenticación local iniciado")
        print(f"[DEV_DB] Usuarios disponibles: {len(dev_db_mock.users_db)}")
        
        # Mostrar usuarios disponibles
        for user, data in dev_db_mock.users_db.items():
            if data.get('activo', False):
                print(f"[DEV_DB]   - {user} ({data.get('rol', 'user')})")
        
        return True
    return False