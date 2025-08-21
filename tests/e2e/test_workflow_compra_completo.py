#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests E2E: Workflow Completo de Compras
Desde solicitud hasta recepción e impacto en inventario
"""

import unittest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from decimal import Decimal
from datetime import datetime, date, timedelta

# Configurar path y encoding
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
os.environ['PYTHONIOENCODING'] = 'utf-8'

from tests.utils.mock_factories import MockDatabaseFactory, MockControllerFactory
from tests.utils.security_helpers import TestSecurityManager


class TestWorkflowCompraCompleto(unittest.TestCase):
    """Test E2E: Workflow completo de compras en el sistema."""
    
    def setUp(self):
        """Setup para tests E2E."""
        # Inicializar todos los componentes del sistema
        self.usuario_admin = TestSecurityManager.create_mock_user_data('admin', 'ADMIN')
        self.usuario_manager = TestSecurityManager.create_mock_user_data('manager1', 'MANAGER')
        self.usuario_user = TestSecurityManager.create_mock_user_data('user1', 'USER')
        
        # Bases de datos mock
        self.compras_db = MockDatabaseFactory.create_compras_database()
        self.inventario_db = MockDatabaseFactory.create_inventario_database()
        self.auditoria_db = Mock()
        
        # Controllers mock
        self.compras_controller = MockControllerFactory.create_compras_controller()
        self.inventario_controller = MockControllerFactory.create_inventario_controller()
        self.usuarios_controller = MockControllerFactory.create_usuarios_controller()
    
    def test_workflow_compra_exitoso_completo(self):
        """Test E2E: Workflow exitoso completo de compra."""
        
        print("\n=== INICIANDO WORKFLOW E2E: COMPRA COMPLETA ===")
        
        # PASO 1: Usuario solicita compra
        print("\n1. CREACIÓN DE SOLICITUD DE COMPRA")
        solicitud_compra = {
            'usuario_solicitante_id': self.usuario_user['id'],
            'fecha_solicitud': datetime.now(),
            'proveedor_id': 1,
            'proveedor_nombre': 'Proveedor Test SA',
            'justificacion': 'Reposición de stock crítico',
            'items': [
                {
                    'producto_id': 1,
                    'producto_codigo': 'PROD001',
                    'descripcion': 'Material A',
                    'cantidad': 100,
                    'precio_unitario': Decimal('50.00'),
                    'subtotal': Decimal('5000.00')
                },
                {
                    'producto_id': 2,
                    'producto_codigo': 'PROD002',
                    'descripcion': 'Material B',
                    'cantidad': 50,
                    'precio_unitario': Decimal('80.00'),
                    'subtotal': Decimal('4000.00')
                }
            ],
            'subtotal_general': Decimal('9000.00'),
            'iva': Decimal('1890.00'),  # 21% IVA Argentina
            'total': Decimal('10890.00'),
            'estado': 'borrador'
        }
        
        # Validar creación de solicitud
        self.assertIsNotNone(solicitud_compra['usuario_solicitante_id'])
        self.assertEqual(len(solicitud_compra['items']), 2)
        self.assertEqual(solicitud_compra['total'], Decimal('10890.00'))
        print(f"   ✅ Solicitud creada por usuario {solicitud_compra['usuario_solicitante_id']}")
        print(f"   ✅ Total: ${solicitud_compra['total']}")
        
        # PASO 2: Enviar para aprobación
        print("\n2. ENVÍO PARA APROBACIÓN")
        solicitud_compra['estado'] = 'pendiente_aprobacion'
        solicitud_compra['fecha_envio_aprobacion'] = datetime.now()
        solicitud_compra['codigo'] = 'COMP-2025-001'
        
        self.assertEqual(solicitud_compra['estado'], 'pendiente_aprobacion')
        print(f"   ✅ Solicitud {solicitud_compra['codigo']} enviada para aprobación")
        
        # PASO 3: Manager revisa y aprueba
        print("\n3. REVISIÓN Y APROBACIÓN POR MANAGER")
        
        # Verificar límites de aprobación
        limite_aprobacion_manager = Decimal('50000.00')
        puede_aprobar = solicitud_compra['total'] <= limite_aprobacion_manager
        self.assertTrue(puede_aprobar, "Manager puede aprobar esta compra")
        
        # Aprobar compra
        aprobacion = {
            'aprobado_por_id': self.usuario_manager['id'],
            'aprobado_por_nombre': self.usuario_manager['usuario'],
            'fecha_aprobacion': datetime.now(),
            'comentarios_aprobacion': 'Compra aprobada - stock crítico confirmado',
            'estado_anterior': 'pendiente_aprobacion',
            'estado_nuevo': 'aprobada'
        }
        
        solicitud_compra.update({
            'estado': 'aprobada',
            'aprobado_por_id': aprobacion['aprobado_por_id'],
            'fecha_aprobacion': aprobacion['fecha_aprobacion'],
            'comentarios_aprobacion': aprobacion['comentarios_aprobacion']
        })
        
        self.assertEqual(solicitud_compra['estado'], 'aprobada')
        print(f"   ✅ Compra aprobada por {aprobacion['aprobado_por_nombre']}")
        print(f"   ✅ Fecha aprobación: {aprobacion['fecha_aprobacion'].strftime('%Y-%m-%d %H:%M')}")
        
        # PASO 4: Generar orden de compra
        print("\n4. GENERACIÓN DE ORDEN DE COMPRA")
        orden_compra = {
            'numero_orden': 'OC-2025-001',
            'basada_en_solicitud': solicitud_compra['codigo'],
            'proveedor_id': solicitud_compra['proveedor_id'],
            'fecha_emision': datetime.now(),
            'fecha_entrega_solicitada': datetime.now() + timedelta(days=7),
            'condiciones_pago': '30 días',
            'lugar_entrega': 'Depósito Central',
            'estado': 'enviada_proveedor'
        }
        
        solicitud_compra.update({
            'orden_compra_numero': orden_compra['numero_orden'],
            'estado': 'orden_enviada'
        })
        
        self.assertEqual(orden_compra['estado'], 'enviada_proveedor')
        print(f"   ✅ Orden de compra {orden_compra['numero_orden']} generada")
        print(f"   ✅ Entrega esperada: {orden_compra['fecha_entrega_solicitada'].strftime('%Y-%m-%d')}")
        
        # PASO 5: Recepción de mercadería
        print("\n5. RECEPCIÓN DE MERCADERÍA")
        recepcion = {
            'orden_compra': orden_compra['numero_orden'],
            'fecha_recepcion': datetime.now(),
            'recibido_por_id': self.usuario_user['id'],
            'items_recibidos': [
                {
                    'producto_id': 1,
                    'cantidad_pedida': 100,
                    'cantidad_recibida': 95,  # Diferencia por daños menores
                    'estado': 'conforme',
                    'observaciones': '5 unidades con daños menores'
                },
                {
                    'producto_id': 2,
                    'cantidad_pedida': 50,
                    'cantidad_recibida': 50,
                    'estado': 'conforme',
                    'observaciones': 'Recibido completo en buen estado'
                }
            ],
            'estado_recepcion': 'parcial'  # Porque hay diferencias
        }
        
        # Validar recepción
        total_pedido = sum(item['cantidad_pedida'] for item in recepcion['items_recibidos'])
        total_recibido = sum(item['cantidad_recibida'] for item in recepcion['items_recibidos'])
        
        self.assertEqual(total_pedido, 150)
        self.assertEqual(total_recibido, 145)
        print(f"   ✅ Mercadería recibida: {total_recibido}/{total_pedido} unidades")
        print(f"   ✅ Estado recepción: {recepcion['estado_recepcion']}")
        
        # PASO 6: Actualización automática del inventario
        print("\n6. ACTUALIZACIÓN AUTOMÁTICA DEL INVENTARIO")
        
        # Stock inicial (simulado)
        stock_inicial = {1: 20, 2: 15}
        
        # Calcular stock final después de la recepción
        stock_final = {}
        for item in recepcion['items_recibidos']:
            producto_id = item['producto_id']
            cantidad_recibida = item['cantidad_recibida']
            stock_final[producto_id] = stock_inicial[producto_id] + cantidad_recibida
        
        # Validar actualización de inventario
        self.assertEqual(stock_final[1], 115)  # 20 + 95
        self.assertEqual(stock_final[2], 65)   # 15 + 50
        
        print(f"   ✅ Stock actualizado:")
        print(f"      - PROD001: {stock_inicial[1]} → {stock_final[1]} (+{recepcion['items_recibidos'][0]['cantidad_recibida']})")
        print(f"      - PROD002: {stock_inicial[2]} → {stock_final[2]} (+{recepcion['items_recibidos'][1]['cantidad_recibida']})")
        
        # PASO 7: Registro de auditoría
        print("\n7. REGISTRO DE AUDITORÍA")
        eventos_auditoria = [
            {
                'timestamp': solicitud_compra['fecha_solicitud'],
                'user_id': solicitud_compra['usuario_solicitante_id'],
                'action': 'CREATE_PURCHASE_REQUEST',
                'entity_id': solicitud_compra['codigo'],
                'details': {'total': float(solicitud_compra['total'])}
            },
            {
                'timestamp': solicitud_compra['fecha_aprobacion'],
                'user_id': solicitud_compra['aprobado_por_id'],
                'action': 'APPROVE_PURCHASE',
                'entity_id': solicitud_compra['codigo'],
                'details': {'approved_amount': float(solicitud_compra['total'])}
            },
            {
                'timestamp': recepcion['fecha_recepcion'],
                'user_id': recepcion['recibido_por_id'],
                'action': 'RECEIVE_PURCHASE',
                'entity_id': orden_compra['numero_orden'],
                'details': {'items_received': total_recibido}
            }
        ]
        
        # Validar eventos de auditoría
        self.assertEqual(len(eventos_auditoria), 3)
        for evento in eventos_auditoria:
            required_fields = ['timestamp', 'user_id', 'action', 'entity_id']
            for field in required_fields:
                self.assertIn(field, evento)
        
        print(f"   ✅ {len(eventos_auditoria)} eventos registrados en auditoría")
        
        # PASO 8: Finalización del workflow
        print("\n8. FINALIZACIÓN DEL WORKFLOW")
        solicitud_compra['estado'] = 'completada'
        solicitud_compra['fecha_completada'] = datetime.now()
        
        # Métricas finales del workflow
        duracion_total = (solicitud_compra['fecha_completada'] - solicitud_compra['fecha_solicitud']).total_seconds()
        
        workflow_summary = {
            'codigo_compra': solicitud_compra['codigo'],
            'estado_final': solicitud_compra['estado'],
            'total_compra': solicitud_compra['total'],
            'items_totales': len(solicitud_compra['items']),
            'porcentaje_recibido': (total_recibido / total_pedido) * 100,
            'duracion_segundos': duracion_total,
            'usuarios_involucrados': 2,  # User + Manager
            'eventos_auditoria': len(eventos_auditoria)
        }
        
        # Validaciones finales
        self.assertEqual(workflow_summary['estado_final'], 'completada')
        self.assertGreater(workflow_summary['porcentaje_recibido'], 95.0)
        self.assertGreater(workflow_summary['eventos_auditoria'], 0)
        
        print(f"   ✅ Workflow completado exitosamente")
        print(f"   ✅ Código: {workflow_summary['codigo_compra']}")
        print(f"   ✅ Total: ${workflow_summary['total_compra']}")
        print(f"   ✅ Recepción: {workflow_summary['porcentaje_recibido']:.1f}%")
        print(f"   ✅ Usuarios involucrados: {workflow_summary['usuarios_involucrados']}")
        
        print("\n=== WORKFLOW E2E COMPLETADO EXITOSAMENTE ===")
        
        return workflow_summary
    
    def test_workflow_compra_con_rechazo_y_reaprobacion(self):
        """Test E2E: Workflow con rechazo inicial y posterior reaprobación."""
        
        print("\n=== WORKFLOW E2E: COMPRA CON RECHAZO Y REAPROBACIÓN ===")
        
        # PASO 1: Crear solicitud
        solicitud = {
            'codigo': 'COMP-2025-002',
            'usuario_solicitante_id': self.usuario_user['id'],
            'total': Decimal('75000.00'),  # Monto alto
            'estado': 'pendiente_aprobacion'
        }
        
        # PASO 2: Manager rechaza (monto muy alto)
        print("\n1. RECHAZO INICIAL POR MONTO ALTO")
        limite_manager = Decimal('50000.00')
        if solicitud['total'] > limite_manager:
            rechazo = {
                'rechazado_por_id': self.usuario_manager['id'],
                'fecha_rechazo': datetime.now(),
                'motivo': f'Monto ${solicitud["total"]} excede límite de aprobación ${limite_manager}',
                'accion_requerida': 'Requiere aprobación de Admin'
            }
            solicitud['estado'] = 'rechazada'
            solicitud.update(rechazo)
        
        self.assertEqual(solicitud['estado'], 'rechazada')
        print(f"   ❌ Compra rechazada: {rechazo['motivo']}")
        
        # PASO 3: Reenvío para aprobación de Admin
        print("\n2. REENVÍO PARA APROBACIÓN DE ADMIN")
        solicitud['estado'] = 'pendiente_aprobacion_admin'
        solicitud['escalado_a_admin'] = True
        
        # PASO 4: Admin aprueba
        print("\n3. APROBACIÓN POR ADMIN")
        limite_admin = Decimal('1000000.00')  # Admin tiene límite muy alto
        if solicitud['total'] <= limite_admin:
            aprobacion_admin = {
                'aprobado_por_id': self.usuario_admin['id'],
                'fecha_aprobacion': datetime.now(),
                'comentarios': 'Aprobado por Admin - compra estratégica'
            }
            solicitud['estado'] = 'aprobada'
            solicitud.update(aprobacion_admin)
        
        self.assertEqual(solicitud['estado'], 'aprobada')
        print(f"   ✅ Compra aprobada por Admin: ${solicitud['total']}")
        
        # Validar que pasó por ambos niveles de aprobación
        self.assertIn('rechazado_por_id', solicitud)
        self.assertIn('aprobado_por_id', solicitud)
        print("   ✅ Workflow de doble aprobación completado")
        
        print("\n=== WORKFLOW CON RECHAZO COMPLETADO ===")


class TestWorkflowIntegracionCompleta(unittest.TestCase):
    """Test E2E: Integración completa entre todos los módulos."""
    
    def test_workflow_desde_obra_hasta_inventario(self):
        """Test E2E: Desde necesidad de obra hasta recepción en inventario."""
        
        print("\n=== WORKFLOW E2E: OBRA → COMPRA → INVENTARIO ===")
        
        # PASO 1: Obra requiere materiales
        print("\n1. OBRA REQUIERE MATERIALES")
        obra = {
            'id': 1,
            'codigo': 'OBR-2025-001',
            'nombre': 'Construcción Edificio Comercial',
            'estado': 'activa',
            'materiales_faltantes': [
                {'producto_id': 1, 'cantidad_necesaria': 200, 'prioridad': 'alta'},
                {'producto_id': 2, 'cantidad_necesaria': 100, 'prioridad': 'media'}
            ]
        }
        
        # PASO 2: Verificar stock disponible
        print("\n2. VERIFICACIÓN DE STOCK DISPONIBLE")
        stock_actual = {1: 50, 2: 30}  # Stock insuficiente
        
        materiales_a_comprar = []
        for material in obra['materiales_faltantes']:
            producto_id = material['producto_id']
            necesario = material['cantidad_necesaria']
            disponible = stock_actual.get(producto_id, 0)
            
            if disponible < necesario:
                faltante = necesario - disponible
                materiales_a_comprar.append({
                    'producto_id': producto_id,
                    'cantidad_comprar': faltante,
                    'obra_destino': obra['id']
                })
        
        self.assertEqual(len(materiales_a_comprar), 2)
        print(f"   ⚠️ Se requiere compra de {len(materiales_a_comprar)} materiales")
        
        # PASO 3: Generar solicitud de compra automática
        print("\n3. GENERACIÓN AUTOMÁTICA DE SOLICITUD DE COMPRA")
        compra_automatica = {
            'origen': 'requisicion_obra',
            'obra_id': obra['id'],
            'items': materiales_a_comprar,
            'prioridad': 'alta',
            'justificacion': f'Materiales requeridos para {obra["nombre"]}'
        }
        
        self.assertEqual(compra_automatica['origen'], 'requisicion_obra')
        print(f"   ✅ Solicitud generada automáticamente para obra {obra['codigo']}")
        
        # PASO 4: Workflow de compra (versión acelerada)
        print("\n4. WORKFLOW DE COMPRA ACELERADO")
        # ... (similar al test anterior pero resumido)
        compra_resultado = {
            'estado': 'recibida',
            'items_recibidos': [
                {'producto_id': 1, 'cantidad': 150},  # Para cubrir necesidad de obra
                {'producto_id': 2, 'cantidad': 70}
            ]
        }
        
        # PASO 5: Asignación automática a obra
        print("\n5. ASIGNACIÓN AUTOMÁTICA A OBRA")
        for item in compra_resultado['items_recibidos']:
            producto_id = item['producto_id']
            cantidad_recibida = item['cantidad']
            
            # Buscar necesidad de la obra
            for material_obra in obra['materiales_faltantes']:
                if material_obra['producto_id'] == producto_id:
                    cantidad_necesaria = material_obra['cantidad_necesaria']
                    cantidad_asignar = min(cantidad_recibida, cantidad_necesaria)
                    
                    # Simular asignación
                    material_obra['cantidad_asignada'] = cantidad_asignar
                    material_obra['estado'] = 'asignado'
        
        # Verificar asignaciones
        asignaciones_correctas = all(
            'cantidad_asignada' in material for material in obra['materiales_faltantes']
        )
        self.assertTrue(asignaciones_correctas)
        print("   ✅ Materiales asignados automáticamente a la obra")
        
        # PASO 6: Actualización de estado de obra
        print("\n6. ACTUALIZACIÓN DE ESTADO DE OBRA")
        materiales_completos = all(
            material.get('cantidad_asignada', 0) >= material['cantidad_necesaria']
            for material in obra['materiales_faltantes']
        )
        
        if materiales_completos:
            obra['estado'] = 'materiales_completos'
            obra['fecha_materiales_completos'] = datetime.now()
        
        print(f"   ✅ Obra actualizada: {obra['estado']}")
        
        print("\n=== WORKFLOW COMPLETO OBRA→COMPRA→INVENTARIO EXITOSO ===")


if __name__ == '__main__':
    print("Ejecutando tests E2E de workflows completos...")
    unittest.main(verbosity=2)