"""
Automated Backup and Recovery System for Rexus.app v2.0.0
Sistema automatizado de respaldo y recuperación

Funcionalidades:
- Backup automático de base de datos
- Backup de archivos de configuración
- Backup incremental y completo
- Recuperación automática en caso de fallos
- Verificación de integridad de backups
- Programación automática de backups
"""

import os
import shutil
import sqlite3
import zipfile
import hashlib
import threading
import schedule
import time
                        return True
            
        except Exception as e:
            logger.exception(f"SQL files restore failed: {e}")
            # FIXME: Specify concrete exception types instead of generic Exceptionreturn False


# Instancia global del gestor de backup
_backup_recovery_manager = None

def get_backup_recovery_manager() -> BackupRecoveryManager:
    """Obtiene la instancia global del gestor de backup y recovery"""
    global _backup_recovery_manager
    if _backup_recovery_manager is None:
        _backup_recovery_manager = BackupRecoveryManager()
    return _backup_recovery_manager

# Funciones de conveniencia
def create_emergency_backup() -> Optional[BackupInfo]:
    """Crea un backup de emergencia inmediato"""
    manager = get_backup_recovery_manager()
    logger.info("Creating emergency backup...")
    return manager.create_full_backup()

def restore_latest_backup(target_directory: str = None) -> bool:
    """Restaura desde el backup más reciente"""
    manager = get_backup_recovery_manager()
    last_backup = manager._get_last_successful_backup()
    if last_backup:
        logger.info(f"Restoring from latest backup: {last_backup.backup_id}")
        return manager.restore_from_backup(last_backup.backup_id, target_directory)
    else:
        logger.error("No successful backup found for restoration")
        return False

def start_automatic_backups():
    """Inicia el sistema de backup automático"""
    manager = get_backup_recovery_manager()
    manager.start_automated_backup()

def get_backup_health_report() -> Dict:
    """Obtiene reporte de salud del sistema de backup"""
    manager = get_backup_recovery_manager()
    status = manager.get_backup_status()
    
    # Agregar información de salud
    last_backup_age = None
    if status['last_backup']:
        last_backup_time = datetime.fromisoformat(status['last_backup']['timestamp'])
        last_backup_age = (datetime.now() - last_backup_time).days
    
    health_report = status.copy()
    health_report.update({
        'health_status': 'healthy' if status['success_rate'] > 90 else 'warning' if status['success_rate'] > 70 else 'critical',
        'last_backup_age_days': last_backup_age,
        'backup_age_status': 'recent' if last_backup_age and last_backup_age < 7 else 'old' if last_backup_age and last_backup_age < 30 else 'very_old'
    })
    
    return health_report