#!/usr/bin/env python3
"""
Correcciones Automáticas en Lote - Rexus.app
Aplica correcciones sistemáticas a múltiples archivos
Fecha: 23/08/2025
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple

class BatchCorrector:
    """Aplicador de correcciones automáticas en lote."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.corrections_applied = 0
        self.files_processed = 0
        
    def apply_print_to_logging_corrections(self) -> Dict[str, int]:
        """Aplica correcciones de print a logging en archivos críticos."""
        
        critical_patterns = [
            # Patrones de print statements críticos
            (r'print\(f?\[SECURITY\]([^)]+)\)', r'logger.critical("[SECURITY]"\1)'),
            (r'print\(f?\[ERROR\]([^)]+)\)', r'logger.error("[ERROR]"\1)'),  
            (r'print\(f?\[WARNING\]([^)]+)\)', r'logger.warning("[WARNING]"\1)'),
            (r'print\(f?\[INFO\]([^)]+)\)', r'logger.info("[INFO]"\1)'),
            (r'print\(f?\[DEBUG\]([^)]+)\)', r'logger.debug("[DEBUG]"\1)'),
            
            # Exception handling mejorado
            (r'except Exception as e:\s*print\([^)]+\)', 
             'except Exception as e:\n            logger.exception("Error: %s", e)'),
        ]
        
        # Archivos críticos a procesar
        critical_files = [
            'rexus/core/*.py',
            'rexus/main/*.py', 
            'rexus/modules/*/model.py',
            'rexus/modules/*/controller.py',
            'rexus/ui/style_manager.py'
        ]
        
        results = {
            'files_processed': 0,
            'corrections_applied': 0,
            'errors': []
        }
        
        for pattern in critical_files:
            for file_path in self.project_root.glob(pattern):
                if '.backup' in str(file_path) or '__pycache__' in str(file_path):
                    continue
                    
                try:
                    self._process_file(file_path, critical_patterns, results)
                except Exception as e:
                    results['errors'].append(f"{file_path}: {e}")
                    
        return results
    
    def _process_file(self, file_path: Path, patterns: List[Tuple[str, str]], 
                     results: Dict[str, int]) -> None:
        """Procesa un archivo aplicando los patrones de corrección."""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            original_content = content
            changes_made = 0
            
            # Aplicar cada patrón
            for find_pattern, replace_pattern in patterns:
                matches = re.findall(find_pattern, content)
                if matches:
                    content = re.sub(find_pattern, replace_pattern, content)
                    changes_made += len(matches)
                    
            if changes_made > 0:
                # Asegurar que logger esté importado
                if 'logger' in content and 'from rexus.utils.app_logger import get_logger' not in content:
                    # Buscar línea de imports
                    lines = content.split('\\n')
                    insert_pos = 0
                    
                    for i, line in enumerate(lines):
                        if line.startswith('import ') or line.startswith('from '):
                            insert_pos = i + 1
                            
                    if insert_pos > 0:
                        lines.insert(insert_pos, '')
                        lines.insert(insert_pos + 1, '# Sistema de logging centralizado')
                        lines.insert(insert_pos + 2, 'from rexus.utils.app_logger import get_logger')
                        lines.insert(insert_pos + 3, 'logger = get_logger()')
                        content = '\\n'.join(lines)
                        
                # Escribir archivo corregido
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                    
                results['corrections_applied'] += changes_made
                print(f"[BATCH] Corregido {file_path}: {changes_made} cambios")
                
            results['files_processed'] += 1
            
        except Exception as e:
            print(f"[BATCH] Error procesando {file_path}: {e}")
            raise
    
    def fix_common_syntax_errors(self) -> Dict[str, int]:
        """Corrige errores de sintaxis comunes en archivos core."""
        
        syntax_fixes = [
            # Clases faltantes
            (r'^(\s*)def\s+([^(]+)\(self,', r'\\1class TempClass:\\n\\1    def \\2(self,'),
            
            # Indentación incorrecta
            (r'^                    return', r'        return'),
            (r'^                    logger', r'        logger'),
            
            # Except vacíos
            (r'except Exception as e:\s*$', 'except Exception as e:\\n            logger.exception("Error: %s", e)'),
        ]
        
        results = {
            'files_processed': 0,
            'corrections_applied': 0,
            'errors': []
        }
        
        # Procesar archivos core críticos
        for file_path in self.project_root.glob('rexus/core/*.py'):
            if '.backup' in str(file_path):
                continue
                
            try:
                self._process_file(file_path, syntax_fixes, results)
            except Exception as e:
                results['errors'].append(f"{file_path}: {e}")
                
        return results

def main():
    """Función principal de correcciones en lote."""
    print("CORRECTOR AUTOMATICO EN LOTE - Rexus.app")
    print("=" * 50)
    
    current_dir = Path(__file__).parent.parent
    corrector = BatchCorrector(str(current_dir))
    
    # Aplicar correcciones de print a logging
    print("\\nAplicando correcciones print -> logging...")
    print_results = corrector.apply_print_to_logging_corrections()
    
    print(f"Archivos procesados: {print_results['files_processed']}")
    print(f"Correcciones aplicadas: {print_results['corrections_applied']}")
    
    if print_results['errors']:
        print("\\nErrores encontrados:")
        for error in print_results['errors'][:5]:
            print(f"  - {error}")
    
    # Aplicar correcciones de sintaxis
    print("\\nAplicando correcciones de sintaxis...")
    syntax_results = corrector.fix_common_syntax_errors()
    
    print(f"Archivos procesados: {syntax_results['files_processed']}")  
    print(f"Correcciones aplicadas: {syntax_results['corrections_applied']}")
    
    if syntax_results['errors']:
        print("\\nErrores de sintaxis encontrados:")
        for error in syntax_results['errors'][:5]:
            print(f"  - {error}")
    
    total_corrections = print_results['corrections_applied'] + syntax_results['corrections_applied']
    print(f"\\nTOTAL: {total_corrections} correcciones aplicadas")
    
    return 0 if total_corrections > 0 else 1

if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)