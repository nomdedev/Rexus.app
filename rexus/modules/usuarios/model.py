
"""
Modelo de Usuarios - Rexus.app
Gestión de usuarios del sistema
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class UsuariosModel:
    """Modelo para gestión de usuarios."""
    
    def __init__(self, db_connection=None):
        """Inicializa el modelo de usuarios."""
        self.db_connection = db_connection
        self.sql_manager = None
        self.data_sanitizer = None
        
    def buscar_usuarios_filtrado(self, filtros: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Busca usuarios aplicando filtros."""
        try:
            if not self.db_connection:
                logger.warning("No hay conexión a base de datos disponible")
                return []
            
            # Preparar parámetros para la consulta
            params = {
                'busqueda': filtros.get('busqueda') if filtros.get('busqueda') else None,
                'rol': filtros.get('rol') if filtros.get('rol') and filtros['rol'] != 'Todos' else None,
                'estado': filtros.get('estado') if filtros.get('estado') and filtros['estado'] != 'Todos' else None
            }
            
            # Ejecutar consulta usando SQL Manager
            if self.sql_manager:
                usuarios = self.sql_manager.ejecutar_consulta_archivo(
                    'usuarios/buscar_usuarios_filtrado.sql',
                    params
                )
            else:
                # Fallback básico
                usuarios = []
            
            # Convertir a lista de diccionarios si es necesario
            if usuarios and not isinstance(usuarios[0], dict):
                # Convertir tuplas a diccionarios
                columns = ['id', 'username', 'email', 'nombre_completo', 'departamento', 
                          'cargo', 'telefono', 'activo', 'fecha_creacion', 'ultimo_acceso', 'rol', 'estado']
                usuarios = [dict(zip(columns, row)) for row in usuarios]
            
            # Sanitizar datos de salida si está disponible
            if self.data_sanitizer and usuarios:
                usuarios = [self.data_sanitizer.sanitize_dict(usuario) for usuario in usuarios]
            
            logger.info(f"Filtrados {len(usuarios) if usuarios else 0} usuarios exitosamente")
            return usuarios or []
            
        except Exception as e:
            logger.error(f"Error filtrando usuarios: {e}")
            return []
