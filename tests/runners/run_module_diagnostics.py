#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Diagnóstico de Módulos - Rexus.app
Identifica módulos con problemas de inicialización
"""

import sys
import os
import traceback
from pathlib import Path

# Configurar path y encoding
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
os.environ['PYTHONIOENCODING'] = 'utf-8'

def test_module_import(module_path, module_name):
    """Test de importación de un módulo específico."""
    try:
        module = __import__(module_path, fromlist=[module_name])
        return True, "OK"
    except ImportError as e:
        return False, f"ImportError: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def test_module_instantiation(module_path, class_name):
    """Test de instanciación de una clase del módulo."""
    try:
        module = __import__(module_path, fromlist=[class_name])
        class_obj = getattr(module, class_name)
        # Intentar crear instancia sin parámetros
        instance = class_obj()
        return True, "OK"
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    """Ejecutar diagnóstico completo de módulos."""
    print("=" * 80)
    print("DIAGNÓSTICO DE MÓDULOS - REXUS.APP")
    print("=" * 80)
    
    # Módulos principales a diagnosticar
    modules_to_test = [
        # Format: (module_path, description, class_to_test)
        ("rexus.modules.usuarios.controller", "Usuarios Controller", "UsuariosController"),
        ("rexus.modules.usuarios.model", "Usuarios Model", "UsuariosModel"),
        ("rexus.modules.usuarios.view", "Usuarios View", "UsuariosView"),
        
        ("rexus.modules.inventario.controller", "Inventario Controller", "InventarioController"),
        ("rexus.modules.inventario.model", "Inventario Model", "InventarioModel"),
        ("rexus.modules.inventario.view", "Inventario View", "InventarioView"),
        
        ("rexus.modules.obras.controller", "Obras Controller", "ObrasController"),
        ("rexus.modules.obras.model", "Obras Model", "ObrasModel"),
        ("rexus.modules.obras.view", "Obras View", "ObrasView"),
        
        ("rexus.modules.compras.controller", "Compras Controller", "ComprasController"),
        ("rexus.modules.compras.model", "Compras Model", "ComprasModel"),
        ("rexus.modules.compras.view", "Compras View", "ComprasView"),
        
        ("rexus.modules.pedidos.controller", "Pedidos Controller", "PedidosController"),
        ("rexus.modules.pedidos.model", "Pedidos Model", "PedidosModel"),
        ("rexus.modules.pedidos.view", "Pedidos View", "PedidosView"),
        
        ("rexus.modules.vidrios.controller", "Vidrios Controller", "VidriosController"),
        ("rexus.modules.vidrios.model", "Vidrios Model", "VidriosModel"),
        ("rexus.modules.vidrios.view", "Vidrios View", "VidriosView"),
        
        ("rexus.modules.notificaciones.controller", "Notificaciones Controller", "NotificacionesController"),
        ("rexus.modules.notificaciones.model", "Notificaciones Model", "NotificacionesModel"),
        ("rexus.modules.notificaciones.view", "Notificaciones View", None),
        
        ("rexus.modules.configuracion.controller", "Configuración Controller", "ConfiguracionController"),
        ("rexus.modules.configuracion.model", "Configuración Model", "ConfiguracionModel"),
        ("rexus.modules.configuracion.view", "Configuración View", "ConfiguracionView"),
    ]
    
    results = {
        'importable': [],
        'not_importable': [],
        'instantiable': [],
        'not_instantiable': []
    }
    
    print(f"\nProbando importación de {len(modules_to_test)} módulos...\n")
    
    for module_path, description, class_name in modules_to_test:
        print(f"Testing {description}:")
        print(f"  Module: {module_path}")
        
        # Test 1: Importación
        can_import, import_msg = test_module_import(module_path, class_name or "")
        if can_import:
            results['importable'].append((module_path, description))
            print(f"  ✅ Import: {import_msg}")
        else:
            results['not_importable'].append((module_path, description, import_msg))
            print(f"  ❌ Import: {import_msg}")
        
        # Test 2: Instanciación (solo si se puede importar y hay clase definida)
        if can_import and class_name:
            can_instantiate, instantiate_msg = test_module_instantiation(module_path, class_name)
            if can_instantiate:
                results['instantiable'].append((module_path, description))
                print(f"  ✅ Instantiate: {instantiate_msg}")
            else:
                results['not_instantiable'].append((module_path, description, instantiate_msg))
                print(f"  ❌ Instantiate: {instantiate_msg}")
        elif class_name:
            print(f"  ⏭️  Instantiate: Skipped (import failed)")
        else:
            print(f"  ⏭️  Instantiate: Skipped (no class specified)")
        
        print()
    
    # Resumen de resultados
    print("=" * 80)
    print("RESUMEN DE DIAGNÓSTICO")
    print("=" * 80)
    
    print(f"✅ MÓDULOS IMPORTABLES: {len(results['importable'])}")
    for module_path, description in results['importable']:
        print(f"   - {description}")
    
    print(f"\n❌ MÓDULOS NO IMPORTABLES: {len(results['not_importable'])}")
    for module_path, description, error in results['not_importable']:
        print(f"   - {description}: {error}")
    
    print(f"\n✅ MÓDULOS INSTANCIABLES: {len(results['instantiable'])}")
    for module_path, description in results['instantiable']:
        print(f"   - {description}")
    
    print(f"\n❌ MÓDULOS NO INSTANCIABLES: {len(results['not_instantiable'])}")
    for module_path, description, error in results['not_instantiable']:
        print(f"   - {description}: {error}")
    
    # Estadísticas finales
    total_modules = len(modules_to_test)
    importable_count = len(results['importable'])
    instantiable_count = len(results['instantiable'])
    
    print(f"\n📊 ESTADÍSTICAS FINALES:")
    print(f"   Total módulos probados: {total_modules}")
    print(f"   Módulos importables: {importable_count} ({(importable_count/total_modules)*100:.1f}%)")
    print(f"   Módulos instanciables: {instantiable_count} ({(instantiable_count/total_modules)*100:.1f}%)")
    
    success_rate = (instantiable_count / total_modules) * 100
    if success_rate >= 80:
        print(f"   🎉 Estado: BUENO ({success_rate:.1f}% funcional)")
    elif success_rate >= 60:
        print(f"   ⚠️  Estado: REGULAR ({success_rate:.1f}% funcional)")
    else:
        print(f"   🚨 Estado: CRÍTICO ({success_rate:.1f}% funcional)")
    
    print("\n" + "=" * 80)
    
    # Recomendaciones
    print("RECOMENDACIONES DE CORRECCIÓN:")
    print("=" * 80)
    
    if results['not_importable']:
        print("🔧 PRIORIDAD ALTA - Arreglar importaciones:")
        for module_path, description, error in results['not_importable']:
            if "ModuleNotFoundError" in error:
                print(f"   - {description}: Módulo no existe o path incorrecto")
            elif "ImportError" in error:
                print(f"   - {description}: Dependencia faltante o error de sintaxis")
            else:
                print(f"   - {description}: Error desconocido")
    
    if results['not_instantiable']:
        print("\n🔧 PRIORIDAD MEDIA - Arreglar constructores:")
        for module_path, description, error in results['not_instantiable']:
            if "__init__" in error:
                print(f"   - {description}: Constructor requiere parámetros o tiene errores")
            elif "database" in error.lower():
                print(f"   - {description}: Problema de conexión a base de datos")
            else:
                print(f"   - {description}: Error de inicialización")
    
    print("\n🎯 PRÓXIMOS PASOS:")
    print("1. Arreglar módulos no importables (CRÍTICO)")
    print("2. Solucionar problemas de instanciación")
    print("3. Crear tests unitarios para módulos funcionales")
    print("4. Implementar mejoras visuales (especialmente Compras)")
    
    return results

if __name__ == "__main__":
    results = main()