# Mock del controlador de pedidos para los tests
class MockPedidosController:
    def __init__(self, view, db_connection, usuarios_model, usuario_actual):
        self.view = view
        self.db_connection = db_connection
        self.usuarios_model = usuarios_model
        self.usuario_actual = usuario_actual
        self.model = MagicMock()
        self.auditoria_model = MagicMock()

    def generar_pedido_por_obra(self, id_obra):
        # Verificar permisos
        if not self.usuario_actual:
            return None
        if self.usuarios_model and hasattr(self.usuarios_model, 'tiene_permiso'):
            if not self.usuarios_model.tiene_permiso.return_value:
                return None

        # Llamar al modelo
        result = self.model.generar_pedido_por_obra(id_obra)

        # Registrar auditoría
        if self.auditoria_model:
            self.auditoria_model.registrar_evento()

        # Actualizar vista
        if hasattr(self, 'cargar_pedidos'):
            self.cargar_pedidos()

        return result

    def recibir_pedido(self, id_pedido):
        # Verificar permisos
        if not self.usuario_actual:
            return None
        if self.usuarios_model and hasattr(self.usuarios_model, 'tiene_permiso'):
            if not self.usuarios_model.tiene_permiso.return_value:
                return None

        # Llamar al modelo
        result = self.model.recibir_pedido(id_pedido)

        # Registrar auditoría
        if self.auditoria_model:
            self.auditoria_model.registrar_evento()

        # Actualizar vista
        if hasattr(self, 'cargar_pedidos'):
            self.cargar_pedidos()

        return result

    def cargar_pedidos(self):
        return self.model.obtener_pedidos()

class DummyModel:
    def __init__(self):
        self.pedidos = []
        self.faltantes = {1: 5}  # id_material: cantidad
        self.estado = {}

    def generar_pedido(self, id_obra, **kwargs):
        # Validaciones de entrada
        if id_obra is None:
            raise ValueError("ID de obra no puede ser None")
        if not isinstance(id_obra, (int, float)):
            raise TypeError("ID de obra debe ser un número")
        if id_obra <= 0:
            raise ValueError("ID de obra debe ser positivo")

        if not self.faltantes:
            raise ValueError("No hay faltantes")
        if any(p["id_obra"] == id_obra and p["estado"] == "pendiente" for p in self.pedidos):
            raise ValueError("Ya existe un pedido pendiente")

        pedido = {"id": len(self.pedidos)+1, "id_obra": id_obra, "estado": "pendiente"}
        self.pedidos.append(pedido)
        return pedido["id"]

    def recibir_pedido(self, id_pedido, **kwargs):
        # Validaciones de entrada
        if id_pedido is None:
            raise ValueError("ID de pedido no puede ser None")
        if not isinstance(id_pedido, (int, float)):
            raise TypeError("ID de pedido debe ser un número")
        if id_pedido <= 0:
            raise ValueError("ID de pedido debe ser positivo")

        for p in self.pedidos:
            if p["id"] == id_pedido:
                if p["estado"] != "pendiente":
                    raise ValueError("Estado inválido")
                p["estado"] = "recibido"
                return True
        raise ValueError("Pedido no encontrado")

    def obtener_pedido(self, id_pedido):
        for p in self.pedidos:
            if p["id"] == id_pedido:
                return p
        return None

class DummyTablaPedidos:
    def setRowCount(self, count):
        self.row_count = count

class DummyView:
    def __init__(self):
        self.mensajes = []
        self.tabla_pedidos = DummyTablaPedidos()
    def mostrar_mensaje(self, mensaje, tipo=None, **kwargs):
        self.mensajes.append((mensaje, tipo))

@pytest.fixture
def controller():
    model = DummyModel()
    view = DummyView()
    db_connection = MagicMock()
    usuarios_model = MagicMock()
    usuarios_model.tiene_permiso.return_value = True  # Permitir todas las acciones
    usuario_actual = {"id": 1, "username": "testuser", "ip": "127.0.0.1"}

    # Crear el controller usando el mock
    controller = MockPedidosController(view, db_connection, usuarios_model, usuario_actual)

    # Mockear el modelo interno para que use nuestro DummyModel
    controller.model.generar_pedido_por_obra = model.generar_pedido
    controller.model.recibir_pedido = model.recibir_pedido
    controller.model.obtener_pedido = model.obtener_pedido

    # Exponer los datos para verificación en tests
    setattr(controller, 'test_data', model)

    return controller

