#!/usr/bin/env python3
"""
Migración masiva de print statements a logging centralizado
Prioriza archivos críticos de producción
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

def migrate_prints_to_logging(file_path: Path) -> Tuple[bool, int]:
    """
    Migra print statements a logging en un archivo específico.
    
    Returns:
        Tuple[bool, int]: (éxito, número de prints migrados)
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        
        # Patrones de print a reemplazar
        patterns = [
            # print("[ERROR] ...") -> logger.error("...")
            (r'print\s*\(\s*f?["\']?\[ERROR\]\s*([^"\']*)["\']?\s*\)', r'logger.error(\1)'),
            (r'print\s*\(\s*f?["\']?\[WARN\]\s*([^"\']*)["\']?\s*\)', r'logger.warning(\1)'),
            (r'print\s*\(\s*f?["\']?\[WARNING\]\s*([^"\']*)["\']?\s*\)', r'logger.warning(\1)'),
            (r'print\s*\(\s*f?["\']?\[INFO\]\s*([^"\']*)["\']?\s*\)', r'logger.info(\1)'),
            (r'print\s*\(\s*f?["\']?\[DEBUG\]\s*([^"\']*)["\']?\s*\)', r'logger.debug(\1)'),
            
            # Casos específicos comunes
            (r'print\s*\(\s*f?"Error ([^\"]*)"', r'logger.error(f"Error \1")'),
            (r'print\s*\(\s*f?"Advertencia ([^\"]*)"', r'logger.warning(f"Advertencia \1")'),
            (r'print\s*\(\s*f?"Iniciando ([^\"]*)"', r'logger.info(f"Iniciando \1")'),
            (r'print\s*\(\s*f?"Cargando ([^\"]*)"', r'logger.info(f"Cargando \1")'),
            (r'print\s*\(\s*f?"Guardando ([^\"]*)"', r'logger.info(f"Guardando \1")'),
            (r'print\s*\(\s*f?"Creando ([^\"]*)"', r'logger.info(f"Creando \1")'),
            (r'print\s*\(\s*f?"Actualizando ([^\"]*)"', r'logger.info(f"Actualizando \1")'),
            (r'print\s*\(\s*f?"Eliminando ([^\"]*)"', r'logger.info(f"Eliminando \1")'),
            (r'print\s*\(\s*f?"Conectando ([^\"]*)"', r'logger.info(f"Conectando \1")'),
            (r'print\s*\(\s*f?"Verificando ([^\"]*)"', r'logger.debug(f"Verificando \1")'),
            (r'print\s*\(\s*f?"Validando ([^\"]*)"', r'logger.debug(f"Validando \1")'),
        ]
        
        migrations_made = 0
        
        for pattern, replacement in patterns:
            new_content, count = re.subn(pattern, replacement, content, flags=re.IGNORECASE)
            if count > 0:
                content = new_content
                migrations_made += count
        
        # Solo escribir si hubo cambios
        if content != original_content:
            # Verificar si ya tiene logger importado
            if 'logger' not in content and 'logging' not in content:
                # Agregar import de logger al inicio
                lines = content.split('\n')
                import_added = False
                
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        # Insertar después del último import
                        if i + 1 < len(lines) and not (lines[i+1].startswith('import ') or lines[i+1].startswith('from ')):
                            lines.insert(i + 1, '')
                            lines.insert(i + 2, '# Importar logging centralizado')
                            lines.insert(i + 3, 'try:')
                            lines.insert(i + 4, '    from rexus.utils.app_logger import get_logger')
                            lines.insert(i + 5, f'    logger = get_logger("{file_path.stem}")')
                            lines.insert(i + 6, 'except ImportError:')
                            lines.insert(i + 7, '    import logging')
                            lines.insert(i + 8, f'    logger = logging.getLogger("{file_path.stem}")')
                            lines.insert(i + 9, '')
                            import_added = True
                            break
                
                if import_added:
                    content = '\n'.join(lines)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True, migrations_made
        
        return False, 0
        
    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        return False, 0

def main():
    """Migrar prints en archivos críticos."""
    project_root = Path('.')
    
    # Archivos críticos prioritarios (los que tienen más prints)
    priority_files = [
        'rexus/modules/inventario/model.py',
        'rexus/main/app.py', 
        'rexus/modules/usuarios/model.py',
        'rexus/ui/style_manager.py',
        'rexus/core/module_manager.py',
        'rexus/modules/vidrios/model.py',
        'rexus/modules/usuarios/controller.py',
        'rexus/modules/administracion/contabilidad/model.py',
        'rexus/modules/herrajes/model.py',
        'rexus/core/security.py'
    ]
    
    total_migrations = 0
    files_processed = 0
    
    print("MIGRANDO PRINT STATEMENTS A LOGGING")
    print("=" * 50)
    
    for file_path_str in priority_files:
        file_path = project_root / file_path_str
        
        if file_path.exists():
            print(f"Procesando: {file_path_str}")
            success, migrations = migrate_prints_to_logging(file_path)
            
            if success:
                files_processed += 1
                total_migrations += migrations
                print(f"  OK {migrations} prints migrados")
            else:
                print(f"  - Sin cambios")
        else:
            print(f"  ERROR: Archivo no encontrado: {file_path_str}")
    
    print(f"\nRESUMEN:")
    print(f"Archivos procesados: {files_processed}")
    print(f"Total prints migrados: {total_migrations}")
    
    return total_migrations

if __name__ == '__main__':
    total = main()
    sys.exit(0)
