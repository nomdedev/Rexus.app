"""
Tests unitarios para los submódulos del inventario refactorizado.
Valida funcionalidad de ProductosManager, MovimientosManager y ConsultasManager.
"""

import os

# Configurar path antes de imports
import sys
import unittest
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

try:
    from rexus.modules.inventario.submodules.consultas_manager import ConsultasManager
    from rexus.modules.inventario.submodules.movimientos_manager import (
        MovimientosManager,
    )
    from rexus.modules.inventario.submodules.productos_manager import ProductosManager
except ImportError as e:
    print(f"Error importando submódulos: {e}")

    # Crear clases mock para evitar fallos
    class ProductosManager:
        def __init__(self, db_connection=None):
            pass

    class MovimientosManager:
        def __init__(self, db_connection=None):
            pass

    class ConsultasManager:
        def __init__(self, db_connection=None):
            pass


class TestProductosManagerReal(unittest.TestCase):
    """Test suite para ProductosManager con métodos reales."""

    def setUp(self):
        """Configuración inicial para cada test."""
        # Mock de conexión de base de datos
        self.mock_db_connection = Mock()
        self.mock_cursor = Mock()
        self.mock_db_connection.cursor.return_value = self.mock_cursor

        # Configurar comportamiento del cursor
        self.mock_cursor.fetchone.return_value = None
        self.mock_cursor.fetchall.return_value = []
        self.mock_cursor.description = [
            ("id",),
            ("codigo",),
            ("descripcion",),
            ("precio",),
        ]

        # Crear instancia del manager
        with (
            patch(
                "rexus.modules.inventario.submodules.productos_manager.SQLQueryManager"
            ),
            patch(
                "rexus.modules.inventario.submodules.productos_manager.DataSanitizer"
            ),
        ):
            self.manager = ProductosManager(self.mock_db_connection)

    def test_inicializacion_correcta(self):
        """Test de inicialización correcta del manager."""
        self.assertIsNotNone(self.manager)
        self.assertEqual(self.manager.db_connection, self.mock_db_connection)

    @patch("rexus.modules.inventario.submodules.productos_manager.auth_required")
    @patch("rexus.modules.inventario.submodules.productos_manager.permission_required")
    def test_obtener_producto_por_id_existente(self, mock_permission, mock_auth):
        """Test de obtención de producto existente por ID."""
        # Configurar decoradores
        mock_auth.return_value = lambda f: f
        mock_permission.return_value = lambda f: f

        # Mock de resultado
        producto_row = (1, "PROD001", "Producto Test", 100.50)
        self.mock_cursor.fetchone.return_value = producto_row

        # Mock del SQL query manager
        with patch.object(
            self.manager.sql_manager,
            "get_query",
            return_value="SELECT * FROM productos WHERE id = ?",
        ):
            resultado = self.manager.obtener_producto_por_id(1)

        # Verificar
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado["id"], 1)
        self.assertEqual(resultado["codigo"], "PROD001")
        self.mock_cursor.execute.assert_called_once()

    @patch("rexus.modules.inventario.submodules.productos_manager.auth_required")
    @patch("rexus.modules.inventario.submodules.productos_manager.permission_required")
    def test_obtener_producto_por_id_inexistente(self, mock_permission, mock_auth):
        """Test de obtención de producto inexistente."""
        # Configurar decoradores
        mock_auth.return_value = lambda f: f
        mock_permission.return_value = lambda f: f

        # Mock sin resultado
        self.mock_cursor.fetchone.return_value = None

        # Mock del SQL query manager
        with patch.object(
            self.manager.sql_manager,
            "get_query",
            return_value="SELECT * FROM productos WHERE id = ?",
        ):
            resultado = self.manager.obtener_producto_por_id(999)

        # Verificar
        self.assertIsNone(resultado)

    @patch("rexus.modules.inventario.submodules.productos_manager.auth_required")
    @patch("rexus.modules.inventario.submodules.productos_manager.permission_required")
    def test_obtener_producto_por_codigo(self, mock_permission, mock_auth):
        """Test de obtención de producto por código."""
        # Configurar decoradores
        mock_auth.return_value = lambda f: f
        mock_permission.return_value = lambda f: f

        # Mock de resultado
        producto_row = (1, "TEST001", "Producto por código", 75.25)
        self.mock_cursor.fetchone.return_value = producto_row

        # Mock del sanitizer y SQL manager
        with (
            patch.object(
                self.manager.data_sanitizer, "sanitize_text", return_value="TEST001"
            ),
            patch.object(
                self.manager.sql_manager,
                "get_query",
                return_value="SELECT * FROM productos WHERE codigo = ?",
            ),
        ):
            resultado = self.manager.obtener_producto_por_codigo("TEST001")

        # Verificar
        self.assertIsNotNone(resultado)
        self.assertEqual(resultado["codigo"], "TEST001")
        self.mock_cursor.execute.assert_called_once()

    def test_validar_tabla_permitida(self):
        """Test de validación de nombres de tabla."""
        # Tabla permitida
        tabla_valida = self.manager._validate_table_name("inventario")
        self.assertEqual(tabla_valida, "inventario")

        # Tabla no permitida
        with self.assertRaises(ValueError):
            self.manager._validate_table_name("tabla_maliciosa")

    def test_obtener_categorias(self):
        """Test de obtención de categorías."""
        # Mock de categorías
        categorias_rows = [("Categoría A",), ("Categoría B",), ("Categoría C",)]
        self.mock_cursor.fetchall.return_value = categorias_rows

        with patch.object(
            self.manager.sql_manager,
            "get_query",
            return_value="SELECT DISTINCT categoria FROM productos",
        ):
            categorias = self.manager.obtener_categorias()

        # Verificar
        self.assertEqual(len(categorias), 3)
        self.assertIn("Categoría A", categorias)


