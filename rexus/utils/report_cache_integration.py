# -*- coding: utf-8 -*-
"""
Integración del Sistema de Cache Inteligente con Reportes
Proporciona funcionalidades específicas para cachear reportes del sistema Rexus

Funciones principales:
1. Integración automática con ReportesManager
2. Invalidación inteligente basada en cambios de datos
3. Cache específico para diferentes tipos de reportes
4. Métricas de rendimiento de reportes
5. Configuración adaptada para diferentes módulos

Autor: Rexus Development Team
Fecha: 23/08/2025
Versión: 1.0.0
"""

import sys
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
import logging
from pathlib import Path

# Configurar encoding UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Imports del sistema de cache
from .intelligent_cache_manager import (
    IntelligentCacheManager, 
    get_intelligent_cache_manager,
    CacheStrategy,
    cache_report
)

logger = logging.getLogger(__name__)


class ReportCacheManager:
    """Gestor especializado de cache para reportes del sistema."""
    
    def __init__(self):
        """Inicializar el gestor de cache de reportes."""
        self.cache_manager = get_intelligent_cache_manager(
            strategy=CacheStrategy.ADAPTIVE
        )
        
        # Configuración de TTL por tipo de reporte
        self.ttl_config = {
            # Reportes de inventario - datos que cambian frecuentemente
            'inventario_stock': 1800,        # 30 minutos
            'inventario_movimientos': 900,    # 15 minutos
            'inventario_valoracion': 3600,    # 1 hora
            'inventario_abc': 7200,          # 2 horas
            'inventario_rotacion': 7200,     # 2 horas
            
            # Reportes de obras - datos menos volátiles
            'obras_progreso': 1800,          # 30 minutos
            'obras_presupuesto': 3600,       # 1 hora
            'obras_cronograma': 3600,        # 1 hora
            'obras_recursos': 1800,          # 30 minutos
            
            # Reportes de compras
            'compras_ordenes': 1800,         # 30 minutos
            'compras_proveedores': 7200,     # 2 horas
            'compras_analisis': 3600,        # 1 hora
            
            # Reportes de pedidos
            'pedidos_estado': 900,           # 15 minutos
            'pedidos_entregas': 1800,        # 30 minutos
            'pedidos_analisis': 3600,        # 1 hora
            
            # Reportes financieros - datos críticos pero estables
            'finanzas_balance': 14400,       # 4 horas
            'finanzas_flujo_caja': 7200,     # 2 horas
            'finanzas_rentabilidad': 14400,  # 4 horas
            
            # Reportes de usuarios y auditoría
            'usuarios_actividad': 3600,      # 1 hora
            'auditoria_logs': 1800,          # 30 minutos
            'auditoria_seguridad': 900,      # 15 minutos
            
            # Reportes de logística
            'logistica_transportes': 1800,   # 30 minutos
            'logistica_rutas': 7200,         # 2 horas
            'logistica_estadisticas': 3600,  # 1 hora
        }
        
        # Tags para invalidación por módulos
        self.module_tags = {
            'inventario': ['inventario', 'stock', 'productos', 'materiales'],
            'obras': ['obras', 'proyectos', 'cronogramas', 'presupuestos'],
            'compras': ['compras', 'proveedores', 'ordenes'],
            'pedidos': ['pedidos', 'entregas', 'clientes'],
            'usuarios': ['usuarios', 'permisos', 'roles'],
            'finanzas': ['finanzas', 'contabilidad', 'balance'],
            'logistica': ['logistica', 'transportes', 'rutas'],
            'auditoria': ['auditoria', 'logs', 'seguridad']
        }
    
    def get_ttl_for_report(self, report_type: str) -> int:
        """Obtener TTL específico para un tipo de reporte."""
        return self.ttl_config.get(report_type, 3600)  # Default 1 hora
    
    def get_tags_for_module(self, module: str) -> List[str]:
        """Obtener tags para un módulo específico."""
        return self.module_tags.get(module, [module])
    
    def cache_inventory_report(self, report_type: str, data: Any, 
                              filters: Dict = None) -> bool:
        """Cachear reporte de inventario."""
        ttl = self.get_ttl_for_report(f'inventario_{report_type}')
        tags = self.get_tags_for_module('inventario')
        
        return self.cache_manager.set(
            data_source=f'inventario_{report_type}',
            data=data,
            parameters={'filters': filters or {}},
            ttl=ttl,
            tags=tags
        )
    
    def get_inventory_report(self, report_type: str, 
                           filters: Dict = None) -> Optional[Any]:
        """Obtener reporte de inventario desde cache."""
        return self.cache_manager.get(
            data_source=f'inventario_{report_type}',
            parameters={'filters': filters or {}}
        )
    
    def cache_works_report(self, report_type: str, data: Any,
                          filters: Dict = None) -> bool:
        """Cachear reporte de obras."""
        ttl = self.get_ttl_for_report(f'obras_{report_type}')
        tags = self.get_tags_for_module('obras')
        
        return self.cache_manager.set(
            data_source=f'obras_{report_type}',
            data=data,
            parameters={'filters': filters or {}},
            ttl=ttl,
            tags=tags
        )
    
    def get_works_report(self, report_type: str,
                        filters: Dict = None) -> Optional[Any]:
        """Obtener reporte de obras desde cache."""
        return self.cache_manager.get(
            data_source=f'obras_{report_type}',
            parameters={'filters': filters or {}}
        )
    
    def cache_purchases_report(self, report_type: str, data: Any,
                              filters: Dict = None) -> bool:
        """Cachear reporte de compras."""
        ttl = self.get_ttl_for_report(f'compras_{report_type}')
        tags = self.get_tags_for_module('compras')
        
        return self.cache_manager.set(
            data_source=f'compras_{report_type}',
            data=data,
            parameters={'filters': filters or {}},
            ttl=ttl,
            tags=tags
        )
    
    def get_purchases_report(self, report_type: str,
                            filters: Dict = None) -> Optional[Any]:
        """Obtener reporte de compras desde cache."""
        return self.cache_manager.get(
            data_source=f'compras_{report_type}',
            parameters={'filters': filters or {}}
        )
    
    def cache_orders_report(self, report_type: str, data: Any,
                           filters: Dict = None) -> bool:
        """Cachear reporte de pedidos."""
        ttl = self.get_ttl_for_report(f'pedidos_{report_type}')
        tags = self.get_tags_for_module('pedidos')
        
        return self.cache_manager.set(
            data_source=f'pedidos_{report_type}',
            data=data,
            parameters={'filters': filters or {}},
            ttl=ttl,
            tags=tags
        )
    
    def get_orders_report(self, report_type: str,
                         filters: Dict = None) -> Optional[Any]:
        """Obtener reporte de pedidos desde cache."""
        return self.cache_manager.get(
            data_source=f'pedidos_{report_type}',
            parameters={'filters': filters or {}}
        )
    
    def invalidate_module_cache(self, module: str) -> int:
        """Invalidar todo el cache de un módulo."""
        tags = self.get_tags_for_module(module)
        return self.cache_manager.invalidate(tags=tags)
    
    def invalidate_report_type(self, report_pattern: str) -> int:
        """Invalidar reportes por patrón (ej: 'inventario_*')."""
        return self.cache_manager.invalidate(pattern=report_pattern)
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas del cache de reportes."""
        return self.cache_manager.get_stats()
    
    def clear_all_report_cache(self) -> bool:
        """Limpiar todo el cache de reportes."""
        return self.cache_manager.clear()


# Instancia global del gestor de cache de reportes
_report_cache_manager = None


def get_report_cache_manager() -> ReportCacheManager:
    """Obtener instancia global del gestor de cache de reportes."""
    global _report_cache_manager
    
    if _report_cache_manager is None:
        _report_cache_manager = ReportCacheManager()
        logger.info("Gestor de cache de reportes inicializado")
    
    return _report_cache_manager


# Decoradores específicos para diferentes tipos de reportes
def cache_inventory_report(report_type: str, ttl: int = None):
    """Decorador para cachear reportes de inventario."""
    manager = get_report_cache_manager()
    actual_ttl = ttl or manager.get_ttl_for_report(f'inventario_{report_type}')
    tags = manager.get_tags_for_module('inventario')
    
    return cache_report(f'inventario_{report_type}', ttl=actual_ttl, tags=tags)


def cache_works_report(report_type: str, ttl: int = None):
    """Decorador para cachear reportes de obras."""
    manager = get_report_cache_manager()
    actual_ttl = ttl or manager.get_ttl_for_report(f'obras_{report_type}')
    tags = manager.get_tags_for_module('obras')
    
    return cache_report(f'obras_{report_type}', ttl=actual_ttl, tags=tags)


def cache_purchases_report(report_type: str, ttl: int = None):
    """Decorador para cachear reportes de compras."""
    manager = get_report_cache_manager()
    actual_ttl = ttl or manager.get_ttl_for_report(f'compras_{report_type}')
    tags = manager.get_tags_for_module('compras')
    
    return cache_report(f'compras_{report_type}', ttl=actual_ttl, tags=tags)


def cache_orders_report(report_type: str, ttl: int = None):
    """Decorador para cachear reportes de pedidos."""
    manager = get_report_cache_manager()
    actual_ttl = ttl or manager.get_ttl_for_report(f'pedidos_{report_type}')
    tags = manager.get_tags_for_module('pedidos')
    
    return cache_report(f'pedidos_{report_type}', ttl=actual_ttl, tags=tags)


def cache_financial_report(report_type: str, ttl: int = None):
    """Decorador para cachear reportes financieros."""
    manager = get_report_cache_manager()
    actual_ttl = ttl or manager.get_ttl_for_report(f'finanzas_{report_type}')
    tags = manager.get_tags_for_module('finanzas')
    
    return cache_report(f'finanzas_{report_type}', ttl=actual_ttl, tags=tags)


def cache_logistics_report(report_type: str, ttl: int = None):
    """Decorador para cachear reportes de logística."""
    manager = get_report_cache_manager()
    actual_ttl = ttl or manager.get_ttl_for_report(f'logistica_{report_type}')
    tags = manager.get_tags_for_module('logistica')
    
    return cache_report(f'logistica_{report_type}', ttl=actual_ttl, tags=tags)


class CacheInvalidationHooks:
    """Hooks para invalidación automática de cache basada en cambios de datos."""
    
    @staticmethod
    def on_inventory_change(operation: str, item_data: Dict):
        """Hook para cambios en inventario."""
        manager = get_report_cache_manager()
        
        # Invalidar reportes de inventario relacionados
        if operation in ['create', 'update', 'delete']:
            manager.invalidate_module_cache('inventario')
            
            # Si es un cambio de stock, invalidar también reportes relacionados
            if 'stock' in item_data or 'cantidad' in item_data:
                manager.invalidate_report_type('inventario_stock')
                manager.invalidate_report_type('inventario_valoracion')
        
        logger.debug(f"Cache invalidado por cambio en inventario: {operation}")
    
    @staticmethod
    def on_works_change(operation: str, work_data: Dict):
        """Hook para cambios en obras."""
        manager = get_report_cache_manager()
        
        if operation in ['create', 'update', 'delete']:
            manager.invalidate_module_cache('obras')
            
            # Si es cambio de presupuesto o cronograma, invalidar específicamente
            if any(field in work_data for field in ['presupuesto', 'fecha_inicio', 'fecha_fin']):
                manager.invalidate_report_type('obras_presupuesto')
                manager.invalidate_report_type('obras_cronograma')
        
        logger.debug(f"Cache invalidado por cambio en obras: {operation}")
    
    @staticmethod
    def on_purchases_change(operation: str, purchase_data: Dict):
        """Hook para cambios en compras."""
        manager = get_report_cache_manager()
        
        if operation in ['create', 'update', 'delete']:
            manager.invalidate_module_cache('compras')
            
            # Invalidar también inventario si afecta stock
            if operation == 'create' and 'productos' in purchase_data:
                manager.invalidate_report_type('inventario_movimientos')
        
        logger.debug(f"Cache invalidado por cambio en compras: {operation}")
    
    @staticmethod
    def on_orders_change(operation: str, order_data: Dict):
        """Hook para cambios en pedidos."""
        manager = get_report_cache_manager()
        
        if operation in ['create', 'update', 'delete']:
            manager.invalidate_module_cache('pedidos')
            
            # Si cambia el estado, invalidar reportes de estado
            if 'estado' in order_data:
                manager.invalidate_report_type('pedidos_estado')
                manager.invalidate_report_type('pedidos_entregas')
        
        logger.debug(f"Cache invalidado por cambio en pedidos: {operation}")


# Función para integrar hooks en el sistema
def setup_cache_invalidation_hooks():
    """Configurar hooks de invalidación automática."""
    # Esta función debe ser llamada durante la inicialización del sistema
    # para conectar los hooks con los eventos de cambio de datos
    
    logger.info("Hooks de invalidación de cache configurados")


# Utilidades para monitoreo de rendimiento de cache
class CachePerformanceMonitor:
    """Monitor de rendimiento del sistema de cache de reportes."""
    
    def __init__(self):
        self.manager = get_report_cache_manager()
        self.performance_log = []
    
    def log_report_execution(self, report_name: str, execution_time: float, 
                           from_cache: bool, data_size: int = 0):
        """Registrar ejecución de reporte para análisis de rendimiento."""
        entry = {
            'timestamp': datetime.now(),
            'report_name': report_name,
            'execution_time': execution_time,
            'from_cache': from_cache,
            'data_size': data_size
        }
        self.performance_log.append(entry)
        
        # Mantener solo últimas 1000 entradas
        if len(self.performance_log) > 1000:
            self.performance_log = self.performance_log[-1000:]
    
    def get_performance_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Obtener resumen de rendimiento de las últimas horas."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_logs = [
            entry for entry in self.performance_log 
            if entry['timestamp'] > cutoff_time
        ]
        
        if not recent_logs:
            return {'message': 'No hay datos de rendimiento disponibles'}
        
        # Calcular estadísticas
        total_reports = len(recent_logs)
        cached_reports = sum(1 for entry in recent_logs if entry['from_cache'])
        cache_hit_rate = (cached_reports / total_reports) * 100 if total_reports > 0 else 0
        
        avg_cache_time = sum(
            entry['execution_time'] for entry in recent_logs if entry['from_cache']
        ) / cached_reports if cached_reports > 0 else 0
        
        avg_db_time = sum(
            entry['execution_time'] for entry in recent_logs if not entry['from_cache']
        ) / (total_reports - cached_reports) if (total_reports - cached_reports) > 0 else 0
        
        # Reportes más lentos
        slowest_reports = sorted(
            recent_logs, key=lambda x: x['execution_time'], reverse=True
        )[:5]
        
        return {
            'period_hours': hours,
            'total_reports': total_reports,
            'cache_hit_rate': round(cache_hit_rate, 2),
            'cached_reports': cached_reports,
            'database_reports': total_reports - cached_reports,
            'avg_cache_time_ms': round(avg_cache_time * 1000, 2),
            'avg_database_time_ms': round(avg_db_time * 1000, 2),
            'time_saved_ratio': round(
                (avg_db_time - avg_cache_time) / avg_db_time * 100, 2
            ) if avg_db_time > 0 else 0,
            'slowest_reports': [
                {
                    'name': entry['report_name'],
                    'time_ms': round(entry['execution_time'] * 1000, 2),
                    'from_cache': entry['from_cache']
                }
                for entry in slowest_reports
            ]
        }


# Instancia global del monitor de rendimiento
_performance_monitor = None


def get_performance_monitor() -> CachePerformanceMonitor:
    """Obtener instancia del monitor de rendimiento."""
    global _performance_monitor
    
    if _performance_monitor is None:
        _performance_monitor = CachePerformanceMonitor()
    
    return _performance_monitor


# Decorador con monitoreo de rendimiento
def monitored_cache_report(report_name: str, report_type: str, 
                          module: str, ttl: int = None):
    """Decorador que incluye monitoreo de rendimiento."""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            import time
            
            # Obtener managers
            cache_manager = get_report_cache_manager()
            monitor = get_performance_monitor()
            
            # Intentar obtener del cache
            start_time = time.time()
            
            # Generar parámetros para cache
            parameters = {'args': args[1:], 'kwargs': kwargs}  # Excluir self
            
            cached_result = cache_manager.cache_manager.get(
                f'{module}_{report_type}', parameters
            )
            
            if cached_result is not None:
                end_time = time.time()
                execution_time = end_time - start_time
                
                # Log rendimiento
                monitor.log_report_execution(
                    report_name, execution_time, True, 
                    sys.getsizeof(cached_result)
                )
                
                logger.debug(f"Reporte servido desde cache: {report_name}")
                return cached_result
            
            # Ejecutar función
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Cachear resultado
            actual_ttl = ttl or cache_manager.get_ttl_for_report(f'{module}_{report_type}')
            tags = cache_manager.get_tags_for_module(module)
            
            cache_manager.cache_manager.set(
                data_source=f'{module}_{report_type}',
                data=result,
                parameters=parameters,
                ttl=actual_ttl,
                tags=tags
            )
            
            # Log rendimiento
            monitor.log_report_execution(
                report_name, execution_time, False, 
                sys.getsizeof(result)
            )
            
            logger.debug(f"Reporte calculado y cacheado: {report_name}")
            return result
        
        return wrapper
    return decorator


if __name__ == '__main__':
    # Configurar logging para prueba
    logging.basicConfig(level=logging.INFO)
    
    # Obtener gestor de cache de reportes
    manager = get_report_cache_manager()
    
    # Ejemplo de uso
    test_data = {
        'productos': [
            {'id': 1, 'nombre': 'Producto A', 'stock': 100},
            {'id': 2, 'nombre': 'Producto B', 'stock': 50}
        ],
        'totales': {'productos': 2, 'valor_total': 15000}
    }
    
    # Cachear reporte de inventario
    success = manager.cache_inventory_report('stock', test_data, {'activos': True})
    print(f"Reporte cacheado: {success}")
    
    # Recuperar reporte
    cached_report = manager.get_inventory_report('stock', {'activos': True})
    print(f"Reporte recuperado: {cached_report is not None}")
    
    # Estadísticas
    stats = manager.get_cache_statistics()
    print(f"Estadísticas del cache: {stats}")
    
    print("✅ Sistema de cache de reportes funcionando correctamente")