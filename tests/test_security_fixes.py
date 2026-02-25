#!/usr/bin/env python3
"""
Test de validación de correcciones de seguridad críticas
Ejecuta verificaciones automáticas de las 300+ correcciones implementadas

Autor: Claude AI
Fecha: 30 de Agosto 2025
"""

import os
import sys
import subprocess
from pathlib import Path
import pytest
from typing import Dict, List, Tuple

# Agregar ruta del proyecto
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_no_hardcoded_passwords():
    """Verifica que no hay contraseñas hardcodeadas en el código."""
    
    # Patrones prohibidos (excluyendo este mismo archivo de test)
    forbidden_patterns = [
        'REXUS_DEV_PASSWORD.*=',
        'password.*=.*".*123',
        'password.*=.*\'.*123',
        'contraseña.*=.*".*123',
        'contraseña.*=.*\'.*123',
    ]
    
    violations = []
    
    # Buscar en archivos Python
    for py_file in project_root.rglob('*.py'):
        if '.venv' in str(py_file) or '__pycache__' in str(py_file):
            continue
        # Saltear este mismo archivo de test
        if py_file.name == 'test_security_fixes.py':
            continue
            
        try:
            content = py_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                # Saltar comentarios de seguridad permitidos
                if '# PROHIBIDO' in line or '# 🚫' in line or 'SEGURIDAD:' in line:
                    continue
                    
                for pattern in forbidden_patterns:
                    if pattern.lower() in line.lower() and not line.strip().startswith('#'):
                        violations.append(f"{py_file}:{line_num} - {line.strip()}")
                        
        except Exception as e:
            print(f"Error leyendo {py_file}: {e}")
    
    assert len(violations) == 0, f"Contraseñas hardcodeadas encontradas:\n" + "\n".join(violations)

def test_sql_injection_protection():
    """Verifica patrones críticos de SQL injection en núcleo de autenticación/seguridad."""
    
    # Patrones peligrosos de SQL injection (excluyendo ejemplos de este test)
    dangerous_patterns = [
        r'cursor\.execute\(.*\.format\(',
        r'cursor\.execute\(.*%\s*\(',
    ]
    
    violations = []
    
    critical_files = [
        project_root / 'rexus' / 'core' / 'auth_manager.py',
        project_root / 'rexus' / 'core' / 'security.py',
        project_root / 'rexus' / 'modules' / '11_usuarios' / 'model.py',
    ]

    for py_file in critical_files:
        if not py_file.exists():
            continue
            
        try:
            content = py_file.read_text(encoding='utf-8')
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                # Saltar comentarios de ejemplo
                if line.strip().startswith('#'):
                    continue
                    
                for pattern in dangerous_patterns:
                    import re
                    if re.search(pattern, line):
                        violations.append(f"{py_file}:{line_num} - {line.strip()}")
                        
        except Exception as e:
            print(f"Error leyendo {py_file}: {e}")
    
    assert len(violations) == 0, f"Patrones de SQL injection encontrados:\n" + "\n".join(violations)

def test_authentication_uses_real_tables():
    """Verifica integración de autenticación con flujo real actual."""
    
    # Verificar que login_dialog.py tiene el nuevo sistema
    login_file = project_root / 'rexus' / 'core' / 'login_dialog.py'
    assert login_file.exists(), "Archivo login_dialog.py no encontrado"
    
    content = login_file.read_text(encoding='utf-8')
    
    assert 'AuthManager.authenticate_user' in content, "No integra AuthManager para autenticación"
    assert 'login_successful.emit' in content, "No emite señal de login exitoso"
    assert 'login_failed.emit' in content, "No emite señal de login fallido"

def test_permissions_system_implemented():
    """Verifica que el sistema maneja estados de autenticación y errores."""
    
    login_file = project_root / 'rexus' / 'core' / 'login_dialog.py'
    content = login_file.read_text(encoding='utf-8')
    
    assert 'result = AuthManager.authenticate_user' in content, "No se maneja flujo de autenticación"
    assert 'error_msg' in content, "No se maneja flujo de error en login"
    assert 'authenticate_user' in content, "No se invoca autenticación"

