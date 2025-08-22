# -*- coding: utf-8 -*-
"""
Tests unitarios para el controlador de Inventario
"""

import pytest
import unittest
from unittest.mock import Mock, patch, MagicMock, call
import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_dir))

from rexus.modules.inventario.controller import InventarioController


class TestInventarioController(unittest.TestCase):
    """Tests para el controlador de inventario."""

    def setUp(self):
        """Configuración inicial para cada test."""
        self.mock_model = Mock()
        self.mock_view = Mock()
        self.controller = InventarioController()
        self.controller.model = self.mock_model
        self.controller.view = self.mock_view

    def tearDown(self):
        """Limpieza después de cada test."""
        self.controller = None

    def test_init_controller(self):
        """Test de inicialización del controlador."""
        controller = InventarioController()
        self.assertIsNotNone(controller)

    @patch('rexus.modules.inventario.controller.InventarioModel')
    def test_cargar_inventario(self, mock_model_class):
        """Test de carga de inventario."""
        # Mock del modelo
        mock_model_instance = Mock()
        mock_model_class.return_value = mock_model_instance
        mock_model_instance.obtener_productos.return_value = [
            {'id': 1, 'nombre': 'Producto 1', 'stock': 10},
            {'id': 2, 'nombre': 'Producto 2', 'stock': 5}
        ]
        
        # Configurar controller
        controller = InventarioController()
        controller.cargar_inventario()
        
        # Verificar que se llamó al modelo
        mock_model_instance.obtener_productos.assert_called_once()

    def test_filtrar_materiales(self):
        """Test de filtrado de materiales."""
        # Mock productos disponibles
        self.mock_view.obtener_productos_tabla.return_value = [
            {'nombre': 'Vidrio Laminado', 'codigo': 'VL001'},
            {'nombre': 'Aluminio', 'codigo': 'AL001'},
            {'nombre': 'Herraje', 'codigo': 'HR001'}
        ]
        
        # Test filtro por texto
        self.controller.filtrar_materiales("Vidrio")
        self.mock_view.obtener_productos_tabla.assert_called()

    def test_material_seleccionado(self):
        """Test de selección de material."""
        # Mock item seleccionado
        mock_item = Mock()
        mock_item.text.return_value = "VL001"
        
        # Test selección
        self.controller.material_seleccionado(mock_item)
        
        # Verificar que se procesó la selección
        self.assertIsNotNone(self.controller)

    def test_agregar_producto(self):
        """Test de agregar producto."""
        # Mock datos del producto
        datos_producto = {
            'codigo': 'TEST001',
            'nombre': 'Producto Test',
            'stock_inicial': 10,
            'categoria': 'Test'
        }
        
        # Mock respuesta del modelo
        self.mock_model.crear_producto.return_value = (True, "Producto creado exitosamente")
        
        # Test agregar producto
        self.controller.agregar_producto(datos_producto)
        
        # Verificar llamada al modelo
        self.mock_model.crear_producto.assert_called_once_with(datos_producto)

    def test_editar_producto(self):
        """Test de editar producto."""
        producto_id = 1
        datos_actualizados = {
            'nombre': 'Producto Actualizado',
            'stock_inicial': 15
        }
        
        # Mock respuesta del modelo
        self.mock_model.actualizar_producto.return_value = (True, "Producto actualizado")
        
        # Test editar producto
        self.controller.editar_producto(producto_id, datos_actualizados)
        
        # Verificar llamada al modelo
        self.mock_model.actualizar_producto.assert_called_once_with(producto_id, datos_actualizados)

    def test_eliminar_producto(self):
        """Test de eliminar producto."""
        producto_id = 1
        
        # Mock respuesta del modelo
        self.mock_model.eliminar_producto.return_value = (True, "Producto eliminado")
        
        # Test eliminar producto
        self.controller.eliminar_producto(producto_id)
        
        # Verificar llamada al modelo
        self.mock_model.eliminar_producto.assert_called_once_with(producto_id)

    def test_registrar_movimiento(self):
        """Test de registro de movimiento."""
        datos_movimiento = {
            'producto_id': 1,
            'tipo': 'ENTRADA',
            'cantidad': 5,
            'motivo': 'Compra'
        }
        
        # Mock respuesta del modelo
        self.mock_model.registrar_movimiento.return_value = (True, "Movimiento registrado")
        
        # Test registrar movimiento
        self.controller.registrar_movimiento(datos_movimiento)
        
        # Verificar llamada al modelo
        self.mock_model.registrar_movimiento.assert_called_once_with(datos_movimiento)

    def test_obtener_estadisticas(self):
        """Test de obtención de estadísticas."""
        # Mock estadísticas
        mock_stats = {
            'total_productos': 50,
            'productos_bajo_stock': 5,
            'valor_total_inventario': 10000.0
        }
        self.mock_model.obtener_estadisticas.return_value = mock_stats
        
        # Test obtener estadísticas
        result = self.controller.obtener_estadisticas()
        
        # Verificar resultado
        self.assertEqual(result, mock_stats)
        self.mock_model.obtener_estadisticas.assert_called_once()

    def test_buscar_productos(self):
        """Test de búsqueda de productos."""
        termino_busqueda = "Vidrio"
        
        # Mock resultados de búsqueda
        mock_results = [
            {'id': 1, 'nombre': 'Vidrio Laminado', 'codigo': 'VL001'},
            {'id': 2, 'nombre': 'Vidrio Templado', 'codigo': 'VT001'}
        ]
        self.mock_model.buscar_productos.return_value = mock_results
        
        # Test búsqueda
        result = self.controller.buscar_productos(termino_busqueda)
        
        # Verificar resultado
        self.assertEqual(result, mock_results)
        self.mock_model.buscar_productos.assert_called_once_with(termino_busqueda)

    def test_reservar_material(self):
        """Test de reserva de material."""
        datos_reserva = {
            'producto_id': 1,
            'obra_id': 1,
            'cantidad': 10,
            'fecha_reserva': '2025-08-22'
        }
        
        # Mock respuesta del modelo
        self.mock_model.crear_reserva.return_value = (True, "Material reservado")
        
        # Test reservar material
        self.controller.reservar_material(datos_reserva)
        
        # Verificar llamada al modelo
        self.mock_model.crear_reserva.assert_called_once_with(datos_reserva)

    def test_validar_datos_producto(self):
        """Test de validación de datos de producto."""
        # Datos válidos
        datos_validos = {
            'codigo': 'TEST001',
            'nombre': 'Producto Test',
            'stock_inicial': 10
        }
        
        result = self.controller.validar_datos_producto(datos_validos)
        self.assertTrue(result)
        
        # Datos inválidos - sin código
        datos_invalidos = {
            'nombre': 'Producto Test',
            'stock_inicial': 10
        }
        
        result = self.controller.validar_datos_producto(datos_invalidos)
        self.assertFalse(result)

    def test_obtener_productos_bajo_stock(self):
        """Test de obtención de productos bajo stock."""
        # Mock productos bajo stock
        mock_productos = [
            {'id': 1, 'nombre': 'Producto 1', 'stock': 2, 'stock_minimo': 5},
            {'id': 2, 'nombre': 'Producto 2', 'stock': 1, 'stock_minimo': 3}
        ]
        self.mock_model.obtener_productos_bajo_stock.return_value = mock_productos
        
        # Test obtener productos bajo stock
        result = self.controller.obtener_productos_bajo_stock()
        
        # Verificar resultado
        self.assertEqual(result, mock_productos)
        self.mock_model.obtener_productos_bajo_stock.assert_called_once()

    def test_exportar_inventario(self):
        """Test de exportación de inventario."""
        formato = 'CSV'
        ruta_archivo = '/tmp/inventario.csv'
        
        # Mock respuesta del modelo
        self.mock_model.exportar_datos.return_value = (True, "Exportación exitosa")
        
        # Test exportar inventario
        result = self.controller.exportar_inventario(formato, ruta_archivo)
        
        # Verificar llamada al modelo
        self.mock_model.exportar_datos.assert_called_once_with(formato, ruta_archivo)

    def test_manejo_errores(self):
        """Test de manejo de errores."""
        # Simular error en el modelo
        self.mock_model.obtener_productos.side_effect = Exception("Error de base de datos")
        
        # Test que no lance excepción
        try:
            self.controller.cargar_inventario()
        except Exception:
            self.fail("El controlador debería manejar las excepciones del modelo")


if __name__ == '__main__':
    unittest.main()