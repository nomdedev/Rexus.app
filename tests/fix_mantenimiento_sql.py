#!/usr/bin/env python3
"""
Script para refactorizar el módulo de mantenimiento
Externaliza todas las consultas SQL embebidas al sistema SQLQueryManager
"""

import re
from pathlib import Path

def fix_mantenimiento_sql_injection():
    """Refactoriza el modelo de mantenimiento para eliminar SQL injection."""
    
    model_path = Path("rexus/modules/mantenimiento/model.py")
    
    if not model_path.exists():
        print(f"Error: {model_path} no encontrado")
        return
    
    with open(model_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Reemplazos específicos para las consultas más problemáticas
    replacements = [
        # Crear equipo
        (
            r'query = """\s*INSERT INTO.*?"""\s*\.format\([^)]+\)',
            'query = self.sql_manager.get_query("mantenimiento.crear_equipo")',
            re.DOTALL
        ),
        # Actualizar equipo 
        (
            r'query = """\s*UPDATE.*?"""\s*\.format\([^)]+\)',
            'query = self.sql_manager.get_query("mantenimiento.update_equipo")',
            re.DOTALL
        ),
        # Obtener mantenimientos
        (
            r'query = """\s*SELECT.*?mantenimientos.*?"""\s*\.format\([^)]+\)',
            'query = self.sql_manager.get_query("mantenimiento.obtener_mantenimientos_base")',
            re.DOTALL
        ),
        # Estadísticas con format()
        (
            r'"SELECT COUNT\(\*\) FROM \[{}\] WHERE activo = 1"\.format\([^)]+\)',
            'self.sql_manager.get_query("mantenimiento.obtener_estadisticas")'
        ),
        # Cualquier query con triple quotes y format
        (
            r'query = """\s*SELECT.*?"""\s*\.format\([^)]+\)',
            'query = self.sql_manager.get_query("mantenimiento.obtener_equipos_base")',
            re.DOTALL
        )
    ]
    
    modified = False
    
    for pattern, replacement, *flags in replacements:
        flag = flags[0] if flags else 0
        if re.search(pattern, content, flag):
            content = re.sub(pattern, replacement, content, flags=flag)
            modified = True
            print(f"Aplicado reemplazo: {replacement[:50]}...")
    
    # También reemplazar bloques de query más simples
    simple_patterns = [
        (r'query = """[^"]*SELECT[^"]*"""', 'query = self.sql_manager.get_query("mantenimiento.obtener_equipos_base")'),
        (r'query = """[^"]*INSERT[^"]*"""', 'query = self.sql_manager.get_query("mantenimiento.crear_equipo")'),
        (r'query = """[^"]*UPDATE[^"]*"""', 'query = self.sql_manager.get_query("mantenimiento.update_equipo")'),
    ]
    
    for pattern, replacement in simple_patterns:
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            modified = True
            print(f"Aplicado reemplazo simple: {replacement[:50]}...")
    
    if modified:
        # Hacer backup
        backup_path = model_path.with_suffix('.py.backup_sql_fix')
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Escribir archivo modificado
        with open(model_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Modelo de mantenimiento refactorizado")
        print(f"📁 Backup guardado en: {backup_path}")
    else:
        print("ℹ️  No se encontraron patrones SQL para reemplazar")

if __name__ == "__main__":
    fix_mantenimiento_sql_injection()
