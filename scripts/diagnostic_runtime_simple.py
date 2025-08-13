#!/usr/bin/env python3
"""
Diagnostico simplificado de errores de runtime en modulos de Rexus.app
"""

import sys
import os
import traceback
from pathlib import Path

# Configurar codificacion para Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Anadir el directorio raiz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_module_runtime(module_name):
    """Prueba runtime completo de un modulo incluyendo instanciacion."""
    errors = []
    warnings = []
    
    try:
        print(f"\nTesteando modulo: {module_name}")
        
        # 1. Test de import basico
        try:
            view_module = __import__(f'rexus.modules.{module_name}.view', fromlist=[''])
            print(f"  OK Import view: OK")
        except Exception as e:
            errors.append(f"Import view fallo: {str(e)}")
            return errors, warnings
            
        try:
            model_module = __import__(f'rexus.modules.{module_name}.model', fromlist=[''])
            print(f"  OK Import model: OK")
        except Exception as e:
            errors.append(f"Import model fallo: {str(e)}")
            
        try:
            controller_module = __import__(f'rexus.modules.{module_name}.controller', fromlist=[''])
            print(f"  OK Import controller: OK")
        except Exception as e:
            warnings.append(f"Import controller fallo: {str(e)}")
        
        # 2. Test de clases disponibles
        view_classes = [name for name in dir(view_module) if 'View' in name and not name.startswith('_')]
        model_classes = [name for name in dir(model_module) if 'Model' in name and not name.startswith('_')]
        
        print(f"  Clases view encontradas: {view_classes}")
        print(f"  Clases model encontradas: {model_classes}")
        
        if not view_classes:
            errors.append("No se encontraron clases View en el modulo")
            
        if not model_classes:
            warnings.append("No se encontraron clases Model en el modulo")
        
        # 3. Test de instanciacion basica de View (sin DB)
        for view_class_name in view_classes:
            try:
                view_class = getattr(view_module, view_class_name)
                print(f"  Intentando instanciar {view_class_name}...")
                
                # Intentar instanciacion con parametros minimos
                if 'parent' in view_class.__init__.__code__.co_varnames:
                    # Instanciar con parent=None
                    view_instance = view_class(parent=None)
                else:
                    # Instanciar sin parametros
                    view_instance = view_class()
                    
                print(f"  OK Instanciacion {view_class_name}: OK")
                
                # Test de metodos criticos
                critical_methods = ['setup_ui', 'setupUI', 'init_ui', '__init__']
                for method in critical_methods:
                    if hasattr(view_instance, method):
                        print(f"    OK Metodo {method}: disponible")
                        
                # Cleanup
                if hasattr(view_instance, 'deleteLater'):
                    view_instance.deleteLater()
                    
            except Exception as e:
                errors.append(f"Instanciacion {view_class_name} fallo: {str(e)}")
                print(f"  ERROR instanciando {view_class_name}: {str(e)}")
        
        # 4. Test de dependencias criticas
        critical_imports = [
            'PyQt6.QtWidgets',
            'PyQt6.QtCore', 
            'PyQt6.QtGui'
        ]
        
        for imp in critical_imports:
            try:
                __import__(imp)
                print(f"  OK Dependencia {imp}: OK")
            except Exception as e:
                errors.append(f"Dependencia {imp} fallo: {str(e)}")
        
    except Exception as e:
        errors.append(f"Error general en modulo: {str(e)}")
        print(f"  ERROR general: {str(e)}")
        traceback.print_exc()
    
    return errors, warnings

def main():
    """Ejecuta diagnostico completo de todos los modulos."""
    print("DIAGNOSTICO COMPLETO DE RUNTIME - Modulos Rexus.app")
    print("=" * 70)
    
    modules = [
        'inventario', 'obras', 'usuarios', 'compras', 'pedidos', 
        'herrajes', 'vidrios', 'logistica', 'auditoria', 
        'configuracion', 'mantenimiento'
    ]
    
    total_errors = 0
    total_warnings = 0
    module_status = {}
    
    for module in modules:
        errors, warnings = test_module_runtime(module)
        module_status[module] = {
            'errors': errors,
            'warnings': warnings,
            'status': 'OK' if not errors else 'ERROR'
        }
        total_errors += len(errors)
        total_warnings += len(warnings)
    
    # Resumen final
    print("\n" + "=" * 70)
    print("RESUMEN DE DIAGNOSTICO")
    print("=" * 70)
    
    for module, status in module_status.items():
        status_icon = "OK" if status['status'] == 'OK' else "ERROR"
        error_count = len(status['errors'])
        warning_count = len(status['warnings'])
        
        print(f"{status_icon} {module.capitalize()}: {status['status']}")
        if error_count > 0:
            print(f"    Errores: {error_count}")
            for error in status['errors']:
                print(f"      - {error}")
        if warning_count > 0:
            print(f"    Advertencias: {warning_count}")
            for warning in status['warnings']:
                print(f"      - {warning}")
    
    print(f"\nESTADISTICAS TOTALES:")
    print(f"   Total errores: {total_errors}")
    print(f"   Total advertencias: {total_warnings}")
    print(f"   Modulos funcionales: {sum(1 for s in module_status.values() if s['status'] == 'OK')}")
    print(f"   Modulos con errores: {sum(1 for s in module_status.values() if s['status'] == 'ERROR')}")
    
    if total_errors == 0:
        print("\nTODOS LOS MODULOS ESTAN FUNCIONANDO CORRECTAMENTE!")
    else:
        print(f"\nSE ENCONTRARON {total_errors} ERRORES QUE REQUIEREN ATENCION")
    
    return total_errors == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)