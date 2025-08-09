#!/usr/bin/env python3
"""
Test script para verificar las correcciones de tema críticas.

Este script prueba:
1. Detección automática de tema del sistema
2. Aplicación de correcciones críticas para formularios
3. Tema de emergencia claro cuando es necesario
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QLineEdit, QComboBox, QTextEdit, QLabel, QPushButton,
    QSpinBox, QDateEdit, QHBoxLayout
)
from PyQt6.QtCore import QDate

try:
    from rexus.ui.style_manager import StyleManager
    style_manager_available = True
    print("[TEST] ✓ StyleManager importado correctamente")
except ImportError as e:
    print(f"[TEST] ✗ Error importando StyleManager: {e}")
    style_manager_available = False

class ThemeTestWindow(QMainWindow):
    """Ventana de prueba para temas."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test de Correcciones de Tema - Rexus.app")
        self.setGeometry(100, 100, 800, 600)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Título
        title = QLabel("🔍 Test de Correcciones Críticas de Tema")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Información del tema
        self.theme_info = QLabel()
        layout.addWidget(self.theme_info)
        
        # Sección de formularios de prueba
        form_section = QLabel("📝 Formularios de Prueba (deben ser legibles)")
        form_section.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px 0;")
        layout.addWidget(form_section)
        
        # Crear formularios de prueba
        self.create_test_forms(layout)
        
        # Botones de control de tema
        self.create_theme_controls(layout)
        
        # Inicializar StyleManager si está disponible
        if style_manager_available:
            self.style_manager = StyleManager()
            self.update_theme_info()
            # Aplicar tema automático
            self.style_manager.apply_global_theme()
        else:
            self.style_manager = None
            self.theme_info.setText("⚠ StyleManager no disponible")
    
    def create_test_forms(self, layout):
        """Crea formularios de prueba."""
        # Row 1: Campos de texto
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Texto:"))
        self.line_edit = QLineEdit("Texto de prueba")
        row1.addWidget(self.line_edit)
        
        row1.addWidget(QLabel("Número:"))
        self.spin_box = QSpinBox()
        self.spin_box.setValue(42)
        row1.addWidget(self.spin_box)
        layout.addLayout(row1)
        
        # Row 2: ComboBox y fecha
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Opción:"))
        self.combo_box = QComboBox()
        self.combo_box.addItems(["Opción 1", "Opción 2", "Opción 3"])
        row2.addWidget(self.combo_box)
        
        row2.addWidget(QLabel("Fecha:"))
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        row2.addWidget(self.date_edit)
        layout.addLayout(row2)
        
        # Área de texto
        layout.addWidget(QLabel("Texto largo:"))
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText("Este es un texto de prueba más largo.\n¿Se puede leer correctamente?\n\nEsta es la línea más importante para probar la legibilidad.")
        self.text_edit.setMaximumHeight(100)
        layout.addWidget(self.text_edit)
    
    def create_theme_controls(self, layout):
        """Crea controles para probar temas."""
        if not style_manager_available:
            return
            
        controls_section = QLabel("🎨 Controles de Tema")
        controls_section.setStyleSheet("font-size: 14px; font-weight: bold; margin: 10px 0;")
        layout.addWidget(controls_section)
        
        buttons_layout = QHBoxLayout()
        
        # Botón para aplicar correcciones críticas
        btn_fix = QPushButton("🔧 Aplicar Correcciones Críticas")
        btn_fix.clicked.connect(self.apply_critical_fixes)
        buttons_layout.addWidget(btn_fix)
        
        # Botón para tema de emergencia claro
        btn_emergency = QPushButton("🚨 Tema de Emergencia Claro")
        btn_emergency.clicked.connect(self.apply_emergency_light)
        buttons_layout.addWidget(btn_emergency)
        
        # Botón para tema automático
        btn_auto = QPushButton("🔄 Detectar Tema Automático")
        btn_auto.clicked.connect(self.apply_auto_theme)
        buttons_layout.addWidget(btn_auto)
        
        layout.addLayout(buttons_layout)
        
        # Botones de temas específicos
        themes_layout = QHBoxLayout()
        for theme in ['light', 'dark', 'professional']:
            btn_theme = QPushButton(f"Tema {theme.title()}")
            btn_theme.clicked.connect(lambda checked, t=theme: self.apply_specific_theme(t))
            themes_layout.addWidget(btn_theme)
        
        layout.addLayout(themes_layout)
    
    def update_theme_info(self):
        """Actualiza la información del tema actual."""
        if not self.style_manager:
            return
            
        current_theme = self.style_manager.get_current_theme()
        available_themes = self.style_manager.get_available_themes()
        
        info_text = f"""
        🎨 <b>Tema Actual:</b> {current_theme}
        📋 <b>Temas Disponibles:</b> {', '.join(available_themes)}
        🖥️ <b>Sistema:</b> {self.get_system_info()}
        """
        self.theme_info.setText(info_text)
    
    def get_system_info(self):
        """Obtiene información del sistema."""
        import platform
        return f"{platform.system()} {platform.release()}"
    
    def apply_critical_fixes(self):
        """Aplica correcciones críticas de formularios."""
        if not self.style_manager:
            return
            
        success = self.style_manager.apply_critical_form_fixes()
        if success:
            print("[TEST] ✓ Correcciones críticas aplicadas")
            self.show_message("Correcciones Críticas", "Se han aplicado las correcciones críticas para mejorar la legibilidad de los formularios.")
        else:
            print("[TEST] ✗ Error aplicando correcciones críticas")
            self.show_message("Error", "No se pudieron aplicar las correcciones críticas.")
    
    def apply_emergency_light(self):
        """Aplica tema de emergencia claro."""
        if not self.style_manager:
            return
            
        success = self.style_manager.force_light_theme_for_forms()
        if success:
            print("[TEST] ✓ Tema de emergencia claro aplicado")
            self.show_message("Tema de Emergencia", "Se ha aplicado el tema de emergencia claro. Los formularios ahora deberían ser legibles independientemente del tema del sistema.")
        else:
            print("[TEST] ✗ Error aplicando tema de emergencia")
    
    def apply_auto_theme(self):
        """Aplica tema automático detectando el sistema."""
        if not self.style_manager:
            return
            
        # Re-detectar tema del sistema
        self.style_manager._detect_system_theme()
        success = self.style_manager.apply_global_theme()
        
        if success:
            current_theme = self.style_manager.get_current_theme()
            print(f"[TEST] ✓ Tema automático aplicado: {current_theme}")
            self.update_theme_info()
            self.show_message("Tema Automático", f"Se ha detectado y aplicado el tema '{current_theme}' basado en la configuración del sistema.")
        else:
            print("[TEST] ✗ Error aplicando tema automático")
    
    def apply_specific_theme(self, theme_name):
        """Aplica un tema específico."""
        if not self.style_manager:
            return
            
        success = self.style_manager.apply_global_theme(theme_name)
        if success:
            print(f"[TEST] ✓ Tema '{theme_name}' aplicado")
            self.update_theme_info()
            self.show_message("Tema Aplicado", f"Se ha aplicado el tema '{theme_name}'.")
        else:
            print(f"[TEST] ✗ Error aplicando tema '{theme_name}'")
            self.show_message("Error", f"No se pudo aplicar el tema '{theme_name}'.")
    
    def show_message(self, title, message):
        """Muestra un mensaje al usuario."""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, title, message)

def main():
    """Función principal del test."""
    print("=" * 60)
    print("🧪 TEST DE CORRECCIONES CRÍTICAS DE TEMA - REXUS.APP")
    print("=" * 60)
    
    app = QApplication(sys.argv)
    
    # Crear ventana de prueba
    window = ThemeTestWindow()
    window.show()
    
    print("\n📋 INSTRUCCIONES:")
    print("1. Verifica que los formularios sean legibles")
    print("2. Si están en negro/ilegibles, usa 'Aplicar Correcciones Críticas'")
    print("3. Si aún hay problemas, usa 'Tema de Emergencia Claro'")
    print("4. Prueba diferentes temas para verificar la compatibilidad")
    print("\n🔍 Observa la consola para mensajes de debug")
    print("=" * 60)
    
    # Ejecutar aplicación
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())