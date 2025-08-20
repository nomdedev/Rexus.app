#!/usr/bin/env python3
"""
Punto de entrada principal para Rexus.app - REESTRUCTURADO
"""

import sys
import os
from pathlib import Path

def setup_environment():
    """Configura el entorno de la aplicación."""
    root_dir = Path(__file__).parent
    os.chdir(root_dir)
    sys.path.insert(0, str(root_dir))

    # Detectar modo desarrollo
    is_dev_mode = (
        '--dev' in sys.argv or
        os.getenv('REXUS_ENV') == 'development' or
        os.getenv('HOTRELOAD_ENABLED', '').lower() == 'true'
    )

    if is_dev_mode:
        print("[DEV] Modo desarrollo activado")
        os.environ.setdefault('REXUS_DEV_USER', 'admin')
        os.environ.setdefault('REXUS_DEV_PASSWORD', 'admin')
        os.environ.setdefault('REXUS_DEV_AUTO_LOGIN', 'true')

    return True

def main():
    """Función principal simplificada."""
    if not setup_environment():
        sys.exit(1)
    
    # Intentar cargar la aplicación real, con fallback
    try:
        print("Intentando cargar aplicación completa...")
        from rexus.main.app import main as app_main
        app_main()
    except ImportError as e:
        print(f"Error de importación: {e}")
        print("Iniciando en modo básico...")
        run_basic_mode()
    except Exception as e:
        print(f"Error general: {e}")
        print("Iniciando en modo de emergencia...")
        run_emergency_mode()

def run_basic_mode():
    """Modo básico cuando fallan los imports."""
    try:
        from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
        from PyQt6.QtCore import Qt
        
        app = QApplication(sys.argv)
        
        window = QMainWindow()
        window.setWindowTitle("Rexus.app - Modo Básico")
        window.setGeometry(100, 100, 600, 400)
        
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        
        label = QLabel("Rexus.app - Modo Básico\n\nAlgunos módulos no están disponibles.")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 18px; padding: 50px;")
        
        layout.addWidget(label)
        window.setCentralWidget(central_widget)
        
        window.show()
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Error en modo básico: {e}")
        run_emergency_mode()

def run_emergency_mode():
    """Modo de emergencia cuando todo falla."""
    print("=== MODO DE EMERGENCIA ===")
    print("La aplicación no puede iniciarse normalmente.")
    print("\nPosibles soluciones:")
    print("1. Instalar dependencias: pip install PyQt6")
    print("2. Verificar estructura de archivos")
    print("3. Contactar al administrador")
    print("\nPresiona Enter para salir...")
    input()

if __name__ == "__main__":
    main()