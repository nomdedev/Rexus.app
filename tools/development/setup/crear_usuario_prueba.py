#!/usr/bin/env python3
"""
Script para crear un usuario de prueba con permisos completos
para realizar testing de la aplicación de forma segura.
"""

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
except ImportError as e:
    print(f"[ERROR] Error al importar módulos necesarios: {e}")
    print("💡 Asegúrese de ejecutar desde el directorio raíz del proyecto")
    sys.exit(1)

import hashlib
import os
import sys
from datetime import datetime

from core.database import DatabaseConnection


def hash_password(password):
    """Genera un hash seguro de la contraseña"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def crear_usuario_prueba():
    """Crea un usuario de prueba para testing"""

    print("🔧 CREADOR DE USUARIO DE PRUEBA")
    print("="*50)

    # Datos del usuario de prueba
    usuario_data = {
        'usuario': 'test_user',
        'nombre': 'Usuario de Prueba',
        'apellido': 'Testing',
        'email': 'test@testing.local',
        'password': 'Test123!',  # Contraseña temporal para testing
        'rol': 'TEST_USER',
        'activo': 1
    }

    try:
        # Conectar a la base de datos
        db = DatabaseConnection()
        db.conectar_a_base('users')

        print("[CHECK] Conexión a base de datos establecida")

        # Verificar si el usuario ya existe
        result = db.ejecutar_query("""
            SELECT COUNT(*) as count FROM usuarios
            WHERE usuario = ? OR email = ?
        """, (usuario_data['usuario'], usuario_data['email']))

        if result and result[0][0] > 0:
            print("[WARN] El usuario de prueba ya existe")

            # Preguntar si quiere actualizar
            respuesta = input("¿Desea actualizar el usuario existente? (s/n): ").lower()
            if respuesta not in ['s', 'si', 'y', 'yes']:
                print("[ERROR] Operación cancelada")
                return False

            # Actualizar usuario existente
            password_hash = hash_password(usuario_data['password'])
            db.ejecutar_query("""
                UPDATE usuarios
                SET nombre = ?, apellido = ?, email = ?, password = ?,
                    rol = ?, activo = ?, fecha_modificacion = ?
                WHERE usuario = ?
            """, (
                usuario_data['nombre'],
                usuario_data['apellido'],
                usuario_data['email'],
                password_hash,
                usuario_data['rol'],
                usuario_data['activo'],
                datetime.now(),
                usuario_data['usuario']
            ))

            print("[CHECK] Usuario de prueba actualizado")

        else:
            # Crear nuevo usuario
            password_hash = hash_password(usuario_data['password'])
            db.ejecutar_query("""
                INSERT INTO usuarios (usuario, nombre, apellido, email, password, rol, activo, fecha_creacion)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                usuario_data['usuario'],
                usuario_data['nombre'],
                usuario_data['apellido'],
                usuario_data['email'],
                password_hash,
                usuario_data['rol'],
                usuario_data['activo'],
                datetime.now()
            ))

            print("[CHECK] Usuario de prueba creado")

        # Obtener el ID del usuario
        result = db.ejecutar_query("SELECT id FROM usuarios WHERE usuario = ?", (usuario_data['usuario'],))
        if not result:
            print("[ERROR] Error: No se pudo obtener el ID del usuario")
            return False

        user_id = result[0][0]

        # Asignar permisos completos para todos los módulos
        modulos = [
            'Inventario', 'Obras', 'Pedidos', 'Compras', 'Vidrios',
            'Herrajes', 'Logística', 'Mantenimiento', 'Producción',
            'Contabilidad', 'Auditoría', 'Usuarios', 'Configuración'
        ]

        # Limpiar permisos existentes
        db.ejecutar_query("DELETE FROM permisos_usuarios WHERE usuario_id = ?", (user_id,))

        # Asignar permisos completos
        for modulo in modulos:
            db.ejecutar_query("""
                INSERT INTO permisos_usuarios (usuario_id, modulo, lectura, escritura, eliminacion, configuracion)
                VALUES (?, ?, 1, 1, 1, 1)
            """, (user_id, modulo))

        print("[CHECK] Permisos completos asignados")

        # Mostrar información del usuario creado
        print("\n" + "="*50)
        print("📋 INFORMACIÓN DEL USUARIO DE PRUEBA")
        print("="*50)
        print(f"👤 Usuario: {usuario_data['usuario']}")
        print(f"🔑 Contraseña: {usuario_data['password']}")
        print(f"📧 Email: {usuario_data['email']}")
        print(f"🏷️ Rol: {usuario_data['rol']}")
        print(f"[CHART] Módulos con acceso: {len(modulos)}")

        print("\n🔐 PERMISOS ASIGNADOS:")
        for modulo in modulos:
            print(f"  [CHECK] {modulo}: Lectura, Escritura, Eliminación, Configuración")

        print("\n[WARN] IMPORTANTE:")
        print("• Este usuario es SOLO para testing y desarrollo")
        print("• Cambie la contraseña en producción")
        print("• Elimine este usuario cuando termine las pruebas")

        return True

    except Exception as e:
        print(f"[ERROR] Error inesperado: {e}")
        return False

