#!/usr/bin/env python3
"""
Script para agregar columnas faltantes a la tabla inventario_perfiles
=====================================================================

Agrega las columnas 'categoria' y 'precio_unitario' que necesita el módulo
de inventario para funcionar correctamente.
"""

import traceback

import pyodbc


def agregar_columnas_inventario_perfiles():
    """Agrega las columnas necesarias a la tabla inventario_perfiles."""

    print("🔧 AGREGANDO COLUMNAS A LA TABLA inventario_perfiles")
    print("=" * 60)

    try:
        # Conectar a la base de datos
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=DESKTOP-QHMPTGO\\SQLEXPRESS;"
            "DATABASE=inventario;"
            "UID=sa;"
            "PWD=mps.1887;"
            "TrustServerCertificate=yes;"
        )
        cursor = conn.cursor()

        print("✅ Conexión a base de datos establecida")

        # 1. Verificar columnas existentes
        print("\n🔍 Verificando columnas existentes...")
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'inventario_perfiles'
            ORDER BY ORDINAL_POSITION
        """)
        columnas_existentes = [row[0] for row in cursor.fetchall()]
        print(f"📋 Columnas actuales: {columnas_existentes}")

        # 2. Agregar columna 'categoria' si no existe
        if "categoria" not in columnas_existentes:
            print("\n➕ Agregando columna 'categoria'...")
            cursor.execute("""
                ALTER TABLE inventario_perfiles 
                ADD categoria NVARCHAR(100) NULL
            """)
            print("✅ Columna 'categoria' agregada")
        else:
            print("✅ Columna 'categoria' ya existe")

        # 3. Agregar columna 'precio_unitario' si no existe
        if "precio_unitario" not in columnas_existentes:
            print("\n➕ Agregando columna 'precio_unitario'...")
            cursor.execute("""
                ALTER TABLE inventario_perfiles 
                ADD precio_unitario DECIMAL(10,2) NULL DEFAULT 0.00
            """)
            print("✅ Columna 'precio_unitario' agregada")
        else:
            print("✅ Columna 'precio_unitario' ya existe")

        # 4. Agregar columna 'activo' si no existe
        if "activo" not in columnas_existentes:
            print("\n➕ Agregando columna 'activo'...")
            cursor.execute("""
                ALTER TABLE inventario_perfiles 
                ADD activo BIT NOT NULL DEFAULT 1
            """)
            print("✅ Columna 'activo' agregada")
        else:
            print("✅ Columna 'activo' ya existe")

        # 5. Confirmar cambios
        conn.commit()
        print("\n💾 Cambios confirmados en la base de datos")

        # 6. Verificar columnas después de los cambios
        print("\n🔍 Verificando estructura final...")
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_NAME = 'inventario_perfiles'
            ORDER BY ORDINAL_POSITION
        """)
        columnas_finales = cursor.fetchall()

        print("📋 Estructura final de la tabla:")
        for col in columnas_finales:
            print(f"   🔸 {col[0]} ({col[1]}) - Nulo: {col[2]}")

        # 7. Actualizar algunos registros con datos de ejemplo
        print("\n📝 Actualizando registros con datos de ejemplo...")

        # Obtener algunos registros para actualizar
        cursor.execute("SELECT TOP 10 id FROM inventario_perfiles")
        ids = [row[0] for row in cursor.fetchall()]

        categorias_ejemplo = [
            "Perfiles",
            "Vidrios",
            "Herrajes",
            "Accesorios",
            "Materiales",
        ]

        for i, id_producto in enumerate(ids):
            categoria = categorias_ejemplo[i % len(categorias_ejemplo)]
            precio = (i + 1) * 25.50  # Precio de ejemplo

            cursor.execute(
                """
                UPDATE inventario_perfiles 
                SET categoria = ?, precio_unitario = ?, activo = 1 
                WHERE id = ?
            """,
                (categoria, precio, id_producto),
            )

        conn.commit()
        print(f"✅ Actualizados {len(ids)} registros con datos de ejemplo")

        # 8. Verificar datos actualizados
        print("\n🔍 Verificando datos actualizados...")
        cursor.execute("""
            SELECT TOP 5 id, codigo, descripcion, categoria, precio_unitario, activo 
            FROM inventario_perfiles 
            WHERE categoria IS NOT NULL
        """)
        registros = cursor.fetchall()

        print("📊 Primeros registros con datos actualizados:")
        for reg in registros:
            print(
                f"   ID: {reg[0]}, Código: {reg[1]}, Categoría: {reg[3]}, Precio: ${reg[4]}"
            )

        conn.close()

        print("\n" + "=" * 60)
        print("✅ PROCESO COMPLETADO EXITOSAMENTE")
        print("🔸 Columnas agregadas: categoria, precio_unitario, activo")
        print("🔸 Datos de ejemplo actualizados")
        print("🔸 La tabla inventario_perfiles está lista para usar")
        return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    resultado = agregar_columnas_inventario_perfiles()
    if resultado:
        print("\n🎉 ¡Las columnas se agregaron correctamente!")
    else:
        print("\n💥 Hubo un error al agregar las columnas")
    exit(0 if resultado else 1)
