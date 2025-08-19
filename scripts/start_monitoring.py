#!/usr/bin/env python3
"""
Script para iniciar el sistema de monitoreo de Rexus.app
Inicia todos los componentes de monitoreo y métricas en tiempo real
"""

import sys
import os
import signal
import time
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from rexus.utils.app_logger import get_logger
from rexus.utils.monitoring_system import start_monitoring, stop_monitoring, get_system_status
from rexus.utils.performance_monitor import performance_monitor

logger = get_logger(__name__)

class MonitoringService:
    """Servicio principal de monitoreo"""
    
    def __init__(self):
        self.is_running = False
        self.logger = get_logger(self.__class__.__name__)
        
    def start(self, interval: int = 30):
        """Inicia todos los servicios de monitoreo"""
        try:
            self.logger.info("=== INICIANDO SISTEMA DE MONITOREO REXUS.APP ===")
            
            # Iniciar recolector de métricas
            self.logger.info("Iniciando recolector de métricas del sistema...")
            start_monitoring(interval=interval)
            
            # Iniciar monitor de rendimiento
            self.logger.info("Iniciando monitor de rendimiento...")
            performance_monitor.start_monitoring(interval_seconds=60)
            
            self.is_running = True
            self.logger.info(f"✅ Sistema de monitoreo iniciado exitosamente")
            self.logger.info(f"   - Intervalo de métricas del sistema: {interval}s")
            self.logger.info(f"   - Intervalo de rendimiento: 60s")
            self.logger.info("   - Logs disponibles en tiempo real")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Error iniciando sistema de monitoreo: {e}")
            return False
            
    def stop(self):
        """Detiene todos los servicios de monitoreo"""
        try:
            self.logger.info("=== DETENIENDO SISTEMA DE MONITOREO ===")
            
            # Detener servicios
            stop_monitoring()
            performance_monitor.stop_monitoring()
            
            self.is_running = False
            self.logger.info("✅ Sistema de monitoreo detenido correctamente")
            
        except Exception as e:
            self.logger.error(f"❌ Error deteniendo monitoreo: {e}")
            
    def get_status(self):
        """Obtiene el estado actual del monitoreo"""
        try:
            system_status = get_system_status()
            performance_stats = performance_monitor.get_current_stats()
            optimization_report = performance_monitor.get_optimization_report()
            
            return {
                'running': self.is_running,
                'system_metrics': system_status,
                'performance_stats': performance_stats,
                'optimization': optimization_report
            }
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estado: {e}")
            return {'running': False, 'error': str(e)}
            
    def run_monitoring_loop(self, interval: int = 30):
        """Ejecuta el loop principal de monitoreo"""
        if not self.start(interval):
            return False
            
        try:
            self.logger.info("=== ENTRANDO EN MODO MONITOREO CONTINUO ===")
            self.logger.info("Presiona Ctrl+C para detener el monitoreo")
            
            # Configurar handler para señales
            def signal_handler(signum, frame):
                self.logger.info("\\n=== SEÑAL DE INTERRUPCIÓN RECIBIDA ===")
                self.stop()
                sys.exit(0)
                
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
            
            # Loop principal
            report_interval = 300  # Reporte cada 5 minutos
            last_report = time.time()
            
            while self.is_running:
                current_time = time.time()
                
                # Generar reporte periódico
                if current_time - last_report >= report_interval:
                    self._generate_status_report()
                    last_report = current_time
                
                time.sleep(10)  # Check cada 10 segundos
                
        except KeyboardInterrupt:
            self.logger.info("\\n=== INTERRUPCIÓN MANUAL ===")
            self.stop()
        except Exception as e:
            self.logger.error(f"❌ Error en loop de monitoreo: {e}")
            self.stop()
            
    def _generate_status_report(self):
        """Genera reporte de estado periódico"""
        try:
            status = self.get_status()
            
            self.logger.info("=== REPORTE DE ESTADO PERIÓDICO ===")
            
            # Métricas del sistema
            system = status.get('system_metrics', {})
            if system:
                self.logger.info(f"Estado del sistema: {system.get('status', 'DESCONOCIDO')}")
                self.logger.info(f"CPU promedio: {system.get('cpu_promedio', 0):.1f}%")
                self.logger.info(f"Memoria promedio: {system.get('memoria_promedio', 0):.1f}%")
                self.logger.info(f"Tiempo respuesta: {system.get('tiempo_respuesta_promedio', 0):.3f}s")
                self.logger.info(f"Total errores: {system.get('total_errores', 0)}")
                self.logger.info(f"Total consultas: {system.get('total_consultas', 0)}")
                
            # Estadísticas de rendimiento
            perf = status.get('performance_stats', {})
            if perf:
                self.logger.info(f"Threads activos: {perf.get('active_threads', 0)}")
                self.logger.info(f"Memoria actual: {perf.get('current_memory_mb', 0):.1f} MB")
                
            # Recomendaciones de optimización
            opt = status.get('optimization', {})
            if opt and opt.get('recommendations'):
                self.logger.info("Recomendaciones de optimización:")
                for rec in opt['recommendations']:
                    self.logger.info(f"  - {rec}")
                    
            self.logger.info("=" * 50)
            
        except Exception as e:
            self.logger.error(f"Error generando reporte: {e}")

def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sistema de Monitoreo Rexus.app')
    parser.add_argument('--interval', type=int, default=30, 
                       help='Intervalo de recolección de métricas en segundos (default: 30)')
    parser.add_argument('--daemon', action='store_true', 
                       help='Ejecutar como servicio en background')
    parser.add_argument('--status', action='store_true',
                       help='Mostrar estado actual y salir')
    parser.add_argument('--stop', action='store_true',
                       help='Detener monitoreo y salir')
    
    args = parser.parse_args()
    
    service = MonitoringService()
    
    # Mostrar solo estado
    if args.status:
        status = service.get_status()
        print("=== ESTADO DEL SISTEMA DE MONITOREO ===")
        print(f"Estado: {'ACTIVO' if status.get('running') else 'INACTIVO'}")
        
        system = status.get('system_metrics', {})
        if system:
            print(f"CPU: {system.get('cpu_promedio', 0):.1f}%")
            print(f"Memoria: {system.get('memoria_promedio', 0):.1f}%")
            print(f"Errores: {system.get('total_errores', 0)}")
            print(f"Consultas: {system.get('total_consultas', 0)}")
            
        return
        
    # Detener monitoreo
    if args.stop:
        print("Deteniendo sistema de monitoreo...")
        service.stop()
        return
        
    # Ejecutar monitoreo
    if args.daemon:
        print(f"Iniciando monitoreo en modo daemon (intervalo: {args.interval}s)...")
        service.run_monitoring_loop(args.interval)
    else:
        print(f"Iniciando monitoreo interactivo (intervalo: {args.interval}s)...")
        service.run_monitoring_loop(args.interval)

if __name__ == "__main__":
    main()