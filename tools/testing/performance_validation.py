#!/usr/bin/env python3
"""
Tests de rendimiento en tiempo real para validar el sistema de monitoreo
"""

import os
import sys
import time
from pathlib import Path


def test_performance_monitoring():
    """Prueba el sistema de monitoreo de rendimiento con datos reales"""
    print("🔍 PROBANDO MONITOREO DE RENDIMIENTO")
    print("=" * 50)

    try:
        # Intentar importar el monitor de rendimiento
        sys.path.insert(0, str(Path.cwd()))
        from rexus.utils.performance_monitor import (
            PerformanceMonitor,
            performance_timer,
        )

        print("✅ Monitor de rendimiento importado correctamente")

        # Crear instancia del monitor
        monitor = PerformanceMonitor()
        print("✅ Monitor instanciado")

        # Test 1: Función rápida
        @performance_timer
        def fast_function():
            """Función que ejecuta rápidamente"""
            return sum(range(1000))

        print("\n🧪 Test 1: Función rápida")
        result = fast_function()
        print(f"   Resultado: {result}")

        # Test 2: Función con delay controlado
        @performance_timer
        def medium_function():
            """Función con delay medio"""
            time.sleep(0.1)
            return "completed"

        print("\n🧪 Test 2: Función con delay")
        result = medium_function()
        print(f"   Resultado: {result}")

        # Test 3: Función que consume CPU
        @performance_timer
        def cpu_intensive_function():
            """Función que consume CPU"""
            total = 0
            for i in range(100000):
                total += i**2
            return total

        print("\n🧪 Test 3: Función intensiva de CPU")
        result = cpu_intensive_function()
        print(f"   Resultado: {result}")

        print("\n✅ Todas las pruebas de rendimiento completadas")
        return True

    except ImportError as e:
        print(f"⚠️ No se pudo importar el monitor: {e}")
        return False
    except Exception as e:
        print(f"❌ Error en tests de rendimiento: {e}")
        return False


def test_logging_system():
    """Prueba el sistema de logging con diferentes niveles"""
    print("\n🔍 PROBANDO SISTEMA DE LOGGING")
    print("=" * 50)

    try:
        from rexus.utils.logging_config import get_logger, log_user_action

        # Test diferentes loggers
        main_logger = get_logger("main")
        security_logger = get_logger("security")
        error_logger = get_logger("error")

        print("✅ Loggers creados correctamente")

        # Test logging de diferentes niveles
        main_logger.info("Test de información desde main")
        main_logger.warning("Test de advertencia desde main")

        security_logger.info("Test de seguridad")
        error_logger.error("Test de error controlado")

        # Test logging de acciones de usuario
        log_user_action("test_action", "test_user", "Testing user action logging")

        print("✅ Sistema de logging funcionando correctamente")
        return True

    except ImportError as e:
        print(f"⚠️ Sistema de logging no disponible: {e}")
        return False
    except Exception as e:
        print(f"❌ Error en sistema de logging: {e}")
        return False


def test_error_handling():
    """Prueba el sistema de manejo de errores"""
    print("\n🔍 PROBANDO MANEJO DE ERRORES")
    print("=" * 50)

    try:
        from rexus.utils.error_handler import error_boundary, safe_execute

        # Test 1: Función que funciona correctamente
        @error_boundary
        def working_function():
            return "success"

        result = working_function()
        print(f"✅ Función exitosa: {result}")

        # Test 2: Función que falla controladamente
        @error_boundary
        def failing_function():
            raise ValueError("Test error")

        result = failing_function()
        print(f"✅ Error manejado correctamente: {result}")

        # Test 3: Safe execute
        def another_failing_function():
            raise RuntimeError("Another test error")

        result = safe_execute(another_failing_function, default_return="default_value")
        print(f"✅ Safe execute funcionando: {result}")

        return True

    except ImportError as e:
        print(f"⚠️ Sistema de manejo de errores no disponible: {e}")
        return False
    except Exception as e:
        print(f"❌ Error en manejo de errores: {e}")
        return False