def validar_usuario_prueba():
    """Valida que el usuario de prueba funcione correctamente"""

    print("\n🔍 VALIDANDO USUARIO DE PRUEBA...")

    try:
        db = DatabaseConnection()
        db.conectar_a_base('users')

        # Verificar usuario
        result = db.ejecutar_query("""
            SELECT id, usuario, nombre, rol, activo
            FROM usuarios
            WHERE usuario = 'test_user'
        """)

        if not result:
            print("[ERROR] Usuario de prueba no encontrado")
            return False

        user = result[0]
        print(f"[CHECK] Usuario encontrado: {user[1]} ({user[2]}) - Rol: {user[3]}")

        # Verificar permisos
        result = db.ejecutar_query("""
            SELECT modulo, lectura, escritura, eliminacion, configuracion
            FROM permisos_usuarios
            WHERE usuario_id = ?
        """, (user[0],))

        if not result:
            print("[ERROR] No se encontraron permisos para el usuario")
            return False

        print(f"[CHECK] Permisos encontrados: {len(result)} módulos")

        # Verificar que tiene permisos completos
        permisos_completos = all(
            perm[1] == 1 and perm[2] == 1 and perm[3] == 1 and perm[4] == 1
            for perm in result
        )

        if permisos_completos:
            print("[CHECK] Todos los permisos están configurados correctamente")
        else:
            print("[WARN] Algunos permisos pueden estar limitados")

        return True

    except Exception as e:
        print(f"[ERROR] Error en validación: {e}")
        return False

def eliminar_usuario_prueba():
    """Elimina el usuario de prueba cuando ya no se necesite"""

    print("\n🗑️ ELIMINANDO USUARIO DE PRUEBA...")

    confirmacion = input("¿Está seguro de que desea eliminar el usuario de prueba? (s/n): ").lower()
    if confirmacion not in ['s', 'si', 'y', 'yes']:
        print("[ERROR] Operación cancelada")
        return False

    try:
        db = DatabaseConnection()
        db.conectar_a_base('users')

        # Obtener ID del usuario
        result = db.ejecutar_query("SELECT id FROM usuarios WHERE usuario = 'test_user'")

        if not result:
            print("[WARN] Usuario de prueba no encontrado")
            return True

        user_id = result[0][0]

        # Eliminar permisos
        db.ejecutar_query("DELETE FROM permisos_usuarios WHERE usuario_id = ?", (user_id,))

        # Eliminar usuario
        db.ejecutar_query("DELETE FROM usuarios WHERE id = ?", (user_id,))

        print("[CHECK] Usuario de prueba eliminado exitosamente")

        return True

    except Exception as e:
        print(f"[ERROR] Error al eliminar usuario: {e}")
        return False

def main():
    """Función principal"""
    print("🛠️ GESTOR DE USUARIO DE PRUEBA")
    print("="*60)
    print("Este script permite crear/validar/eliminar un usuario de prueba")
    print("para realizar testing seguro de la aplicación.")
    print()

    opciones = {
        '1': ('Crear/Actualizar usuario de prueba', crear_usuario_prueba),
        '2': ('Validar usuario de prueba', validar_usuario_prueba),
        '3': ('Eliminar usuario de prueba', eliminar_usuario_prueba),
        '4': ('Salir', lambda: True)
    }

    while True:
        print("\n📋 OPCIONES DISPONIBLES:")
        for key, (desc, _) in opciones.items():
            print(f"  {key}. {desc}")

        opcion = input("\nSeleccione una opción (1-4): ").strip()

        if opcion not in opciones:
            print("[ERROR] Opción inválida")
            continue

        if opcion == '4':
            print("👋 ¡Hasta luego!")
            break

        desc, func = opciones[opcion]
        print(f"\n[ROCKET] Ejecutando: {desc}")
        print("-" * 40)

        try:
            resultado = func()
            if resultado:
                print("[CHECK] Operación completada exitosamente")
            else:
                print("[ERROR] La operación no se completó correctamente")
        except Exception as e:
            print(f"[ERROR] Error inesperado: {e}")

if __name__ == '__main__':
    main()
