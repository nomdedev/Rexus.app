#!/usr/bin/env python3
"""
MIT License

Copyright (c) 2024 Rexus.app

Script para corregir propiedades CSS no soportadas por Qt
"""

import re
import os
from pathlib import Path
from typing import List, Tuple


def find_and_fix_transform_properties(content: str) -> Tuple[str, int]:
    """
    Encuentra y elimina propiedades transform no soportadas por Qt.
    
    Args:
        content: Contenido del archivo
        
    Returns:
        Tuple con contenido corregido y número de correcciones
    """
    # Patrón para encontrar líneas con transform
    transform_pattern = r'(\s*)transform:\s*[^;]+;?\s*\n'
    
    matches = list(re.finditer(transform_pattern, content, re.MULTILINE | re.IGNORECASE))
    
    if not matches:
        return content, 0
    
    # Reemplazar todas las propiedades transform
    fixed_content = content
    for match in reversed(matches):  # Reverso para mantener índices válidos
        # Reemplazar con comentario explicativo
        indent = match.group(1)
        replacement = f"{indent}/* transform no soportado en Qt - removido */\n"
        fixed_content = fixed_content[:match.start()] + replacement + fixed_content[match.end():]
    
    return fixed_content, len(matches)


def find_and_fix_box_shadow_properties(content: str) -> Tuple[str, int]:
    """
    Encuentra y comenta propiedades box-shadow no soportadas por Qt.
    
    Args:
        content: Contenido del archivo
        
    Returns:
        Tuple con contenido corregido y número de correcciones
    """
    # Patrón para encontrar líneas con box-shadow
    box_shadow_pattern = r'(\s*)box-shadow:\s*[^;]+;?\s*\n'
    
    matches = list(re.finditer(box_shadow_pattern, content, re.MULTILINE | re.IGNORECASE))
    
    if not matches:
        return content, 0
    
    # Reemplazar todas las propiedades box-shadow
    fixed_content = content
    for match in reversed(matches):  # Reverso para mantener índices válidos
        # Reemplazar con comentario explicativo
        indent = match.group(1)
        replacement = f"{indent}/* box-shadow no soportado en Qt - usar QGraphicsDropShadowEffect */\n"
        fixed_content = fixed_content[:match.start()] + replacement + fixed_content[match.end():]
    
    return fixed_content, len(matches)


def find_and_fix_row_height_properties(content: str) -> Tuple[str, int]:
    """
    Encuentra y elimina propiedades row-height no soportadas por Qt.
    
    Args:
        content: Contenido del archivo
        
    Returns:
        Tuple con contenido corregido y número de correcciones
    """
    # Patrón para encontrar líneas con row-height
    row_height_pattern = r'(\s*)row-height:\s*[^;]+;?\s*\n'
    
    matches = list(re.finditer(row_height_pattern, content, re.MULTILINE | re.IGNORECASE))
    
    if not matches:
        return content, 0
    
    # Reemplazar todas las propiedades row-height
    fixed_content = content
    for match in reversed(matches):  # Reverso para mantener índices válidos
        # Reemplazar con comentario explicativo
        indent = match.group(1)
        replacement = f"{indent}/* row-height no soportado en Qt - removido */\n"
        fixed_content = fixed_content[:match.start()] + replacement + fixed_content[match.end():]
    
    return fixed_content, len(matches)


