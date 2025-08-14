#!/usr/bin/env python3
"""
Diagnóstico completo de errores de runtime en módulos de Rexus.app
Verifica no solo imports sino instanciación y funcionalidad básica
"""

import sys
import os
import traceback
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_module_runtime(module_name):
    """Prueba runtime completo de un módulo incluyendo instanciación."""
    errors = []
    warnings = []

    try:
        print(f"\n🔍 Testeando módulo: {module_name}")

        # 1. Test de import básico
        try:
            view_module = __import__(f'rexus.modules.{module_name}.view', fromlist=[''])
            print(f"  ✅ Import view: OK")
        except Exception as e:
            errors.append(f"Import view falló: {str(e)}")
            return errors, warnings

        try:
            model_module = __import__(f'rexus.modules.{module_name}.model', fromlist=[''])
            print(f"  ✅ Import model: OK")
        except Exception as e:
            errors.append(f"Import model falló: {str(e)}")

        try:
            controller_module = __import__(f'rexus.modules.{module_name}.controller', fromlist=[''])
            print(f"  ✅ Import controller: OK")
        except Exception as e:
            warnings.append(f"Import controller falló: {str(e)}")

        # 2. Test de clases disponibles
        view_classes = [name for name in dir(view_module) if 'View' in name and \
            not name.startswith('_')]
        model_classes = [name for name in dir(model_module) if 'Model' in name and \
            not name.startswith('_')]

        print(f"  📋 Clases view encontradas: {view_classes}")
        print(f"  📋 Clases model encontradas: {model_classes}")

        if not view_classes:
            errors.append("No se encontraron clases View en el módulo")

        if not model_classes:
            warnings.append("No se encontraron clases Model en el módulo")

        # 3. Test de instanciación básica de View (sin DB)
        for view_class_name in view_classes:
            try:
                view_class = getattr(view_module, view_class_name)
                print(f"  🔧 Intentando instanciar {view_class_name}...")

                # Intentar instanciación con parámetros mínimos
                if 'parent' in view_class.__init__.__code__.co_varnames:
                    # Instanciar con parent=None
                    view_instance = view_class(parent=None)
                else:
                    # Instanciar sin parámetros
                    view_instance = view_class()

                print(f"  ✅ Instanciación {view_class_name}: OK")

                # Test de métodos críticos
                critical_methods = ['setup_ui', 'setupUI', 'init_ui', '__init__']
                for method in critical_methods:
                    if hasattr(view_instance, method):
                        print(f"    ✅ Método {method}: disponible")

                # Cleanup
                if hasattr(view_instance, 'deleteLater'):
                    view_instance.deleteLater()

            except Exception as e:
                errors.append(f"Instanciación {view_class_name} falló: {str(e)}")
                print(f"  ❌ Error instanciando {view_class_name}: {str(e)}")

        # 4. Test de dependencias críticas
        critical_imports = [
            'PyQt6.QtWidgets',
            'PyQt6.QtCore',
            'PyQt6.QtGui'
        ]

        for imp in critical_imports:
            try:
                __import__(imp)
                print(f"  ✅ Dependencia {imp}: OK")
            except Exception as e:
                errors.append(f"Dependencia {imp} falló: {str(e)}")

    except Exception as e:
        errors.append(f"Error general en módulo: {str(e)}")
        print(f"  ❌ Error general: {str(e)}")
        traceback.print_exc()

    return errors, warnings

def main():
    """Ejecuta diagnóstico completo de todos los módulos."""
    # Configurar codificación para Windows
    import codecs
    import locale
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

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
    print("📊 RESUMEN DE DIAGNÓSTICO")
    print("=" * 70)

    for module, status in module_status.items():
        status_icon = "✅" if status['status'] == 'OK' else "❌"
        error_count = len(status['errors'])
        warning_count = len(status['warnings'])

        print(f"{status_icon} {module.capitalize()}: {status['status']}")
        if error_count > 0:
            print(f"    🔴 Errores: {error_count}")
            for error in status['errors']:
                print(f"      - {error}")
        if warning_count > 0:
            print(f"    🟡 Advertencias: {warning_count}")
            for warning in status['warnings']:
                print(f"      - {warning}")

    print(f"\n📈 ESTADÍSTICAS TOTALES:")
    print(f"   🔴 Total errores: {total_errors}")
    print(f"   🟡 Total advertencias: {total_warnings}")
    print(f"   ✅ Módulos funcionales: {sum(1 for s in module_status.values() if s['status'] == 'OK')}")
    print(f"   ❌ Módulos con errores: {sum(1 for s in module_status.values() if s['status'] == 'ERROR')}")

    if total_errors == 0:
        print("\n🎉 ¡TODOS LOS MÓDULOS ESTÁN FUNCIONANDO CORRECTAMENTE!")
    else:
        print(f"\n⚠️  SE ENCONTRARON {total_errors} ERRORES QUE REQUIEREN ATENCIÓN")

    return total_errors == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
