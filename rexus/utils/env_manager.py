"""
MIT License

Copyright (c) 2024 Rexus.app

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Environment Manager - Gestión segura de variables de entorno
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any


class EnvironmentManager:
    """Gestor de variables de entorno con validación de seguridad."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._load_env_file()
    
    def _load_env_file(self) -> None:
        """Carga variables desde archivo .env si existe."""
        env_path = Path.cwd() / '.env'
        if env_path.exists():
            try:
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"\'')
                            if key and not key in os.environ:
                                os.environ[key] = value
                self.logger.info("Variables de entorno cargadas desde .env")
            except Exception as e:
                self.logger.warning(f"Error cargando .env: {e}")
    
    def get_secure_credential(self, key: str, default: Optional[str] = None, 
                            mask_in_logs: bool = True) -> str:
        """
        Obtiene una credencial de forma segura.
        
        Args:
            key: Nombre de la variable de entorno
            default: Valor por defecto si no existe
            mask_in_logs: Si ocultar el valor en logs
        
        Returns:
            Valor de la credencial
            
        Raises:
            ValueError: Si la credencial es crítica y no está configurada
        """
        value = os.getenv(key, default)
        
        if not value:
            if key in ['DB_PASSWORD', 'JWT_SECRET_KEY', 'PASSWORD_SALT']:
                raise ValueError(f"Credencial crítica '{key}' no configurada en variables de entorno")
            self.logger.warning(f"Variable de entorno '{key}' no encontrada, usando default")
        
        if mask_in_logs and value:
            masked = f"{value[:2]}{'*' * (len(value) - 4)}{value[-2:]}" if len(value) > 4 else "***"
            self.logger.debug(f"Credencial '{key}' cargada: {masked}")
        
        return value or ""
    
    def get_dev_credentials(self) -> Dict[str, str]:
        """Obtiene credenciales de desarrollo de forma segura."""
        return {
            'user': self.get_secure_credential('REXUS_DEV_USER', 'admin'),
            'password': self.get_secure_credential('REXUS_DEV_PASSWORD'),
            'auto_login': os.getenv('REXUS_DEV_AUTO_LOGIN', 'false').lower() == 'true'
        }
    
    def get_demo_credentials(self) -> Dict[str, str]:
        """Obtiene credenciales de modo demo."""
        return {
            'admin': self.get_secure_credential('DEMO_ADMIN_PASSWORD', 'demo_admin_2025'),
            'supervisor': self.get_secure_credential('DEMO_SUPERVISOR_PASSWORD', 'demo_supervisor_2025'),
            'operador': self.get_secure_credential('DEMO_OPERADOR_PASSWORD', 'demo_operador_2025'),
            'contador': self.get_secure_credential('DEMO_CONTADOR_PASSWORD', 'demo_contador_2025')
        }
    
    def get_database_credentials(self) -> Dict[str, str]:
        """Obtiene credenciales de base de datos."""
        return {
            'server': os.getenv('DB_SERVER', 'localhost'),
            'username': self.get_secure_credential('DB_USERNAME'),
            'password': self.get_secure_credential('DB_PASSWORD'),
            'inventario': os.getenv('DB_INVENTARIO', 'rexus_inventario'),
            'users': os.getenv('DB_USERS', 'rexus_users'),
            'auditoria': os.getenv('DB_AUDITORIA', 'rexus_auditoria')
        }
    
    def get_security_config(self) -> Dict[str, str]:
        """Obtiene configuración de seguridad."""
        return {
            'jwt_secret': self.get_secure_credential('JWT_SECRET_KEY'),
            'password_salt': self.get_secure_credential('PASSWORD_SALT'),
            'app_env': os.getenv('APP_ENV', 'development'),
            'debug': os.getenv('DEBUG', 'true').lower() == 'true'
        }
    
    def is_production(self) -> bool:
        """Verifica si está en modo producción."""
        return os.getenv('APP_ENV', 'development').lower() == 'production'
    
    def is_development(self) -> bool:
        """Verifica si está en modo desarrollo."""
        return os.getenv('APP_ENV', 'development').lower() == 'development'
    
    def validate_security_requirements(self) -> Dict[str, Any]:
        """
        Valida que todas las variables críticas estén configuradas.
        
        Returns:
            Dict con el estado de validación
        """
        results = {
            'valid': True,
            'missing': [],
            'warnings': [],
            'recommendations': []
        }
        
        # Variables críticas para producción
        if self.is_production():
            critical_vars = [
                'DB_PASSWORD', 'JWT_SECRET_KEY', 'PASSWORD_SALT',
                'DB_USERNAME'
            ]
            
            for var in critical_vars:
                if not os.getenv(var):
                    results['missing'].append(var)
                    results['valid'] = False
        
        # Warnings para contraseñas débiles
        dev_password = os.getenv('REXUS_DEV_PASSWORD')
        if dev_password and len(dev_password) < 8:
            results['warnings'].append('REXUS_DEV_PASSWORD es muy corta (mínimo 8 caracteres)')
        
        # Recomendaciones
        if os.getenv('REXUS_DEV_AUTO_LOGIN', 'false').lower() == 'true' and self.is_production():
            results['recommendations'].append('Deshabilitar REXUS_DEV_AUTO_LOGIN en producción')
        
        if not os.getenv('JWT_SECRET_KEY'):
            results['recommendations'].append('Configurar JWT_SECRET_KEY para mayor seguridad')
        
        return results


# Instancia global del gestor
env_manager = EnvironmentManager()


# Funciones de conveniencia
def get_secure_credential(key: str, default: Optional[str] = None) -> str:
    """Función de conveniencia para obtener credenciales."""
    return env_manager.get_secure_credential(key, default)


def get_dev_credentials() -> Dict[str, str]:
    """Función de conveniencia para credenciales de desarrollo."""
    return env_manager.get_dev_credentials()


def get_demo_credentials() -> Dict[str, str]:
    """Función de conveniencia para credenciales de demo."""
    return env_manager.get_demo_credentials()


def is_production() -> bool:
    """Función de conveniencia para verificar modo producción."""
    return env_manager.is_production()


def is_development() -> bool:
    """Función de conveniencia para verificar modo desarrollo."""
    return env_manager.is_development()