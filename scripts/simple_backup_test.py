#!/usr/bin/env python3
"""
Test simple del sistema de backup sin Unicode

Prueba básica del sistema de backup sin caracteres especiales
para evitar problemas de codificación en Windows.
"""

import os
import sys
import sqlite3
import tempfile
from pathlib import Path

# Agregar directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from rexus.utils.backup_system import BackupConfig, DatabaseBackupManager
from rexus.core.backup_integration import BackupIntegration


def test_backup_config():
    """Test configuración básica."""
    print("=== TEST CONFIGURACION ===")
    
    config = BackupConfig()
    print(f"Directorio backup: {config.backup_dir}")
    print(f"Horario: {config.backup_schedule} a las {config.backup_time}")
    print(f"Retencion: {config.retention_days} dias")
    print(f"Compresion: {config.compress_backups}")
    print(f"Bases de datos: {config.backup_databases}")
    print("OK - Configuracion basica funciona")
    return config


def test_create_demo_db():
    """Crea una base de datos simple para testing."""
    print("\n=== CREAR BD DEMO ===")
    
    # Crear archivo temporal
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        demo_db_path = f.name
    
    try:
        # Crear base de datos simple
        conn = sqlite3.connect(demo_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE test_data (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                value INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insertar datos de prueba
        test_data = [
            ("Test Record 1", 100),
            ("Test Record 2", 200), 
            ("Test Record 3", 300)
        ]
        
        cursor.executemany("INSERT INTO test_data (name, value) VALUES (?, ?)", test_data)
        conn.commit()
        conn.close()
        
        # Verificar que se creó
        size_mb = os.path.getsize(demo_db_path) / (1024 * 1024)
        print(f"BD creada: {demo_db_path}")
        print(f"Tamaño: {size_mb:.3f} MB")
        print("OK - BD demo creada")
        
        return demo_db_path
        
    except Exception as e:
        print(f"ERROR creando BD: {e}")
        if os.path.exists(demo_db_path):
            os.unlink(demo_db_path)
        return None


def test_backup_manager(demo_db_path):
    """Test del gestor de backup."""
    print("\n=== TEST BACKUP MANAGER ===")
    
    # Crear configuración temporal
    config = BackupConfig()
    config.backup_dir = "test_backups"
    
    # Crear gestor
    manager = DatabaseBackupManager(config)
    print("Gestor creado")
    
    # Realizar backup
    print("Realizando backup...")
    result = manager.backup_single_database("test_db", demo_db_path)
    
    if result.success:
        print(f"EXITO - Backup creado: {result.backup_path}")
        print(f"Tamaño: {result.size_mb:.3f} MB")
        print(f"Duracion: {result.duration_seconds:.2f} segundos")
        return True
    else:
        print(f"ERROR - {result.message}")
        return False


def test_backup_integration():
    """Test de integración."""
    print("\n=== TEST INTEGRACION ===")
    
    try:
        integration = BackupIntegration()
        print("Integracion creada")
        
        # Test configuración por defecto
        integration._create_default_config()
        print("Configuracion por defecto creada")
        
        config = integration.get_config()
        if config:
            print(f"Config cargada: {len(config)} parametros")
            print("OK - Integracion funciona")
            return True
        else:
            print("ERROR - No se pudo cargar config")
            return False
            
    except Exception as e:
        print(f"ERROR en integracion: {e}")
        return False


def cleanup_test_files():
    """Limpia archivos de prueba."""
    print("\n=== LIMPIEZA ===")
    
    try:
        # Limpiar directorio de backups test
        test_backups_dir = Path("test_backups")
        if test_backups_dir.exists():
            for file in test_backups_dir.glob("*"):
                file.unlink()
                print(f"Eliminado: {file.name}")
            test_backups_dir.rmdir()
            print("Directorio test_backups eliminado")
        
        # Limpiar configuración de prueba
        config_file = Path("backup_config.json")
        if config_file.exists():
            config_file.unlink()
            print("Config de prueba eliminada")
            
        print("OK - Limpieza completada")
        
    except Exception as e:
        print(f"WARNING - Error en limpieza: {e}")


def main():
    """Ejecuta todos los tests."""
    print("=== TEST SISTEMA BACKUP REXUS.APP ===")
    print("Version simple sin Unicode")
    print("="*50)
    
    demo_db_path = None
    tests_passed = 0
    total_tests = 4
    
    try:
        # Test 1: Configuración
        config = test_backup_config()
        tests_passed += 1
        
        # Test 2: Crear BD demo
        demo_db_path = test_create_demo_db()
        if demo_db_path:
            tests_passed += 1
        
        # Test 3: Backup manager
        if demo_db_path:
            if test_backup_manager(demo_db_path):
                tests_passed += 1
        
        # Test 4: Integración
        if test_backup_integration():
            tests_passed += 1
        
        # Resultados
        print(f"\n=== RESULTADOS ===")
        print(f"Tests pasados: {tests_passed}/{total_tests}")
        
        if tests_passed == total_tests:
            print("EXITO - Todos los tests pasaron!")
            print("El sistema de backup esta funcionando correctamente.")
        else:
            print("ATENCION - Algunos tests fallaron")
            print("Revisar implementacion del sistema de backup.")
        
        # Limpieza opcional
        print(f"\nLimpiar archivos de prueba? (y/N): ", end="")
        try:
            response = input().lower().strip()
            if response in ['y', 'yes', 's', 'si']:
                if demo_db_path and os.path.exists(demo_db_path):
                    os.unlink(demo_db_path)
                    print(f"BD demo eliminada: {demo_db_path}")
                cleanup_test_files()
            else:
                print("Archivos de prueba mantenidos para inspeccion")
        except (EOFError, KeyboardInterrupt):
            print("\nArchivos de prueba mantenidos")
    
    except KeyboardInterrupt:
        print("\n\nTest interrumpido por el usuario")
    except Exception as e:
        print(f"\nERROR GENERAL: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Limpieza de seguridad
        if demo_db_path and os.path.exists(demo_db_path):
            try:
                os.unlink(demo_db_path)
                print(f"BD demo eliminada: {demo_db_path}")
            except:
                pass
    
    print("\nTest completado.")


if __name__ == "__main__":
    main()