#!/usr/bin/env python3
"""
MIT License - Copyright (c) 2025 Rexus.app

Test Rate Limiter - Rexus.app
=============================

Script para probar el funcionamiento del sistema de rate limiting
en el login para verificar protección contra ataques de fuerza bruta.
"""

import sys
import time
from pathlib import Path

# Agregar ruta del proyecto
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))

try:
    from rexus.core.rate_limiter import LoginRateLimiter, RateLimitConfig, get_rate_limiter
    RATE_LIMITER_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] Rate limiter no disponible: {e}")
    RATE_LIMITER_AVAILABLE = False


def test_rate_limiter_basic():
    """Test básico de funcionalidad del rate limiter"""
    print("\n" + "="*60)
    print("[TEST] Prueba básica de rate limiter")
    print("="*60)
    
    # Configuración de prueba (más permisiva)
    config = RateLimitConfig(
        max_attempts=3,
        base_lockout_minutes=1,
        max_lockout_minutes=5,
        progressive_multiplier=2
    )
    
    limiter = LoginRateLimiter(config)
    test_user = "test_user_basic"
    
    print(f"\n[INFO] Configuración de prueba:")
    print(f"  Max intentos: {config.max_attempts}")
    print(f"  Bloqueo base: {config.base_lockout_minutes} minutos")
    print(f"  Usuario de prueba: {test_user}")
    
    # Estado inicial
    info = limiter.get_lockout_info(test_user)
    print(f"\n[INITIAL] Estado inicial:")
    print(f"  Bloqueado: {info['is_blocked']}")
    print(f"  Fallos consecutivos: {info['consecutive_failures']}")
    print(f"  Intentos restantes: {info['remaining_attempts']}")
    
    # Simular intentos fallidos
    print(f"\n[SIMULATION] Simulando {config.max_attempts} intentos fallidos...")
    for i in range(config.max_attempts):
        limiter.record_failed_attempt(test_user)
        info = limiter.get_lockout_info(test_user)
        
        print(f"  Intento {i+1}: Fallos={info['consecutive_failures']}, "
              f"Restantes={info['remaining_attempts']}, "
              f"Bloqueado={info['is_blocked']}")
    
    # Verificar bloqueo
    info = limiter.get_lockout_info(test_user)
    print(f"\n[RESULT] Estado después de {config.max_attempts} intentos:")
    print(f"  Bloqueado: {info['is_blocked']}")
    print(f"  Bloqueado hasta: {info['locked_until']}")
    
    if info['is_blocked']:
        print("[PASS] Usuario correctamente bloqueado después de max intentos")
    else:
        print("[FAIL] Usuario debería estar bloqueado")
        return False
    
    # Simular login exitoso para resetear
    print(f"\n[RESET] Simulando login exitoso...")
    limiter.record_successful_attempt(test_user)
    info = limiter.get_lockout_info(test_user)
    
    print(f"  Estado después de login exitoso:")
    print(f"    Bloqueado: {info['is_blocked']}")
    print(f"    Fallos consecutivos: {info['consecutive_failures']}")
    
    if not info['is_blocked'] and info['consecutive_failures'] == 0:
        print("[PASS] Estado correctamente resetado después de login exitoso")
        return True
    else:
        print("[FAIL] Estado no se resetó correctamente")
        return False


def test_rate_limiter_progressive():
    """Test de escalación progresiva"""
    print("\n" + "="*60)
    print("[TEST] Prueba de escalación progresiva")
    print("="*60)
    
    config = RateLimitConfig(
        max_attempts=2,
        base_lockout_minutes=1,
        max_lockout_minutes=8,
        progressive_multiplier=2
    )
    
    limiter = LoginRateLimiter(config)
    test_user = "test_user_progressive"
    
    print(f"[INFO] Testing escalacion: {config.base_lockout_minutes} -> "
          f"{config.base_lockout_minutes * 2} -> "
          f"{config.base_lockout_minutes * 4} -> {config.max_lockout_minutes} (max)")
    
    # Primer ciclo de bloqueo
    print(f"\n[CYCLE 1] Primer bloqueo...")
    for i in range(config.max_attempts):
        limiter.record_failed_attempt(test_user)
    
    info = limiter.get_lockout_info(test_user)
    print(f"  Bloqueado: {info['is_blocked']}")
    print(f"  Tiempo de bloqueo esperado: {config.base_lockout_minutes} minutos")
    
    # Simular que el bloqueo expiró y hacer más intentos
    print(f"\n[CYCLE 2] Segundo bloqueo (escalación)...")
    
    # Forzar expiración del bloqueo para continuar la prueba
    if test_user in limiter.attempts:
        limiter.attempts[test_user]['locked_until'] = None
    
    # Más intentos fallidos
    for i in range(config.max_attempts):
        limiter.record_failed_attempt(test_user)
    
    failures_after_second_cycle = limiter.attempts[test_user]['consecutive_failures']
    print(f"  Fallos consecutivos después del segundo ciclo: {failures_after_second_cycle}")
    print(f"  Escalación esperada: > {config.max_attempts}")
    
    if failures_after_second_cycle > config.max_attempts:
        print("[PASS] Escalación progresiva funcionando")
        return True
    else:
        print("[FAIL] Escalación progresiva no funciona correctamente")
        return False


