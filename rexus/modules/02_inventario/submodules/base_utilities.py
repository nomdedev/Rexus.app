"""
Utilidades Base para Inventario - Rexus.app v2.0.0

Utilidades fundamentales para el módulo de inventario:
- Validaciones y sanitización de datos
- Manejo de conexiones de base de datos
- Configuración y inicialización
- Generación de códigos QR y barras
"""

import datetime
import logging
import qrcode
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class BaseInventarioUtilities:
    """Utilidades base para el módulo de inventario."""
    
    def __init__(self, db_connection=None):
        """Inicializa las utilidades base."""
        self.db_connection = db_connection
        self.logger = logger
        
    def crear_paginacion_query(self, base_query: str, offset: int, limit: int,
                              where_clause: str = "", order_clause: str = "") -> str:
        """Crea query con paginación."""
        try:
            # Construir query completa
            full_query = base_query
            
            if where_clause:
                full_query += f" WHERE {where_clause}"
                
            if order_clause:
                full_query += f" ORDER BY {order_clause}"
            else:
                full_query += " ORDER BY id DESC"
                
            # Agregar paginación
            full_query += f" LIMIT {limit} OFFSET {offset}"
            
            return full_query
            
        except Exception as e:
            self.logger.error(f"Error creando query de paginación: {e}")
            return base_query
            
    def validar_conexion_db(self) -> bool:
        """Valida que la conexión a BD esté disponible."""
        try:
            if not self.db_connection:
                return False
                
            cursor = self.db_connection.cursor()
            cursor.execute("SELECT 1", {})
            cursor.close()
            return True
            
        except Exception as e:
            self.logger.error(f"Error validando conexión BD: {e}")
            return False
        finally:
            if 'cursor' in locals():
                cursor.close()