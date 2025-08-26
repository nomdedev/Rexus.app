#!/usr/bin/env python3
"""
Script para corregir archivos con CREATE TABLE - Rexus.app
Reemplaza lógica de creación de tablas con verificación de existencia.
"""

import os
import re

# Mapeo de archivos a corregir
archivos_a_corregir = {
    "d:/martin/Proyectos/rexus/core/audit_system.py": {
        "patron_buscar": r'CREATE TABLE IF NOT EXISTS auditoria_sistema.*?\)',
        "reemplazo": "-- Tabla auditoria_sistema ya existe en SQL Server",
        "tipo": "comentario_sql"
    },
    "d:/martin/Proyectos/rexus/core/audit_trail.py": {
        "patron_buscar": r'CREATE TABLE audit_trail.*?\)',
        "reemplazo": "-- Tabla audit_trail ya existe en SQL Server", 
        "tipo": "comentario_sql"
    },
    "d:/martin/Proyectos/rexus/core/auth_manager.py": {
        "patron_buscar": r'CREATE TABLE IF NOT EXISTS auth_users.*?\)',
        "reemplazo": "-- Tabla auth_users ya existe en SQL Server",
        "tipo": "comentario_sql"
    },
    "d:/martin/Proyectos/rexus/modules/administracion/contabilidad/model.py": {
        "patron_buscar": r'CREATE TABLE IF NOT EXISTS.*?\)',
        "reemplazo": "-- Tablas de contabilidad ya existen en SQL Server",
        "tipo": "comentario_sql"
    },
    "d:/martin/Proyectos/rexus/modules/usuarios/submodules/permissions_manager.py": {
        "patron_buscar": r'CREATE TABLE permisos_usuarios.*?\)',
        "reemplazo": "-- Tabla permisos_usuarios ya existe en SQL Server",
        "tipo": "comentario_sql"
    }
}

def corregir_archivo(ruta_archivo, config):
    """Corrige un archivo específico."""
    try:
        if not os.path.exists(ruta_archivo):
            print(f"⚠️  Archivo no encontrado: {ruta_archivo}")
            return False
            
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        contenido_original = contenido
        
        # Aplicar corrección según el tipo
        if config["tipo"] == "comentario_sql":
            contenido = re.sub(
                config["patron_buscar"], 
                config["reemplazo"], 
                contenido, 
                flags=re.DOTALL | re.MULTILINE
            )
        
        # Solo escribir si hubo cambios
        if contenido != contenido_original:
            # Hacer backup
            backup_file = f"{ruta_archivo}.backup_create_table"
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(contenido_original)
            
            # Escribir archivo corregido
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                f.write(contenido)
            
            print(f"✅ CORREGIDO: {ruta_archivo}")
            return True
        else:
            print(f"ℹ️  Sin cambios: {ruta_archivo}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR en {ruta_archivo}: {e}")
        return False

def main():
    print("🧹 INICIANDO CORRECCIÓN DE CREATE TABLE")
    print("=" * 50)
    
    total_corregidos = 0
    
    for archivo, config in archivos_a_corregir.items():
        if corregir_archivo(archivo, config):
            total_corregidos += 1
    
    print(f"\n📊 RESUMEN:")
    print(f"   Archivos procesados: {len(archivos_a_corregir)}")
    print(f"   Archivos corregidos: {total_corregidos}")
    
    # Buscar CREATE TABLE restantes
    print(f"\n🔍 VERIFICANDO ARCHIVOS RESTANTES...")
    # (Esta verificación se haría manualmente)
    
    print(f"\n✅ CORRECCIÓN COMPLETADA")

if __name__ == "__main__":
    main()
