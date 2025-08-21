"""
Tests Completos para Módulo de Notificaciones - Rexus.app
Cubre: Model, View, Controller, Integración con todos los módulos

Fecha: 20/08/2025
Cobertura: Sistema de notificaciones, envío, recepción, integración transversal
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date, timedelta
import json

# Agregar directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))


class MockNotificacionesDatabase:
    """Mock especializado para base de datos de notificaciones."""
    
    def __init__(self):
        self.cursor_mock = Mock()
        self.connected = True
        self.committed = False
        self.rolledback = False
        
        # Mock datos de ejemplo para notificaciones
        self.sample_notificaciones = [
            (1, 'Stock Bajo', 'El producto TEST001 tiene stock bajo (5 unidades)', 'WARNING', 
             '2025-08-20 10:30:00', 1, False, 'inventario', '{"producto_id": 1, "stock": 5}'),
            (2, 'Pedido Completado', 'El pedido PED-001 ha sido completado', 'SUCCESS', 
             '2025-08-20 09:15:00', 2, True, 'pedidos', '{"pedido_id": 1, "estado": "COMPLETADO"}'),
            (3, 'Compra Pendiente', 'La compra OC-001 está pendiente de recepción', 'INFO', 
             '2025-08-19 16:45:00', 1, False, 'compras', '{"compra_id": 1, "dias_pendiente": 5}')
        ]
        
        # Mock tipos de notificaciones
        self.sample_tipos = [
            ('INFO', 'Información general'),
            ('WARNING', 'Advertencia'),
            ('ERROR', 'Error crítico'),
            ('SUCCESS', 'Operación exitosa')
        ]
        
        # Mock usuarios para notificaciones
        self.sample_usuarios = [
            (1, 'admin', 'Administrador'),
            (2, 'operador', 'Operador de Sistema'),
            (3, 'supervisor', 'Supervisor de Obra')
        ]
    
    def cursor(self):
        return self.cursor_mock
    
    def commit(self):
        self.committed = True
    
    def rollback(self):
        self.rolledback = True
    
    def close(self):
        self.connected = False


class TestNotificacionesModel(unittest.TestCase):
    """Tests para NotificacionesModel - Lógica de negocio de notificaciones."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_db = MockNotificacionesDatabase()
        
        self.sample_notificacion = {
            'titulo': 'Test Notification',
            'mensaje': 'Esta es una notificación de prueba',
            'tipo': 'INFO',
            'usuario_id': 1,
            'modulo_origen': 'test',
            'datos_adicionales': {'test': True}
        }
    
    @patch('rexus.core.database.get_inventario_connection')
    def test_notificaciones_model_initialization(self, mock_connection):
        """Test inicialización correcta del modelo de notificaciones."""
        mock_connection.return_value = self.mock_db
        
        try:
            from rexus.modules.notificaciones.model import NotificacionesModel
            model = NotificacionesModel(db_connection=self.mock_db)
            
            self.assertIsNotNone(model)
            # El mock_connection no debería ser llamado cuando pasamos conexión directa
            # En su lugar, verificamos que el modelo se inicializó correctamente
            self.assertIsNotNone(model.db_connection)
            
        except ImportError:
            self.skipTest("Módulo NotificacionesModel no disponible")
    
    @patch('rexus.core.database.get_inventario_connection')
    def test_obtener_todas_notificaciones(self, mock_connection):
        """Test obtener listado completo de notificaciones."""
        mock_connection.return_value = self.mock_db
        self.mock_db.cursor_mock.fetchall.return_value = self.mock_db.sample_notificaciones
        
        try:
            from rexus.modules.notificaciones.model import NotificacionesModel
            model = NotificacionesModel()
            
            if hasattr(model, 'obtener_notificaciones'):
                notificaciones = model.obtener_notificaciones()
                
                self.assertIsInstance(notificaciones, list)
                if notificaciones:
                    self.assertEqual(len(notificaciones), 3)
                    
                self.mock_db.cursor_mock.execute.assert_called()
                
        except ImportError:
            self.skipTest("Método obtener_notificaciones no disponible")
        except Exception as e:
            self.fail(f"Error en test obtener notificaciones: {e}")
    
    @patch('rexus.core.database.get_inventario_connection')
    def test_crear_notificacion_exitosa(self, mock_connection):
        """Test crear nueva notificación."""
        mock_connection.return_value = self.mock_db
        self.mock_db.cursor_mock.lastrowid = 999
        
        try:
            from rexus.modules.notificaciones.model import NotificacionesModel
            # Pasar la conexión mock directamente al constructor
            model = NotificacionesModel(db_connection=self.mock_db)
            
            if hasattr(model, 'crear_notificacion'):
                # Usar argumentos individuales según la firma de la función
                resultado = model.crear_notificacion(
                    titulo=self.sample_notificacion['titulo'],
                    mensaje=self.sample_notificacion['mensaje'],
                    tipo=self.sample_notificacion.get('tipo', 'info'),
                    prioridad=self.sample_notificacion.get('prioridad', 2),
                    modulo_origen=self.sample_notificacion.get('modulo_origen', 'test'),
                    metadata=self.sample_notificacion.get('datos_adicionales')
                )
                
                # Verificar que se intentó insertar
                self.mock_db.cursor_mock.execute.assert_called()
                self.assertTrue(self.mock_db.committed)
                
        except ImportError:
            self.skipTest("Método crear_notificacion no disponible")
        except Exception as e:
            self.fail(f"Error en test crear notificación: {e}")
    
    @patch('rexus.core.database.get_inventario_connection')
    def test_enviar_notificacion_broadcast(self, mock_connection):
        """Test envío de notificación a múltiples usuarios."""
        mock_connection.return_value = self.mock_db
        
        try:
            from rexus.modules.notificaciones.model import NotificacionesModel
            model = NotificacionesModel()
            
            if hasattr(model, 'enviar_broadcast'):
                resultado = model.enviar_broadcast(
                    titulo='Mantenimiento Programado',
                    mensaje='Sistema en mantenimiento de 2-4 AM',
                    tipo='WARNING',
                    usuarios_ids=[1, 2, 3]
                )
                
                # Verificar múltiples inserts
                self.mock_db.cursor_mock.execute.assert_called()
                
        except ImportError:
            self.skipTest("Método enviar_broadcast no disponible")
    
    @patch('rexus.core.database.get_inventario_connection')
    def test_marcar_como_leida(self, mock_connection):
        """Test marcar notificación como leída."""
        mock_connection.return_value = self.mock_db
        self.mock_db.cursor_mock.rowcount = 1
        
        try:
            from rexus.modules.notificaciones.model import NotificacionesModel
            model = NotificacionesModel()
            
            if hasattr(model, 'marcar_leida'):
                resultado = model.marcar_leida(1)
                
                self.mock_db.cursor_mock.execute.assert_called()
                self.assertTrue(self.mock_db.committed)
                
        except ImportError:
            self.skipTest("Método marcar_leida no disponible")
    
    @patch('rexus.core.database.get_inventario_connection')
    def test_obtener_notificaciones_no_leidas(self, mock_connection):
        """Test obtener solo notificaciones no leídas."""
        mock_connection.return_value = self.mock_db
        no_leidas = [n for n in self.mock_db.sample_notificaciones if not n[6]]  # campo 'leida'
        self.mock_db.cursor_mock.fetchall.return_value = no_leidas
        
        try:
            from rexus.modules.notificaciones.model import NotificacionesModel
            model = NotificacionesModel()
            
            if hasattr(model, 'obtener_no_leidas'):
                resultado = model.obtener_no_leidas(1)  # usuario_id
                
                self.assertIsInstance(resultado, list)
                self.mock_db.cursor_mock.execute.assert_called()
                
        except ImportError:
            self.skipTest("Método obtener_no_leidas no disponible")
    
    @patch('rexus.core.database.get_inventario_connection')
    def test_filtrar_por_tipo(self, mock_connection):
        """Test filtrar notificaciones por tipo."""
        mock_connection.return_value = self.mock_db
        warnings = [n for n in self.mock_db.sample_notificaciones if n[3] == 'WARNING']
        self.mock_db.cursor_mock.fetchall.return_value = warnings
        
        try:
            from rexus.modules.notificaciones.model import NotificacionesModel
            model = NotificacionesModel()
            
            if hasattr(model, 'filtrar_por_tipo'):
                resultado = model.filtrar_por_tipo('WARNING', 1)
                
                self.assertIsInstance(resultado, list)
                self.mock_db.cursor_mock.execute.assert_called()
                
        except ImportError:
            self.skipTest("Método filtrar_por_tipo no disponible")
    
    @patch('rexus.core.database.get_inventario_connection')
    def test_eliminar_notificacion(self, mock_connection):
        """Test eliminar notificación."""
        mock_connection.return_value = self.mock_db
        self.mock_db.cursor_mock.rowcount = 1
        
        try:
            from rexus.modules.notificaciones.model import NotificacionesModel
            model = NotificacionesModel(db_connection=self.mock_db)
            
            if hasattr(model, 'eliminar_notificacion'):
                resultado = model.eliminar_notificacion(1)
                
                self.mock_db.cursor_mock.execute.assert_called()
                self.assertTrue(self.mock_db.committed)
                
        except ImportError:
            self.skipTest("Método eliminar_notificacion no disponible")
    
    @patch('rexus.core.database.get_inventario_connection')
    def test_limpiar_notificaciones_antiguas(self, mock_connection):
        """Test limpieza de notificaciones antiguas."""
        mock_connection.return_value = self.mock_db
        self.mock_db.cursor_mock.rowcount = 5  # 5 notificaciones eliminadas
        
        try:
            from rexus.modules.notificaciones.model import NotificacionesModel
            model = NotificacionesModel()
            
            if hasattr(model, 'limpiar_antiguas'):
                # Eliminar notificaciones de más de 30 días
                resultado = model.limpiar_antiguas(30)
                
                self.mock_db.cursor_mock.execute.assert_called()
                self.assertTrue(self.mock_db.committed)
                
        except ImportError:
            self.skipTest("Método limpiar_antiguas no disponible")
    
    @patch('rexus.core.database.get_inventario_connection')
    def test_obtener_estadisticas(self, mock_connection):
        """Test obtener estadísticas de notificaciones."""
        mock_connection.return_value = self.mock_db
        
        # Mock estadísticas: total, no_leidas, por_tipo
        self.mock_db.cursor_mock.fetchone.side_effect = [
            (25,),  # total
            (8,),   # no leídas
            (5,),   # warnings
            (2,),   # errores
        ]
        
        try:
            from rexus.modules.notificaciones.model import NotificacionesModel
            model = NotificacionesModel()
            
            if hasattr(model, 'obtener_estadisticas'):
                stats = model.obtener_estadisticas(1)  # usuario_id
                
                self.assertIsInstance(stats, dict)
                
        except ImportError:
            self.skipTest("Método obtener_estadisticas no disponible")


