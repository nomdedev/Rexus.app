#!/usr/bin/env python3
"""
Gestor Central de Optimizaciones para Rexus
Coordina cache, lazy loading y compresión
"""

from typing import Dict, Any
import time

class OptimizationManager:
    """Gestor central de todas las optimizaciones"""

    def __init__(self):
        self.cache_system = None
        self.lazy_loader = None
        self.backup_compressor = None
        self._stats = {
            'optimization_start_time': time.time(),
            'cache_hits': 0,
            'modules_loaded': 0,
            'backups_compressed': 0
        }

    def initialize_systems(self):
        """Inicializa todos los sistemas de optimización"""
        try:
            from .intelligent_cache import cache_instance
            self.cache_system = cache_instance
            print("[CHECK] Cache inteligente inicializado")
        except ImportError:
            print("[WARN] Cache inteligente no disponible")

        try:
            from .lazy_loader import lazy_loader, preload_essential_modules
            self.lazy_loader = lazy_loader
            preload_essential_modules()
            print("[CHECK] Carga bajo demanda inicializada")
        except ImportError:
            print("[WARN] Carga bajo demanda no disponible")

        try:
            from .backup_compressor import backup_compressor
            self.backup_compressor = backup_compressor
            print("[CHECK] Compresión de backups inicializada")
        except ImportError:
            print("[WARN] Compresión de backups no disponible")

    def get_performance_report(self) -> Dict[str, Any]:
        """Genera reporte de rendimiento"""
        report = {
            'uptime_seconds': time.time() - self._stats['optimization_start_time'],
            'systems_active': []
        }

        if self.cache_system:
            cache_stats = self.cache_system.get_stats()
            report['cache_system'] = cache_stats
            report['systems_active'].append('cache')

        if self.lazy_loader:
            loader_stats = self.lazy_loader.get_loading_stats()
            report['lazy_loading'] = loader_stats
            report['systems_active'].append('lazy_loading')

        if self.backup_compressor:
            compression_stats = self.backup_compressor.get_compression_stats()
            report['backup_compression'] = compression_stats
            report['systems_active'].append('backup_compression')

        return report

    def optimize_system(self):
        """Ejecuta optimización completa del sistema"""
        optimizations_applied = []

        # Limpiar cache expirado
        if self.cache_system:
            self.cache_system.invalidate()
            optimizations_applied.append("cache_cleanup")

        # Comprimir logs antiguos
        if self.backup_compressor:
            compressed = self.backup_compressor.compress_logs()
            if compressed:
                optimizations_applied.append(f"compressed_{len(compressed)}_logs")

        return optimizations_applied

# Instancia global del gestor
optimization_manager = OptimizationManager()

def initialize_optimizations():
    """Función utilitaria para inicializar optimizaciones"""
    optimization_manager.initialize_systems()

def get_optimization_report() -> Dict[str, Any]:
    """Función utilitaria para obtener reporte de optimizaciones"""
    return optimization_manager.get_performance_report()
