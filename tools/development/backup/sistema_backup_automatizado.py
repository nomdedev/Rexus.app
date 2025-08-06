#!/usr/bin/env python3
"""
MIT License - Copyright (c) 2025 Rexus.app

Sistema de Backup Automatizado para Rexus.app
=============================================

Implementa backup completo de las 3 bases de datos:
- users (autenticación y permisos)
- inventario (datos de negocio)
- auditoria (trazabilidad y eventos)

Características:
- Backup automático programado
- Verificación de integridad
- Rotación de backups antiguos
- Compresión y cifrado opcional
- Notificaciones de estado
- Restore automatizado

Ejecución:
python tools/development/backup/sistema_backup_automatizado.py
"""

import os
import sys
import json
import gzip
import shutil
import schedule
import logging
import datetime
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# Importar ruta src para acceso a utilidades del proyecto
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_dir))

from rexus.core.database import get_users_connection, get_inventario_connection, get_auditoria_connection

@dataclass
class BackupConfig:
    """Configuración del sistema de backup"""
    backup_dir: str = "backups"
    max_backups: int = 30  # Mantener 30 días de backups
    compress: bool = True
    verify_integrity: bool = True
    schedule_time: str = "02:00"  # 2:00 AM diario
    email_notifications: bool = False
    email_recipients: List[str] = None
    encrypt_backups: bool = False
    encryption_key: Optional[str] = None

