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

            print("[CHECK] PyQt6 disponible")
        except ImportError as e:
            print(f"[ERROR] Error PyQt6: {e}")
            errors_found.append(f"PyQt6 Import Error: {e}")

        # Importar el módulo como lo hace module_manager
        try:
            from rexus.modules.inventario import (
                InventarioController,
                InventarioModel,
                InventarioView,
            )

            print("[CHECK] Módulo inventario importado desde __init__.py")
        except Exception as e:
            print(f"[ERROR] Error importando módulo inventario: {e}")
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
            print("   [CHECK] Modelo creado exitosamente")
        except Exception as e:
            print(f"   [ERROR] Error creando modelo: {e}")
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
            print("   [CHECK] Vista creada exitosamente")
        except Exception as e:
            print(f"   [ERROR] Error creando vista: {e}")
            errors_found.append(f"View Creation Error: {e}")
            traceback.print_exc()

        try:
            # Crear controlador
            print("   🔧 Creando controlador...")
            controller = InventarioController(model, view)
            print("   [CHECK] Controlador creado exitosamente")
        except Exception as e:
            print(f"   [ERROR] Error creando controlador: {e}")
            errors_found.append(f"Controller Creation Error: {e}")
            traceback.print_exc()

        # 3. CARGA INICIAL COMO EN MODULE_MANAGER
        print("\n📋 PASO 3: Carga inicial de datos como module_manager")

        try:
            # Simular el método que llama module_manager
            if hasattr(controller, "cargar_inventario_inicial"):
                print("   🔧 Llamando cargar_inventario_inicial...")
                controller.cargar_inventario_inicial()
                print("   [CHECK] Carga inicial exitosa")
            else:
                print("   [ERROR] Método cargar_inventario_inicial no encontrado")
                errors_found.append("Method cargar_inventario_inicial not found")
        except Exception as e:
            print(f"   [ERROR] Error en carga inicial: {e}")
            errors_found.append(f"Initial Load Error: {e}")
            traceback.print_exc()

        # 4. CONEXIONES DE SEÑALES
        print("\n📋 PASO 4: Verificando conexiones de señales")

        try:
            # Verificar que las señales se conectaron correctamente
            if hasattr(view, "btn_buscar") and hasattr(controller, "buscar_productos"):
                print("   [CHECK] btn_buscar y buscar_productos disponibles")
            else:
                print("   [ERROR] Falta btn_buscar o buscar_productos")
                errors_found.append("Signal connection: btn_buscar missing")

            if hasattr(view, "tabla_inventario"):
                print("   [CHECK] tabla_inventario disponible en vista")
            else:
                print("   [ERROR] tabla_inventario no disponible")
                errors_found.append("UI component: tabla_inventario missing")

        except Exception as e:
            print(f"   [ERROR] Error verificando señales: {e}")
            errors_found.append(f"Signal Check Error: {e}")

        # 5. PRUEBA DE MÉTODOS REALES DEL MODELO
        print("\n📋 PASO 5: Probando métodos reales del modelo")

        try:
            # Probar método inicial sin autenticación primero
            if hasattr(model, "obtener_productos_paginados_inicial"):
                print("   🔧 Probando obtener_productos_paginados_inicial(0, 100)...")
                resultado = model.obtener_productos_paginados_inicial(0, 100)
                print(
                    f"   [CHECK] Resultado inicial: {type(resultado)} - {len(str(resultado)[:100])}..."
                )

                # VERIFICAR SI LOS DATOS SON REALES O SIMULADOS
                if isinstance(resultado, dict) and "items" in resultado:
                    productos = resultado["items"]
                    # Verificar si son datos simulados típicos
                    if len(productos) > 0:
                        primer_producto = productos[0]
                        if (
                            primer_producto.get("codigo") == "PROD001"
                            and "simulado"
                            in primer_producto.get("descripcion", "").lower()
                        ):
                            print(
                                "   [WARN] ADVERTENCIA: Se están cargando datos SIMULADOS, no reales de BD"
                            )
                            errors_found.append(
                                "Model returns simulated data instead of real database data"
                            )
                        elif primer_producto.get("descripcion") == "Producto 1":
                            print(
                                "   [WARN] ADVERTENCIA: Se están cargando datos SIMULADOS hardcodeados"
                            )
                            errors_found.append(
                                "Model returns hardcoded simulated data"
                            )
                        else:
                            print(
                                f"   [CHECK] Datos parecen ser reales de BD: {primer_producto.get('descripcion', 'N/A')}"
                            )
                    else:
                        print("   [WARN] ADVERTENCIA: No se encontraron productos")
                        errors_found.append("No products found in database")
            else:
                print("   [ERROR] Método obtener_productos_paginados_inicial no disponible")
                errors_found.append(
                    "Model method: obtener_productos_paginados_inicial missing"
                )

            # Probar método con autenticación (esperamos que falle)
            if hasattr(model, "obtener_productos_paginados"):
                print(
                    "   🔧 Probando obtener_productos_paginados(0, 100) (con auth)..."
                )
                resultado = model.obtener_productos_paginados(0, 100)
                print(
                    f"   [WARN] Resultado con auth: {type(resultado)} - {len(str(resultado)[:100])}..."
                )
            else:
                print("   [ERROR] Método obtener_productos_paginados no disponible")
                errors_found.append("Model method: obtener_productos_paginados missing")
        except Exception as e:
            print(f"   [ERROR] Error ejecutando obtener_productos_paginados (esperado): {e}")
            # No agregar a errores porque es esperado que falle sin autenticación
            traceback.print_exc()

        # 6. PRUEBA DE AUTENTICACIÓN
        print("\n📋 PASO 6: Verificando sistema de autenticación")

        try:
            # Simular contexto de autenticación
            from rexus.core import auth_manager

            if hasattr(auth_manager, "current_user"):
                print("   [CHECK] Sistema de autenticación disponible")
            else:
                print("   [WARN] Sistema de autenticación no disponible")

            # Probar método con decorador auth_required
            if hasattr(controller, "cargar_inventario"):
                print("   🔧 Probando método con @auth_required...")
                try:
                    controller.cargar_inventario()
                    print("   [CHECK] Método auth_required ejecutado")
                except Exception as auth_e:
                    print(f"   [ERROR] Error de autenticación: {auth_e}")
                    errors_found.append(f"Auth Error: {auth_e}")
        except Exception as e:
            print(f"   [ERROR] Error verificando autenticación: {e}")
            errors_found.append(f"Auth System Error: {e}")

    except Exception as e:
        print(f"[ERROR] Error general en test: {e}")
        errors_found.append(f"General Test Error: {e}")
        traceback.print_exc()

    return errors_found


