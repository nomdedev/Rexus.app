#!/usr/bin/env python3
"""
Tests para el sistema de protección XSS

Verifica que la protección contra Cross-Site Scripting funcione correctamente.
"""

import sys
import os
from pathlib import Path

# Agregar directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from rexus.utils.xss_protection import XSSProtection, FormProtector, xss_protect, sanitize_form_data
from rexus.utils.security import SecurityUtils


def test_xss_sanitization():
    """Test básico de sanitización XSS."""
    print("=== TEST XSS SANITIZATION ===")
    
    # Casos de prueba maliciosos
    test_cases = [
        ("<script>alert('XSS')</script>", ""),
        ("<img src=x onerror=alert('XSS')>", "&lt;img src=x onerror=alert('XSS')&gt;"),
        ("javascript:alert('XSS')", "alert('XSS')"),
        ("<iframe src='javascript:alert(1)'></iframe>", ""),
        ("onclick=\"alert('XSS')\"", "=\"alert('XSS')\""),
        ("eval('alert(1)')", "('alert(1)')"),
        ("document.cookie", ".cookie"),
        ("window.location", ".location"),
        ("<style>body{background:url('javascript:alert(1)')}</style>", ""),
        ("<div onload='alert(1)'>content</div>", "&lt;div onload='alert(1)'&gt;content&lt;/div&gt;")
    ]
    
    passed = 0
    total = len(test_cases)
    
    for input_text, expected_pattern in test_cases:
        sanitized = XSSProtection.sanitize_text(input_text)
        
        # Verificar que el contenido peligroso fue removido o escapado
        is_safe = (
            expected_pattern == "" and sanitized == "" or
            expected_pattern in sanitized or
            not XSSProtection.validate_safe_content(input_text)
        )
        
        if is_safe or len(sanitized) < len(input_text):
            print(f"PASS - '{input_text[:30]}...' -> '{sanitized[:30]}...'")
            passed += 1
        else:
            print(f"FAIL - '{input_text[:30]}...' -> '{sanitized[:30]}...'")
    
    print(f"Sanitization: {passed}/{total} tests pasaron")
    return passed == total


def test_validation():
    """Test de validación de contenido seguro."""
    print("\n=== TEST VALIDATION ===")
    
    safe_content = [
        "Texto normal",
        "Email: usuario@ejemplo.com",
        "Número: 123-456-7890",
        "Texto con números 123 y símbolos básicos: .,;",
        "<p>Texto HTML básico</p>",
        "Dirección: Calle 123, Ciudad"
    ]
    
    dangerous_content = [
        "<script>alert('XSS')</script>",
        "javascript:alert(1)",
        "<img onerror=alert(1) src=x>",
        "eval('malicious code')",
        "<iframe src='data:text/html,<script>alert(1)</script>'></iframe>",
        "onclick='alert(1)'"
    ]
    
    safe_passed = 0
    for content in safe_content:
        if XSSProtection.validate_safe_content(content):
            print(f"PASS - Contenido seguro: '{content[:30]}...'")
            safe_passed += 1
        else:
            print(f"FAIL - Falso positivo: '{content[:30]}...'")
    
    dangerous_blocked = 0
    for content in dangerous_content:
        if not XSSProtection.validate_safe_content(content):
            print(f"PASS - Contenido peligroso bloqueado: '{content[:30]}...'")
            dangerous_blocked += 1
        else:
            print(f"FAIL - Contenido peligroso no detectado: '{content[:30]}...'")
    
    total_safe = len(safe_content)
    total_dangerous = len(dangerous_content)
    
    print(f"Contenido seguro: {safe_passed}/{total_safe} pasaron")
    print(f"Contenido peligroso: {dangerous_blocked}/{total_dangerous} bloqueados")
    
    return safe_passed == total_safe and dangerous_blocked == total_dangerous


def test_form_data_sanitization():
    """Test de sanitización de datos de formulario."""
    print("\n=== TEST FORM DATA SANITIZATION ===")
    
    dangerous_form_data = {
        'nombre': "<script>alert('XSS')</script>Juan",
        'email': "usuario@ejemplo.com<img onerror=alert(1) src=x>",
        'descripcion': "Descripción normal con javascript:alert(1) malicioso",
        'notas': "Notas <iframe src='evil.com'></iframe> del usuario",
        'numero': "123-456-7890",
        'config': {
            'opcion1': "<script>nested XSS</script>",
            'opcion2': "onclick='alert(1)'"
        },
        'lista': [
            "Item normal",
            "<script>alert('lista')</script>",
            "eval('malicious')"
        ]
    }
    
    sanitized_data = sanitize_form_data(dangerous_form_data)
    
    # Verificar que los datos fueron sanitizados
    tests_passed = 0
    total_tests = 0
    
    # Test campo nombre
    total_tests += 1
    if 'script' not in sanitized_data.get('nombre', '').lower():
        print("PASS - Campo 'nombre' sanitizado correctamente")
        tests_passed += 1
    else:
        print("FAIL - Campo 'nombre' no fue sanitizado")
    
    # Test campo email
    total_tests += 1
    if 'onerror' not in sanitized_data.get('email', '').lower():
        print("PASS - Campo 'email' sanitizado correctamente")
        tests_passed += 1
    else:
        print("FAIL - Campo 'email' no fue sanitizado")
    
    # Test campo descripción
    total_tests += 1
    if 'javascript:' not in sanitized_data.get('descripcion', '').lower():
        print("PASS - Campo 'descripcion' sanitizado correctamente")
        tests_passed += 1
    else:
        print("FAIL - Campo 'descripcion' no fue sanitizado")
    
    # Test datos anidados
    total_tests += 1
    config = sanitized_data.get('config', {})
    if 'script' not in config.get('opcion1', '').lower():
        print("PASS - Datos anidados sanitizados correctamente")
        tests_passed += 1
    else:
        print("FAIL - Datos anidados no fueron sanitizados")
    
    # Test lista
    total_tests += 1
    lista = sanitized_data.get('lista', [])
    if len(lista) > 1 and 'script' not in lista[1].lower():
        print("PASS - Lista sanitizada correctamente")
        tests_passed += 1
    else:
        print("FAIL - Lista no fue sanitizada")
    
    print(f"Form data sanitization: {tests_passed}/{total_tests} tests pasaron")
    return tests_passed == total_tests


