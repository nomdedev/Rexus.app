#!/usr/bin/env python3
"""
Script para verificar el estado actual de compilación después de las correcciones
"""
import ast
import glob
import os

def verificar_compilacion():
    archivos_python = glob.glob('rexus/**/*.py', recursive=True)
    
    compilados_ok = []
    con_errores = []
    total_archivos = len(archivos_python)
    
    print(f"Verificando {total_archivos} archivos Python...")
    print("=" * 50)
    
    for archivo in archivos_python:
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            # Intentar parsear con AST
            ast.parse(contenido)
            compilados_ok.append(archivo)
            
        except Exception as e:
            con_errores.append((archivo, str(e)))
    
    # Estadísticas
    num_ok = len(compilados_ok)
    num_errores = len(con_errores)
    porcentaje_ok = (num_ok / total_archivos) * 100
    
    print(f"RESULTADO FINAL:")
    print(f"Total archivos: {total_archivos}")
    print(f"Compilan OK: {num_ok} ({porcentaje_ok:.1f}%)")
    print(f"Con errores: {num_errores} ({100-porcentaje_ok:.1f}%)")
    print("=" * 50)
    
    if con_errores:
        print("\nARCHIVOS CON ERRORES:")
        for i, (archivo, error) in enumerate(con_errores[:20], 1):  # Mostrar solo primeros 20
            error_tipo = error.split(':')[0] if ':' in error else error
            print(f"{i:2d}. {archivo}")
            print(f"    ERROR: {error_tipo}")
        
        if len(con_errores) > 20:
            print(f"    ... y {len(con_errores) - 20} archivos más con errores")
    
    print("\n" + "=" * 50)
    print(f"PROGRESO: {num_ok}/{total_archivos} archivos funcionando")
    
    return num_ok, num_errores, total_archivos

if __name__ == "__main__":
    verificar_compilacion()