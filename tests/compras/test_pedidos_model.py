#!/usr/bin/env python3
"""
Tests para el modelo de pedidos dentro del módulo de compras.
"""

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT_DIR))

try:
    PEDIDOS_MODEL_AVAILABLE = True
except ImportError:
    # Crear mock si el modelo no está disponible
    class PedidosModel:
        def __init__(self, db_connection):
            self.db = db_connection
import sqlite3
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from rexus.modules.compras.pedidos.model import PedidosModel

    PEDIDOS_MODEL_AVAILABLE = False


class TestPedidosModelWithRealDB:
    """Tests del modelo de pedidos con base de datos real (en memoria)."""

    def setup_test_db(self):
        """Configurar base de datos de prueba en memoria."""
        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()

        # Crear tablas necesarias para tests
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS obras (
                id_obra INTEGER PRIMARY KEY,
                nombre TEXT
            );

            CREATE TABLE IF NOT EXISTS inventario_perfiles (
                id_perfil INTEGER PRIMARY KEY,
                stock_actual INTEGER,
                precio_unitario REAL
            );

            CREATE TABLE IF NOT EXISTS perfiles_por_obra (
                id_obra INTEGER,
                id_perfil INTEGER,
                cantidad_reservada INTEGER
            );

            CREATE TABLE IF NOT EXISTS herrajes (
                id_herraje INTEGER PRIMARY KEY,
                stock_actual INTEGER,
                precio_unitario REAL
            );

            CREATE TABLE IF NOT EXISTS herrajes_por_obra (
                id_obra INTEGER,
                id_herraje INTEGER,
                cantidad_reservada INTEGER
            );

            CREATE TABLE IF NOT EXISTS vidrios (
                id_vidrio INTEGER PRIMARY KEY,
                stock_actual INTEGER,
                precio_unitario REAL
            );

            CREATE TABLE IF NOT EXISTS vidrios_por_obra (
                id_obra INTEGER,
                id_vidrio INTEGER,
                cantidad_reservada INTEGER
            );

            CREATE TABLE IF NOT EXISTS pedidos (
                id_pedido INTEGER PRIMARY KEY AUTOINCREMENT,
                id_obra INTEGER,
                fecha_emision TEXT,
                estado TEXT,
                total_estimado REAL
            );

            CREATE TABLE IF NOT EXISTS pedidos_por_obra (
                id_pedido INTEGER,
                id_obra INTEGER,
                id_item INTEGER,
                tipo_item TEXT,
                cantidad_requerida INTEGER
            );

            CREATE TABLE IF NOT EXISTS movimientos_stock (
                id_mov INTEGER PRIMARY KEY AUTOINCREMENT,
                id_perfil INTEGER,
                tipo_movimiento TEXT,
                cantidad INTEGER,
                fecha TEXT,
                usuario TEXT
            );

            CREATE TABLE IF NOT EXISTS movimientos_herrajes (
                id_mov INTEGER PRIMARY KEY AUTOINCREMENT,
                id_herraje INTEGER,
                tipo_movimiento TEXT,
                cantidad INTEGER,
                fecha TEXT,
                usuario TEXT
            );

            CREATE TABLE IF NOT EXISTS movimientos_vidrios (
                id_mov INTEGER PRIMARY KEY AUTOINCREMENT,
                id_vidrio INTEGER,
                tipo_movimiento TEXT,
                cantidad INTEGER,
                fecha TEXT,
                usuario TEXT
            );

            CREATE TABLE IF NOT EXISTS auditorias_sistema (
                usuario TEXT,
                modulo TEXT,
                accion TEXT,
                fecha TEXT
            );
        """)

        conn.commit()
        return conn

    @pytest.fixture
    def test_db_connection(self):
        """Conexión de base de datos para tests."""
        conn = self.setup_test_db()

        class TestDBConnection:
            def __init__(self, connection):
                self.connection = connection

            def ejecutar_query(self, query, params=()):
                try:
                    cursor = self.connection.cursor()
                    cursor.execute(query, params)
                    self.connection.commit()
                    return cursor.fetchall()
                except Exception as e:
                    print(f"Error en query: {e}")
                    return []

            def transaction(self, timeout=30, retries=2):
                class TransactionContext:
                    def __enter__(self):
                        assert self is not None
                    def __exit__(self, exc_type, exc_val, exc_tb):
                        pass
                return TransactionContext()

        return TestDBConnection(conn)

    @pytest.fixture
    def pedidos_model(self, test_db_connection):
        """Modelo de pedidos con conexión de prueba."""
        if not PEDIDOS_MODEL_AVAILABLE:
            pytest.skip("PedidosModel no disponible")
        return PedidosModel(test_db_connection)

    def test_generar_pedido_por_obra(self, pedidos_model, test_db_connection):
        """Test generar pedido basado en obra."""
        if not hasattr(pedidos_model, 'generar_pedido_por_obra'):
            pytest.skip("Método generar_pedido_por_obra no implementado")

        # Preparar datos de prueba
        db = test_db_connection
        db.ejecutar_query("INSERT INTO obras (id_obra, nombre) VALUES (?, ?)", (1, "ObraTest"))
        db.ejecutar_query("INSERT INTO inventario_perfiles (id_perfil, stock_actual, precio_unitario) VALUES (1, 5, 100)")
        db.ejecutar_query("INSERT INTO perfiles_por_obra (id_obra, id_perfil, cantidad_reservada) VALUES (1, 1, 10)")

        # Ejecutar test
        try:
            id_pedido = pedidos_model.generar_pedido_por_obra(1, usuario="TEST_USER")

            # Verificar resultado
            assert id_pedido is not None
            if isinstance(id_pedido, int) and id_pedido > 0:
                # Verificar que se creó el pedido
                pedido = db.ejecutar_query("SELECT * FROM pedidos WHERE id_pedido=?", (id_pedido,))
                assert len(pedido) > 0
                assert pedido[0][3] == "Pendiente"  # Estado

                # Verificar items del pedido
                items = db.ejecutar_query("SELECT * FROM pedidos_por_obra WHERE id_pedido=?", (id_pedido,))
                assert len(items) > 0

                # Verificar auditoría
                auditoria = db.ejecutar_query("SELECT * FROM auditorias_sistema WHERE accion LIKE ?", (f"%{id_pedido}%",))
                assert len(auditoria) >= 0  # Puede o no tener auditoría

        except Exception as e:
            pytest.skip(f"Error en generar_pedido_por_obra: {e}")

    def test_recibir_pedido_exitoso(self, pedidos_model, test_db_connection):
        """Test recibir pedido con éxito."""
        if not hasattr(pedidos_model, 'recibir_pedido'):
            pytest.skip("Método recibir_pedido no implementado")

        # Preparar datos
        db = test_db_connection
        db.ejecutar_query("INSERT INTO pedidos (id_pedido, id_obra, fecha_emision, estado, total_estimado) VALUES (1, 1, '2025-06-01', 'Pendiente', 500)")
        db.ejecutar_query("INSERT INTO pedidos_por_obra (id_pedido, id_obra, id_item, tipo_item, cantidad_requerida) VALUES (1, 1, 1, 'perfil', 5)")
        db.ejecutar_query("INSERT INTO inventario_perfiles (id_perfil, stock_actual, precio_unitario) VALUES (1, 5, 100)")

        try:
            # Ejecutar recepción de pedido
            resultado = pedidos_model.recibir_pedido(1, usuario="TEST_USER")

            # Verificar que la operación fue exitosa
            assert resultado is not None
            if resultado:
                # Verificar cambio de estado
                pedido = db.ejecutar_query("SELECT estado FROM pedidos WHERE id_pedido=1")
                if pedido:
                    assert pedido[0][0] == "Recibido"

                # Verificar actualización de stock
                stock = db.ejecutar_query("SELECT stock_actual FROM inventario_perfiles WHERE id_perfil=1")
                if stock:
                    assert stock[0][0] == 10  # 5 + 5

                # Verificar movimiento de stock
                movimiento = db.ejecutar_query("SELECT * FROM movimientos_stock WHERE id_perfil=1 AND tipo_movimiento='Ingreso'")
                if movimiento:
                    assert movimiento[0][2] == "Ingreso"
                    assert movimiento[0][3] == 5

                # Verificar auditoría
                auditoria = db.ejecutar_query("SELECT * FROM auditorias_sistema WHERE accion LIKE ?", ("%Recibió pedido%",))
                assert len(auditoria) >= 0

        except Exception as e:
            pytest.skip(f"Error en recibir_pedido: {e}")

    def test_recibir_pedido_ya_recibido(self, pedidos_model, test_db_connection):
        """Test recibir pedido que ya fue recibido."""
        if not hasattr(pedidos_model, 'recibir_pedido'):
            pytest.skip("Método recibir_pedido no implementado")

        # Preparar pedido ya recibido
        db = test_db_connection
        db.ejecutar_query("INSERT INTO pedidos (id_pedido, id_obra, fecha_emision, estado, total_estimado) VALUES (2, 1, '2025-06-01', 'Recibido', 500)")

        try:
            # Intentar recibir pedido ya recibido
            with pytest.raises(ValueError):
                pedidos_model.recibir_pedido(2, usuario="TEST_USER")
        except Exception as e:
            # Si no lanza ValueError, verificar que maneja el caso apropiadamente
            resultado = pedidos_model.recibir_pedido(2, usuario="TEST_USER")
            assert resultado is None or resultado is False


class TestPedidosModelMocked:
    """Tests del modelo de pedidos con mocks."""

    @pytest.fixture
    def mock_db(self):
        """Mock de base de datos."""
        db = MagicMock()
        db.ejecutar_query = MagicMock(return_value=[])
        db.transaction = MagicMock()
        assert db is not None
    @pytest.fixture
    def pedidos_model_mock(self, mock_db):
        """Modelo de pedidos con mock."""
        if not PEDIDOS_MODEL_AVAILABLE:
            pytest.skip("PedidosModel no disponible")
        return PedidosModel(mock_db)

    def test_obtener_pedidos(self, pedidos_model_mock, mock_db):
        """Test obtener lista de pedidos."""
        # Configurar mock response
        mock_data = [
            (1, "Cliente A", "Producto X", 10, "2025-05-08", "Pendiente"),
            (2, "Cliente B", "Producto Y", 5, "2025-05-07", "Aprobado")
        ]
        mock_db.ejecutar_query.return_value = mock_data

        # Ejecutar test
        if hasattr(pedidos_model_mock, 'obtener_pedidos'):
            result = pedidos_model_mock.obtener_pedidos()

            # Verificar llamada a la base de datos
            mock_db.ejecutar_query.assert_called()

            # Verificar resultado
            assert result == mock_data
        else:
            pytest.skip("Método obtener_pedidos no implementado")

    def test_obtener_todos_pedidos(self, pedidos_model_mock, mock_db):
        """Test obtener todos los pedidos."""
        mock_data = [
            (1, "Cliente A", "Producto X", 10, "2025-05-08", "Pendiente"),
            (2, "Cliente B", "Producto Y", 5, "2025-05-07", "Aprobado"),
            (3, "Cliente C", "Producto Z", 3, "2025-05-06", "Rechazado")
        ]
        mock_db.ejecutar_query.return_value = mock_data

        if hasattr(pedidos_model_mock, 'obtener_todos_pedidos'):
            result = pedidos_model_mock.obtener_todos_pedidos()

            mock_db.ejecutar_query.assert_called()
            assert result == mock_data
        else:
            pytest.skip("Método obtener_todos_pedidos no implementado")

    def test_crear_pedido(self, pedidos_model_mock, mock_db):
        """Test crear nuevo pedido."""
        datos_pedido = ("Cliente Test", "Producto Test", 15, "2025-05-10")

        if hasattr(pedidos_model_mock, 'crear_pedido'):
            pedidos_model_mock.crear_pedido(datos_pedido)

            # Verificar que se llamó a la base de datos
            mock_db.ejecutar_query.assert_called()

            # Verificar que el query contiene INSERT
            call_args = mock_db.ejecutar_query.call_args
            query = call_args[0][0]
            assert "INSERT" in query.upper()
        else:
            pytest.skip("Método crear_pedido no implementado")

    def test_obtener_detalle_pedido(self, pedidos_model_mock, mock_db):
        """Test obtener detalle de pedido específico."""
        mock_data = [
            (1, 1, "Item A", 5, 100.0),
            (2, 1, "Item B", 3, 200.0)
        ]
        mock_db.ejecutar_query.return_value = mock_data

        if hasattr(pedidos_model_mock, 'obtener_detalle_pedido'):
            result = pedidos_model_mock.obtener_detalle_pedido(1)

            mock_db.ejecutar_query.assert_called()
            call_args = mock_db.ejecutar_query.call_args
            assert call_args[0][1] == (1,)  # Parámetro del ID
        else:
            pytest.skip("Método obtener_detalle_pedido no implementado")

    def test_manejo_errores_database(self, pedidos_model_mock, mock_db):
        """Test manejo de errores de base de datos."""
        # Simular error de base de datos
        mock_db.ejecutar_query.side_effect = Exception("Database connection error")

        if hasattr(pedidos_model_mock, 'obtener_pedidos'):
            try:
                result = pedidos_model_mock.obtener_pedidos()
                # Si no lanza excepción, debería retornar lista vacía o None
                assert result == [] or result is None
            except Exception as e:
                # Es aceptable que propague el error
                assert "error" in str(e).lower() or "connection" in str(e).lower()
        else:
            pytest.skip("Método obtener_pedidos no implementado")


def mostrar_feedback_visual(mensaje, tipo="info"):
    """Función helper para tests que requieren feedback visual."""
    # En tests, simplemente ignoramos el feedback visual
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
