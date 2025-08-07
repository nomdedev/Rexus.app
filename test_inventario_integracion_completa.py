#!/usr/bin/env python3
"""
Test de Integración Completa para el Módulo Inventario
Replica exactamente el comportamiento de la aplicación real para detectar errores reales.
"""

import os
import sys
import traceback
from unittest.mock import MagicMock, Mock

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_real_application_flow():
    """Prueba el flujo completo como en la aplicación real."""
    print("🔍 AUDITORIA COMPLETA: Simulando flujo real de la aplicación")
    print("=" * 80)

    errors_found = []

    try:
        # 1. IMPORTACIONES COMO EN MAIN.PY
        print("\n📋 PASO 1: Importaciones como en la aplicación real")

        # Simular el entorno de PyQt6
        try:
            from PyQt6.QtCore import QObject, pyqtSignal
            from PyQt6.QtWidgets import QApplication, QWidget

            print("✅ PyQt6 disponible")
        except ImportError as e:
            print(f"❌ Error PyQt6: {e}")
            errors_found.append(f"PyQt6 Import Error: {e}")

        # Importar el módulo como lo hace module_manager
        try:
            from rexus.modules.inventario import (
                InventarioController,
                InventarioModel,
                InventarioView,
            )

            print("✅ Módulo inventario importado desde __init__.py")
        except Exception as e:
            print(f"❌ Error importando módulo inventario: {e}")
            errors_found.append(f"Module Import Error: {e}")
            traceback.print_exc()

        # 2. CREACIÓN DE INSTANCIAS COMO EN MODULE_MANAGER
        print("\n📋 PASO 2: Creación de instancias como module_manager")

        # Simular conexión de base de datos
        mock_db = Mock()
        mock_db.cursor.return_value = Mock()

        try:
            # Crear modelo
            print("   🔧 Creando modelo...")
            model = InventarioModel(mock_db)
            print("   ✅ Modelo creado exitosamente")
        except Exception as e:
            print(f"   ❌ Error creando modelo: {e}")
            errors_found.append(f"Model Creation Error: {e}")
            traceback.print_exc()

        try:
            # Crear vista
            print("   🔧 Creando vista...")
            # Simular QApplication para evitar errores de Qt
            app = None
            try:
                app = QApplication.instance()
                if app is None:
                    app = QApplication([])
            except:
                pass

            view = InventarioView()
            print("   ✅ Vista creada exitosamente")
        except Exception as e:
            print(f"   ❌ Error creando vista: {e}")
            errors_found.append(f"View Creation Error: {e}")
            traceback.print_exc()

        try:
            # Crear controlador
            print("   🔧 Creando controlador...")
            controller = InventarioController(model, view)
            print("   ✅ Controlador creado exitosamente")
        except Exception as e:
            print(f"   ❌ Error creando controlador: {e}")
            errors_found.append(f"Controller Creation Error: {e}")
            traceback.print_exc()

        # 3. CARGA INICIAL COMO EN MODULE_MANAGER
        print("\n📋 PASO 3: Carga inicial de datos como module_manager")

        try:
            # Simular el método que llama module_manager
            if hasattr(controller, "cargar_inventario_inicial"):
                print("   🔧 Llamando cargar_inventario_inicial...")
                controller.cargar_inventario_inicial()
                print("   ✅ Carga inicial exitosa")
            else:
                print("   ❌ Método cargar_inventario_inicial no encontrado")
                errors_found.append("Method cargar_inventario_inicial not found")
        except Exception as e:
            print(f"   ❌ Error en carga inicial: {e}")
            errors_found.append(f"Initial Load Error: {e}")
            traceback.print_exc()

        # 4. CONEXIONES DE SEÑALES
        print("\n📋 PASO 4: Verificando conexiones de señales")

        try:
            # Verificar que las señales se conectaron correctamente
            if hasattr(view, "btn_buscar") and hasattr(controller, "buscar_productos"):
                print("   ✅ btn_buscar y buscar_productos disponibles")
            else:
                print("   ❌ Falta btn_buscar o buscar_productos")
                errors_found.append("Signal connection: btn_buscar missing")

            if hasattr(view, "tabla_inventario"):
                print("   ✅ tabla_inventario disponible en vista")
            else:
                print("   ❌ tabla_inventario no disponible")
                errors_found.append("UI component: tabla_inventario missing")

        except Exception as e:
            print(f"   ❌ Error verificando señales: {e}")
            errors_found.append(f"Signal Check Error: {e}")

        # 5. PRUEBA DE MÉTODOS REALES DEL MODELO
        print("\n📋 PASO 5: Probando métodos reales del modelo")

        try:
            # Probar obtener_productos_paginados con parámetros reales
            if hasattr(model, "obtener_productos_paginados"):
                print("   🔧 Probando obtener_productos_paginados(0, 100)...")
                resultado = model.obtener_productos_paginados(0, 100)
                print(
                    f"   ✅ Resultado: {type(resultado)} - {len(str(resultado)[:100])}..."
                )
            else:
                print("   ❌ Método obtener_productos_paginados no disponible")
                errors_found.append("Model method: obtener_productos_paginados missing")
        except Exception as e:
            print(f"   ❌ Error ejecutando obtener_productos_paginados: {e}")
            errors_found.append(f"Model Method Error: {e}")
            traceback.print_exc()

        # 6. PRUEBA DE AUTENTICACIÓN
        print("\n📋 PASO 6: Verificando sistema de autenticación")

        try:
            # Simular contexto de autenticación
            from rexus.core import auth_manager

            if hasattr(auth_manager, "current_user"):
                print("   ✅ Sistema de autenticación disponible")
            else:
                print("   ⚠️ Sistema de autenticación no disponible")

            # Probar método con decorador auth_required
            if hasattr(controller, "cargar_inventario"):
                print("   🔧 Probando método con @auth_required...")
                try:
                    controller.cargar_inventario()
                    print("   ✅ Método auth_required ejecutado")
                except Exception as auth_e:
                    print(f"   ❌ Error de autenticación: {auth_e}")
                    errors_found.append(f"Auth Error: {auth_e}")
        except Exception as e:
            print(f"   ❌ Error verificando autenticación: {e}")
            errors_found.append(f"Auth System Error: {e}")

    except Exception as e:
        print(f"❌ Error general en test: {e}")
        errors_found.append(f"General Test Error: {e}")
        traceback.print_exc()

    return errors_found


