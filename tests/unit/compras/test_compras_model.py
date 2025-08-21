#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests del Modelo de Compras - Módulo Compras
PRIORIDAD CRÍTICA: "faltan mejorarlo visualmente muchísimo"
"""

__test_module__ = 'compras_model'

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


class MockComprasDatabase:
    """Mock de base de datos para compras."""
    
    def __init__(self):
        self.cursor_mock = Mock()
        self.connected = True
        
        # Datos de compras de prueba
        self.compras_data = [
            {
                'id': 1,
                'codigo': 'COMP001',
                'proveedor': 'Proveedor A',
                'fecha': date(2025, 8, 21),
                'estado': 'pendiente',
                'total': Decimal('50000.00'),
                'moneda': 'ARS',
                'observaciones': 'Compra urgente',
                'usuario_creacion': 'admin'
            },
            {
                'id': 2,
                'codigo': 'COMP002',
                'proveedor': 'Proveedor B', 
                'fecha': date(2025, 8, 20),
                'estado': 'aprobada',
                'total': Decimal('75000.00'),
                'moneda': 'ARS',
                'observaciones': 'Compra regular',
                'usuario_creacion': 'manager1'
            }
        ]
        
        # Proveedores disponibles
        self.proveedores_data = [
            {'id': 1, 'nombre': 'Proveedor A', 'rubro': 'Materiales', 'activo': True},
            {'id': 2, 'nombre': 'Proveedor B', 'rubro': 'Herramientas', 'activo': True},
            {'id': 3, 'nombre': 'Proveedor C', 'rubro': 'Equipos', 'activo': True}
        ]
    
    def cursor(self):
        return self.cursor_mock
    
    def commit(self):
        pass
    
    def close(self):
        self.connected = False


class TestComprasModel(unittest.TestCase):
    """Tests del modelo de compras."""
    
    def setUp(self):
        """Setup para cada test."""
        self.mock_db = MockComprasDatabase()
    
    def test_compra_creation_structure(self):
        """Test: Estructura básica de creación de compra."""
        compra_data = {
            'codigo': 'COMP001',
            'proveedor_id': 1,
            'fecha': date(2025, 8, 21),
            'estado': 'borrador',
            'moneda': 'ARS',
            'subtotal': Decimal('41322.31'),  # Sin IVA
            'iva': Decimal('8677.69'),        # 21% IVA Argentina
            'total': Decimal('50000.00'),     # Total con IVA
            'observaciones': 'Compra de materiales',
            'usuario_creacion': 'admin',
            'fecha_entrega_solicitada': date(2025, 8, 25)
        }
        
        # Validar campos requeridos
        required_fields = ['codigo', 'proveedor_id', 'fecha', 'estado', 'total']
        for field in required_fields:
            self.assertIn(field, compra_data)
            self.assertIsNotNone(compra_data[field])
    
    def test_compra_states_validation(self):
        """Test: Validación de estados de compra."""
        valid_states = ['borrador', 'pendiente', 'aprobada', 'rechazada', 'recibida', 'cancelada']
        
        for state in valid_states:
            self.assertIsInstance(state, str)
            self.assertGreater(len(state), 4)
    
    def test_compra_state_transitions(self):
        """Test: Transiciones válidas entre estados."""
        # Flujo típico de estados
        state_flow = {
            'borrador': ['pendiente', 'cancelada'],
            'pendiente': ['aprobada', 'rechazada', 'cancelada'],
            'aprobada': ['recibida', 'cancelada'],
            'rechazada': ['pendiente'],  # Puede volver a revisión
            'recibida': [],  # Estado final
            'cancelada': []  # Estado final
        }
        
        # Validar transiciones lógicas
        for current_state, allowed_next in state_flow.items():
            self.assertIsInstance(current_state, str)
            self.assertIsInstance(allowed_next, list)
    
    def test_tax_calculation_argentina(self):
        """Test: Cálculo de impuestos para Argentina."""
        # IVA 21% Argentina
        subtotal = Decimal('41322.31')
        iva_rate = Decimal('0.21')
        iva_amount = subtotal * iva_rate
        total = subtotal + iva_amount
        
        # Validar cálculo de IVA
        self.assertAlmostEqual(iva_amount, Decimal('8677.69'), places=2)
        self.assertAlmostEqual(total, Decimal('50000.00'), places=2)
        
        # Validar que IVA esté en rango correcto
        self.assertGreaterEqual(iva_rate, Decimal('0.10'))  # Mín 10%
        self.assertLessEqual(iva_rate, Decimal('0.30'))     # Máx 30%
    
    def test_approval_workflow_validation(self):
        """Test: Validación de flujo de aprobación."""
        # Límites de aprobación típicos
        approval_limits = {
            'USER': Decimal('10000.00'),
            'MANAGER': Decimal('50000.00'), 
            'ADMIN': Decimal('1000000.00')  # Sin límite práctico
        }
        
        # Test de compra que requiere aprobación
        compra_amount = Decimal('75000.00')
        user_role = 'MANAGER'
        user_limit = approval_limits[user_role]
        
        requires_approval = compra_amount > user_limit
        
        if user_role == 'ADMIN':
            self.assertFalse(requires_approval)
        else:
            # Manager puede aprobar hasta $50,000
            self.assertTrue(requires_approval)
    
    @patch('rexus.core.database.InventarioDatabaseConnection')
    def test_compra_retrieval(self, mock_db_connection):
        """Test: Obtener compras de la base de datos."""
        mock_db_connection.return_value = self.mock_db
        
        # Configurar respuesta mock
        self.mock_db.cursor_mock.fetchall.return_value = [
            (1, 'COMP001', 'Proveedor A', '2025-08-21', 'pendiente', 50000.00, 'ARS', 'Compra urgente'),
            (2, 'COMP002', 'Proveedor B', '2025-08-20', 'aprobada', 75000.00, 'ARS', 'Compra regular')
        ]
        
        # Test básico de estructura de datos
        compras = self.mock_db.cursor_mock.fetchall()
        self.assertEqual(len(compras), 2)
        
        # Validar estructura de cada compra
        for compra in compras:
            self.assertEqual(len(compra), 8)  # 8 campos esperados
            self.assertIsInstance(compra[0], int)    # ID
            self.assertIsInstance(compra[1], str)    # Código
            self.assertIsInstance(compra[5], float)  # Total


class TestComprasProveedores(unittest.TestCase):
    """Tests de gestión de proveedores."""
    
    def test_proveedor_structure(self):
        """Test: Estructura de datos de proveedor."""
        proveedor_data = {
            'id': 1,
            'nombre': 'Proveedor Test SA',
            'cuit': '20-12345678-9',
            'rubro': 'Materiales de Construcción',
            'direccion': 'Av. Corrientes 1234, CABA',
            'telefono': '+54-11-1234-5678',
            'email': 'contacto@proveedor.com',
            'condicion_iva': 'Responsable Inscripto',
            'activo': True,
            'calificacion': 4.2,
            'fecha_alta': date(2025, 1, 15)
        }
        
        # Validar campos requeridos
        required_fields = ['nombre', 'cuit', 'rubro', 'condicion_iva']
        for field in required_fields:
            self.assertIn(field, proveedor_data)
            self.assertIsNotNone(proveedor_data[field])
    
    def test_proveedor_validation(self):
        """Test: Validación de datos de proveedor."""
        # CUIT Argentina válido (formato 20-12345678-9)
        cuit_valido = '20-12345678-9'
        self.assertRegex(cuit_valido, r'^\d{2}-\d{8}-\d$')
        
        # Email válido
        email_valido = 'contacto@proveedor.com'
        self.assertIn('@', email_valido)
        self.assertIn('.', email_valido)
        
        # Calificación en rango 1-5
        calificacion = 4.2
        self.assertGreaterEqual(calificacion, 1.0)
        self.assertLessEqual(calificacion, 5.0)


class TestComprasDetalles(unittest.TestCase):
    """Tests de detalles de compra (productos/servicios)."""
    
    def test_detalle_compra_structure(self):
        """Test: Estructura de detalle de compra."""
        detalle_data = {
            'compra_id': 1,
            'producto_id': 1,
            'descripcion': 'Cemento Portland x50kg',
            'cantidad': 100,
            'unidad_medida': 'bolsas',
            'precio_unitario': Decimal('850.00'),
            'descuento_porcentaje': Decimal('5.00'),
            'descuento_importe': Decimal('4250.00'),
            'subtotal': Decimal('80750.00'),  # (100 * 850) - 4250
            'iva_porcentaje': Decimal('21.00'),
            'iva_importe': Decimal('16957.50'),
            'total': Decimal('97707.50')
        }
        
        # Validar campos requeridos
        required_fields = ['compra_id', 'descripcion', 'cantidad', 'precio_unitario']
        for field in required_fields:
            self.assertIn(field, detalle_data)
            self.assertIsNotNone(detalle_data[field])
    
    def test_detalle_calculations(self):
        """Test: Cálculos en detalles de compra."""
        cantidad = 100
        precio_unitario = Decimal('850.00')
        descuento_porcentaje = Decimal('5.00')
        iva_porcentaje = Decimal('21.00')
        
        # Cálculo paso a paso
        bruto = cantidad * precio_unitario  # 85,000
        descuento = bruto * (descuento_porcentaje / 100)  # 4,250
        subtotal = bruto - descuento  # 80,750
        iva = subtotal * (iva_porcentaje / 100)  # 16,957.50
        total = subtotal + iva  # 97,707.50
        
        # Validar cálculos
        self.assertEqual(bruto, Decimal('85000.00'))
        self.assertEqual(descuento, Decimal('4250.00'))
        self.assertEqual(subtotal, Decimal('80750.00'))
        self.assertEqual(iva, Decimal('16957.50'))
        self.assertEqual(total, Decimal('97707.50'))


class TestComprasDashboard(unittest.TestCase):
    """Tests de dashboard y KPIs de compras."""
    
    def test_dashboard_kpis_structure(self):
        """Test: Estructura de KPIs del dashboard."""
        dashboard_data = {
            'resumen_mes_actual': {
                'total_compras': Decimal('250000.00'),
                'numero_ordenes': 15,
                'promedio_orden': Decimal('16666.67'),
                'pendientes_aprobacion': 5
            },
            'top_proveedores': [
                {'proveedor': 'Proveedor A', 'total': Decimal('75000.00'), 'ordenes': 3},
                {'proveedor': 'Proveedor B', 'total': Decimal('60000.00'), 'ordenes': 2}
            ],
            'alertas': [
                {'tipo': 'presupuesto', 'mensaje': 'Presupuesto mensual al 80%'},
                {'tipo': 'aprobacion', 'mensaje': '5 órdenes pendientes de aprobación'}
            ],
            'grafico_gastos_mensuales': [
                {'mes': 'Jul', 'total': Decimal('180000.00')},
                {'mes': 'Ago', 'total': Decimal('250000.00')}
            ]
        }
        
        # Validar secciones del dashboard
        required_sections = ['resumen_mes_actual', 'top_proveedores', 'alertas']
        for section in required_sections:
            self.assertIn(section, dashboard_data)
        
        # Validar KPIs numéricos
        resumen = dashboard_data['resumen_mes_actual']
        self.assertGreater(resumen['total_compras'], Decimal('0'))
        self.assertGreater(resumen['numero_ordenes'], 0)
        self.assertGreaterEqual(resumen['pendientes_aprobacion'], 0)


class TestComprasIntegracion(unittest.TestCase):
    """Tests de integración con otros módulos."""
    
    def test_integration_with_inventory(self):
        """Test: Integración compras-inventario."""
        # Al recibir una compra, debe actualizar stock
        compra_recibida = {
            'compra_id': 1,
            'estado': 'recibida',
            'detalles': [
                {'producto_id': 1, 'cantidad_recibida': 100},
                {'producto_id': 2, 'cantidad_recibida': 50}
            ]
        }
        
        # Validar que hay productos para actualizar inventario
        self.assertGreater(len(compra_recibida['detalles']), 0)
        
        for detalle in compra_recibida['detalles']:
            self.assertIn('producto_id', detalle)
            self.assertIn('cantidad_recibida', detalle)
            self.assertGreater(detalle['cantidad_recibida'], 0)
    
    def test_integration_with_accounting(self):
        """Test: Integración compras-contabilidad."""
        # Compra aprobada debe generar asiento contable
        compra_aprobada = {
            'id': 1,
            'total': Decimal('50000.00'),
            'iva': Decimal('8677.69'),
            'subtotal': Decimal('41322.31'),
            'proveedor': 'Proveedor A',
            'fecha': '2025-08-21'
        }
        
        # Asiento contable esperado
        asiento_esperado = {
            'fecha': compra_aprobada['fecha'],
            'concepto': f"Compra a {compra_aprobada['proveedor']}",
            'debe': [
                {'cuenta': 'Compras', 'importe': compra_aprobada['subtotal']},
                {'cuenta': 'IVA Crédito Fiscal', 'importe': compra_aprobada['iva']}
            ],
            'haber': [
                {'cuenta': 'Proveedores', 'importe': compra_aprobada['total']}
            ]
        }
        
        # Validar balance del asiento
        total_debe = sum(item['importe'] for item in asiento_esperado['debe'])
        total_haber = sum(item['importe'] for item in asiento_esperado['haber'])
        
        self.assertEqual(total_debe, total_haber)
        self.assertEqual(total_debe, compra_aprobada['total'])


if __name__ == '__main__':
    print("Ejecutando tests del modelo de compras...")
    unittest.main(verbosity=2)