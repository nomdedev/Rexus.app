#!/usr/bin/env python3
"""
Script para corrección masiva de problemas de indentación
Etapa 1 del Plan Sistemático de Corrección
"""

import os
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IndentationFixer:
    def __init__(self):
        self.files_fixed = 0
        self.total_lines_fixed = 0
        self.errors_found = []
        
    def detect_indentation_type(self, content):
        """Detecta si el archivo usa tabs o espacios y cuántos."""
        lines = content.split('\n')
        tab_count = 0
        space_count = 0
        space_sizes = {}
        
        for line in lines:
            if line.strip() and line.startswith(' '):
                # Contar espacios al inicio
                spaces = len(line) - len(line.lstrip(' '))
                if spaces > 0:
                    space_count += 1
                    space_sizes[spaces] = space_sizes.get(spaces, 0) + 1
            elif line.startswith('\t'):
                tab_count += 1
        
        # Determinar el tipo predominante
        if tab_count > space_count:
            return 'tabs', 1
        elif space_sizes:
            # Encontrar el tamaño de indentación más común
            most_common_size = max(space_sizes.items(), key=lambda x: x[1])[0]
            # Normalizar a múltiplos comunes (2, 4, 8)
            if most_common_size <= 2:
                return 'spaces', 2
            elif most_common_size <= 4:
                return 'spaces', 4
            else:
                return 'spaces', 8
        else:
            return 'spaces', 4  # Default
    
    def fix_mixed_indentation(self, content):
        """Corrige indentación mixta (tabs + espacios)."""
        indent_type, indent_size = self.detect_indentation_type(content)
        lines = content.split('\n')
        fixed_lines = []
        changes_made = 0
        
        for i, line in enumerate(lines):
            if not line.strip():  # Línea vacía
                fixed_lines.append('')
                continue
                
            # Detectar indentación actual
            original_line = line
            content_start = len(line) - len(line.lstrip())
            line_content = line.lstrip()
            
            if content_start > 0:
                # Calcular nivel de indentación
                # Convertir tabs a espacios para análisis
                normalized = line[:content_start].expandtabs(4)
                indent_level = len(normalized) // indent_size
                
                # Aplicar indentación consistente
                if indent_type == 'tabs':
                    new_indent = '\t' * indent_level
                else:
                    new_indent = ' ' * (indent_level * indent_size)
                
                fixed_line = new_indent + line_content
                
                if fixed_line != original_line:
                    changes_made += 1
                    logger.debug(f"Línea {i+1}: '{original_line[:20]}...' → '{fixed_line[:20]}...'")
                
                fixed_lines.append(fixed_line)
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines), changes_made
    
    def fix_unexpected_indent(self, content):
        """Corrige indentaciones inesperadas específicas."""
        lines = content.split('\n')
        fixed_lines = []
        changes_made = 0
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Detectar líneas con indentación inesperada al inicio de archivo/función
            if (line.strip() and 
                line.startswith('    ') and 
                i > 0 and 
                not lines[i-1].strip().endswith(':')):
                
                # Verificar si es realmente una indentación incorrecta
                prev_line = lines[i-1].strip() if i > 0 else ""
                
                # Si la línea anterior no requiere indentación, quitar indent
                if not any(prev_line.endswith(x) for x in [':', 'try', 'except', 'if', 'elif', 'else', 'for', 'while', 'with', 'def', 'class']):
                    fixed_lines.append(line.lstrip())
                    changes_made += 1
                    logger.debug(f"Removed unexpected indent at line {i+1}")
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
            
            i += 1
        
        return '\n'.join(fixed_lines), changes_made
    
    def fix_file(self, filepath):
        """Corrige un archivo específico."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Aplicar correcciones
            content = original_content
            total_changes = 0
            
            # 1. Corregir indentación mixta
            content, changes1 = self.fix_mixed_indentation(content)
            total_changes += changes1
            
            # 2. Corregir indentaciones inesperadas
            content, changes2 = self.fix_unexpected_indent(content)
            total_changes += changes2
            
            # Solo escribir si hay cambios
            if total_changes > 0:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.files_fixed += 1
                self.total_lines_fixed += total_changes
                logger.info(f"✅ Corregido: {filepath} ({total_changes} líneas)")
                return True
            else:
                logger.debug(f"⏭️  Sin cambios: {filepath}")
                return False
                
        except Exception as e:
            error_msg = f"❌ Error procesando {filepath}: {e}"
            logger.error(error_msg)
            self.errors_found.append(error_msg)
            return False
    
    def fix_directory(self, directory_path):
        """Corrige todos los archivos .py en un directorio."""
        directory = Path(directory_path)
        
        # Buscar archivos .py recursivamente
        python_files = list(directory.rglob('*.py'))
        
        logger.info(f"🔍 Encontrados {len(python_files)} archivos Python en {directory}")
        
        for filepath in python_files:
            self.fix_file(str(filepath))
        
        # Reporte final
        logger.info("\n📊 REPORTE DE CORRECCIÓN DE INDENTACIÓN:")
        logger.info(f"✅ Archivos corregidos: {self.files_fixed}")
        logger.info(f"📝 Total líneas corregidas: {self.total_lines_fixed}")
        logger.info(f"❌ Errores encontrados: {len(self.errors_found)}")
        
        if self.errors_found:
            logger.info("\n🚨 Errores detallados:")
            for error in self.errors_found:
                logger.info(f"   {error}")
        
        return self.files_fixed, self.total_lines_fixed

def main():
    """Función principal."""
    logger.info("🚀 Iniciando corrección masiva de indentación...")
    
    # Directorios prioritarios basados en el análisis
    target_directories = [
        'rexus/modules/herrajes',
        'rexus/modules/inventario/submodules',
        'rexus/modules/inventario/dialogs',
        'rexus/modules/administracion',
        'rexus/modules/compras'
    ]
    
    fixer = IndentationFixer()
    total_files = 0
    total_lines = 0
    
    for directory in target_directories:
        if os.path.exists(directory):
            logger.info(f"\n🔧 Procesando directorio: {directory}")
            files, lines = fixer.fix_directory(directory)
            total_files += files
            total_lines += lines
        else:
            logger.warning(f"⚠️  Directorio no encontrado: {directory}")
    
    logger.info("\n🎯 RESUMEN FINAL:")
    logger.info(f"📁 Directorios procesados: {len(target_directories)}")
    logger.info(f"✅ Total archivos corregidos: {total_files}")
    logger.info(f"📝 Total líneas corregidas: {total_lines}")
    
    if total_files > 0:
        logger.info("\n💡 Recomendación: Ejecutar verificación de compilación")
        logger.info("   python -c \"import py_compile, glob; [print('OK:', file) for file in glob.glob('rexus/**/*.py', recursive=True) if py_compile.compile(file, doraise=False)]\"")

if __name__ == "__main__":
    main()
