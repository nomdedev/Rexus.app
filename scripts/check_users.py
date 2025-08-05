#!/usr/bin/env python3
"""
Script simple para verificar usuarios en la base de datos
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))


def verificar_usuarios():
    """Verifica usuarios en la base de datos"""
    try:
        print("🔍 VERIFICANDO USUARIOS EN BASE DE DATOS")
        print("=" * 50)

        from rexus.core.database import get_users_connection

        # Conectar a la base de datos de usuarios
        db = get_users_connection()

        if not db.connection:
            print("❌ No se pudo conectar a la base de datos 'users'")
            return False

        print("✅ Conexión exitosa a base de datos 'users'")

        # Verificar tabla usuarios
        try:
            result = db.execute_query("""
                SELECT COUNT(*) 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = 'usuarios'
            """)

            if result and result[0][0] > 0:
                print("✅ Tabla 'usuarios' existe")
            else:
                print("❌ Tabla 'usuarios' NO existe")
                return False

        except Exception as e:
            print(f"❌ Error verificando tabla usuarios: {e}")
            return False

        # Listar usuarios activos
        try:
            users = db.execute_query("""
                SELECT usuario, nombre, apellido, email, rol, estado
                FROM usuarios
                WHERE estado = 'activo'
            """)

            print(f"\n👥 Usuarios activos encontrados: {len(users) if users else 0}")

            if users:
                for user in users:
                    print(f"  - Usuario: {user[0]} | Rol: {user[4]} | Email: {user[3]}")
            else:
                print("❌ NO hay usuarios activos")
                return False

        except Exception as e:
            print(f"❌ Error consultando usuarios: {e}")
            return False

        # Verificar passwords
        try:
            pass_count = db.execute_query("""
                SELECT COUNT(*) 
                FROM usuarios 
                WHERE password_hash IS NOT NULL AND password_hash != ''
            """)

            if pass_count and pass_count[0][0] > 0:
                print(f"✅ {pass_count[0][0]} usuarios con password configurada")
                return True
            else:
                print("❌ NO hay usuarios con password configurada")
                return False

        except Exception as e:
            print(f"❌ Error verificando passwords: {e}")
            return False

    except Exception as e:
        print(f"❌ Error general: {e}")
        return False


if __name__ == "__main__":
    exito = verificar_usuarios()
    if not exito:
        print("\n💡 SOLUCIONES POSIBLES:")
        print(
            "   1. Ejecutar migraciones: python -m scripts.migration.execute_database_migration"
        )
        print("   2. Verificar configuración en .env")
        print("   3. Crear usuarios con el script correspondiente")

    sys.exit(0 if exito else 1)
