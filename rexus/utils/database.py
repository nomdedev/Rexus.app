"""
Alias para database_manager - mantiene compatibilidad con importaciones existentes
"""

# Re-exportar todo desde database_manager
from .database_manager import *
from .database_manager import DatabaseManager, DatabasePool
