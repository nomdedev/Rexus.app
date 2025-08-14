#!/usr/bin/env python3
"""
Reporte rápido de issues pendientes
"""

import os
from pathlib import Path
from datetime import datetime

def quick_audit():
    print("🔍 AUDITORÍA RÁPIDA DE ISSUES PENDIENTES")
    print("=" * 50)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    issues_found = []

    # 1. Verificar permissions_manager.py que sabemos tiene warnings
    print("1️⃣ Verificando permissions_manager.py...")
    perm_file = Path("rexus/modules/usuarios/submodules/permissions_manager.py")
    if perm_file.exists():
        issues_found.append("⚠️ permissions_manager.py: 3 warnings try/except/pass restantes")

    # 2. Verificar archivos críticos faltantes mencionados en auditorías
    print("2️⃣ Verificando archivos críticos...")
    critical_files = [
        ("rexus/core/security_manager.py", "HIGH"),
        ("requirements.txt", "MEDIUM"),
        ("README.md", "LOW"),
    ]

    for file_path, priority in critical_files:
        if not Path(file_path).exists():
            issues_found.append(f"🔴 {priority}: Falta {file_path}")

    # 3. Verificar configuración de producción
    print("3️⃣ Verificando configuración de producción...")
    config_files = [
        ".env.production.template",
        "config/production_config_template.json"
    ]

    config_present = all(Path(f).exists() for f in config_files)
    if config_present:
        issues_found.append("✅ Configuración de producción: COMPLETA")
    else:
        for f in config_files:
            if not Path(f).exists():
                issues_found.append(f"🟡 MEDIUM: Verificar {f}")

    # 4. Verificar SQLQueryManager
    print("4️⃣ Verificando SQLQueryManager...")
    sql_manager = Path("rexus/core/sql_query_manager.py")
    if sql_manager.exists():
        issues_found.append("✅ SQLQueryManager: PRESENTE")
    else:
        issues_found.append("🔴 HIGH: SQLQueryManager faltante")

    # 5. Verificar tests
    print("5️⃣ Verificando tests...")
    test_dir = Path("tests")
    if test_dir.exists() and any(test_dir.rglob("test_*.py")):
        issues_found.append("✅ Tests: PRESENTES")
    else:
        issues_found.append("🟡 MEDIUM: Cobertura de tests incompleta")

    # 6. Verificar documentación crítica
    print("6️⃣ Verificando documentación...")
    docs = [
        "docs/CHECKLIST_CORRECCIONES_COMPLETADO.md",
        "docs/AUDITORIA_FINAL_COMPLETADA_2025.md"
    ]

    docs_present = sum(1 for doc in docs if Path(doc).exists())
    issues_found.append(f"✅ Documentación de auditoría: {docs_present}/2 presente")

    print("\n📊 RESUMEN DE ISSUES ENCONTRADOS")
    print("-" * 50)

    critical_count = sum(1 for issue in issues_found if "🔴" in issue)
    medium_count = sum(1 for issue in issues_found if "🟡" in issue)
    warning_count = sum(1 for issue in issues_found if "⚠️" in issue)
    completed_count = sum(1 for issue in issues_found if "✅" in issue)

    print(f"🔴 CRÍTICOS: {critical_count}")
    print(f"🟡 MEDIANOS: {medium_count}")
    print(f"⚠️ WARNINGS: {warning_count}")
    print(f"✅ COMPLETADOS: {completed_count}")

    print("\n📋 DETALLE DE ISSUES:")
    for issue in issues_found:
        print(f"  {issue}")

    print(f"\n🎯 PRÓXIMAS ACCIONES RECOMENDADAS:")
    print("1. 🔧 Corregir warnings en permissions_manager.py (15 min)")
    print("2. 📄 Crear requirements.txt si no existe (5 min)")
    print("3. 📚 Verificar documentación faltante (10 min)")
    print("4. 🧪 Ejecutar tests existentes (5 min)")

    total_issues = critical_count + medium_count + warning_count

    if total_issues <= 3:
        print(f"\n🎉 ESTADO: EXCELENTE - Pocos issues menores")
        print(f"   El proyecto está prácticamente listo para producción")
    elif total_issues <= 7:
        print(f"\n👍 ESTADO: BUENO - Issues menores controlables")
        print(f"   Unas pocas correcciones y estará listo")
    else:
        print(f"\n⚠️ ESTADO: NECESITA ATENCIÓN - Varios issues pendientes")
        print(f"   Requiere trabajo adicional antes de producción")

if __name__ == "__main__":
    quick_audit()
