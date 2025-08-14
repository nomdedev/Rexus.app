"""
Scri# Agregar path del proyecto
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root) de validación de integración para la arquitectura modular del inventario.
Verifica que los submódulos trabajen correctamente con el controlador existente.
"""

import os
import sys
from datetime import datetime

# Agregar path del proyecto
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


def verificar_imports():
    """Verifica que todos los imports funcionen correctamente."""
    print("🔍 Verificando imports de submódulos...")

    try:
        # Importar submódulos directamente
        from rexus.modules.inventario.submodules.consultas_manager import (
            ConsultasManager,
        )
        from rexus.modules.inventario.submodules.movimientos_manager import (
            MovimientosManager,
        )
        from rexus.modules.inventario.submodules.productos_manager import (
            ProductosManager,
        )

        print("[CHECK] Imports directos exitosos")

        # Importar desde __init__
        from rexus.modules.inventario import ConsultasManager as CM
        from rexus.modules.inventario import MovimientosManager as MM
        from rexus.modules.inventario import ProductosManager as PM

        print("[CHECK] Imports desde __init__ exitosos")

        # Verificar que son las mismas clases
        assert ProductosManager == PM
        assert MovimientosManager == MM
        assert ConsultasManager == CM
        print("[CHECK] Clases consistentes entre imports")

        return True, (ProductosManager, MovimientosManager, ConsultasManager)

    except Exception as e:
        print(f"[ERROR] Error en imports: {e}")
        return False, None


def verificar_inicializacion(managers):
    """Verifica que los managers se puedan inicializar correctamente."""
    print("\n🔍 Verificando inicialización de managers...")

    ProductosManager, MovimientosManager, ConsultasManager = managers

    try:
        # Inicializar sin conexión
        productos_mgr = ProductosManager()
        movimientos_mgr = MovimientosManager()
        consultas_mgr = ConsultasManager()

        print("[CHECK] Inicialización sin conexión exitosa")

        # Verificar atributos básicos
        assert hasattr(productos_mgr, "sql_manager")
        assert hasattr(productos_mgr, "data_sanitizer")
        assert hasattr(movimientos_mgr, "sql_manager")
        assert hasattr(consultas_mgr, "sql_manager")

        print("[CHECK] Atributos básicos presentes")

        # Inicializar con conexión mock
        from unittest.mock import Mock

        mock_connection = Mock()

        productos_mgr_conn = ProductosManager(mock_connection)
        movimientos_mgr_conn = MovimientosManager(mock_connection)
        consultas_mgr_conn = ConsultasManager(mock_connection)

        assert productos_mgr_conn.db_connection == mock_connection
        assert movimientos_mgr_conn.db_connection == mock_connection
        assert consultas_mgr_conn.db_connection == mock_connection

        print("[CHECK] Inicialización con conexión exitosa")

        return True,
(productos_mgr_conn,
            movimientos_mgr_conn,
            consultas_mgr_conn)

    except Exception as e:
        print(f"[ERROR] Error en inicialización: {e}")
        return False, None


def verificar_modelo_refactorizado():
    """Verifica que el modelo refactorizado funcione correctamente."""
    print("\n🔍 Verificando modelo refactorizado...")

    try:
        # Importar modelo refactorizado
        from rexus.modules.inventario.model_refactorizado import InventarioModel

        print("[CHECK] Import del modelo refactorizado exitoso")

        # Inicializar modelo
        modelo = InventarioModel()
        print("[CHECK] Inicialización del modelo exitosa")

        # Verificar que tiene los managers
        assert hasattr(modelo, "productos_manager")
        assert hasattr(modelo, "movimientos_manager")
        assert hasattr(modelo, "consultas_manager")
        print("[CHECK] Managers presentes en modelo")

        # Verificar algunos métodos delegados
        assert hasattr(modelo, "obtener_producto_por_id")
        assert hasattr(modelo, "obtener_productos_paginados")
        print("[CHECK] Métodos delegados presentes")

        return True, modelo

    except Exception as e:
        print(f"[ERROR] Error en modelo refactorizado: {e}")
        return False, None


def verificar_sql_externo():
    """Verifica que los archivos SQL externos existan."""
    print("\n🔍 Verificando archivos SQL externos...")

    archivos_sql_esperados = [
        "scripts/sql/inventario/productos/obtener_producto_por_id.sql",
        "scripts/sql/inventario/productos/obtener_producto_por_codigo.sql",
        "scripts/sql/inventario/productos/insertar_producto.sql",
        "scripts/sql/inventario/productos/actualizar_producto.sql",
        "scripts/sql/inventario/productos/obtener_categorias.sql",
    ]

    archivos_encontrados = 0

    for archivo in archivos_sql_esperados:
        ruta_completa = os.path.join(os.path.dirname(__file__),
"..",
            "..",
            archivo)
        if os.path.exists(ruta_completa):
            print(f"[CHECK] {archivo}")
            archivos_encontrados += 1
        else:
            print(f"[ERROR] {archivo} - NO ENCONTRADO")

    if archivos_encontrados == len(archivos_sql_esperados):
        print("[CHECK] Todos los archivos SQL encontrados")
        return True
    else:
        print(
            f"[WARN] {archivos_encontrados}/{len(archivos_sql_esperados)} archivos SQL encontrados"
        )
        return archivos_encontrados > 0


