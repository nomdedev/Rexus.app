#!/usr/bin/env python3
"""
Script de prueba para el sistema de conexión inteligente
Muestra cómo cambiar entre diferentes bases de datos
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Configurar path del proyecto
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Cargar variables de entorno
load_dotenv()

def test_smart_connection():
    """Prueba el sistema de conexión inteligente"""
    print("=== PRUEBA DE CONEXIÓN INTELIGENTE ===\n")

    try:
        from src.core.database import get_users_connection, get_inventario_connection, get_auditoria_connection

        print("1. Conectando a base de datos 'users'...")
        users_db = get_users_connection(auto_connect=True)
        print(f"   - Base de datos actual: {users_db.database}")

        print("\n2. Cambiando a base de datos 'inventario'...")
        inventario_db = get_inventario_connection(auto_connect=True)
        print(f"   - Base de datos actual: {inventario_db.database}")

        print("\n3. Cambiando a base de datos 'auditoria'...")
        auditoria_db = get_auditoria_connection(auto_connect=True)
        print(f"   - Base de datos actual: {auditoria_db.database}")

        print("\n4. Verificando que es la misma conexión...")
        print(f"   - users_db es inventario_db: {users_db is inventario_db}")
        print(f"   - inventario_db es auditoria_db: {inventario_db is auditoria_db}")

        print("\n5. Realizando consulta de prueba...")
        result = auditoria_db.execute_query("SELECT 1 as test")
        if result:
            print(f"   OK Consulta exitosa: {result}")
        else:
            print("   ERROR Consulta falló")

        return True

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_traditional_connections():
    """Prueba las clases tradicionales para comparación"""
    print("\n=== PRUEBA DE CONEXIONES TRADICIONALES ===\n")

    try:
        from src.core.database import UsersDatabaseConnection, InventarioDatabaseConnection

        print("1. Creando conexión tradicional a 'users'...")
        users_db = UsersDatabaseConnection(auto_connect=True)
        print(f"   - Base de datos: {users_db.database}")

        print("\n2. Creando conexión tradicional a 'inventario'...")
        inventario_db = InventarioDatabaseConnection(auto_connect=True)
        print(f"   - Base de datos: {inventario_db.database}")

        print("\n3. Verificando que son conexiones separadas...")
        print(f"   - users_db es inventario_db: {users_db is inventario_db}")

        return True

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Probando sistema de conexión inteligente...\n")

    # Verificar variables de entorno
    print("Variables de entorno:")
    print(f"  DB_SERVER: {os.getenv('DB_SERVER', 'NO CONFIGURADO')}")
    print(f"  DB_USERS: {os.getenv('DB_USERS', 'NO CONFIGURADO')}")
    print(f"  DB_INVENTARIO: {os.getenv('DB_INVENTARIO', 'NO CONFIGURADO')}")
    print(f"  DB_AUDITORIA: {os.getenv('DB_AUDITORIA', 'NO CONFIGURADO')}")
    print()

    # Ejecutar pruebas
    smart_ok = test_smart_connection()
    traditional_ok = test_traditional_connections()

    print("\n=== RESUMEN ===")
    print(f"Conexión inteligente: {'OK' if smart_ok else 'ERROR'}")
    print(f"Conexiones tradicionales: {'OK' if traditional_ok else 'ERROR'}")

    if smart_ok and traditional_ok:
        print("\nTodas las pruebas pasaron. Sistema funcionando correctamente.")
        print("\nUSO RECOMENDADO:")
        print("- Para módulos nuevos: usar get_[nombre]_connection()")
        print("- Las funciones reutilizan la misma conexión cambiando solo la DB")
        print("- Más eficiente que crear múltiples conexiones")
        sys.exit(0)
    else:
        print("\nAlgunas pruebas fallaron. Revisa la configuración.")
        sys.exit(1)
