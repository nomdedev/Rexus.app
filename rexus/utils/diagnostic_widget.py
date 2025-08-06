"""
Widget de Diagnóstico para Módulos de Rexus.app

Muestra información detallada sobre errores de carga de módulos
y proporciona soluciones específicas para cada tipo de problema.
"""

import sys
import traceback
from pathlib import Path

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class DiagnosticWidget(QWidget):
    """Widget que muestra diagnósticos detallados de errores de módulos."""

    retry_requested = pyqtSignal(str)  # Señal para reintentar carga del módulo

    def __init__(self, module_name: str, error_info: dict):
        # Solo inicializar QWidget si hay una aplicación Qt activa
        try:
            from PyQt6.QtWidgets import QApplication

            if QApplication.instance() is not None:
                super().__init__()
                self.qt_initialized = True
            else:
                # No hay aplicación Qt, crear como objeto Python normal
                self.qt_initialized = False
        except:
            self.qt_initialized = False

        self.module_name = module_name
        self.error_info = error_info

        if self.qt_initialized:
            self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz de diagnóstico."""
        if not self.qt_initialized:
            return

        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)  # Header con ícono de error
        header_layout = QHBoxLayout()

        # Ícono de error (usando emoji como fallback)
        icon_label = QLabel("⚠️")
        icon_label.setStyleSheet("font-size: 48px;")
        header_layout.addWidget(icon_label)

        # Título del error
        title_layout = QVBoxLayout()
        title = QLabel(f"Error en Módulo: {self.module_name.title()}")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #d32f2f;
                margin-bottom: 5px;
            }
        """)

        subtitle = QLabel("El módulo no pudo cargarse correctamente")
        subtitle.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #666;
            }
        """)

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        # Información del error
        self.create_error_section(layout)

        # Diagnóstico automático
        self.create_diagnostic_section(layout)

        # Soluciones sugeridas
        self.create_solutions_section(layout)

        # Botones de acción
        self.create_action_buttons(layout)

        layout.addStretch()

    def create_error_section(self, parent_layout):
        """Crea la sección de información del error."""
        error_group = QGroupBox("📋 Información del Error")
        error_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

        error_layout = QVBoxLayout(error_group)

        # Error principal
        error_msg = self.error_info.get("error", "Error desconocido")
        error_label = QLabel(f"Error: {error_msg}")
        error_label.setStyleSheet("""
            QLabel {
                background-color: #ffebee;
                border: 1px solid #ffcdd2;
                border-radius: 4px;
                padding: 8px;
                color: #c62828;
                font-family: 'Consolas', 'Monaco', monospace;
            }
        """)
        error_label.setWordWrap(True)
        error_layout.addWidget(error_label)

        # Traceback si está disponible
        if "traceback" in self.error_info:
            traceback_text = QTextEdit()
            traceback_text.setPlainText(self.error_info["traceback"])
            traceback_text.setMaximumHeight(100)
            traceback_text.setStyleSheet("""
                QTextEdit {
                    background-color: #f5f5f5;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    font-family: 'Consolas', 'Monaco', monospace;
                    font-size: 9px;
                }
            """)
            error_layout.addWidget(QLabel("Traceback detallado:"))
            error_layout.addWidget(traceback_text)

        parent_layout.addWidget(error_group)

    def create_diagnostic_section(self, parent_layout):
        """Crea la sección de diagnóstico automático."""
        diagnostic_group = QGroupBox("🔍 Diagnóstico Automático")
        diagnostic_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

        diagnostic_layout = QVBoxLayout(diagnostic_group)

        # Ejecutar diagnósticos
        diagnostics = self.run_diagnostics()

        for diagnostic in diagnostics:
            status_icon = (
                "✅"
                if diagnostic["status"] == "ok"
                else "❌"
                if diagnostic["status"] == "error"
                else "⚠️"
            )
            diagnostic_label = QLabel(f"{status_icon} {diagnostic['description']}")

            if diagnostic["status"] == "error":
                diagnostic_label.setStyleSheet("color: #d32f2f; font-weight: bold;")
            elif diagnostic["status"] == "warning":
                diagnostic_label.setStyleSheet("color: #f57c00; font-weight: bold;")
            else:
                diagnostic_label.setStyleSheet("color: #388e3c;")

            diagnostic_layout.addWidget(diagnostic_label)

            if diagnostic.get("details"):
                details_label = QLabel(f"   → {diagnostic['details']}")
                details_label.setStyleSheet(
                    "color: #666; font-size: 11px; margin-left: 20px;"
                )
                diagnostic_layout.addWidget(details_label)

        parent_layout.addWidget(diagnostic_group)

    def run_diagnostics(self):
        """Ejecuta diagnósticos automáticos del módulo."""
        diagnostics = []

        # 1. Verificar archivos del módulo
        module_path = Path(f"rexus/modules/{self.module_name}")
        required_files = ["__init__.py", "model.py", "view.py", "controller.py"]

        for file in required_files:
            file_path = module_path / file
            if file_path.exists():
                diagnostics.append(
                    {
                        "status": "ok",
                        "description": f"Archivo {file} encontrado",
                        "details": str(file_path),
                    }
                )
            else:
                diagnostics.append(
                    {
                        "status": "error",
                        "description": f"Archivo {file} faltante",
                        "details": f"Se esperaba en: {file_path}",
                    }
                )

        # 2. Verificar sintaxis de archivos Python
        for file in ["model.py", "view.py", "controller.py"]:
            file_path = module_path / file
            if file_path.exists():
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    compile(content, str(file_path), "exec")
                    diagnostics.append(
                        {"status": "ok", "description": f"Sintaxis de {file} correcta"}
                    )
                except SyntaxError as e:
                    diagnostics.append(
                        {
                            "status": "error",
                            "description": f"Error de sintaxis en {file}",
                            "details": f"Línea {e.lineno}: {e.msg}",
                        }
                    )
                except Exception as e:
                    diagnostics.append(
                        {
                            "status": "warning",
                            "description": f"No se pudo verificar {file}",
                            "details": str(e),
                        }
                    )

        # 3. Verificar imports principales
        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                f"rexus.modules.{self.module_name}.model", module_path / "model.py"
            )
            if spec and spec.loader:
                diagnostics.append({"status": "ok", "description": "Modelo importable"})
            else:
                diagnostics.append(
                    {"status": "error", "description": "Modelo no importable"}
                )
        except Exception as e:
            diagnostics.append(
                {
                    "status": "error",
                    "description": "Error importando modelo",
                    "details": str(e),
                }
            )

        # 4. Verificar dependencias
        error_msg = self.error_info.get("error", "")
        if "ModuleNotFoundError" in error_msg:
            missing_module = (
                error_msg.split("'")[1] if "'" in error_msg else "desconocido"
            )
            diagnostics.append(
                {
                    "status": "error",
                    "description": f"Dependencia faltante: {missing_module}",
                    "details": "Ejecutar: pip install " + missing_module,
                }
            )

        if "auth_required" in error_msg:
            diagnostics.append(
                {
                    "status": "error",
                    "description": "Error en decoradores de autenticación",
                    "details": "Verificar imports de rexus.core.auth_manager",
                }
            )

        return diagnostics

    def create_solutions_section(self, parent_layout):
        """Crea la sección de soluciones sugeridas."""
        solutions_group = QGroupBox("🔧 Soluciones Sugeridas")
        solutions_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ddd;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

        solutions_layout = QVBoxLayout(solutions_group)

        # Generar soluciones basadas en el error
        solutions = self.generate_solutions()

        for i, solution in enumerate(solutions, 1):
            solution_label = QLabel(f"{i}. {solution['title']}")
            solution_label.setStyleSheet("font-weight: bold; color: #1976d2;")
            solutions_layout.addWidget(solution_label)

            if solution.get("description"):
                desc_label = QLabel(f"   {solution['description']}")
                desc_label.setStyleSheet("color: #666; margin-left: 15px;")
                desc_label.setWordWrap(True)
                solutions_layout.addWidget(desc_label)

            if solution.get("command"):
                cmd_label = QLabel(f"   Comando: {solution['command']}")
                cmd_label.setStyleSheet("""
                    background-color: #f5f5f5;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    padding: 4px;
                    margin-left: 15px;
                    font-family: 'Consolas', 'Monaco', monospace;
                """)
                solutions_layout.addWidget(cmd_label)

        parent_layout.addWidget(solutions_group)

    def generate_solutions(self):
        """Genera soluciones basadas en el tipo de error."""
        solutions = []
        error_msg = self.error_info.get("error", "").lower()

        if "modulenotfounderror" in error_msg:
            solutions.append(
                {
                    "title": "Instalar dependencias faltantes",
                    "description": "Algunas librerías requeridas no están instaladas.",
                    "command": "pip install -r requirements.txt",
                }
            )

        if (
            "auth_required" in error_msg
            or "name" in error_msg
            and "not defined" in error_msg
        ):
            solutions.append(
                {
                    "title": "Corregir imports de autenticación",
                    "description": "Los decoradores de autenticación no están importados correctamente.",
                    "command": "python corregir_decoradores.py",
                }
            )

        if "syntaxerror" in error_msg or "invalid syntax" in error_msg:
            solutions.append(
                {
                    "title": "Corregir errores de sintaxis",
                    "description": "Hay errores de sintaxis en el código Python.",
                    "command": "python corregir_sintaxis.py",
                }
            )

        if "unterminated" in error_msg:
            solutions.append(
                {
                    "title": "Corregir strings mal terminados",
                    "description": "Hay cadenas de texto o f-strings mal cerrados.",
                    "command": "Buscar y corregir comillas no cerradas en el archivo",
                }
            )

        # Soluciones generales
        solutions.extend(
            [
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
            ]
        )

        return solutions

    def create_action_buttons(self, parent_layout):
        """Crea los botones de acción."""
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
        auto_fix_btn = QPushButton("🔧 Corrección Automática")
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
            from rexus.utils.dialogs import show_info

            show_info(
                "Corrección Automática",
                f"Ejecutando correcciones automáticas para el módulo {self.module_name}...\n\n"
                "Esto puede tardar unos momentos.",
            )

            # Ejecutar scripts de corrección
            import os
            import subprocess

            # Cambiar al directorio raíz
            os.chdir(Path(__file__).parent.parent.parent)

            # Ejecutar corrección de decoradores
            result1 = subprocess.run(
                [sys.executable, "corregir_decoradores.py"],
                capture_output=True,
                text=True,
            )

            # Ejecutar corrección de sintaxis
            result2 = subprocess.run(
                [sys.executable, "corregir_sintaxis.py"], capture_output=True, text=True
            )

            if result1.returncode == 0 and result2.returncode == 0:
                show_info(
                    "Éxito",
                    "Correcciones automáticas completadas. Reintentando carga del módulo...",
                )
                self.retry_requested.emit(self.module_name)
            else:
                from rexus.utils.dialogs import show_error

                show_error(
                    "Error en Corrección",
                    f"Algunas correcciones fallaron:\n{result1.stderr}\n{result2.stderr}",
                )

        except Exception as e:
            from rexus.utils.dialogs import show_error

            show_error("Error", f"Error ejecutando correcciones automáticas: {e}")

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

            from rexus.utils.dialogs import show_info

            show_info(
                "Reporte Generado",
                f"Reporte de error guardado en:\n{report_file.absolute()}",
            )

        except Exception as e:
            from rexus.utils.dialogs import show_error

            show_error("Error", f"Error generando reporte: {e}")


def create_diagnostic_widget(
    module_name: str, error: Exception, traceback_str: str = None
) -> DiagnosticWidget:
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
