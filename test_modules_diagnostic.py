#!/usr/bin/env python3
"""
Test diagnóstico para identificar problemas en los módulos
"""

import sys
import traceback
from pathlib import Path

# Agregar el directorio del proyecto al path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

def test_module_import(module_name, view_class):
    """Testa la importación de un módulo específico"""
    print(f"\n{'='*50}")
    print(f"TESTING MODULE: {module_name}")
    print(f"{'='*50}")
    
    try:
        # Importar el módulo
        module_path = f"rexus.modules.{module_name}.view"
        print(f"Importing: {module_path}")
        
        module = __import__(module_path, fromlist=[view_class])
        view_cls = getattr(module, view_class)
        
        print(f"[OK] Import successful: {view_class}")
        
        # Intentar instanciar la vista
        print(f"Creating instance of {view_class}...")
        view_instance = view_cls()
        print(f"[OK] Instance creation successful")
        
        # Verificar métodos básicos
        basic_methods = ['init_ui', '__init__']
        for method in basic_methods:
            if hasattr(view_instance, method):
                print(f"[OK] Method '{method}' found")
            else:
                print(f"[WARN] Method '{method}' missing")
        
        return True, None
        
    except ImportError as e:
        print(f"[ERROR] Import Error: {e}")
        print("Traceback:")
        traceback.print_exc()
        return False, f"ImportError: {e}"
        
    except Exception as e:
        print(f"[ERROR] Runtime Error: {e}")
        print("Traceback:")
        traceback.print_exc()
        return False, f"RuntimeError: {e}"

def main():
    """Función principal de pruebas"""
    print("DIAGNÓSTICO DE MÓDULOS REXUS")
    print("="*60)
    
    # Lista de módulos a probar
    modules_to_test = [
        ("administracion", "AdministracionView"),
        ("auditoria", "AuditoriaView"),
        ("compras", "ComprasView"),
        ("configuracion", "ConfiguracionView"),
        ("herrajes", "HerrajesView"),
        ("inventario", "InventarioView"),
        ("logistica", "LogisticaView"),
        ("mantenimiento", "MantenimientoView"),
        ("obras", "ObrasView"),
        ("pedidos", "PedidosView"),
        ("usuarios", "UsuariosView"),
        ("vidrios", "VidriosView"),
    ]
    
    results = []
    
    for module_name, view_class in modules_to_test:
        success, error = test_module_import(module_name, view_class)
        results.append((module_name, view_class, success, error))
    
    # Resumen final
    print(f"\n{'='*60}")
    print("RESUMEN DE RESULTADOS")
    print(f"{'='*60}")
    
    successful = 0
    failed = 0
    
    for module_name, view_class, success, error in results:
        status = "[OK]" if success else "[FAIL]"
        print(f"{module_name:15} | {view_class:20} | {status}")
        if not success:
            print(f"                 | Error: {error}")
        
        if success:
            successful += 1
        else:
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"TOTAL: {len(results)} módulos")
    print(f"EXITOSOS: {successful}")
    print(f"FALLIDOS: {failed}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()