def test_rate_limiter_statistics():
    """Test de estadísticas"""
    print("\n" + "="*60)
    print("[TEST] Prueba de estadísticas")
    print("="*60)
    
    limiter = get_rate_limiter()  # Usar instancia global
    
    # Generar algo de actividad
    test_users = ["stats_user1", "stats_user2", "stats_user3"]
    for user in test_users:
        limiter.record_failed_attempt(user)
        limiter.record_failed_attempt(user)
    
    # Obtener estadísticas
    stats = limiter.get_statistics()
    
    print(f"[STATS] Estadísticas del rate limiter:")
    print(f"  Usuarios rastreados: {stats['total_tracked_users']}")
    print(f"  Usuarios bloqueados: {stats['currently_blocked']}")
    print(f"  Intentos recientes (1h): {stats['recent_attempts_1h']}")
    print(f"  Configuración:")
    print(f"    Max intentos: {stats['config']['max_attempts']}")
    print(f"    Bloqueo base: {stats['config']['base_lockout_minutes']} min")
    print(f"    Bloqueo máximo: {stats['config']['max_lockout_minutes']} min")
    
    if stats['total_tracked_users'] >= len(test_users):
        print("[PASS] Estadísticas generadas correctamente")
        return True
    else:
        print("[FAIL] Estadísticas incorrectas")
        return False


def test_rate_limiter_persistence():
    """Test de persistencia de datos"""
    print("\n" + "="*60)
    print("[TEST] Prueba de persistencia")
    print("="*60)
    
    test_user = "test_persistence"
    
    # Crear primer limiter y generar actividad
    config1 = RateLimitConfig(max_attempts=3)
    limiter1 = LoginRateLimiter(config1)
    
    print(f"[PHASE 1] Generando actividad en primera instancia...")
    limiter1.record_failed_attempt(test_user)
    limiter1.record_failed_attempt(test_user)
    
    info1 = limiter1.get_lockout_info(test_user)
    print(f"  Fallos en primera instancia: {info1['consecutive_failures']}")
    
    # Crear segunda instancia (debería cargar datos persistidos)
    print(f"[PHASE 2] Creando segunda instancia...")
    limiter2 = LoginRateLimiter(config1)
    
    info2 = limiter2.get_lockout_info(test_user)
    print(f"  Fallos en segunda instancia: {info2['consecutive_failures']}")
    
    if info1['consecutive_failures'] == info2['consecutive_failures']:
        print("[PASS] Persistencia de datos funcionando")
        return True
    else:
        print("[FAIL] Persistencia de datos no funciona")
        return False


def run_all_tests():
    """Ejecuta todas las pruebas del rate limiter"""
    print("[RATE LIMITER TESTS] Ejecutando pruebas del sistema de rate limiting")
    print("=" * 70)
    
    if not RATE_LIMITER_AVAILABLE:
        print("[ERROR] Rate limiter no disponible")
        return False
    
    tests = [
        ("Funcionalidad Básica", test_rate_limiter_basic),
        ("Escalación Progresiva", test_rate_limiter_progressive),  
        ("Estadísticas", test_rate_limiter_statistics),
        ("Persistencia", test_rate_limiter_persistence)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"[RUNNING] {test_name}")
        print(f"{'='*60}")
        
        try:
            if test_func():
                print(f"[PASS] {test_name}")
                passed += 1
            else:
                print(f"[FAIL] {test_name}")
        except Exception as e:
            print(f"[ERROR] {test_name}: {e}")
            import traceback
            traceback.print_exc()
    
    # Resumen final
    print(f"\n{'='*70}")
    print(f"[FINAL REPORT] RESUMEN DE PRUEBAS DE RATE LIMITER")
    print(f"{'='*70}")
    print(f"  Pruebas ejecutadas: {total}")
    print(f"  Pruebas exitosas: {passed}")
    print(f"  Pruebas fallidas: {total - passed}")
    print(f"  Porcentaje de éxito: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print(f"\n[SUCCESS] Todas las pruebas del rate limiter pasaron")
        print(f"          El sistema está listo para proteger contra ataques de fuerza bruta")
        return True
    else:
        print(f"\n[WARNING] Algunas pruebas fallaron")
        print(f"          Revisar implementación antes de despliegue")
        return False


def main():
    """Función principal"""
    try:
        success = run_all_tests()
        
        if success:
            print(f"\n[INFO] Rate limiter validado exitosamente")
            sys.exit(0)
        else:
            print(f"\n[WARNING] Rate limiter necesita revisión")
            sys.exit(1)
            
    except Exception as e:
        print(f"[ERROR] Error ejecutando pruebas: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()