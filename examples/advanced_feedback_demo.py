#!/usr/bin/env python3
"""
Demo de Componentes Avanzados de Feedback - Rexus.app
Versión: 2.0.0 - Enterprise Ready

Demostración completa de todos los componentes de feedback visual
integrados con el sistema de temas.
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QGroupBox, QGridLayout, QComboBox, QLabel, QSpacerItem,
    QSizePolicy
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont

from rexus.ui.feedback_mixin import FeedbackWidget
from rexus.utils.theme_manager import ThemeManager
from rexus.core.themes import get_available_themes


class AdvancedFeedbackDemo(FeedbackWidget):
    """Demo completa de componentes avanzados de feedback."""
    
    def __init__(self, theme_manager: ThemeManager):
        super().__init__(theme_manager)
        
        self.theme_manager = theme_manager
        self.progress_value = 0
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self.update_progress_demo)
        
        self.init_ui()
        
    def init_ui(self):
        """Inicializar la interfaz de usuario."""
        self.setWindowTitle("Demo - Componentes Avanzados de Feedback")
        self.setMinimumSize(900, 700)
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Header con selector de tema
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Grid de demos
        demos_layout = QGridLayout()
        
        # Sección 1: Spinners y Loading
        loading_group = self.create_loading_demo_group()
        demos_layout.addWidget(loading_group, 0, 0)
        
        # Sección 2: Progress Bars
        progress_group = self.create_progress_demo_group()
        demos_layout.addWidget(progress_group, 0, 1)
        
        # Sección 3: Toast Notifications
        toast_group = self.create_toast_demo_group()
        demos_layout.addWidget(toast_group, 1, 0)
        
        # Sección 4: Status Indicators
        status_group = self.create_status_demo_group()
        demos_layout.addWidget(status_group, 1, 1)
        
        main_layout.addLayout(demos_layout)
        
        # Sección 5: Loading Overlays (ocupa todo el ancho)
        overlay_group = self.create_overlay_demo_group()
        main_layout.addWidget(overlay_group)
        
        # Status bar con múltiples indicadores
        status_bar = self.create_status_bar()
        main_layout.addWidget(status_bar)
        
        # Spacer
        main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
    
    def create_header(self):
        """Crear header con selector de tema."""
        header = QGroupBox("🎨 Control de Temas y Demo")
        layout = QHBoxLayout(header)
        
        # Selector de tema
        layout.addWidget(QLabel("Tema:"))
        
        self.theme_combo = QComboBox()
        themes = get_available_themes()
        self.theme_combo.addItems(themes)
        self.theme_combo.setCurrentText(self.theme_manager.current_theme_name)
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        layout.addWidget(self.theme_combo)
        
        layout.addStretch()
        
        # Info
        info_label = QLabel("[ROCKET] Demo completa de componentes de feedback integrados con temas")
        info_label.setStyleSheet("font-weight: bold; color: #666;")
        layout.addWidget(info_label)
        
        return header
        
    def create_loading_demo_group(self):
        """Crear grupo de demos de loading y spinners."""
        group = QGroupBox("🔄 Spinners y Loading")
        layout = QVBoxLayout(group)
        
        # Crear componentes
        self.spinner_main = self.crear_spinner("main")
        self.spinner_small = self.crear_spinner("small")
        
        # Layout de spinners
        spinners_layout = QHBoxLayout()
        
        spinner_container = QWidget()
        spinner_container.setFixedHeight(60)
        spinner_container_layout = QVBoxLayout(spinner_container)
        spinner_container_layout.addWidget(self.spinner_main, 0, Qt.AlignmentFlag.AlignCenter)
        spinners_layout.addWidget(spinner_container)
        
        spinner_small_container = QWidget()
        spinner_small_container.setFixedHeight(60)
        spinner_small_container_layout = QVBoxLayout(spinner_small_container)
        spinner_small_container_layout.addWidget(self.spinner_small, 0, Qt.AlignmentFlag.AlignCenter)
        spinners_layout.addWidget(spinner_small_container)
        
        layout.addLayout(spinners_layout)
        
        # Controles
        controls_layout = QHBoxLayout()
        
        start_btn = QPushButton("▶️ Iniciar")
        start_btn.clicked.connect(lambda: self.iniciar_spinner("main"))
        controls_layout.addWidget(start_btn)
        
        stop_btn = QPushButton("⏹️ Detener")
        stop_btn.clicked.connect(lambda: self.detener_spinner("main"))
        controls_layout.addWidget(stop_btn)
        
        layout.addLayout(controls_layout)
        
        return group
    
    def create_progress_demo_group(self):
        """Crear grupo de demos de progress bars."""
        group = QGroupBox("[CHART] Progress Bars")
        layout = QVBoxLayout(group)
        
        # Crear progress bars
        self.progress_bar = self.crear_progress_bar("main")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        self.progress_bar_secondary = self.crear_progress_bar("secondary")
        self.progress_bar_secondary.setRange(0, 100)
        self.progress_bar_secondary.setValue(50)
        layout.addWidget(self.progress_bar_secondary)
        
        # Controles
        controls_layout = QHBoxLayout()
        
        start_progress_btn = QPushButton("[ROCKET] Simular Progreso")
        start_progress_btn.clicked.connect(self.start_progress_demo)
        controls_layout.addWidget(start_progress_btn)
        
        reset_btn = QPushButton("🔄 Reset")
        reset_btn.clicked.connect(self.reset_progress)
        controls_layout.addWidget(reset_btn)
        
        layout.addLayout(controls_layout)
        
        return group
    
    def create_toast_demo_group(self):
        """Crear grupo de demos de toast notifications."""
        group = QGroupBox("🍞 Toast Notifications")
        layout = QVBoxLayout(group)
        
        # Crear toast
        self.main_toast = self.crear_toast("main")
        
        # Controles
        controls_layout = QGridLayout()
        
        # Botones para diferentes tipos de toast
        toast_types = [
            ("ℹ️ Info", "info", "Información del sistema"),
            ("[CHECK] Success", "success", "Operación completada exitosamente"),
            ("[WARN] Warning", "warning", "Advertencia importante"),
            ("[ERROR] Error", "error", "Error crítico del sistema")
        ]
        
        for i, (btn_text, toast_type, message) in enumerate(toast_types):
            btn = QPushButton(btn_text)
            btn.clicked.connect(lambda checked, t=toast_type, m=message: self.mostrar_toast(m, t))
            controls_layout.addWidget(btn, i // 2, i % 2)
        
        layout.addLayout(controls_layout)
        
        return group
    
    def create_status_demo_group(self):
        """Crear grupo de demos de status indicators."""
        group = QGroupBox("🔘 Status Indicators")
        layout = QVBoxLayout(group)
        
        # Crear indicadores
        self.status_main = self.crear_status_indicator("main")
        self.status_secondary = self.crear_status_indicator("secondary")
        
        # Mostrar indicadores
        layout.addWidget(self.status_main)
        layout.addWidget(self.status_secondary)
        
        # Controles
        controls_layout = QGridLayout()
        
        status_types = [
            ("🟢 Activo", "active", "Sistema operativo"),
            ("🟡 Advertencia", "warning", "Recursos limitados"),
            ("🔴 Error", "error", "Fallo crítico"),
            ("⚫ Inactivo", "inactive", "Sistema pausado")
        ]
        
        for i, (btn_text, status_type, message) in enumerate(status_types):
            btn = QPushButton(btn_text)
            btn.clicked.connect(lambda checked, s=status_type, m=message: 
                              self.actualizar_status_indicator(s, m, "main"))
            controls_layout.addWidget(btn, i // 2, i % 2)
        
        layout.addLayout(controls_layout)
        
        return group
    
    def create_overlay_demo_group(self):
        """Crear grupo de demos de loading overlays."""
        group = QGroupBox("[LOCK] Loading Overlays")
        layout = QVBoxLayout(group)
        
        # Crear overlay
        self.main_overlay = self.crear_loading_overlay("main")
        
        # Área de contenido para demostrar el overlay
        content_area = QWidget()
        content_area.setFixedHeight(100)
        content_area.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
        """)
        
        content_layout = QVBoxLayout(content_area)
        content_label = QLabel("📄 Área de contenido que será cubierta por el overlay")
        content_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        content_layout.addWidget(content_label)
        
        layout.addWidget(content_area)
        
        # Controles
        controls_layout = QHBoxLayout()
        
        show_overlay_btn = QPushButton("[LOCK] Mostrar Overlay")
        show_overlay_btn.clicked.connect(lambda: self.mostrar_loading_overlay("Procesando datos..."))
        controls_layout.addWidget(show_overlay_btn)
        
        hide_overlay_btn = QPushButton("🔓 Ocultar Overlay")  
        hide_overlay_btn.clicked.connect(lambda: self.ocultar_loading_overlay())
        controls_layout.addWidget(hide_overlay_btn)
        
        auto_demo_btn = QPushButton("⏰ Demo Automático (5s)")
        auto_demo_btn.clicked.connect(self.demo_auto_overlay)
        controls_layout.addWidget(auto_demo_btn)
        
        layout.addLayout(controls_layout)
        
        return group
    
    def create_status_bar(self):
        """Crear barra de estado con múltiples indicadores."""
        status_bar = QGroupBox("[CHART] Barra de Estado del Sistema")
        layout = QHBoxLayout(status_bar)
        
        # Crear múltiples indicadores
        self.status_db = self.crear_status_indicator("database")
        self.status_network = self.crear_status_indicator("network")
        self.status_cpu = self.crear_status_indicator("cpu")
        
        # Configurar estados iniciales
        self.actualizar_status_indicator("active", "Conectado", "database")
        self.actualizar_status_indicator("active", "En línea", "network") 
        self.actualizar_status_indicator("warning", "Alto uso", "cpu")
        
        layout.addWidget(QLabel("BD:"))
        layout.addWidget(self.status_db)
        layout.addWidget(QLabel("Red:"))
        layout.addWidget(self.status_network)
        layout.addWidget(QLabel("CPU:"))
        layout.addWidget(self.status_cpu)
        
        layout.addStretch()
        
        # Botón para simular cambios
        simulate_btn = QPushButton("🎲 Simular Cambios")
        simulate_btn.clicked.connect(self.simulate_status_changes)
        layout.addWidget(simulate_btn)
        
        return status_bar
    
    def change_theme(self, theme_name: str):
        """Cambiar tema de la aplicación."""
        if self.theme_manager:
            self.theme_manager.set_theme(theme_name)
            self.mostrar_toast(f"Tema cambiado a: {theme_name}", "info")
    
    def start_progress_demo(self):
        """Iniciar demo de progreso."""
        self.progress_value = 0
        self.progress_timer.start(100)  # Actualizar cada 100ms
        
        self.mostrar_toast("Iniciando simulación de progreso", "info")
    
    def update_progress_demo(self):
        """Actualizar progreso de la demo."""
        self.progress_value += 2
        self.actualizar_progress(self.progress_value, "main")
        
        if self.progress_value >= 100:
            self.progress_timer.stop()
            self.mostrar_toast("Progreso completado", "success")
    
    def reset_progress(self):
        """Resetear progress bars."""
        self.progress_timer.stop()
        self.progress_value = 0
        self.actualizar_progress(0, "main")
        self.actualizar_progress(50, "secondary")
        
        self.mostrar_toast("Progress bars reseteadas", "info")
    
    def demo_auto_overlay(self):
        """Demo automático del overlay."""
        self.mostrar_loading_overlay("Demo automático en progreso...")
        
        # Ocultar después de 5 segundos
        QTimer.singleShot(5000, lambda: (
            self.ocultar_loading_overlay(),
            self.mostrar_toast("Demo automático completado", "success")
        ))
    
    def simulate_status_changes(self):
        """Simular cambios en los indicadores de estado."""
        import random
        
        statuses = ["active", "warning", "error", "inactive"]
        messages = {
            "active": ["Operativo", "En línea", "Funcionando"],
            "warning": ["Recursos limitados", "Latencia alta", "Carga elevada"],
            "error": ["Desconectado", "Error crítico", "Fallo del sistema"],
            "inactive": ["Pausado", "Mantenimiento", "Inactivo"]
        }
        
        # Cambiar cada indicador aleatoriamente
        for indicator_name in ["database", "network", "cpu"]:
            status = random.choice(statuses)
            message = random.choice(messages[status])
            self.actualizar_status_indicator(status, message, indicator_name)
        
        self.mostrar_toast("Estados actualizados aleatoriamente", "info")


class MainWindow(QMainWindow):
    """Ventana principal de la demo."""
    
    def __init__(self):
        super().__init__()
        
        # Inicializar theme manager
        self.theme_manager = ThemeManager()
        
        # Widget central
        self.demo_widget = AdvancedFeedbackDemo(self.theme_manager)
        self.setCentralWidget(self.demo_widget)
        
        # Configurar ventana
        self.setWindowTitle("Rexus.app - Demo Componentes Avanzados de Feedback")
        self.setMinimumSize(1000, 800)
        
        # Aplicar fuente del sistema
        font = QFont("Segoe UI", 9)
        self.setFont(font)


def main():
    """Función principal."""
    app = QApplication(sys.argv)
    
    # Configurar aplicación
    app.setApplicationName("Rexus Advanced Feedback Demo")
    app.setApplicationVersion("2.0.0")
    
    # Crear y mostrar ventana principal
    window = MainWindow()
    window.show()
    
    # Mensaje de bienvenida
    QTimer.singleShot(1000, lambda: window.demo_widget.mostrar_toast(
        "¡Bienvenido a la demo de componentes avanzados!", "success", 5000
    ))
    
    # Ejecutar aplicación
    sys.exit(app.exec())


if __name__ == "__main__":
    main()