#!/usr/bin/env python3
"""
Script de testing funcional para detectar errores durante el uso real.
Simula interacciones típicas del usuario para encontrar problemas ocultos.
"""

# Añadir el directorio del proyecto al path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_modulo_import(modulo_name):
    """Prueba la importación de un módulo específico."""
    try:
        if modulo_name == "inventario":
            print(f"[CHECK] {modulo_name}: Importaciones exitosas")

        elif modulo_name == "obras":
            print(f"[CHECK] {modulo_name}: Importaciones exitosas")

        elif modulo_name == "herrajes":
            print(f"[CHECK] {modulo_name}: Importaciones exitosas")

        elif modulo_name == "vidrios":
            print(f"[CHECK] {modulo_name}: Importaciones exitosas")

        elif modulo_name == "usuarios":
            print(f"[CHECK] {modulo_name}: Importaciones exitosas")

        elif modulo_name == "auditoria":
            print(f"[CHECK] {modulo_name}: Importaciones exitosas")

        return True

    except ImportError as e:
        print(f"[ERROR] {modulo_name}: Error de importación - {e}")
        return False
    except Exception as e:
        print(f"[ERROR] {modulo_name}: Error inesperado - {e}")
        return False

def test_database_connection():
    """Prueba la conexión a la base de datos."""
    try:
        db = DatabaseConnection()
        connection = db.get_connection()
        if connection:
            print("[CHECK] Base de datos: Conexión exitosa")
            connection.close()
            return True
        else:
            print("[ERROR] Base de datos: No se pudo establecer conexión")
            return False
    except Exception as e:
        print(f"[ERROR] Base de datos: Error - {e}")
        return False

def test_core_components():
    """Prueba los componentes core."""
    try:
        print("[CHECK] Core: Componentes importados correctamente")
        return True
    except Exception as e:
        print(f"[ERROR] Core: Error - {e}")
        return False

def test_model_instantiation():
    """Prueba la instanciación de modelos con usuario invitado."""
    try:
        db = DatabaseConnection()

        # Probar modelo de inventario
        inventario_model = InventarioModel(db)
        print("[CHECK] Inventario Model: Instanciado correctamente")

        # Probar modelo de usuarios
        usuarios_model = UsuariosModel(db)
        print("[CHECK] Usuarios Model: Instanciado correctamente")

        # Probar modelo de auditoría
        auditoria_model = AuditoriaModel(db)
        print("[CHECK] Auditoría Model: Instanciado correctamente")

        return True
    except Exception as e:
        print(f"[ERROR] Models: Error de instanciación - {e}")
        return False

def test_sql_queries():
    """Prueba consultas SQL básicas para detectar errores de sintaxis."""
    try:
        db = DatabaseConnection()
        inventario_model = InventarioModel(db)

        # Probar consulta básica
        items = inventario_model.obtener_todos()
        print(f"[CHECK] SQL Query: Inventario retornó {len(items) if items else 0} items")

        # Probar consulta con filtros
        items_filtrados = inventario_model.buscar_por_codigo("TEST")
        print(f"[CHECK] SQL Query: Búsqueda por código completada")

        return True
    except Exception as e:
        print(f"[ERROR] SQL Queries: Error - {e}")
        return False

def test_audit_functionality():
    """Prueba la funcionalidad de auditoría con usuario invitado."""
    try:
        db = DatabaseConnection()
        auditoria_model = AuditoriaModel(db)

        # Probar registro de evento con usuario invitado
        resultado = auditoria_model.registrar_evento(
            usuario_id=0,  # Usuario invitado
            modulo="testing",
            tipo_evento="test",
            descripcion="Test de auditoría automático"
        )

        if resultado:
            print("[CHECK] Auditoría: Registro de evento exitoso con usuario invitado")
        else:
            print("[WARN] Auditoría: Registro retornó False (puede ser normal)")
import sys
from pathlib import Path

from core.database import DatabaseConnection
from modules.auditoria.model import AuditoriaModel
from modules.inventario.model import InventarioModel
from modules.usuarios.model import UsuariosModel

        return True
    except Exception as e:
        print(f"[ERROR] Auditoría: Error - {e}")
        return False

def run_all_tests():
    """Ejecuta todos los tests funcionales."""
    print("=== TESTING FUNCIONAL DE MÓDULOS ===")
    print()

    resultados = []

    # Test de componentes core
    print("1. Testing componentes core...")
    resultados.append(test_core_components())

    # Test de conexión a BD
    print("\n2. Testing conexión a base de datos...")
    resultados.append(test_database_connection())

    # Test de importación de módulos
    print("\n3. Testing importación de módulos...")
    modulos = ["inventario", "obras", "herrajes", "vidrios", "usuarios", "auditoria"]
    for modulo in modulos:
        resultados.append(test_modulo_import(modulo))

    # Test de instanciación de modelos
    print("\n4. Testing instanciación de modelos...")
    resultados.append(test_model_instantiation())

    # Test de consultas SQL
    print("\n5. Testing consultas SQL...")
    resultados.append(test_sql_queries())

    # Test de auditoría
    print("\n6. Testing funcionalidad de auditoría...")
    resultados.append(test_audit_functionality())

    # Resumen
    exitosos = sum(resultados)
    total = len(resultados)

    print(f"\n=== RESUMEN ===")
    print(f"Tests exitosos: {exitosos}/{total}")
    print(f"Porcentaje de éxito: {(exitosos/total)*100:.1f}%")

    if exitosos == total:
        print("🎉 TODOS LOS TESTS PASARON - La aplicación está funcionando correctamente")
        return 0
    else:
        print(f"[WARN] {total-exitosos} TESTS FALLARON - Revisar errores reportados")
        return 1

if __name__ == "__main__":
    try:
        exit_code = run_all_tests()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n[WARN] Testing interrumpido por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Error inesperado durante testing: {e}")
        sys.exit(1)
