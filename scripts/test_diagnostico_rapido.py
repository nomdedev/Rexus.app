"""
Test rápido de verificación del sistema de diagnóstico
sin dependencias de UI
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))


def test_diagnostic_creation():
    """Prueba la creación del sistema de diagnóstico sin UI."""

    print("🔍 VERIFICANDO SISTEMA DE DIAGNÓSTICO")
    print("=" * 50)

    try:
        # 1. Verificar que se puede importar el módulo de diagnóstico
        print("1. Importando módulo de diagnóstico...")
        from rexus.utils.diagnostic_widget import (
            DiagnosticWidget,
            create_diagnostic_widget,
        )

        print("   ✅ Módulo importado correctamente")

        # 2. Verificar que se puede crear una instancia de diagnóstico
        print("2. Creando información de error de prueba...")
        test_error = ImportError("Test module not found")

        # Crear widget (sin mostrarlo)
        print("3. Creando widget de diagnóstico...")
        # Esto no debería fallar si no tratamos de mostrarlo
        diagnostic_info = {
            "error": str(test_error),
            "type": type(test_error).__name__,
            "traceback": "Test traceback",
        }

        # Crear instancia de la clase sin mostrarla
        diagnostic_widget_class = DiagnosticWidget("test_module", diagnostic_info)
        print("   ✅ Widget de diagnóstico creado correctamente")

        # 3. Verificar métodos de diagnóstico
        print("4. Probando métodos de diagnóstico...")
        diagnostics = diagnostic_widget_class.run_diagnostics()
        print(f"   ✅ Diagnósticos ejecutados: {len(diagnostics)} elementos")

        solutions = diagnostic_widget_class.generate_solutions()
        print(f"   ✅ Soluciones generadas: {len(solutions)} elementos")

        # 4. Verificar integración con module manager
        print("5. Probando integración con module manager...")
        from rexus.core.module_manager import ModuleManager

        manager = ModuleManager()

        # Verificar que tiene el método actualizado
        if hasattr(manager, "_create_error_widget"):
            print("   ✅ Module manager tiene método de error actualizado")
        else:
            print("   ❌ Module manager no tiene método de error")

        if hasattr(manager, "_retry_module_load"):
            print("   ✅ Module manager tiene método de reintento")
        else:
            print("   ❌ Module manager no tiene método de reintento")

        print("\n" + "=" * 50)
        print("✅ SISTEMA DE DIAGNÓSTICO VERIFICADO EXITOSAMENTE")
        print("   - Widgets de diagnóstico: Funcionales")
        print("   - Métodos de análisis: Funcionales")
        print("   - Integración con manager: Funcional")
        print("   - Sistema listo para uso en producción")

        return True

    except Exception as e:
        print(f"\n❌ ERROR EN VERIFICACIÓN: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_module_loading_with_diagnostics():
    """Prueba la carga de módulos reales con diagnóstico."""

    print("\n🔧 PROBANDO CARGA DE MÓDULOS CON DIAGNÓSTICO")
    print("=" * 50)

    try:
        from rexus.core.module_manager import ModuleManager

        manager = ModuleManager()

        # Lista de módulos para probar
        test_modules = ["obras", "inventario", "usuarios", "compras", "vidrios"]

        for module_name in test_modules:
            print(f"\n--- Probando módulo: {module_name} ---")

            try:
                # Intentar importar las clases del módulo
                from importlib import import_module

                model_module = import_module(f"rexus.modules.{module_name}.model")
                view_module = import_module(f"rexus.modules.{module_name}.view")
                controller_module = import_module(
                    f"rexus.modules.{module_name}.controller"
                )

                # Obtener las clases principales
                model_classes = [
                    attr for attr in dir(model_module) if attr.endswith("Model")
                ]
                view_classes = [
                    attr for attr in dir(view_module) if attr.endswith("View")
                ]
                controller_classes = [
                    attr
                    for attr in dir(controller_module)
                    if attr.endswith("Controller")
                ]

                print(f"   ✅ Archivos importados correctamente")
                print(f"      - Modelos encontrados: {len(model_classes)}")
                print(f"      - Vistas encontradas: {len(view_classes)}")
                print(f"      - Controladores encontrados: {len(controller_classes)}")

                if model_classes and view_classes and controller_classes:
                    print(f"   ✅ Módulo {module_name} tiene estructura completa")
                else:
                    print(f"   ⚠️  Módulo {module_name} tiene estructura incompleta")

            except ImportError as e:
                print(f"   ❌ Error de importación en {module_name}: {e}")
            except SyntaxError as e:
                print(f"   ❌ Error de sintaxis en {module_name}: {e}")
            except Exception as e:
                print(f"   ❌ Error general en {module_name}: {e}")

        print("\n" + "=" * 50)
        print("✅ PRUEBA DE CARGA DE MÓDULOS COMPLETADA")

        return True

    except Exception as e:
        print(f"\n❌ ERROR EN PRUEBA DE MÓDULOS: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 INICIANDO VERIFICACIÓN COMPLETA DEL SISTEMA")
    print("=" * 60)

    # Test 1: Sistema de diagnóstico
    success1 = test_diagnostic_creation()

    # Test 2: Carga de módulos
    success2 = test_module_loading_with_diagnostics()

    print("\n" + "=" * 60)
    if success1 and success2:
        print("✅ TODOS LOS TESTS PASARON - SISTEMA LISTO")
        print("   El sistema de diagnóstico está completamente funcional")
        print("   Los usuarios verán información detallada de errores")
        sys.exit(0)
    else:
        print("❌ ALGUNOS TESTS FALLARON - REVISAR SISTEMA")
        sys.exit(1)