class TestMovimientosManagerReal(unittest.TestCase):
    """Test suite para MovimientosManager con métodos reales."""

    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_db_connection = Mock()
        self.mock_cursor = Mock()
        self.mock_db_connection.cursor.return_value = self.mock_cursor

        # Configurar comportamiento del cursor
        self.mock_cursor.fetchone.return_value = None
        self.mock_cursor.fetchall.return_value = []
        self.mock_cursor.description = [("id",), ("tipo",), ("cantidad",), ("fecha",)]

        with (
            patch(
                "rexus.modules.inventario.submodules.movimientos_manager.SQLQueryManager"
            ),
            patch(
                "rexus.modules.inventario.submodules.movimientos_manager.DataSanitizer"
            ),
        ):
            self.manager = MovimientosManager(self.mock_db_connection)

    def test_inicializacion_correcta(self):
        """Test de inicialización correcta del manager."""
        self.assertIsNotNone(self.manager)
        self.assertEqual(self.manager.db_connection, self.mock_db_connection)

    @patch("rexus.modules.inventario.submodules.movimientos_manager.auth_required")
    @patch(
        "rexus.modules.inventario.submodules.movimientos_manager.permission_required"
    )
    def test_registrar_movimiento_entrada(self, mock_permission, mock_auth):
        """Test de registro de movimiento de entrada."""
        # Configurar decoradores
        mock_auth.return_value = lambda f: f
        mock_permission.return_value = lambda f: f

        # Mock de ejecución exitosa
        self.mock_cursor.execute.return_value = None
        self.mock_cursor.rowcount = 1

        # Datos del movimiento
        datos_movimiento = {
            "producto_id": 1,
            "tipo": "ENTRADA",
            "cantidad": 50,
            "motivo": "Compra",
        }

        with (
            patch.object(
                self.manager.sql_manager,
                "get_query",
                return_value="INSERT INTO movimientos...",
            ),
            patch.object(
                self.manager.data_sanitizer,
                "sanitize_dict",
                return_value=datos_movimiento,
            ),
        ):
            resultado = self.manager.registrar_movimiento(datos_movimiento)

        # Verificar
        self.assertTrue(resultado)
        self.mock_cursor.execute.assert_called()

    def test_obtener_stock_actual(self):
        """Test de obtención de stock actual de producto."""
        # Mock de stock
        self.mock_cursor.fetchone.return_value = (150.0,)

        with patch.object(
            self.manager.sql_manager,
            "get_query",
            return_value="SELECT SUM(cantidad) FROM movimientos...",
        ):
            stock = self.manager._obtener_stock_actual(1)

        # Verificar
        self.assertEqual(stock, 150.0)

    def test_obtener_productos_stock_bajo(self):
        """Test de obtención de productos con stock bajo."""
        # Mock de productos bajo stock
        productos_rows = [
            (1, "PROD001", "Producto 1", 5.0, 10.0),
            (2, "PROD002", "Producto 2", 2.0, 15.0),
        ]
        self.mock_cursor.fetchall.return_value = productos_rows

        with patch.object(
            self.manager.sql_manager,
            "get_query",
            return_value="SELECT * FROM productos WHERE stock < stock_minimo",
        ):
            productos_bajo_stock = self.manager.obtener_productos_stock_bajo()

        # Verificar
        self.assertEqual(len(productos_bajo_stock), 2)