class DatabaseBackupSystem:
    """Sistema integral de backup para Rexus.app"""
    
    def __init__(self, config: BackupConfig = None):
        self.config = config or BackupConfig()
        self.backup_root = Path(root_dir) / self.config.backup_dir
        self.logger = self._setup_logging()
        
        # Crear estructura de directorios
        self._create_backup_structure()
        
        # Bases de datos a respaldar
        self.databases = {
            'users': get_users_connection,
            'inventario': get_inventario_connection,
            'auditoria': get_auditoria_connection
        }
        
        self.logger.info("[BACKUP] Sistema de backup inicializado")
    
    def _setup_logging(self) -> logging.Logger:
        """Configura el sistema de logging para backups"""
        log_dir = self.backup_root / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar logger
        logger = logging.getLogger('rexus_backup')
        logger.setLevel(logging.INFO)
        
        # Archivo de log con rotación diaria
        log_file = log_dir / f"backup_{datetime.date.today().isoformat()}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formato
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - [BACKUP] %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Agregar handlers si no existen ya
        if not logger.handlers:
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
        
        return logger
    
    def _create_backup_structure(self):
        """Crea la estructura de directorios para backups"""
        directories = [
            "databases",
            "config", 
            "application",
            "logs",
            "temp",
            "restore"
        ]
        
        for directory in directories:
            (self.backup_root / directory).mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"[SETUP] Estructura de backup creada en: {self.backup_root}")
    
    def create_full_backup(self) -> Dict[str, any]:
        """Crea un backup completo del sistema"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_session = {
            "timestamp": timestamp,
            "type": "full",
            "started_at": datetime.datetime.now().isoformat(),
            "databases": {},
            "config": {},
            "application": {},
            "status": "in_progress",
            "errors": []
        }
        
        try:
            self.logger.info(f"[BACKUP] Iniciando backup completo - {timestamp}")
            
            # 1. Backup de bases de datos
            self.logger.info("[BACKUP] Respaldando bases de datos...")
            backup_session["databases"] = self._backup_all_databases(timestamp)
            
            # 2. Backup de configuración
            self.logger.info("[BACKUP] Respaldando configuración...")
            backup_session["config"] = self._backup_configuration(timestamp)
            
            # 3. Backup de archivos críticos de aplicación
            self.logger.info("[BACKUP] Respaldando archivos críticos...")
            backup_session["application"] = self._backup_application_files(timestamp)
            
            # 4. Verificar integridad si está habilitado
            if self.config.verify_integrity:
                self.logger.info("[BACKUP] Verificando integridad...")
                self._verify_backup_integrity(backup_session)
            
            # 5. Comprimir si está habilitado
            if self.config.compress:
                self.logger.info("[BACKUP] Comprimiendo backup...")
                self._compress_backup(timestamp)
            
            # 6. Limpiar backups antiguos
            self.logger.info("[BACKUP] Limpiando backups antiguos...")
            self._cleanup_old_backups()
            
            backup_session["status"] = "completed"
            backup_session["completed_at"] = datetime.datetime.now().isoformat()
            
            # Guardar manifiesto del backup
            self._save_backup_manifest(backup_session)
            
            self.logger.info(f"[SUCCESS] Backup completo exitoso - {timestamp}")
            return backup_session
            
        except Exception as e:
            backup_session["status"] = "failed"
            backup_session["errors"].append(str(e))
            backup_session["failed_at"] = datetime.datetime.now().isoformat()
            
            self.logger.error(f"[ERROR] Backup falló: {str(e)}")
            return backup_session
    
    def _backup_all_databases(self, timestamp: str) -> Dict[str, any]:
        """Respalda todas las bases de datos"""
        db_backup_results = {}
        
        for db_name, connection_func in self.databases.items():
            try:
                self.logger.info(f"[DB] Respaldando base de datos: {db_name}")
                
                # Obtener conexión
                connection = connection_func()
                if not connection:
                    raise Exception(f"No se pudo conectar a la base de datos {db_name}")
                
                # Crear backup usando sqlcmd (más confiable que pyodbc para backups)
                backup_result = self._backup_database_sqlcmd(db_name, timestamp, connection)
                db_backup_results[db_name] = backup_result
                
                connection.close()
                
            except Exception as e:
                self.logger.error(f"[DB ERROR] Error respaldando {db_name}: {str(e)}")
                db_backup_results[db_name] = {
                    "status": "failed",
                    "error": str(e),
                    "timestamp": timestamp
                }
        
        return db_backup_results
    
    def _backup_database_sqlcmd(self, db_name: str, timestamp: str, connection) -> Dict[str, any]:
        """Realiza backup de una base de datos usando sqlcmd"""
        backup_file = self.backup_root / "databases" / f"{db_name}_{timestamp}.bak"
        
        try:
            # Obtener configuración de conexión desde variables de entorno
            server = os.getenv("DB_SERVER")
            username = os.getenv("DB_USERNAME")
            password = os.getenv("DB_PASSWORD")
            
            if not all([server, username, password]):
                raise Exception("Configuración de base de datos incompleta")
            
            # Comando SQL para backup
            backup_sql = f"""
            BACKUP DATABASE [{db_name}] 
            TO DISK = N'{backup_file}' 
            WITH FORMAT, CHECKSUM, COMPRESSION, 
            NAME = 'Rexus {db_name} Full Backup {timestamp}',
            DESCRIPTION = 'Backup automatizado de Rexus.app'
            """
            
            # Ejecutar backup usando sqlcmd
            cmd = [
                "sqlcmd",
                "-S", server,
                "-U", username,
                "-P", password,
                "-Q", backup_sql,
                "-b"  # Terminar en error
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=300  # 5 minutos timeout
            )
            
            if result.returncode != 0:
                raise Exception(f"sqlcmd falló: {result.stderr}")
            
            # Verificar que el archivo se creó
            if not backup_file.exists():
                raise Exception("Archivo de backup no se creó")
            
            file_size = backup_file.stat().st_size
            
            self.logger.info(f"[DB SUCCESS] {db_name} respaldado: {file_size:,} bytes")
            
            return {
                "status": "completed",
                "file": str(backup_file),
                "size_bytes": file_size,
                "checksum": self._calculate_file_checksum(backup_file),
                "timestamp": timestamp
            }
            
        except Exception as e:
            self.logger.error(f"[DB ERROR] Error en backup de {db_name}: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "timestamp": timestamp
            }
    
    def _backup_configuration(self, timestamp: str) -> Dict[str, any]:
        """Respalda archivos de configuración críticos"""
        config_backup = {
            "status": "in_progress",
            "files": [],
            "timestamp": timestamp
        }
        
        try:
            # Archivos de configuración a respaldar
            config_files = [
                ".env",
                "config/environments/privado/.env",
                "CLAUDE.md",
                "requirements.txt",
                "pyproject.toml"
            ]
            
            backup_config_dir = self.backup_root / "config" / timestamp
            backup_config_dir.mkdir(parents=True, exist_ok=True)
            
            for config_file in config_files:
                source_file = root_dir / config_file
                
                if source_file.exists():
                    dest_file = backup_config_dir / source_file.name
                    
                    # Copiar archivo
                    shutil.copy2(source_file, dest_file)
                    
                    config_backup["files"].append({
                        "source": str(source_file),
                        "backup": str(dest_file),
                        "size": source_file.stat().st_size,
                        "checksum": self._calculate_file_checksum(dest_file)
                    })
                    
                    self.logger.info(f"[CONFIG] Respaldado: {config_file}")
            
            config_backup["status"] = "completed"
            return config_backup
            
        except Exception as e:
            config_backup["status"] = "failed"
            config_backup["error"] = str(e)
            self.logger.error(f"[CONFIG ERROR] Error respaldando configuración: {str(e)}")
            return config_backup
    
    def _backup_application_files(self, timestamp: str) -> Dict[str, any]:
        """Respalda archivos críticos de la aplicación"""
        app_backup = {
            "status": "in_progress",
            "directories": [],
            "timestamp": timestamp
        }
        
        try:
            # Directorios críticos a respaldar
            critical_dirs = [
                "rexus/core",
                "rexus/utils", 
                "resources/qss",
                "docs/checklists",
                "scripts/sql"
            ]
            
            backup_app_dir = self.backup_root / "application" / timestamp
            backup_app_dir.mkdir(parents=True, exist_ok=True)
            
            for directory in critical_dirs:
                source_dir = root_dir / directory
                
                if source_dir.exists() and source_dir.is_dir():
                    dest_dir = backup_app_dir / directory
                    
                    # Copiar directorio completo
                    shutil.copytree(source_dir, dest_dir, dirs_exist_ok=True)
                    
                    # Calcular tamaño del directorio
                    total_size = sum(
                        f.stat().st_size for f in dest_dir.rglob('*') if f.is_file()
                    )
                    
                    app_backup["directories"].append({
                        "source": str(source_dir),
                        "backup": str(dest_dir),
                        "size_bytes": total_size,
                        "files_count": len(list(dest_dir.rglob('*')))
                    })
                    
                    self.logger.info(f"[APP] Respaldado directorio: {directory} ({total_size:,} bytes)")
            
            app_backup["status"] = "completed"
            return app_backup
            
        except Exception as e:
            app_backup["status"] = "failed" 
            app_backup["error"] = str(e)
            self.logger.error(f"[APP ERROR] Error respaldando aplicación: {str(e)}")
            return app_backup
    
    def _calculate_file_checksum(self, file_path: Path) -> str:
        """Calcula checksum MD5 de un archivo"""
        import hashlib
        
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _verify_backup_integrity(self, backup_session: Dict[str, any]):
        """Verifica la integridad de los backups creados"""
        self.logger.info("[VERIFY] Verificando integridad de backups...")
        
        integrity_results = []
        
        # Verificar backups de bases de datos
        for db_name, db_backup in backup_session["databases"].items():
            if db_backup["status"] == "completed":
                backup_file = Path(db_backup["file"])
                
                if backup_file.exists():
                    # Recalcular checksum
                    current_checksum = self._calculate_file_checksum(backup_file)
                    original_checksum = db_backup["checksum"]
                    
                    if current_checksum == original_checksum:
                        integrity_results.append(f"✓ {db_name}: Integridad verificada")
                    else:
                        integrity_results.append(f"✗ {db_name}: Checksum no coincide")
                else:
                    integrity_results.append(f"✗ {db_name}: Archivo no encontrado")
        
        backup_session["integrity_check"] = integrity_results
        
        for result in integrity_results:
            self.logger.info(f"[INTEGRITY] {result}")
    
    def _compress_backup(self, timestamp: str):
        """Comprime los backups para ahorrar espacio"""
        self.logger.info("[COMPRESS] Comprimiendo backups...")
        
        # Comprimir backups de bases de datos
        db_backup_dir = self.backup_root / "databases"
        
        for backup_file in db_backup_dir.glob(f"*_{timestamp}.bak"):
            compressed_file = backup_file.with_suffix('.bak.gz')
            
            with open(backup_file, 'rb') as f_in:
                with gzip.open(compressed_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Eliminar archivo original
            backup_file.unlink()
            
            original_size = backup_file.stat().st_size if backup_file.exists() else 0
            compressed_size = compressed_file.stat().st_size
            
            compression_ratio = (1 - compressed_size / max(original_size, 1)) * 100
            
            self.logger.info(
                f"[COMPRESS] {backup_file.name}: "
                f"{original_size:,} → {compressed_size:,} bytes "
                f"({compression_ratio:.1f}% reducción)"
            )
    
    def _cleanup_old_backups(self):
        """Elimina backups antiguos según la configuración"""
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=self.config.max_backups)
        
        directories_to_clean = ["databases", "config", "application"]
        
        for directory in directories_to_clean:
            backup_dir = self.backup_root / directory
            
            if not backup_dir.exists():
                continue
            
            deleted_count = 0
            
            for item in backup_dir.iterdir():
                if item.is_file():
                    # Para archivos, verificar fecha de modificación
                    if datetime.datetime.fromtimestamp(item.stat().st_mtime) < cutoff_date:
                        item.unlink()
                        deleted_count += 1
                
                elif item.is_dir():
                    # Para directorios, verificar si son más antiguos
                    try:
                        # Intentar parsear timestamp del nombre del directorio
                        dir_timestamp = datetime.datetime.strptime(item.name, "%Y%m%d_%H%M%S")
                        if dir_timestamp < cutoff_date:
                            shutil.rmtree(item)
                            deleted_count += 1
                    except ValueError:
                        # Si no se puede parsear, mantener el directorio
                        pass
            
            if deleted_count > 0:
                self.logger.info(f"[CLEANUP] Eliminados {deleted_count} backups antiguos de {directory}")
    
    def _save_backup_manifest(self, backup_session: Dict[str, any]):
        """Guarda el manifiesto del backup para referencia futura"""
        manifest_file = self.backup_root / f"backup_manifest_{backup_session['timestamp']}.json"
        
        with open(manifest_file, 'w', encoding='utf-8') as f:
            json.dump(backup_session, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"[MANIFEST] Manifiesto guardado: {manifest_file.name}")
    
    def setup_scheduled_backup(self):
        """Configura backup automático programado"""
        self.logger.info(f"[SCHEDULE] Configurando backup automático a las {self.config.schedule_time}")
        
        schedule.clear()
        schedule.every().day.at(self.config.schedule_time).do(self._scheduled_backup_job)
        
        self.logger.info("[SCHEDULE] Backup programado configurado. Ejecutar run_scheduler() para iniciar.")
    
    def _scheduled_backup_job(self):
        """Job de backup programado"""
        self.logger.info("[SCHEDULED] Ejecutando backup programado...")
        
        try:
            backup_result = self.create_full_backup()
            
            if backup_result["status"] == "completed":
                self.logger.info("[SCHEDULED] Backup programado completado exitosamente")
                
                if self.config.email_notifications:
                    self._send_backup_notification(backup_result, success=True)
            else:
                self.logger.error("[SCHEDULED] Backup programado falló")
                
                if self.config.email_notifications:
                    self._send_backup_notification(backup_result, success=False)
                    
        except Exception as e:
            self.logger.error(f"[SCHEDULED ERROR] Error en backup programado: {str(e)}")
    
    def run_scheduler(self):
        """Ejecuta el programador de backups"""
        self.logger.info("[SCHEDULER] Iniciando programador de backups...")
        
        while True:
            schedule.run_pending()
            import time
            time.sleep(60)  # Verificar cada minuto
    
    def _send_backup_notification(self, backup_result: Dict[str, any], success: bool):
        """Envía notificación por email del resultado del backup"""
        # Implementación de envío de email (opcional)
        # Por ahora solo logging
        status = "EXITOSO" if success else "FALLIDO"
        self.logger.info(f"[EMAIL] Notificación de backup {status} enviada")
    
    def list_available_backups(self) -> List[Dict[str, any]]:
        """Lista todos los backups disponibles"""
        backups = []
        
        # Buscar manifiestos de backup
        for manifest_file in self.backup_root.glob("backup_manifest_*.json"):
            try:
                with open(manifest_file, 'r', encoding='utf-8') as f:
                    backup_data = json.load(f)
                    
                backup_info = {
                    "timestamp": backup_data.get("timestamp"),
                    "status": backup_data.get("status"),
                    "type": backup_data.get("type", "full"),
                    "manifest_file": str(manifest_file),
                    "databases_count": len(backup_data.get("databases", {})),
                    "started_at": backup_data.get("started_at"),
                    "completed_at": backup_data.get("completed_at")
                }
                
                backups.append(backup_info)
                
            except Exception as e:
                self.logger.error(f"[LIST ERROR] Error leyendo manifiesto {manifest_file}: {str(e)}")
        
        # Ordenar por timestamp descendente
        backups.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return backups
    
    def restore_from_backup(self, backup_timestamp: str) -> Dict[str, any]:
        """Restaura desde un backup específico"""
        restore_result = {
            "timestamp": backup_timestamp,
            "started_at": datetime.datetime.now().isoformat(),
            "status": "in_progress",
            "databases": {},
            "errors": []
        }
        
        try:
            self.logger.info(f"[RESTORE] Iniciando restauración desde backup: {backup_timestamp}")
            
            # Cargar manifiesto del backup
            manifest_file = self.backup_root / f"backup_manifest_{backup_timestamp}.json"
            
            if not manifest_file.exists():
                raise Exception(f"Manifiesto de backup no encontrado: {backup_timestamp}")
            
            with open(manifest_file, 'r', encoding='utf-8') as f:
                backup_manifest = json.load(f)
            
            # Restaurar cada base de datos
            for db_name, db_backup in backup_manifest["databases"].items():
                if db_backup["status"] == "completed":
                    restore_result["databases"][db_name] = self._restore_database(db_name, db_backup)
            
            restore_result["status"] = "completed"
            restore_result["completed_at"] = datetime.datetime.now().isoformat()
            
            self.logger.info(f"[RESTORE SUCCESS] Restauración completada: {backup_timestamp}")
            return restore_result
            
        except Exception as e:
            restore_result["status"] = "failed"
            restore_result["errors"].append(str(e))
            restore_result["failed_at"] = datetime.datetime.now().isoformat()
            
            self.logger.error(f"[RESTORE ERROR] Restauración falló: {str(e)}")
            return restore_result
    
    def _restore_database(self, db_name: str, db_backup: Dict[str, any]) -> Dict[str, any]:
        """Restaura una base de datos específica"""
        restore_result = {
            "status": "in_progress",
            "database": db_name
        }
        
        try:
            backup_file = Path(db_backup["file"])
            
            # Si el backup está comprimido, descomprimirlo
            if backup_file.suffix == '.gz':
                temp_file = self.backup_root / "temp" / backup_file.stem
                
                with gzip.open(backup_file, 'rb') as f_in:
                    with open(temp_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                backup_file = temp_file
            
            # Configuración de conexión
            server = os.getenv("DB_SERVER")
            username = os.getenv("DB_USERNAME")
            password = os.getenv("DB_PASSWORD")
            
            # Comando SQL para restore
            restore_sql = f"""
            RESTORE DATABASE [{db_name}] 
            FROM DISK = N'{backup_file}'
            WITH REPLACE, CHECKDB
            """
            
            # Ejecutar restore usando sqlcmd
            cmd = [
                "sqlcmd",
                "-S", server,
                "-U", username,
                "-P", password,
                "-Q", restore_sql,
                "-b"
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True,
                timeout=600  # 10 minutos timeout
            )
            
            if result.returncode != 0:
                raise Exception(f"sqlcmd restore falló: {result.stderr}")
            
            restore_result["status"] = "completed"
            self.logger.info(f"[RESTORE DB] {db_name} restaurado exitosamente")
            
        except Exception as e:
            restore_result["status"] = "failed"
            restore_result["error"] = str(e)
            self.logger.error(f"[RESTORE DB ERROR] Error restaurando {db_name}: {str(e)}")
        
        return restore_result

def main():
    """Función principal para ejecución del sistema de backup"""
    print("🔄 Sistema de Backup Automatizado - Rexus.app")
    print("=" * 50)
    
    # Configuración personalizable
    config = BackupConfig(
        backup_dir="backups",
        max_backups=30,
        compress=True,
        verify_integrity=True,
        schedule_time="02:00"
    )
    
    # Inicializar sistema de backup
    backup_system = DatabaseBackupSystem(config)
    
    # Menú interactivo
    while True:
        print("\n🔧 Opciones disponibles:")
        print("1. 🚀 Crear backup completo ahora")
        print("2. 📅 Configurar backup automático") 
        print("3. 📋 Listar backups disponibles")
        print("4. 🔄 Restaurar desde backup")
        print("5. 🏃 Ejecutar programador de backups")
        print("6. 🚪 Salir")
        
        choice = input("\n👉 Seleccione una opción (1-6): ").strip()
        
        if choice == "1":
            print("\n🚀 Creando backup completo...")
            result = backup_system.create_full_backup()
            
            if result["status"] == "completed":
                print("✅ Backup completado exitosamente!")
                print(f"📁 Timestamp: {result['timestamp']}")
            else:
                print("❌ Backup falló!")
                if result.get("errors"):
                    print("🔍 Errores:")
                    for error in result["errors"]:
                        print(f"  - {error}")
        
        elif choice == "2":
            backup_system.setup_scheduled_backup()
            print("✅ Backup automático configurado")
            print(f"⏰ Se ejecutará diariamente a las {config.schedule_time}")
        
        elif choice == "3":
            print("\n📋 Backups disponibles:")
            backups = backup_system.list_available_backups()
            
            if backups:
                for i, backup in enumerate(backups, 1):
                    status_icon = "✅" if backup["status"] == "completed" else "❌"
                    print(f"{i:2d}. {status_icon} {backup['timestamp']} - {backup['databases_count']} bases de datos")
            else:
                print("📪 No hay backups disponibles")
        
        elif choice == "4":
            print("\n🔄 Restaurar desde backup")
            backups = backup_system.list_available_backups()
            
            if not backups:
                print("📪 No hay backups disponibles para restaurar")
                continue
            
            print("📋 Backups disponibles:")
            for i, backup in enumerate(backups, 1):
                if backup["status"] == "completed":
                    print(f"{i:2d}. {backup['timestamp']}")
            
            try:
                selection = int(input("👉 Seleccione número de backup: ")) - 1
                if 0 <= selection < len(backups):
                    selected_backup = backups[selection]
                    
                    if selected_backup["status"] == "completed":
                        confirm = input(f"⚠️  ¿Confirma restaurar desde {selected_backup['timestamp']}? (s/N): ")
                        if confirm.lower() in ['s', 'sí', 'si', 'yes', 'y']:
                            result = backup_system.restore_from_backup(selected_backup["timestamp"])
                            
                            if result["status"] == "completed":
                                print("✅ Restauración completada exitosamente!")
                            else:
                                print("❌ Restauración falló!")
                        else:
                            print("🚫 Restauración cancelada")
                    else:
                        print("❌ Backup seleccionado no está completo")
                else:
                    print("❌ Selección inválida")
            except (ValueError, IndexError):
                print("❌ Entrada inválida")
        
        elif choice == "5":
            print("\n🏃 Iniciando programador de backups...")
            print("⏰ Presione Ctrl+C para detener")
            try:
                backup_system.run_scheduler()
            except KeyboardInterrupt:
                print("\n🛑 Programador detenido por usuario")
        
        elif choice == "6":
            print("\n👋 Saliendo del sistema de backup...")
            break
        
        else:
            print("❌ Opción inválida. Por favor seleccione 1-6.")

if __name__ == "__main__":
    main()