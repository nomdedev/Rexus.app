"""
Integración del Sistema de Backup con la aplicación principal

Proporciona una interfaz simple para integrar el sistema de backup
con los módulos principales de Rexus.app
"""

import os
import json
from datetime import datetime
from typing import Optional, Dict, List
from pathlib import Path

from rexus.utils.backup_system import (
    DatabaseBackupManager, 
    AutomatedBackupScheduler, 
    BackupConfig,
    BackupResult
)


class BackupIntegration:
    """Integración del sistema de backup con la aplicación principal."""
    
    def __init__(self):
        self.config_path = "config/backup_config.json"
        self.backup_manager: Optional[DatabaseBackupManager] = None
        self.scheduler: Optional[AutomatedBackupScheduler] = None
        self.initialized = False
    
    def initialize(self) -> bool:
        """
        Inicializa el sistema de backup.
        
        Returns:
            True si se inicializó correctamente, False si hubo error
        """
        try:
            # Crear directorio de configuración si no existe
            config_dir = Path(self.config_path).parent
            config_dir.mkdir(parents=True, exist_ok=True)
            
            # Cargar o crear configuración
            if not os.path.exists(self.config_path):
                self._create_default_config()
            
            config = BackupConfig.from_file(self.config_path)
            
            # Crear componentes del sistema
            self.backup_manager = DatabaseBackupManager(config)
            self.scheduler = AutomatedBackupScheduler(self.backup_manager, config)
            
            # Iniciar programador automático
            self.scheduler.start_scheduler()
            
            self.initialized = True
            print("[CHECK] Sistema de backup inicializado correctamente")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error inicializando sistema de backup: {e}")
            return False
    
    def _create_default_config(self):
        """Crea un archivo de configuración por defecto."""
        config = BackupConfig()
        
        # Configuración personalizada para Rexus.app
        config.backup_dir = "backups"
        config.backup_schedule = "daily"
        config.backup_time = "02:00"
        config.retention_days = 30
        config.compress_backups = True
        config.backup_databases = ["users", "inventario", "auditoria"]
        config.notification_enabled = True
        config.auto_cleanup = True
        
        config.save_to_file(self.config_path)
        print(f"Configuracion de backup por defecto creada: {self.config_path}")
    
    def backup_now(self) -> List[BackupResult]:
        """
        Realiza un backup inmediato de todas las bases de datos.
        
        Returns:
            Lista de resultados de backup
        """
        if not self.initialized or not self.backup_manager:
            print("[ERROR] Sistema de backup no inicializado")
            return []
        
        print("🔄 Iniciando backup manual...")
        results = self.backup_manager.backup_all_databases()
        
        # Mostrar resultados
        success_count = sum(1 for r in results if r.success)
        total_count = len(results)
        
        if success_count == total_count:
            print(f"[CHECK] Backup completado exitosamente: {success_count}/{total_count} bases de datos")
        else:
            print(f"[WARN] Backup completado con errores: {success_count}/{total_count} bases de datos")
        
        return results
    
    def backup_single_database(self, database_name: str) -> Optional[BackupResult]:
        """
        Realiza backup de una base de datos específica.
        
        Args:
            database_name: Nombre de la base de datos (users, inventario, auditoria)
            
        Returns:
            Resultado del backup o None si hay error
        """
        if not self.initialized or not self.backup_manager:
            print("[ERROR] Sistema de backup no inicializado")
            return None
        
        db_connections = self.backup_manager.get_database_connections()
        
        if database_name not in db_connections:
            print(f"[ERROR] Base de datos no encontrada: {database_name}")
            return None
        
        db_path = db_connections[database_name]
        print(f"🔄 Realizando backup de {database_name}...")
        
        result = self.backup_manager.backup_single_database(database_name, db_path)
        
        if result.success:
            print(f"[CHECK] Backup de {database_name} completado: {result.backup_path}")
        else:
            print(f"[ERROR] Error en backup de {database_name}: {result.message}")
        
        return result
    
    def get_backup_history(self) -> List[Dict]:
        """
        Obtiene el historial de backups disponibles.
        
        Returns:
            Lista de backups disponibles con su información
        """
        if not self.initialized or not self.backup_manager:
            return []
        
        return self.backup_manager.get_available_backups()
    
    def get_statistics(self) -> Dict:
        """
        Obtiene estadísticas del sistema de backup.
        
        Returns:
            Diccionario con estadísticas
        """
        if not self.initialized or not self.backup_manager:
            return {}
        
        return self.backup_manager.get_backup_statistics()
    
    def restore_database(self, backup_path: str, database_name: str) -> bool:
        """
        Restaura una base de datos desde un backup.
        
        Args:
            backup_path: Ruta al archivo de backup
            database_name: Nombre de la base de datos a restaurar
            
        Returns:
            True si se restauró correctamente, False si hubo error
        """
        if not self.initialized or not self.backup_manager:
            print("[ERROR] Sistema de backup no inicializado")
            return False
        
        db_connections = self.backup_manager.get_database_connections()
        
        if database_name not in db_connections:
            print(f"[ERROR] Base de datos no encontrada: {database_name}")
            return False
        
        target_path = db_connections[database_name]
        print(f"🔄 Restaurando {database_name} desde {backup_path}...")
        
        success = self.backup_manager.restore_database(backup_path, target_path)
        
        if success:
            print(f"[CHECK] Base de datos {database_name} restaurada correctamente")
        else:
            print(f"[ERROR] Error restaurando base de datos {database_name}")
        
        return success
    
    def cleanup_old_backups(self):
        """Limpia backups antiguos según la política de retención."""
        if not self.initialized or not self.backup_manager:
            print("[ERROR] Sistema de backup no inicializado")
            return
        
        print("🧹 Ejecutando limpieza de backups antiguos...")
        self.backup_manager.cleanup_old_backups()
        print("[CHECK] Limpieza completada")
    
    def update_config(self, **kwargs):
        """
        Actualiza la configuración del sistema de backup.
        
        Args:
            **kwargs: Parámetros de configuración a actualizar
        """
        if not os.path.exists(self.config_path):
            self._create_default_config()
        
        try:
            config = BackupConfig.from_file(self.config_path)
            
            # Actualizar parámetros proporcionados
            for key, value in kwargs.items():
                if hasattr(config, key):
                    setattr(config, key, value)
                    print(f"[NOTE] Configuración actualizada: {key} = {value}")
            
            # Guardar configuración
            config.save_to_file(self.config_path)
            
            # Reinicializar si ya estaba inicializado
            if self.initialized:
                self.shutdown()
                self.initialize()
                print("🔄 Sistema de backup reinicializado con nueva configuración")
            
        except Exception as e:
            print(f"[ERROR] Error actualizando configuración: {e}")
    
    def get_config(self) -> Dict:
        """
        Obtiene la configuración actual del sistema.
        
        Returns:
            Diccionario con la configuración actual
        """
        if not os.path.exists(self.config_path):
            return {}
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] Error leyendo configuración: {e}")
            return {}
    
    def shutdown(self):
        """Detiene el sistema de backup."""
        if self.scheduler:
            self.scheduler.stop_scheduler()
        
        self.backup_manager = None
        self.scheduler = None
        self.initialized = False
        print("⏹️ Sistema de backup detenido")
    
    def is_running(self) -> bool:
        """
        Verifica si el sistema de backup está funcionando.
        
        Returns:
            True si está funcionando, False si no
        """
        return self.initialized and self.backup_manager is not None
    
    def get_next_scheduled_backup(self) -> Optional[str]:
        """
        Obtiene información del próximo backup programado.
        
        Returns:
            String con información del próximo backup o None
        """
        if not self.initialized:
            return None
        
        config = self.get_config()
        schedule_type = config.get('backup_schedule', 'daily')
        backup_time = config.get('backup_time', '02:00')
        
        if schedule_type == 'daily':
            return f"Diariamente a las {backup_time}"
        elif schedule_type == 'weekly':
            return f"Semanalmente los lunes a las {backup_time}"
        elif schedule_type == 'monthly':
            return f"Mensualmente a las {backup_time}"
        
        return None