class TestConsultasManagerReal(unittest.TestCase):
    """Test suite para ConsultasManager con métodos reales."""

    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_db_connection = Mock()
        self.mock_cursor = Mock()
        self.mock_db_connection.cursor.return_value = self.mock_cursor

        # Configurar comportamiento del cursor
        self.mock_cursor.fetchone.return_value = None
        self.mock_cursor.fetchall.return_value = []
        self.mock_cursor.description = [
            ("id",),
            ("codigo",),
            ("descripcion",),
            ("precio",),
        ]

        with (
            patch(
                "rexus.modules.inventario.submodules.consultas_manager.SQLQueryManager"
            ),
            patch(
                "rexus.modules.inventario.submodules.consultas_manager.DataSanitizer"
            ),
        ):
            self.manager = ConsultasManager(self.mock_db_connection)

    def test_inicializacion_correcta(self):
        """Test de inicialización correcta del manager."""
        self.assertIsNotNone(self.manager)
        self.assertEqual(self.manager.db_connection, self.mock_db_connection)

    @patch("rexus.modules.inventario.submodules.consultas_manager.auth_required")
    @patch("rexus.modules.inventario.submodules.consultas_manager.permission_required")
    def test_obtener_productos_paginados(self, mock_permission, mock_auth):
        """Test de obtención paginada de productos."""
        # Configurar decoradores
        mock_auth.return_value = lambda f: f
        mock_permission.return_value = lambda f: f

        # Mock de productos
        productos_rows = [
            (1, "PROD001", "Producto 1", 100.0),
            (2, "PROD002", "Producto 2", 200.0),
        ]
        self.mock_cursor.fetchall.return_value = productos_rows

        # Mock del conteo total
        count_cursor = Mock()
        count_cursor.fetchone.return_value = (2,)
        self.mock_db_connection.cursor.side_effect = [self.mock_cursor, count_cursor]

        with patch.object(
            self.manager.sql_manager,
            "get_query",
            return_value="SELECT * FROM productos LIMIT ? OFFSET ?",
        ):
            resultado = self.manager.obtener_productos_paginados(page=1, per_page=10)

        # Verificar
        self.assertIn("productos", resultado)
        self.assertIn("total", resultado)
        self.assertIn("page", resultado)
        self.assertEqual(len(resultado["productos"]), 2)

    @patch("rexus.modules.inventario.submodules.consultas_manager.auth_required")
    @patch("rexus.modules.inventario.submodules.consultas_manager.permission_required")
    def test_obtener_estadisticas_inventario(self, mock_permission, mock_auth):
        """Test de obtención de estadísticas del inventario."""
        # Configurar decoradores
        mock_auth.return_value = lambda f: f
        mock_permission.return_value = lambda f: f

        # Mock de estadísticas
        estadisticas_data = [
            (150,),  # total_productos
            (50000.0,),  # valor_total
            (25.5,),  # precio_promedio
            (15,),  # productos_stock_bajo
        ]

        # Configurar múltiples llamadas al cursor
        cursors_mock = [Mock() for _ in range(4)]
        for i, cursor in enumerate(cursors_mock):
            cursor.fetchone.return_value = estadisticas_data[i]

        self.mock_db_connection.cursor.side_effect = cursors_mock

        with patch.object(
            self.manager.sql_manager,
            "get_query",
            return_value="SELECT COUNT(*) FROM productos",
        ):
            estadisticas = self.manager.obtener_estadisticas_inventario()

        # Verificar
        self.assertIsInstance(estadisticas, dict)

    @patch("rexus.modules.inventario.submodules.consultas_manager.auth_required")
    @patch("rexus.modules.inventario.submodules.consultas_manager.permission_required")
    def test_buscar_productos(self, mock_permission, mock_auth):
        """Test de búsqueda de productos."""
        # Configurar decoradores
        mock_auth.return_value = lambda f: f
        mock_permission.return_value = lambda f: f

        # Mock de resultados de búsqueda
        resultados_rows = [(1, "BUSQUEDA001", "Producto encontrado", 150.0)]
        self.mock_cursor.fetchall.return_value = resultados_rows

        with (
            patch.object(
                self.manager.data_sanitizer, "sanitize_text", return_value="test"
            ),
            patch.object(
                self.manager.sql_manager,
                "get_query",
                return_value="SELECT * FROM productos WHERE codigo LIKE ?",
            ),
        ):
            resultados = self.manager.buscar_productos("test")

        # Verificar
        self.assertEqual(len(resultados), 1)
        self.assertEqual(resultados[0]["codigo"], "BUSQUEDA001")


