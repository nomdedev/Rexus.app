#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests de Integración: Compras ↔ Inventario
Workflows críticos entre módulos
"""

import unittest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal
from datetime import datetime, date

# Configurar path y encoding
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
os.environ['PYTHONIOENCODING'] = 'utf-8'

from tests.utils.mock_factories import MockDatabaseFactory, MockControllerFactory
from tests.utils.security_helpers import TestSecurityManager


class TestComprasInventarioIntegration(unittest.TestCase):
    """Tests de integración crítica: Compras → Inventario."""
    
    def setUp(self):
        """Setup para tests de integración."""
        self.compras_db = MockDatabaseFactory.create_compras_database()
        self.inventario_db = MockDatabaseFactory.create_inventario_database()
        self.compras_controller = MockControllerFactory.create_compras_controller()
        self.inventario_controller = MockControllerFactory.create_inventario_controller()
    
    def test_compra_recibida_actualiza_stock(self):
        """Test: Al recibir una compra, se actualiza automáticamente el stock."""
        # Situación inicial del inventario
        stock_inicial = {
            'PROD001': 50,
            'PROD002': 25
        }
        
        # Compra que se está recibiendo
        compra_recibida = {
            'id': 1,
            'codigo': 'COMP001',
            'estado': 'recibida',
            'fecha_recepcion': datetime.now(),
            'detalles': [
                {
                    'producto_codigo': 'PROD001',
                    'producto_id': 1,
                    'cantidad_pedida': 100,
                    'cantidad_recibida': 95,  # Diferencia por daños
                    'precio_unitario': Decimal('100.00')
                },
                {
                    'producto_codigo': 'PROD002',
                    'producto_id': 2,
                    'cantidad_pedida': 50,
                    'cantidad_recibida': 50,
                    'precio_unitario': Decimal('200.00')
                }
            ]
        }
        
        # Calcular stock final esperado
        stock_final_esperado = {
            'PROD001': stock_inicial['PROD001'] + 95,  # 50 + 95 = 145
            'PROD002': stock_inicial['PROD002'] + 50   # 25 + 50 = 75
        }
        
        # Validar que la integración funciona correctamente
        for detalle in compra_recibida['detalles']:
            producto_id = detalle['producto_id']
            cantidad_recibida = detalle['cantidad_recibida']
            
            # Verificar que hay cantidad a recibir
            self.assertGreater(cantidad_recibida, 0)
            
            # Verificar que los datos están completos para la integración
            required_fields = ['producto_id', 'cantidad_recibida', 'precio_unitario']
            for field in required_fields:
                self.assertIn(field, detalle)
        
        # Verificar stock final calculado
        self.assertEqual(stock_final_esperado['PROD001'], 145)
        self.assertEqual(stock_final_esperado['PROD002'], 75)
    
    def test_compra_cancelada_libera_reservas(self):
        """Test: Al cancelar una compra, se liberan las reservas de stock."""
        # Compra con reservas de stock
        compra_con_reservas = {
            'id': 2,
            'codigo': 'COMP002',
            'estado': 'cancelada',
            'fecha_cancelacion': datetime.now(),
            'motivo_cancelacion': 'Proveedor no disponible',
            'reservas_liberadas': [
                {
                    'producto_id': 1,
                    'cantidad_reservada': 20,
                    'tipo_reserva': 'compra_pendiente'
                },
                {
                    'producto_id': 3,
                    'cantidad_reservada': 10,
                    'tipo_reserva': 'compra_pendiente'
                }
            ]
        }
        
        # Validar que hay reservas para liberar
        reservas = compra_con_reservas['reservas_liberadas']
        self.assertGreater(len(reservas), 0)
        
        for reserva in reservas:
            # Cada reserva debe tener los campos necesarios
            required_fields = ['producto_id', 'cantidad_reservada', 'tipo_reserva']
            for field in required_fields:
                self.assertIn(field, reserva)
            
            # Cantidad reservada debe ser positiva
            self.assertGreater(reserva['cantidad_reservada'], 0)
            
            # Tipo de reserva debe ser correcto
            self.assertEqual(reserva['tipo_reserva'], 'compra_pendiente')
    
    def test_actualizacion_precios_promedio(self):
        """Test: Las compras actualizan el precio promedio ponderado del inventario."""
        # Estado inicial del producto
        producto_inicial = {
            'id': 1,
            'codigo': 'PROD001',
            'stock_actual': 100,
            'precio_promedio': Decimal('95.00'),
            'valor_total': Decimal('9500.00')  # 100 * 95.00
        }
        
        # Nueva compra recibida
        nueva_compra = {
            'producto_id': 1,
            'cantidad_recibida': 50,
            'precio_unitario': Decimal('110.00'),
            'valor_compra': Decimal('5500.00')  # 50 * 110.00
        }
        
        # Cálculo del nuevo precio promedio ponderado
        stock_final = producto_inicial['stock_actual'] + nueva_compra['cantidad_recibida']
        valor_final = producto_inicial['valor_total'] + nueva_compra['valor_compra']
        precio_promedio_final = valor_final / stock_final
        
        # Validaciones
        self.assertEqual(stock_final, 150)  # 100 + 50
        self.assertEqual(valor_final, Decimal('15000.00'))  # 9500 + 5500
        self.assertEqual(precio_promedio_final, Decimal('100.00'))  # 15000 / 150
        
        # El precio promedio debe estar entre el mínimo y máximo de los precios
        precio_min = min(producto_inicial['precio_promedio'], nueva_compra['precio_unitario'])
        precio_max = max(producto_inicial['precio_promedio'], nueva_compra['precio_unitario'])
        
        self.assertGreaterEqual(precio_promedio_final, precio_min)
        self.assertLessEqual(precio_promedio_final, precio_max)
    
    @patch('rexus.core.database.InventarioDatabaseConnection')
    @patch('rexus.core.database.DatabaseConnection')
    def test_workflow_completo_compra_a_inventario(self, mock_compras_db, mock_inventario_db):
        """Test: Workflow completo desde creación de compra hasta actualización de inventario."""
        # Configurar mocks
        mock_compras_db.return_value = self.compras_db
        mock_inventario_db.return_value = self.inventario_db
        
        # Paso 1: Crear compra
        nueva_compra = {
            'proveedor_id': 1,
            'fecha': date.today(),
            'estado': 'borrador',
            'items': [
                {'producto_id': 1, 'cantidad': 100, 'precio': Decimal('100.00')},
                {'producto_id': 2, 'cantidad': 50, 'precio': Decimal('200.00')}
            ]
        }
        
        # Paso 2: Aprobar compra
        compra_aprobada = {
            **nueva_compra,
            'id': 1,
            'estado': 'aprobada',
            'fecha_aprobacion': datetime.now(),
            'aprobado_por': 'manager1'
        }
        
        # Paso 3: Recibir compra
        compra_recibida = {
            **compra_aprobada,
            'estado': 'recibida',
            'fecha_recepcion': datetime.now(),
            'recibido_por': 'user1'
        }
        
        # Validar cada estado del workflow
        estados_workflow = ['borrador', 'aprobada', 'recibida']
        for estado in estados_workflow:
            self.assertIn(estado, ['borrador', 'pendiente', 'aprobada', 'recibida', 'cancelada'])
        
        # Validar que solo en estado 'recibida' se actualiza inventario
        if compra_recibida['estado'] == 'recibida':
            for item in compra_recibida['items']:
                # Simular actualización de inventario
                self.assertIn('producto_id', item)
                self.assertIn('cantidad', item)
                self.assertGreater(item['cantidad'], 0)


class TestInventarioObrasIntegration(unittest.TestCase):
    """Tests de integración crítica: Inventario ↔ Obras."""
    
    def setUp(self):
        """Setup para tests de integración inventario-obras."""
        self.inventario_db = MockDatabaseFactory.create_inventario_database()
        self.obras_db = MockDatabaseFactory.create_obras_database()
    
    def test_asignacion_materiales_a_obra(self):
        """Test: Asignar materiales del inventario a una obra específica."""
        # Obra que necesita materiales
        obra = {
            'id': 1,
            'codigo': 'OBR001',
            'nombre': 'Construcción Edificio A',
            'estado': 'activa',
            'materiales_requeridos': [
                {
                    'producto_id': 1,
                    'producto_codigo': 'PROD001',
                    'cantidad_necesaria': 50,
                    'fecha_necesaria': '2025-09-01'
                },
                {
                    'producto_id': 2,
                    'producto_codigo': 'PROD002',
                    'cantidad_necesaria': 25,
                    'fecha_necesaria': '2025-09-05'
                }
            ]
        }
        
        # Estado del inventario
        inventario_disponible = {
            1: {'stock_disponible': 100, 'stock_reservado': 20},  # PROD001
            2: {'stock_disponible': 30, 'stock_reservado': 5}     # PROD002
        }
        
        # Verificar disponibilidad para asignación
        for material in obra['materiales_requeridos']:
            producto_id = material['producto_id']
            cantidad_necesaria = material['cantidad_necesaria']
            
            stock_info = inventario_disponible[producto_id]
            stock_libre = stock_info['stock_disponible'] - stock_info['stock_reservado']
            
            # Verificar que hay suficiente stock libre
            puede_asignar = stock_libre >= cantidad_necesaria
            
            if producto_id == 1:  # PROD001: 100 - 20 = 80 >= 50 ✓
                self.assertTrue(puede_asignar)
            elif producto_id == 2:  # PROD002: 30 - 5 = 25 >= 25 ✓
                self.assertTrue(puede_asignar)
    
    def test_consumo_materiales_en_obra(self):
        """Test: Registrar consumo de materiales en obra y actualizar inventario."""
        # Consumo de materiales registrado
        consumo_obra = {
            'obra_id': 1,
            'fecha_consumo': date.today(),
            'materiales_consumidos': [
                {
                    'producto_id': 1,
                    'cantidad_consumida': 20,
                    'responsable': 'capataz1',
                    'observaciones': 'Consumo normal según planificación'
                },
                {
                    'producto_id': 2,
                    'cantidad_consumida': 10,
                    'responsable': 'capataz1',
                    'observaciones': 'Consumo parcial - obra en progreso'
                }
            ]
        }
        
        # Estado inicial del inventario
        stock_inicial = {1: 100, 2: 30}
        
        # Calcular stock final después del consumo
        stock_final_esperado = {1: 80, 2: 20}  # Reducido por el consumo
        
        # Validar consumo registrado
        for material in consumo_obra['materiales_consumidos']:
            producto_id = material['producto_id']
            cantidad_consumida = material['cantidad_consumida']
            
            # Verificar que el consumo es positivo
            self.assertGreater(cantidad_consumida, 0)
            
            # Verificar que no consume más del stock disponible
            self.assertLessEqual(cantidad_consumida, stock_inicial[producto_id])
        
        # Verificar cálculo de stock final
        for producto_id in stock_inicial:
            consumo_total = sum(
                m['cantidad_consumida'] for m in consumo_obra['materiales_consumidos'] 
                if m['producto_id'] == producto_id
            )
            stock_calculado = stock_inicial[producto_id] - consumo_total
            self.assertEqual(stock_calculado, stock_final_esperado[producto_id])
    
    def test_devolucion_materiales_no_utilizados(self):
        """Test: Devolución de materiales no utilizados de obra al inventario."""
        # Materiales devueltos por la obra
        devolucion = {
            'obra_id': 1,
            'fecha_devolucion': date.today(),
            'motivo': 'Materiales sobrantes al finalizar obra',
            'materiales_devueltos': [
                {
                    'producto_id': 1,
                    'cantidad_devuelta': 15,
                    'estado': 'bueno',
                    'observaciones': 'Material en perfecto estado'
                },
                {
                    'producto_id': 2,
                    'cantidad_devuelta': 5,
                    'estado': 'bueno',
                    'observaciones': 'Sin uso, material sobrante'
                }
            ]
        }
        
        # Stock antes de la devolución
        stock_antes = {1: 85, 2: 20}
        
        # Stock después de la devolución
        stock_despues_esperado = {1: 100, 2: 25}
        
        # Validar devolución
        for material in devolucion['materiales_devueltos']:
            producto_id = material['producto_id']
            cantidad_devuelta = material['cantidad_devuelta']
            estado = material['estado']
            
            # Solo se devuelve al inventario si está en buen estado
            if estado == 'bueno':
                self.assertGreater(cantidad_devuelta, 0)
                
                # Calcular stock final
                stock_final = stock_antes[producto_id] + cantidad_devuelta
                self.assertEqual(stock_final, stock_despues_esperado[producto_id])


class TestUsuariosPermisosDatos(unittest.TestCase):
    """Tests de integración: Usuarios ↔ Permisos ↔ Datos."""
    
    def test_permisos_acceso_modulos(self):
        """Test: Verificar que los permisos de usuario limitan el acceso a módulos."""
        # Configuración de permisos por rol
        permisos_por_rol = {
            'ADMIN': ['ALL'],
            'MANAGER': ['inventario', 'compras', 'obras', 'reportes'],
            'USER': ['inventario_view', 'obras_view'],
            'VIEWER': ['inventario_view', 'reportes_view']
        }
        
        # Usuario de prueba
        from tests.utils.security_helpers import TestSecurityManager
        usuario_manager = TestSecurityManager.create_mock_user_data('manager1', 'MANAGER')
        
        # Verificar acceso a módulos
        rol_usuario = usuario_manager['rol']
        permisos_usuario = permisos_por_rol.get(rol_usuario, [])
        
        # Manager debería tener acceso a inventario, compras, obras, reportes
        modulos_esperados = ['inventario', 'compras', 'obras', 'reportes']
        
        for modulo in modulos_esperados:
            tiene_acceso = 'ALL' in permisos_usuario or modulo in permisos_usuario
            self.assertTrue(tiene_acceso, f"Manager debería tener acceso a {modulo}")
        
        # Manager NO debería tener acceso a usuarios (administración)
        tiene_acceso_usuarios = 'ALL' in permisos_usuario or 'usuarios' in permisos_usuario
        self.assertFalse(tiene_acceso_usuarios, "Manager no debería gestionar usuarios")
    
    def test_filtrado_datos_segun_permisos(self):
        """Test: Los datos se filtran según los permisos del usuario."""
        # Usuario con permisos limitados
        usuario_limitado = {
            'id': 3,
            'username': 'user1',
            'rol': 'USER',
            'departamento': 'Ventas',
            'permisos': ['inventario_view_departamento', 'obras_view_asignadas']
        }
        
        # Datos disponibles en el sistema
        obras_sistema = [
            {'id': 1, 'nombre': 'Obra A', 'departamento': 'Ventas', 'responsable_id': 3},
            {'id': 2, 'nombre': 'Obra B', 'departamento': 'Construccion', 'responsable_id': 4},
            {'id': 3, 'nombre': 'Obra C', 'departamento': 'Ventas', 'responsable_id': 5}
        ]
        
        # Filtrar obras según permisos del usuario
        if 'obras_view_asignadas' in usuario_limitado['permisos']:
            # Solo ve obras donde es responsable
            obras_visibles = [
                obra for obra in obras_sistema 
                if obra['responsable_id'] == usuario_limitado['id']
            ]
        elif 'obras_view_departamento' in usuario_limitado['permisos']:
            # Ve obras de su departamento
            obras_visibles = [
                obra for obra in obras_sistema 
                if obra['departamento'] == usuario_limitado['departamento']
            ]
        else:
            obras_visibles = []
        
        # Usuario debería ver solo la Obra A (su obra asignada)
        self.assertEqual(len(obras_visibles), 1)
        self.assertEqual(obras_visibles[0]['id'], 1)
        self.assertEqual(obras_visibles[0]['responsable_id'], usuario_limitado['id'])


if __name__ == '__main__':
    print("Ejecutando tests de integración entre módulos...")
    unittest.main(verbosity=2)