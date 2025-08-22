# -*- coding: utf-8 -*-
"""
Dashboard Package - Rexus.app
Sistema de dashboard centralizado con métricas y KPIs
"""

from .main_dashboard import MainDashboard
from .dashboard_controller import DashboardController
from .widgets.kpi_widget import KPIWidget
from .widgets.chart_widget import ChartWidget
from .widgets.activity_widget import ActivityWidget

__all__ = [
    'MainDashboard',
    'DashboardController',
    'KPIWidget', 
    'ChartWidget',
    'ActivityWidget'
]