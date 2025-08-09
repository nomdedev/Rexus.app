#!/usr/bin/env python3
"""
Análisis crítico de errores restantes en el sistema
"""

import os
import re
import glob
from pathlib import Path

def buscar_sql_injection_patterns():
    """Busca patrones peligrosos de SQL injection."""
    print("ANALISIS CRITICO - SQL INJECTION PATTERNS")
    print("=" * 60)
    
    patrones_peligrosos = [
        r'cursor\.execute\([^?]*%[^?]*\)',  # cursor.execute con % formatting
        r'cursor\.execute\([^?]*\+[^?]*\)',  # cursor.execute con concatenación +
        r'cursor\.execute\([^?]*f"[^?]*\)',  # cursor.execute con f-strings
        r'cursor\.execute\([^?]*\.format\([^?]*\)',  # cursor.execute con .format()
    ]
    
    archivos_python = glob.glob("rexus/**/*.py", recursive=True)
    problemas_encontrados = []
    
    for archivo in archivos_python:
        try:
            with open(archivo, 'r', encoding='utf-8', errors='ignore') as f:
                contenido = f.read()
                
            for i, linea in enumerate(contenido.split('\n'), 1):
                for patron in patrones_peligrosos:
                    if re.search(patron, linea):
                        problemas_encontrados.append({
                            'archivo': archivo,
                            'linea': i,
                            'codigo': linea.strip(),
                            'patron': patron
                        })
        except Exception as e:
            print(f"ERROR leyendo {archivo}: {e}")
    
    print(f"Problemas encontrados: {len(problemas_encontrados)}")
    for problema in problemas_encontrados:
        print(f"  - {problema['archivo']}:{problema['linea']}")
        print(f"    {problema['codigo']}")
    
    return problemas_encontrados

def buscar_errores_manejo():
    """Busca errores en manejo de excepciones."""
    print("\nANALISIS CRITICO - MANEJO DE ERRORES")
    print("=" * 60)
    
    patrones_problematicos = [
        r'except:\s*$',  # except: vacío
        r'except Exception:\s*pass',  # except Exception: pass
        r'try:.*except.*print\(',  # try/except que solo hace print
    ]
    
    archivos_python = glob.glob("rexus/**/*.py", recursive=True)
    problemas_encontrados = []
    
    for archivo in archivos_python:
        try:
            with open(archivo, 'r', encoding='utf-8', errors='ignore') as f:
                contenido = f.read()
                
            for i, linea in enumerate(contenido.split('\n'), 1):
                for patron in patrones_problematicos:
                    if re.search(patron, linea):
                        problemas_encontrados.append({
                            'archivo': archivo,
                            'linea': i,
                            'codigo': linea.strip()
                        })
        except Exception as e:
            print(f"ERROR leyendo {archivo}: {e}")
    
    print(f"Problemas encontrados: {len(problemas_encontrados)}")
    for problema in problemas_encontrados[:10]:  # Solo primeros 10
        print(f"  - {problema['archivo']}:{problema['linea']}")
        print(f"    {problema['codigo']}")
    
    return problemas_encontrados

def buscar_imports_problemticos():
    """Busca imports problemáticos o circulares."""
    print("\nANALISIS CRITICO - IMPORTS PROBLEMATICOS")
    print("=" * 60)
    
    patrones_problematicos = [
        r'from \..*import.*\*',  # from .module import *
        r'import sys.*sys\.path',  # Modificación de sys.path
        r'importlib\.import_module',  # Import dinámico
    ]
    
    archivos_python = glob.glob("rexus/**/*.py", recursive=True)
    problemas_encontrados = []
    
    for archivo in archivos_python:
        try:
            with open(archivo, 'r', encoding='utf-8', errors='ignore') as f:
                contenido = f.read()
                
            for i, linea in enumerate(contenido.split('\n'), 1):
                for patron in patrones_problematicos:
                    if re.search(patron, linea):
                        problemas_encontrados.append({
                            'archivo': archivo,
                            'linea': i,
                            'codigo': linea.strip()
                        })
        except Exception as e:
            print(f"ERROR leyendo {archivo}: {e}")
    
    print(f"Problemas encontrados: {len(problemas_encontrados)}")
    for problema in problemas_encontrados[:5]:  # Solo primeros 5
        print(f"  - {problema['archivo']}:{problema['linea']}")
        print(f"    {problema['codigo']}")
    
    return problemas_encontrados