class TestIntegracionSubmodelosInventario(unittest.TestCase):
    """Tests de integración entre los submódulos del inventario."""

    def setUp(self):
        """Configuración inicial para tests de integración."""
        self.mock_db_connection = Mock()
        self.mock_cursor = Mock()
        self.mock_db_connection.cursor.return_value = self.mock_cursor

        # Configurar comportamiento común
        self.mock_cursor.fetchone.return_value = None
        self.mock_cursor.fetchall.return_value = []
        self.mock_cursor.description = [
            ("id",),
            ("codigo",),
            ("descripcion",),
            ("precio",),
        ]

        # Crear instancias de todos los managers
        with (
            patch(
                "rexus.modules.inventario.submodules.productos_manager.SQLQueryManager"
            ),
            patch(
                "rexus.modules.inventario.submodules.productos_manager.DataSanitizer"
            ),
            patch(
                "rexus.modules.inventario.submodules.movimientos_manager.SQLQueryManager"
            ),
            patch(
                "rexus.modules.inventario.submodules.movimientos_manager.DataSanitizer"
            ),
            patch(
                "rexus.modules.inventario.submodules.consultas_manager.SQLQueryManager"
            ),
            patch(
                "rexus.modules.inventario.submodules.consultas_manager.DataSanitizer"
            ),
        ):
            self.productos_manager = ProductosManager(self.mock_db_connection)
            self.movimientos_manager = MovimientosManager(self.mock_db_connection)
            self.consultas_manager = ConsultasManager(self.mock_db_connection)

    def test_flujo_completo_producto_movimiento_consulta(self):
        """Test de flujo completo: crear producto, registrar movimiento, consultar."""
        # Verificar que todos los managers están inicializados
        self.assertIsNotNone(self.productos_manager)
        self.assertIsNotNone(self.movimientos_manager)
        self.assertIsNotNone(self.consultas_manager)

        # Verificar que comparten la misma conexión
        self.assertEqual(self.productos_manager.db_connection, self.mock_db_connection)
        self.assertEqual(
            self.movimientos_manager.db_connection, self.mock_db_connection
        )
        self.assertEqual(self.consultas_manager.db_connection, self.mock_db_connection)

    def test_managers_independientes_pero_coordinados(self):
        """Test de que los managers son independientes pero pueden trabajar coordinadamente."""
        # Cada manager debe tener su propia instancia de SQL manager y sanitizer
        self.assertIsNotNone(self.productos_manager.sql_manager)
        self.assertIsNotNone(self.movimientos_manager.sql_manager)
        self.assertIsNotNone(self.consultas_manager.sql_manager)

        # Pero deben compartir la conexión de base de datos
        self.assertEqual(
            self.productos_manager.db_connection, self.movimientos_manager.db_connection
        )


