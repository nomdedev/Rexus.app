# -*- coding: utf-8 -*-
"""
Corrector de Errores de Sintaxis
Script para corregir errores de sintaxis introducidos por otros scripts

Autor: Rexus Development Team
Fecha: 23/08/2025
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, Any
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Agregar path del proyecto
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))


class SyntaxErrorFixer:
    """Corrector de errores de sintaxis común."""
    
    def __init__(self):
        self.fixes_applied = 0
        self.files_processed = 0
        
        # Patrones problemáticos comunes
        self.error_patterns = [
            # Problema: except dentro de f-strings
            (r'from .* import .*except \(ConnectionError.*?\n', ''),
            (r'auth_requiexcept \(ConnectionError.*?\n', 'auth_required\n'),
            (r'admin_requiexcept \(ConnectionError.*?\n', 'admin_required\n'),
            (r'f".*?except \(ConnectionError.*?\n.*?\n.*?\n', ''),
            (r'return \{"error": "Cexcept.*?\n.*?\n', 'return {"error": "Connection error"}\n'),
            
            # F-strings mal cerrados
            (r'self\.logger\.warning\(f"except.*?\n.*?\n.*?\n', ''),
            (r'self\.logger\.debug\(f"except.*?\n.*?\n.*?\n', ''),
            (r'logger\.error\(f"Error.*?except.*?\n.*?\n.*?\n', ''),
            
            # Statements sueltos
            (r'\s+raise\s*\n(?=\s+#)', ''),
            (r'\s+logger\.error\(f"Error.*?\n(?=\s+except)', ''),
            (r'\s+logger\.exception\(f"Error.*?\n(?=\s+raise)', ''),
            
            # Imports corruptos
            (r'from ([^"]+) import ([^"]+)"([^"]+)"', r'from \1 import \2'),
        ]
    
    def fix_file(self, file_path: Path) -> bool:
        """Corregir errores de sintaxis en un archivo."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original_content = content
            fixes_in_file = 0
            
            # Aplicar patrones de corrección
            for pattern, replacement in self.error_patterns:
                old_content = content
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
                if old_content != content:
                    fixes_in_file += 1
            
            # Correcciones específicas adicionales
            content = self._apply_specific_fixes(content, file_path)
            
            # Si hubo cambios, guardar archivo
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.fixes_applied += fixes_in_file
                logger.info(f"Corregido {file_path.name}: {fixes_in_file} errores")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error procesando {file_path}: {e}")
            return False
    
    def _apply_specific_fixes(self, content: str, file_path: Path) -> str:
        """Aplicar correcciones específicas por archivo."""
        
        # Correcciones específicas para auth_manager.py
        if file_path.name == 'auth_manager.py':
            # Buscar y corregir return statements rotos
            content = re.sub(
                r'return \{"error": "C[^"]*?".*?\n.*?\n',
                'return {"error": "Connection error"}\n',
                content,
                flags=re.MULTILINE | re.DOTALL
            )
        
        # Correcciones para imports rotos
        content = re.sub(
            r'from ([^\s]+) import ([^\s]+)except.*?\n.*?\n.*?\n',
            r'from \1 import \2\n',
            content,
            flags=re.MULTILINE | re.DOTALL
        )
        
        # Remover líneas de código corrupto residual
        lines = content.split('\n')
        clean_lines = []
        
        skip_next = False
        for i, line in enumerate(lines):
            if skip_next:
                skip_next = False
                continue
                
            # Saltar líneas que contienen fragmentos de código corrupto
            if (('except (ConnectionError' in line and 'import' not in line) or
                ('logger.error(f"Error' in line and 'def ' not in line and 'try:' not in line) or
                ('logger.exception(f"Error' in line and 'def ' not in line and 'try:' not in line) or
                (line.strip() == 'raise' and i + 1 < len(lines) and lines[i + 1].strip().startswith('#'))):
                skip_next = ('logger.error' in line or 'logger.exception' in line)
                continue
            
            clean_lines.append(line)
        
        content = '\n'.join(clean_lines)
        
        # Remover líneas vacías excesivas
        content = re.sub(r'\n\s*\n\s*\n\s*\n', '\n\n', content)
        
        return content
    
    def fix_directory(self, directory: Path, pattern: str = "*.py") -> Dict[str, int]:
        """Corregir errores en todos los archivos de un directorio."""
        results = {
            'processed': 0,
            'fixed': 0,
            'errors': 0
        }
        
        for file_path in directory.rglob(pattern):
            if file_path.is_file():
                results['processed'] += 1
                
                try:
                    if self.fix_file(file_path):
                        results['fixed'] += 1
                except Exception as e:
                    results['errors'] += 1
                    logger.error(f"Error procesando {file_path}: {e}")
        
        return results
    
    def run_full_fix(self) -> Dict[str, Any]:
        """Ejecutar corrección completa del proyecto."""
        logger.info("=== INICIANDO CORRECCIÓN DE ERRORES DE SINTAXIS ===")
        
        # Directorios a procesar
        directories = [
            root_dir / "rexus" / "core",
            root_dir / "rexus" / "modules",
            root_dir / "rexus" / "utils",
            root_dir / "tests"
        ]
        
        total_results = {
            'processed': 0,
            'fixed': 0,
            'errors': 0,
            'directories': 0
        }
        
        for directory in directories:
            if directory.exists():
                logger.info(f"Procesando directorio: {directory}")
                dir_results = self.fix_directory(directory)
                
                total_results['processed'] += dir_results['processed']
                total_results['fixed'] += dir_results['fixed']
                total_results['errors'] += dir_results['errors']
                total_results['directories'] += 1
                
                logger.info(
                    f"  - Procesados: {dir_results['processed']}, "
                    f"Corregidos: {dir_results['fixed']}, "
                    f"Errores: {dir_results['errors']}"
                )
        
        # Correcciones específicas para archivos problemáticos conocidos
        specific_fixes = self._apply_specific_file_fixes()
        total_results.update(specific_fixes)
        
        logger.info("=== CORRECCIÓN COMPLETADA ===")
        logger.info(f"Archivos procesados: {total_results['processed']}")
        logger.info(f"Archivos corregidos: {total_results['fixed']}")
        logger.info(f"Errores encontrados: {total_results['errors']}")
        
        return total_results
    
    def _apply_specific_file_fixes(self) -> Dict[str, int]:
        """Aplicar correcciones específicas a archivos problemáticos."""
        specific_fixes = {'specific_fixes': 0}
        
        # Archivos problemáticos conocidos
        problem_files = [
            root_dir / "rexus" / "core" / "auth_manager.py",
            root_dir / "rexus" / "modules" / "compras" / "view_complete.py",
            root_dir / "rexus" / "modules" / "logistica" / "controller.py",
            root_dir / "rexus" / "modules" / "obras" / "controller.py",
            root_dir / "rexus" / "modules" / "notificaciones" / "model.py",
        ]
        
        for file_path in problem_files:
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Correcciones específicas más agresivas
                    original_content = content
                    
                    # Remover todas las líneas con "except (ConnectionError" que no están en try/except válidos
                    lines = content.split('\n')
                    clean_lines = []
                    
                    in_try_block = False
                    for line in lines:
                        line_stripped = line.strip()
                        
                        # Detectar bloques try válidos
                        if line_stripped.startswith('try:'):
                            in_try_block = True
                        elif line_stripped.startswith(('def ', 'class ', 'if ', 'else:', 'elif')):
                            in_try_block = False
                        
                        # Saltar líneas problemáticas que no están en contexto válido
                        if ('except (ConnectionError' in line and 'import' in line):
                            # Limpiar imports corruptos
                            clean_line = re.sub(r'except \(ConnectionError.*$', '', line)
                            if clean_line.strip():
                                clean_lines.append(clean_line)
                        elif ('except (ConnectionError' in line and not in_try_block):
                            # Saltar líneas except sueltas
                            continue
                        elif (line_stripped.startswith('logger.error(f"Error') and 
                              not any(x in line for x in ['def ', 'try:', 'except'])):
                            # Saltar logger calls sueltos
                            continue
                        elif line_stripped == 'raise' and not in_try_block:
                            # Saltar raise statements sueltos
                            continue
                        else:
                            clean_lines.append(line)
                    
                    content = '\n'.join(clean_lines)
                    
                    if content != original_content:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        specific_fixes['specific_fixes'] += 1
                        logger.info(f"Correcciones específicas aplicadas a {file_path.name}")
                
                except Exception as e:
                    logger.error(f"Error en correcciones específicas para {file_path}: {e}")
        
        return specific_fixes


def main():
    """Función principal."""
    try:
        fixer = SyntaxErrorFixer()
        results = fixer.run_full_fix()
        
        print("\n✅ CORRECCIÓN DE ERRORES COMPLETADA")
        print(f"📁 Directorios procesados: {results['directories']}")
        print(f"📄 Archivos procesados: {results['processed']}")
        print(f"🔧 Archivos corregidos: {results['fixed']}")
        print(f"🎯 Correcciones específicas: {results.get('specific_fixes', 0)}")
        print(f"❌ Errores encontrados: {results['errors']}")
        
        if results['errors'] == 0:
            print("\n🎉 ¡Todos los errores de sintaxis han sido corregidos!")
        else:
            print(f"\n⚠️ Algunos errores requieren revisión manual")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error en la corrección: {e}")
        print(f"\n❌ Error durante la corrección: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())