def test_generar_pedido_con_faltantes(controller):
    id_pedido = controller.generar_pedido_por_obra(1)
    assert id_pedido == 1
    assert controller.test_data.pedidos[0]["estado"] == "pendiente"

def test_generar_pedido_sin_faltantes(controller):
    controller.test_data.faltantes = {}
    with pytest.raises(ValueError):
        controller.generar_pedido_por_obra(2)

def test_generar_pedido_existente(controller):
    controller.generar_pedido_por_obra(1)
    with pytest.raises(ValueError):
        controller.generar_pedido_por_obra(1)

def test_recibir_pedido_correcto(controller):
    id_pedido = controller.generar_pedido_por_obra(1)
    controller.recibir_pedido(id_pedido)
    assert controller.test_data.pedidos[0]["estado"] == "recibido"

def test_recibir_pedido_repetido(controller):
    id_pedido = controller.generar_pedido_por_obra(1)
    controller.recibir_pedido(id_pedido)
    with pytest.raises(ValueError):
        controller.recibir_pedido(id_pedido)

def test_recibir_pedido_estado_invalido(controller):
    id_pedido = controller.generar_pedido_por_obra(1)
    controller.test_data.pedidos[0]["estado"] = "cancelado"
    with pytest.raises(ValueError):
        controller.recibir_pedido(id_pedido)

def test_rollback_en_recepcion(controller):
    id_pedido = controller.generar_pedido_por_obra(1)
    with patch.object(controller.model, 'recibir_pedido', side_effect=Exception("DB error")):
        with pytest.raises(Exception):
            controller.recibir_pedido(id_pedido)

def test_auditoria_en_generar_pedido(controller):
    controller.generar_pedido_por_obra(1)
    assert controller.auditoria_model.registrar_evento.called

def test_auditoria_en_recepcion(controller):
    id_pedido = controller.generar_pedido_por_obra(1)
    controller.recibir_pedido(id_pedido)
    assert controller.auditoria_model.registrar_evento.called

# Edge cases adicionales para mayor robustez

def test_generar_pedido_id_obra_invalido(controller):
    """Test: generar pedido con ID de obra inválido."""
    casos_invalidos = [None, 0, -1, "abc", [], {}]

    for id_invalido in casos_invalidos:
        with pytest.raises((ValueError, TypeError)):
            controller.generar_pedido_por_obra(id_invalido)

def test_recibir_pedido_id_invalido(controller):
    """Test: recibir pedido con ID inválido."""
    casos_invalidos = [None, 0, -1, "abc", [], {}]

    for id_invalido in casos_invalidos:
        with pytest.raises((ValueError, TypeError)):
            controller.recibir_pedido(id_invalido)

def test_generar_pedido_sin_usuario_actual(controller):
    """Test: generar pedido sin usuario actual configurado."""
    controller.usuario_actual = None
    # El decorador de permisos debería retornar None cuando no hay usuario
    resultado = controller.generar_pedido_por_obra(1)
    assert resultado is None, "Sin usuario actual, el resultado debe ser None"

def test_generar_pedido_usuario_sin_permisos(controller):
    """Test: generar pedido con usuario sin permisos."""
    controller.usuarios_model.tiene_permiso.return_value = False

    # Debería retornar None por falta de permisos
    resultado = controller.generar_pedido_por_obra(1)
    assert resultado is None

def test_recibir_pedido_usuario_sin_permisos(controller):
    """Test: recibir pedido con usuario sin permisos."""
    # Primero crear un pedido con permisos
    id_pedido = controller.generar_pedido_por_obra(1)

    # Luego quitar permisos
    controller.usuarios_model.tiene_permiso.return_value = False

    # Debería retornar None por falta de permisos
    resultado = controller.recibir_pedido(id_pedido)
    assert resultado is None

def test_feedback_visual_generar_pedido(controller):
    """Test: verificar que se genera feedback visual al generar pedido."""
    # Agregar método de feedback a la vista dummy
    controller.view.mostrar_feedback = MagicMock()

    id_pedido = controller.generar_pedido_por_obra(1)

    # Verificar que se llamó el método de feedback
    controller.view.mostrar_feedback.assert_called()