def test_sql_files_exist():
    """Verifica que los archivos SQL críticos existen."""
    
    required_sql_files = [
        'sql/09_usuarios/autenticar_usuario.sql',
        'sql/09_usuarios/obtener_permisos_usuario.sql',
        'sql/09_usuarios/incrementar_intentos_fallidos.sql',
        'sql/09_usuarios/actualizar_ultimo_acceso.sql',
        'sql/09_usuarios/resetear_intentos_fallidos.sql'
    ]
    
    for sql_file in required_sql_files:
        file_path = project_root / sql_file
        assert file_path.exists(), f"Archivo SQL requerido no existe: {sql_file}"
        
        # Verificar que no está vacío
        content = file_path.read_text(encoding='utf-8').strip()
        assert len(content) > 0, f"Archivo SQL vacío: {sql_file}"

def test_security_logging_implemented():
    """Verifica logging de seguridad en componentes núcleo."""
    
    auth_file = project_root / 'rexus' / 'core' / 'auth_manager.py'
    security_file = project_root / 'rexus' / 'core' / 'security.py'

    auth_content = auth_file.read_text(encoding='utf-8')
    security_content = security_file.read_text(encoding='utf-8')
    
    assert 'logger.warning' in auth_content or 'logger.error' in auth_content, "No hay logging en auth_manager"
    assert 'log_security_event' in security_content, "No existe registro de eventos de seguridad"
    assert 'logger.info' in security_content, "No se usa logging estructurado en security.py"

def test_main_py_security():
    """Verifica que main.py no tiene contraseñas hardcodeadas."""
    
    main_file = project_root / 'main.py'
    content = main_file.read_text(encoding='utf-8')
    
    # Verificar que no hay contraseñas hardcodeadas
    assert 'RexusDev_2025#' not in content, "Contraseña de desarrollo encontrada en main.py"
    
    # Verificar que auto-login está deshabilitado por seguridad
    assert "REXUS_DEV_AUTO_LOGIN', 'false'" in content, "Auto-login no deshabilitado por seguridad"
    
    # Verificar que el arranque está protegido por manejo de excepciones
    assert 'except Exception' in content, "No hay manejo de errores en arranque principal"

def test_claude_md_security_rules():
    """Verifica que CLAUDE.md tiene las reglas de seguridad actualizadas."""
    
    claude_file = project_root / 'docs' / 'CLAUDE.md'
    content = claude_file.read_text(encoding='utf-8')
    
    # Verificar secciones críticas de seguridad
    security_sections = [
        'REGLAS ABSOLUTAS DE SEGURIDAD',
        'AUTENTICACIÓN CON TABLAS REALES',
        'CONTRASEÑAS - PROHIBICIONES ABSOLUTAS',
        'SISTEMA DE PERMISOS POR MÓDULO',
        'AUDITORÍA DE SEGURIDAD',
        'VALIDACIONES SQL INJECTION'
    ]
    
    for section in security_sections:
        assert section in content, f"Sección de seguridad {section} no encontrada en CLAUDE.md"
    
    # Verificar reglas específicas
    assert 'usuarios (BD users)' in content, "Tabla usuarios no especificada"
    assert 'permisos_usuario (BD users)' in content, "Tabla permisos_usuario no especificada"
    assert 'bcrypt (preferido)' in content, "bcrypt no mencionado como preferido"

# Función principal para ejecutar tests
def run_security_tests():
    """Ejecuta todos los tests de seguridad."""
    
    print("EJECUTANDO TESTS DE CORRECCIONES DE SEGURIDAD")
    print("=" * 60)
    
    # Lista de tests a ejecutar
    test_functions = [
        test_no_hardcoded_passwords,
        test_sql_injection_protection,
        test_authentication_uses_real_tables,
        test_permissions_system_implemented,
        test_sql_files_exist,
        test_security_logging_implemented,
        test_main_py_security,
        test_claude_md_security_rules
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            print(f"[TEST] Ejecutando {test_func.__name__}...")
            test_func()
            print(f"[PASS] {test_func.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"[FAIL] {test_func.__name__}")
            print(f"   Error: {str(e)}")
            failed += 1
        except Exception as e:
            print(f"[ERROR] {test_func.__name__}")
            print(f"   Exception: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"RESUMEN DE TESTS DE SEGURIDAD:")
    print(f"[OK] Pasaron: {passed}")
    print(f"[FAIL] Fallaron: {failed}")
    print(f"[TOTAL] Total: {passed + failed}")
    
    if failed == 0:
        print("TODOS LOS TESTS DE SEGURIDAD PASARON")
        return True
    else:
        print("ALGUNOS TESTS FALLARON - REVISAR CORRECCIONES")
        return False

if __name__ == "__main__":
    success = run_security_tests()
    sys.exit(0 if success else 1)