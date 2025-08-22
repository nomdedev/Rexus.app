# -*- coding: utf-8 -*-
"""
Sistema de Reportes Unificado - Rexus.app
Generación automática de reportes en múltiples formatos
"""

from .report_generator import (
    BaseReportGenerator,
    InventarioReportGenerator,
    ObrasReportGenerator,
    ReportGeneratorFactory,
    UnifiedReportManager,
    generate_quick_report,
    get_available_formats
)

__all__ = [
    'BaseReportGenerator',
    'InventarioReportGenerator', 
    'ObrasReportGenerator',
    'ReportGeneratorFactory',
    'UnifiedReportManager',
    'generate_quick_report',
    'get_available_formats'
]