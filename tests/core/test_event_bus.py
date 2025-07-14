"""
Tests para core.event_bus
Cobertura: EventBus, señales, integración entre módulos, edge cases
"""
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestEventBus:
    """Tests unitarios para EventBus"""

    @pytest.fixture
    def app(self):
        """Fixture para aplicación Qt"""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        yield app
        # Cleanup se maneja automáticamente por pytest-qt

    @pytest.fixture
    def event_bus_instance(self, app):
        """Fixture que provee una instancia limpia de EventBus"""
        return EventBus()

    def test_event_bus_is_qobject(self, event_bus_instance):
        """Test que verifica que EventBus hereda de QObject"""
        assert isinstance(event_bus_instance, QObject)

    def test_event_bus_has_all_signals(self, event_bus_instance):
        """Test que verifica que EventBus tiene todas las señales definidas"""
        # Assert - Verificar que las señales existen
        assert hasattr(event_bus_instance, 'obra_agregada')
        assert hasattr(event_bus_instance, 'pedido_actualizado')
        assert hasattr(event_bus_instance, 'pedido_cancelado')
        assert hasattr(event_bus_instance, 'stock_modificado')
        assert hasattr(event_bus_instance, 'vidrio_asignado')

        # Verificar que son pyqtSignal
        assert isinstance(event_bus_instance.obra_agregada, pyqtSignal)
        assert isinstance(event_bus_instance.pedido_actualizado, pyqtSignal)
        assert isinstance(event_bus_instance.pedido_cancelado, pyqtSignal)
        assert isinstance(event_bus_instance.stock_modificado, pyqtSignal)
        assert isinstance(event_bus_instance.vidrio_asignado, pyqtSignal)

    def test_obra_agregada_signal_emission(self, event_bus_instance):
        """Test que verifica la emisión de señal obra_agregada"""
        # Arrange
        callback = Mock()
        event_bus_instance.obra_agregada.connect(callback)
        test_data = {
            "id": 1,
            "nombre": "Obra Test",
            "cliente": "Cliente Test",
            "fecha": "2024-01-01"
        }

        # Act
        event_bus_instance.obra_agregada.emit(test_data)

        # Assert
        callback.assert_called_once_with(test_data)

    def test_pedido_actualizado_signal_emission(self, event_bus_instance):
        """Test que verifica la emisión de señal pedido_actualizado"""
        # Arrange
        callback = Mock()
        event_bus_instance.pedido_actualizado.connect(callback)
        test_data = {
            "id": 2,
            "estado": "actualizado",
            "modificado_por": "usuario_test"
        }

        # Act
        event_bus_instance.pedido_actualizado.emit(test_data)

        # Assert
        callback.assert_called_once_with(test_data)

    def test_pedido_cancelado_signal_emission(self, event_bus_instance):
        """Test que verifica la emisión de señal pedido_cancelado"""
        # Arrange
        callback = Mock()
        event_bus_instance.pedido_cancelado.connect(callback)
        test_data = {
            "id": 3,
            "estado": "cancelado",
            "razon": "solicitud_cliente"
        }

        # Act
        event_bus_instance.pedido_cancelado.emit(test_data)

        # Assert
        callback.assert_called_once_with(test_data)

    def test_stock_modificado_signal_emission(self, event_bus_instance):
        """Test que verifica la emisión de señal stock_modificado"""
        # Arrange
        callback = Mock()
        event_bus_instance.stock_modificado.connect(callback)
        test_data = {
            "producto_id": 4,
            "cantidad_anterior": 100,
            "cantidad_nueva": 90,
            "operacion": "venta"
        }

        # Act
        event_bus_instance.stock_modificado.emit(test_data)

        # Assert
        callback.assert_called_once_with(test_data)

    def test_vidrio_asignado_signal_emission(self, event_bus_instance):
        """Test que verifica la emisión de señal vidrio_asignado"""
        # Arrange
        callback = Mock()
        event_bus_instance.vidrio_asignado.connect(callback)
        test_data = {
            "vidrio_id": 5,
            "obra_id": 1,
            "asignado_por": "usuario_test",
            "fecha_asignacion": "2024-01-01T12:00:00"
        }

        # Act
        event_bus_instance.vidrio_asignado.emit(test_data)

        # Assert
        callback.assert_called_once_with(test_data)

    def test_multiple_callbacks_same_signal(self, event_bus_instance):
        """Test que verifica múltiples callbacks en la misma señal"""
        # Arrange
        callback1 = Mock()
        callback2 = Mock()
        callback3 = Mock()

        event_bus_instance.obra_agregada.connect(callback1)
        event_bus_instance.obra_agregada.connect(callback2)
        event_bus_instance.obra_agregada.connect(callback3)

        test_data = {"id": 1, "nombre": "Test"}

        # Act
        event_bus_instance.obra_agregada.emit(test_data)

        # Assert
        callback1.assert_called_once_with(test_data)
        callback2.assert_called_once_with(test_data)
        callback3.assert_called_once_with(test_data)

    def test_signal_disconnection(self, event_bus_instance):
        """Test que verifica la desconexión de señales"""
        # Arrange
        callback = Mock()
        event_bus_instance.pedido_actualizado.connect(callback)

        # Act - Emitir antes de desconectar
        test_data = {"id": 1}
        event_bus_instance.pedido_actualizado.emit(test_data)

        # Desconectar
        event_bus_instance.pedido_actualizado.disconnect(callback)

        # Emitir después de desconectar
        event_bus_instance.pedido_actualizado.emit({"id": 2})

        # Assert - Solo debe haberse llamado una vez (antes de desconectar)
        callback.assert_called_once_with(test_data)

    def test_signal_with_empty_dict(self, event_bus_instance):
        """Test que verifica emisión con diccionario vacío"""
        # Arrange
        callback = Mock()
        event_bus_instance.stock_modificado.connect(callback)

        # Act
        event_bus_instance.stock_modificado.emit({})

        # Assert
        callback.assert_called_once_with({})

    def test_signal_with_complex_data(self, event_bus_instance):
        """Test que verifica emisión con datos complejos"""
        # Arrange
        callback = Mock()
        event_bus_instance.obra_agregada.connect(callback)

        complex_data = {
            "id": 1,
            "datos_cliente": {
                "nombre": "Cliente Test",
                "contacto": {
                    "email": "test@example.com",
                    "telefono": "+123456789"
                }
            },
            "materiales": [
                {"tipo": "vidrio", "cantidad": 10},
                {"tipo": "aluminio", "cantidad": 5}
            ],
            "configuracion": {
                "urgente": True,
                "descuento": 15.5,
                "notas": "Pedido especial con entrega urgente"
            }
        }

        # Act
        event_bus_instance.obra_agregada.emit(complex_data)

        # Assert
        callback.assert_called_once_with(complex_data)

    def test_signal_callback_exception_handling(self, event_bus_instance):
        """Test que verifica manejo de excepciones en callbacks"""
        # Arrange
        def callback_that_fails(data):
            raise ValueError("Test exception in callback")

        callback_normal = Mock()

        event_bus_instance.pedido_cancelado.connect(callback_that_fails)
        event_bus_instance.pedido_cancelado.connect(callback_normal)

        # Act - No debe fallar aunque un callback genere excepción
        test_data = {"id": 1, "razon": "test"}
        event_bus_instance.pedido_cancelado.emit(test_data)

        # Assert - El callback normal debe haberse ejecutado
        callback_normal.assert_called_once_with(test_data)

    def test_rapid_signal_emissions(self, event_bus_instance):
        """Test que verifica emisiones rápidas de señales"""
        # Arrange
        callback = Mock()
        event_bus_instance.stock_modificado.connect(callback)

        # Act - Emitir múltiples señales rápidamente
        for i in range(100):
            event_bus_instance.stock_modificado.emit({"operacion": f"test_{i}"})

        # Assert
        assert callback.call_count == 100

    def test_signal_emission_order(self, event_bus_instance):
        """Test que verifica el orden de emisión de señales"""
        # Arrange
        call_order = []

        def callback1(data):
            call_order.append(f"callback1: {data['id']}")

        def callback2(data):
            call_order.append(f"callback2: {data['id']}")

        event_bus_instance.vidrio_asignado.connect(callback1)
        event_bus_instance.vidrio_asignado.connect(callback2)

        # Act
        event_bus_instance.vidrio_asignado.emit({"id": 1})
        event_bus_instance.vidrio_asignado.emit({"id": 2})

        # Assert - Verificar orden de llamadas
        expected_order = [
            "callback1: 1", "callback2: 1",
            "callback1: 2", "callback2: 2"
        ]
        assert call_order == expected_order


