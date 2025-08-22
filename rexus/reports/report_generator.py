# -*- coding: utf-8 -*-
"""
Sistema de Reportes Unificado - Rexus.app
Generador central para todos los reportes del sistema
"""

import datetime
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod

# Imports para diferentes formatos de exportación
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class BaseReportGenerator(ABC):
    """Clase base para generadores de reportes."""
    
    def __init__(self, title: str, description: str = ""):
        self.title = title
        self.description = description
        self.generated_date = datetime.datetime.now()
        self.data = []
        self.metadata = {}
    
    @abstractmethod
    def collect_data(self, filters: Dict = None) -> List[Dict]:
        """Recolecta los datos para el reporte."""
        pass
    
    @abstractmethod
    def format_data(self, data: List[Dict]) -> Any:
        """Formatea los datos según el tipo de reporte."""
        pass
    
    def generate(self, output_path: str, format_type: str = "pdf", filters: Dict = None):
        """
        Genera el reporte en el formato especificado.
        
        Args:
            output_path: Ruta donde guardar el reporte
            format_type: Formato del reporte (pdf, excel, csv, html)
            filters: Filtros a aplicar en los datos
        """
        # Recolectar datos
        self.data = self.collect_data(filters)
        
        # Formatear según el tipo
        if format_type.lower() == "pdf":
            return self.generate_pdf(output_path)
        elif format_type.lower() == "excel":
            return self.generate_excel(output_path)
        elif format_type.lower() == "csv":
            return self.generate_csv(output_path)
        elif format_type.lower() == "html":
            return self.generate_html(output_path)
        else:
            raise ValueError(f"Formato no soportado: {format_type}")
    
    def generate_pdf(self, output_path: str):
        """Genera reporte en formato PDF."""
        if not REPORTLAB_AVAILABLE:
            raise ImportError("ReportLab no está instalado. Instale con: pip install reportlab")
        
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Center
        )
        elements.append(Paragraph(self.title, title_style))
        
        # Descripción
        if self.description:
            elements.append(Paragraph(self.description, styles['Normal']))
            elements.append(Spacer(1, 12))
        
        # Fecha de generación
        elements.append(Paragraph(f"Generado el: {self.generated_date.strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Datos en tabla si hay datos
        if self.data:
            formatted_data = self.format_data_for_pdf()
            if formatted_data:
                table = Table(formatted_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 14),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(table)
        
        doc.build(elements)
        return output_path
    
    def generate_excel(self, output_path: str):
        """Genera reporte en formato Excel."""
        if not PANDAS_AVAILABLE:
            raise ImportError("Pandas no está instalado. Instale con: pip install pandas openpyxl")
        
        if not self.data:
            # Crear DataFrame vacío con información del reporte
            df = pd.DataFrame([{
                'Reporte': self.title,
                'Descripción': self.description,
                'Fecha': self.generated_date.strftime('%d/%m/%Y %H:%M'),
                'Estado': 'Sin datos disponibles'
            }])
        else:
            df = pd.DataFrame(self.data)
        
        # Crear writer con múltiples hojas
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Hoja de datos
            df.to_excel(writer, sheet_name='Datos', index=False)
            
            # Hoja de metadata
            metadata_df = pd.DataFrame([{
                'Título': self.title,
                'Descripción': self.description,
                'Fecha de Generación': self.generated_date.strftime('%d/%m/%Y %H:%M'),
                'Total de Registros': len(self.data)
            }])
            metadata_df.to_excel(writer, sheet_name='Información', index=False)
        
        return output_path
    
    def generate_csv(self, output_path: str):
        """Genera reporte en formato CSV."""
        if not PANDAS_AVAILABLE:
            # Fallback manual si pandas no está disponible
            import csv
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                if self.data:
                    fieldnames = self.data[0].keys()
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(self.data)
                else:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Reporte', 'Sin datos disponibles'])
        else:
            df = pd.DataFrame(self.data) if self.data else pd.DataFrame(['Sin datos'])
            df.to_csv(output_path, index=False, encoding='utf-8')
        
        return output_path
    
    def generate_html(self, output_path: str):
        """Genera reporte en formato HTML."""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{self.title}</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #333; border-bottom: 2px solid #667eea; }}
                .metadata {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #667eea; color: white; }}
                tr:nth-child(even) {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>{self.title}</h1>
            <div class="metadata">
                <p><strong>Descripción:</strong> {self.description}</p>
                <p><strong>Fecha de generación:</strong> {self.generated_date.strftime('%d/%m/%Y %H:%M')}</p>
                <p><strong>Total de registros:</strong> {len(self.data)}</p>
            </div>
        """
        
        if self.data:
            html_content += "<table><thead><tr>"
            
            # Headers
            if self.data:
                for key in self.data[0].keys():
                    html_content += f"<th>{key}</th>"
            
            html_content += "</tr></thead><tbody>"
            
            # Datos
            for row in self.data:
                html_content += "<tr>"
                for value in row.values():
                    html_content += f"<td>{value}</td>"
                html_content += "</tr>"
            
            html_content += "</tbody></table>"
        else:
            html_content += "<p>No hay datos disponibles para mostrar.</p>"
        
        html_content += "</body></html>"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    def format_data_for_pdf(self):
        """Formatea datos específicamente para PDF."""
        if not self.data:
            return [["Sin datos disponibles"]]
        
        # Headers
        headers = list(self.data[0].keys())
        formatted_data = [headers]
        
        # Datos
        for row in self.data:
            formatted_data.append([str(value) for value in row.values()])
        
        return formatted_data


class InventarioReportGenerator(BaseReportGenerator):
    """Generador de reportes para el módulo de Inventario."""
    
    def __init__(self, db_connection=None):
        super().__init__(
            "Reporte de Inventario",
            "Estado actual del inventario de productos"
        )
        self.db_connection = db_connection
    
    def collect_data(self, filters: Dict = None) -> List[Dict]:
        """Recolecta datos del inventario."""
        # Datos de ejemplo (en implementación real, consultar BD)
        sample_data = [
            {
                'ID': 1,
                'Producto': 'Vidrio Templado 6mm',
                'Categoría': 'Vidrios',
                'Stock': 150,
                'Precio Unitario': 45.50,
                'Valor Total': 6825.00,
                'Estado': 'Disponible'
            },
            {
                'ID': 2,
                'Producto': 'Herraje Bisagra Premium',
                'Categoría': 'Herrajes',
                'Stock': 45,
                'Precio Unitario': 12.30,
                'Valor Total': 553.50,
                'Estado': 'Stock Bajo'
            },
            {
                'ID': 3,
                'Producto': 'Marco Aluminio Blanco',
                'Categoría': 'Marcos',
                'Stock': 30,
                'Precio Unitario': 25.00,
                'Valor Total': 750.00,
                'Estado': 'Disponible'
            }
        ]
        
        # Aplicar filtros si se proporcionan
        if filters:
            filtered_data = []
            for item in sample_data:
                include = True
                
                if 'categoria' in filters and filters['categoria']:
                    if item['Categoría'].lower() != filters['categoria'].lower():
                        include = False
                
                if 'stock_minimo' in filters and filters['stock_minimo']:
                    if item['Stock'] < int(filters['stock_minimo']):
                        include = False
                
                if include:
                    filtered_data.append(item)
            
            return filtered_data
        
        return sample_data
    
    def format_data(self, data: List[Dict]) -> Any:
        """Formatea datos específicos del inventario."""
        return data


class ObrasReportGenerator(BaseReportGenerator):
    """Generador de reportes para el módulo de Obras."""
    
    def __init__(self, db_connection=None):
        super().__init__(
            "Reporte de Obras",
            "Estado y progreso de obras en ejecución"
        )
        self.db_connection = db_connection
    
    def collect_data(self, filters: Dict = None) -> List[Dict]:
        """Recolecta datos de obras."""
        sample_data = [
            {
                'ID': 1,
                'Nombre': 'Edificio Central - Torre A',
                'Cliente': 'Constructora ABC',
                'Estado': 'En Progreso',
                'Progreso': '65%',
                'Fecha Inicio': '2024-01-15',
                'Fecha Fin Estimada': '2024-12-30',
                'Presupuesto': 2500000.00,
                'Gastado': 1625000.00
            },
            {
                'ID': 2,
                'Nombre': 'Casa Familiar Pérez',
                'Cliente': 'Sr. Pérez',
                'Estado': 'Completada',
                'Progreso': '100%',
                'Fecha Inicio': '2024-02-01',
                'Fecha Fin Estimada': '2024-06-15',
                'Presupuesto': 350000.00,
                'Gastado': 342000.00
            }
        ]
        
        return sample_data
    
    def format_data(self, data: List[Dict]) -> Any:
        """Formatea datos específicos de obras."""
        return data


class ReportGeneratorFactory:
    """Factory para crear generadores de reportes."""
    
    _generators = {
        'inventario': InventarioReportGenerator,
        'obras': ObrasReportGenerator,
        # Agregar más generadores según sea necesario
    }
    
    @classmethod
    def create_generator(cls, report_type: str, **kwargs) -> BaseReportGenerator:
        """
        Crea un generador de reportes del tipo especificado.
        
        Args:
            report_type: Tipo de reporte a generar
            **kwargs: Argumentos adicionales para el generador
            
        Returns:
            Instancia del generador correspondiente
        """
        if report_type not in cls._generators:
            raise ValueError(f"Tipo de reporte no soportado: {report_type}")
        
        generator_class = cls._generators[report_type]
        return generator_class(**kwargs)
    
    @classmethod
    def get_available_reports(cls) -> List[str]:
        """Retorna lista de tipos de reportes disponibles."""
        return list(cls._generators.keys())


class UnifiedReportManager:
    """Gestor unificado de reportes para toda la aplicación."""
    
    def __init__(self, output_directory: str = "reports"):
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(exist_ok=True)
    
    def generate_report(self, report_type: str, format_type: str = "pdf", 
                       filters: Dict = None, custom_filename: str = None) -> str:
        """
        Genera un reporte del tipo especificado.
        
        Args:
            report_type: Tipo de reporte (inventario, obras, etc.)
            format_type: Formato de salida (pdf, excel, csv, html)
            filters: Filtros a aplicar
            custom_filename: Nombre personalizado del archivo
            
        Returns:
            Ruta del archivo generado
        """
        # Crear generador
        generator = ReportGeneratorFactory.create_generator(report_type)
        
        # Generar nombre de archivo si no se proporciona
        if not custom_filename:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            custom_filename = f"{report_type}_report_{timestamp}.{format_type}"
        
        # Ruta completa de salida
        output_path = self.output_directory / custom_filename
        
        # Generar reporte
        return generator.generate(str(output_path), format_type, filters)
    
    def get_report_history(self) -> List[Dict]:
        """Retorna historial de reportes generados."""
        reports = []
        
        for file_path in self.output_directory.iterdir():
            if file_path.is_file():
                stat = file_path.stat()
                reports.append({
                    'filename': file_path.name,
                    'size': stat.st_size,
                    'created': datetime.datetime.fromtimestamp(stat.st_ctime),
                    'modified': datetime.datetime.fromtimestamp(stat.st_mtime),
                    'path': str(file_path)
                })
        
        # Ordenar por fecha de creación (más reciente primero)
        reports.sort(key=lambda x: x['created'], reverse=True)
        return reports
    
    def cleanup_old_reports(self, days_old: int = 30):
        """Limpia reportes antiguos."""
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_old)
        
        for file_path in self.output_directory.iterdir():
            if file_path.is_file():
                if datetime.datetime.fromtimestamp(file_path.stat().st_ctime) < cutoff_date:
                    file_path.unlink()
                    print(f"Reporte antiguo eliminado: {file_path.name}")


# Funciones de conveniencia
def generate_quick_report(report_type: str, format_type: str = "pdf", 
                         output_dir: str = "reports") -> str:
    """
    Función de conveniencia para generar reportes rápidamente.
    
    Args:
        report_type: Tipo de reporte
        format_type: Formato de salida
        output_dir: Directorio de salida
        
    Returns:
        Ruta del archivo generado
    """
    manager = UnifiedReportManager(output_dir)
    return manager.generate_report(report_type, format_type)


def get_available_formats() -> List[str]:
    """Retorna lista de formatos disponibles."""
    formats = ["pdf", "html", "csv"]
    
    if PANDAS_AVAILABLE:
        formats.append("excel")
    
    return formats