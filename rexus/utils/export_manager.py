"""
Sistema de Exportación Estándar - Rexus.app v2.0.0

Sistema unificado de exportación de datos para todos los módulos del sistema.
Soporta exportación a Excel, CSV y PDF con configuraciones personalizables.
"""

import logging
import os
            
            show_success(parent_widget, "Exportación Exitosa",
                        f"Datos exportados a CSV:\n{file_path}")
            return True

        except Exception as e:
            logging.error(f"Error exportando a CSV: {e}")
            show_error(parent_widget, "Error", f"Error exportando a CSV: {str(e)}")
            return False

    def _export_to_pdf(self,
data: List[Dict],
        headers: List[str],
        filename: str,
        parent_widget: QWidget) -> bool:
        """Exporta datos a formato PDF (implementación básica)."""
        try:
            # Por ahora, exportar como CSV y mostrar mensaje
            show_warning(
                parent_widget,
                "Funcionalidad PDF",
                "Exportación PDF en desarrollo.\nExportando como CSV en su lugar."
            )
            return self._export_to_csv(data, headers, filename, parent_widget)

        except Exception as e:
            logging.error(f"Error exportando a PDF: {e}")
            show_error(parent_widget, "Error", f"Error exportando a PDF: {str(e)}")
            return False

    def get_export_dialog_filters(self) -> str:
        """Retorna los filtros para diálogos de exportación."""
        filters = []
        if OPENPYXL_AVAILABLE:
            filters.append("Excel (*.xlsx)")
        filters.append("CSV (*.csv)")
        filters.append("Todos los archivos (*)")
        return ";;".join(filters)

    def validate_data_for_export(self,
data: List[Dict],
        headers: List[str]) -> tuple[bool,
        str]:
        """
        Valida que los datos sean apropiados para exportación.

        Returns:
            tuple: (es_valido, mensaje_error)
        """
        if not data:
            return False, "No hay datos para exportar"

        if not headers:
            return False, "No se han definido encabezados"

        if not isinstance(data, list):
            return False, "Los datos deben ser una lista"

        if not all(isinstance(record, dict) for record in data):
            return False, "Todos los registros deben ser diccionarios"

        return True, ""


class ModuleExportMixin:
    """
    Mixin para agregar funcionalidad de exportación a vistas de módulos.
    """

    def __init__(self):
        self.export_manager = ExportManager()

    def export_table_data(self, export_format: str = 'excel'):
        """
        Exporta los datos de la tabla principal del módulo.
        Debe ser sobrescrito por cada módulo.
        """
        # Esta es una implementación base que debe ser personalizada
        if hasattr(self, 'tabla_principal'):
            data = self._extract_table_data()
            headers = self._get_table_headers()
            module_name = self.__class__.__name__.replace('View', '').lower()

            return self.export_manager.export_data(
                data=data,
                headers=headers,
                module_name=module_name,
                export_format=export_format,
                parent_widget=self
            )
        else:
            show_error(self, "Error", "No se encontró tabla principal para exportar")
            return False

    def _extract_table_data(self) -> List[Dict[str, Any]]:
        """Extrae datos de la tabla principal."""
        data = []
        if hasattr(self, 'tabla_principal'):
            table = self.tabla_principal
            for row in range(table.rowCount()):
                record = {}
                for col in range(table.columnCount()):
                    header = table.horizontalHeaderItem(col)
                    item = table.item(row, col)

                    header_text = header.text() if header else f"Columna_{col}"
                    item_text = item.text() if item else ""

                    record[header_text] = item_text
                data.append(record)
        return data

    def _get_table_headers(self) -> List[str]:
        """Obtiene los encabezados de la tabla principal."""
        headers = []
        if hasattr(self, 'tabla_principal'):
            table = self.tabla_principal
            for col in range(table.columnCount()):
                header = table.horizontalHeaderItem(col)
                header_text = header.text() if header else f"Columna_{col}"
                headers.append(header_text)
        return headers

    def add_export_button(self, layout, button_text: str = "📄 Exportar"):
        """Agrega un botón de exportación al layout especificado."""
        try:
            from rexus.ui.components import RexusButton

            export_button = RexusButton(button_text, )
            export_button.clicked.connect(self.show_export_dialog)
            layout.addWidget(export_button)

        except Exception as e:
            logging.error(f"Error agregando botón de exportación: {e}")

    def show_export_dialog(self):
        """Muestra diálogo de selección de formato de exportación."""
        try:
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QRadioButton, QPushButton

            dialog = QDialog(self)
            dialog.setWindowTitle()
            dialog.setFixedSize(300, 200)

            layout = QVBoxLayout(dialog)

            # Opciones de formato
            self.excel_radio = QRadioButton("Excel (.xlsx)")
            self.csv_radio = QRadioButton("CSV (.csv)")
            self.pdf_radio = QRadioButton("PDF (.pdf)")

            # Seleccionar Excel por defecto
            self.excel_radio.setChecked(True)

            layout.addWidget(self.excel_radio)
            layout.addWidget(self.csv_radio)
            layout.addWidget(self.pdf_radio)

            # Botones
            button_layout = QHBoxLayout()

            export_btn = QPushButton("Exportar")
            export_btn.clicked.connect(lambda: self._execute_export_from_dialog(dialog))

            cancel_btn = QPushButton("Cancelar")
            cancel_btn.clicked.connect(dialog.reject)

            button_layout.addWidget(export_btn)
            button_layout.addWidget(cancel_btn)

            layout.addLayout(button_layout)

            dialog.exec()

        except Exception as e:
            logging.error(f"Error mostrando diálogo de exportación: {e}")
            show_error(self, "Error", f"Error mostrando diálogo: {str(e)}")

    def _execute_export_from_dialog(self, dialog):
        """Ejecuta la exportación según el formato seleccionado."""
        try:
            format_selected = 'excel'  # Default

            if hasattr(self, 'csv_radio') and self.csv_radio.isChecked():
                format_selected = 'csv'
            elif hasattr(self, 'pdf_radio') and self.pdf_radio.isChecked():
                format_selected = 'pdf'

            dialog.accept()
            self.export_table_data(format_selected)

        except Exception as e:
            logging.error(f"Error ejecutando exportación: {e}")
            show_error(self, "Error", f"Error en exportación: {str(e)}")


# Instancia global del gestor de exportación
export_manager = ExportManager()
