#!/usr/bin/env python3
"""
Sistema de Compresión de Backups para Rexus
Optimiza el almacenamiento de backups y logs
"""

import gzip
import shutil
import os
import json
import time
from pathlib import Path
from typing import List, Dict

class BackupCompressor:
    """Compresor de backups y archivos de log"""
    
    def __init__(self, backup_dir: str = "backups", compression_level: int = 6):
        self.backup_dir = Path(backup_dir)
        self.compression_level = compression_level
        self.backup_dir.mkdir(exist_ok=True)
    
    def compress_file(self, source_path: str, compressed_path: str = None) -> str:
        """Comprime un archivo individual"""
        source = Path(source_path)
        if not source.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {source_path}")
        
        if compressed_path is None:
            compressed_path = str(source) + ".gz"
        
        with open(source, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb', compresslevel=self.compression_level) as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        original_size = source.stat().st_size
        compressed_size = Path(compressed_path).stat().st_size
        compression_ratio = (1 - compressed_size / original_size) * 100
        
        return {
            'compressed_path': compressed_path,
            'original_size': original_size,
            'compressed_size': compressed_size,
            'compression_ratio': compression_ratio
        }
    
    def compress_directory(self, source_dir: str, archive_name: str = None) -> Dict:
        """Comprime un directorio completo"""
        source = Path(source_dir)
        if not source.exists():
            raise FileNotFoundError(f"Directorio no encontrado: {source_dir}")
        
        if archive_name is None:
            archive_name = f"{source.name}_{int(time.time())}.tar.gz"
        
        archive_path = self.backup_dir / archive_name
        
        # Crear archivo tar.gz
        shutil.make_archive(
            str(archive_path).replace('.tar.gz', ''),
            'gztar',
            str(source.parent),
            str(source.name)
        )
        
        return {
            'archive_path': str(archive_path),
            'source_directory': str(source),
            'created_at': time.time()
        }
    
    def compress_logs(self, log_dir: str = "logs", age_days: int = 7) -> List[Dict]:
        """Comprime logs antiguos"""
        log_path = Path(log_dir)
        if not log_path.exists():
            return []
        
        compressed_files = []
        cutoff_time = time.time() - (age_days * 24 * 3600)
        
        for log_file in log_path.glob("*.log"):
            if log_file.stat().st_mtime < cutoff_time:
                try:
                    result = self.compress_file(str(log_file))
                    # Eliminar archivo original después de comprimir
                    log_file.unlink()
                    compressed_files.append(result)
                except Exception as e:
                    print(f"Error comprimiendo {log_file}: {e}")
        
        return compressed_files
    
    def cleanup_old_backups(self, max_backups: int = 10) -> List[str]:
        """Limpia backups antiguos manteniendo solo los más recientes"""
        backup_files = list(self.backup_dir.glob("*.gz"))
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        removed_files = []
        for backup_file in backup_files[max_backups:]:
            try:
                backup_file.unlink()
                removed_files.append(str(backup_file))
            except Exception as e:
                print(f"Error eliminando backup {backup_file}: {e}")
        
        return removed_files
    
    def get_compression_stats(self) -> Dict:
        """Obtiene estadísticas de compresión"""
        backup_files = list(self.backup_dir.glob("*.gz"))
        total_size = sum(f.stat().st_size for f in backup_files)
        
        return {
            'total_backups': len(backup_files),
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'backup_directory': str(self.backup_dir),
            'compression_level': self.compression_level
        }

# Instancia global del compresor
backup_compressor = BackupCompressor()

def compress_backup(source_path: str, compressed_path: str = None) -> Dict:
    """Función utilitaria para comprimir backups"""
    return backup_compressor.compress_file(source_path, compressed_path)

def auto_compress_logs(log_dir: str = "logs", age_days: int = 7) -> List[Dict]:
    """Función utilitaria para compresión automática de logs"""
    return backup_compressor.compress_logs(log_dir, age_days)

def cleanup_backups(max_backups: int = 10) -> List[str]:
    """Función utilitaria para limpieza de backups"""
    return backup_compressor.cleanup_old_backups(max_backups)