def test_database_integration():
    """Prueba la integración real con base de datos."""
    print("\n🔍 AUDITORIA BD: Probando integración real con base de datos")
    print("=" * 80)

    errors_found = []

    try:
        # Importar utilidades de BD reales
        from rexus.utils.database import DatabaseManager

        # Crear conexión real
        db_manager = DatabaseManager()
        connection = db_manager.get_connection()

        if connection:
            print("✅ Conexión a BD exitosa")

            # Probar modelo con BD real
            from rexus.modules.inventario import InventarioModel

            model = InventarioModel(connection)

            # Probar métodos con BD real
            try:
                resultado = model.obtener_productos_paginados(0, 10)
                print(f"✅ obtener_productos_paginados funcionó: {type(resultado)}")
            except Exception as e:
                print(f"❌ Error en obtener_productos_paginados: {e}")
                errors_found.append(f"DB Method Error: {e}")

        else:
            print("❌ No se pudo conectar a la BD")
            errors_found.append("Database connection failed")

    except Exception as e:
        print(f"❌ Error en test de BD: {e}")
        errors_found.append(f"DB Test Error: {e}")
        traceback.print_exc()

    return errors_found


def test_ui_integration():
    """Prueba la integración real con interfaz de usuario."""
    print("\n🔍 AUDITORIA UI: Probando integración real con interfaz")
    print("=" * 80)

    errors_found = []

    try:
        from PyQt6.QtWidgets import QApplication

        from rexus.modules.inventario import InventarioView

        # Crear aplicación Qt si no existe
        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        # Crear vista
        view = InventarioView()

        # Verificar componentes UI requeridos
        required_components = [
            "btn_buscar",
            "btn_actualizar",
            "btn_limpiar",
            "btn_nuevo_producto",
            "btn_editar",
            "btn_eliminar",
            "btn_movimiento",
            "btn_exportar",
            "tabla_inventario",
        ]

        for component in required_components:
            if hasattr(view, component):
                widget = getattr(view, component)
                if widget is not None:
                    print(f"   ✅ {component}: {type(widget).__name__}")
                else:
                    print(f"   ❌ {component}: existe pero es None")
                    errors_found.append(f"UI Component is None: {component}")
            else:
                print(f"   ❌ {component}: no existe")
                errors_found.append(f"UI Component missing: {component}")

        # Probar actualización de vista
        try:
            if hasattr(view, "tabla_inventario") and view.tabla_inventario:
                # Simular datos de prueba
                test_data = [
                    {"codigo": "TEST001", "descripcion": "Test Product", "stock": 10}
                ]

                # Intentar diferentes métodos de actualización
                if hasattr(view, "actualizar_tabla"):
                    view.actualizar_tabla(test_data)
                    print("   ✅ actualizar_tabla funcionó")
                elif hasattr(view, "mostrar_productos"):
                    view.mostrar_productos(test_data)
                    print("   ✅ mostrar_productos funcionó")
                else:
                    print("   ❌ No hay método para actualizar vista")
                    errors_found.append("No method to update view found")

        except Exception as e:
            print(f"   ❌ Error actualizando vista: {e}")
            errors_found.append(f"View Update Error: {e}")

    except Exception as e:
        print(f"❌ Error en test UI: {e}")
        errors_found.append(f"UI Test Error: {e}")
        traceback.print_exc()

    return errors_found


