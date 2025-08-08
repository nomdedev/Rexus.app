"""
Tests unitarios para los métodos refactorizados del módulo obras.
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch
from PyQt6.QtWidgets import QApplication

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from rexus.modules.obras.data_mapper import ObrasDataMapper, ObrasValidator, ObrasTableHelper


class TestObrasDataMapper:
    """Tests para el mapper de datos de obras."""

    def test_tupla_a_dict_obra_completa(self):
        """Test: conversión de tupla completa a diccionario."""
        # Tupla simulando estructura real de BD (27 campos)
        tupla_obra = tuple([
            1,                          # 0: id
            "Edificio Central",         # 1: nombre
            None, None, None,           # 2-4: campos intermedios
            "Cliente A",                # 5: cliente
            "EN_PROCESO",               # 6: estado
            None, None, None, None,     # 7-10: campos intermedios
            None, None, None, None,     # 11-14: campos intermedios
            None, None, None, None,     # 15-18: campos intermedios
            None,                       # 19: campo intermedio
            "OBR-001",                  # 20: codigo
            "Juan Pérez",               # 21: responsable
            "2024-01-15",               # 22: fecha_inicio
            "2024-12-15",               # 23: fecha_fin_estimada
            150000.0,                   # 24: presupuesto_inicial
            None,                       # 25: campo intermedio
            "Construcción principal"    # 26: descripcion
        ])
        
        resultado = ObrasDataMapper.tupla_a_dict(tupla_obra)
        
        assert resultado['id'] == 1
        assert resultado['codigo'] == "OBR-001"
        assert resultado['nombre'] == "Edificio Central"
        assert resultado['cliente'] == "Cliente A"
        assert resultado['estado'] == "EN_PROCESO"
        assert resultado['responsable'] == "Juan Pérez"
        assert resultado['presupuesto_inicial'] == 150000.0

    def test_tupla_a_dict_obra_incompleta(self):
        """Test: conversión de tupla incompleta a diccionario."""
        tupla_obra = (1, "Obra Simple", "DESC", "Descripción")
        
        resultado = ObrasDataMapper.tupla_a_dict(tupla_obra)
        
        assert resultado['id'] == 1
        assert resultado['nombre'] == "Obra Simple"
        assert resultado['codigo'] == ''  # Campo faltante
        assert resultado['cliente'] == ''  # Campo faltante

    def test_tupla_vacia(self):
        """Test: manejo de tupla vacía."""
        resultado = ObrasDataMapper.tupla_a_dict(())
        
        assert resultado == {}

    def test_lista_tuplas_a_dicts(self):
        """Test: conversión de lista de tuplas."""
        tuplas = [
            (1, "Obra 1", None, None, None, "Cliente 1"),
            (2, "Obra 2", None, None, None, "Cliente 2")
        ]
        
        resultado = ObrasDataMapper.lista_tuplas_a_dicts(tuplas)
        
        assert len(resultado) == 2
        assert resultado[0]['id'] == 1
        assert resultado[1]['id'] == 2

    def test_dict_a_fila_tabla(self):
        """Test: conversión de diccionario a fila de tabla."""
        obra_dict = {
            'codigo': 'OBR-001',
            'nombre': 'Edificio Central',
            'cliente': 'Cliente A',
            'responsable': 'Juan Pérez',
            'fecha_inicio': '2024-01-15',
            'fecha_fin_estimada': '2024-12-15',
            'estado': 'EN_PROCESO',
            'presupuesto_inicial': 150000.0
        }
        
        resultado = ObrasDataMapper.dict_a_fila_tabla(obra_dict)
        
        assert len(resultado) == 8
        assert resultado[0] == 'OBR-001'
        assert resultado[1] == 'Edificio Central'
        assert resultado[7] == '$150,000.00'

    def test_formatear_presupuesto_tabla(self):
        """Test: formateo de presupuesto para tabla."""
        assert ObrasDataMapper._formatear_presupuesto_tabla(150000) == '$150,000.00'
        assert ObrasDataMapper._formatear_presupuesto_tabla(0) == ''
        assert ObrasDataMapper._formatear_presupuesto_tabla(None) == ''

    def test_formatear_fecha_tabla(self):
        """Test: formateo de fecha para tabla."""
        assert ObrasDataMapper._formatear_fecha_tabla('2024-01-15 10:30:00') == '2024-01-15'
        assert ObrasDataMapper._formatear_fecha_tabla('2024-01-15') == '2024-01-15'
        assert ObrasDataMapper._formatear_fecha_tabla('') == ''


class TestObrasValidator:
    """Tests para el validador de obras."""

    def test_validar_obra_completa_valida(self):
        """Test: validación de obra completa y válida."""
        obra_dict = {
            'nombre': 'Edificio Central',
            'codigo': 'OBR-001',
            'cliente': 'Cliente A',
            'responsable': 'Juan Pérez',
            'fecha_inicio': '2024-01-15',
            'fecha_fin_estimada': '2024-12-15',
            'presupuesto_inicial': 150000.0
        }
        
        es_valida, errores = ObrasValidator.validar_obra_dict(obra_dict)
        
        assert es_valida is True
        assert len(errores) == 0

    def test_validar_obra_campos_faltantes(self):
        """Test: validación con campos requeridos faltantes."""
        obra_dict = {
            'nombre': '',  # Vacío
            'codigo': 'OBR-001',
            'cliente': '',  # Vacío
            'responsable': 'Juan Pérez'
        }
        
        es_valida, errores = ObrasValidator.validar_obra_dict(obra_dict)
        
        assert es_valida is False
        assert 'El nombre es requerido' in errores
        assert 'El cliente es requerido' in errores

    def test_validar_fechas_invalidas(self):
        """Test: validación con fechas inválidas."""
        obra_dict = {
            'nombre': 'Edificio Central',
            'codigo': 'OBR-001',
            'cliente': 'Cliente A',
            'responsable': 'Juan Pérez',
            'fecha_inicio': 'fecha-invalida',
            'fecha_fin_estimada': '2024-13-45'  # Fecha imposible
        }
        
        es_valida, errores = ObrasValidator.validar_obra_dict(obra_dict)
        
        assert es_valida is False
        assert any('fecha' in error.lower() for error in errores)

    def test_validar_presupuesto_negativo(self):
        """Test: validación con presupuesto negativo."""
        obra_dict = {
            'nombre': 'Edificio Central',
            'codigo': 'OBR-001',
            'cliente': 'Cliente A',
            'responsable': 'Juan Pérez',
            'presupuesto_inicial': -50000.0
        }
        
        es_valida, errores = ObrasValidator.validar_obra_dict(obra_dict)
        
        assert es_valida is False
        assert 'negativo' in str(errores).lower()


class TestObrasTableHelper:
    """Tests para el helper de tabla."""

    @pytest.fixture
    def app(self):
        """Fixture para QApplication."""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        yield app

    def test_crear_boton_accion(self, app):
        """Test: creación de botón de acción."""
        callback_llamado = False
        
        def callback_test(fila):
            nonlocal callback_llamado
            callback_llamado = True
            assert fila == 5
        
        boton = ObrasTableHelper.crear_boton_accion("Test", callback_test, 5)
        
        assert boton is not None
        assert boton.text() == "Test"
        
        # Simular click
        boton.click()
        assert callback_llamado is True


if __name__ == "__main__":
    # Ejecutar tests
    import subprocess
    subprocess.run(["python", "-m", "pytest", __file__, "-v"])
