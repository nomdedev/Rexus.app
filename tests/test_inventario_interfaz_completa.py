#!/usr/bin/env python3
"""
Test Completo de Interfaz - Módulo Inventario
==============================================

Verifica que los datos se cargan correctamente y se muestran en la interfaz
como debería ser, probando todo el flujo desde base de datos hasta la tabla.
"""

import os
import sys
import time
import traceback

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

# Agregar ruta del proyecto
sys.path.insert(0, os.path.abspath("."))


def test_inventario_interfaz_completa():
    """Test completo de carga de datos y visualización en interfaz."""

    print("🧪 INICIANDO TEST COMPLETO DE INTERFAZ - MÓDULO INVENTARIO")
    print("=" * 80)

    app = None
    try:
        # 1. Crear aplicación Qt
        app = QApplication(sys.argv)

        # 2. Importar y configurar componentes del módulo
        print("📦 Importando componentes del módulo inventario...")

        # Importar conexión a base de datos
        from rexus.core.database import InventarioDatabaseConnection

        # Importar controlador
        from rexus.modules.inventario.controller import InventarioController

        # Importar modelo
        from rexus.modules.inventario.model import InventarioModel

        # Importar vista
        from rexus.modules.inventario.view import InventarioView

        print("[CHECK] Componentes importados correctamente")

        # 3. Configurar conexión a base de datos
        print("\n🔌 Configurando conexión a base de datos...")
        db_connection = InventarioDatabaseConnection(auto_connect=True)

        if db_connection.connection:
            print("[CHECK] Conexión a base de datos establecida")
            print(f"   [CHART] Base de datos: {db_connection.database}")
        else:
            print("[ERROR] Error en conexión a base de datos")
            return False

        # 4. Test directo de consulta a base de datos
        print("\n💾 Probando consulta directa a base de datos...")
        try:
            cursor = db_connection.connection.cursor()

            # Verificar tabla inventario_perfiles
            cursor.execute(
                "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'inventario_perfiles'"
            )
            tabla_existe = cursor.fetchone()

            if tabla_existe:
                print("[CHECK] Tabla 'inventario_perfiles' existe")

                # Contar registros
                cursor.execute("SELECT COUNT(*) FROM inventario_perfiles")
                result = cursor.fetchone()
                total_registros = result[0] if result else 0
                print(f"[CHART] Total de registros en tabla: {total_registros}")

                if total_registros > 0:
                    # Obtener algunos registros
                    cursor.execute(
                        "SELECT TOP 5 id, codigo, descripcion, stock_actual, categoria, precio_unitario FROM inventario_perfiles"
                    )
                    registros = cursor.fetchall()
                    print("🔍 Primeros registros encontrados:")
                    for reg in registros:
                        print(
                            f"   ID: {reg[0]}, Código: {reg[1]}, Descripción: {reg[2]}, Stock: {reg[3]}"
                        )
                else:
                    print("[WARN] La tabla existe pero está vacía")

                    # Insertar datos de prueba
                    print("📝 Insertando datos de prueba...")
                    test_data = [
                        (
                            1001,
                            "PERFIL001",
                            "Perfil Aluminio 20x20",
                            100,
                            "Perfiles",
                            25.50,
                        ),
                        (
                            1002,
                            "PERFIL002",
                            "Perfil Aluminio 30x30",
                            75,
                            "Perfiles",
                            35.75,
                        ),
                        (
                            1003,
                            "PERFIL003",
                            "Perfil Aluminio 40x40",
                            50,
                            "Perfiles",
                            45.00,
                        ),
                        (
                            1004,
                            "VIDRIO001",
                            "Vidrio Templado 6mm",
                            25,
                            "Vidrios",
                            120.00,
                        ),
                        (1005, "HERR001", "Herraje Premium", 30, "Herrajes", 85.50),
                    ]

                    for data in test_data:
                        try:
                            cursor.execute(
                                """
                                INSERT INTO inventario_perfiles (id, codigo, descripcion, stock_actual, categoria, precio_unitario, activo)
                                VALUES (?, ?, ?, ?, ?, ?, 1)
                            """,
                                data,
                            )
                        except Exception as e:
                            print(f"   [WARN] Error insertando registro {data[0]}: {e}")

                    db_connection.connection.commit()
                    print("[CHECK] Datos de prueba insertados")

                    # Verificar inserción
                    cursor.execute(
                        "SELECT COUNT(*) FROM inventario_perfiles WHERE activo = 1"
                    )
                    result = cursor.fetchone()
                    nuevos_registros = result[0] if result else 0
                    print(
                        f"[CHART] Registros activos después de inserción: {nuevos_registros}"
                    )

            else:
                print("[ERROR] Tabla 'inventario_perfiles' NO existe")
                return False

        except Exception as e:
            print(f"[ERROR] Error en consulta directa: {e}")
            traceback.print_exc()
            return False

        # 5. Crear instancias del patrón MVC
        print("\n🏗️ Creando instancias del patrón MVC...")

        # Crear modelo
        model = InventarioModel(db_connection=db_connection.connection)
        print("[CHECK] Modelo creado")

        # Crear vista principal en ventana
        main_window = QMainWindow()
        main_window.setWindowTitle("Test Inventario - Vista Completa")
        main_window.setGeometry(100, 100, 1200, 800)

        # Widget principal
        central_widget = QWidget()
        main_window.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Crear vista del inventario
        view = InventarioView()
        layout.addWidget(view)
        print("[CHECK] Vista creada e integrada")

        # Crear controlador
        controller = InventarioController(
            model=model, view=view, db_connection=db_connection.connection
        )
        print("[CHECK] Controlador creado")

        # 6. Conectar vista con controlador
        print("\n🔗 Conectando vista con controlador...")
        view.controller = controller
        controller.view = view
        print("[CHECK] Vista y controlador conectados")

        # 7. Test del controlador - carga de datos
        print("\n🎮 Probando carga de datos desde el controlador...")

        # Forzar carga de datos
        controller._cargar_datos_inventario()

        # 8. Verificar que la tabla se pobló
        print("\n📋 Verificando datos en la tabla de la interfaz...")

        interfaz_exitosa = False

        if hasattr(view, "tabla_inventario") and view.tabla_inventario:
            tabla = view.tabla_inventario
            filas = tabla.rowCount()
            columnas = tabla.columnCount()

            print(f"[CHART] Tabla: {filas} filas x {columnas} columnas")

            if filas > 0:
                print("[CHECK] La tabla contiene datos:")

                # Mostrar encabezados
                headers = []
                for col in range(columnas):
                    item = tabla.horizontalHeaderItem(col)
                    headers.append(item.text() if item else f"Col {col}")
                print(f"   📝 Encabezados: {headers}")

                # Mostrar primeras filas
                for fila in range(min(filas, 5)):
                    row_data = []
                    for col in range(columnas):
                        item = tabla.item(fila, col)
                        row_data.append(item.text() if item else "")
                    print(f"   📌 Fila {fila + 1}: {row_data}")

                print(f"[CHECK] ÉXITO: La interfaz muestra {filas} productos correctamente")
                interfaz_exitosa = True

            else:
                print("[ERROR] La tabla está vacía - no se cargaron datos en la interfaz")
                interfaz_exitosa = False
        else:
            print("[ERROR] No se pudo acceder a la tabla de la interfaz")
            interfaz_exitosa = False

        # 9. Mostrar ventana para inspección visual (opcional)
        print("\n👁️ Mostrando ventana para inspección visual...")
        main_window.show()

        # Timer para cerrar automáticamente después de 3 segundos
        def cerrar_automatico():
            print("⏰ Cerrando ventana automáticamente...")
            main_window.close()
            app.quit()

        timer = QTimer()
        timer.timeout.connect(cerrar_automatico)
        timer.start(3000)  # 3 segundos

        # Procesar eventos de la aplicación
        app.processEvents()
        time.sleep(3.5)  # Esperar un poco más que el timer

        # 10. Generar reporte final
        print("\n" + "=" * 80)
        print("[CHART] REPORTE FINAL DEL TEST")
        print("=" * 80)

        if interfaz_exitosa:
            print(
                "[CHECK] ÉXITO TOTAL: El módulo inventario carga y muestra datos correctamente"
            )
            print("   🔹 Conexión a base de datos: [CHECK] Funcional")
            print("   🔹 Consulta de datos: [CHECK] Funcional")
            print("   🔹 Modelo MVC: [CHECK] Funcional")
            print("   🔹 Controlador: [CHECK] Funcional")
            print("   🔹 Vista/Interfaz: [CHECK] Funcional")
            print("   🔹 Carga en tabla: [CHECK] Funcional")
            return True
        else:
            print("[ERROR] FALLO: El módulo tiene problemas en la carga o visualización")
            print("   🔹 Revisar métodos de carga de datos en el controlador")
            print("   🔹 Verificar integración vista-controlador")
            print("   🔹 Comprobar estructura de datos devueltos por el modelo")
            return False

    except Exception as e:
        print(f"\n[ERROR] ERROR CRÍTICO EN EL TEST: {e}")
        traceback.print_exc()
        return False

    finally:
        if app:
            try:
                app.quit()
            except Exception:
                pass


if __name__ == "__main__":
    resultado = test_inventario_interfaz_completa()
    exit(0 if resultado else 1)