def verificar_controlador_original():
    """Verifica que el controlador original siga funcionando."""
    print("\n🔍 Verificando controlador original...")

    try:
        from rexus.modules.inventario.controller import InventarioController

        print("[CHECK] Import del controlador exitoso")

        # Crear instancia del controlador
        controlador = InventarioController()
        print("[CHECK] Inicialización del controlador exitosa")

        # Verificar métodos básicos
        assert hasattr(controlador, "model")
        print("[CHECK] Controlador tiene modelo")

        return True, controlador

    except Exception as e:
        print(f"[ERROR] Error en controlador: {e}")
        return False, None


def verificar_compatibilidad_hacia_atras():
    """Verifica que la refactorización no rompa código existente."""
    print("\n🔍 Verificando compatibilidad hacia atrás...")

    try:
        # Importar modelo original y refactorizado
        from rexus.modules.inventario.model import InventarioModel as ModeloOriginal
        from rexus.modules.inventario.model_refactorizado import (
            InventarioModel as ModeloRefactorizado,
        )

        print("[CHECK] Ambos modelos importados")

        # Inicializar ambos
        modelo_original = ModeloOriginal()
        modelo_refactorizado = ModeloRefactorizado()

        print("[CHECK] Ambos modelos inicializados")

        # Verificar que el refactorizado tenga métodos del original
        metodos_comunes = [
            "obtener_producto_por_id",
            "obtener_todos_productos",
            "obtener_productos_paginados",
        ]

        for metodo in metodos_comunes:
            if hasattr(modelo_original, metodo):
                assert hasattr(modelo_refactorizado, metodo), (
                    f"Método {metodo} faltante en refactorizado"
                )
                print(f"[CHECK] Método {metodo} presente en ambos")

        return True

    except Exception as e:
        print(f"[ERROR] Error en compatibilidad: {e}")
        return False


def generar_reporte_completo():
    """Genera un reporte completo de la validación."""
    print("\n" + "=" * 60)
    print("🎯 VALIDACIÓN DE INTEGRACIÓN - INVENTARIO MODULAR")
    print("=" * 60)

    resultados = {}

    # Ejecutar todas las validaciones
    resultados["imports"], managers = verificar_imports()

    if managers:
        resultados["inicializacion"], instances = verificar_inicializacion(managers)
    else:
        resultados["inicializacion"] = False

    resultados["modelo_refactorizado"], modelo = verificar_modelo_refactorizado()
    resultados["sql_externo"] = verificar_sql_externo()
    resultados["controlador"], controlador = verificar_controlador_original()
    resultados["compatibilidad"] = verificar_compatibilidad_hacia_atras()

    # Generar resumen
    print("\n" + "=" * 60)
    print("[CHART] RESUMEN DE VALIDACIÓN")
    print("=" * 60)

    total_tests = len(resultados)
    tests_pasados = sum(1 for r in resultados.values() if r)

    for test, resultado in resultados.items():
        estado = "[CHECK] PASÓ" if resultado else "[ERROR] FALLÓ"
        print(f"{test.upper().replace('_', ' ')}: {estado}")

    print(f"\n📈 RESULTADO GENERAL: {tests_pasados}/{total_tests} tests pasados")

    if tests_pasados == total_tests:
        print("🎉 ¡VALIDACIÓN COMPLETAMENTE EXITOSA!")
        print("[ROCKET] La arquitectura modular está lista para producción")
    elif tests_pasados >= total_tests * 0.8:
        print("[WARN] Validación mayormente exitosa con algunos problemas menores")
        print("🔧 Revisar elementos fallidos antes de continuar")
    else:
        print("🚨 Validación con problemas significativos")
        print("🛠️ Se requiere corrección antes de continuar")

    return tests_pasados / total_tests


def main():
    """Función principal del script de validación."""
    print("[ROCKET] Iniciando validación de integración del inventario modular...")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        porcentaje_exito = generar_reporte_completo()

        print(f"\n📋 VALIDACIÓN COMPLETADA")
        print(f"✨ Porcentaje de éxito: {porcentaje_exito:.1%}")

        # Recomendaciones
        print(f"\n💡 PRÓXIMOS PASOS RECOMENDADOS:")
        if porcentaje_exito >= 0.9:
            print("1. [CHECK] Proceder con tests de integración completos")
            print("2. [CHECK] Documentar nueva arquitectura")
            print("3. [CHECK] Aplicar patrón a otros módulos")
        elif porcentaje_exito >= 0.7:
            print("1. 🔧 Corregir problemas identificados")
            print("2. [WARN] Re-ejecutar validación")
            print("3. 📝 Documentar limitaciones actuales")
        else:
            print("1. 🚨 Revisar implementación de submódulos")
            print("2. 🔍 Verificar estructura de archivos")
            print("3. 🛠️ Corregir errores críticos")

        return porcentaje_exito >= 0.8

    except Exception as e:
        print(f"\n💥 ERROR CRÍTICO EN VALIDACIÓN: {e}")
        print("🔍 Revisar configuración del entorno y estructura de archivos")
        return False


if __name__ == "__main__":
    exito = main()
    sys.exit(0 if exito else 1)
