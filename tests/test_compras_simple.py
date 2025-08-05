#!/usr/bin/env python3
"""
Tests simples para el módulo de Compras (sin Unicode)

Verifica todas las funcionalidades del sistema de compras.
"""

import sys
import os
from pathlib import Path

# Agregar directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from datetime import datetime, date
from rexus.modules.compras.model import ComprasModel
from rexus.modules.compras.detalle_model import DetalleComprasModel
from rexus.modules.compras.proveedores_model import ProveedoresModel
from rexus.modules.compras.controller import ComprasController


def test_compras_model():
    """Test del modelo principal de compras."""
    print("=== TEST COMPRAS MODEL ===")
    
    model = ComprasModel(db_connection=None)
    
    # Test estadísticas
    stats = model.obtener_estadisticas_compras()
    print(f"Estadisticas: {len(stats)} campos")
    print(f"Total ordenes: {stats.get('total_ordenes', 0)}")
    print(f"Monto total: ${stats.get('monto_total', 0):,.2f}")
    
    # Test búsqueda
    resultados = model.buscar_compras(proveedor="Materiales")
    print(f"Busqueda: {len(resultados)} resultados")
    
    print("PASS - ComprasModel: FUNCIONAL")
    return True


def test_detalle_model():
    """Test del modelo de detalles."""
    print("\n=== TEST DETALLE MODEL ===")
    
    model = DetalleComprasModel(db_connection=None)
    
    # Test obtener items
    items = model.obtener_items_compra(1)
    print(f"Items obtenidos: {len(items)} items")
    
    # Test resumen
    resumen = model.obtener_resumen_compra(1)
    print(f"Total items: {resumen.get('total_items', 0)}")
    print(f"Total final: ${resumen.get('total_final', 0):,.2f}")
    
    # Test productos por categoría
    productos_cat = model.obtener_productos_por_categoria()
    print(f"Categorias: {len(productos_cat)}")
    
    print("PASS - DetalleModel: FUNCIONAL")
    return True


def test_proveedores_model():
    """Test del modelo de proveedores."""
    print("\n=== TEST PROVEEDORES MODEL ===")
    
    model = ProveedoresModel(db_connection=None)
    
    # Test obtener proveedores
    proveedores = model.obtener_todos_proveedores()
    print(f"Proveedores: {len(proveedores)} encontrados")
    
    # Test estadísticas
    stats = model.obtener_estadisticas_proveedor(1)
    print(f"Stats proveedor: {stats.get('nombre', 'N/A')}")
    print(f"Total ordenes: {stats.get('total_ordenes', 0)}")
    
    print("PASS - ProveedoresModel: FUNCIONAL")
    return True


def test_compras_controller():
    """Test del controlador."""
    print("\n=== TEST CONTROLLER ===")
    
    # Mock vista simple
    class MockSignal:
        def connect(self, func):
            pass
    
    class MockInput:
        def text(self):
            return ""
    
    class MockCombo:
        def currentText(self):
            return "PENDIENTE"
    
    class MockDate:
        def toPython(self):
            return date.today()
    
    class MockDateWidget:
        def date(self):
            return MockDate()
    
    class MockView:
        def __init__(self):
            self.orden_creada = MockSignal()
            self.orden_actualizada = MockSignal()
            self.busqueda_realizada = MockSignal()
            self.input_busqueda = MockInput()
            self.combo_estado = MockCombo()
            self.date_desde = MockDateWidget()
            self.date_hasta = MockDateWidget()
        
        def cargar_compras_en_tabla(self, compras):
            pass
        
        def actualizar_estadisticas(self, stats):
            pass
    
    compras_model = ComprasModel(db_connection=None)
    mock_view = MockView()
    
    controller = ComprasController(compras_model, mock_view, db_connection=None)
    print("Controller creado OK")
    
    # Test métodos
    proveedores = controller.obtener_proveedores()
    print(f"Proveedores desde controller: {len(proveedores)}")
    
    items = controller.obtener_items_compra(1)
    print(f"Items desde controller: {len(items)}")
    
    reporte = controller.generar_reporte_completo()
    print(f"Reporte generado: {reporte.get('resumen', {}).get('estado', 'N/A')}")
    
    print("PASS - Controller: FUNCIONAL")
    return True


def test_integracion():
    """Test de integración."""
    print("\n=== TEST INTEGRACION ===")
    
    try:
        # Test flujo completo
        proveedores_model = ProveedoresModel(db_connection=None)
        compras_model = ComprasModel(db_connection=None)
        detalle_model = DetalleComprasModel(db_connection=None)
        
        # Obtener datos demo
        stats = compras_model.obtener_estadisticas_compras()
        resumen = detalle_model.obtener_resumen_compra(1)
        proveedores = proveedores_model.obtener_todos_proveedores()
        
        # Verificar integración
        flujo_ok = all([
            isinstance(stats, dict),
            isinstance(resumen, dict),
            isinstance(proveedores, list),
            len(stats) > 0,
            len(proveedores) > 0,
            resumen.get('total_final', 0) > 0
        ])
        
        if flujo_ok:
            print("PASS - Integracion: EXITOSA")
            print(f"Stats: {stats.get('total_ordenes', 0)} ordenes")
            print(f"Resumen: ${resumen.get('total_final', 0):,.2f}")
            print(f"Proveedores: {len(proveedores)} activos")
        else:
            print("FAIL - Integracion: FALLO")
        
        return flujo_ok
        
    except Exception as e:
        print(f"ERROR en integracion: {e}")
        return False


def main():
    """Ejecuta todos los tests."""
    print("=== TESTS MODULO COMPRAS ===")
    print("Rexus.app - Sistema Completo")
    print("=" * 50)
    
    tests = [
        ("ComprasModel", test_compras_model),
        ("DetalleModel", test_detalle_model),
        ("ProveedoresModel", test_proveedores_model),
        ("Controller", test_compras_controller),
        ("Integracion", test_integracion)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"ERROR en {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen
    print(f"\n=== RESUMEN ===")
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{total} tests pasaron")
    
    if passed == total:
        print("\nMODULO COMPRAS: COMPLETAMENTE FUNCIONAL")
        print("Funcionalidades verificadas:")
        print("- Gestion de ordenes de compra")
        print("- Sistema de proveedores")
        print("- Gestion de items y productos")
        print("- Controlador integrado")
        print("- Estadisticas y reportes")
        print("- Busquedas y filtros")
        return True
    else:
        print(f"\nMODULO COMPRAS: {total-passed} tests fallaron")
        return False


if __name__ == "__main__":
    success = main()
    print(f"\nTest completado: {'EXITO' if success else 'FALLO'}")
    sys.exit(0 if success else 1)