#!/usr/bin/env python3
"""
Script de prueba para verificar correcciones críticas de tema
Verifica que los formularios sean legibles con tema oscuro
"""

import sys
import os

# Agregar directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                            QWidget, QLabel, QLineEdit, QComboBox, QTextEdit,
                            QPushButton, QDateEdit, QSpinBox)
from PyQt6.QtCore import Qt

def test_theme_corrections():
    """Prueba las correcciones críticas de tema oscuro."""
    try:
        print("=== PRUEBA DE CORRECCIONES CRÍTICAS DE TEMA ===")

        # Importar StyleManager
        from rexus.ui.style_manager import StyleManager

        # Crear aplicación
        app = QApplication(sys.argv)

        # Crear ventana de prueba
        main_window = QMainWindow()
        main_window.setWindowTitle("Prueba de Correcciones de Tema - Rexus.app")
        main_window.setGeometry(100, 100, 800, 600)

        # Widget central
        central_widget = QWidget()
        main_window.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Título
        title = QLabel("PRUEBA DE FORMULARIOS CON TEMA OSCURO")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 20px;")
        layout.addWidget(title)

        # Crear formulario de prueba
        form_layout = QVBoxLayout()

        # Campo de texto
        layout_line = QHBoxLayout()
        layout_line.addWidget(QLabel("Campo de texto:"))
        line_edit = QLineEdit()
        line_edit.setPlaceholderText("Escribe aquí...")
        line_edit.setText("Texto de prueba")
        layout_line.addWidget(line_edit)
        form_layout.addLayout(layout_line)

        # ComboBox
        layout_combo = QHBoxLayout()
        layout_combo.addWidget(QLabel("Lista desplegable:"))
        combo_box = QComboBox()
        combo_box.addItems(["Opción 1", "Opción 2", "Opción 3"])
        layout_combo.addWidget(combo_box)
        form_layout.addLayout(layout_combo)

        # Área de texto
        layout_text = QVBoxLayout()
        layout_text.addWidget(QLabel("Área de texto:"))
        text_edit = QTextEdit()
        text_edit.setPlainText("Este es un texto de prueba en el área de texto.\n¿Es legible con tema oscuro?")
        text_edit.setMaximumHeight(100)
        layout_text.addWidget(text_edit)
        form_layout.addLayout(layout_text)

        # Campo numérico
        layout_spin = QHBoxLayout()
        layout_spin.addWidget(QLabel("Campo numérico:"))
        spin_box = QSpinBox()
        spin_box.setValue(42)
        layout_spin.addWidget(spin_box)
        form_layout.addLayout(layout_spin)

        # Campo de fecha
        layout_date = QHBoxLayout()
        layout_date.addWidget(QLabel("Campo de fecha:"))
        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        layout_date.addWidget(date_edit)
        form_layout.addLayout(layout_date)

        layout.addLayout(form_layout)

        # Botones de prueba
        button_layout = QHBoxLayout()

        btn_apply_dark = QPushButton("Aplicar Tema Oscuro")
        btn_apply_light = QPushButton("Aplicar Tema Claro")
        btn_apply_fixes = QPushButton("Aplicar Correcciones Críticas")

        button_layout.addWidget(btn_apply_dark)
        button_layout.addWidget(btn_apply_light)
        button_layout.addWidget(btn_apply_fixes)

        layout.addLayout(button_layout)

        # Información
        info_label = QLabel("""
INSTRUCCIONES DE PRUEBA:
1. Click en 'Aplicar Tema Oscuro' para probar el tema mejorado
2. Verifica que todos los campos sean legibles (texto claro sobre fondo oscuro)
3. Verifica que al enfocar campos el contraste mejore
4. Click en 'Aplicar Correcciones Críticas' si hay problemas
5. Los campos NUNCA deben ser negros sobre negro

PROBLEMA ORIGINAL: Formularios negros ilegibles con tema oscuro
SOLUCIÓN: Tema oscuro mejorado con contraste forzado (!important)
        """)
        info_label.setStyleSheet("background-color: #f0f0f0; padding: 15px; border-radius: 5px; margin: 10px;")
        layout.addWidget(info_label)

        # Instanciar StyleManager
        style_manager = StyleManager()

        def apply_dark_theme():
            print("\n[PRUEBA] Aplicando tema oscuro mejorado...")
            success = style_manager.apply_global_theme('dark')
            if success:
                print("✅ Tema oscuro aplicado exitosamente")
                status_label.setText("✅ Tema oscuro aplicado - Verifica legibilidad de campos")
                status_label.setStyleSheet("color: green; font-weight: bold;")
            else:
                print("❌ Error aplicando tema oscuro")
                status_label.setText("❌ Error aplicando tema oscuro")
                status_label.setStyleSheet("color: red; font-weight: bold;")

        def apply_light_theme():
            print("\n[PRUEBA] Aplicando tema claro...")
            success = style_manager.apply_global_theme('light')
            if success:
                print("✅ Tema claro aplicado exitosamente")
                status_label.setText("✅ Tema claro aplicado")
                status_label.setStyleSheet("color: green; font-weight: bold;")
            else:
                print("❌ Error aplicando tema claro")
                status_label.setText("❌ Error aplicando tema claro")
                status_label.setStyleSheet("color: red; font-weight: bold;")

        def apply_critical_fixes():
            print("\n[PRUEBA] Aplicando correcciones críticas...")
            success = style_manager.apply_critical_contrast_fixes()
            if success:
                print("✅ Correcciones críticas aplicadas")
                status_label.setText("✅ Correcciones críticas aplicadas - Formularios deben ser legibles")
                status_label.setStyleSheet("color: blue; font-weight: bold;")
            else:
                print("❌ Error aplicando correcciones críticas")
                status_label.setText("❌ Error en correcciones críticas")
                status_label.setStyleSheet("color: red; font-weight: bold;")

        # Conectar botones
        btn_apply_dark.clicked.connect(apply_dark_theme)
        btn_apply_light.clicked.connect(apply_light_theme)
        btn_apply_fixes.clicked.connect(apply_critical_fixes)

        # Label de estado
        status_label = QLabel("Haz click en los botones para probar los temas")
        status_label.setStyleSheet("font-size: 14px; padding: 10px; text-align: center;")
        layout.addWidget(status_label)

        # Aplicar tema oscuro por defecto para prueba
        print("\n[INIT] Aplicando tema oscuro por defecto...")
        style_manager.apply_global_theme('dark')

        # Mostrar ventana
        main_window.show()

        print("\n=== VENTANA DE PRUEBA INICIADA ===")
        print("✅ La aplicación de prueba está ejecutándose")
        print("📋 Verifica la legibilidad de todos los campos de formulario")
        print("🎯 Los campos NUNCA deben ser negros sobre negro")

        return app.exec()

    except Exception as e:
        print(f"❌ Error en prueba: {e}")
        import traceback
        traceback.print_exc()
        return -1

if __name__ == "__main__":
    sys.exit(test_theme_corrections())