# Instancia global del sistema de backup
_backup_integration = None


def get_backup_system() -> BackupIntegration:
    """
    Obtiene la instancia global del sistema de backup.
    
    Returns:
        Instancia de BackupIntegration
    """
    global _backup_integration
    if _backup_integration is None:
        _backup_integration = BackupIntegration()
    return _backup_integration


def initialize_backup_system() -> bool:
    """
    Inicializa el sistema de backup global.
    
    Returns:
        True si se inicializó correctamente, False si hubo error
    """
    backup_system = get_backup_system()
    return backup_system.initialize()


def backup_now() -> List[BackupResult]:
    """
    Realiza un backup inmediato usando el sistema global.
    
    Returns:
        Lista de resultados de backup
    """
    backup_system = get_backup_system()
    return backup_system.backup_now()


def get_backup_info() -> Dict:
    """
    Obtiene información del sistema de backup global.
    
    Returns:
        Diccionario con información del sistema
    """
    backup_system = get_backup_system()
    
    return {
        'running': backup_system.is_running(),
        'next_backup': backup_system.get_next_scheduled_backup(),
        'statistics': backup_system.get_statistics(),
        'config': backup_system.get_config()
    }


# Funciones de conveniencia para integración con módulos

def backup_before_critical_operation(operation_name: str = "operación crítica") -> bool:
    """
    Realiza un backup de seguridad antes de una operación crítica.
    
    Args:
        operation_name: Nombre de la operación para logging
        
    Returns:
        True si el backup fue exitoso, False si no
    """
    print(f"[SHIELD] Realizando backup de seguridad antes de {operation_name}...")
    
    backup_system = get_backup_system()
    if not backup_system.is_running():
        if not backup_system.initialize():
            print("[ERROR] No se pudo inicializar el sistema de backup")
            return False
    
    results = backup_system.backup_now()
    success_count = sum(1 for r in results if r.success)
    
    if success_count == len(results):
        print(f"[CHECK] Backup de seguridad completado antes de {operation_name}")
        return True
    else:
        print(f"[WARN] Backup de seguridad completado con errores antes de {operation_name}")
        return False


def schedule_backup_after_maintenance() -> bool:
    """
    Programa un backup después de operaciones de mantenimiento.
    
    Returns:
        True si se programó correctamente, False si no
    """
    backup_system = get_backup_system()
    if not backup_system.is_running():
        return backup_system.initialize()
    
    # El backup se ejecutará en el próximo horario programado
    print("📅 Backup programado para después del mantenimiento")
    return True