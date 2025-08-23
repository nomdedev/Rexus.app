#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de corrección automatizada de vulnerabilidades de seguridad - Rexus.app
Corrige los patrones identificados en la auditoría de seguridad
"""

import os
import re
import glob
from pathlib import Path

class SecurityFixer:
    """Automatiza la corrección de vulnerabilidades de seguridad."""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.changes_made = []
        
    def fix_generic_exceptions(self, file_path: Path) -> bool:
        """Corrige excepciones genéricas 'except Exception'."""
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Patrones específicos para diferentes contextos
        patterns = [
            # Operaciones de base de datos
            {
                'pattern': r'except Exception as e:\s*logger\.error\(f?"?Error [^"]*base.*datos[^"]*[^"]*?"\)',
                'replacement': '''except (ConnectionError, ValueError, TypeError) as e:
            logger.error(f"Error de datos/conexión: {e}")
        except Exception as e:
            logger.exception(f"Error inesperado en BD: {e}")
            raise'''
            },
            # Operaciones de archivos/IO
            {
                'pattern': r'except Exception as e:\s*logger\.error\(f?"?Error [^"]*archivo[^"]*[^"]*?"\)',
                'replacement': '''except (FileNotFoundError, PermissionError, OSError) as e:
            logger.error(f"Error de archivo/IO: {e}")
        except Exception as e:
            logger.exception(f"Error inesperado de archivo: {e}")
            raise'''
            },
            # Operaciones de red/API
            {
                'pattern': r'except Exception as e:\s*logger\.error\(f?"?Error [^"]*API|red|conexi[oó]n[^"]*[^"]*?"\)',
                'replacement': '''except (ConnectionError, TimeoutError, ValueError) as e:
            logger.error(f"Error de red/API: {e}")
        except Exception as e:
            logger.exception(f"Error inesperado de red: {e}")
            raise'''
            }
        ]
        
        for pattern_data in patterns:
            content = re.sub(
                pattern_data['pattern'], 
                pattern_data['replacement'], 
                content, 
                flags=re.MULTILINE | re.IGNORECASE
            )
        
        # Cambio genérico más conservativo
        # Solo reemplaza si no hay logger.exception ya presente
        generic_pattern = r'except Exception as e:\s*logger\.error\([^)]+\)\s*(?!.*logger\.exception)'
        
        def replace_generic(match):
            original_log = match.group(0)
            # Extraer el mensaje del logger.error original
            log_match = re.search(r'logger\.error\(([^)]+)\)', original_log)
            if log_match:
                log_msg = log_match.group(1)
                return f'''except Exception as e:
            logger.exception({log_msg})
            # FIXME: Specify concrete exception types instead of generic Exception'''
            return original_log
        
        content = re.sub(generic_pattern, replace_generic, content, flags=re.MULTILINE)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.changes_made.append(f"Fixed generic exceptions in {file_path}")
            return True
        
        return False
    
    def fix_sql_injection_risks(self, file_path: Path) -> bool:
        """Corrige riesgos potenciales de inyección SQL."""
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Buscar patrones peligrosos de concatenación de SQL
        dangerous_patterns = [
            # cursor.execute con concatenación de strings
            r'cursor\.execute\s*\(\s*f"[^"]*{[^}]+}[^"]*"\s*\)',
            r'cursor\.execute\s*\(\s*"[^"]*"\s*\+[^)]+\)',
            r'cursor\.execute\s*\(\s*\'[^\']*\'\s*\+[^)]+\)'
        ]
        
        for pattern in dangerous_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                # Agregar comentario de advertencia
                dangerous_line = match.group(0)
                safe_comment = f"# SECURITY WARNING: Potential SQL injection risk\n        # TODO: Use parameterized queries instead\n        {dangerous_line}"
                content = content.replace(dangerous_line, safe_comment)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.changes_made.append(f"Marked SQL injection risks in {file_path}")
            return True
        
        return False
    
    def fix_print_statements(self, file_path: Path) -> bool:
        """Migra print() statements a logging."""
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Verificar que el archivo tenga import de logging
        if 'import logging' not in content and 'from rexus.utils.app_logger import' not in content:
            # Agregar import al inicio del archivo
            lines = content.split('\n')
            # Buscar después de los docstrings pero antes del primer import
            insert_pos = 0
            for i, line in enumerate(lines):
                if line.strip().startswith('"""') or line.strip().startswith("'''"):
                    # Buscar el final del docstring
                    quote_type = '"""' if '"""' in line else "'''"
                    if line.count(quote_type) == 2:
                        insert_pos = i + 1
                    else:
                        for j in range(i + 1, len(lines)):
                            if quote_type in lines[j]:
                                insert_pos = j + 1
                                break
                elif line.strip().startswith('from ') or line.strip().startswith('import '):
                    insert_pos = i
                    break
            
            lines.insert(insert_pos, '')
            lines.insert(insert_pos + 1, 'import logging')
            lines.insert(insert_pos + 2, 'logger = logging.getLogger(__name__)')
            lines.insert(insert_pos + 3, '')
            content = '\n'.join(lines)
        
        # Reemplazar print statements
        print_patterns = [
            (r'print\s*\(\s*f"([^"]+)"\s*\)', r'logger.info(f"\1")'),
            (r'print\s*\(\s*"([^"]+)"\s*\)', r'logger.info("\1")'),
            (r'print\s*\(\s*f\'([^\']+)\'\s*\)', r'logger.info(f\'\1\')'),
            (r'print\s*\(\s*\'([^\']+)\'\s*\)', r'logger.info(\'\1\')'),
        ]
        
        for pattern, replacement in print_patterns:
            content = re.sub(pattern, replacement, content)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.changes_made.append(f"Migrated print statements to logging in {file_path}")
            return True
        
        return False
    
    def process_directory(self, directory: str, patterns: list = None):
        """Procesa un directorio completo."""
        
        if patterns is None:
            patterns = ["*.py"]
        
        dir_path = self.base_path / directory
        if not dir_path.exists():
            print(f"Directorio {dir_path} no existe")
            return
        
        files_processed = 0
        files_changed = 0
        
        for pattern in patterns:
            for file_path in dir_path.rglob(pattern):
                if file_path.is_file():
                    files_processed += 1
                    
                    changed = False
                    try:
                        # Aplicar todas las correcciones
                        if self.fix_generic_exceptions(file_path):
                            changed = True
                        if self.fix_sql_injection_risks(file_path):
                            changed = True
                        if self.fix_print_statements(file_path):
                            changed = True
                        
                        if changed:
                            files_changed += 1
                            
                    except Exception as e:
                        print(f"Error procesando {file_path}: {e}")
        
        print(f"Procesados {files_processed} archivos en {directory}, {files_changed} modificados")
    
    def generate_report(self) -> str:
        """Genera un reporte de los cambios realizados."""
        
        if not self.changes_made:
            return "No se realizaron cambios."
        
        report = "# Reporte de Correcciones de Seguridad\n\n"
        report += f"Total de cambios: {len(self.changes_made)}\n\n"
        
        for change in self.changes_made:
            report += f"- {change}\n"
        
        report += "\n## Recomendaciones Post-Corrección\n\n"
        report += "1. Revisar los comentarios TODO agregados\n"
        report += "2. Ejecutar tests para validar funcionalidad\n"
        report += "3. Considerar refactoring adicional en archivos grandes\n"
        report += "4. Configurar lint rules para prevenir regresiones\n"
        
        return report


def main():
    """Función principal del script."""
    
    base_dir = Path(__file__).parent.parent
    fixer = SecurityFixer(str(base_dir))
    
    print("Iniciando correcciones de seguridad...")
    
    # Procesar directorios prioritarios
    priority_dirs = [
        "rexus/core",
        "rexus/modules", 
        "rexus/utils",
        "rexus/api"
    ]
    
    for directory in priority_dirs:
        print(f"\nProcesando {directory}...")
        fixer.process_directory(directory)
    
    # Generar reporte
    report = fixer.generate_report()
    
    # Guardar reporte
    report_path = base_dir / "logs" / "security_fixes_report.md"
    report_path.parent.mkdir(exist_ok=True)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nCorrecciones completadas!")
    print(f"Reporte guardado en: {report_path}")
    print(f"\n{report}")


if __name__ == "__main__":
    main()