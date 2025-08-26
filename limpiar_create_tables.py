#!/usr/bin/env python3
"""
Script para eliminar todas las funciones y código CREATE TABLE de archivos Python.
SOLO para uso en la migración a SQL Server - NO USAR EN PRODUCCIÓN.
"""

import os
import re
import glob

def limpiar_create_tables_python():
    """Elimina código CREATE TABLE de archivos Python."""
    
    # Patrones de archivos a procesar
    archivos_python = [
        "d:/martin/Proyectos/rexus/modules/*/model.py",
        "d:/martin/Proyectos/rexus/modules/*/submodules/*.py",
        "d:/martin/Proyectos/rexus/core/*.py",
        "d:/martin/Proyectos/rexus/utils/*.py"
    ]
    
    total_archivos = 0
    total_cambios = 0
    
    for patron in archivos_python:
        for archivo in glob.glob(patron):
            if os.path.exists(archivo):
                try:
                    with open(archivo, 'r', encoding='utf-8') as f:
                        contenido = f.read()
                    
                    # Guardar original
                    contenido_original = contenido
                    
                    # Patrones a eliminar
                    patrones_eliminar = [
                        # Funciones completas CREATE TABLE
                        r'def crear_tablas?\(.*?\):.*?(?=def|\Z)',
                        # Bloques CREATE TABLE completos
                        r'create_\w*_table\s*=\s*""".*?"""',
                        r'CREATE TABLE.*?;',
                        r'cursor\.execute\(create_\w*_table\)',
                        # Índices CREATE INDEX
                        r'cursor\.execute\("CREATE INDEX.*?"\)',
                    ]
                    
                    for patron in patrones_eliminar:
                        contenido = re.sub(patron, '', contenido, flags=re.DOTALL | re.MULTILINE)
                    
                    # Limpiar líneas vacías excesivas
                    contenido = re.sub(r'\n{3,}', '\n\n', contenido)
                    
                    if contenido != contenido_original:
                        # Hacer backup
                        backup_file = f"{archivo}.backup_{int(time.time())}"
                        with open(backup_file, 'w', encoding='utf-8') as f:
                            f.write(contenido_original)
                        
                        # Escribir archivo limpio
                        with open(archivo, 'w', encoding='utf-8') as f:
                            f.write(contenido)
                        
                        print(f"✅ LIMPIADO: {archivo}")
                        total_cambios += 1
                    
                    total_archivos += 1
                    
                except Exception as e:
                    print(f"❌ ERROR en {archivo}: {e}")
    
    print(f"\n📊 RESUMEN:")
    print(f"   Archivos procesados: {total_archivos}")
    print(f"   Archivos modificados: {total_cambios}")

def eliminar_archivos_sql_create():
    """Elimina archivos .sql que solo crean tablas."""
    
    archivos_sql_create = [
        "d:/martin/Proyectos/sql/*/create_table_*.sql",
        "d:/martin/Proyectos/sql/*/create_*_table.sql",
        "d:/martin/Proyectos/sql/*/*/create_table_*.sql",
    ]
    
    total_eliminados = 0
    
    for patron in archivos_sql_create:
        for archivo in glob.glob(patron):
            try:
                # Verificar que es realmente un archivo CREATE TABLE
                with open(archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read().upper()
                
                if 'CREATE TABLE' in contenido and 'INSERT' not in contenido and 'SELECT' not in contenido:
                    os.remove(archivo)
                    print(f"🗑️  ELIMINADO: {archivo}")
                    total_eliminados += 1
                    
            except Exception as e:
                print(f"❌ ERROR eliminando {archivo}: {e}")
    
    print(f"\n📊 Archivos SQL CREATE TABLE eliminados: {total_eliminados}")

if __name__ == "__main__":
    import time
    
    print("🧹 INICIANDO LIMPIEZA DE CREATE TABLE...")
    print("=" * 50)
    
    # 1. Limpiar archivos Python
    print("\n1️⃣  Limpiando archivos Python...")
    limpiar_create_tables_python()
    
    # 2. Eliminar archivos SQL CREATE
    print("\n2️⃣  Eliminando archivos SQL CREATE TABLE...")
    eliminar_archivos_sql_create()
    
    print("\n✅ LIMPIEZA COMPLETADA")
    print("=" * 50)
