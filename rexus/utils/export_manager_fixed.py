"""
Sistema de Exportación Estándar - Rexus.app v2.0.0

Sistema unificado de exportación de datos para todos los módulos del sistema.
Soporta exportación a Excel, CSV y PDF con configuraciones personalizables.
"""

import logging
import os
import csv
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    from PyQt6.QtWidgets import QWidget, QDialog, QVBoxLayout, QLabel, QPushButton
except ImportError:
    QWidget = None
    QDialog = None
    QVBoxLayout = None
    QLabel = None
    QPushButton = None

try:
    from rexus.utils.message_system import show_success, show_error, show_warning, show_info
except ImportError:
    def show_success(parent, title, message): print(f"SUCCESS: {title} - {message}")
    def show_error(parent, title, message): print(f"ERROR: {title} - {message}")
    def show_warning(parent, title, message): print(f"WARNING: {title} - {message}")
    def show_info(parent, title, message): print(f"INFO: {title} - {message}")

# Verificar disponibilidad de openpyxl
try:
    import openpyxl
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False


class ExportManager:
    """Gestor de exportación unificado."""
    
    def __init__(self):
        """Inicializa el gestor de exportación."""
        self.logger = logging.getLogger(__name__)
        
    def export_to_csv(self, data: List[Dict], headers: List[str], filename: str, parent_widget=None) -> bool:
        """Exporta datos a CSV."""
        try:
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                for row in data:
                    writer.writerow(row)
            
            show_success(parent_widget, "Exportación Exitosa",
                        f"Datos exportados a CSV:\n{filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exportando a CSV: {e}")
            show_error(parent_widget, "Error", f"Error exportando a CSV: {str(e)}")
            return False

    def export_to_excel(self, data: List[Dict], headers: List[str], filename: str, parent_widget=None) -> bool:
        """Exporta datos a Excel."""
        try:
            if not OPENPYXL_AVAILABLE:
                show_warning(parent_widget, "Excel no disponible", 
                           "openpyxl no está instalado. Exportando a CSV.")
                return self.export_to_csv(data, headers, filename.replace('.xlsx', '.csv'), parent_widget)
            
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            
            # Escribir headers
            for col, header in enumerate(headers, 1):
                sheet.cell(row=1, column=col, value=header)
            
            # Escribir datos
            for row_idx, row_data in enumerate(data, 2):
                for col_idx, header in enumerate(headers, 1):
                    sheet.cell(row=row_idx, column=col_idx, value=row_data.get(header, ''))
            
            workbook.save(filename)
            show_success(parent_widget, "Exportación Exitosa",
                        f"Datos exportados a Excel:\n{filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exportando a Excel: {e}")
            show_error(parent_widget, "Error", f"Error exportando a Excel: {str(e)}")
            return False

    def export_to_pdf(self, data: List[Dict], headers: List[str], filename: str, parent_widget=None) -> bool:
        """Exporta datos a PDF (implementación básica)."""
        try:
            # Por ahora, exportar como CSV y mostrar mensaje
            show_warning(parent_widget, "Funcionalidad PDF",
                        "La exportación a PDF está en desarrollo. Exportando como CSV.")
            return self.export_to_csv(data, headers, filename.replace('.pdf', '.csv'), parent_widget)
            
        except Exception as e:
            self.logger.error(f"Error exportando a PDF: {e}")
            show_error(parent_widget, "Error", f"Error exportando a PDF: {str(e)}")
            return False

    def export_data(self, data: List[Dict], headers: List[str], filename: str, 
                   format_type: str = "csv", parent_widget=None) -> bool:
        """Exporta datos en el formato especificado."""
        try:
            if format_type.lower() == "csv":
                return self.export_to_csv(data, headers, filename, parent_widget)
            elif format_type.lower() == "excel":
                return self.export_to_excel(data, headers, filename, parent_widget)
            elif format_type.lower() == "pdf":
                return self.export_to_pdf(data, headers, filename, parent_widget)
            else:
                show_error(parent_widget, "Error", f"Formato no soportado: {format_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error en export_data: {e}")
            show_error(parent_widget, "Error", f"Error exportando datos: {str(e)}")
            return False


class ModuleExportMixin:
    """Mixin para agregar funcionalidad de exportación a módulos."""
    
    def __init__(self):
        """Inicializa el mixin de exportación."""
        self.export_manager = ExportManager()
    
    def export_table_data(self, export_format: str = "csv") -> bool:
        """Exporta los datos de la tabla principal del módulo."""
        try:
            # Esta función debe ser sobrescrita por cada módulo
            show_info(None, "Exportación", "Función de exportación debe ser implementada por el módulo")
            return False
            
        except Exception as e:
            show_error(None, "Error", f"Error exportando datos de tabla: {str(e)}")
            return False

    def show_export_dialog(self):
        """Muestra un diálogo de exportación simple."""
        try:
            if not QDialog:
                show_warning(None, "Exportación", "Interfaz gráfica no disponible")
                return
                
            dialog = QDialog()
            dialog.setWindowTitle("Exportar Datos")
            dialog.setModal(True)
            
            layout = QVBoxLayout()
            
            label = QLabel("Seleccione el formato de exportación:")
            layout.addWidget(label)
            
            # Botones de exportación
            csv_btn = QPushButton("Exportar CSV")
            csv_btn.clicked.connect(lambda: self.export_table_data("csv"))
            layout.addWidget(csv_btn)
            
            if OPENPYXL_AVAILABLE:
                excel_btn = QPushButton("Exportar Excel")
                excel_btn.clicked.connect(lambda: self.export_table_data("excel"))
                layout.addWidget(excel_btn)
            
            dialog.setLayout(layout)
            dialog.exec()
            
        except Exception as e:
            show_error(None, "Error", f"Error mostrando diálogo de exportación: {str(e)}")


# Instancia global del gestor de exportación
export_manager = ExportManager()
