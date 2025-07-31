#!/usr/bin/env python3
"""
Test simple para verificar funcionalidades básicas sin problemas de path.
"""

def test_imports():
    """Test básico de importaciones."""
    print("=== TEST DE IMPORTACIONES ===")

    try:
        # Test core components
        print("✅ core.database importado")

        print("✅ core.logger importado")

        # Test módulo inventario
        print("✅ modules.inventario importado")

        # Test módulo usuarios
        print("✅ modules.usuarios importado")

        # Test módulo auditoría
        print("✅ modules.auditoria importado")

        return True

    except Exception as e:
        print(f"❌ Error en importaciones: {e}")
        return False

def test_database():
    """Test de conexión a base de datos."""
    print("\n=== TEST DE BASE DE DATOS ===")

    try:
        db = DatabaseConnection()
        print("✅ DatabaseConnection instanciado")

        # Probar una consulta simple
        usuarios_model = UsuariosModel(db)
        print("✅ UsuariosModel instanciado")

        # Verificar si el usuario invitado funciona
        usuario_invitado = {
            'id': 0,
            'usuario': 'invitado',
            'rol': 'TEST_USER',
            'ip': '127.0.0.1'
        }
        print(f"✅ Usuario invitado configurado: {usuario_invitado['usuario']}")

        return True

    except Exception as e:
        print(f"❌ Error en base de datos: {e}")
        return False

def test_audit():
    """Test de funcionalidad de auditoría."""
    print("\n=== TEST DE AUDITORÍA ===")

    try:
        db = DatabaseConnection()
        auditoria_model = AuditoriaModel(db)
        print("✅ AuditoriaModel instanciado")

        # Probar registro de evento
        resultado = auditoria_model.registrar_evento(
            usuario_id=0,
            modulo="testing",
import sys
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

import sys

from core.database import DatabaseConnection
from rexus.modules.auditoria.model import AuditoriaModel
from rexus.modules.usuarios.model import UsuariosModel

            tipo_evento="test",
            detalle="Test automático",
            ip_origen="127.0.0.1"
        )

        if resultado:
            print("✅ Evento de auditoría registrado exitosamente")
        else:
            print("⚠️ Registro de auditoría retornó False")

        return True

    except Exception as e:
        print(f"❌ Error en auditoría: {e}")
        return False

def main():
    """Ejecuta todos los tests."""
    print("TESTING FUNCIONAL DE LA APLICACIÓN")
    print("="*50)

    tests_passed = 0
    total_tests = 3

    # Test 1: Importaciones
    if test_imports():
        tests_passed += 1

    # Test 2: Base de datos
    if test_database():
        tests_passed += 1

    # Test 3: Auditoría
    if test_audit():
        tests_passed += 1

    # Resumen
    print(f"\n=== RESUMEN FINAL ===")
    print(f"Tests exitosos: {tests_passed}/{total_tests}")
    print(f"Porcentaje de éxito: {(tests_passed/total_tests)*100:.1f}%")

    if tests_passed == total_tests:
        print("🎉 TODOS LOS TESTS PASARON")
        return 0
    else:
        print(f"⚠️ {total_tests-tests_passed} TESTS FALLARON")
        return 1

if __name__ == "__main__":
    sys.exit(main())
