#!/usr/bin/env python3
"""
Script para verificar la estructura de usuarios en la base de datos
y mostrar qué usuarios están disponibles para autenticación
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))


def verificar_usuarios_bd():
    """Verifica la estructura de usuarios en la base de datos"""
    try:
        print("🔍 VERIFICANDO ESTRUCTURA DE USUARIOS EN BASE DE DATOS")
        print("=" * 60)

        # Importar el módulo de base de datos
        from rexus.core.database import get_connection

        # Conectar a la base de datos de usuarios
        conn = get_connection("users")
        cursor = conn.cursor()

        print("✅ Conexión exitosa a base de datos 'users'")

        # Verificar si existe la tabla usuarios
        print("\n📋 Verificando existencia de tabla 'usuarios'...")
        cursor.execute("""
            SELECT COUNT(*) 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_NAME = 'usuarios'
        """)

        if cursor.fetchone()[0] == 0:
            print("❌ Tabla 'usuarios' NO EXISTE")
            print("   Necesitas ejecutar las migraciones de base de datos")
            return False
        else:
            print("✅ Tabla 'usuarios' existe")

        # Mostrar estructura de la tabla
        print("\n📊 Estructura de la tabla 'usuarios':")
        cursor.execute("""
            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'usuarios'
            ORDER BY ORDINAL_POSITION
        """)

        columns = cursor.fetchall()
        for col in columns:
            nullable = "NULL" if col[2] == "YES" else "NOT NULL"
            default = f" DEFAULT {col[3]}" if col[3] else ""
            print(f"  - {col[0]}: {col[1]} {nullable}{default}")

        # Verificar qué usuarios existen (sin mostrar passwords)
        print("\n👥 Usuarios existentes en la base de datos:")
        cursor.execute("""
            SELECT usuario, nombre, apellido, email, rol, estado
            FROM usuarios
            WHERE estado = 'activo'
        """)

        users = cursor.fetchall()
        if not users:
            print("❌ NO HAY USUARIOS ACTIVOS en la base de datos")
            print("   Necesitas crear usuarios antes de hacer login")
            return False

        print(f"   Encontrados {len(users)} usuarios activos:")
        for user in users:
            print(f"   - Usuario: {user[0]}")
            print(f"     Nombre: {user[1]} {user[2] or ''}")
            print(f"     Email: {user[3]}")
            print(f"     Rol: {user[4]}")
            print(f"     Estado: {user[5]}")
            print()

        # Verificar si hay passwords configuradas
        print("🔐 Verificando configuración de passwords...")
        cursor.execute("""
            SELECT COUNT(*) 
            FROM usuarios 
            WHERE password_hash IS NOT NULL AND password_hash != ''
        """)

        users_with_pass = cursor.fetchone()[0]
        print(f"   Usuarios con password configurada: {users_with_pass}/{len(users)}")

        if users_with_pass == 0:
            print("❌ NINGÚN USUARIO tiene password configurada")
            print("   Necesitas configurar passwords antes de hacer login")
            return False
        elif users_with_pass < len(users):
            print("⚠️  Algunos usuarios NO tienen password configurada")
        else:
            print("✅ Todos los usuarios tienen password configurada")

        conn.close()

        print("\n" + "=" * 60)
        print("📝 RESUMEN:")
        print(f"   - Tabla usuarios: ✅ Existe")
        print(f"   - Usuarios activos: {len(users)}")
        print(f"   - Usuarios con password: {users_with_pass}")

        if users_with_pass > 0:
            print("✅ La base de datos está lista para autenticación")
            return True
        else:
            print("❌ La base de datos NO está lista para autenticación")
            return False

    except ImportError as e:
        print(f"❌ Error importando módulos: {e}")
        print("   Verifica que los módulos de base de datos estén disponibles")
        return False
    except Exception as e:
        print(f"❌ Error conectando a base de datos: {e}")
        print("   Verifica la configuración de conexión en .env")
        return False


if __name__ == "__main__":
    exito = verificar_usuarios_bd()
    if not exito:
        print("\n⚠️  Para solucionar esto, necesitas:")
        print("   1. Ejecutar las migraciones de base de datos")
        print("   2. Crear usuarios con passwords")
        print("   3. Configurar roles y permisos correctamente")
    sys.exit(0 if exito else 1)
