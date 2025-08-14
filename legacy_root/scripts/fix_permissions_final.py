#!/usr/bin/env python3
"""
Corrección final de permissions_manager.py
"""

def fix_permissions_manager():
    file_path = "rexus/modules/usuarios/submodules/permissions_manager.py"

    print("🔧 Corrigiendo permissions_manager.py...")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix 1: Corregir return None por return Dict en línea 246
    content = content.replace(
        'return None\n            return {\'success\': False, \'message\': \'Error interno del sistema\'}',
        'return {\'success\': False, \'message\': \'Error crítico del sistema\'}\n            return {\'success\': False, \'message\': \'Error interno del sistema\'}'
    )

    # Fix 2: Similar para línea 294
    content = content.replace(
        'return None\n            return {\'success\': False, \'message\': \'Error interno del sistema\'}',
        'return {\'success\': False, \'message\': \'Error crítico del sistema\'}\n            return {\'success\': False, \'message\': \'Error interno del sistema\'}'
    )

    # Fix 3: Corregir todas las ocurrencias de return None en rollback
    import re

    # Patrón para encontrar y reemplazar return None en contexto de rollback
    pattern = r'(except Exception as \w+:\s*\n\s*logger\.error\(.*?\)\s*\n\s*)return None'
    replacement = r'\1return {\'success\': False, \'message\': \'Error crítico del sistema\'}'

    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

    # Fix 4: Corregir inicialización de cursor
    # Buscar patrones donde cursor no se inicializa correctamente
    cursor_pattern = r'(\s+)(cursor = self\.db_connection\.cursor\(\))'
    cursor_replacement = r'\1cursor = None\n\1cursor = self.db_connection.cursor()'

    content = re.sub(cursor_pattern, cursor_replacement, content)

    # Fix 5: Corregir finally blocks
    finally_pattern = r'(\s+)if \'cursor\' in locals\(\):\s*\n(\s+)if cursor:'
    finally_replacement = r'\1if cursor is not None:'

    content = re.sub(finally_pattern,
finally_replacement,
        content,
        flags=re.MULTILINE)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ permissions_manager.py corregido")

if __name__ == "__main__":
    fix_permissions_manager()
