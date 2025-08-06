#!/usr/bin/env python3
"""
Verificador del Sistema de Backup - Rexus.app
============================================

Script para verificar que el sistema de backup esté correctamente instalado
y configurado antes de su uso en producción.
"""

import os
import sys
import subprocess
from pathlib import Path

def verificar_python():
    """Verifica versión de Python"""
    print("[CHECK] Verificando Python...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"[OK] Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"[ERROR] Python {version.major}.{version.minor} - Se requiere Python 3.8+")
        return False

def verificar_dependencias():
    """Verifica dependencias Python"""
    print("[CHECK] Verificando dependencias...")
    dependencias = ['pyodbc', 'schedule']
    
    for dep in dependencias:
        try:
            __import__(dep)
            print(f"[OK] {dep} instalado")
        except ImportError:
            print(f"[ERROR] {dep} no instalado - ejecutar: pip install {dep}")
            return False
    
    return True

def verificar_sqlcmd():
    """Verifica disponibilidad de sqlcmd"""
    print("[CHECK] Verificando sqlcmd...")
    try:
        result = subprocess.run(['sqlcmd', '/?'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        if result.returncode == 0:
            print("[OK] sqlcmd disponible")
            return True
        else:
            print("[WARNING] sqlcmd no funciona correctamente")
            return False
    except FileNotFoundError:
        print("[WARNING] sqlcmd no encontrado - funcionalidad limitada")
        return False
    except Exception as e:
        print(f"[WARNING] Error verificando sqlcmd: {e}")
        return False

def verificar_estructura():
    """Verifica estructura del proyecto"""
    print("[CHECK] Verificando estructura del proyecto...")
    
    directorios_requeridos = [
        'rexus',
        'rexus/core',
        'rexus/utils',
        'tools/development/backup'
    ]
    
    archivos_requeridos = [
        '.env',
        'tools/development/backup/sistema_backup_automatizado.py',
        'tools/development/backup/backup_config.json'
    ]
    
    for directorio in directorios_requeridos:
        if Path(directorio).exists():
            print(f"[OK] Directorio: {directorio}")
        else:
            print(f"[ERROR] Directorio faltante: {directorio}")
            return False
    
    for archivo in archivos_requeridos:
        if Path(archivo).exists():
            print(f"[OK] Archivo: {archivo}")
        else:
            print(f"[ERROR] Archivo faltante: {archivo}")
            return False
    
    return True

def verificar_variables_entorno():
    """Verifica variables de entorno de base de datos"""
    print("[CHECK] Verificando variables de entorno...")
    
    variables_requeridas = [
        'DB_SERVER',
        'DB_USERNAME', 
        'DB_PASSWORD',
        'DB_USERS',
        'DB_INVENTARIO',
        'DB_AUDITORIA'
    ]
    
    # Cargar .env si existe
    env_file = Path('.env')
    if env_file.exists():
        print("[INFO] Archivo .env encontrado")
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            print("[WARNING] python-dotenv no instalado, usando solo variables de sistema")
    
    missing = []
    for var in variables_requeridas:
        if os.getenv(var):
            print(f"[OK] {var} configurado")
        else:
            missing.append(var)
    
    if missing:
        print(f"[ERROR] Variables faltantes: {', '.join(missing)}")
        return False
    
    return True

def verificar_conectividad():
    """Verifica conectividad básica a bases de datos"""
    print("[CHECK] Verificando conectividad a bases de datos...")
    
    try:
        # Importar el sistema de backup
        sys.path.insert(0, '.')
        from rexus.core.database import get_users_connection, get_inventario_connection, get_auditoria_connection
        
        conexiones = {
            'users': get_users_connection,
            'inventario': get_inventario_connection,
            'auditoria': get_auditoria_connection
        }
        
        for db_name, connection_func in conexiones.items():
            try:
                conn = connection_func()
                if conn:
                    conn.close()
                    print(f"[OK] Conexión a {db_name}")
                else:
                    print(f"[ERROR] No se pudo conectar a {db_name}")
                    return False
            except Exception as e:
                print(f"[ERROR] Error conectando a {db_name}: {str(e)}")
                return False
        
        return True
        
    except ImportError as e:
        print(f"[ERROR] Error importando módulos de conexión: {e}")
        return False

def verificar_permisos():
    """Verifica permisos de escritura"""
    print("[CHECK] Verificando permisos...")
    
    # Verificar directorio actual
    if not os.access('.', os.W_OK):
        print("[ERROR] Sin permisos de escritura en directorio actual")
        return False
    
    # Crear directorio de backups de prueba
    backup_test_dir = Path('backups_test')
    try:
        backup_test_dir.mkdir(exist_ok=True)
        
        # Crear archivo de prueba
        test_file = backup_test_dir / 'test.txt'
        test_file.write_text('test')
        
        # Leer archivo
        content = test_file.read_text()
        
        # Limpiar
        test_file.unlink()
        backup_test_dir.rmdir()
        
        print("[OK] Permisos de lectura/escritura")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error de permisos: {e}")
        return False

def main():
    """Función principal de verificación"""
    print("=" * 60)
    print("  VERIFICADOR DEL SISTEMA DE BACKUP - REXUS.APP")
    print("=" * 60)
    print()
    
    verificaciones = [
        ("Python", verificar_python),
        ("Dependencias", verificar_dependencias),
        ("SQL Command", verificar_sqlcmd),
        ("Estructura", verificar_estructura),
        ("Variables de Entorno", verificar_variables_entorno),
        ("Conectividad", verificar_conectividad),
        ("Permisos", verificar_permisos)
    ]
    
    resultados = []
    
    for nombre, funcion in verificaciones:
        print(f"\n--- {nombre} ---")
        try:
            resultado = funcion()
            resultados.append((nombre, resultado))
        except Exception as e:
            print(f"[CRASH] Error ejecutando verificación {nombre}: {e}")
            resultados.append((nombre, False))
    
    print("\n" + "=" * 60)
    print("  RESUMEN DE VERIFICACIÓN")
    print("=" * 60)
    
    exitosos = 0
    for nombre, resultado in resultados:
        status = "[OK]" if resultado else "[FAIL]"
        print(f"{status:6} {nombre}")
        if resultado:
            exitosos += 1
    
    print(f"\nResultado: {exitosos}/{len(resultados)} verificaciones exitosas")
    
    if exitosos == len(resultados):
        print("\n[SUCCESS] Sistema de backup listo para usar!")
        print("Ejecutar: python tools/development/backup/sistema_backup_automatizado.py")
        return True
    else:
        print(f"\n[WARNING] {len(resultados) - exitosos} problemas encontrados")
        print("Resolver problemas antes de usar el sistema de backup")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)