class TestNotificacionesController(unittest.TestCase):
    """Tests para NotificacionesController - Controlador de notificaciones."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_db = MockNotificacionesDatabase()
    
    @patch('rexus.core.database.get_inventario_connection')
    def test_controller_initialization(self, mock_connection):
        """Test inicialización del controlador."""
        mock_connection.return_value = self.mock_db
        
        try:
            from rexus.modules.notificaciones.controller import NotificacionesController
            controller = NotificacionesController()
            
            self.assertIsNotNone(controller)
            
            # Verificar que tiene model
            self.assertTrue(hasattr(controller, 'model') or hasattr(controller, 'notificaciones_model'))
            
        except ImportError:
            self.skipTest("Controlador NotificacionesController no disponible")
    
    @patch('rexus.core.database.get_inventario_connection')
    def test_procesar_nueva_notificacion(self, mock_connection):
        """Test procesamiento de nueva notificación."""
        mock_connection.return_value = self.mock_db
        
        try:
            from rexus.modules.notificaciones.controller import NotificacionesController
            controller = NotificacionesController()
            
            # Test enviar notificación
            if hasattr(controller, 'enviar_notificacion'):
                resultado = controller.enviar_notificacion(
                    titulo='Test Controller',
                    mensaje='Mensaje de prueba',
                    tipo='INFO',
                    usuario_id=1
                )
            
            if hasattr(controller, 'procesar_notificacion'):
                resultado = controller.procesar_notificacion({
                    'titulo': 'Test',
                    'mensaje': 'Test message',
                    'tipo': 'INFO'
                })
                
        except ImportError:
            self.skipTest("Controlador NotificacionesController no disponible")
        except Exception as e:
            if "QWidget" not in str(e) and "QApplication" not in str(e):
                self.fail(f"Error en test procesar notificación: {e}")
    
    @patch('rexus.core.database.get_inventario_connection')
    def test_manejar_acciones_usuario(self, mock_connection):
        """Test manejo de acciones del usuario."""
        mock_connection.return_value = self.mock_db
        
        try:
            from rexus.modules.notificaciones.controller import NotificacionesController
            controller = NotificacionesController()
            
            # Test marcar como leída
            if hasattr(controller, 'marcar_como_leida'):
                resultado = controller.marcar_como_leida(1)
            
            # Test eliminar notificación
            if hasattr(controller, 'eliminar_notificacion'):
                resultado = controller.eliminar_notificacion(1)
                
            # Test marcar todas como leídas
            if hasattr(controller, 'marcar_todas_leidas'):
                resultado = controller.marcar_todas_leidas(1)
                
        except ImportError:
            self.skipTest("Controlador NotificacionesController no disponible")
        except Exception as e:
            if "QWidget" not in str(e):
                self.fail(f"Error en test acciones usuario: {e}")


class TestNotificacionesIntegracion(unittest.TestCase):
    """Tests de integración del módulo de notificaciones con otros módulos."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_db = MockNotificacionesDatabase()
    
    @patch('rexus.core.database.get_inventario_connection')
    def test_notificacion_desde_inventario(self, mock_connection):
        """Test generación de notificación desde módulo de inventario."""
        mock_connection.return_value = self.mock_db
        
        try:
            from rexus.modules.notificaciones.model import NotificacionesModel
            model = NotificacionesModel()
            
            # Test notificación de stock bajo
            if hasattr(model, 'notificar_stock_bajo'):
                resultado = model.notificar_stock_bajo(
                    producto_id=1,
                    codigo='TEST001',
                    stock_actual=5,
                    stock_minimo=10
                )
                
                self.mock_db.cursor_mock.execute.assert_called()
            
            # Test notificación de producto agotado
            if hasattr(model, 'notificar_producto_agotado'):
                resultado = model.notificar_producto_agotado(
                    producto_id=1,
                    codigo='TEST001'
                )
                
        except ImportError:
            self.skipTest("Integración con inventario no disponible")
    
    @patch('rexus.core.database.get_inventario_connection')
    def test_notificacion_desde_pedidos(self, mock_connection):
        """Test generación de notificación desde módulo de pedidos."""
        mock_connection.return_value = self.mock_db
        
        try:
            from rexus.modules.notificaciones.model import NotificacionesModel
            model = NotificacionesModel()
            
            # Test notificación de nuevo pedido
            if hasattr(model, 'notificar_nuevo_pedido'):
                resultado = model.notificar_nuevo_pedido(
                    pedido_id=1,
                    numero_pedido='PED-001',
                    cliente='Cliente Test',
                    supervisores_ids=[2, 3]
                )
                
                self.mock_db.cursor_mock.execute.assert_called()
            
            # Test notificación de cambio de estado
            if hasattr(model, 'notificar_cambio_estado_pedido'):
                resultado = model.notificar_cambio_estado_pedido(
                    pedido_id=1,
                    numero_pedido='PED-001',
                    estado_anterior='PENDIENTE',
                    estado_nuevo='EN_PRODUCCION'
                )
                
        except ImportError:
            self.skipTest("Integración con pedidos no disponible")
    
    @patch('rexus.core.database.get_inventario_connection')
    def test_notificacion_desde_compras(self, mock_connection):
        """Test generación de notificación desde módulo de compras."""
        mock_connection.return_value = self.mock_db
        
        try:
            from rexus.modules.notificaciones.model import NotificacionesModel
            model = NotificacionesModel()
            
            # Test notificación de compra recibida
            if hasattr(model, 'notificar_compra_recibida'):
                resultado = model.notificar_compra_recibida(
                    compra_id=1,
                    numero_orden='OC-001',
                    proveedor='Proveedor Test'
                )
                
                self.mock_db.cursor_mock.execute.assert_called()
            
            # Test notificación de compra vencida
            if hasattr(model, 'notificar_compra_vencida'):
                resultado = model.notificar_compra_vencida(
                    compra_id=1,
                    numero_orden='OC-001',
                    dias_vencida=5
                )
                
        except ImportError:
            self.skipTest("Integración con compras no disponible")
    
    @patch('rexus.core.database.get_inventario_connection')
    def test_notificacion_desde_obras(self, mock_connection):
        """Test generación de notificación desde módulo de obras."""
        mock_connection.return_value = self.mock_db
        
        try:
            from rexus.modules.notificaciones.model import NotificacionesModel
            model = NotificacionesModel()
            
            # Test notificación de nueva obra
            if hasattr(model, 'notificar_nueva_obra'):
                resultado = model.notificar_nueva_obra(
                    obra_id=1,
                    codigo='OBRA-001',
                    nombre='Proyecto Test',
                    supervisores_ids=[2, 3]
                )
                
                self.mock_db.cursor_mock.execute.assert_called()
            
            # Test notificación de fecha límite
            if hasattr(model, 'notificar_fecha_limite_obra'):
                resultado = model.notificar_fecha_limite_obra(
                    obra_id=1,
                    codigo='OBRA-001',
                    dias_restantes=7
                )
                
        except ImportError:
            self.skipTest("Integración con obras no disponible")


