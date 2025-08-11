"""
Rexus Security Package

Módulos de seguridad para la aplicación Rexus:
- CSRF Protection
- User enumeration protection
- Password management with bcrypt
- Authentication enhancements
- Security middleware
"""

from .csrf_protection import (
    CSRFProtection,
    CSRFToken,
    init_csrf_protection,
    get_csrf_protection,
    generate_csrf_token,
    validate_csrf_token
)

from .user_enumeration_protection import (
    UserEnumerationProtection,
    init_user_enumeration_protection,
    get_user_enumeration_protection,
    record_login_attempt,
    get_response_delay,
    simulate_password_check
)

from .password_manager import (
    PasswordManager,
    init_password_manager,
    get_password_manager,
    hash_password,
    verify_password,
    generate_secure_password,
    validate_password_strength
)

# Backwards compatibility
try:
    from .security_manager import security_manager
    __all__ = ['security_manager']
except ImportError:
    __all__ = []

__all__.extend([
    'CSRFProtection',
    'CSRFToken',
    'init_csrf_protection',
    'get_csrf_protection',
    'generate_csrf_token',
    'validate_csrf_token',
    'UserEnumerationProtection',
    'init_user_enumeration_protection',
    'get_user_enumeration_protection',
    'record_login_attempt',
    'get_response_delay',
    'simulate_password_check',
    'PasswordManager',
    'init_password_manager',
    'get_password_manager',
    'hash_password',
    'verify_password',
    'generate_secure_password',
    'validate_password_strength'
])