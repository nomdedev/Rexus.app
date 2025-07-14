"""
Script para unificar nomenclatura de columnas en la base de datos
Corrige la inconsistencia entre obra_id e id_obra
"""
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def unificar_nomenclatura_columnas():
    """Unifica la nomenclatura de columnas para usar 'obra_id' consistentemente"""
import os
import sys

from core.database import ObrasDatabaseConnection

    db = ObrasDatabaseConnection()
    try:
        db.conectar()
        print("✅ Conectado a la base de datos")

        # Lista de cambios a realizar: (tabla, columna_actual, columna_nueva)
        cambios_nomenclatura = [
            ('vidrios_por_obra', 'id_obra', 'obra_id'),
            ('herrajes_por_obra', 'id_obra', 'obra_id'),
            ('obra_materiales', 'id_obra', 'obra_id'),  # Si existe
            ('pagos_por_obra', 'id_obra', 'obra_id'),   # Si existe
            ('logistica_por_obra', 'id_obra', 'obra_id'), # Si existe
        ]

        print("\n🔧 Verificando y corrigiendo nomenclatura de columnas...")

        for tabla, columna_actual, columna_nueva in cambios_nomenclatura:
            try:
                # Verificar si la tabla existe
                check_table = f"SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '{tabla}'"
                table_exists = db.ejecutar_query(check_table)

                if not table_exists:
                    print(f"  ⚠️ Tabla {tabla} no existe - saltando")
                    continue

                # Verificar si la columna actual existe
                check_column = f"""
                SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = '{tabla}' AND COLUMN_NAME = '{columna_actual}'
                """
                column_exists = db.ejecutar_query(check_column)

                if not column_exists:
                    print(f"  ⚠️ Columna {columna_actual} no existe en {tabla} - saltando")
                    continue

                # Verificar si ya existe la columna nueva
                check_new_column = f"""
                SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = '{tabla}' AND COLUMN_NAME = '{columna_nueva}'
                """
                new_column_exists = db.ejecutar_query(check_new_column)

                if new_column_exists:
                    print(f"  ✅ Columna {columna_nueva} ya existe en {tabla}")
                    continue

                # Realizar el cambio de nombre
                sql_rename = f"EXEC sp_rename '{tabla}.{columna_actual}', '{columna_nueva}', 'COLUMN'"

                print(f"  🔧 Renombrando {tabla}.{columna_actual} → {columna_nueva}")
                db.ejecutar_query(sql_rename)
                print(f"  ✅ {tabla}.{columna_nueva} - Cambio completado")

            except Exception as e:
                print(f"  ❌ Error en {tabla}: {e}")

        print("\n📋 Verificando resultados...")

        # Verificar las tablas principales
        tablas_verificar = ['vidrios_por_obra', 'herrajes_por_obra', 'pedidos_material']

        for tabla in tablas_verificar:
            try:
                query_cols = f"""
                SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_NAME = '{tabla}' AND COLUMN_NAME LIKE '%obra%'
                """
                cols = db.ejecutar_query(query_cols)
                col_names = [row[0] for row in cols] if cols else []
                print(f"  📌 {tabla}: columnas obra = {col_names}")
            except Exception as e:
                print(f"  ❌ Error verificando {tabla}: {e}")

        print("\n✅ Proceso de unificación completado")

    except Exception as e:
        print(f"❌ Error crítico: {e}")
    finally:
        db.cerrar_conexion()
        print("🔚 Conexión cerrada")

def verificar_integridad_post_cambio():
    """Verifica que las relaciones funcionen después del cambio"""

    db = ObrasDatabaseConnection()
    try:
        db.conectar()
        print("\n🔍 Verificando integridad post-cambio...")

        # Test de joins entre tablas
        test_queries = [
            ("Obras con vidrios", """
            SELECT COUNT(*) FROM obras o
            INNER JOIN vidrios_por_obra v ON o.id = v.obra_id
            """),
            ("Obras con herrajes", """
            SELECT COUNT(*) FROM obras o
            INNER JOIN herrajes_por_obra h ON o.id = h.obra_id
            """),
            ("Obras con pedidos material", """
            SELECT COUNT(*) FROM obras o
            INNER JOIN pedidos_material p ON o.id = p.obra_id
            """)
        ]

        for nombre, query in test_queries:
            try:
                result = db.ejecutar_query(query)
                count = result[0][0] if result else 0
                print(f"  ✅ {nombre}: {count} relaciones válidas")
            except Exception as e:
                print(f"  ❌ {nombre}: Error - {e}")

    except Exception as e:
        print(f"❌ Error en verificación: {e}")
    finally:
        db.cerrar_conexion()

if __name__ == "__main__":
    print("🚀 UNIFICACIÓN DE NOMENCLATURA DE COLUMNAS")
    print("=" * 60)

    unificar_nomenclatura_columnas()
    verificar_integridad_post_cambio()

    print("\n🎉 Proceso completado - Base de datos unificada")
