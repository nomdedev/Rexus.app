#!/usr/bin/env python3
"""
XSS Protection Final Check - Rexus.app
=====================================

Script simple para verificar y completar XSS protection en archivos críticos
"""

import os
import re
from pathlib import Path

def check_xss_protection(file_path):
    """Verifica si un archivo tiene protección XSS"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        markers = [
            "XSSProtection",
            "XSS Protection Added",
            "FormProtector",
            "sanitize_text"
        ]

        has_protection = any(marker in content for marker in markers)
        has_forms = any(widget in content for widget in ["QLineEdit", "QTextEdit", "QComboBox"])

        return has_protection, has_forms, len(content.split('\n'))

    except Exception as e:
        return False, False, 0

def main():
    """Verificar estado de protección XSS"""

    print("[XSS CHECK] Verificando estado de proteccion XSS")
    print("=" * 50)

    modules_dir = Path("rexus/modules")
    results = {
        "protected": [],
        "needs_protection": [],
        "no_forms": []
    }

    for module_dir in modules_dir.iterdir():
        if module_dir.is_dir() and not module_dir.name.startswith('__'):
            view_file = module_dir / "view.py"

            if view_file.exists():
                has_protection, has_forms, lines = check_xss_protection(view_file)

                module_name = module_dir.name
                status = ""

                if has_protection:
                    status = "[OK] PROTEGIDO"
                    results["protected"].append(module_name)
                elif has_forms:
                    status = "[NEEDS] SIN PROTECCION"
                    results["needs_protection"].append(module_name)
                else:
                    status = "[SKIP] SIN FORMULARIOS"
                    results["no_forms"].append(module_name)

                print(f"{status:20} {module_name:15} ({lines:4} lineas)")

    print("\n" + "=" * 50)
    print("[SUMMARY] RESUMEN")
    print("=" * 50)

    print(f"Modulos protegidos: {len(results['protected'])}")
    print(f"Necesitan proteccion: {len(results['needs_protection'])}")
    print(f"Sin formularios: {len(results['no_forms'])}")

    if results['needs_protection']:
        print(f"\n[TODO] Modulos que necesitan proteccion XSS:")
        for module in results['needs_protection']:
            print(f"  - {module}")

    total_modules = len(results['protected']) + len(results['needs_protection'])
    if total_modules > 0:
        protection_percentage = (len(results['protected']) / total_modules) * 100
        print(f"\n[RESULT] Cobertura XSS: {protection_percentage:.1f}%")

    if len(results['needs_protection']) == 0:
        print("[SUCCESS] Todos los formularios tienen proteccion XSS!")
    else:
        print(f"[WARNING] {len(results['needs_protection'])} modulos necesitan proteccion")

if __name__ == "__main__":
    main()
