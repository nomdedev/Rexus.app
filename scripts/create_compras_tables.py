#!/usr/bin/env python3
"""
Script para crear las tablas de compras faltantes
Ejecuta el script SQL existente de forma segura
"""

import sys
import os
from pathlib import Path

# Añadir path del proyecto
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    # Intentar importar desde la estructura nueva
    from rexus.core.database import get_inventario_connection
except ImportError:
    print("[ERROR] No se puede importar get_inventario_connection")
    print("Verificar estructura de proyecto")
    sys.exit(1)


def execute_sql_file(sql_file_path):
    """Ejecuta un archivo SQL de forma segura."""
    try:
        # Leer el archivo SQL
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        # Conectar a base de datos
        connection = get_inventario_connection()
        if not connection:
            print("[ERROR] No se pudo conectar a la base de datos inventario")
            return False

        cursor = connection.cursor()

        # Ejecutar el script completo
        print(f"[INFO] Ejecutando script: {sql_file_path}")
        cursor.execute(sql_content)
        connection.commit()

        print("[SUCCESS] Script ejecutado exitosamente")
        print("[SUCCESS] Tablas 'compras' y 'detalle_compras' creadas")

        # Verificar que las tablas fueron creadas
        cursor.execute("""
            SELECT TABLE_NAME
            FROM INFORMATION_SCHEMA.TABLES
            WHERE TABLE_NAME IN ('compras', 'detalle_compras')
        """)

        tables = [row[0] for row in cursor.fetchall()]
        print(f"[VERIFY] Tablas encontradas: {tables}")

        if 'compras' in tables and 'detalle_compras' in tables:
            print("[SUCCESS] ✅ Verificación exitosa: Ambas tablas existen")
            return True
        else:
            print("[WARNING] ⚠️ Algunas tablas no fueron encontradas")
            return False

    except Exception as e:
        print(f"[ERROR] Error ejecutando script SQL: {e}")
        return False
    finally:
        if 'connection' in locals():
            connection.close()


def main():
    """Función principal."""
    print("=" * 60)
    print("🔧 REXUS.APP - CREACIÓN DE TABLAS COMPRAS")
    print("=" * 60)

    # Buscar el archivo SQL
    sql_paths = [
        project_root / "sql" / "compras_simple.sql",
        project_root / "scripts" / "database" / "compras_simple.sql",
    ]

    sql_file = None
    for path in sql_paths:
        if path.exists():
            sql_file = path
            break

    if not sql_file:
        print("[ERROR] No se encontró el archivo compras_simple.sql")
        print("Rutas buscadas:")
        for path in sql_paths:
            print(f"  - {path}")
        sys.exit(1)

    print(f"[INFO] Usando archivo SQL: {sql_file}")

    # Ejecutar el script
    success = execute_sql_file(sql_file)

    if success:
        print("\n" + "=" * 60)
        print("✅ COMPLETADO EXITOSAMENTE")
        print("✅ Las tablas de compras han sido creadas")
        print("✅ El módulo de compras ahora debería funcionar correctamente")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("❌ ERROR EN LA CREACIÓN")
        print("❌ Revisar logs para más detalles")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