def test_controller_methods():
    """Prueba específica de métodos del controlador."""
    print("\n🔍 AUDITORIA CONTROLLER: Probando métodos del controlador")
    print("=" * 80)

    errors_found = []

    try:
        from rexus.modules.inventario import InventarioController

        # Mock de dependencias
        mock_model = Mock()
        mock_view = Mock()

        # Configurar mock_view con atributos esperados
        mock_view.btn_buscar = Mock()
        mock_view.btn_actualizar = Mock()
        mock_view.tabla_inventario = Mock()

        # Crear controlador
        controller = InventarioController(mock_model, mock_view)

        # Verificar métodos requeridos
        required_methods = [
            "cargar_inventario_inicial",
            "cargar_inventario",
            "buscar_productos",
            "conectar_senales",
            "_cargar_datos_inventario",
            "_actualizar_vista_productos",
        ]

        for method in required_methods:
            if hasattr(controller, method):
                print(f"   ✅ {method}: disponible")

                # Probar ejecución si es seguro
                if method in ["conectar_senales"]:
                    try:
                        getattr(controller, method)()
                        print(f"   ✅ {method}: ejecutado exitosamente")
                    except Exception as e:
                        print(f"   ❌ {method}: error al ejecutar - {e}")
                        errors_found.append(f"Controller method error {method}: {e}")
            else:
                print(f"   ❌ {method}: no disponible")
                errors_found.append(f"Controller method missing: {method}")

    except Exception as e:
        print(f"❌ Error en test controller: {e}")
        errors_found.append(f"Controller Test Error: {e}")
        traceback.print_exc()

    return errors_found


def main():
    """Ejecuta auditoría completa del módulo inventario."""
    print("🚀 AUDITORÍA COMPLETA DEL MÓDULO INVENTARIO")
    print("🔍 Detectando errores reales que ocurren en la aplicación")
    print("=" * 80)

    all_errors = []

    # Ejecutar todas las pruebas
    tests = [
        ("Flujo Real de Aplicación", test_real_application_flow),
        ("Integración con Base de Datos", test_database_integration),
        ("Integración con Interfaz", test_ui_integration),
        ("Métodos del Controlador", test_controller_methods),
    ]

    for test_name, test_func in tests:
        print(f"\n🧪 EJECUTANDO: {test_name}")
        print("-" * 60)
        try:
            errors = test_func()
            if errors:
                all_errors.extend([(test_name, error) for error in errors])
            else:
                print(f"✅ {test_name}: Sin errores detectados")
        except Exception as e:
            print(f"❌ {test_name}: Error en test - {e}")
            all_errors.append((test_name, f"Test execution error: {e}"))

    # Reporte final
    print("\n" + "=" * 80)
    print("📊 REPORTE FINAL DE AUDITORÍA")
    print("=" * 80)

    if all_errors:
        print(f"❌ SE ENCONTRARON {len(all_errors)} ERRORES:")
        print()

        error_categories = {}
        for test_name, error in all_errors:
            if test_name not in error_categories:
                error_categories[test_name] = []
            error_categories[test_name].append(error)

        for category, errors in error_categories.items():
            print(f"🔸 {category}:")
            for error in errors:
                print(f"   • {error}")
            print()

        print("🔧 ACCIONES REQUERIDAS:")
        print("   1. Corregir errores de importación en __init__.py")
        print("   2. Arreglar métodos faltantes en controlador")
        print("   3. Sincronizar vista-controlador")
        print("   4. Resolver problemas de autenticación")
        print("   5. Verificar integración con base de datos")

        return False
    else:
        print("🎉 ¡NO SE ENCONTRARON ERRORES!")
        print("✅ El módulo inventario está funcionando correctamente")
        return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