class TestGlobalEventBusInstance:
    """Tests para la instancia global de event_bus"""

    @pytest.fixture
    def app(self):
        """Fixture para aplicación Qt"""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        yield app
        # Cleanup se maneja automáticamente por pytest-qt

    def test_global_event_bus_is_instance_of_eventbus(self, app):
        """Test que verifica que la instancia global es de tipo EventBus"""
        assert isinstance(event_bus, EventBus)

    def test_global_event_bus_singleton_behavior(self, app):
        """Test que verifica comportamiento de singleton de la instancia global"""
        # Arrange & Act
        # Assert - Ambas importaciones deben referenciar el mismo objeto
        assert event_bus1 is event_bus2
        assert id(event_bus1) == id(event_bus2)

    def test_global_event_bus_has_all_signals(self, app):
        """Test que verifica que la instancia global tiene todas las señales"""
        assert hasattr(event_bus, 'obra_agregada')
        assert hasattr(event_bus, 'pedido_actualizado')
        assert hasattr(event_bus, 'pedido_cancelado')
        assert hasattr(event_bus, 'stock_modificado')
        assert hasattr(event_bus, 'vidrio_asignado')
import os
import sys
from unittest.mock import MagicMock, Mock, patch

import pytest
from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from PyQt6.QtWidgets import QApplication

