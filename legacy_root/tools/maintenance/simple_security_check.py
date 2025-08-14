#!/usr/bin/env python3
"""
Verificación simple de seguridad
"""

import os
import sys
import re
from pathlib import Path

def check_sql_injection():
    """Buscar SQL injection en archivos específicos"""
    print("VERIFICANDO SQL INJECTION")
    print("=" * 30)

    # Archivos a revisar
    files_to_check = [
        'src/modules/usuarios/model.py',
        'src/core/security.py',
        'src/core/auth.py'
    ]

    problems = []

    for file_path in files_to_check:
        if not os.path.exists(file_path):
            continue

        print(f"\nRevisando: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, 1):
            line = line.strip()

            # Buscar patrones peligrosos
            if re.search(r'f".*SELECT.*\{', line):
                problems.append(f"{file_path}:{line_num} - f-string en SELECT: {line}")
            elif re.search(r'f".*INSERT.*\{', line):
                problems.append(f"{file_path}:{line_num} - f-string en INSERT: {line}")
            elif re.search(r'f".*UPDATE.*\{', line):
                problems.append(f"{file_path}:{line_num} - f-string en UPDATE: {line}")
            elif re.search(r'f".*DELETE.*\{', line):
                problems.append(f"{file_path}:{line_num} - f-string en DELETE: {line}")
            elif '.format(' in line and 'execute' in line:
                problems.append(f"{file_path}:{line_num} - .format() con execute: {line}")

    if problems:
        print(f"\nPROBLEMAS ENCONTRADOS: {len(problems)}")
        for problem in problems:
            print(f"  - {problem}")
    else:
        print("\nOK: No se encontraron problemas obvios de SQL injection")

    return problems

def check_hardcoded_users():
    """Buscar creación de usuarios hardcodeados"""
    print(f"\n\nVERIFICANDO USUARIOS HARDCODEADOS")
    print("=" * 30)

    files_to_check = [
        'src/core/security.py',
        'src/modules/usuarios/model.py'
    ]

    problems = []

    for file_path in files_to_check:
        if not os.path.exists(file_path):
            continue

        print(f"\nRevisando: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, 1):
            line_lower = line.lower().strip()

            # Buscar creación de usuarios
            if 'insert into usuarios' in line_lower and \
                ('admin' in line_lower or 'password' in line_lower):
                problems.append(f"{file_path}:{line_num} - INSERT usuario hardcodeado: {line.strip()}")
            elif 'create_default_admin' in line and 'def ' in line:
                problems.append(f"{file_path}:{line_num} - Función crear admin: {line.strip()}")

    if problems:
        print(f"\nPROBLEMAS ENCONTRADOS: {len(problems)}")
        for problem in problems:
            print(f"  - {problem}")
    else:
        print("\nOK: No se encontraron creaciones de usuarios hardcodeados")

    return problems

if __name__ == "__main__":
    print("VERIFICACION SIMPLE DE SEGURIDAD")
    print("=" * 40)

    sql_problems = check_sql_injection()
    user_problems = check_hardcoded_users()

    total = len(sql_problems) + len(user_problems)

    print(f"\n" + "=" * 40)
    print("RESUMEN")
    print(f"SQL Injection: {len(sql_problems)} problemas")
    print(f"Usuarios hardcodeados: {len(user_problems)} problemas")
    print(f"TOTAL: {total} problemas")

    if total > 0:
        print("\nACCION REQUERIDA: Corregir problemas de seguridad")
    else:
        print("\nOK: Verificación básica pasada")
