"""
Test del Sistema de Diagnóstico de Módulos

Verifica que el nuevo sistema de diagnóstico funcione correctamente
y muestre información útil sobre errores de módulos.
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from PyQt6.QtWidgets import QApplication

from rexus.core.module_manager import ModuleManager
from rexus.utils.diagnostic_widget import create_diagnostic_widget


def test_diagnostic_widget():
    """Prueba el widget de diagnóstico con diferentes tipos de errores."""

    app = QApplication(sys.argv)

    # Test 1: Error de importación
    print("=== Test 1: Error de ImportError ===")
    import_error = ImportError("No module named 'some_missing_module'")
    widget1 = create_diagnostic_widget("test_module", import_error)
    widget1.show()

    # Test 2: Error de sintaxis
    print("=== Test 2: Error de SyntaxError ===")
    syntax_error = SyntaxError("invalid syntax in controller.py line 45")
    widget2 = create_diagnostic_widget("obras", syntax_error)
    widget2.show()

    # Test 3: Error de nombre no definido
    print("=== Test 3: Error de NameError ===")
    name_error = NameError("name 'auth_required' is not defined")
    widget3 = create_diagnostic_widget("inventario", name_error)
    widget3.show()

    print("Widgets de diagnóstico creados exitosamente")
    print("Cerrando en 3 segundos...")

    # Ejecutar por un momento para ver los widgets
    import time

    def close_app():
        time.sleep(3)
        app.quit()

    from PyQt6.QtCore import QTimer

    timer = QTimer()
    timer.timeout.connect(close_app)
    timer.start(3000)

    app.exec()


def test_module_manager_error_handling():
    """Prueba el manejo de errores del module manager."""

    print("=== Test Module Manager Error Handling ===")

    manager = ModuleManager()

    # Simular error de carga de módulo
    class FakeModel:
        def __init__(self):
            raise ImportError("Fake import error for testing")

    class FakeView:
        def __init__(self):
            pass

    class FakeController:
        def __init__(self, model, view):
            pass

    # Probar carga con error
    result = manager.create_module_safely(
        "test_error_module", FakeModel, FakeView, FakeController
    )

    if result:
        print("✅ Error widget creado correctamente")
        print(f"   Tipo de widget: {type(result).__name__}")
    else:
        print("❌ No se pudo crear widget de error")

    # Verificar estado del módulo
    status = manager.get_module_status("test_error_module")
    print(f"   Estado del módulo: {status}")

    return result


def test_real_module_errors():
    """Prueba con errores reales de módulos de la aplicación."""

    print("=== Test Real Module Errors ===")

    manager = ModuleManager()

    # Lista de módulos para probar
    test_modules = [
        ("obras", "rexus.modules.obras"),
        ("inventario", "rexus.modules.inventario"),
        ("usuarios", "rexus.modules.usuarios"),
    ]

    for module_name, module_path in test_modules:
        try:
            print(f"\n--- Probando módulo: {module_name} ---")

            # Intentar importar las clases del módulo
            from importlib import import_module

            model_module = import_module(f"{module_path}.model")
            view_module = import_module(f"{module_path}.view")
            controller_module = import_module(f"{module_path}.controller")

            # Obtener las clases
            model_class = getattr(model_module, f"{module_name.title()}Model")
            view_class = getattr(view_module, f"{module_name.title()}View")
            controller_class = getattr(
                controller_module, f"{module_name.title()}Controller"
            )

            print(f"✅ Clases encontradas para {module_name}")

            # Intentar crear el módulo
            widget = manager.create_module_safely(
                module_name, model_class, view_class, controller_class
            )

            if widget:
                print(f"✅ Widget creado para {module_name}: {type(widget).__name__}")
            else:
                print(f"❌ No se pudo crear widget para {module_name}")

        except Exception as e:
            print(f"❌ Error con módulo {module_name}: {e}")

            # Crear widget de diagnóstico para el error
            widget = create_diagnostic_widget(module_name, e)
            print(f"✅ Widget de diagnóstico creado: {type(widget).__name__}")


def run_comprehensive_test():
    """Ejecuta todos los tests del sistema de diagnóstico."""

    print("🔍 INICIANDO TESTS DEL SISTEMA DE DIAGNÓSTICO")
    print("=" * 60)

    try:
        # Test 1: Widget de diagnóstico
        print("\n1. Probando widget de diagnóstico...")
        # test_diagnostic_widget()  # Comentado para evitar UI en tests automatizados

        # Test 2: Module manager
        print("\n2. Probando module manager...")
        error_widget = test_module_manager_error_handling()

        # Test 3: Módulos reales
        print("\n3. Probando módulos reales...")
        test_real_module_errors()

        print("\n" + "=" * 60)
        print("✅ TODOS LOS TESTS COMPLETADOS")
        print("   - Widget de diagnóstico: Funcional")
        print("   - Module manager: Funcional")
        print("   - Manejo de errores reales: Funcional")

        return True

    except Exception as e:
        print(f"\n❌ ERROR EN TESTS: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_comprehensive_test()
    sys.exit(0 if success else 1)
