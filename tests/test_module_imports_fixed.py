#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para verificar la importación de módulos críticos y dependencias creadas
"""

import sys
import traceback
import os
from pathlib import Path

# Configurar codificación para Windows
if sys.platform == "win32":
    os.system("chcp 65001 >nul")

# Añadir el directorio raíz del proyecto al path
project_root = Path(__file__).parent.parent  # Subir un nivel desde tests/
sys.path.insert(0, str(project_root))

def test_import(module_name, description=""):
    """Función para probar la importación de un módulo"""
    try:
        exec(f"import {module_name}")
        print(f"[OK] {module_name} - Importado correctamente {description}")
        return True
    except ImportError as e:
        print(f"[ERROR] {module_name} - Error de importación: {e} {description}")
        traceback.print_exc()
        return False
    except SyntaxError as e:
        print(f"[ERROR] {module_name} - Error de sintaxis: {e} {description}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"[ERROR] {module_name} - Error inesperado: {e} {description}")
        traceback.print_exc()
        return False

def test_from_import(module_name, items, description=""):
    """Función para probar importaciones específicas desde un módulo"""
    try:
        for item in items:
            exec(f"from {module_name} import {item}")
        print(f"[OK] {module_name} - Importaciones específicas correctas: {', '.join(items)} {description}")
        return True
    except ImportError as e:
        print(f"[ERROR] {module_name} - Error de importación específica: {e} {description}")
        traceback.print_exc()
        return False
    except SyntaxError as e:
        print(f"[ERROR] {module_name} - Error de sintaxis: {e} {description}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"[ERROR] {module_name} - Error inesperado: {e} {description}")
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("FASE 1: VERIFICACION DE IMPORTACION DE MODULOS CRITICOS")
    print("=" * 60)
    
    # Pruebas de dependencias creadas
    print("\n--- DEPENDENCIAS CREADAS ---")
    dependencies = [
        ("rexus.utils.unified_sanitizer", "Sanitizador unificado"),
        ("rexus.utils.sql_script_loader", "Cargador de scripts SQL"),
        ("rexus.core.auth_decorators", "Decoradores de autenticación"),
        ("rexus.utils.logging_config", "Configuración de logs"),
        ("rexus.utils.task_queue", "Cola de tareas"),
        ("rexus.utils.dependency_validator", "Validador de dependencias"),
        ("rexus.utils.two_factor_auth", "Autenticación de dos factores"),
    ]
    
    dep_results = []
    for module, desc in dependencies:
        result = test_import(module, f"({desc})")
        dep_results.append(result)
    
    # Pruebas de módulos principales
    print("\n--- MODULOS PRINCIPALES ---")
    modules = [
        ("rexus.modules.obras", "Gestión de Obras"),
        ("rexus.modules.inventario", "Gestión de Inventario"),
        ("rexus.modules.herrajes", "Gestión de Herrajes"),
        ("rexus.modules.vidrios", "Gestión de Vidrios"),
        ("rexus.modules.logistica", "Gestión de Logística"),
        ("rexus.modules.pedidos", "Gestión de Pedidos"),
        ("rexus.modules.compras", "Gestión de Compras"),
        ("rexus.modules.mantenimiento", "Gestión de Mantenimiento"),
        ("rexus.modules.usuarios", "Gestión de Usuarios"),
        ("rexus.modules.auditoria", "Sistema de Auditoría"),
        ("rexus.modules.configuracion", "Configuración del Sistema"),
        ("rexus.modules.notificaciones", "Sistema de Notificaciones"),
    ]
    
    module_results = []
    for module, desc in modules:
        result = test_import(module, f"({desc})")
        module_results.append(result)
    
    # Pruebas de importaciones específicas críticas
    print("\n--- IMPORTACIONES ESPECIFICAS CRITICAS ---")
    specific_imports = [
        ("rexus.utils.unified_sanitizer", ["sanitize_string", "sanitize_email", "sanitize_sql_identifier"]),
        ("rexus.utils.sql_script_loader", ["SqlScriptLoader"]),  # Clase disponible
        ("rexus.core.auth_decorators", ["auth_required", "admin_required", "audit_log"]),
        ("rexus.utils.logging_config", ["get_logger"]),  # setup_logging no existe como función directa
    ]
    
    specific_results = []
    for module, items in specific_imports:
        result = test_from_import(module, items)
        specific_results.append(result)
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE RESULTADOS")
    print("=" * 60)
    
    total_deps = len(dep_results)
    successful_deps = sum(dep_results)
    
    total_modules = len(module_results)
    successful_modules = sum(module_results)
    
    total_specific = len(specific_results)
    successful_specific = sum(specific_results)
    
    print(f"Dependencias: {successful_deps}/{total_deps} importadas correctamente")
    print(f"Módulos principales: {successful_modules}/{total_modules} importados correctamente")
    print(f"Importaciones específicas: {successful_specific}/{total_specific} correctas")
    
    total_tests = total_deps + total_modules + total_specific
    total_successful = successful_deps + successful_modules + successful_specific
    
    print(f"\nTotal: {total_successful}/{total_tests} pruebas exitosas ({total_successful/total_tests*100:.1f}%)")
    
    if total_successful == total_tests:
        print("\n[EXITO] TODAS LAS IMPORTACIONES FUERON EXITOSAS")
        return True
    else:
        print("\n[ADVERTENCIA] HAY ERRORES DE IMPORTACION QUE NECESITAN CORRECCION")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)