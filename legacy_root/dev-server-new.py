#!/usr/bin/env python3
"""
Servidor de desarrollo con hot-reload para Rexus.app
Auto-login con credenciales de desarrollo - Sin más contraseñas!
"""

import sys
import os
import time
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Cargar configuración de desarrollo
try:
    from dotenv import load_dotenv
    env_file = Path('.env.development')
    if env_file.exists():
        load_dotenv(env_file)
        print(f"🔧 Configuración cargada desde {env_file}")
except ImportError:
    print("⚠️  python-dotenv no disponible, usando variables del sistema")

class RexusDevHandler(FileSystemEventHandler):
    """Handler para reiniciar la aplicación cuando cambian los archivos."""

    def __init__(self):
        self.process = None
        self.restart_count = 0
        self.last_restart = 0
        print("🚀 Servidor de desarrollo Rexus iniciado")
        print("📁 Monitoreando cambios en archivos .py")
        self.start_app()

    def on_modified(self, event):
        """Reinicia la app cuando se modifica un archivo .py"""
        if not event.is_directory and event.src_path.endswith('.py'):
            # Evitar reinicios demasiado frecuentes
            current_time = time.time()
            if current_time - self.last_restart < 2:
                return

            self.last_restart = current_time
            print(f"📝 Cambio detectado: {event.src_path}")
            self.restart_app()

    def start_app(self):
        """Inicia la aplicación Rexus con auto-login"""
        try:
            # Configurar variables de entorno para desarrollo
            env = os.environ.copy()
            env['PYTHONPATH'] = str(Path('.').resolve())

            # Habilitar modo desarrollo y auto-login
            env['REXUS_ENV'] = 'development'
            env['HOTRELOAD_ENABLED'] = 'true'

            # Credenciales de desarrollo (desde .env.development)
            env['REXUS_DEV_USER'] = os.getenv('REXUS_DEV_USER', 'admin')
            env['REXUS_DEV_PASSWORD'] = os.getenv('REXUS_DEV_PASSWORD', 'admin')
            env['REXUS_DEV_AUTO_LOGIN'] = os.getenv('REXUS_DEV_AUTO_LOGIN', 'true')

            # Ejecutar con parámetro --dev para indicar modo desarrollo
            self.process = subprocess.Popen(
                [sys.executable, 'main.py', '--dev'],
                env=env,
                cwd='.',
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print(f"✅ Aplicación iniciada en modo desarrollo (PID: {self.process.pid})")
            print(f"🔐 Auto-login habilitado con usuario: {env['REXUS_DEV_USER']}")

        except Exception as e:
            print(f"❌ Error iniciando aplicación: {e}")

    def restart_app(self):
        """Reinicia la aplicación"""
        self.restart_count += 1
        print(f"🔄 Reiniciando aplicación (#{self.restart_count})...")

        # Terminar proceso anterior
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()

        # Pequeña pausa antes de reiniciar
        time.sleep(0.5)
        self.start_app()

def main():
    """Función principal del servidor de desarrollo"""

    # Verificar que estamos en el directorio correcto
    if not Path('main.py').exists():
        print("❌ Error: main.py no encontrado")
        print("   Asegúrate de ejecutar desde el directorio raíz de Rexus.app")
        sys.exit(1)

    # Verificar dependencias
    try:
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
    except ImportError:
        print("❌ Error: watchdog no está instalado")
        print("   Instala con: pip install watchdog")
        sys.exit(1)

    print("🎯 Rexus.app - Servidor de Desarrollo")
    print("=" * 50)
    print("💡 Características:")
    print("   • Hot-reload automático")
    print("   • Sin problemas de Docker/contraseñas")
    print("   • Reinicio rápido < 2 segundos")
    print("   • Ctrl+C para salir")
    print("=" * 50)

    # Configurar watchdog
    event_handler = RexusDevHandler()
    observer = Observer()

    # Monitorear directorios clave
    watch_dirs = ['rexus', 'scripts', 'resources', 'tools']
    for watch_dir in watch_dirs:
        if Path(watch_dir).exists():
            observer.schedule(event_handler, watch_dir, recursive=True)
            print(f"👀 Monitoreando: {watch_dir}/")

    # También monitorear archivos raíz
    observer.schedule(event_handler, '.', recursive=False)

    observer.start()

    try:
        print("\n🟢 Servidor activo. Presiona Ctrl+C para salir...")
        while True:
            time.sleep(1)

            # Verificar si el proceso sigue vivo
            if event_handler.process and \
                event_handler.process.poll() is not None:
                return_code = event_handler.process.returncode
                if return_code != 0:
                    print(f"⚠️  La aplicación terminó con código: {return_code}")
                    print("🔄 Intentando reiniciar...")
                    event_handler.restart_app()

    except KeyboardInterrupt:
        print("\n🛑 Deteniendo servidor de desarrollo...")
        observer.stop()

        # Terminar la aplicación
        if event_handler.process and event_handler.process.poll() is None:
            print("🔚 Cerrando aplicación...")
            event_handler.process.terminate()
            event_handler.process.wait()

        print("✅ Servidor detenido correctamente")

    observer.join()

if __name__ == "__main__":
    main()
