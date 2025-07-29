#!/usr/bin/env python3
"""
Auditoría de seguridad - Buscar vulnerabilidades SQL injection
"""

import os
import sys
import re
from pathlib import Path

# Configurar path del proyecto
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def scan_sql_injection_vulnerabilities():
    """Buscar posibles vulnerabilidades de SQL injection"""
    print("AUDITORIA DE SEGURIDAD - SQL INJECTION")
    print("=" * 50)
    
    # Patrones peligrosos
    dangerous_patterns = [
        (r'f".*SELECT.*\{.*\}', 'f-string en SELECT'),
        (r"f'.*SELECT.*\{.*\}", 'f-string en SELECT'),
        (r'f".*INSERT.*\{.*\}', 'f-string en INSERT'),
        (r"f'.*INSERT.*\{.*\}", 'f-string en INSERT'),
        (r'f".*UPDATE.*\{.*\}', 'f-string en UPDATE'),
        (r"f'.*UPDATE.*\{.*\}", 'f-string en UPDATE'),
        (r'f".*DELETE.*\{.*\}', 'f-string en DELETE'),
        (r"f'.*DELETE.*\{.*\}", 'f-string en DELETE'),
        (r'\.format\(.*\).*execute', '.format() con execute'),
        (r'%.*%.*execute', '% formatting con execute'),
        (r'".*\+.*\+.*".*execute', 'concatenación de strings en SQL'),
        (r"'.*\+.*\+.*'.*execute", 'concatenación de strings en SQL'),
    ]
    
    vulnerable_files = []
    
    # Buscar en archivos Python
    for py_file in Path('src').rglob('*.py'):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    for pattern, description in dangerous_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            vulnerable_files.append({
                                'file': str(py_file),
                                'line': line_num,
                                'content': line.strip(),
                                'vulnerability': description
                            })
        except Exception as e:
            print(f"Error leyendo {py_file}: {e}")
    
    # Reportar resultados
    if vulnerable_files:
        print(f"🚨 ENCONTRADAS {len(vulnerable_files)} VULNERABILIDADES POTENCIALES:")
        print()
        
        for vuln in vulnerable_files:
            print(f"Archivo: {vuln['file']}")
            print(f"Línea: {vuln['line']}")
            print(f"Tipo: {vuln['vulnerability']}")
            print(f"Código: {vuln['content']}")
            print("-" * 50)
    else:
        print("✅ No se encontraron vulnerabilidades SQL injection obvias")
    
    return vulnerable_files

def scan_hardcoded_credentials():
    """Buscar credenciales hardcodeadas"""
    print(f"\nBUSCANDO CREDENCIALES HARDCODEADAS")
    print("=" * 50)
    
    credential_patterns = [
        (r'password\s*=\s*["\'][^"\']+["\']', 'password hardcodeado'),
        (r'pwd\s*=\s*["\'][^"\']+["\']', 'pwd hardcodeado'),
        (r'admin.*admin', 'usuario/contraseña admin'),
        (r'sa.*password', 'credenciales SQL Server'),
        (r'secret.*=.*["\'][^"\']+["\']', 'secret hardcodeado'),
    ]
    
    credential_issues = []
    
    for py_file in Path('src').rglob('*.py'):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    for pattern, description in credential_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            credential_issues.append({
                                'file': str(py_file),
                                'line': line_num,
                                'content': line.strip(),
                                'issue': description
                            })
        except Exception as e:
            print(f"Error leyendo {py_file}: {e}")
    
    if credential_issues:
        print(f"🚨 ENCONTRADAS {len(credential_issues)} CREDENCIALES HARDCODEADAS:")
        print()
        
        for issue in credential_issues:
            print(f"Archivo: {issue['file']}")
            print(f"Línea: {issue['line']}")
            print(f"Tipo: {issue['issue']}")
            print(f"Código: {issue['content']}")
            print("-" * 50)
    else:
        print("✅ No se encontraron credenciales hardcodeadas obvias")
    
    return credential_issues

def scan_user_creation_functions():
    """Buscar funciones que crean usuarios automáticamente"""
    print(f"\nBUSCANDO CREACION AUTOMATICA DE USUARIOS")
    print("=" * 50)
    
    user_creation_patterns = [
        (r'def.*create.*user', 'función create user'),
        (r'def.*crear.*usuario', 'función crear usuario'),
        (r'INSERT.*usuarios.*admin', 'insert usuario admin'),
        (r'default.*admin', 'admin por defecto'),
    ]
    
    user_creation_issues = []
    
    for py_file in Path('src').rglob('*.py'):
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                for line_num, line in enumerate(lines, 1):
                    for pattern, description in user_creation_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            user_creation_issues.append({
                                'file': str(py_file),
                                'line': line_num,
                                'content': line.strip(),
                                'issue': description
                            })
        except Exception as e:
            print(f"Error leyendo {py_file}: {e}")
    
    if user_creation_issues:
        print(f"⚠️  ENCONTRADAS {len(user_creation_issues)} FUNCIONES DE CREACION DE USUARIOS:")
        print()
        
        for issue in user_creation_issues:
            print(f"Archivo: {issue['file']}")
            print(f"Línea: {issue['line']}")
            print(f"Tipo: {issue['issue']}")
            print(f"Código: {issue['content']}")
            print("-" * 50)
    else:
        print("✅ No se encontraron funciones de creación automática de usuarios")
    
    return user_creation_issues

if __name__ == "__main__":
    print("INICIANDO AUDITORIA DE SEGURIDAD...")
    print()
    
    # Ejecutar auditorías
    sql_vulns = scan_sql_injection_vulnerabilities()
    cred_issues = scan_hardcoded_credentials()
    user_creation_issues = scan_user_creation_functions()
    
    # Resumen
    total_issues = len(sql_vulns) + len(cred_issues) + len(user_creation_issues)
    
    print(f"\n" + "=" * 50)
    print("RESUMEN DE AUDITORIA")
    print("=" * 50)
    print(f"SQL Injection vulnerabilidades: {len(sql_vulns)}")
    print(f"Credenciales hardcodeadas: {len(cred_issues)}")
    print(f"Creación automática usuarios: {len(user_creation_issues)}")
    print(f"TOTAL DE PROBLEMAS: {total_issues}")
    
    if total_issues > 0:
        print(f"\n🚨 SE REQUIERE ACCION INMEDIATA")
        print("Estos problemas de seguridad deben ser corregidos antes de producción")
    else:
        print(f"\n✅ AUDITORIA BASICA PASADA")
        print("No se encontraron problemas de seguridad obvios")