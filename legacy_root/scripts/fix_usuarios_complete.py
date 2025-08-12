#!/usr/bin/env python3
"""
Corrección completa y definitiva de submódulos de usuarios
"""

import re
from pathlib import Path

def fix_all_cursor_issues():
    """Corrige todos los problemas de cursor en profiles_manager.py"""
    file_path = Path("rexus/modules/usuarios/submodules/profiles_manager.py")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Inicializar todos los cursors correctamente
    # Buscar patrones donde cursor se declara directamente
    cursor_patterns = [
        (r'(\s+)(cursor = self\.db_connection\.cursor\(\))', 
         r'\1cursor = None\n\1cursor = self.db_connection.cursor()'),
    ]
    
    for pattern, replacement in cursor_patterns:
        content = re.sub(pattern, replacement, content)
    
    # 2. Corregir todos los finally blocks con cursor
    finally_pattern = r'(\s+)finally:\s*\n(\s+)if \'cursor\' in locals\(\):\s*\n(\s+)if cursor:\s*\n(\s+)cursor\.close\(\)'
    finally_replacement = r'\1finally:\n\2if cursor is not None:\n\2    try:\n\2        cursor.close()\n\2    except Exception as e:\n\2        logger.error(f"Error cerrando cursor: {e}")'
    
    content = re.sub(finally_pattern, finally_replacement, content, flags=re.MULTILINE)
    
    # 3. Corregir otros patterns de if cursor:
    if_cursor_pattern = r'(\s+)if cursor:\s*\n(\s+)cursor\.close\(\)'
    if_cursor_replacement = r'\1if cursor is not None:\n\2try:\n\2    cursor.close()\n\2except Exception as e:\n\2    logger.error(f"Error cerrando cursor: {e}")'
    
    content = re.sub(if_cursor_pattern, if_cursor_replacement, content, flags=re.MULTILINE)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Corregidos problemas de cursor en profiles_manager.py")

def fix_auth_manager():
    """Corrige auth_manager.py"""
    file_path = Path("rexus/modules/usuarios/submodules/auth_manager.py")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Buscar el try/except/pass específico en línea 187
    # Reemplazar except Exception: pass con manejo de error apropiado
    pattern = r'(\s+)try:\s*\n(\s+)if cursor:\s*\n(\s+)cursor\.close\(\)\s*\n(\s+)except Exception:\s*\n(\s+)pass'
    replacement = r'\1try:\n\2if cursor is not None:\n\3cursor.close()\n\4except Exception as e:\n\5logger.error(f"Error cerrando cursor: {e}")'
    
    content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Corregido auth_manager.py")

def fix_permissions_manager():
    """Corrige permissions_manager.py"""
    file_path = Path("rexus/modules/usuarios/submodules/permissions_manager.py")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Corregir los try/except/pass patterns
    patterns = [
        # Pattern 1: if self.db_connection: con try/except/pass
        (r'(\s+)if self\.db_connection:\s*\n(\s+)try:\s*\n(\s+)self\.db_connection\.close\(\)\s*\n(\s+)except Exception:\s*\n(\s+)pass',
         r'\1if self.db_connection:\n\2try:\n\3self.db_connection.close()\n\4except Exception as e:\n\5logger.error(f"Error cerrando conexión: {e}")'),
        
        # Pattern 2: except Exception as e: pass
        (r'(\s+)except Exception as e:\s*\n(\s+)pass',
         r'\1except Exception as e:\n\2logger.error(f"Error en operación: {e}")'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Corregido permissions_manager.py")

def main():
    print("🔧 CORRECCIÓN DEFINITIVA - SUBMÓDULOS DE USUARIOS")
    print("=" * 55)
    
    fix_all_cursor_issues()
    fix_auth_manager()
    fix_permissions_manager()
    
    print("\n📊 CORRECCIONES COMPLETADAS")
    print("  • Problemas de cursor resueltos")
    print("  • Patrones try/except/pass corregidos")
    print("  • Manejo de errores mejorado")
    
    print("\n🔄 Ejecutar get_errors para verificar correcciones")

if __name__ == "__main__":
    main()
