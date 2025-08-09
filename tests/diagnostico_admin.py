#!/usr/bin/env python3
"""
Diagnóstico de errores cuando se ejecuta como administrador
"""

import sys
import traceback
from pathlib import Path

# Configurar entorno
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

def test_module_import(module_name, import_path):
    """Prueba importar un módulo específico."""
    print(f"\n=== TESTING {module_name.upper()} ===")
    try:
        exec(f"from {import_path} import *")
        print(f"OK {module_name}: Import OK")
        return True
    except Exception as e:
        print(f"ERROR {module_name}: Import ERROR")
        print(f"   Error: {e}")
        print(f"   Traceback: {traceback.format_exc()}")
        return False

def test_database_connections():
    """Prueba las conexiones de base de datos."""
    print("\n=== TESTING DATABASE CONNECTIONS ===")
    
    # Test inventario DB
    try:
        from rexus.core.database import InventarioDatabaseConnection
        db = InventarioDatabaseConnection()
        print("OK InventarioDB: OK")
    except Exception as e:
        print(f"ERROR InventarioDB: ERROR - {e}")
        print(f"   Traceback: {traceback.format_exc()}")
    
    # Test users DB
    try:
        from rexus.core.database import UsersDatabaseConnection  
        db = UsersDatabaseConnection()
        print("OK UsersDB: OK")
    except Exception as e:
        print(f"ERROR UsersDB: ERROR - {e}")
        print(f"   Traceback: {traceback.format_exc()}")
    
    # Test auditoria DB
    try:
        from rexus.core.database import AuditoriaDatabaseConnection
        db = AuditoriaDatabaseConnection()
        print("OK AuditoriaDB: OK")
    except Exception as e:
        print(f"ERROR AuditoriaDB: ERROR - {e}")
        print(f"   Traceback: {traceback.format_exc()}")

def test_core_components():
    """Prueba componentes core."""
    print("\n=== TESTING CORE COMPONENTS ===")
    
    try:
        from rexus.core.module_manager import ModuleManager
        mm = ModuleManager()
        print("OK ModuleManager: OK")
    except Exception as e:
        print(f"ERROR ModuleManager: ERROR - {e}")
        print(f"   Traceback: {traceback.format_exc()}")
    
    try:
        from rexus.ui.components import RexusButton, RexusLabel
        print("OK UI Components: OK")
    except Exception as e:
        print(f"ERROR UI Components: ERROR - {e}")
        print(f"   Traceback: {traceback.format_exc()}")

def test_module_creation():
    """Prueba crear un módulo específico paso a paso."""
    print("\n=== TESTING MODULE CREATION (INVENTARIO) ===")
    
    try:
        # Paso 1: Import model
        print("Paso 1: Importando modelo...")
        from rexus.modules.inventario.model import InventarioModel
        print("OK Modelo importado")
        
        # Paso 2: Import controller
        print("Paso 2: Importando controlador...")
        from rexus.modules.inventario.controller import InventarioController
        print("OK Controlador importado")
        
        # Paso 3: Import view
        print("Paso 3: Importando vista...")
        from rexus.modules.inventario.view import InventarioView
        print("OK Vista importada")
        
        # Paso 4: Create DB connection
        print("Paso 4: Creando conexión DB...")
        from rexus.core.database import InventarioDatabaseConnection
        db_connection = InventarioDatabaseConnection()
        print("OK Conexión DB creada")
        
        # Paso 5: Create model instance
        print("Paso 5: Creando instancia del modelo...")
        model = InventarioModel(db_connection)
        print("OK Modelo instanciado")
        
        # Paso 6: Create view instance
        print("Paso 6: Creando instancia de la vista...")
        view = InventarioView()
        print("OK Vista instanciada")
        
        # Paso 7: Create controller instance  
        print("Paso 7: Creando instancia del controlador...")
        controller = InventarioController(model, view)
        print("OK Controlador instanciado")
        
        print("SUCCESS INVENTARIO: Creación completa exitosa")
        
    except Exception as e:
        print(f"ERROR INVENTARIO: ERROR en creación")
        print(f"   Error: {e}")
        print(f"   Traceback: {traceback.format_exc()}")

def main():
    """Función principal de diagnóstico."""
    print("DIAGNOSTICO DE ERRORES ADMIN - REXUS.APP")
    print("=" * 60)
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {Path.cwd()}")
    print(f"Script directory: {root_dir}")
    
    # Tests básicos
    test_core_components()
    test_database_connections()
    
    # Test imports de módulos principales
    modules_to_test = [
        ("Inventario Model", "rexus.modules.inventario.model"),
        ("Inventario View", "rexus.modules.inventario.view"),
        ("Inventario Controller", "rexus.modules.inventario.controller"),
        ("Usuarios Model", "rexus.modules.usuarios.model"), 
        ("Usuarios View", "rexus.modules.usuarios.view"),
        ("Obras Model", "rexus.modules.obras.model"),
        ("Obras View", "rexus.modules.obras.view"),
    ]
    
    print(f"\n=== TESTING MODULE IMPORTS ===")
    for module_name, import_path in modules_to_test:
        test_module_import(module_name, import_path)
    
    # Test creación completa de módulo
    test_module_creation()
    
    print(f"\n=== DIAGNOSTICO COMPLETADO ===")
    print("Si todos los tests pasan, el problema esta en otro lado.")
    print("Si hay errores, revisar los tracebacks para identificar el problema.")

if __name__ == "__main__":
    main()