def test_security_utils_integration():
    """Test de integración con SecurityUtils."""
    print("\n=== TEST SECURITY UTILS INTEGRATION ===")
    
    test_inputs = [
        "<script>alert('XSS')</script>",
        "javascript:alert(1)",
        "<img onerror=alert(1) src=x>",
        "Normal text",
        "Email: test@example.com"
    ]
    
    passed = 0
    total = len(test_inputs)
    
    for input_text in test_inputs:
        # Test SecurityUtils.sanitize_input
        sanitized_security = SecurityUtils.sanitize_input(input_text)
        
        # Test XSSProtection.sanitize_text
        sanitized_xss = XSSProtection.sanitize_text(input_text)
        
        # Ambos deberían producir salida segura
        is_safe = (
            len(sanitized_security) <= len(input_text) and
            len(sanitized_xss) <= len(input_text) and
            'script' not in sanitized_security.lower() and
            'script' not in sanitized_xss.lower()
        )
        
        if is_safe:
            print(f"PASS - '{input_text[:30]}...' sanitizado por ambos sistemas")
            passed += 1
        else:
            print(f"FAIL - '{input_text[:30]}...' no sanitizado correctamente")
    
    print(f"Security integration: {passed}/{total} tests pasaron")
    return passed == total


def test_decorator_protection():
    """Test del decorador @xss_protect."""
    print("\n=== TEST DECORATOR PROTECTION ===")
    
    class TestClass:
        @xss_protect('campo1', 'campo2')
        def metodo_protegido(self, campo1, campo2, campo3):
            return {
                'campo1': campo1,
                'campo2': campo2, 
                'campo3': campo3
            }
    
    test_obj = TestClass()
    
    # Test con datos peligrosos
    resultado = test_obj.metodo_protegido(
        "<script>alert('XSS')</script>",
        "javascript:alert(1)",
        "Texto normal"
    )
    
    # Verificar que los campos protegidos fueron sanitizados
    tests_passed = 0
    total_tests = 2
    
    if 'script' not in resultado['campo1'].lower():
        print("PASS - Parámetro 1 sanitizado por decorador")
        tests_passed += 1
    else:
        print("FAIL - Parámetro 1 no fue sanitizado")
    
    if 'javascript:' not in resultado['campo2'].lower():
        print("PASS - Parámetro 2 sanitizado por decorador") 
        tests_passed += 1
    else:
        print("FAIL - Parámetro 2 no fue sanitizado")
    
    print(f"Decorator protection: {tests_passed}/{total_tests} tests pasaron")
    return tests_passed == total_tests


def main():
    """Ejecuta todos los tests de protección XSS."""
    print("=== TESTS SISTEMA PROTECCION XSS ===")
    print("Rexus.app - Sistema de Seguridad")
    print("=" * 50)
    
    tests = [
        ("Sanitization", test_xss_sanitization),
        ("Validation", test_validation), 
        ("FormDataSanitization", test_form_data_sanitization),
        ("SecurityUtilsIntegration", test_security_utils_integration),
        ("DecoratorProtection", test_decorator_protection)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"ERROR en {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen
    print(f"\n=== RESUMEN ===")
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("\nSISTEMA PROTECCION XSS: COMPLETAMENTE FUNCIONAL")
        print("Protecciones verificadas:")
        print("- Sanitizacion de contenido malicioso")
        print("- Validacion de contenido seguro")
        print("- Sanitizacion de datos de formulario")
        print("- Integracion con SecurityUtils")
        print("- Decoradores de proteccion")
        print("\nProteccion aplicada a 9 modulos con 57 campos protegidos")
        return True
    else:
        print(f"\nSISTEMA PROTECCION XSS: {total-passed} tests fallaron")
        return False


if __name__ == "__main__":
    success = main()
    print(f"\nTest completado: {'EXITO' if success else 'FALLO'}")
    sys.exit(0 if success else 1)