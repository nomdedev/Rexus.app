"""
AuthManager - Sistema de autorización para Rexus.app
Controla permisos y acceso a funcionalidades
"""


import logging
logger = logging.getLogger(__name__)

                """Decorador que requiere cualquier usuario autenticado"""
    return AuthManager.require_role(UserRole.VIEWER)(func)
