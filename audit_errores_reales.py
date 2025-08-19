#!/usr/bin/env python3
"""
Auditoría de Errores Reales - Rexus.app
Detecta todos los errores que realmente ocurren al ejecutar cada módulo
"""

import sys
import traceback
import importlib
from pathlib import Path

def audit_module(module_path, module_name):
    """Audita un módulo específico y captura errores reales."""
    print(f"\n{'='*60}")
    print(f"[AUDIT] AUDITANDO MODULO: {module_name}")
    print(f"{'='*60}")
    
    errors = []
    
    try:
        # Test 1: Import del modelo
        print(f"* Testing import: {module_path}.model")
        try:
            model_module = importlib.import_module(f"{module_path}.model")
            print("  [OK] Model import OK")
        except Exception as e:
            error = f"❌ MODEL IMPORT ERROR: {str(e)}"
            print(f"  {error}")
            errors.append(error)
        
        # Test 2: Import de la vista
        print(f"✓ Testing import: {module_path}.view")
        try:
            view_module = importlib.import_module(f"{module_path}.view")
            print("  ✅ View import OK")
        except Exception as e:
            error = f"❌ VIEW IMPORT ERROR: {str(e)}"
            print(f"  {error}")
            errors.append(error)
        
        # Test 3: Import del controlador
        print(f"✓ Testing import: {module_path}.controller")
        try:
            controller_module = importlib.import_module(f"{module_path}.controller")
            print("  ✅ Controller import OK")
        except Exception as e:
            error = f"❌ CONTROLLER IMPORT ERROR: {str(e)}"
            print(f"  {error}")
            errors.append(error)
        
        # Test 4: Instanciación del modelo
        if 'model_module' in locals():
            try:
                print("✓ Testing model instantiation")
                model_class = getattr(model_module, f"{module_name.title()}Model", None)
                if model_class:
                    model_instance = model_class()
                    print("  ✅ Model instantiation OK")
                else:
                    error = f"❌ MODEL CLASS NOT FOUND: {module_name.title()}Model"
                    print(f"  {error}")
                    errors.append(error)
            except Exception as e:
                error = f"❌ MODEL INSTANTIATION ERROR: {str(e)}"
                print(f"  {error}")
                errors.append(error)
        
        # Test 5: Instanciación de la vista
        if 'view_module' in locals():
            try:
                print("✓ Testing view instantiation")
                view_classes = [f"{module_name.title()}View", f"{module_name.title()}ModernView", f"{module_name.title()}ViewComplete"]
                view_instance = None
                for view_class_name in view_classes:
                    view_class = getattr(view_module, view_class_name, None)
                    if view_class:
                        view_instance = view_class()
                        print(f"  ✅ View instantiation OK ({view_class_name})")
                        break
                
                if not view_instance:
                    error = f"❌ VIEW CLASS NOT FOUND: tried {view_classes}"
                    print(f"  {error}")
                    errors.append(error)
                    
            except Exception as e:
                error = f"❌ VIEW INSTANTIATION ERROR: {str(e)}"
                print(f"  {error}")
                errors.append(error)
        
        # Test 6: Instanciación del controlador
        if 'controller_module' in locals():
            try:
                print("✓ Testing controller instantiation")
                controller_class = getattr(controller_module, f"{module_name.title()}Controller", None)
                if controller_class:
                    controller_instance = controller_class()
                    print("  ✅ Controller instantiation OK")
                else:
                    error = f"❌ CONTROLLER CLASS NOT FOUND: {module_name.title()}Controller"
                    print(f"  {error}")
                    errors.append(error)
            except Exception as e:
                error = f"❌ CONTROLLER INSTANTIATION ERROR: {str(e)}"
                print(f"  {error}")
                errors.append(error)
    
    except Exception as e:
        error = f"❌ GENERAL MODULE ERROR: {str(e)}"
        print(f"  {error}")
        errors.append(error)
    
    # Resumen del módulo
    if errors:
        print(f"\n❌ MÓDULO {module_name.upper()} - {len(errors)} ERRORES ENCONTRADOS:")
        for i, error in enumerate(errors, 1):
            print(f"   {i}. {error}")
    else:
        print(f"\n✅ MÓDULO {module_name.upper()} - SIN ERRORES CRÍTICOS")
    
    return errors

def main():
    """Función principal de auditoría."""
    print("🔍 AUDITORÍA COMPLETA DE ERRORES REALES - REXUS.APP")
    print("=" * 80)
    
    # Módulos a auditar
    modules = [
        ("rexus.modules.inventario", "inventario"),
        ("rexus.modules.compras", "compras"),  
        ("rexus.modules.administracion", "administracion"),
        ("rexus.modules.auditoria", "auditoria"),
        ("rexus.modules.obras", "obras"),
        ("rexus.modules.pedidos", "pedidos"),
        ("rexus.modules.usuarios", "usuarios"),
        ("rexus.modules.configuracion", "configuracion"),
        ("rexus.modules.herrajes", "herrajes"),
        ("rexus.modules.vidrios", "vidrios"),
        ("rexus.modules.logistica", "logistica"),
        ("rexus.modules.mantenimiento", "mantenimiento")
    ]
    
    all_errors = {}
    
    for module_path, module_name in modules:
        errors = audit_module(module_path, module_name)
        if errors:
            all_errors[module_name] = errors
    
    # Resumen final
    print(f"\n{'='*80}")
    print("📊 RESUMEN FINAL DE ERRORES")
    print(f"{'='*80}")
    
    if all_errors:
        print(f"❌ MÓDULOS CON ERRORES: {len(all_errors)}")
        for module, errors in all_errors.items():
            print(f"\n🔴 {module.upper()}: {len(errors)} errores")
            for i, error in enumerate(errors, 1):
                print(f"   {i}. {error}")
    else:
        print("✅ TODOS LOS MÓDULOS FUNCIONAN CORRECTAMENTE")
    
    print(f"\n📈 ESTADÍSTICAS:")
    print(f"   • Total módulos auditados: {len(modules)}")
    print(f"   • Módulos con errores: {len(all_errors)}")
    print(f"   • Módulos sin errores: {len(modules) - len(all_errors)}")
    
    return all_errors

if __name__ == "__main__":
    try:
        errors = main()
        
        # Escribir resultado a archivo
        with open("audit_results.txt", "w", encoding="utf-8") as f:
            f.write("AUDITORÍA DE ERRORES REALES - REXUS.APP\n")
            f.write("=" * 50 + "\n\n")
            
            if errors:
                for module, module_errors in errors.items():
                    f.write(f"\nMÓDULO: {module.upper()}\n")
                    f.write("-" * 30 + "\n")
                    for i, error in enumerate(module_errors, 1):
                        f.write(f"{i}. {error}\n")
            else:
                f.write("✅ NO SE ENCONTRARON ERRORES CRÍTICOS\n")
        
        print(f"\n💾 Resultados guardados en: audit_results.txt")
        
    except Exception as e:
        print(f"❌ ERROR EN AUDITORÍA: {e}")
        traceback.print_exc()