from core.event_bus import EventBus
from core.event_bus import event_bus
from core.event_bus import event_bus as event_bus1
from core.event_bus import event_bus as event_bus2

    def test_global_event_bus_signal_functionality(self, app):
        """Test que verifica funcionalidad de señales en instancia global"""
        # Arrange
        callback = Mock()
        event_bus.obra_agregada.connect(callback)
        test_data = {"test": "global_signal"}

        # Act
        event_bus.obra_agregada.emit(test_data)

        # Assert
        callback.assert_called_once_with(test_data)

        # Cleanup
        event_bus.obra_agregada.disconnect(callback)


class TestEventBusIntegrationScenarios:
    """Tests de escenarios de integración entre módulos usando EventBus"""

    @pytest.fixture
    def app(self):
        """Fixture para aplicación Qt"""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        yield app
        # Cleanup se maneja automáticamente por pytest-qt

    @pytest.fixture
    def event_bus_instance(self, app):
        """Fixture que provee una instancia limpia de EventBus"""
        return EventBus()

    def test_obra_to_inventario_integration(self, event_bus_instance):
        """Test de integración: Obra agregada actualiza inventario"""
        # Arrange - Simular módulos
        inventario_callback = Mock()
        logistica_callback = Mock()

        event_bus_instance.obra_agregada.connect(inventario_callback)
        event_bus_instance.obra_agregada.connect(logistica_callback)

        obra_data = {
            "id": 1,
            "materiales_requeridos": [
                {"tipo": "vidrio_6mm", "cantidad": 20},
                {"tipo": "perfil_aluminio", "cantidad": 15}
            ],
            "fecha_entrega": "2024-02-15"
        }

        # Act
        event_bus_instance.obra_agregada.emit(obra_data)

        # Assert
        inventario_callback.assert_called_once_with(obra_data)
        logistica_callback.assert_called_once_with(obra_data)

    def test_stock_modification_cascade(self, event_bus_instance):
        """Test de cascada: Modificación de stock genera múltiples actualizaciones"""
        # Arrange
        pedidos_callback = Mock()
        reportes_callback = Mock()
        notificaciones_callback = Mock()

        event_bus_instance.stock_modificado.connect(pedidos_callback)
        event_bus_instance.stock_modificado.connect(reportes_callback)
        event_bus_instance.stock_modificado.connect(notificaciones_callback)

        stock_data = {
            "producto_id": 5,
            "codigo": "VID-6MM-TEMP",
            "stock_anterior": 100,
            "stock_nuevo": 20,
            "operacion": "asignacion_obra",
            "obra_id": 3,
            "nivel_critico": True
        }

        # Act
        event_bus_instance.stock_modificado.emit(stock_data)

        # Assert - Todos los módulos deben recibir la notificación
        pedidos_callback.assert_called_once_with(stock_data)
        reportes_callback.assert_called_once_with(stock_data)
        notificaciones_callback.assert_called_once_with(stock_data)

    def test_pedido_cancellation_workflow(self, event_bus_instance):
        """Test de flujo: Cancelación de pedido afecta múltiples módulos"""
        # Arrange
        inventario_restock = Mock()
        contabilidad_ajuste = Mock()
        cliente_notificacion = Mock()

        event_bus_instance.pedido_cancelado.connect(inventario_restock)
        event_bus_instance.pedido_cancelado.connect(contabilidad_ajuste)
        event_bus_instance.pedido_cancelado.connect(cliente_notificacion)

        cancelacion_data = {
            "pedido_id": 10,
            "materiales_a_devolver": [
                {"codigo": "ALU-PERFIL-20", "cantidad": 10},
                {"codigo": "VID-8MM-TRANS", "cantidad": 5}
            ],
            "valor_pedido": 2500.00,
            "cliente_id": 7,
            "razon_cancelacion": "cambio_especificaciones",
            "requiere_reembolso": True
        }

        # Act
        event_bus_instance.pedido_cancelado.emit(cancelacion_data)

        # Assert
        inventario_restock.assert_called_once_with(cancelacion_data)
        contabilidad_ajuste.assert_called_once_with(cancelacion_data)
        cliente_notificacion.assert_called_once_with(cancelacion_data)

    def test_vidrio_assignment_coordination(self, event_bus_instance):
        """Test de coordinación: Asignación de vidrio coordina múltiples operaciones"""
        # Arrange
        obra_actualizacion = Mock()
        inventario_descuento = Mock()
        produccion_programacion = Mock()

        event_bus_instance.vidrio_asignado.connect(obra_actualizacion)
        event_bus_instance.vidrio_asignado.connect(inventario_descuento)
        event_bus_instance.vidrio_asignado.connect(produccion_programacion)

        asignacion_data = {
            "vidrio_id": 15,
            "obra_id": 8,
            "especificaciones": {
                "tipo": "templado",
                "espesor": "6mm",
                "dimensiones": "1200x800",
                "acabado": "transparente"
            },
            "cantidad": 3,
            "fecha_necesaria": "2024-03-01",
            "prioridad": "alta",
            "requiere_fabricacion": True
        }

        # Act
        event_bus_instance.vidrio_asignado.emit(asignacion_data)

        # Assert
        obra_actualizacion.assert_called_once_with(asignacion_data)
        inventario_descuento.assert_called_once_with(asignacion_data)
        produccion_programacion.assert_called_once_with(asignacion_data)

    def test_cross_module_data_consistency(self, event_bus_instance):
        """Test de consistencia: Los datos se mantienen consistentes entre módulos"""
        # Arrange
        received_data = []

        def capture_data(data):
            received_data.append(data.copy())  # Copia para evitar mutaciones

        # Conectar múltiples módulos
        event_bus_instance.pedido_actualizado.connect(capture_data)
        event_bus_instance.pedido_actualizado.connect(capture_data)
        event_bus_instance.pedido_actualizado.connect(capture_data)

        original_data = {
            "id": 20,
            "estado": "en_proceso",
            "items": [1, 2, 3],
            "metadatos": {"version": 1, "timestamp": "2024-01-01T12:00:00"}
        }

        # Act
        event_bus_instance.pedido_actualizado.emit(original_data)

        # Assert - Todos los módulos deben recibir datos idénticos
        assert len(received_data) == 3
        for data in received_data:
            assert data == original_data
            assert data is not original_data  # Diferentes instancias

    def test_high_frequency_events_handling(self, event_bus_instance):
        """Test de manejo de eventos de alta frecuencia"""
        # Arrange
        processed_count = [0]  # Lista para mutabilidad en callback

        def high_frequency_processor(data):
            processed_count[0] += 1

        event_bus_instance.stock_modificado.connect(high_frequency_processor)

        # Act - Simular muchas modificaciones de stock en poco tiempo
        for i in range(1000):
            event_bus_instance.stock_modificado.emit({
                "producto_id": i % 10,  # 10 productos diferentes
                "cantidad": i,
                "timestamp": f"2024-01-01T12:{i//60:02d}:{i%60:02d}"
            })

        # Assert
        assert processed_count[0] == 1000

    def test_module_registration_and_deregistration(self, event_bus_instance):
        """Test de registro y desregistro dinámico de módulos"""
        # Arrange
        module_a_calls = []
        module_b_calls = []

        def module_a_handler(data):
            module_a_calls.append(data)

        def module_b_handler(data):
            module_b_calls.append(data)

        # Act - Registrar módulos
        event_bus_instance.obra_agregada.connect(module_a_handler)
        event_bus_instance.obra_agregada.connect(module_b_handler)

        # Emitir evento con ambos módulos registrados
        event_bus_instance.obra_agregada.emit({"test": "both_modules"})

        # Desregistrar módulo A
        event_bus_instance.obra_agregada.disconnect(module_a_handler)

        # Emitir evento con solo módulo B
        event_bus_instance.obra_agregada.emit({"test": "only_module_b"})

        # Assert
        assert len(module_a_calls) == 1
        assert len(module_b_calls) == 2
        assert module_a_calls[0]["test"] == "both_modules"
        assert module_b_calls[0]["test"] == "both_modules"
        assert module_b_calls[1]["test"] == "only_module_b"


class TestEventBusDocumentation:
    """Tests para verificar documentación y metadatos del EventBus"""

    def test_eventbus_has_docstring(self):
        """Test que verifica que EventBus tiene documentación"""
        assert EventBus.__doc__ is not None
        assert "Bus de eventos centralizado" in EventBus.__doc__
        assert "señales entre módulos principales" in EventBus.__doc__
        assert "desacoplar la lógica de actualización" in EventBus.__doc__

    def test_signals_have_meaningful_names(self):
        """Test que verifica que las señales tienen nombres descriptivos"""
        event_bus_instance = EventBus()

        # Las señales deben estar bien nombradas y ser descriptivas
        signal_names = [
            "obra_agregada",
            "pedido_actualizado",
            "pedido_cancelado",
            "stock_modificado",
            "vidrio_asignado"
        ]

        for signal_name in signal_names:
            assert hasattr(event_bus_instance, signal_name)
            # Los nombres deben ser descriptivos (más de 5 caracteres)
            assert len(signal_name) > 5
            # Los nombres deben contener al menos un underscore para separar palabras
            assert "_" in signal_name
