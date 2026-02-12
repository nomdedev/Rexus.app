#!/usr/bin/env python3
"""
Script para verificar las correcciones críticas realizadas.
"""

import sys
import os
import traceback

sys.path.insert(0, os.getcwd())

def test_imports():
    """Prueba las importaciones críticas."""
    print("🔍 Probando importaciones críticas...")
    
    tests = [
        ("rexus.utils.unified_sanitizer", "UnifiedSanitizer"),
        ("rexus.utils.sql_script_loader", "SQLScriptLoader"),
        ("rexus.utils.logging_config", "get_logger"),
        ("rexus.core.auth_decorators", "auth_required"),
    ]
    
    for module_name, class_name in tests:
        try:
            module = __import__(module_name, fromlist=[class_name])
            getattr(module, class_name)
            print(f"✅ {module_name}.{class_name} - Importado correctamente")
        except Exception as e:
            print(f"❌ {module_name}.{class_name} - Error: {e}")
            traceback.print_exc()

def test_syntax():
    """Prueba la sintaxis de archivos críticos."""
    print("\n🔍 Probando sintaxis de archivos críticos...")
    
    files_to_check = [
        'rexus/modules/11_usuarios/model.py',
        'rexus/modules/11_usuarios/security_features.py',
        'rexus/modules/04_vidrios/model.py'
    ]
    
    for file_path in files_to_check:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            compile(content, file_path, 'exec')
            print(f"✅ {file_path} - Sintaxis correcta")
        except SyntaxError as e:
            print(f"❌ {file_path} - Error de sintaxis: {e}")
            print(f"   Línea {e.lineno}: {e.text}")
        except Exception as e:
            print(f"⚠️  {file_path} - Error: {e}")

def main():
    """Función principal."""
    print("🚀 Iniciando verificación de correcciones críticas...")
    
    test_imports()
    test_syntax()
    
    print("\n🏁 Verificación completada.")

if __name__ == "__main__":
    main()