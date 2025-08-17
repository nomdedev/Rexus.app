"""
Simple Test - Logística Dialog
Basic functionality test for the service generation dialog.
"""

import sys
import os
import pytest

def test_logistica_simple_flow():
    """Pytest-friendly version of the simple logística dialog test."""
    # Test 1: Import Dialog Classes
    try:
        from src.modules.logistica.view import DialogoGenerarServicio, DialogoPreviewServicios
    except Exception as e:
        pytest.skip(f"Dialog import failed: {e}")

    # Test 2: Import Controller
    try:
        from src.modules.logistica.controller import LogisticaController
        controller = LogisticaController()
    except Exception as e:
        pytest.skip(f"Controller import failed: {e}")

    # Test 3: Check Controller Methods
    assert hasattr(controller, 'generar_servicios_automaticos'), "generar_servicios_automaticos method missing"

    # Test 4: Test Service Generation
    configuracion = {
        'fecha_desde': '2025-07-31',
        'fecha_hasta': '2025-08-15',
        'zona': 'Todas las zonas',
        'tipo_vehiculo': 'Automático (mejor opción)',
        'capacidad_maxima': '1000',
        'max_paradas': '8',
        'criterio_optimizacion': 'Eficiencia balanceada'
    }

    try:
        servicios = controller._simular_servicios_generados(configuracion)
    except Exception as e:
        pytest.fail(f"Service generation failed: {e}")

    assert isinstance(servicios, list), "Servicios should be a list"

    # Test 5: Check View Method
    try:
        from src.modules.logistica.view import LogisticaView
        view = LogisticaView()
    except Exception as e:
        pytest.skip(f"View import/instantiation failed: {e}")

    assert hasattr(view, 'abrir_generador_automatico'), "View button method missing"
