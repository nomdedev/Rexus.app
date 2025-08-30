#!/usr/bin/env python3
"""
Script para verificar y reparar problemas de import en todos los módulos de Rexus.app
"""

import sys
import os
import subprocess
from pathlib import Path

def test_module_import(module_path, module_name):
    """Prueba importar un módulo específico."""
    print(f"\n🔍 Probando módulo: {module_name}")

    # Validar nombres para prevenir command injection
    import re
    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_.]*$', module_path):
        print(f"❌ {module_name}: NOMBRE DE MÓDULO INVÁLIDO")
        return False

    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_.]*$', module_name):
        print(f"❌ {module_name}: NOMBRE DE MÓDULO INVÁLIDO")
        return False

    # Usar lista de argumentos en lugar de shell=True para seguridad
    cmd = [
        'python', '-c',
        f"import sys; sys.path.append('d:/martin/Proyectos'); from {module_path} import *; print('✅ {module_name} importado correctamente')"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            print(f"✅ {module_name}: IMPORT EXITOSO")
            return True
        else:
            print(f"❌ {module_name}: ERROR DE IMPORT")
            print(f"   Error: {result.stderr.strip()}")
            return False

    except subprocess.TimeoutExpired:
        print(f"⏱️ {module_name}: TIMEOUT")
        return False
    except Exception as e:
        print(f"❌ {module_name}: EXCEPCIÓN - {e}")
        return False

def test_basic_imports():
    """Prueba imports básicos de todos los módulos principales."""
    
    print("🧪 INICIANDO TEST DE IMPORTS DE MÓDULOS")
    print("=" * 60)
    
    # Módulos principales a probar
    modules_to_test = [
        # Módulos básicos
        ("rexus.modules.configuracion.model", "Configuración"),
        ("rexus.modules.auditoria.model", "Auditoría"),
        
        # Módulos restaurados
        ("rexus.modules.herrajes.model", "Herrajes"),
        ("rexus.modules.vidrios.model", "Vidrios"),
        ("rexus.modules.inventario.model", "Inventario"),
        ("rexus.modules.notificaciones.model", "Notificaciones"),
        ("rexus.modules.mantenimiento.model", "Mantenimiento"),
        
        # Módulos complejos
        ("rexus.modules.compras.model", "Compras"),
        ("rexus.modules.logistica.model", "Logística"),
        ("rexus.modules.obras.model", "Obras"),
        ("rexus.modules.pedidos.model", "Pedidos"),
        ("rexus.modules.usuarios.model", "Usuarios"),
    ]
    
    resultados = []
    
    for module_path, module_name in modules_to_test:
        exito = test_module_import(module_path, module_name)
        resultados.append((module_name, exito))
    
    # Resumen
    print("\n📊 RESUMEN DE IMPORTS")
    print("=" * 40)
    
    exitosos = sum(1 for _, exito in resultados if exito)
    total = len(resultados)
    
    print(f"✅ Módulos exitosos: {exitosos}/{total}")
    print(f"❌ Módulos con errores: {total - exitosos}/{total}")
    
    if exitosos == total:
        print("🎉 TODOS LOS MÓDULOS IMPORTAN CORRECTAMENTE")
    else:
        print("\n⚠️  MÓDULOS CON PROBLEMAS:")
        for nombre, exito in resultados:
            if not exito:
                print(f"   ❌ {nombre}")
    
    return exitosos == total

def check_create_table_presence():
    """Verifica que no haya CREATE TABLE en el código."""
    
    print("\n🔍 VERIFICANDO AUSENCIA DE CREATE TABLE")
    print("-" * 50)
    
    base_path = Path("d:/martin/Proyectos/rexus/modules")
    
    found_create_table = False
    
    for py_file in base_path.rglob("*.py"):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Buscar CREATE TABLE (excluyendo comentarios)
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if 'CREATE TABLE' in line.upper() and not line.strip().startswith('#'):
                    print(f"❌ {py_file.relative_to(base_path)} línea {i}: {line.strip()}")
                    found_create_table = True
                    
        except Exception as e:
            print(f"⚠️  Error leyendo {py_file}: {e}")
    
    if not found_create_table:
        print("✅ No se encontraron CREATE TABLE en el código")
    else:
        print("❌ Se encontraron CREATE TABLE en archivos de código")
    
    return not found_create_table

def check_backup_references():
    """Verifica que no haya referencias a backups en el código."""
    
    print("\n🔍 VERIFICANDO AUSENCIA DE REFERENCIAS A BACKUPS")
    print("-" * 50)
    
    base_path = Path("d:/martin/Proyectos/rexus")
    
    found_backup_refs = False
    
    for py_file in base_path.rglob("*.py"):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Buscar referencias a backups
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if 'backups/' in line or 'backup_20' in line:
                    if not line.strip().startswith('#') and 'backup_system' not in line:
                        print(f"❌ {py_file.relative_to(base_path)} línea {i}: {line.strip()}")
                        found_backup_refs = True
                        
        except Exception as e:
            print(f"⚠️  Error leyendo {py_file}: {e}")
    
    if not found_backup_refs:
        print("✅ No se encontraron referencias a backups")
    else:
        print("❌ Se encontraron referencias a backups en el código")
    
    return not found_backup_refs

def main():
    """Función principal del test."""
    
    print("🚀 TEST INTEGRAL DE MÓDULOS REXUS.APP")
    print("=" * 70)
    
    # Cambiar al directorio del proyecto
    os.chdir("d:/martin/Proyectos")
    
    # Ejecutar tests
    imports_ok = test_basic_imports()
    create_table_ok = check_create_table_presence()
    backup_refs_ok = check_backup_references()
    
    # Resultado final
    print("\n🏆 RESULTADO FINAL")
    print("=" * 50)
    
    if imports_ok and create_table_ok and backup_refs_ok:
        print("✅ TODOS LOS TESTS PASARON EXITOSAMENTE")
        print("🎉 El proyecto está en estado óptimo")
        return True
    else:
        print("❌ ALGUNOS TESTS FALLARON")
        print("⚠️  El proyecto necesita correcciones")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