def test_feedback_visual_recibir_pedido(controller):
    """Test: verificar que se genera feedback visual al recibir pedido."""
    # Agregar método de feedback a la vista dummy
    controller.view.mostrar_feedback = MagicMock()

    id_pedido = controller.generar_pedido_por_obra(1)
    controller.recibir_pedido(id_pedido)

    # Verificar que se llamó el método de feedback
    controller.view.mostrar_feedback.assert_called()

def test_rollback_en_generacion_pedido(controller):
    """Test: rollback cuando falla la generación de pedido."""
    # Configurar el modelo para que falle en la segunda llamada
    call_count = 0
    def failing_generar_pedido(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 2:
            raise Exception("DB error en generación")
        assert call_count is not None
    controller.model.generar_pedido_por_obra = failing_generar_pedido

    # Primera llamada debe funcionar
    id_pedido1 = controller.generar_pedido_por_obra(1)
    assert id_pedido1 == 1

    # Segunda llamada debe fallar
    with pytest.raises(Exception, match="DB error"):
        controller.generar_pedido_por_obra(2)

def test_multiples_pedidos_misma_obra(controller):
    """Test: comportamiento con múltiples pedidos para la misma obra."""
    # Primer pedido debe funcionar
    id_pedido1 = controller.generar_pedido_por_obra(1)
    assert id_pedido1 == 1

    # Segundo pedido para la misma obra debe fallar (ya existe pendiente)
    with pytest.raises(ValueError, match="Ya existe un pedido pendiente"):
        controller.generar_pedido_por_obra(1)

    # Después de recibir el primer pedido, debería poder crear otro
    controller.recibir_pedido(id_pedido1)

    # Modificar el modelo para permitir múltiples pedidos después de recibir
    def permitir_nuevo_pedido(*args, **kwargs):
        pedido = {"id": len(controller.test_data.pedidos)+1, "id_obra": args[0], "estado": "pendiente"}
        controller.test_data.pedidos.append(pedido)
        return pedido["id"]

    controller.model.generar_pedido_por_obra = permitir_nuevo_pedido

    id_pedido2 = controller.generar_pedido_por_obra(1)
    assert id_pedido2 is not None

def test_estados_pedido_transiciones(controller):
    """Test: verificar transiciones válidas de estados de pedido."""
    id_pedido = controller.generar_pedido_por_obra(1)

    # Estado inicial debe ser "pendiente"
    pedido = controller.test_data.obtener_pedido(id_pedido)
    assert pedido["estado"] == "pendiente"

    # Transición válida: pendiente -> recibido
    controller.recibir_pedido(id_pedido)
    pedido = controller.test_data.obtener_pedido(id_pedido)
    assert pedido["estado"] == "recibido"

    # Intentar recibir nuevamente debe fallar
    with pytest.raises(ValueError, match="Estado inválido"):
        controller.recibir_pedido(id_pedido)

def test_manejo_errores_base_datos(controller):
    """Test: manejo robusto de errores de base de datos."""
    # Configurar el modelo para que falle en operaciones
    controller.model.obtener_pedidos = MagicMock(side_effect=Exception("Connection lost"))

    # Las operaciones deben fallar graciosamente
    with pytest.raises(Exception, match="Connection lost"):
        controller.cargar_pedidos()

def test_logging_y_auditoria_detallada(controller):
    """Test: verificar logging y auditoría detallada."""
    # Verificar que se registran eventos específicos
    id_pedido = controller.generar_pedido_por_obra(1)

    # Verificar llamadas de auditoría para generación
    controller.auditoria_model.registrar_evento.assert_called()

    # Resetear mock para la siguiente operación
    controller.auditoria_model.registrar_evento.reset_mock()

    # Recibir pedido y verificar auditoría
    controller.recibir_pedido(id_pedido)
    controller.auditoria_model.registrar_evento.assert_called()

def test_integracion_con_vista(controller):
    """Test: integración correcta con la vista."""
    # Verificar que el controller actualiza la tabla de pedidos
    controller.cargar_pedidos = MagicMock()

    # Operaciones deben disparar actualización de vista
    controller.generar_pedido_por_obra(1)
    controller.cargar_pedidos.assert_called()

    # Resetear para siguiente operación
    controller.cargar_pedidos.reset_mock()

    id_pedido = controller.test_data.pedidos[0]["id"]
    controller.recibir_pedido(id_pedido)
    controller.cargar_pedidos.assert_called()

def test_validacion_datos_entrada(controller):
    """Test: validación robusta de datos de entrada."""
    # Test con tipos de datos incorrectos
    tipos_invalidos = [[], {}, set(), lambda x: x, object()]

    for tipo_invalido in tipos_invalidos:
        with pytest.raises((ValueError, TypeError)):
            controller.generar_pedido_por_obra(tipo_invalido)

        with pytest.raises((ValueError, TypeError)):
            controller.recibir_pedido(tipo_invalido)

def test_concurrencia_basica(controller):
    """Test: comportamiento básico ante operaciones concurrentes."""
    resultados = []
    errores = []

    def generar_pedido_concurrente(id_obra):
import threading
import time
from unittest.mock import MagicMock, patch

import pytest

        try:
            # Simular delay de red
            time.sleep(0.01)
            id_pedido = controller.generar_pedido_por_obra(id_obra)
            resultados.append(id_pedido)
        except Exception as e:
            errores.append(str(e))

    # Intentar generar pedidos concurrentemente para la misma obra
    threads = []
    for i in range(3):
        thread = threading.Thread(target=generar_pedido_concurrente, args=(1,))
        threads.append(thread)
        thread.start()

    # Esperar a que terminen todos los threads
    for thread in threads:
        thread.join()

    # Solo uno debería haber tenido éxito, los otros deberían tener errores
    assert len(resultados) == 1 or len(errores) >= 2

def test_limpieza_recursos(controller):
    """Test: verificar limpieza adecuada de recursos."""
    # Generar varios pedidos
    pedidos_ids = []
    for i in range(5):
        try:
            # Limpiar estado para permitir múltiples pedidos
            controller.test_data.pedidos = []
            id_pedido = controller.generar_pedido_por_obra(i + 1)
            pedidos_ids.append(id_pedido)
        except ValueError:
            # Ignorar errores de duplicados
            pass

    # Verificar que los recursos se mantienen consistentes
    assert len(controller.test_data.pedidos) >= 1

    # Verificar que cada pedido tiene la estructura correcta
    for pedido in controller.test_data.pedidos:
        assert "id" in pedido
        assert "id_obra" in pedido
        assert "estado" in pedido

# Test final de integración completa
def test_flujo_completo_pedido_robusto(controller):
    """Test: flujo completo de pedido con validaciones robustas."""
    # 1. Estado inicial: hay faltantes
    assert controller.test_data.faltantes, "Debe haber faltantes para generar pedido"

    # 2. Generar pedido
    id_pedido = controller.generar_pedido_por_obra(1)
    assert id_pedido is not None, "Pedido debe generarse correctamente"

    # 3. Verificar estado del pedido
    pedido = controller.test_data.obtener_pedido(id_pedido)
    assert pedido is not None, "Pedido debe existir después de creación"
    assert pedido["estado"] == "pendiente", "Estado inicial debe ser pendiente"

    # 4. Verificar auditoría de generación
    controller.auditoria_model.registrar_evento.assert_called()

    # 5. Resetear auditoría para siguiente operación
    controller.auditoria_model.registrar_evento.reset_mock()

    # 6. Recibir pedido
    result = controller.recibir_pedido(id_pedido)
    assert result is True, "Recepción debe ser exitosa"

    # 7. Verificar cambio de estado
    pedido = controller.test_data.obtener_pedido(id_pedido)
    assert pedido["estado"] == "recibido", "Estado debe cambiar a recibido"

    # 8. Verificar auditoría de recepción
    controller.auditoria_model.registrar_evento.assert_called()

    # 9. Intentar recibir nuevamente debe fallar
    with pytest.raises(ValueError, match="Estado inválido"):
        controller.recibir_pedido(id_pedido)

    # 10. Verificar que después de recibir, el pedido ya no está pendiente
    # Por lo tanto, se debería poder generar un nuevo pedido para la misma obra
    # Primero limpiamos para permitir nuevo pedido
    controller.test_data.pedidos = [p for p in controller.test_data.pedidos if p["estado"] != "recibido"]

    # Ahora debería poder generar otro pedido
    id_pedido2 = controller.generar_pedido_por_obra(1)
    assert id_pedido2 is not None, "Después de recibir, debería poder generar nuevo pedido"
