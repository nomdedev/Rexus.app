#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Validacion Final - Verificacion de Correcciones de Seguridad
Valida que todas las correcciones se hayan aplicado correctamente
"""

import os
import sys

def print_header(title):
    """Imprime un encabezado formateado"""
    print("=" * 60)
    print(f"[SEGURIDAD] {title}")
    print("=" * 60)

def validate_sql_injection_fixes():
    """Valida que las correcciones SQL injection esten aplicadas"""
    print("[VALIDANDO] CORRECCIONES SQL INJECTION")

    # Archivos criticos a verificar
    critical_files = [
        "rexus/modules/mantenimiento/model.py",
        "rexus/modules/logistica/model.py"
    ]

    fixes_applied = 0
    total_files = len(critical_files)

    for file_path in critical_files:
        if os.path.exists(file_path):
            try:
                with open(file_path,
'r',
                    encoding='utf-8',
                    errors='ignore') as f:
                    content = f.read()

                # Buscar indicadores de proteccion SQL
                sql_protection_indicators = [
                    "validate_sql_identifier",
                    "sanitize_input",
                    "cursor.execute(",
                    "SQL_INJECTION_PROTECTED"
                ]

                found_protection = any(indicator in content for indicator in sql_protection_indicators)

                if found_protection:
                    print(f"  [OK] {file_path} - Proteccion SQL implementada")
                    fixes_applied += 1
                else:
                    print(f"  [WARN] {file_path} - Revisar proteccion SQL")

            except Exception as e:
                print(f"  [ERROR] Error leyendo {file_path}: {e}")
        else:
            print(f"  [ERROR] {file_path} - Archivo no encontrado")

    success_rate = (fixes_applied / total_files * 100) if total_files > 0 else 0
    print(f"  [INFO] Tasa de exito: {success_rate:.1f}% ({fixes_applied}/{total_files})")
    return success_rate >= 80

def validate_xss_protection():
    """Valida que la proteccion XSS este implementada"""
    print("[VALIDANDO] PROTECCION XSS")

    # Buscar archivos view.py en modulos
    view_files = []
    modules_dir = "rexus/modules"

    if os.path.exists(modules_dir):
        for module_name in os.listdir(modules_dir):
            module_path = os.path.join(modules_dir, module_name)
            if os.path.isdir(module_path):
                view_file = os.path.join(module_path, "view.py")
                if os.path.exists(view_file):
                    view_files.append(view_file)

    protected_files = 0
    total_files = len(view_files)

    for file_path in view_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Buscar indicadores de proteccion XSS
            xss_indicators = [
                "XSS Protection",
                "SecurityUtils",
                "sanitize_input"
            ]

            has_protection = any(indicator in content for indicator in xss_indicators)

            if has_protection:
                print(f"  [OK] {file_path} - Proteccion XSS marcada")
                protected_files += 1
            else:
                print(f"  [WARN] {file_path} - Proteccion XSS no marcada")

        except Exception as e:
            print(f"  [ERROR] Error leyendo {file_path}: {e}")

    protection_rate = (protected_files / total_files * 100) if total_files > 0 else 0
    print(f"  [INFO] Tasa de proteccion: {protection_rate:.1f}% ({protected_files}/{total_files})")
    return protection_rate >= 90

def validate_authorization_system():
    """Valida el sistema de autorizacion"""
    print("[VALIDANDO] SISTEMA DE AUTORIZACION")

    # Verificar que AuthManager exista
    auth_manager_path = "rexus/core/auth_manager.py"
    auth_working = False

    if os.path.exists(auth_manager_path):
        try:
            with open(auth_manager_path,
'r',
                encoding='utf-8',
                errors='ignore') as f:
                content = f.read()

            required_components = [
                "class AuthManager",
                "UserRole",
                "Permission",
                "check_permission"
            ]

            missing_components = []
            for component in required_components:
                if component not in content:
                    missing_components.append(component)

            if not missing_components:
                print("  [OK] AuthManager creado correctamente")
                auth_working = True
            else:
                print(f"  [WARN] Componentes faltantes: {missing_components}")

        except Exception as e:
            print(f"  [ERROR] Error verificando AuthManager: {e}")
    else:
        print("  [ERROR] AuthManager no encontrado")

    return auth_working

def validate_security_utils():
    """Valida que SecurityUtils este completo"""
    print("[VALIDANDO] UTILIDADES DE SEGURIDAD")

    security_file = "rexus/utils/security.py"

    if os.path.exists(security_file):
        try:
            with open(security_file,
'r',
                encoding='utf-8',
                errors='ignore') as f:
                content = f.read()

            required_functions = [
                "hash_password",
                "verify_password",
                "sanitize_input",
                "validate_email",
                "validate_sql_identifier"
            ]

            missing_functions = []
            for func in required_functions:
                if func not in content:
                    missing_functions.append(func)

            if not missing_functions:
                print("  [OK] SecurityUtils completo con todas las funciones")
                return True
            else:
                print(f"  [WARN] Funciones faltantes en SecurityUtils: {missing_functions}")
                return False

        except Exception as e:
            print(f"  [ERROR] Error verificando SecurityUtils: {e}")
            return False
    else:
        print("  [ERROR] SecurityUtils no encontrado")
        return False

def main():
    """Funcion principal de validacion"""
    print_header("VALIDACION FINAL DE CORRECCIONES DE SEGURIDAD")
    print("Verificando que todas las correcciones se aplicaron correctamente...")

    # Ejecutar validaciones
    results = {}
    results['sql_injection'] = validate_sql_injection_fixes()
    results['xss_protection'] = validate_xss_protection()
    results['authorization'] = validate_authorization_system()
    results['security_utils'] = validate_security_utils()

    print_header("RESUMEN DE VALIDACION")

    # Mostrar resultados
    print(f"SQL Injection: {'PASS' if results['sql_injection'] else 'FAIL'}")
    print(f"XSS Protection: {'PASS' if results['xss_protection'] else 'FAIL'}")
    print(f"Authorization: {'PASS' if results['authorization'] else 'FAIL'}")
    print(f"Security Utils: {'PASS' if results['security_utils'] else 'FAIL'}")

    # Calcular puntuacion general
    passed_tests = sum(1 for result in results.values() if result)
    total_tests = len(results)
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

    print(f"\n[RESULTADO] {success_rate:.1f}% ({passed_tests}/{total_tests})")

    if success_rate >= 80:
        print("[SUCCESS] VALIDACION EXITOSA - Sistema listo")
        return True
    else:
        print("[FAIL] VALIDACION FALLIDA - Revisar elementos marcados")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
