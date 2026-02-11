"""
Tests Críticos - Rexus.app
Paquete de pruebas críticas para seguridad, base de datos e integración

Ejecutar todos los tests críticos:
    pytest tests/critical/ -v

Ejecutar tests específicos:
    pytest tests/critical/test_security_critical.py -v
    pytest tests/critical/test_database_critical.py -v
    pytest tests/critical/test_integration_critical.py -v

Ver cobertura:
    pytest tests/critical/ --cov=rexus --cov-report=html
"""

__all__ = [
    'test_security_critical',
    'test_database_critical',
    'test_integration_critical'
]
