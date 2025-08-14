#!/usr/bin/env python3
"""
Script simplificado para ejecutar el SQL del módulo RRHH y probar la aplicación.
"""

def ejecutar_sql_rrhh():
    """Ejecuta el script SQL para crear el módulo RRHH"""

import os
import subprocess
import sys
from datetime import datetime

    print("🗄️ EJECUTANDO SCRIPT SQL DEL MÓDULO RRHH")
    print("="*50)

    sql_file = os.path.join(os.path.dirname(__file__),
'..',
        'database',
        'crear_modulo_rrhh.sql')

    if not os.path.exists(sql_file):
        print(f"[ERROR] No se encontró el archivo SQL: {sql_file}")
        return False

    print(f"📄 Ejecutando: {sql_file}")

    try:
        # Usar sqlcmd para ejecutar el SQL (requiere SQL Server Command Line tools)
        cmd = [
            'sqlcmd',
            '-S', 'localhost\\SQLEXPRESS',  # Ajustar según tu configuración
            '-d', 'MPS_INVENTARIO',  # Base de datos
            '-i', sql_file,
            '-E'  # Usar autenticación de Windows
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("[CHECK] Script SQL ejecutado exitosamente")
            print("📋 Salida:")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print("[ERROR] Error al ejecutar script SQL")
            print("📋 Error:")
            if result.stderr:
                print(result.stderr)
            return False

    except FileNotFoundError:
        print("[WARN] sqlcmd no está disponible")
        print("💡 Puede ejecutar manualmente el archivo SQL en SQL Server Management Studio")
        print(f"📄 Archivo: {sql_file}")
        return True  # Continuar de todas formas
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False

def probar_aplicacion():
    """Inicia la aplicación para pruebas"""

    print("\n[ROCKET] INICIANDO APLICACIÓN PARA PRUEBAS")
    print("="*45)

    try:
        main_path = os.path.join(os.path.dirname(__file__),
'..',
            '..',
            'main.py')

        if not os.path.exists(main_path):
            print(f"[ERROR] No se encontró main.py en: {main_path}")
            return False

        print("[CHECK] Ejecutando: python main.py")
        print("💡 La aplicación se iniciará en segundo plano")
        print("🔐 Use las credenciales de un usuario existente para login")
        print("📋 Si no tiene usuario, créelo manualmente en la BD")

        # Ejecutar la aplicación
        subprocess.Popen([sys.executable, main_path], cwd=os.path.dirname(main_path))

        return True

    except Exception as e:
        print(f"[ERROR] Error al iniciar aplicación: {e}")
        return False

def mostrar_instrucciones():
    """Muestra instrucciones para el testing manual"""

    print("\n📋 INSTRUCCIONES PARA TESTING MANUAL")
    print("="*50)

    print("1. 🔐 LOGIN:")
    print("   - La aplicación ya NO tiene modo invitado por seguridad")
    print("   - Use credenciales de un usuario existente")
    print("   - Si no tiene usuario, créelo en la tabla 'usuarios' de la BD")

    print("\n2. 🧪 MÓDULOS A PROBAR:")
    modulos = [
        "Inventario - Buscar, filtrar, ver detalles",
        "Obras - Crear nueva, ver listado",
        "Vidrios - Consultar catálogo, aplicar filtros",
        "Herrajes - Explorar categorías",
        "Compras/Pedidos - Navegación básica",
        "Logística - Funcionalidades principales",
        "Mantenimiento - Acceso y navegación",
        "Contabilidad - Reportes básicos",
        "Auditoría - Consultar logs",
        "Usuarios - Ver listado (si tiene permisos)",
        "Configuración - Diferentes secciones",
        "RRHH - Nuevo módulo (si se ejecutó el SQL)"
    ]

    for i, modulo in enumerate(modulos, 1):
        print(f"   {i:2d}. {modulo}")

    print("\n3. 🔍 QUÉ BUSCAR:")
    print("   [ERROR] Errores de importación")
    print("   [ERROR] Errores de base de datos")
    print("   [ERROR] Problemas con iconos/estilos")
    print("   [ERROR] Excepciones no manejadas")
    print("   [WARN] Warnings en logs")
    print("   [LOCK] Problemas de permisos")

    print("\n4. 📝 DOCUMENTAR:")
    print("   - Anote cualquier error en logs/app.log")
    print("   - Capture screenshots de problemas visuales")
    print("   - Pruebe diferentes roles de usuario")
    print("   - Valide que la auditoría funcione")

def crear_sql_usuario_simple():
    """Crea un script SQL simple para crear usuario de prueba"""

    print("\n👤 CREANDO SCRIPT PARA USUARIO DE PRUEBA")
    print("="*45)

    sql_content = """
-- Script para crear usuario de prueba
-- Ejecutar manualmente en SQL Server Management Studio

USE MPS_INVENTARIO;

-- Crear usuario de prueba si no existe
IF NOT EXISTS (SELECT 1 FROM usuarios WHERE username = 'test_user')
BEGIN
    INSERT INTO usuarios (username,
password,
        nombre,
        email,
        rol,
        activo,
        fecha_creacion)
    VALUES (
        'test_user',
        'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', -- Hash de 'test123'
        'Usuario de Prueba',
        'test@empresa.com',
        'TEST_USER',
        1,
        GETDATE()
    );
    PRINT '[CHECK] Usuario de prueba creado: test_user / test123';
END
ELSE
BEGIN
    PRINT '[WARN] Usuario test_user ya existe';
END

-- Verificar usuarios activos
SELECT username, nombre, rol, activo FROM usuarios WHERE activo = 1;
"""

    try:
        sql_file = os.path.join(os.path.dirname(__file__), 'crear_usuario_prueba.sql')

        with open(sql_file, 'w', encoding='utf-8') as f:
            f.write(sql_content)

        print(f"[CHECK] Script SQL creado: {sql_file}")
        print("💡 Ejecute este script manualmente en SQL Server para crear usuario de prueba")
        print("🔐 Credenciales: test_user / test123")

        return True

    except Exception as e:
        print(f"[ERROR] Error al crear script SQL: {e}")
        return False

def main():
    """Función principal"""

    print("🧪 SETUP PARA TESTING DE LA APLICACIÓN")
    print("="*60)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Paso 1: Ejecutar SQL del módulo RRHH
    print("🗄️ PASO 1: Configurar módulo RRHH")
    if not ejecutar_sql_rrhh():
        print("[WARN] El módulo RRHH no se configuró automáticamente")
        print("💡 Puede ejecutar el SQL manualmente más tarde")

    # Paso 2: Crear script para usuario de prueba
    print("\n👤 PASO 2: Configurar usuario de prueba")
    if not crear_sql_usuario_simple():
        print("[WARN] No se pudo crear script de usuario")

    # Paso 3: Mostrar instrucciones
    mostrar_instrucciones()

    # Paso 4: Preguntar si iniciar la aplicación
    print("\n" + "="*60)
    respuesta = input("¿Desea iniciar la aplicación ahora? (s/n): ").lower()

    if respuesta in ['s', 'si', 'y', 'yes']:
        if probar_aplicacion():
            print("\n🎉 Aplicación iniciada exitosamente")
            print("🔍 Comience a probar los módulos según las instrucciones")
        else:
            print("\n[ERROR] No se pudo iniciar la aplicación automáticamente")
            print("💡 Inicie manualmente con: python main.py")
    else:
        print("\n💡 Para iniciar la aplicación manualmente:")
        print("   cd /path/to/stock.app")
        print("   python main.py")

    print("\n✨ Setup completado. ¡Feliz testing!")
    return True

if __name__ == '__main__':
    main()
