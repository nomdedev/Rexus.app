#!/usr/bin/env python3
"""
Script de validación para el módulo de usuarios refactorizado
"""

import os
import sys

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_imports():
    """Prueba las importaciones del módulo refactorizado."""
    print("🔍 Validando importaciones del módulo usuarios...")

    try:
        # Importar submódulos
        from rexus.modules.usuarios.submodules import (
            AutenticacionManager,
            ConsultasManager,
            UsuariosManager,
        )

        print("[CHECK] Submódulos importados correctamente")

        # Importar modelo refactorizado
        from rexus.modules.usuarios.model_refactorizado import (
            ModeloUsuariosRefactorizado,
        )

        print("[CHECK] Modelo refactorizado importado correctamente")

        return True

    except Exception as e:
        print(f"[ERROR] Error en importaciones: {str(e)}")
        return False


def test_structure():
    """Valida la estructura del modelo refactorizado."""
    print("\n🔍 Validando estructura del modelo refactorizado...")

    try:
        from rexus.modules.usuarios.model_refactorizado import (
            ModeloUsuariosRefactorizado,
        )

        # Crear instancia sin conexión DB
        modelo = ModeloUsuariosRefactorizado()

        # Verificar que tiene los submódulos
        if not hasattr(modelo, "autenticacion_manager"):
            raise AssertionError("Falta autenticacion_manager")
        if not hasattr(modelo, "usuarios_manager"):
            raise AssertionError("Falta usuarios_manager")
        if not hasattr(modelo, "consultas_manager"):
            raise AssertionError("Falta consultas_manager")

        # Verificar métodos principales
        metodos_esperados = [
            "autenticar_usuario_seguro",
            "crear_usuario",
            "obtener_usuario_por_id",
            "actualizar_usuario",
            "eliminar_usuario",
            "buscar_usuarios",
            "obtener_estadisticas_usuarios",
        ]

        for metodo in metodos_esperados:
            if not hasattr(modelo, metodo):
                raise AssertionError(f"Falta método {metodo}")

        print("[CHECK] Estructura del modelo validada")

        # Probar método de información
        info = modelo.obtener_info_modular()
        if "modelo" not in info:
            raise AssertionError("Falta información del modelo")
        if "submodulos" not in info:
            raise AssertionError("Falta información de submódulos")

        print(f"[CHECK] Información modular: {info['modelo']} v{info['version']}")

        return True

    except Exception as e:
        print(f"[ERROR] Error validando estructura: {str(e)}")
        return False


def test_submodules():
    """Valida la estructura de los submódulos."""
    print("\n🔍 Validando submódulos individuales...")

    try:
        from rexus.modules.usuarios.submodules import (
            AutenticacionManager,
            ConsultasManager,
            UsuariosManager,
        )

        # Crear instancias
        am = AutenticacionManager()
        um = UsuariosManager()
        cm = ConsultasManager()

        # Verificar métodos específicos de cada submódulo
        if not hasattr(am, "autenticar_usuario_seguro"):
            raise AssertionError(
                "AutenticacionManager: falta autenticar_usuario_seguro"
            )
        if not hasattr(am, "validar_fortaleza_password"):
            raise AssertionError(
                "AutenticacionManager: falta validar_fortaleza_password"
            )

        if not hasattr(um, "crear_usuario"):
            raise AssertionError("UsuariosManager: falta crear_usuario")
        if not hasattr(um, "obtener_usuario_por_id"):
            raise AssertionError("UsuariosManager: falta obtener_usuario_por_id")

        if not hasattr(cm, "buscar_usuarios"):
            raise AssertionError("ConsultasManager: falta buscar_usuarios")
        if not hasattr(cm, "obtener_estadisticas_usuarios"):
            raise AssertionError(
                "ConsultasManager: falta obtener_estadisticas_usuarios"
            )

        print("[CHECK] Submódulos validados correctamente")
        return True

    except Exception as e:
        print(f"[ERROR] Error validando submódulos: {str(e)}")
        return False


def main():
    """Ejecuta todas las validaciones."""
    print("[ROCKET] Iniciando validación del módulo usuarios refactorizado")
    print("=" * 60)

    tests = [test_imports, test_structure, test_submodules]

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
        print("🎉 ¡Refactorización de usuarios completada exitosamente!")
        print("\n📋 Próximos pasos:")
        print("   1. Crear archivos SQL externos")
        print("   2. Validar integración con controlador existente")
        print("   3. Ejecutar tests de funcionalidad")
        return True
    else:
        print("[WARN]  Refactorización incompleta. Revisar errores.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
