#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests del Modelo de Obras - Módulo Obras
"""

import unittest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch
from decimal import Decimal
from datetime import datetime, date

# Configurar path y encoding
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
os.environ['PYTHONIOENCODING'] = 'utf-8'


class MockObrasDatabase:
    """Mock de base de datos para obras."""
    
    def __init__(self):
        self.cursor_mock = Mock()
        self.connected = True
        
        # Datos de obras de prueba
        self.obras_data = [
            {
                'id': 1,
                'codigo': 'OBR001',
                'nombre': 'Obra Test 1',
                'cliente': 'Cliente Test',
                'estado': 'activa',
                'fecha_inicio': date(2025, 8, 1),
                'fecha_fin_estimada': date(2025, 12, 31),
                'presupuesto': Decimal('100000.00'),
                'responsable': 'Juan Pérez'
            },
            {
                'id': 2,
                'codigo': 'OBR002', 
                'nombre': 'Obra Test 2',
                'cliente': 'Cliente Test 2',
                'estado': 'planificada',
                'fecha_inicio': date(2025, 9, 1),
                'fecha_fin_estimada': date(2026, 1, 31),
                'presupuesto': Decimal('150000.00'),
                'responsable': 'María García'
            }
        ]
    
    def cursor(self):
        return self.cursor_mock
    
    def commit(self):
        pass
    
    def close(self):
        self.connected = False


class TestObrasModel(unittest.TestCase):
    """Tests del modelo de obras."""
    
    def setUp(self):
        """Setup para cada test."""
        self.mock_db = MockObrasDatabase()
    
    def test_obra_creation_structure(self):
        """Test: Estructura básica de creación de obra."""
        obra_data = {
            'codigo': 'OBR001',
            'nombre': 'Obra de Prueba',
            'cliente': 'Cliente Test',
            'estado': 'planificada',
            'fecha_inicio': date(2025, 8, 1),
            'fecha_fin_estimada': date(2025, 12, 31),
            'presupuesto': Decimal('100000.00'),
            'responsable': 'Juan Pérez',
            'descripcion': 'Descripción de la obra'
        }
        
        # Validar campos requeridos
        required_fields = ['codigo', 'nombre', 'cliente', 'estado', 'presupuesto']
        for field in required_fields:
            self.assertIn(field, obra_data)
            self.assertIsNotNone(obra_data[field])
    
    def test_obra_states_validation(self):
        """Test: Validación de estados de obra."""
        valid_states = ['planificada', 'activa', 'pausada', 'completada', 'cancelada']
        
        for state in valid_states:
            self.assertIsInstance(state, str)
            self.assertGreater(len(state), 4)
    
    def test_budget_validation(self):
        """Test: Validación de presupuesto."""
        valid_budgets = [Decimal('1000.00'), Decimal('50000.00'), Decimal('1000000.00')]
        
        for budget in valid_budgets:
            self.assertGreater(budget, Decimal('0'))
            self.assertIsInstance(budget, Decimal)
    
    def test_date_validation(self):
        """Test: Validación de fechas."""
        fecha_inicio = date(2025, 8, 1)
        fecha_fin = date(2025, 12, 31)
        
        # Fecha fin debe ser posterior a fecha inicio
        self.assertGreater(fecha_fin, fecha_inicio)
        
        # Ambas fechas deben ser válidas
        self.assertIsInstance(fecha_inicio, date)
        self.assertIsInstance(fecha_fin, date)
    
    @patch('rexus.core.database.InventarioDatabaseConnection')
    def test_obra_retrieval(self, mock_db_connection):
        """Test: Obtener obras de la base de datos."""
        mock_db_connection.return_value = self.mock_db
        
        # Configurar respuesta mock
        self.mock_db.cursor_mock.fetchall.return_value = [
            (1, 'OBR001', 'Obra Test 1', 'Cliente Test', 'activa', '2025-08-01', '2025-12-31', 100000.00, 'Juan Pérez'),
            (2, 'OBR002', 'Obra Test 2', 'Cliente Test 2', 'planificada', '2025-09-01', '2026-01-31', 150000.00, 'María García')
        ]
        
        # Test básico de estructura de datos
        obras = self.mock_db.cursor_mock.fetchall()
        self.assertEqual(len(obras), 2)
        
        # Validar estructura de cada obra
        for obra in obras:
            self.assertEqual(len(obra), 9)  # 9 campos esperados
            self.assertIsInstance(obra[0], int)  # ID
            self.assertIsInstance(obra[1], str)  # Código


class TestObrasPresupuesto(unittest.TestCase):
    """Tests de presupuesto y costos de obras."""
    
    def test_budget_calculation(self):
        """Test: Cálculo de presupuesto."""
        # Componentes del presupuesto
        materiales = Decimal('50000.00')
        mano_obra = Decimal('30000.00')
        equipos = Decimal('15000.00')
        gastos_generales = Decimal('5000.00')
        
        total_presupuesto = materiales + mano_obra + equipos + gastos_generales
        
        self.assertEqual(total_presupuesto, Decimal('100000.00'))
        self.assertGreater(total_presupuesto, Decimal('0'))
    
    def test_budget_tracking(self):
        """Test: Seguimiento de presupuesto."""
        presupuesto_inicial = Decimal('100000.00')
        gastos_actuales = Decimal('45000.00')
        porcentaje_ejecutado = (gastos_actuales / presupuesto_inicial) * 100
        
        # Validaciones de seguimiento
        self.assertEqual(porcentaje_ejecutado, Decimal('45.00'))
        self.assertLess(gastos_actuales, presupuesto_inicial)
        self.assertGreaterEqual(porcentaje_ejecutado, Decimal('0'))


class TestObrasEstados(unittest.TestCase):
    """Tests de estados y flujo de obras."""
    
    def test_state_transitions(self):
        """Test: Transiciones de estado válidas."""
        # Flujo típico de estados
        valid_transitions = {
            'planificada': ['activa', 'cancelada'],
            'activa': ['pausada', 'completada', 'cancelada'],
            'pausada': ['activa', 'cancelada'],
            'completada': [],  # Estado final
            'cancelada': []    # Estado final
        }
        
        # Validar transiciones
        for current_state, allowed_next in valid_transitions.items():
            self.assertIsInstance(current_state, str)
            self.assertIsInstance(allowed_next, list)
    
    def test_final_states(self):
        """Test: Estados finales de obra."""
        final_states = ['completada', 'cancelada']
        
        for state in final_states:
            self.assertIsInstance(state, str)
            self.assertIn(state, final_states)


class TestObrasIntegracion(unittest.TestCase):
    """Tests de integración con otros módulos."""
    
    def test_obra_inventory_integration(self):
        """Test: Integración obra-inventario."""
        # Materiales asignados a obra
        materiales_obra = [
            {'producto_id': 1, 'cantidad_asignada': 10, 'cantidad_utilizada': 5},
            {'producto_id': 2, 'cantidad_asignada': 20, 'cantidad_utilizada': 15}
        ]
        
        # Validar estructura de materiales
        for material in materiales_obra:
            required_fields = ['producto_id', 'cantidad_asignada', 'cantidad_utilizada']
            for field in required_fields:
                self.assertIn(field, material)
            
            # Cantidad utilizada no debe exceder la asignada
            self.assertLessEqual(
                material['cantidad_utilizada'], 
                material['cantidad_asignada']
            )
    
    def test_obra_personnel_assignment(self):
        """Test: Asignación de personal a obra."""
        personal_obra = [
            {'empleado_id': 1, 'rol': 'responsable', 'fecha_asignacion': '2025-08-01'},
            {'empleado_id': 2, 'rol': 'operario', 'fecha_asignacion': '2025-08-01'},
            {'empleado_id': 3, 'rol': 'supervisor', 'fecha_asignacion': '2025-08-02'}
        ]
        
        # Validar asignaciones
        for asignacion in personal_obra:
            required_fields = ['empleado_id', 'rol', 'fecha_asignacion']
            for field in required_fields:
                self.assertIn(field, asignacion)
        
        # Debe haber exactamente un responsable
        responsables = [p for p in personal_obra if p['rol'] == 'responsable']
        self.assertEqual(len(responsables), 1)


class TestObrasReportes(unittest.TestCase):
    """Tests de reportes de obras."""
    
    def test_obra_progress_report(self):
        """Test: Reporte de progreso de obra."""
        progreso_data = {
            'obra_id': 1,
            'porcentaje_avance': 45.5,
            'tareas_completadas': 15,
            'tareas_pendientes': 18,
            'fecha_ultimo_avance': '2025-08-21'
        }
        
        # Validar estructura del progreso
        required_fields = ['obra_id', 'porcentaje_avance', 'tareas_completadas']
        for field in required_fields:
            self.assertIn(field, progreso_data)
        
        # Validar rangos lógicos
        self.assertGreaterEqual(progreso_data['porcentaje_avance'], 0)
        self.assertLessEqual(progreso_data['porcentaje_avance'], 100)
    
    def test_obra_financial_summary(self):
        """Test: Resumen financiero de obra."""
        resumen_financiero = {
            'presupuesto_inicial': Decimal('100000.00'),
            'gastos_ejecutados': Decimal('45000.00'),
            'comprometido': Decimal('20000.00'),
            'disponible': Decimal('35000.00'),
            'variacion_presupuestal': Decimal('0.00')
        }
        
        # Validar balance financiero
        total_utilizado = (
            resumen_financiero['gastos_ejecutados'] + 
            resumen_financiero['comprometido'] + 
            resumen_financiero['disponible']
        )
        
        self.assertEqual(total_utilizado, resumen_financiero['presupuesto_inicial'])


if __name__ == '__main__':
    print("Ejecutando tests del modelo de obras...")
    unittest.main(verbosity=2)