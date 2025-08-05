#!/usr/bin/env python3
"""
Demo del sistema de backup automatizado

Demuestra las funcionalidades principales del sistema de backup
sin requerir bases de datos reales.
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
from rexus.core.backup_integration import BackupIntegration, get_backup_info


def create_demo_databases():
    """Crea bases de datos de demostración para testing."""
    print("Creando bases de datos de demostracion...")
    
    # Crear directorio de datos demo
    data_dir = Path("demo_data")
    data_dir.mkdir(exist_ok=True)
    
    databases = {
        "users": {
            "path": data_dir / "users_demo.db",
            "schema": """
                CREATE TABLE usuarios (
                    id INTEGER PRIMARY KEY,
                    usuario TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    rol TEXT DEFAULT 'usuario',
                    nombre TEXT,
                    apellido TEXT,
                    email TEXT,
                    estado TEXT DEFAULT 'Activo',
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ultimo_login TIMESTAMP
                );
            """,
            "data": [
                ("admin", "hash123", "admin", "Admin", "Sistema", "admin@rexus.app", "Activo"),
                ("usuario1", "hash456", "usuario", "Juan", "Pérez", "juan@empresa.com", "Activo"),
                ("supervisor1", "hash789", "supervisor", "María", "García", "maria@empresa.com", "Activo")
            ]
        },
        "inventario": {
            "path": data_dir / "inventario_demo.db",
            "schema": """
                CREATE TABLE productos (
                    id INTEGER PRIMARY KEY,
                    codigo TEXT UNIQUE NOT NULL,
                    descripcion TEXT NOT NULL,
                    categoria TEXT,
                    stock_actual INTEGER DEFAULT 0,
                    stock_minimo INTEGER DEFAULT 0,
                    precio_unitario DECIMAL(10,2),
                    ubicacion TEXT,
                    proveedor TEXT,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE movimientos (
                    id INTEGER PRIMARY KEY,
                    producto_id INTEGER REFERENCES productos(id),
                    tipo_movimiento TEXT,
                    cantidad INTEGER,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    usuario TEXT,
                    observaciones TEXT
                );
            """,
            "data": [
                ("PROD-001", "Vidrio Templado 6mm", "Vidrios", 100, 10, 25.50, "Almacén A", "Proveedor XYZ"),
                ("HERR-001", "Bisagra Acero Inox", "Herrajes", 500, 50, 12.75, "Almacén B", "Herrajes SA"),
                ("SELL-001", "Sellador Silicona", "Selladores", 200, 20, 8.90, "Almacén C", "QuímicaCorp")
            ]
        },
        "auditoria": {
            "path": data_dir / "auditoria_demo.db",
            "schema": """
                CREATE TABLE auditoria_logs (
                    id INTEGER PRIMARY KEY,
                    usuario_id INTEGER,
                    accion TEXT NOT NULL,
                    modulo TEXT,
                    tabla_afectada TEXT,
                    registro_id INTEGER,
                    valores_anteriores TEXT,
                    valores_nuevos TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE security_events (
                    id INTEGER PRIMARY KEY,
                    usuario_id INTEGER,
                    evento TEXT NOT NULL,
                    nivel TEXT DEFAULT 'INFO',
                    detalles TEXT,
                    ip_address TEXT,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """,
            "data": [
                (1, "LOGIN", "USUARIOS", None, None, None, None, "192.168.1.100", "Rexus.app/2.0.0"),
                (1, "CREAR_PRODUCTO", "INVENTARIO", "productos", 1, None, '{"codigo":"PROD-001"}', "192.168.1.100", "Rexus.app/2.0.0"),
                (2, "CONSULTA_INVENTARIO", "INVENTARIO", None, None, None, None, "192.168.1.101", "Rexus.app/2.0.0")
            ]
        }
    }
    
    created_dbs = {}
    
    for db_name, db_info in databases.items():
        db_path = db_info["path"]
        
        try:
            # Crear base de datos
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Ejecutar schema
            cursor.executescript(db_info["schema"])
            
            # Insertar datos de demo
            if db_name == "users":
                cursor.executemany("""
                    INSERT INTO usuarios (usuario, password_hash, rol, nombre, apellido, email, estado)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, db_info["data"])
            elif db_name == "inventario":
                cursor.executemany("""
                    INSERT INTO productos (codigo, descripcion, categoria, stock_actual, stock_minimo, precio_unitario, ubicacion, proveedor)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, db_info["data"])
            elif db_name == "auditoria":
                cursor.executemany("""
                    INSERT INTO auditoria_logs (usuario_id, accion, modulo, tabla_afectada, registro_id, valores_anteriores, valores_nuevos, ip_address, user_agent)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, db_info["data"])
            
            conn.commit()
            conn.close()
            
            created_dbs[db_name] = str(db_path)
            print(f"✅ Base de datos {db_name} creada: {db_path}")
            
        except Exception as e:
            print(f"❌ Error creando base de datos {db_name}: {e}")
    
    return created_dbs


def demo_backup_configuration():
    """Demuestra la configuración del sistema de backup."""
    print("\n🔧 === CONFIGURACIÓN DEL SISTEMA DE BACKUP ===")
    
    # Crear configuración personalizada
    config = BackupConfig()
    config.backup_dir = "demo_backups"
    config.backup_schedule = "daily"
    config.backup_time = "03:00"
    config.retention_days = 15
    config.compress_backups = True
    
    print(f"📁 Directorio de backups: {config.backup_dir}")
    print(f"⏰ Horario: {config.backup_schedule} a las {config.backup_time}")
    print(f"🗂️ Retención: {config.retention_days} días")
    print(f"📦 Compresión: {'Sí' if config.compress_backups else 'No'}")
    print(f"💾 Bases de datos: {', '.join(config.backup_databases)}")
    
    return config


def demo_backup_operations(demo_dbs):
    """Demuestra operaciones de backup."""
    print("\n💾 === OPERACIONES DE BACKUP ===")
    
    # Configurar gestor con rutas demo
    config = BackupConfig()
    config.backup_dir = "demo_backups"
    
    manager = DatabaseBackupManager(config)
    
    # Sobrescribir método para usar bases de datos demo
    original_get_db_connections = manager.get_database_connections
    manager.get_database_connections = lambda: demo_dbs
    
    print("🔄 Realizando backup de bases de datos demo...")
    
    # Realizar backup de cada base de datos
    results = []
    for db_name, db_path in demo_dbs.items():
        print(f"\n📀 Backing up {db_name}...")
        result = manager.backup_single_database(db_name, db_path)
        results.append(result)
        
        if result.success:
            print(f"✅ Backup exitoso: {result.backup_path}")
            print(f"📊 Tamaño: {result.size_mb:.2f} MB")
            print(f"⏱️ Duración: {result.duration_seconds:.2f} segundos")
        else:
            print(f"❌ Error en backup: {result.message}")
    
    return results


def demo_backup_statistics(manager):
    """Demuestra estadísticas del sistema de backup."""
    print("\n📊 === ESTADÍSTICAS DE BACKUP ===")
    
    try:
        stats = manager.get_backup_statistics()
        
        print(f"📦 Total de backups: {stats['total_backups']}")
        print(f"💾 Tamaño total: {stats['total_size_mb']:.2f} MB")
        print(f"🗄️ Bases de datos respaldadas: {', '.join(stats['databases_backed_up'])}")
        
        if stats['newest_backup']:
            print(f"🆕 Backup más reciente: {stats['newest_backup']}")
        if stats['oldest_backup']:
            print(f"📅 Backup más antiguo: {stats['oldest_backup']}")
            
        print(f"📏 Tamaño promedio: {stats['average_size_mb']:.2f} MB")
        
        # Mostrar backups disponibles
        backups = manager.get_available_backups()
        if backups:
            print(f"\n📋 Backups disponibles ({len(backups)}):")
            for backup in backups[:5]:  # Mostrar solo los primeros 5
                print(f"  • {backup['database']} - {backup['timestamp']} ({backup['size_mb']:.2f} MB)")
    
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")


def demo_backup_integration():
    """Demuestra la integración del sistema de backup."""
    print("\n🔗 === INTEGRACIÓN DEL SISTEMA ===")
    
    try:
        # Obtener información del sistema global
        info = get_backup_info()
        
        print(f"🚀 Sistema en funcionamiento: {'Sí' if info['running'] else 'No'}")
        
        if info['next_backup']:
            print(f"⏰ Próximo backup: {info['next_backup']}")
        
        if info['statistics']:
            stats = info['statistics']
            print(f"📊 Estadísticas: {stats.get('total_backups', 0)} backups, {stats.get('total_size_mb', 0):.1f} MB")
        
        if info['config']:
            config = info['config']
            print(f"⚙️ Configuración: {config.get('backup_schedule', 'N/A')} a las {config.get('backup_time', 'N/A')}")
    
    except Exception as e:
        print(f"❌ Error en integración: {e}")


def cleanup_demo_files():
    """Limpia archivos de demostración."""
    print("\n🧹 === LIMPIEZA ===")
    
    try:
        # Limpiar bases de datos demo
        demo_data_dir = Path("demo_data")
        if demo_data_dir.exists():
            for file in demo_data_dir.glob("*.db"):
                file.unlink()
                print(f"🗑️ Eliminado: {file}")
            demo_data_dir.rmdir()
        
        # Limpiar backups demo
        demo_backups_dir = Path("demo_backups")
        if demo_backups_dir.exists():
            for file in demo_backups_dir.glob("*"):
                file.unlink()
                print(f"🗑️ Eliminado: {file}")
            demo_backups_dir.rmdir()
        
        print("✅ Limpieza completada")
        
    except Exception as e:
        print(f"⚠️ Error en limpieza: {e}")


def main():
    """Ejecuta la demostración completa del sistema de backup."""
    print("=== DEMO DEL SISTEMA DE BACKUP AUTOMATIZADO ===")
    print("Rexus.app - Sistema de Gestion Integral")
    print("=" * 60)
    
    try:
        # 1. Crear bases de datos de demostración
        demo_dbs = create_demo_databases()
        
        if not demo_dbs:
            print("❌ No se pudieron crear las bases de datos demo")
            return
        
        # 2. Mostrar configuración
        config = demo_backup_configuration()
        
        # 3. Realizar operaciones de backup
        manager = DatabaseBackupManager(config)
        
        # Sobrescribir método para usar DBs demo
        manager.get_database_connections = lambda: demo_dbs
        
        results = demo_backup_operations(demo_dbs)
        
        # 4. Mostrar estadísticas
        demo_backup_statistics(manager)
        
        # 5. Demostrar integración
        demo_backup_integration()
        
        # 6. Resumen final
        print(f"\n🎯 === RESUMEN ===")
        success_count = sum(1 for r in results if r.success)
        total_count = len(results)
        
        print(f"✅ Backups exitosos: {success_count}/{total_count}")
        
        if success_count == total_count:
            print("🎉 ¡Sistema de backup funcionando perfectamente!")
        else:
            print("⚠️ Algunos backups tuvieron problemas")
        
        # Preguntuar si limpiar archivos
        print(f"\n🤔 ¿Limpiar archivos de demostración? (y/N): ", end="")
        try:
            response = input().lower().strip()
            if response in ['y', 'yes', 's', 'si', 'sí']:
                cleanup_demo_files()
            else:
                print("📁 Archivos de demo mantenidos para inspección")
        except (EOFError, KeyboardInterrupt):
            print("\n📁 Archivos de demo mantenidos")
    
    except KeyboardInterrupt:
        print("\n\n⚠️ Demo interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error en demo: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n👋 Demo completada. ¡Gracias por usar Rexus.app!")


if __name__ == "__main__":
    main()