def fix_file_css_properties(file_path: Path) -> dict:
    """
    Corrige las propiedades CSS no soportadas en un archivo.
    
    Args:
        file_path: Path al archivo a corregir
        
    Returns:
        Dict con estadísticas de correcciones
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        total_fixes = 0
        
        # Corregir transform
        content, transform_fixes = find_and_fix_transform_properties(content)
        total_fixes += transform_fixes
        
        # Corregir box-shadow
        content, box_shadow_fixes = find_and_fix_box_shadow_properties(content)
        total_fixes += box_shadow_fixes
        
        # Corregir row-height
        content, row_height_fixes = find_and_fix_row_height_properties(content)
        total_fixes += row_height_fixes
        
        # Solo escribir si hay cambios
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return {
            'file': str(file_path),
            'transform_fixes': transform_fixes,
            'box_shadow_fixes': box_shadow_fixes,
            'row_height_fixes': row_height_fixes,
            'total_fixes': total_fixes,
            'modified': content != original_content
        }
        
    except Exception as e:
        return {
            'file': str(file_path),
            'error': str(e),
            'modified': False,
            'total_fixes': 0
        }


def scan_and_fix_css_properties(root_path: Path) -> dict:
    """
    Escanea y corrige propiedades CSS no soportadas en todos los archivos Python.
    
    Args:
        root_path: Directorio raíz para escanear
        
    Returns:
        Dict con estadísticas globales
    """
    stats = {
        'files_scanned': 0,
        'files_modified': 0,
        'total_transform_fixes': 0,
        'total_box_shadow_fixes': 0,
        'total_row_height_fixes': 0,
        'total_fixes': 0,
        'errors': [],
        'modified_files': []
    }
    
    # Buscar archivos Python
    python_files = list(root_path.rglob('*.py'))
    
    print(f"Escaneando {len(python_files)} archivos Python...")
    
    for file_path in python_files:
        # Saltar archivos de backup
        if 'backup' in str(file_path).lower():
            continue
            
        stats['files_scanned'] += 1
        result = fix_file_css_properties(file_path)
        
        if 'error' in result:
            stats['errors'].append(result)
            print(f"ERROR en {file_path}: {result['error']}")
        elif result['modified']:
            stats['files_modified'] += 1
            stats['total_transform_fixes'] += result['transform_fixes']
            stats['total_box_shadow_fixes'] += result['box_shadow_fixes']
            stats['total_row_height_fixes'] += result['row_height_fixes']
            stats['total_fixes'] += result['total_fixes']
            stats['modified_files'].append(result)
            
            print(f"OK {file_path.name}: {result['total_fixes']} correcciones")
    
    return stats


def main():
    """Función principal."""
    print("=" * 80)
    print("CORRECTOR DE PROPIEDADES CSS NO SOPORTADAS - REXUS.APP")
    print("=" * 80)
    
    # Obtener directorio raíz del proyecto
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent.parent
    rexus_path = project_root / 'rexus'
    
    print(f"Directorio del proyecto: {project_root}")
    print(f"Directorio rexus: {rexus_path}")
    
    if not rexus_path.exists():
        print(f"ERROR: Directorio rexus no encontrado en {rexus_path}")
        return 1
    
    # Ejecutar correcciones
    print("\nIniciando correcciones...")
    stats = scan_and_fix_css_properties(rexus_path)
    
    # Mostrar resultados
    print("\n" + "=" * 50)
    print("RESUMEN DE CORRECCIONES")
    print("=" * 50)
    
    print(f"Archivos escaneados: {stats['files_scanned']}")
    print(f"Archivos modificados: {stats['files_modified']}")
    print(f"Total de correcciones: {stats['total_fixes']}")
    
    if stats['total_fixes'] > 0:
        print("\nDetalle de correcciones:")
        print(f"   Transform eliminadas: {stats['total_transform_fixes']}")
        print(f"   Box-shadow comentadas: {stats['total_box_shadow_fixes']}")
        print(f"   Row-height eliminadas: {stats['total_row_height_fixes']}")
    
    if stats['modified_files']:
        print("\nArchivos modificados:")
        for result in stats['modified_files']:
            filename = Path(result['file']).name
            print(f"   {filename}: {result['total_fixes']} correcciones")
    
    if stats['errors']:
        print("\nErrores encontrados:")
        for error in stats['errors']:
            filename = Path(error['file']).name
            print(f"   {filename}: {error['error']}")
    
    print("\n" + "=" * 50)
    
    if stats['total_fixes'] > 0:
        print("Correcciones completadas exitosamente!")
        print("Todas las propiedades CSS no soportadas han sido corregidas.")
        print("Se recomienda ejecutar tests para verificar que todo funciona correctamente.")
    else:
        print("No se encontraron propiedades CSS no soportadas.")
        print("El codigo ya esta limpio y compatible con Qt.")
    
    return 0 if not stats['errors'] else 1


if __name__ == "__main__":
    exit(main())