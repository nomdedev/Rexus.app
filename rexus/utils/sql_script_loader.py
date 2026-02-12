#!/usr/bin/env python3
"""
Cargador de scripts SQL para el sistema.
Permite cargar y ejecutar scripts SQL desde archivos.
"""

import os
import logging
from typing import Dict, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

class SQLScriptLoader:
    """
    Clase para cargar scripts SQL desde archivos.
    """
    
    def __init__(self, base_path: str = "sql"):
        """
        Inicializa el cargador de scripts SQL.
        
        Args:
            base_path: Ruta base donde se encuentran los scripts SQL
        """
        self.base_path = Path(base_path)
        self.logger = logging.getLogger(__name__)
        self._script_cache = {}
    
    def load_script(self, script_path: str) -> str:
        """
        Carga un script SQL desde un archivo.
        
        Args:
            script_path: Ruta relativa del script SQL
            
        Returns:
            str: Contenido del script SQL
            
        Raises:
            FileNotFoundError: Si el archivo no existe
            IOError: Si hay error al leer el archivo
        """
        full_path = self.base_path / script_path
        
        # Verificar si está en caché
        if str(full_path) in self._script_cache:
            return self._script_cache[str(full_path)]
        
        try:
            if not full_path.exists():
                raise FileNotFoundError(f"Script SQL no encontrado: {full_path}")
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Almacenar en caché
            self._script_cache[str(full_path)] = content
            
            self.logger.debug(f"Script SQL cargado: {script_path}")
            return content
            
        except Exception as e:
            self.logger.error(f"Error cargando script SQL {script_path}: {e}")
            raise
    
    def load_script_with_params(self, script_path: str, params: Dict[str, str]) -> str:
        """
        Carga un script SQL y reemplaza parámetros.
        
        Args:
            script_path: Ruta relativa del script SQL
            params: Diccionario de parámetros a reemplazar
            
        Returns:
            str: Contenido del script SQL con parámetros reemplazados
        """
        content = self.load_script(script_path)
        
        for key, value in params.items():
            placeholder = f"{{{key}}}"
            content = content.replace(placeholder, str(value))
        
        return content
    
    def list_scripts(self, module_path: str = None) -> List[str]:
        """
        Lista todos los scripts SQL disponibles.
        
        Args:
            module_path: Ruta del módulo específico (opcional)
            
        Returns:
            List[str]: Lista de rutas de scripts SQL
        """
        scripts = []
        
        search_path = self.base_path
        if module_path:
            search_path = self.base_path / module_path
        
        if not search_path.exists():
            return scripts
        
        for file_path in search_path.rglob("*.sql"):
            relative_path = file_path.relative_to(self.base_path)
            scripts.append(str(relative_path))
        
        return sorted(scripts)
    
    def clear_cache(self):
        """Limpia la caché de scripts."""
        self._script_cache.clear()
        self.logger.debug("Caché de scripts SQL limpiada")
    
    def validate_script(self, script_path: str) -> bool:
        """
        Valida que un script SQL sea sintácticamente correcto.
        
        Args:
            script_path: Ruta del script a validar
            
        Returns:
            bool: True si el script es válido
        """
        try:
            content = self.load_script(script_path)
            
            # Validaciones básicas
            if not content.strip():
                return False
            
            # Verificar balance de paréntesis
            paren_count = content.count('(') - content.count(')')
            if paren_count != 0:
                return False
            
            # Verificar que termine con punto y coma si es una sola consulta
            statements = content.split(';')
            for stmt in statements[:-1]:  # Ignorar el último que puede estar vacío
                if not stmt.strip():
                    continue
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error validando script {script_path}: {e}")
            return False

# Instancia global del cargador de scripts
sql_script_loader = SQLScriptLoader()

# Funciones de conveniencia para uso directo
def load_sql_script(script_path: str) -> str:
    """Función de conveniencia para cargar script SQL."""
    return sql_script_loader.load_script(script_path)

def load_sql_script_with_params(script_path: str, params: Dict[str, str]) -> str:
    """Función de conveniencia para cargar script SQL con parámetros."""
    return sql_script_loader.load_script_with_params(script_path, params)

def list_sql_scripts(module_path: str = None) -> List[str]:
    """Función de conveniencia para listar scripts SQL."""
    return sql_script_loader.list_scripts(module_path)