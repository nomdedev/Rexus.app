"""
Widget de Diagnóstico para Módulos de Rexus.app

Muestra información detallada sobre errores de carga de módulos
y proporciona soluciones específicas para cada tipo de problema.
"""


import logging
logger = logging.getLogger(__name__)

import sys
import traceback
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
            from rexus.utils.dialogs import show_info

            show_info(
                ,
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
                    ,
                    f"Algunas correcciones fallaron:\n{result1.stderr}\n{result2.stderr}",
                )

        except Exception as e:
            from rexus.utils.dialogs import show_error

            show_error(, f"Error ejecutando correcciones automáticas: {e}")

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
                ,
                f"Reporte de error guardado en:\n{report_file.absolute()}",
            )

        except Exception as e:
            from rexus.utils.dialogs import show_error

            show_error(, f"Error generando reporte: {e}")


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
