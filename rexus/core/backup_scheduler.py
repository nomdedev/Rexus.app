"""
Scheduler de Backups - Rexus.app
Automatiza la ejecución de backups según la programación configurada

Uso:
    python -m rexus.core.backup_scheduler --daemon
    python -m rexus.core.backup_scheduler --run-once
    python -m rexus.core.backup_scheduler --status
"""

import argparse
import logging
import signal
import sys
import time
from datetime import datetime
from typing import Optional

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./logs/backup_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class BackupScheduler:
    """
    Scheduler para automatizar backups.

    Programa:
    - Backups Full diarios a las 2 AM
    - Backups Diferenciales cada 4 horas
    - Backups de Log cada 15 minutos
    """

    def __init__(self):
        """Inicializa el scheduler de backups."""
        from rexus.core.backup_manager import get_backup_manager, BackupType

        self.backup_manager = get_backup_manager()
        self.running = False
        self.last_full_backup = None
        self.last_differential_backup = None
        self.last_log_backup = None

        # Obtener configuración
        self.full_backup_hour = self.backup_manager.config.full_backup_hour
        self.differential_interval_hours = self.backup_manager.config.differential_interval_hours
        self.log_interval_minutes = self.backup_manager.config.log_interval_minutes

        # Registrar handlers de señales para cierre elegante
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Maneja señales de cierre."""
        logger.info(f"Recibida señal {signum}, deteniendo scheduler...")
        self.stop()

    def should_run_full_backup(self) -> bool:
        """
        Verifica si debe ejecutar un backup full.

        Returns:
            True si es hora del backup full diario
        """
        if self.last_full_backup is None:
            return True

        now = datetime.now()

        # Verificar si estamos en la hora configurada
        if now.hour != self.full_backup_hour:
            return False

        # Verificar si ya corrió hoy
        if self.last_full_backup.date() == now.date():
            return False

        return True

    def should_run_differential_backup(self) -> bool:
        """
        Verifica si debe ejecutar un backup diferencial.

        Returns:
            True si ha pasado el intervalo configurado
        """
        if self.last_differential_backup is None:
            # Primer backup diferencial: ejecutar 1 hora después del full
            if self.last_full_backup:
                hours_since_full = (datetime.now() - self.last_full_backup).total_seconds() / 3600
                return hours_since_full >= 1
            return True

        hours_since_last = (datetime.now() - self.last_differential_backup).total_seconds() / 3600
        return hours_since_last >= self.differential_interval_hours

    def should_run_log_backup(self) -> bool:
        """
        Verifica si debe ejecutar un backup de log.

        Returns:
            True si ha pasado el intervalo configurado
        """
        if self.last_log_backup is None:
            return True

        minutes_since_last = (datetime.now() - self.last_log_backup).total_seconds() / 60
        return minutes_since_last >= self.log_interval_minutes

    def run_full_backup(self) -> dict:
        """Ejecuta un backup full de todas las bases de datos."""
        logger.info("=" * 60)
        logger.info("Iniciando BACKUP FULL de todas las bases de datos")
        logger.info("=" * 60)

        results = self.backup_manager.create_all_backups(BackupType.FULL)

        successful = sum(1 for r in results if r.status == "success")
        failed = len(results) - successful

        logger.info(f"Backup Full completado: {successful} exitosos, {failed} fallidos")

        self.last_full_backup = datetime.now()

        return {
            'type': 'full',
            'successful': successful,
            'failed': failed,
            'timestamp': self.last_full_backup.isoformat()
        }

    def run_differential_backup(self) -> dict:
        """Ejecuta un backup diferencial de todas las bases de datos."""
        logger.info("-" * 60)
        logger.info("Iniciando BACKUP DIFERENCIAL de todas las bases de datos")
        logger.info("-" * 60)

        results = self.backup_manager.create_all_backups(BackupType.DIFFERENTIAL)

        successful = sum(1 for r in results if r.status == "success")
        failed = len(results) - successful

        logger.info(f"Backup Diferencial completado: {successful} exitosos, {failed} fallidos")

        self.last_differential_backup = datetime.now()

        return {
            'type': 'differential',
            'successful': successful,
            'failed': failed,
            'timestamp': self.last_differential_backup.isoformat()
        }

    def run_log_backup(self) -> dict:
        """Ejecuta un backup de log de todas las bases de datos."""
        logger.debug("Iniciando BACKUP DE LOG de todas las bases de datos")

        results = self.backup_manager.create_all_backups(BackupType.LOG)

        successful = sum(1 for r in results if r.status == "success")
        failed = len(results) - successful

        logger.debug(f"Backup de Log completado: {successful} exitosos, {failed} fallidos")

        self.last_log_backup = datetime.now()

        return {
            'type': 'log',
            'successful': successful,
            'failed': failed,
            'timestamp': self.last_log_backup.isoformat()
        }

    def run_cycle(self) -> list:
        """
        Ejecuta un ciclo de verificación y backups.

        Returns:
            Lista de resultados de backups ejecutados
        """
        results = []

        # Verificar backup full
        if self.should_run_full_backup():
            results.append(self.run_full_backup())

        # Verificar backup diferencial (no ejecutar si acaba de correr full)
        elif self.should_run_differential_backup():
            results.append(self.run_differential_backup())

        # Verificar backup de log
        if self.should_run_log_backup():
            results.append(self.run_log_backup())

        # Limpiar backups antiguos (después del backup full)
        if self.last_full_backup and (datetime.now() - self.last_full_backup).total_seconds() < 3600:
            cleanup_stats = self.backup_manager.cleanup_old_backups()
            logger.info(f"Limpieza de backups antiguos: {cleanup_stats}")

        return results

    def start(self):
        """Inicia el scheduler en modo daemon."""
        logger.info("Iniciando scheduler de backups...")
        logger.info(f"Configuración:")
        logger.info(f"  - Backup Full: diario a las {self.full_backup_hour}:00")
        logger.info(f"  - Backup Diferencial: cada {self.differential_interval_hours} horas")
        logger.info(f"  - Backup de Log: cada {self.log_interval_minutes} minutos")

        self.running = True

        while self.running:
            try:
                # Ejecutar ciclo
                results = self.run_cycle()

                # Esperar antes del próximo ciclo
                time.sleep(60)  # Verificar cada minuto

            except Exception as e:
                logger.error(f"Error en ciclo de scheduler: {e}")
                time.sleep(60)

        logger.info("Scheduler detenido")

    def stop(self):
        """Detiene el scheduler."""
        self.running = False

    def run_once(self) -> list:
        """Ejecuta un ciclo único y retorna los resultados."""
        logger.info("Ejecutando ciclo único de backups...")
        return self.run_cycle()

    def get_status(self) -> dict:
        """
        Obtiene el estado actual del scheduler.

        Returns:
            Diccionario con estado del scheduler
        """
        backup_status = self.backup_manager.get_backup_status()

        return {
            'scheduler_running': self.running,
            'last_full_backup': self.last_full_backup.isoformat() if self.last_full_backup else None,
            'last_differential_backup': self.last_differential_backup.isoformat() if self.last_differential_backup else None,
            'last_log_backup': self.last_log_backup.isoformat() if self.last_log_backup else None,
            'next_full_backup': self._calculate_next_full_backup(),
            'next_differential_backup': self._calculate_next_differential_backup(),
            'backup_status': backup_status
        }

    def _calculate_next_full_backup(self) -> str:
        """Calcula cuándo será el próximo backup full."""
        now = datetime.now()

        if self.last_full_backup and self.last_full_backup.date() == now.date():
            # Ya corrió hoy, próxima es mañana
            next_backup = now.replace(hour=self.full_backup_hour, minute=0, second=0, microsecond=0)
            next_backup = next_backup.replace(day=next_backup.day + 1)
        else:
            # No ha corrido hoy, próxima es hoy a la hora configurada
            if now.hour < self.full_backup_hour:
                next_backup = now.replace(hour=self.full_backup_hour, minute=0, second=0, microsecond=0)
            else:
                # Ya pasó la hora, mañana
                next_backup = now.replace(hour=self.full_backup_hour, minute=0, second=0, microsecond=0)
                next_backup = next_backup.replace(day=next_backup.day + 1)

        return next_backup.isoformat()

    def _calculate_next_differential_backup(self) -> str:
        """Calcula cuándo será el próximo backup diferencial."""
        if self.last_differential_backup is None:
            return "Pendiente (primer backup)"

        next_backup = self.last_differential_backup
        while next_backup < datetime.now():
            next_backup = next_backup.replace(hour=next_backup.hour + self.differential_interval_hours)

        return next_backup.isoformat()


def main():
    """Función principal para ejecución desde línea de comandos."""
    parser = argparse.ArgumentParser(
        description='Scheduler de backups para Rexus.app'
    )
    parser.add_argument(
        '--daemon',
        action='store_true',
        help='Ejecuta el scheduler en modo daemon (continuo)'
    )
    parser.add_argument(
        '--run-once',
        action='store_true',
        help='Ejecuta un ciclo único de backups'
    )
    parser.add_argument(
        '--status',
        action='store_true',
        help='Muestra el estado actual del scheduler y los backups'
    )
    parser.add_argument(
        '--full',
        action='store_true',
        help='Ejecuta un backup full inmediatamente'
    )
    parser.add_argument(
        '--differential',
        action='store_true',
        help='Ejecuta un backup diferencial inmediatamente'
    )
    parser.add_argument(
        '--log',
        action='store_true',
        help='Ejecuta un backup de log inmediatamente'
    )

    args = parser.parse_args()

    scheduler = BackupScheduler()

    if args.daemon:
        scheduler.start()

    elif args.run_once:
        results = scheduler.run_once()
        print("\nResultados del ciclo:")
        for result in results:
            print(f"  - {result['type']}: {result['successful']} exitosos, {result['failed']} fallidos")

    elif args.status:
        status = scheduler.get_status()
        print("\nEstado del Scheduler:")
        print(f"  Ejecutándose: {status['scheduler_running']}")
        print(f"  Último backup full: {status['last_full_backup']}")
        print(f"  Último backup diferencial: {status['last_differential_backup']}")
        print(f"  Último backup de log: {status['last_log_backup']}")
        print(f"  Próximo backup full: {status['next_full_backup']}")
        print(f"  Próximo backup diferencial: {status['next_differential_backup']}")
        print(f"\nEstadísticas de backups:")
        print(f"  Total backups full: {status['backup_status']['backup_count']['full']}")
        print(f"  Total backups diferenciales: {status['backup_status']['backup_count']['differential']}")
        print(f"  Total backups de log: {status['backup_status']['backup_count']['log']}")
        print(f"  Tamaño total: {status['backup_status']['total_size_mb']} MB")

    elif args.full:
        from rexus.core.backup_manager import BackupType
        results = scheduler.backup_manager.create_all_backups(BackupType.FULL)
        for result in results:
            status_icon = "✅" if result.status == "success" else "❌"
            print(f"{status_icon} {result.database}: {result.status}")
            if result.status == "failed":
                print(f"   Error: {result.error_message}")

    elif args.differential:
        from rexus.core.backup_manager import BackupType
        results = scheduler.backup_manager.create_all_backups(BackupType.DIFFERENTIAL)
        for result in results:
            status_icon = "✅" if result.status == "success" else "❌"
            print(f"{status_icon} {result.database}: {result.status}")

    elif args.log:
        from rexus.core.backup_manager import BackupType
        results = scheduler.backup_manager.create_all_backups(BackupType.LOG)
        for result in results:
            status_icon = "✅" if result.status == "success" else "❌"
            print(f"{status_icon} {result.database}: {result.status}")

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