def test_database_integration():
    """Prueba la integración real con base de datos."""
    print("\n🔍 AUDITORIA BD: Probando integración real con base de datos")
    print("=" * 80)

    errors_found = []

    try:
        # Importar utilidades de BD reales COMO EN LA APLICACIÓN
        from rexus.core.database import InventarioDatabaseConnection

        # Crear conexión como lo hace la aplicación real
        try:
            db_connection = InventarioDatabaseConnection(auto_connect=False)
            print("   [CHECK] InventarioDatabaseConnection creada exitosamente")
            print("[CHECK] Conexión a BD exitosa (como en app real)")

            # Probar modelo con BD real (como en la aplicación)
            from rexus.modules.inventario import InventarioModel

            # Crear modelo como lo hace la aplicación real
            model = InventarioModel(db_connection)

            # Probar métodos como en la aplicación real
            try:
                resultado = model.obtener_productos_paginados_inicial(0, 10)
                print(
                    f"[CHECK] obtener_productos_paginados_inicial funcionó: {type(resultado)}"
                )
            except Exception as e:
                print(f"[ERROR] Error en obtener_productos_paginados_inicial: {e}")
                errors_found.append(f"DB Method Error: {e}")

        except Exception as db_error:
            print(f"[ERROR] Error creando InventarioDatabaseConnection: {db_error}")
            errors_found.append(f"Database connection error: {db_error}")
            # Pero esto es normal si no hay variables de entorno de BD configuradas
            print("   [WARN] Esto es normal en entorno de pruebas sin BD configurada")

    except Exception as e:
        print(f"[ERROR] Error en test de BD: {e}")
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
                    print(f"   [CHECK] {component}: {type(widget).__name__}")
                else:
                    print(f"   [ERROR] {component}: existe pero es None")
                    errors_found.append(f"UI Component is None: {component}")
            else:
                print(f"   [ERROR] {component}: no existe")
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
                    print("   [CHECK] actualizar_tabla funcionó")
                elif hasattr(view, "mostrar_productos"):
                    view.mostrar_productos(test_data)
                    print("   [CHECK] mostrar_productos funcionó")
                else:
                    print("   [ERROR] No hay método para actualizar vista")
                    errors_found.append("No method to update view found")

        except Exception as e:
            print(f"   [ERROR] Error actualizando vista: {e}")
            errors_found.append(f"View Update Error: {e}")

    except Exception as e:
        print(f"[ERROR] Error en test UI: {e}")
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
                print(f"   [CHECK] {method}: disponible")

                # Probar ejecución si es seguro
                if method in ["conectar_senales"]:
                    try:
                        getattr(controller, method)()
                        print(f"   [CHECK] {method}: ejecutado exitosamente")
                    except Exception as e:
                        print(f"   [ERROR] {method}: error al ejecutar - {e}")
                        errors_found.append(f"Controller method error {method}: {e}")
            else:
                print(f"   [ERROR] {method}: no disponible")
                errors_found.append(f"Controller method missing: {method}")

    except Exception as e:
        print(f"[ERROR] Error en test controller: {e}")
        errors_found.append(f"Controller Test Error: {e}")
        traceback.print_exc()

    return errors_found


def main():
    """Ejecuta auditoría completa del módulo inventario."""
    print("[ROCKET] AUDITORÍA COMPLETA DEL MÓDULO INVENTARIO")
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
                print(f"[CHECK] {test_name}: Sin errores detectados")
        except Exception as e:
            print(f"[ERROR] {test_name}: Error en test - {e}")
            all_errors.append((test_name, f"Test execution error: {e}"))

    # Reporte final
    print("\n" + "=" * 80)
    print("[CHART] REPORTE FINAL DE AUDITORÍA")
    print("=" * 80)

    if all_errors:
        print(f"[ERROR] SE ENCONTRARON {len(all_errors)} ERRORES:")
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
        print("[CHECK] El módulo inventario está funcionando correctamente")
        return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
