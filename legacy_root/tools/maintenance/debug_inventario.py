#!/usr/bin/env python3
"""
Debug script para diagnosticar problema de Inventario
"""

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# PyQt6 imports
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

def test_inventory_data_loading():
    """Test completo de carga de datos de inventario"""

    print("=== DIAGNÓSTICO INVENTARIO ===")

    # 1. Test environment variables
    print("\n1. VARIABLES DE ENTORNO:")
    import os
    required_vars = ['DB_SERVER', 'DB_DRIVER', 'DB_USERNAME', 'DB_PASSWORD', 'DB_INVENTARIO']
    for var in required_vars:
        value = os.getenv(var)
        print(f"   {var}: {'OK' if value else 'MISSING'}")

    # 2. Test database connection
    print("\n2. CONEXIÓN BASE DE DATOS:")
    try:
        from src.core.database import InventarioDatabaseConnection
        db = InventarioDatabaseConnection()
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM inventario_perfiles")
        count = cursor.fetchone()[0]
        print(f"   OK Conexion exitosa, {count} registros en inventario_perfiles")
    except Exception as e:
        print(f"   ERROR Error conexion BD: {e}")
        return

    # 3. Test model
    print("\n3. MODELO DE INVENTARIO:")
    try:
        from src.modules.inventario.model import InventarioModel
        model = InventarioModel(db)
        productos = model.obtener_todos_productos()
        print(f"   OK Modelo cargado, {len(productos)} productos obtenidos")

        if productos:
            sample = productos[0]
            print(f"   OK Producto ejemplo: {sample.get('codigo', 'N/A')} - {sample.get('descripcion', 'N/A')}")
    except Exception as e:
        print(f"   ERROR Error modelo: {e}")
        return

    # 4. Test view creation
    print("\n4. VISTA DE INVENTARIO:")
    try:
        from src.modules.inventario.view import InventarioView
        view = InventarioView()
        print(f"   OK Vista creada: {type(view).__name__}")
        print(f"   OK Tabla existe: {hasattr(view, 'tabla_inventario')}")
        if hasattr(view, 'tabla_inventario'):
            print(f"   OK Filas iniciales en tabla: {view.tabla_inventario.rowCount()}")
    except Exception as e:
        print(f"   ERROR Error vista: {e}")
        return

    # 5. Test controller
    print("\n5. CONTROLADOR DE INVENTARIO:")
    try:
        from src.modules.inventario.controller import InventarioController
        controller = InventarioController(model, view, db)
        print(f"   OK Controlador creado: {type(controller).__name__}")

        # Test data loading
        print("   - Ejecutando cargar_datos_iniciales()...")
        controller.cargar_datos_iniciales()

        # Check if data was loaded to view
        if hasattr(view, 'tabla_inventario'):
            final_rows = view.tabla_inventario.rowCount()
            print(f"   OK Filas despues de cargar datos: {final_rows}")

            if final_rows > 0:
                print("   EXITO: Los datos se cargaron correctamente en la tabla")
            else:
                print("   PROBLEMA: La tabla sigue vacia despues de cargar datos")

    except Exception as e:
        print(f"   ERROR Error controlador: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n=== DIAGNÓSTICO COMPLETADO ===")

if __name__ == '__main__':
    # Create QApplication for PyQt widgets
    app = QApplication(sys.argv)
    app.setAttribute(Qt.ApplicationAttribute.AA_DontShowIconsInMenus, False)

    test_inventory_data_loading()

    # Don't start event loop, just exit
    sys.exit(0)
