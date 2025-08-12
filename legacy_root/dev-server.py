# Script de desarrollo con hot-reload optimizado
import sys
import time
import subprocess
import threading
import queue
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class QuickRestartHandler(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.restart_queue = queue.Queue()
        self.restart_timer = None
        self.start_app()
        
        # Thread para manejar reinicios con debounce
        self.restart_thread = threading.Thread(target=self._restart_worker, daemon=True)
        self.restart_thread.start()
    
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.py'):
            # Ignorar archivos temporales y cache
            if any(ignore in event.src_path for ignore in ['__pycache__', '.pyc', '~', '.tmp']):
                return
                
            print(f"📝 Cambio detectado: {Path(event.src_path).name}")
            
            # Cancelar timer anterior si existe
            if self.restart_timer:
                self.restart_timer.cancel()
            
            # Crear nuevo timer con debounce de 0.5 segundos
            self.restart_timer = threading.Timer(0.5, self._queue_restart)
            self.restart_timer.start()
    
    def _queue_restart(self):
        self.restart_queue.put(True)
    
    def _restart_worker(self):
        while True:
            self.restart_queue.get()
            self._restart_app()
            # Vaciar queue para evitar reinicios múltiples
            while not self.restart_queue.empty():
                try:
                    self.restart_queue.get_nowait()
                except queue.Empty:
                    break
    
    def start_app(self):
        print("🚀 Iniciando Rexus.app...")
        self.process = subprocess.Popen(
            [sys.executable, "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Thread para mostrar output en tiempo real
        output_thread = threading.Thread(
            target=self._stream_output, 
            args=(self.process,), 
            daemon=True
        )
        output_thread.start()
    
    def _stream_output(self, process):
        for line in iter(process.stdout.readline, ''):
            if line.strip():
                print(f"📱 {line.strip()}")
    
    def _restart_app(self):
        if self.process and self.process.poll() is None:
            print("🔄 Reiniciando aplicación...")
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()
        
        self.start_app()

def main():
    print("🔥 Modo desarrollo Rexus.app - Hot Reload activado")
    print("Monitoring: ./rexus/")
    print("Presiona Ctrl+C para salir\n")
    
    # Configurar observador
    event_handler = QuickRestartHandler()
    observer = Observer()
    observer.schedule(event_handler, "./rexus", recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo desarrollo...")
        observer.stop()
        if event_handler.process and event_handler.process.poll() is None:
            event_handler.process.terminate()
            event_handler.process.wait()
    
    observer.join()
    print("✅ Desarrollo detenido")

if __name__ == "__main__":
    main()
