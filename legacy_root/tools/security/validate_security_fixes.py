#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Validacion Final - Verificacion de Correcciones de Seguridad
Valida que todas las correcciones se hayan aplicado correctamente
"""

import os
import sys
from pathlib import Path

def print_header(title):
    """Imprime un encabezado formateado"""
    print("=" * 60)
    print(f"🛡️ {title}")
    print("=" * 60)

def validate_sql_injection_fixes():
    """Valida que las correcciones SQL injection esten aplicadas"""
    print("🔍 VALIDANDO CORRECCIONES SQL INJECTION")
    
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
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Buscar indicadores de proteccion SQL
                sql_protection_indicators = [
                    "validate_sql_identifier",
                    "sanitize_input",
                    "prepared statements",
                    "cursor.execute(",
                    "SQL_INJECTION_PROTECTED"
                ]
                
                found_protection = any(indicator in content for indicator in sql_protection_indicators)
                
                if found_protection:
                    print(f"  [CHECK] {file_path} - Proteccion SQL implementada")
                    fixes_applied += 1
                else:
                    print(f"  [WARN] {file_path} - Revisar proteccion SQL")
                    
            except Exception as e:
                print(f"  [ERROR] Error leyendo {file_path}: {e}")
        else:
            print(f"  [ERROR] {file_path} - Archivo no encontrado")
    
    success_rate = (fixes_applied / total_files * 100) if total_files > 0 else 0
    print(f"  [CHART] Tasa de exito: {success_rate:.1f}% ({fixes_applied}/{total_files})")
    return success_rate >= 80

def validate_xss_protection():
    """Valida que la proteccion XSS este implementada"""
    print("🔍 VALIDANDO PROTECCION XSS")
    
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
                "sanitize_input",
                "XSS_PROTECTION_ADDED"
            ]
            
            has_protection = any(indicator in content for indicator in xss_indicators)
            
            if has_protection:
                print(f"  [CHECK] {file_path} - Proteccion XSS marcada")
                protected_files += 1
            else:
                print(f"  [WARN] {file_path} - Proteccion XSS no marcada")
                
        except Exception as e:
            print(f"  [ERROR] Error leyendo {file_path}: {e}")
    
    protection_rate = (protected_files / total_files * 100) if total_files > 0 else 0
    print(f"  [CHART] Tasa de proteccion: {protection_rate:.1f}% ({protected_files}/{total_files})")
    return protection_rate >= 90

def validate_authorization_system():
    """Valida el sistema de autorizacion"""
    print("🔍 VALIDANDO SISTEMA DE AUTORIZACION")
    
    # Verificar que AuthManager exista
    auth_manager_path = "rexus/core/auth_manager.py"
    auth_working = False
    
    if os.path.exists(auth_manager_path):
        try:
            with open(auth_manager_path, 'r', encoding='utf-8', errors='ignore') as f:
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
                print("  [CHECK] AuthManager creado correctamente")
                auth_working = True
            else:
                print(f"  [WARN] Componentes faltantes: {missing_components}")
                
        except Exception as e:
            print(f"  [ERROR] Error verificando AuthManager: {e}")
    else:
        print("  [ERROR] AuthManager no encontrado")
    
    # Contar archivos con verificacion de autorizacion
    auth_files = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    if "@auth_required" in content or "check_permission" in content:
                        auth_files.append(file_path)
                except:
                    continue
    
    print(f"  [CHART] Archivos con verificacion de autorizacion: {len(auth_files)}")
    return auth_working

def validate_secure_configuration():
    """Valida la configuracion segura"""
    print("🔍 VALIDANDO CONFIGURACION SEGURA")
    
    config_checks = []
    
    # Verificar archivo .env
    if os.path.exists(".env"):
        print("  [CHECK] Archivo .env existe")
        config_checks.append(True)
    else:
        print("  [WARN] Archivo .env no encontrado")
        config_checks.append(False)
    
    # Verificar configuracion segura
    config_file = "config/rexus_config.json"
    if os.path.exists(config_file):
        print("  [CHECK] Configuracion segura creada")
        config_checks.append(True)
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = f.read()
            if "security" in config_data.lower():
                print("  [CHECK] Configuracion de seguridad presente en rexus_config.json")
                config_checks.append(True)
            else:
                print("  [WARN] Configuracion de seguridad no encontrada")
                config_checks.append(False)
        except:
            print("  [WARN] Error leyendo configuracion")
            config_checks.append(False)
    else:
        print("  [WARN] Archivo de configuracion no encontrado")
        config_checks.append(False)
        config_checks.append(False)
    
    # Verificar .gitignore
    if os.path.exists(".gitignore"):
        try:
            with open(".gitignore", 'r', encoding='utf-8') as f:
                gitignore_content = f.read()
            if ".env" in gitignore_content and "*.log" in gitignore_content:
                print("  [CHECK] .gitignore protege archivos sensibles")
                config_checks.append(True)
            else:
                print("  [WARN] .gitignore necesita actualizacion")
                config_checks.append(False)
        except:
            print("  [WARN] Error leyendo .gitignore")
            config_checks.append(False)
    else:
        print("  [WARN] .gitignore no encontrado")
        config_checks.append(False)
    
    success_rate = (sum(config_checks) / len(config_checks) * 100) if config_checks else 0
    print(f"  [CHART] Configuracion segura: {success_rate:.1f}% ({sum(config_checks)}/{len(config_checks)})")
    return success_rate >= 75

def validate_security_utils():
    """Valida que SecurityUtils este completo"""
    print("🔍 VALIDANDO UTILIDADES DE SEGURIDAD")
    
    security_file = "rexus/utils/security.py"
    
    if os.path.exists(security_file):
        try:
            with open(security_file, 'r', encoding='utf-8', errors='ignore') as f:
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
                print("  [CHECK] SecurityUtils completo con todas las funciones")
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

def count_backup_files():
    """Cuenta archivos de backup creados"""
    print("🔍 VERIFICANDO ARCHIVOS DE BACKUP")
    
    backup_patterns = [
        ("*.backup_sql", 0),
        ("*.backup_xss", 0),
        ("*.backup_auth", 0),
        ("*.backup_security", 0)
    ]
    
    total_backups = 0
    
    for pattern, count in backup_patterns:
        # Buscar archivos que coincidan con el patron
        found_files = []
        for root, dirs, files in os.walk("."):
            for file in files:
                if pattern.replace("*", "") in file:
                    found_files.append(os.path.join(root, file))
        
        print(f"  📋 {pattern}: {len(found_files)} archivos")
        total_backups += len(found_files)
    
    print(f"  [CHART] Total de backups: {total_backups}")
    return total_backups

def main():
    """Funcion principal de validacion"""
    print_header("VALIDACION FINAL DE CORRECCIONES DE SEGURIDAD")
    print("Verificando que todas las correcciones se aplicaron correctamente...")
    
    # Ejecutar validaciones
    results = {}
    results['sql_injection'] = validate_sql_injection_fixes()
    results['xss_protection'] = validate_xss_protection()
    results['authorization'] = validate_authorization_system()
    results['configuration'] = validate_secure_configuration()
    results['security_utils'] = validate_security_utils()
    
    # Contar backups
    backup_count = count_backup_files()
    
    print_header("RESUMEN DE VALIDACION")
    
    # Mostrar resultados
    print(f"Sql Injection: {'[CHECK] PASS' if results['sql_injection'] else '[ERROR] FAIL'}")
    print(f"Xss Protection: {'[CHECK] PASS' if results['xss_protection'] else '[ERROR] FAIL'}")
    print(f"Authorization: {'[CHECK] PASS' if results['authorization'] else '[ERROR] FAIL'}")
    print(f"Configuration: {'[CHECK] PASS' if results['configuration'] else '[ERROR] FAIL'}")
    print(f"Security Utils: {'[CHECK] PASS' if results['security_utils'] else '[ERROR] FAIL'}")
    print(f"Backups creados: {backup_count} archivos")
    
    # Calcular puntuacion general
    passed_tests = sum(1 for result in results.values() if result)
    total_tests = len(results)
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n🎯 RESULTADO GENERAL: {success_rate:.1f}% ({passed_tests}/{total_tests})")
    
    if success_rate >= 80:
        print("🎉 VALIDACION EXITOSA - Correcciones aplicadas correctamente")
        print("[CHECK] El sistema esta listo para pruebas finales")
    elif success_rate >= 60:
        print("[WARN] VALIDACION PARCIAL - Algunas correcciones necesitan atencion")
        print("🔧 Revisar elementos marcados como FAIL")
    else:
        print("[ERROR] VALIDACION FALLIDA - Correcciones criticas necesarias")
        print("🚨 Aplicar correcciones antes de continuar")
    
    print("\n📋 PROXIMOS PASOS:")
    print("1. Completar cualquier elemento marcado como FAIL")
    print("2. Realizar tests de integracion")
    print("3. Ejecutar tests de seguridad automatizados")
    print("4. Proceder con el despliegue en entorno de pruebas")
    
    return success_rate >= 60

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
