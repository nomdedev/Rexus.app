"""
Script para diagnosticar y corregir problemas de estructura de base de datos.
Verifica las columnas faltantes y corrige las consultas SQL.
"""

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from core.database import ObrasDatabaseConnection


def verificar_estructura_tablas():
    """
    Verifica la estructura de las tablas principales para identificar columnas faltantes.
    """
    try:
        db = ObrasDatabaseConnection()
        db.conectar()

        print("🔍 Verificando estructura de tablas...")

        # Verificar tabla vidrios_por_obra
        print("\n📋 Tabla: vidrios_por_obra")
        query_columnas = (
            "SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT "
            "FROM INFORMATION_SCHEMA.COLUMNS "
            "WHERE TABLE_NAME = 'vidrios_por_obra' "
            "ORDER BY ORDINAL_POSITION"
        )

        columnas = db.ejecutar_query(query_columnas)
        if columnas:
            print("   Columnas encontradas:")
            for col in columnas:
                print(f"   • {col[0]} ({col[1]}) - Nullable: {col[2]}")
        else:
            print("   ❌ Tabla no encontrada o sin columnas")

        # Aquí puedes agregar más verificaciones de tablas si lo necesitas

    except Exception as e:
        print(f"❌ Error verificando estructura: {e}")


def main():
    verificar_estructura_tablas()


if __name__ == "__main__":
    main()
