"""
Submódulos de Usuarios - Rexus.app

Exporta los gestores especializados del módulo usuarios.
"""

from .autenticacion_manager import AutenticacionManager
from .consultas_manager import ConsultasManager
from .usuarios_manager import UsuariosManager
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric
from rexus.core.sql_query_manager import SQLQueryManager
from rexus.utils.unified_sanitizer import sanitize_string, sanitize_numeric

__all__ = ["AutenticacionManager", "UsuariosManager", "ConsultasManager"]
