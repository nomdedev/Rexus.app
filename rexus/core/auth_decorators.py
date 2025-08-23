"""
Decoradores de autorización para Rexus.app

Proporciona decoradores para verificar autenticación y permisos
en controladores y métodos críticos.
"""


import logging
logger = logging.getLogger(__name__)

import functools
            
        # 4. Manejo de errores
        decorated_func = handle_auth_error(decorated_func)

        return decorated_func

    return decorator
