#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test simple para debugging del controller de inventario
"""

import sys
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from rexus.modules.inventario.controller import InventarioController

class TestInventarioSimple(unittest.TestCase):
    """Test simple para inventario."""

    def test_simple_init(self):
        """Test simple de inicialización."""
        try:
            controller = InventarioController()
            self.assertIsNotNone(controller)
            print("✅ Inicialización OK")
        except Exception as e:
            print(f"❌ Error en inicialización: {e}")
            raise

    @patch('rexus.modules.inventario.controller.InventarioModel')
    def test_simple_cargar(self, mock_model_class):
        """Test simple de carga."""
        try:
            # Configurar mock
            mock_instance = Mock()
            mock_instance.obtener_productos.return_value = [
                {'id': 1, 'nombre': 'Test', 'stock': 10}
            ]
            mock_instance.obtener_productos_paginados.return_value = (
                [{'id': 1, 'nombre': 'Test', 'stock': 10}], 
                {"total_records": 1}
            )
            mock_model_class.return_value = mock_instance
            
            # Test
            controller = InventarioController()
            controller.cargar_inventario()
            
            print("✅ Carga de inventario OK")
            
        except Exception as e:
            print(f"❌ Error en carga: {e}")
            import traceback
            traceback.print_exc()
            raise

if __name__ == '__main__':
    unittest.main(verbosity=2)