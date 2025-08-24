"""
Sistema de Backup Automatizado para Rexus
Versión: 2.0.0 - Enterprise Ready
"""

import os
import sys
import json
import gzip
import shutil
import logging
import schedule
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

# Sistema de logging
try:
    from ..utils.app_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# Configuración por defecto
BACKUP_CONFIG = {
    "retention_days": 30,
    "compression": True,
    "schedule": "daily",
    "backup_location": "backups/"
}

class BackupManager:
    """Gestor de backups automatizados."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Inicializa el gestor de backups."""
        self.config = config or BACKUP_CONFIG.copy()
        self.backup_dir = Path(self.config.get("backup_location", "backups/"))
        self.backup_dir.mkdir(exist_ok=True)
        
    def create_backup(self, source_path: str, backup_name: str = None) -> bool:
        """Crea un backup de la fuente especificada."""
        try:
            if not backup_name:
                backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            source = Path(source_path)
            if not source.exists():
                logger.error(f"Fuente no encontrada: {source_path}")
                return False
            
            backup_file = self.backup_dir / f"{backup_name}.tar.gz"
            
            # Crear backup comprimido
            shutil.make_archive(
                str(backup_file.with_suffix('')), 
                'gztar', 
                str(source.parent), 
                str(source.name)
            )
            
            logger.info(f"Backup creado exitosamente: {backup_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error creando backup: {e}")
            return False
    
    def cleanup_old_backups(self) -> int:
        """Limpia backups antiguos según configuración."""
        try:
            retention_days = self.config.get("retention_days", 30)
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            removed_count = 0
            for backup_file in self.backup_dir.glob("*.tar.gz"):
                if backup_file.stat().st_mtime < cutoff_date.timestamp():
                    backup_file.unlink()
                    removed_count += 1
                    logger.info(f"Backup antiguo eliminado: {backup_file.name}")
            
            return removed_count
            
        except Exception as e:
            logger.error(f"Error limpiando backups: {e}")
            return 0
    
    def get_backup_status(self) -> Dict[str, Any]:
        """Obtiene estado actual de los backups."""
        try:
            backups = list(self.backup_dir.glob("*.tar.gz"))
            total_size = sum(b.stat().st_size for b in backups)
            
            return {
                "total_backups": len(backups),
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "oldest_backup": min(b.stat().st_mtime for b in backups) if backups else None,
                "newest_backup": max(b.stat().st_mtime for b in backups) if backups else None,
                "backup_location": str(self.backup_dir)
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estado: {e}")
            return {}

# Instancia global
_backup_manager: Optional[BackupManager] = None

def get_backup_manager() -> BackupManager:
    """Obtiene la instancia global del gestor de backups."""
    global _backup_manager
    if _backup_manager is None:
        _backup_manager = BackupManager()
    return _backup_manager

def init_backup_manager(config: Dict[str, Any] = None) -> BackupManager:
    """Inicializa el gestor global de backups."""
    global _backup_manager
    _backup_manager = BackupManager(config)
    return _backup_manager