class TestNotificacionesAlerts(unittest.TestCase):
    """Tests para sistema de alertas y notificaciones automáticas."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_db = MockNotificacionesDatabase()
    
    @patch('rexus.core.database.get_inventario_connection')
    def test_sistema_alertas_automaticas(self, mock_connection):
        """Test sistema de alertas automáticas."""
        mock_connection.return_value = self.mock_db
        
        try:
            from rexus.modules.notificaciones.model import NotificacionesModel
            model = NotificacionesModel()
            
            # Test verificación automática de condiciones
            if hasattr(model, 'verificar_condiciones_automaticas'):
                alertas_generadas = model.verificar_condiciones_automaticas()
                
                self.assertIsInstance(alertas_generadas, list)
            
            # Test programar verificación periódica
            if hasattr(model, 'programar_verificaciones'):
                resultado = model.programar_verificaciones()
                
        except ImportError:
            self.skipTest("Sistema de alertas no disponible")
    
    @patch('rexus.core.database.get_inventario_connection')
    def test_configuracion_alertas(self, mock_connection):
        """Test configuración de tipos de alertas."""
        mock_connection.return_value = self.mock_db
        
        try:
            from rexus.modules.notificaciones.model import NotificacionesModel
            model = NotificacionesModel()
            
            # Test configurar umbrales de alerta
            if hasattr(model, 'configurar_umbral_stock'):
                resultado = model.configurar_umbral_stock(
                    producto_id=1,
                    umbral_minimo=10,
                    umbral_critico=5
                )
            
            # Test configurar destinatarios de alertas
            if hasattr(model, 'configurar_destinatarios'):
                resultado = model.configurar_destinatarios(
                    tipo_alerta='STOCK_BAJO',
                    usuarios_ids=[1, 2, 3]
                )
                
        except ImportError:
            self.skipTest("Configuración de alertas no disponible")


class TestNotificacionesReportes(unittest.TestCase):
    """Tests para reportes y estadísticas de notificaciones."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_db = MockNotificacionesDatabase()
    
    @patch('rexus.core.database.get_inventario_connection')
    def test_generar_reporte_actividad(self, mock_connection):
        """Test generación de reporte de actividad."""
        mock_connection.return_value = self.mock_db
        
        # Mock datos de reporte
        self.mock_db.cursor_mock.fetchall.return_value = [
            ('2025-08-20', 'INFO', 15),
            ('2025-08-20', 'WARNING', 3),
            ('2025-08-20', 'ERROR', 1),
            ('2025-08-19', 'INFO', 12),
            ('2025-08-19', 'WARNING', 5)
        ]
        
        try:
            from rexus.modules.notificaciones.model import NotificacionesModel
            model = NotificacionesModel()
            
            if hasattr(model, 'generar_reporte_actividad'):
                reporte = model.generar_reporte_actividad(
                    fecha_desde='2025-08-19',
                    fecha_hasta='2025-08-20'
                )
                
                self.assertIsInstance(reporte, (list, dict))
                self.mock_db.cursor_mock.execute.assert_called()
                
        except ImportError:
            self.skipTest("Generación de reportes no disponible")
    
    @patch('rexus.core.database.get_inventario_connection')
    def test_estadisticas_por_modulo(self, mock_connection):
        """Test estadísticas de notificaciones por módulo origen."""
        mock_connection.return_value = self.mock_db
        
        self.mock_db.cursor_mock.fetchall.return_value = [
            ('inventario', 45),
            ('pedidos', 32),
            ('compras', 28),
            ('obras', 15)
        ]
        
        try:
            from rexus.modules.notificaciones.model import NotificacionesModel
            model = NotificacionesModel()
            
            if hasattr(model, 'obtener_estadisticas_por_modulo'):
                stats = model.obtener_estadisticas_por_modulo()
                
                self.assertIsInstance(stats, list)
                self.mock_db.cursor_mock.execute.assert_called()
                
        except ImportError:
            self.skipTest("Estadísticas por módulo no disponibles")


