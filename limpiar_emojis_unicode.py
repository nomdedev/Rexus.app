#!/usr/bin/env python3
"""
Limpiador de Emojis Unicode - Rexus.app
Reemplaza todos los emojis problemáticos con equivalentes ASCII
"""

import os
import re
from pathlib import Path

def clean_unicode_emojis():
    """Limpia todos los emojis problemáticos del proyecto."""
    
    # Mapa de reemplazos de emojis problemáticos
    emoji_replacements = {
        '❌': '[ERROR]',
        '✅': '[OK]',
        '⚠️': '[WARNING]',
        '⚠': '[WARNING]',
        '🔧': '[TOOL]',
        '🌙': '[DARK]',
        '☀️': '[LIGHT]',
        '🎯': '[TARGET]',
        '✨': '[STAR]',
        '🔥': '[HOT]',
        '🚀': '[ROCKET]',
        '💡': '[IDEA]',
        '🎨': '[ART]',
        '📊': '[CHART]',
        '📁': '[FOLDER]',
        '🛡️': '[SHIELD]',
        '🔒': '[LOCK]',
        '💎': '[GEM]',
        '🏆': '[TROPHY]',
        '💰': '[MONEY]',
        '🎉': '[PARTY]',
        '❓': '[QUESTION]',
        '🔍': '[SEARCH]',
        '📝': '[NOTE]',
        '⭐': '[STAR]',
        '🌟': '[SHINY]'
    }
    
    # Patrones de archivos a procesar
    python_files = []
    
    # Buscar todos los archivos Python
    for root, dirs, files in os.walk('rexus'):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    files_modified = 0
    total_replacements = 0
    
    print(f"Procesando {len(python_files)} archivos Python...")
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            file_replacements = 0
            
            # Aplicar cada reemplazo
            for emoji, replacement in emoji_replacements.items():
                if emoji in content:
                    count = content.count(emoji)
                    content = content.replace(emoji, replacement)
                    file_replacements += count
            
            # Si hubo cambios, guardar el archivo
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                files_modified += 1
                total_replacements += file_replacements
                print(f"  Modificado: {file_path} - {file_replacements} reemplazos")
        
        except Exception as e:
            print(f"  Error procesando {file_path}: {e}")
    
    print(f"\nRESUMEN:")
    print(f"Archivos procesados: {len(python_files)}")
    print(f"Archivos modificados: {files_modified}")
    print(f"Total reemplazos: {total_replacements}")
    
    return files_modified > 0

if __name__ == "__main__":
    print("LIMPIADOR DE EMOJIS UNICODE - REXUS.APP")
    print("=" * 50)
    success = clean_unicode_emojis()
    if success:
        print("\nLIMPIEZA COMPLETADA - Todos los emojis problemáticos han sido reemplazados")
    else:
        print("\nNo se encontraron emojis para limpiar")