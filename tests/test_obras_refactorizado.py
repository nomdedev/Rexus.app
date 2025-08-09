#!/usr/bin/env python3
"""
Script de validación para el módulo de obras refactorizado
"""

import os
import sys

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_imports():
    """Prueba las importaciones del módulo refactorizado."""
    print("🔍 Validando importaciones del módulo obras...")

    try:
        # Importar submódulos
        from rexus.modules.obras.submodules import (
            ConsultasManager,
            ProyectosManager,
            RecursosManager,
        )

        print("[CHECK] Submódulos importados correctamente")

        # Importar modelo refactorizado
        from rexus.modules.obras.model_refactorizado import ModeloObrasRefactorizado

        print("[CHECK] Modelo refactorizado importado correctamente")

        # Importar desde __init__.py
        from rexus.modules.obras import ConsultasManager as CM2
        from rexus.modules.obras import ModeloObrasRefactorizado as MOR2
        from rexus.modules.obras import ProyectosManager as PM2
        from rexus.modules.obras import RecursosManager as RM2

        print("[CHECK] Importaciones desde __init__.py funcionando")

        return True

    except Exception as e:
        print(f"[ERROR] Error en importaciones: {str(e)}")
        return False


def test_structure():
    """Valida la estructura del modelo refactorizado."""
    print("\n🔍 Validando estructura del modelo refactorizado...")

    try:
        from rexus.modules.obras.model_refactorizado import ModeloObrasRefactorizado

        # Crear instancia sin conexión DB
        modelo = ModeloObrasRefactorizado()

        # Verificar que tiene los submódulos
        assert hasattr(modelo, "proyectos_manager"), "Falta proyectos_manager"
        assert hasattr(modelo, "recursos_manager"), "Falta recursos_manager"
        assert hasattr(modelo, "consultas_manager"), "Falta consultas_manager"

        # Verificar métodos principales
        metodos_esperados = [
            "obtener_obra_por_id",
            "crear_obra",
            "actualizar_obra",
            "eliminar_obra",
            "buscar_obras",
            "obtener_estadisticas_obras",
        ]

        for metodo in metodos_esperados:
            assert hasattr(modelo, metodo), f"Falta método {metodo}"

        print("[CHECK] Estructura del modelo validada")

        # Probar método de información
        info = modelo.obtener_info_modular()
        assert "modelo" in info, "Falta información del modelo"
        assert "submodulos" in info, "Falta información de submódulos"
        print(f"[CHECK] Información modular: {info['modelo']} v{info['version']}")

        return True

    except Exception as e:
        print(f"[ERROR] Error validando estructura: {str(e)}")
        return False


def test_submodules():
    """Valida la estructura de los submódulos."""
    print("\n🔍 Validando submódulos individuales...")

    try:
        from rexus.modules.obras.submodules import (
            ConsultasManager,
            ProyectosManager,
            RecursosManager,
        )

        # Crear instancias
        pm = ProyectosManager()
        rm = RecursosManager()
        cm = ConsultasManager()

        # Verificar métodos específicos de cada submódulo
        assert hasattr(pm, "obtener_obra_por_id"), (
            "ProyectosManager: falta obtener_obra_por_id"
        )
        assert hasattr(pm, "crear_obra"), "ProyectosManager: falta crear_obra"
        assert hasattr(pm, "cambiar_estado_obra"), (
            "ProyectosManager: falta cambiar_estado_obra"
        )

        assert hasattr(rm, "asignar_material_obra"), (
            "RecursosManager: falta asignar_material_obra"
        )
        assert hasattr(rm, "obtener_materiales_obra"), (
            "RecursosManager: falta obtener_materiales_obra"
        )

        assert hasattr(cm, "buscar_obras"), "ConsultasManager: falta buscar_obras"
        assert hasattr(cm, "obtener_estadisticas_obras"), (
            "ConsultasManager: falta obtener_estadisticas_obras"
        )

        print("[CHECK] Submódulos validados correctamente")
        return True

    except Exception as e:
        print(f"[ERROR] Error validando submódulos: {str(e)}")
        return False


def test_sql_files():
    """Verifica que los archivos SQL existan."""
    print("\n🔍 Validando archivos SQL...")

    sql_files = [
        "scripts/sql/obras/proyectos/proyectos_obras.sql",
        "scripts/sql/obras/recursos/recursos_obras.sql",
        "scripts/sql/obras/consultas/consultas_obras.sql",
    ]

    missing_files = []

    for sql_file in sql_files:
        if not os.path.exists(sql_file):
            missing_files.append(sql_file)
        else:
            print(f"[CHECK] Encontrado: {sql_file}")

    if missing_files:
        print(f"[ERROR] Archivos SQL faltantes: {missing_files}")
        return False
    else:
        print("[CHECK] Todos los archivos SQL encontrados")
        return True


def main():
    """Ejecuta todas las validaciones."""
    print("[ROCKET] Iniciando validación del módulo obras refactorizado")
    print("=" * 60)

    tests = [test_imports, test_structure, test_submodules, test_sql_files]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"[ERROR] Error inesperado en {test.__name__}: {str(e)}")

    print("\n" + "=" * 60)
    print(f"[CHART] Resumen de validación: {passed}/{total} pruebas pasaron")

    if passed == total:
        print("🎉 ¡Refactorización de obras completada exitosamente!")
        print("\n📋 Próximos pasos:")
        print("   1. Validar integración con controlador existente")
        print("   2. Ejecutar tests de funcionalidad")
        print("   3. Proceder con siguiente módulo (usuarios)")
        return True
    else:
        print("[WARN]  Refactorización incompleta. Revisar errores.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
