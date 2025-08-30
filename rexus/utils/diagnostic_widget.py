"""
Widget de Diagnóstico para Módulos de Rexus.app

Muestra información detallada sobre errores de carga de módulos
y proporciona soluciones específicas para cada tipo de problema.
"""

import logging
import sys
import traceback
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

try:
    from PyQt6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
        QTextEdit, QFrame, QScrollArea, QGroupBox
    )
    from PyQt6.QtCore import pyqtSignal
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False


class DiagnosticWidget(QWidget):
    """Widget para mostrar diagnósticos de errores de módulos."""

    retry_requested = pyqtSignal(str)  # Emite el nombre del módulo para reintentar

    def __init__(self, module_name: str, error_info: Dict[str, Any]):
        super().__init__()
        self.module_name = module_name
        self.error_info = error_info
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        self.setWindowTitle(f"Diagnóstico - Módulo {self.module_name}")
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout(self)

        # Título
        title_label = QLabel(f"🔍 Error en Módulo: {self.module_name}")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #d32f2f;")
        layout.addWidget(title_label)

        # Información del error
        error_group = QGroupBox("Información del Error")
        error_layout = QVBoxLayout()

        error_text = QTextEdit()
        error_text.setPlainText(self.error_info.get("error", "Error desconocido"))
        error_text.setMaximumHeight(100)
        error_layout.addWidget(error_text)

        error_group.setLayout(error_layout)
        layout.addWidget(error_group)

        # Diagnósticos
        diagnostics_group = QGroupBox("Diagnósticos Automáticos")
        diagnostics_layout = QVBoxLayout()

        diagnostics = self.run_diagnostics()
        for diag in diagnostics:
            diag_label = QLabel(f"• {diag['description']}: {diag['status']}")
            diagnostics_layout.addWidget(diag_label)

        diagnostics_group.setLayout(diagnostics_layout)
        layout.addWidget(diagnostics_group)

        # Soluciones sugeridas
        solutions_group = QGroupBox("Soluciones Sugeridas")
        solutions_layout = QVBoxLayout()

        solutions = self.generate_solutions()
        for solution in solutions:
            solution_frame = QFrame()
            solution_frame.setFrameStyle(QFrame.Shape.Box)
            solution_layout = QVBoxLayout(solution_frame)

            title_label = QLabel(f"💡 {solution['title']}")
            title_label.setStyleSheet("font-weight: bold;")
            solution_layout.addWidget(title_label)

            desc_label = QLabel(solution['description'])
            desc_label.setWordWrap(True)
            solution_layout.addWidget(desc_label)

            if 'command' in solution:
                cmd_label = QLabel(f"Comando: {solution['command']}")
                cmd_label.setStyleSheet("font-family: monospace; background-color: #f5f5f5; padding: 5px;")
                solution_layout.addWidget(cmd_label)

            solutions_layout.addWidget(solution_frame)

        solutions_group.setLayout(solutions_layout)

        # Scroll area para soluciones
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_widget.setLayout(solutions_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(200)

        layout.addWidget(scroll_area)

        # Botones de acción
        self.create_action_buttons(layout)

    def run_diagnostics(self) -> List[Dict[str, str]]:
        """Ejecuta diagnósticos automáticos."""
        diagnostics = []

        # Verificar archivos requeridos
        module_path = Path(f"rexus/modules/{self.module_name}")
        if module_path.exists():
            diagnostics.append({
                "description": "Estructura del módulo",
                "status": "✅ OK"
            })
        else:
            diagnostics.append({
                "description": "Estructura del módulo",
                "status": "❌ Faltante"
            })

        # Verificar archivos específicos
        required_files = ["__init__.py", "controller.py", "model.py", "view.py"]
        for file_name in required_files:
            file_path = module_path / file_name
            if file_path.exists():
                diagnostics.append({
                    "description": f"Archivo {file_name}",
                    "status": "✅ OK"
                })
            else:
                diagnostics.append({
                    "description": f"Archivo {file_name}",
                    "status": "❌ Faltante"
                })

        return diagnostics

    def generate_solutions(self) -> List[Dict[str, str]]:
        """Genera soluciones basadas en el error."""
        solutions = []
        error_msg = self.error_info.get("error", "").lower()

        # Soluciones específicas por tipo de error
        if ("importerror" in error_msg
            or "name" in error_msg
            and "not defined" in error_msg):
            solutions.append({
                "title": "Corregir imports de autenticación",
                "description": "Los decoradores de autenticación no están importados correctamente.",
                "command": "python corregir_decoradores.py",
            })

        if "syntaxerror" in error_msg or "invalid syntax" in error_msg:
            solutions.append({
                "title": "Corregir errores de sintaxis",
                "description": "Hay errores de sintaxis en el código Python.",
                "command": "python corregir_sintaxis.py",
            })

        if "unterminated" in error_msg:
            solutions.append({
                "title": "Corregir strings mal terminados",
                "description": "Hay cadenas de texto o f-strings mal cerrados.",
                "command": "Buscar y corregir comillas no cerradas en el archivo",
            })

        # Soluciones generales
        solutions.extend([
            {
                "title": "Verificar estructura del módulo",
                "description": "Asegurar que todos los archivos requeridos existen.",
                "command": f"ls -la rexus/modules/{self.module_name}/",
            },
            {
                "title": "Ejecutar tests del módulo",
                "description": "Verificar que el módulo pasa todas las pruebas.",
                "command": f"python -m pytest tests/{self.module_name}/ -v",
            },
            {
                "title": "Reiniciar la aplicación",
                "description": "A veces un reinicio puede resolver problemas temporales.",
                "command": "Reiniciar Rexus.app",
            },
        ])

        return solutions

    def create_action_buttons(self, parent_layout):
        """Crea los botones de acción."""
        if not PYQT_AVAILABLE:
            return

        buttons_layout = QHBoxLayout()

        # Botón de reintentar
        retry_btn = QPushButton("🔄 Reintentar Carga")
        retry_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976d2;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
        """)
        retry_btn.clicked.connect(lambda: self.retry_requested.emit(self.module_name))

        # Botón de ejecutar correcciones automáticas
        auto_fix_btn = QPushButton("[TOOL] Corrección Automática")
        auto_fix_btn.setStyleSheet("""
            QPushButton {
                background-color: #388e3c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2e7d32;
            }
            QPushButton:pressed {
                background-color: #1b5e20;
            }
        """)
        auto_fix_btn.clicked.connect(self.run_auto_fix)

        # Botón de reportar error
        report_btn = QPushButton("📋 Reportar Error")
        report_btn.setStyleSheet("""
            QPushButton {
                background-color: #f57c00;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ef6c00;
            }
            QPushButton:pressed {
                background-color: #e65100;
            }
        """)
        report_btn.clicked.connect(self.report_error)

        buttons_layout.addWidget(retry_btn)
        buttons_layout.addWidget(auto_fix_btn)
        buttons_layout.addWidget(report_btn)
        buttons_layout.addStretch()

        parent_layout.addLayout(buttons_layout)

    def run_auto_fix(self):
        """Ejecuta correcciones automáticas."""
        try:
            # Aquí iría la lógica de corrección automática
            logger.info(f"Ejecutando correcciones automáticas para el módulo {self.module_name}")

            # Ejecutar scripts de corrección
            # Cambiar al directorio raíz
            os.chdir(Path(__file__).parent.parent.parent)

            # Ejecutar corrección de decoradores
            result1 = subprocess.run(
                [sys.executable, "corregir_decoradores.py"],
                capture_output=True,
                text=True,
                shell=False,
                check=False
            )

            # Ejecutar corrección de sintaxis
            result2 = subprocess.run(
                [sys.executable, "corregir_sintaxis.py"],
                capture_output=True,
                text=True,
                shell=False,
                check=False
            )

            if result1.returncode == 0 and result2.returncode == 0:
                logger.info("Correcciones automáticas completadas")
                self.retry_requested.emit(self.module_name)
            else:
                logger.error(f"Algunas correcciones fallaron: {result1.stderr} {result2.stderr}")

        except Exception as e:
            logger.error(f"Error ejecutando correcciones automáticas: {e}")

    def report_error(self):
        """Genera un reporte detallado del error."""
        try:
            report_content = f"""
=== REPORTE DE ERROR DEL MÓDULO {self.module_name.upper()} ===
Fecha: {__import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Sistema: {sys.platform}
Python: {sys.version}

ERROR PRINCIPAL:
{self.error_info.get("error", "N/A")}

TRACEBACK:
{self.error_info.get("traceback", "N/A")}

DIAGNÓSTICOS:
{chr(10).join([f"- {d['description']}: {d['status']}" for d in self.run_diagnostics()])}

ARCHIVOS INVOLUCRADOS:
- rexus/modules/{self.module_name}/model.py
- rexus/modules/{self.module_name}/view.py
- rexus/modules/{self.module_name}/controller.py
            """.strip()

            # Guardar reporte
            report_file = Path(
                f"error_report_{self.module_name}_{__import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            )
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(report_content)

            logger.info(f"Reporte de error guardado en: {report_file.absolute()}")

        except Exception as e:
            logger.error(f"Error generando reporte: {e}")


def create_diagnostic_widget(
    module_name: str, error: Exception, traceback_str: str | None = None
):
    """
    Función helper para crear un widget de diagnóstico.

    Args:
        module_name: Nombre del módulo que falló
        error: Excepción que causó el fallo
        traceback_str: Traceback completo (opcional)

    Returns:
        DiagnosticWidget configurado
    """
    error_info = {
        "error": str(error),
        "type": type(error).__name__,
        "traceback": traceback_str or traceback.format_exc(),
    }

    return DiagnosticWidget(module_name, error_info)
