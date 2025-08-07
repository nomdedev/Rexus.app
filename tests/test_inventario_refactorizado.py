#!/usr/bin/env python3
"""
Script de validación para el módulo inventario refactorizado
"""

import os
import sys

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_imports():
    """Prueba las importaciones del módulo refactorizado."""
    print("🔍 Validando importaciones del módulo inventario...")

    try:
        # Importar submódulos
        from rexus.modules.inventario.submodules import (
            ConsultasManager,
            MovimientosManager,
            ProductosManager,
        )

        print("✅ Submódulos importados correctamente")

        # Importar modelo refactorizado
        from rexus.modules.inventario.model_refactorizado import (
            InventarioModelRefactorizado,
        )

        print("✅ Modelo refactorizado importado correctamente")

        return True

    except Exception as e:
        print(f"❌ Error en importaciones: {str(e)}")
        return False


def test_structure():
    """Valida la estructura del modelo refactorizado."""
    print("\n🔍 Validando estructura del modelo refactorizado...")

    try:
        from rexus.modules.inventario.model_refactorizado import (
            InventarioModelRefactorizado,
        )

        # Crear instancia sin conexión DB
        modelo = InventarioModelRefactorizado()

        # Verificar que tiene los submódulos
        if not hasattr(modelo, "productos_manager"):
            raise AssertionError("Falta productos_manager")
        if not hasattr(modelo, "movimientos_manager"):
            raise AssertionError("Falta movimientos_manager")
        if not hasattr(modelo, "consultas_manager"):
            raise AssertionError("Falta consultas_manager")

        # Verificar métodos principales
        metodos_esperados = [
            "crear_producto",
            "obtener_producto_por_id",
            "actualizar_producto",
            "eliminar_producto",
            "registrar_movimiento",
            "obtener_productos_paginados",
            "obtener_estadisticas_inventario",
        ]

        for metodo in metodos_esperados:
            if not hasattr(modelo, metodo):
                raise AssertionError(f"Falta método {metodo}")

        print("✅ Estructura del modelo validada")

        # Probar método de información (si existe)
        if hasattr(modelo, "obtener_info_modular"):
            info = modelo.obtener_info_modular()
            if "modelo" not in info:
                raise AssertionError("Falta información del modelo")
            print(f"✅ Información modular: {info['modelo']}")
        else:
            print("⚠️  Sin método obtener_info_modular")

        return True

    except Exception as e:
        print(f"❌ Error validando estructura: {str(e)}")
        return False


def test_submodules():
    """Valida la estructura de los submódulos."""
    print("\n🔍 Validando submódulos individuales...")

    try:
        from rexus.modules.inventario.submodules import (
            ConsultasManager,
            MovimientosManager,
            ProductosManager,
        )

        # Crear instancias
        pm = ProductosManager()
        mm = MovimientosManager()
        cm = ConsultasManager()

        # Verificar métodos específicos de cada submódulo
        if not hasattr(pm, "crear_producto"):
            raise AssertionError("ProductosManager: falta crear_producto")
        if not hasattr(pm, "obtener_producto_por_id"):
            raise AssertionError("ProductosManager: falta obtener_producto_por_id")

        if not hasattr(mm, "registrar_movimiento"):
            raise AssertionError("MovimientosManager: falta registrar_movimiento")
        if not hasattr(mm, "obtener_movimientos_producto"):
            raise AssertionError(
                "MovimientosManager: falta obtener_movimientos_producto"
            )

        if not hasattr(cm, "obtener_productos_paginados"):
            raise AssertionError("ConsultasManager: falta obtener_productos_paginados")
        if not hasattr(cm, "obtener_estadisticas_inventario"):
            raise AssertionError(
                "ConsultasManager: falta obtener_estadisticas_inventario"
            )

        print("✅ Submódulos validados correctamente")
        return True

    except Exception as e:
        print(f"❌ Error validando submódulos: {str(e)}")
        return False


def test_sql_files():
    """Valida que existan los archivos SQL necesarios."""
    print("\n🔍 Validando archivos SQL...")

    base_path = "scripts/sql/inventario"
    expected_files = [
        "insert_producto.sql",
        "select_by_id.sql",
        "update_producto.sql",
        "insert_movimiento.sql",
        "select_movimientos.sql",
        "select_productos_paginados.sql",
        "select_estadisticas.sql",
        "select_all_productos.sql",
    ]

    found = 0
    total = len(expected_files)

    for file_path in expected_files:
        full_path = os.path.join(base_path, file_path)
        if os.path.exists(full_path):
            print(f"✅ Encontrado: {file_path}")
            found += 1
        else:
            print(f"⚠️  Faltante: {file_path}")

    print(f"📊 Archivos SQL: {found}/{total} encontrados")
    return found >= total * 0.8  # 80% de archivos requeridos


def main():
    """Ejecuta todas las validaciones."""
    print("🚀 Validando estado del módulo inventario refactorizado")
    print("=" * 60)

    tests = [test_imports, test_structure, test_submodules, test_sql_files]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Error inesperado en {test.__name__}: {str(e)}")

    print("\n" + "=" * 60)
    print(f"📊 Resumen de validación: {passed}/{total} pruebas pasaron")

    if passed == total:
        print("🎉 ¡Módulo inventario ya está refactorizado!")
        print("\n📋 Estado encontrado:")
        print("   ✅ Arquitectura modular implementada")
        print("   ✅ Submódulos especializados")
        print("   ✅ Archivos SQL organizados")
        print("   ✅ Imports unificados")
        return True
    else:
        print("🔧 Refactorización parcial detectada")
        print("\n📋 Necesita completarse:")
        if passed < total:
            print("   🔸 Algunos elementos requieren ajustes")
            print("   🔸 Aplicar metodología completa")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
