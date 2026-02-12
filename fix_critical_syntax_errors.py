#!/usr/bin/env python3
"""
Script para corregir errores críticos de sintaxis en los módulos del sistema.
"""

import re
import os
from pathlib import Path

def fix_fstring_errors(file_path):
    """
    Corrige errores de f-string sin cerrar en un archivo.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Patrón para encontrar f-strings sin cerrar
        # Busca patrones como f"texto {variable}" que no tienen la comilla final
        pattern = r'(f"[^"]*{[^}]*}[^"]*)(?!\s*[,;\)\]\}])(?=\s*$)'
        
        # Reemplazar f-strings sin cerrar
        content = re.sub(pattern, r'\1"', content)
        
        # Patrón específico para errores conocidos
        fixes = [
            # Error en model.py:130
            (r'f"Nombre de tabla contiene caracteres no válidos: {table_name}\s*\)', 
             r'f"Nombre de tabla contiene caracteres no válidos: {table_name}"),
            
            # Error en security_features.py:228
            (r'print\(f"\[ERROR\] Error desbloqueando usuario: {e}\)', 
             r'print(f"[ERROR] Error desbloqueando usuario: {e}")'),
            
            # Error en vidrios/model.py:219
            (r'raise ValueError\(f"Nombre de tabla inválido: {table_name}\)', 
             r'raise ValueError(f"Nombre de tabla inválido: {table_name}")'),
            
            # Error en vidrios/model.py:224
            (r'raise ValueError\(f"Tabla no permitida: {table_name}\)', 
             r'raise ValueError(f"Tabla no permitida: {table_name}")'),
        ]
        
        for pattern, replacement in fixes:
            content = re.sub(pattern, replacement, content)
        
        # Si hubo cambios, guardar el archivo
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Corregido: {file_path}")
            return True
        else:
            print(f"ℹ️  Sin cambios necesarios: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error procesando {file_path}: {e}")
        return False

def main():
    """
    Función principal para corregir errores críticos.
    """
    print("🔧 Iniciando corrección de errores críticos de sintaxis...")
    
    # Archivos críticos a corregir
    critical_files = [
        "rexus/modules/11_usuarios/model.py",
        "rexus/modules/11_usuarios/security_features.py", 
        "rexus/modules/04_vidrios/model.py"
    ]
    
    corrected_count = 0
    
    for file_path in critical_files:
        if os.path.exists(file_path):
            if fix_fstring_errors(file_path):
                corrected_count += 1
        else:
            print(f"⚠️  Archivo no encontrado: {file_path}")
    
    print(f"\n📊 Resumen:")
    print(f"   - Archivos corregidos: {corrected_count}")
    print(f"   - Total archivos procesados: {len(critical_files)}")
    
    if corrected_count > 0:
        print(f"\n✅ Se han corregido errores críticos de sintaxis.")
        print(f"   Los módulos deberían poder ejecutarse ahora.")
    else:
        print(f"\nℹ️  No se encontraron errores críticos para corregir.")

if __name__ == "__main__":
    main()