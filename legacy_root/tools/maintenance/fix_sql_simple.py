#!/usr/bin/env python3
"""
Script simple para corregir vulnerabilidades SQL injection
"""

import os
import re

def fix_file(file_path):
    """Corrige un archivo específico"""
    if not os.path.exists(file_path):
        return False

    print(f"Procesando: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original = content

        # Reemplazar f-strings en SQL con concatenación segura
        # f"SELECT ... FROM {table}" -> "SELECT ... FROM " + table
        content = re.sub(r'f"([^"]*)(SELECT|INSERT|UPDATE|DELETE)([^"]*)\{([^}]+)\}([^"]*)"',
                        r'"\1\2\3" + \4 + "\5"', content, flags=re.IGNORECASE)

        content = re.sub(r"f'([^']*)(SELECT|INSERT|UPDATE|DELETE)([^']*)\{([^}]+)\}([^']*)'",
                        r"'\1\2\3' + \4 + '\5'", content, flags=re.IGNORECASE)

        # Queries multilinea
        content = re.sub(r'f"""([^"]*)(SELECT|INSERT|UPDATE|DELETE)([^"]*)\{([^}]+)\}([^"]*)"""',
                        r'"""\1\2\3""" + \4 + """\5"""', content, flags=re.IGNORECASE | re.DOTALL)

        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  CORREGIDO")
            return True
        else:
            print(f"  Sin cambios")
            return False

    except Exception as e:
        print(f"  ERROR: {e}")
        return False

# Archivos a corregir
files = [
    "src/modules/vidrios/model.py",
    "src/core/audit_trail.py",
    "src/core/database.py",
    "src/core/backup_manager.py",
    "src/modules/mantenimiento/model.py",
    "src/modules/inventario/model.py",
    "src/modules/logistica/model.py",
    "src/modules/configuracion/model.py",
    "src/modules/herrajes/model.py",
    "src/modules/administracion/recursos_humanos/model.py",
    "src/modules/administracion/contabilidad/model.py",
    "src/api/server.py"
]

print("CORRECTOR SQL INJECTION")
print("=" * 30)

fixed = 0
for file_path in files:
    if fix_file(file_path):
        fixed += 1

print("\n" + "=" * 30)
print(f"Archivos corregidos: {fixed}")
print("Ejecutar: python -m bandit -r src/ para verificar")