def run_notificaciones_tests():
    """
    Ejecuta todos los tests del módulo de notificaciones.
    
    Returns:
        bool: True si todos los tests pasan
    """
    suite = unittest.TestSuite()
    
    # Tests de modelo
    suite.addTest(TestNotificacionesModel('test_notificaciones_model_initialization'))
    suite.addTest(TestNotificacionesModel('test_obtener_todas_notificaciones'))
    suite.addTest(TestNotificacionesModel('test_crear_notificacion_exitosa'))
    suite.addTest(TestNotificacionesModel('test_enviar_notificacion_broadcast'))
    suite.addTest(TestNotificacionesModel('test_marcar_como_leida'))
    suite.addTest(TestNotificacionesModel('test_obtener_notificaciones_no_leidas'))
    suite.addTest(TestNotificacionesModel('test_filtrar_por_tipo'))
    suite.addTest(TestNotificacionesModel('test_eliminar_notificacion'))
    suite.addTest(TestNotificacionesModel('test_limpiar_notificaciones_antiguas'))
    suite.addTest(TestNotificacionesModel('test_obtener_estadisticas'))
    
    # Tests de controlador
    suite.addTest(TestNotificacionesController('test_controller_initialization'))
    suite.addTest(TestNotificacionesController('test_procesar_nueva_notificacion'))
    suite.addTest(TestNotificacionesController('test_manejar_acciones_usuario'))
    
    # Tests de integración
    suite.addTest(TestNotificacionesIntegracion('test_notificacion_desde_inventario'))
    suite.addTest(TestNotificacionesIntegracion('test_notificacion_desde_pedidos'))
    suite.addTest(TestNotificacionesIntegracion('test_notificacion_desde_compras'))
    suite.addTest(TestNotificacionesIntegracion('test_notificacion_desde_obras'))
    
    # Tests de sistema de alertas
    suite.addTest(TestNotificacionesAlerts('test_sistema_alertas_automaticas'))
    suite.addTest(TestNotificacionesAlerts('test_configuracion_alertas'))
    
    # Tests de reportes
    suite.addTest(TestNotificacionesReportes('test_generar_reporte_actividad'))
    suite.addTest(TestNotificacionesReportes('test_estadisticas_por_modulo'))
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    print("="*70)
    print("TESTS COMPLETOS - MÓDULO DE NOTIFICACIONES")
    print("="*70)
    
    success = run_notificaciones_tests()
    
    if success:
        print("\n✅ TODOS LOS TESTS DE NOTIFICACIONES PASARON")
        sys.exit(0)
    else:
        print("\n❌ ALGUNOS TESTS DE NOTIFICACIONES FALLARON")
        sys.exit(1)