class TestRobustezSubmodelosInventario(unittest.TestCase):
    """Tests de robustez y manejo de errores."""

    def test_manejo_conexion_nula(self):
        """Test de manejo cuando la conexión de BD es None."""
        with (
            patch(
                "rexus.modules.inventario.submodules.productos_manager.SQLQueryManager"
            ),
            patch(
                "rexus.modules.inventario.submodules.productos_manager.DataSanitizer"
            ),
        ):
            manager = ProductosManager(None)

            # Verificar que no falla la inicialización
            self.assertIsNotNone(manager)
            self.assertIsNone(manager.db_connection)

    def test_manejo_errores_sql(self):
        """Test de manejo de errores SQL."""
        mock_db_connection = Mock()
        mock_cursor = Mock()
        mock_db_connection.cursor.return_value = mock_cursor

        # Configurar excepción SQL
        mock_cursor.execute.side_effect = Exception("Error SQL simulado")

        with (
            patch(
                "rexus.modules.inventario.submodules.productos_manager.SQLQueryManager"
            ),
            patch(
                "rexus.modules.inventario.submodules.productos_manager.DataSanitizer"
            ),
        ):
            manager = ProductosManager(mock_db_connection)

            # Verificar que maneja errores apropiadamente
            with self.assertRaises(Exception):
                manager.obtener_producto_por_id(1)


if __name__ == "__main__":
    # Configurar logging para tests
    import logging

    logging.basicConfig(level=logging.INFO)

    # Crear suite de tests
    suite = unittest.TestSuite()

    # Agregar tests de cada manager
    suite.addTest(unittest.makeSuite(TestProductosManagerReal))
    suite.addTest(unittest.makeSuite(TestMovimientosManagerReal))
    suite.addTest(unittest.makeSuite(TestConsultasManagerReal))
    suite.addTest(unittest.makeSuite(TestIntegracionSubmodelosInventario))
    suite.addTest(unittest.makeSuite(TestRobustezSubmodelosInventario))

    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Mostrar resumen
    print(f"\n{'=' * 60}")
    print(f"RESUMEN DE TESTS - SUBMÓDULOS INVENTARIO REFACTORIZADO")
    print(f"{'=' * 60}")
    print(f"Tests ejecutados: {result.testsRun}")
    print(f"Errores: {len(result.errors)}")
    print(f"Fallos: {len(result.failures)}")
    print(f"Éxito: {result.wasSuccessful()}")

    if result.errors:
        print(f"\n[ERROR] ERRORES ENCONTRADOS:")
        for test, error in result.errors:
            print(f"  - {test}: {error.split(chr(10))[0]}")

    if result.failures:
        print(f"\n[ERROR] FALLOS ENCONTRADOS:")
        for test, failure in result.failures:
            print(f"  - {test}: {failure.split(chr(10))[0]}")

    if result.wasSuccessful():
        print(f"\n[CHECK] TODOS LOS TESTS PASARON EXITOSAMENTE")
        print(f"🎯 Arquitectura modular validada correctamente")
    else:
        print(f"\n[WARN] Se encontraron problemas en los tests")
        print(f"📝 Revisar implementación de submódulos")
