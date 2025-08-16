#!/usr/bin/env python3
"""
Script para migrar prints a logging automáticamente en múltiples archivos
Acelera la corrección masiva de problemas de logging

Fecha: 15/08/2025
Objetivo: Migrar todos los print() statements a logging centralizado
"""

import os
import re
from pathlib import Path

def migrate_prints_to_logging(file_path):
    """
    Migra prints a logging en un archivo específico.
    """
    print(f"Migrando prints en: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Backup del archivo original
    backup_path = file_path + '.print_backup'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    new_content = content
    
    # 1. Agregar imports de logging si no existen
    if 'from rexus.utils.app_logger import get_logger' not in new_content:
        logging_import = '''
# Importar logging centralizado
try:
    from rexus.utils.app_logger import get_logger
    logger = get_logger("PLACEHOLDER_MODULE")
except ImportError:
    class DummyLogger:
        def info(self, msg): print(f"[INFO] {msg}")
        def warning(self, msg): print(f"[WARNING] {msg}")
        def error(self, msg): print(f"[ERROR] {msg}")
        def debug(self, msg): print(f"[DEBUG] {msg}")
    logger = DummyLogger()
'''
        
        # Buscar el lugar apropiado para insertar
        import_pattern = r'(from PyQt6\.QtCore import [^\n]+)\n'
        if re.search(import_pattern, new_content):
            new_content = re.sub(
                import_pattern,
                r'\1\n' + logging_import + '\n',
                new_content, count=1
            )
    
    # 2. Reemplazar patrones comunes de print
    
    # Prints de error
    new_content = re.sub(
        r'print\(f?"\[ERROR[^\]]*\][^"]*{[^}]+}[^"]*"\)',
        lambda m: m.group(0).replace('print(f"', 'logger.error(f"').replace('print("', 'logger.error("'),
        new_content
    )
    
    # Prints de warning
    new_content = re.sub(
        r'print\(f?"\[WARNING[^\]]*\][^"]*"\)',
        lambda m: m.group(0).replace('print(f"', 'logger.warning(f"').replace('print("', 'logger.warning("'),
        new_content
    )
    
    # Prints informativos con controlador
    new_content = re.sub(
        r'print\(f?"\[[A-Z_]+ CONTROLLER\][^"]*"\)',
        lambda m: m.group(0).replace('print(f"', 'logger.info(f"').replace('print("', 'logger.info("'),
        new_content
    )
    
    # Prints de OK/SUCCESS
    new_content = re.sub(
        r'print\(f?"(?:OK |✓ )[^"]*"\)',
        lambda m: m.group(0).replace('print(f"', 'logger.info(f"').replace('print("', 'logger.info("'),
        new_content
    )
    
    # Prints generales con f-strings que contienen variables
    new_content = re.sub(
        r'print\(f"[^"]*{[^}]+}[^"]*"\)',
        lambda m: m.group(0).replace('print(f"', 'logger.debug(f"'),
        new_content
    )
    
    # Prints generales simples sin formato especial
    new_content = re.sub(
        r'print\("([^"]+)"\)',
        r'logger.info("\1")',
        new_content
    )
    
    # 3. Actualizar el nombre del módulo en el logger
    module_name = Path(file_path).parent.name
    new_content = new_content.replace('get_logger("PLACEHOLDER_MODULE")', f'get_logger("{module_name}.controller")')
    
    # Escribir archivo actualizado
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Migración completada: {file_path}")

def main():
    """Migra prints a logging en múltiples controladores."""
    
    controllers_to_migrate = [
        'rexus/modules/auditoria/controller.py',
        'rexus/modules/configuracion/controller.py',
        'rexus/modules/mantenimiento/controller.py',
        'rexus/modules/notificaciones/controller.py',
        'rexus/modules/administracion/controller.py'
    ]
    
    base_path = Path('.')
    migrated_count = 0
    
    for controller_path in controllers_to_migrate:
        full_path = base_path / controller_path
        
        if full_path.exists():
            try:
                migrate_prints_to_logging(str(full_path))
                migrated_count += 1
            except Exception as e:
                print(f"Error migrando {controller_path}: {e}")
        else:
            print(f"Archivo no encontrado: {controller_path}")
    
    print(f"\nMigración masiva completada! {migrated_count} controladores migrados.")
    print("Se crearon archivos .print_backup para seguridad")

if __name__ == "__main__":
    main()