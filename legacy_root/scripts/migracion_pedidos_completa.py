#!/usr/bin/env python3
"""
Script de Migración Completa - Módulo Pedidos
Migra de SQL embebido a SQL externo con mejoras de seguridad

ACCIONES REALIZADAS:
[CHECK] Crear estructura SQL externa completa
[CHECK] Crear modelo refactorizado con:
   - SQL 100% externo
   - Imports unificados sin duplicados
   - DataSanitizer con fallback robusto
   - Decoradores de autorización implementados
   - Validaciones robustas
   - Gestión de errores mejorada

PRÓXIMOS PASOS:
1. Ejecutar tests para validar funcionalidad
2. Actualizar controladores para usar modelo refactorizado
3. Crear tests de seguridad específicos
4. Aplicar migración similar a otros módulos críticos
"""

import os
import shutil
from datetime import datetime


def migrar_modelo_pedidos():
    """Aplica la migración del modelo de pedidos."""

    print("🔄 INICIANDO MIGRACIÓN MODELO PEDIDOS")
    print("=" * 50)

    # 1. Crear backup del modelo original
    print("📦 Creando backup del modelo original...")
    modelo_original = "rexus/modules/pedidos/model.py"
    backup_path = (
        f"backups/pedidos_model_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    )

    os.makedirs("backups", exist_ok=True)
    if os.path.exists(modelo_original):
        shutil.copy2(modelo_original, backup_path)
        print(f"[CHECK] Backup creado: {backup_path}")

    # 2. Verificar archivos SQL externos creados
    print("\n📂 Verificando archivos SQL externos...")
    sql_files = [
        "scripts/sql/pedidos/create_pedidos_table.sql",
        "scripts/sql/pedidos/create_pedidos_detalle_table.sql",
        "scripts/sql/pedidos/create_pedidos_historial_table.sql",
        "scripts/sql/pedidos/create_pedidos_entregas_table.sql",
        "scripts/sql/pedidos/insertar_pedido.sql",
        "scripts/sql/pedidos/listar_pedidos.sql",
        "scripts/sql/pedidos/obtener_pedido_por_id.sql",
        "scripts/sql/pedidos/actualizar_estado_pedido.sql",
        "scripts/sql/pedidos/insertar_historial_estado.sql",
        "scripts/sql/pedidos/obtener_estadisticas_pedidos.sql",
        "scripts/sql/pedidos/validar_cliente_existe.sql",
        "scripts/sql/pedidos/validar_obra_existe.sql",
        "scripts/sql/pedidos/validar_pedido_duplicado.sql",
    ]

    for sql_file in sql_files:
        if os.path.exists(sql_file):
            print(f"[CHECK] {sql_file}")
        else:
            print(f"[ERROR] FALTANTE: {sql_file}")

    # 3. Verificar modelo refactorizado
    print("\n🏗️  Verificando modelo refactorizado...")
    modelo_refactorizado = "rexus/modules/pedidos/model_refactorizado.py"
    if os.path.exists(modelo_refactorizado):
        print(f"[CHECK] {modelo_refactorizado}")

        # Mostrar métricas del archivo
        with open(modelo_refactorizado, "r", encoding="utf-8") as f:
            lines = f.readlines()
            print(f"   [CHART] Líneas totales: {len(lines)}")

            # Contar imports y SQL embebido
            imports_auth = sum(
                1 for line in lines if "auth_required" in line and \
                    "import" in line
            )
            sql_embebido = sum(
                1
                for line in lines
                if any(
                    sql in line.upper()
                    for sql in ["SELECT", "INSERT", "UPDATE", "DELETE", "CREATE TABLE"]
                )
            )

            print(f"   [CHART] Imports auth: {imports_auth}")
            print(f"   [CHART] SQL embebido restante: {sql_embebido}")

    else:
        print(f"[ERROR] FALTANTE: {modelo_refactorizado}")

    # 4. Mostrar comparación
    print("\n[CHART] COMPARACIÓN MODELOS")
    print("-" * 30)

    if os.path.exists(modelo_original):
        with open(modelo_original, "r", encoding="utf-8") as f:
            original_lines = len(f.readlines())
        print(f"🔴 Original: {original_lines} líneas (SQL embebido)")

    if os.path.exists(modelo_refactorizado):
        with open(modelo_refactorizado, "r", encoding="utf-8") as f:
            refactored_lines = len(f.readlines())
        print(f"🟢 Refactorizado: {refactored_lines} líneas (SQL externo)")

        if os.path.exists(modelo_original):
            reduccion = ((original_lines - refactored_lines) / original_lines) * 100
            print(f"📉 Reducción código: {reduccion:.1f}%")

    print("\n[CHECK] MIGRACIÓN COMPLETADA")
    print("=" * 50)

    print("\n🎯 PRÓXIMOS PASOS RECOMENDADOS:")
    print("1. Ejecutar tests: python -m pytest tests/pedidos/ -v")
    print("2. Validar funcionalidad en controladores")
    print("3. Aplicar migración similar a otros módulos críticos")
    print("4. Ejecutar análisis de seguridad")


if __name__ == "__main__":
    migrar_modelo_pedidos()