def buscar_hardcoded_credentials():
    """Busca credenciales hardcodeadas."""
    print("\nANALISIS CRITICO - CREDENCIALES HARDCODEADAS")
    print("=" * 60)
    
    patrones_credenciales = [
        r'password\s*=\s*["\'][^"\']+["\']',
        r'pwd\s*=\s*["\'][^"\']+["\']',
        r'api_key\s*=\s*["\'][^"\']+["\']',
        r'secret\s*=\s*["\'][^"\']+["\']',
        r'token\s*=\s*["\'][^"\']+["\']',
    ]
    
    # Excluir archivos de test
    archivos_python = [f for f in glob.glob("rexus/**/*.py", recursive=True) 
                      if 'test' not in f.lower()]
    problemas_encontrados = []
    
    for archivo in archivos_python:
        try:
            with open(archivo, 'r', encoding='utf-8', errors='ignore') as f:
                contenido = f.read()
                
            for i, linea in enumerate(contenido.split('\n'), 1):
                for patron in patrones_credenciales:
                    if re.search(patron, linea.lower()):
                        # Filtrar false positives
                        if not any(fp in linea.lower() for fp in ['example', 'test', 'dummy', 'placeholder']):
                            problemas_encontrados.append({
                                'archivo': archivo,
                                'linea': i,
                                'codigo': linea.strip()
                            })
        except Exception as e:
            print(f"ERROR leyendo {archivo}: {e}")
    
    print(f"Problemas encontrados: {len(problemas_encontrados)}")
    for problema in problemas_encontrados:
        print(f"  - {problema['archivo']}:{problema['linea']}")
        print(f"    {problema['codigo']}")
    
    return problemas_encontrados

def analizar_estructura_modulos():
    """Analiza la estructura de módulos para inconsistencias."""
    print("\nANALISIS CRITICO - ESTRUCTURA DE MODULOS")
    print("=" * 60)
    
    modulos_esperados = [
        'inventario', 'obras', 'usuarios', 'compras', 'pedidos',
        'herrajes', 'vidrios', 'auditoria', 'configuracion', 
        'logistica', 'mantenimiento'
    ]
    
    problemas_estructura = []
    
    for modulo in modulos_esperados:
        ruta_modulo = f"rexus/modules/{modulo}"
        if not os.path.exists(ruta_modulo):
            problemas_estructura.append(f"Módulo {modulo} no existe")
            continue
            
        # Verificar archivos esenciales
        archivos_esenciales = ['__init__.py', 'model.py', 'view.py', 'controller.py']
        for archivo in archivos_esenciales:
            ruta_archivo = os.path.join(ruta_modulo, archivo)
            if not os.path.exists(ruta_archivo):
                problemas_estructura.append(f"Falta {ruta_archivo}")
    
    print(f"Problemas estructura: {len(problemas_estructura)}")
    for problema in problemas_estructura:
        print(f"  - {problema}")
    
    return problemas_estructura

def main():
    """Función principal del análisis."""
    print("ANALISIS CRITICO DE ERRORES RESTANTES - REXUS.APP")
    print("=" * 70)
    
    # Análisis principales
    sql_problems = buscar_sql_injection_patterns()
    error_problems = buscar_errores_manejo()
    import_problems = buscar_imports_problemticos()
    cred_problems = buscar_hardcoded_credentials()
    struct_problems = analizar_estructura_modulos()
    
    # Resumen
    print("\nRESUMEN DE PROBLEMAS CRITICOS")
    print("=" * 70)
    print(f"1. SQL Injection potencial: {len(sql_problems)} problemas")
    print(f"2. Manejo de errores deficiente: {len(error_problems)} problemas")
    print(f"3. Imports problemáticos: {len(import_problems)} problemas") 
    print(f"4. Credenciales hardcodeadas: {len(cred_problems)} problemas")
    print(f"5. Estructura de módulos: {len(struct_problems)} problemas")
    
    total_problemas = len(sql_problems) + len(error_problems) + len(import_problems) + len(cred_problems) + len(struct_problems)
    print(f"\nTOTAL PROBLEMAS CRITICOS: {total_problemas}")
    
    # Prioridades
    if sql_problems:
        print("\nPRIORIDAD ALTA: Corregir patrones SQL injection")
    if cred_problems:
        print("PRIORIDAD ALTA: Eliminar credenciales hardcodeadas")
    if struct_problems:
        print("PRIORIDAD MEDIA: Corregir estructura de módulos")

if __name__ == "__main__":
    main()