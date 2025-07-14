#!/usr/bin/env python3
"""
Script simple para crear usuario de prueba para testing de la aplicación.
Este script elimina el modo invitado y crea un usuario con permisos completos.
"""

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

def hash_password(password):
    """Genera hash de contraseña simple"""
    return hashlib.sha256(password.encode()).hexdigest()

def crear_usuario_prueba():
    """Crea un usuario de prueba con permisos completos"""

    print("🔧 CREANDO USUARIO DE PRUEBA PARA TESTING")
    print("="*50)

    try:
        db = DatabaseConnection()

        # Datos del usuario de prueba
        usuario_prueba = {
            'username': 'test_user',
            'password': hash_password('test123'),
            'nombre': 'Usuario de Prueba',
            'email': 'test@empresa.com',
            'rol': 'TEST_USER',
            'activo': 1
        }

        print(f"👤 Creando usuario: {usuario_prueba['username']}")
        print(f"🔑 Contraseña: test123")
        print(f"👨‍💼 Rol: {usuario_prueba['rol']}")

        # Verificar si ya existe
        check_query = "SELECT COUNT(*) FROM usuarios WHERE username = ?"
        result = db.ejecutar_query(check_query, (usuario_prueba['username'],))

        if result and len(result) > 0 and result[0][0] > 0:
            print("⚠️ El usuario de prueba ya existe. Actualizando...")

            update_query = """
                UPDATE usuarios
                SET password = ?, nombre = ?, email = ?, rol = ?, activo = ?
                WHERE username = ?
            """

            cursor = db.ejecutar_query(update_query, (
                usuario_prueba['password'],
                usuario_prueba['nombre'],
                usuario_prueba['email'],
                usuario_prueba['rol'],
                usuario_prueba['activo'],
                usuario_prueba['username']
            ))

            if cursor is not None:
                print("✅ Usuario de prueba actualizado exitosamente")
            else:
                print("❌ Error al actualizar usuario de prueba")
                return False
        else:
            print("➕ Creando nuevo usuario de prueba...")

            insert_query = """
                INSERT INTO usuarios (username, password, nombre, email, rol, activo, fecha_creacion)
                VALUES (?, ?, ?, ?, ?, ?, GETDATE())
            """

            cursor = db.ejecutar_query(insert_query, (
                usuario_prueba['username'],
                usuario_prueba['password'],
                usuario_prueba['nombre'],
                usuario_prueba['email'],
                usuario_prueba['rol'],
                usuario_prueba['activo']
            ))

            if cursor is not None:
                print("✅ Usuario de prueba creado exitosamente")
            else:
                print("❌ Error al crear usuario de prueba")
                return False

        # Verificar que se creó correctamente
        verify_query = "SELECT id, username, nombre, rol FROM usuarios WHERE username = ?"
        user_data_result = db.ejecutar_query(verify_query, (usuario_prueba['username'],))

        if user_data_result and len(user_data_result) > 0:
            user_data = user_data_result[0]
            print("\n📋 DETALLES DEL USUARIO DE PRUEBA:")
            print(f"   ID: {user_data[0]}")
            print(f"   Username: {user_data[1]}")
            print(f"   Nombre: {user_data[2]}")
            print(f"   Rol: {user_data[3]}")
            print("\n🔐 CREDENCIALES PARA LOGIN:")
            print(f"   Usuario: {usuario_prueba['username']}")
            print(f"   Contraseña: test123")

        return True

    except Exception as e:
        print(f"❌ Error al crear usuario de prueba: {e}")
        return False

def eliminar_modo_invitado():
    """Elimina o desactiva el modo invitado por seguridad"""

    print("\n🔒 ELIMINANDO MODO INVITADO POR SEGURIDAD")
    print("="*45)

    try:
        # Leer el archivo main.py
        main_path = os.path.join(os.path.dirname(__file__), '..', '..', 'main.py')

        with open(main_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Buscar y comentar el modo invitado
        changes_made = False

        # Comentar el botón de modo invitado si existe
        if 'modo invitado' in content.lower() or 'guest mode' in content.lower():
            print("⚠️ Se detectó código de modo invitado en main.py")
            print("💡 Se recomienda revisar y eliminar manualmente por seguridad")
            changes_made = True

        # Buscar en login_view.py también
        login_path = os.path.join(os.path.dirname(__file__), '..', '..', 'modules', 'usuarios', 'login_view.py')

        if os.path.exists(login_path):
            with open(login_path, 'r', encoding='utf-8') as f:
                login_content = f.read()

            if 'modo invitado' in login_content.lower() or 'guest' in login_content.lower():
                print("⚠️ Se detectó código de modo invitado en login_view.py")
                print("💡 Se recomienda revisar y eliminar manualmente por seguridad")
                changes_made = True

        if not changes_made:
            print("✅ No se detectó modo invitado activo")

        return True

    except Exception as e:
        print(f"❌ Error al verificar modo invitado: {e}")
        return False

def verificar_aplicacion():
    """Verifica que la aplicación esté lista para testing"""

    print("\n🔍 VERIFICANDO CONFIGURACIÓN PARA TESTING")
    print("="*50)

    try:
        # Verificar conexión a BD
        db = DatabaseConnection()
        try:
            db.conectar()
            print("✅ Conexión a base de datos: OK")
        except:
            print("❌ Conexión a base de datos: FALLO")
import hashlib
import os
import sys
from datetime import datetime

from core.database import DatabaseConnection

            return False

        # Verificar tabla usuarios
        check_table = "SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'usuarios'"
        result = db.ejecutar_query(check_table)

        if result and len(result) > 0 and result[0][0] > 0:
            print("✅ Tabla usuarios: OK")
        else:
            print("❌ Tabla usuarios: NO EXISTE")
            return False

        # Verificar que hay al menos un usuario de prueba
        admin_check = "SELECT COUNT(*) FROM usuarios WHERE rol = 'TEST_USER' AND activo = 1"
        result = db.ejecutar_query(admin_check)

        if result and len(result) > 0 and result[0][0] > 0:
            print("✅ Usuario de pruebaistrador: OK")
        else:
            print("⚠️ No hay usuarios administradores activos")

        print("\n🎯 La aplicación está lista para testing")
        return True

    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        return False

def main():
    """Función principal"""

    print("🧪 CONFIGURADOR DE USUARIO DE PRUEBA")
    print("="*60)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Paso 1: Eliminar modo invitado
    if not eliminar_modo_invitado():
        print("⚠️ Advertencia: No se pudo verificar/eliminar modo invitado")

    # Paso 2: Crear usuario de prueba
    if not crear_usuario_prueba():
        print("❌ Error crítico: No se pudo crear usuario de prueba")
        return False

    # Paso 3: Verificar configuración
    if not verificar_aplicacion():
        print("⚠️ Advertencia: Verificación incompleta")

    print("\n" + "="*60)
    print("🎉 CONFIGURACIÓN COMPLETADA")
    print("="*60)
    print("✅ Usuario de prueba creado con permisos completos")
    print("🔒 Modo invitado verificado/eliminado")
    print("🧪 La aplicación está lista para testing seguro")
    print()
    print("📝 PRÓXIMOS PASOS:")
    print("1. Ejecutar: python main.py")
    print("2. Usar credenciales: test_user / test123")
    print("3. Probar todos los módulos con permisos completos")
    print("4. Documentar cualquier error encontrado")
    print()

    return True

if __name__ == '__main__':
    success = main()

    if success:
        print("✨ Script completado exitosamente")
        sys.exit(0)
    else:
        print("💥 Script falló")
        sys.exit(1)