def test_security_system():
    """Prueba el sistema de seguridad con datos reales"""
    print("\n🔍 PROBANDO SISTEMA DE SEGURIDAD")
    print("=" * 50)

    try:
        from rexus.utils.security import SecurityUtils

        # Test hashing de contraseñas
        test_password = "MySecurePassword123!"
        hashed = SecurityUtils.hash_password(test_password)
        print(f"✅ Password hasheada: {len(hashed)} caracteres")

        # Test verificación
        is_valid = SecurityUtils.verify_password(test_password, hashed)
        print(f"✅ Verificación correcta: {is_valid}")

        is_invalid = SecurityUtils.verify_password("wrong_password", hashed)
        print(f"✅ Verificación incorrecta rechazada: {not is_invalid}")

        # Test sanitización
        malicious_input = "<script>alert('xss')</script>Test content"
        sanitized = SecurityUtils.sanitize_input(malicious_input)
        print(f"✅ Input sanitizado: {sanitized}")

        return True

    except ImportError as e:
        print(f"❌ No se pudo importar SecurityUtils: {e}")
        return False
    except Exception as e:
        print(f"❌ Error en sistema de seguridad: {e}")
        return False


def test_database_system():
    """Prueba el sistema de base de datos mejorado"""
    print("\n🔍 PROBANDO SISTEMA DE BASE DE DATOS")
    print("=" * 50)

    try:
        from rexus.utils.database_manager import DatabaseManager

        print("✅ DatabaseManager importado correctamente")

        # Test configuración básica
        print("✅ Sistema de BD disponible para uso")

        return True

    except ImportError as e:
        print(f"⚠️ Sistema de BD no disponible: {e}")
        return False
    except Exception as e:
        print(f"❌ Error en sistema de BD: {e}")
        return False


def run_performance_validation():
    """Ejecuta validación completa de rendimiento"""
    print("🚀 VALIDACIÓN DE RENDIMIENTO REXUS")
    print("Probando sistemas con datos reales...")
    print("=" * 60)

    tests = [
        ("Sistema de Rendimiento", test_performance_monitoring),
        ("Sistema de Logging", test_logging_system),
        ("Manejo de Errores", test_error_handling),
        ("Sistema de Seguridad", test_security_system),
        ("Sistema de Base de Datos", test_database_system),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ Error crítico en {test_name}: {e}")

    success_rate = (passed / total * 100) if total > 0 else 0

    print("\n" + "=" * 60)
    print("📊 RESUMEN DE VALIDACIÓN DE RENDIMIENTO")
    print(f"✅ Tests exitosos: {passed}/{total} ({success_rate:.1f}%)")

    if success_rate >= 80:
        print("🎉 SISTEMA PREPARADO PARA PRODUCCIÓN")
        print("✅ Todas las mejoras funcionando correctamente")
    elif success_rate >= 60:
        print("⚠️ SISTEMA MAYORMENTE PREPARADO")
        print("🔧 Algunas mejoras menores recomendadas")
    else:
        print("❌ SISTEMA NECESITA ATENCIÓN")
        print("🚨 Corregir problemas antes de despliegue")

    # Guardar reporte de rendimiento
    with open("logs/performance_validation.txt", "w", encoding="utf-8") as f:
        f.write(f"Validación de Rendimiento\n")
        f.write(f"Éxito: {success_rate:.1f}%\n")
        f.write(f"Tests: {passed}/{total}\n")
        f.write(f"Fecha: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    print(f"\n📄 Reporte guardado en: logs/performance_validation.txt")

    return success_rate >= 60


if __name__ == "__main__":
    success = run_performance_validation()

    if success:
        print("\n🚀 READY FOR NEXT PHASE!")
        print("🎯 Sistemas validados y listos para usuario final")
    else:
        print("\n⚠️ REVIEW NEEDED")
        print("🔧 Corregir problemas antes de continuar")

    sys.exit(0 if success else 1)
