#!/usr/bin/env python3
"""
Script para verificar y arreglar el sistema de login
"""

import sys
import os
import hashlib

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def verificar_login():
    """Verifica si el login funciona correctamente"""
    print("VERIFICANDO SISTEMA DE LOGIN")
    print("=" * 50)
    
    try:
        from src.core.database import DatabaseConnection
        from src.core.security import get_security_manager
        
        # Obtener el security manager
        security_manager = get_security_manager()
        
        # Intentar login con admin/admin
        print("1. Probando login con admin/admin...")
        
        # Primero verificar que el usuario existe
        db = DatabaseConnection('users')
        cursor = db.cursor()
        
        cursor.execute("SELECT id, usuario, password_hash, rol, estado FROM usuarios WHERE usuario = ?", ('admin',))
        usuario = cursor.fetchone()
        
        if usuario:
            print(f"   Usuario encontrado: {usuario[1]}")
            print(f"   Rol: {usuario[3]}")
            print(f"   Estado: {usuario[4]}")
            print(f"   Hash en BD: {usuario[2][:20]}...")
            
            # Verificar hash de contraseña
            hash_admin = hashlib.sha256('admin'.encode()).hexdigest()
            print(f"   Hash calculado: {hash_admin[:20]}...")
            
            if usuario[2] == hash_admin:
                print("   [OK] Hash de contraseña coincide")
                
                # Probar el security manager
                try:
                    result = security_manager.authenticate_user('admin', 'admin')
                    if result:
                        print("   [OK] Autenticación exitosa")
                        print(f"   Resultado: {result}")
                    else:
                        print("   [ERROR] Autenticación falló")
                except Exception as e:
                    print(f"   [ERROR] Error en autenticación: {e}")
                    
            else:
                print("   [ERROR] Hash de contraseña no coincide")
        else:
            print("   [ERROR] Usuario admin no encontrado")
            
        cursor.close()
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def crear_usuario_prueba():
    """Crea un usuario de prueba para verificar el sistema"""
    print("\n" + "=" * 50)
    print("CREANDO USUARIO DE PRUEBA")
    print("=" * 50)
    
    try:
        from src.core.database import DatabaseConnection
        
        db = DatabaseConnection('users')
        cursor = db.cursor()
        
        # Verificar si el usuario test ya existe
        cursor.execute("SELECT id FROM usuarios WHERE usuario = ?", ('test',))
        if cursor.fetchone():
            print("Usuario 'test' ya existe")
            return True
        
        # Crear usuario de prueba
        hash_password = hashlib.sha256('test123'.encode()).hexdigest()
        
        cursor.execute("""
            INSERT INTO usuarios (nombre, apellido, email, usuario, password_hash, rol, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ('Test', 'User', 'test@rexus.com', 'test', hash_password, 'usuario', 'Activo'))
        
        db.commit()
        cursor.close()
        
        print("✓ Usuario 'test' creado exitosamente")
        print("  - Usuario: test")
        print("  - Contraseña: test123")
        print("  - Rol: usuario")
        
        return True
        
    except Exception as e:
        print(f"ERROR creando usuario: {e}")
        return False

def verificar_estructura_permisos():
    """Verifica que existan las tablas necesarias para permisos"""
    print("\n" + "=" * 50)
    print("VERIFICANDO ESTRUCTURA DE PERMISOS")
    print("=" * 50)
    
    try:
        from src.core.database import DatabaseConnection
        
        db = DatabaseConnection('users')
        cursor = db.cursor()
        
        # Verificar tablas necesarias
        tablas_necesarias = ['usuarios', 'roles', 'permisos_usuario', 'modulos']
        
        for tabla in tablas_necesarias:
            cursor.execute("SELECT name FROM sysobjects WHERE name=? AND xtype='U'", (tabla,))
            if cursor.fetchone():
                print(f"✓ Tabla {tabla} existe")
            else:
                print(f"✗ Tabla {tabla} NO existe")
        
        cursor.close()
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    """Función principal"""
    print("DIAGNÓSTICO Y REPARACIÓN DEL SISTEMA DE LOGIN")
    print("=" * 60)
    
    # Verificar login actual
    verificar_login()
    
    # Crear usuario de prueba
    crear_usuario_prueba()
    
    # Verificar estructura de permisos
    verificar_estructura_permisos()
    
    print("\n" + "=" * 60)
    print("DIAGNÓSTICO COMPLETADO")
    print("=" * 60)
    
    print("\nPRÓXIMOS PASOS RECOMENDADOS:")
    print("1. Implementar módulo de gestión de usuarios")
    print("2. Crear sistema de permisos granulares")
    print("3. Implementar interface para crear/editar usuarios")
    print("4. Agregar sistema de roles personalizados")

if __name__ == "__main__":
    main()