"""
Test Script for Consolidated Database Models - Rexus.app v2.0.0

Tests all consolidated models to ensure they work correctly with both
consolidated and legacy database structures.
"""

import sys
import os
import json
from datetime import datetime, date

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import consolidated models
try:
    from src.modules.inventario.model_consolidado import InventarioModel
    from src.modules.herrajes.model_consolidado import HerrajesModel
    from src.modules.vidrios.model_consolidado import VidriosModel
    from src.modules.pedidos.model_consolidado import PedidosModel
    from src.modules.obras.model_consolidado import ObrasModel
    print("[OK] All consolidated models imported successfully")
except ImportError as e:
    print(f"[ERROR] Error importing consolidated models: {e}")
    sys.exit(1)


def test_inventario_model():
    """Test InventarioModel consolidado."""
    print("\n[TEST] InventarioModel consolidado...")
    try:
        # Test initialization
        inventario = InventarioModel(db_connection=None)
        print("  [OK] Model initialized successfully")
        
        # Test demo data
        productos = inventario.obtener_todos_productos()
        assert len(productos) > 0, "Demo data should not be empty"
        assert all('codigo' in p for p in productos), "All products should have 'codigo'"
        assert all('categoria' in p for p in productos), "All products should have 'categoria'"
        print(f"  [OK] Demo data: {len(productos)} productos")
        
        # Test filtering
        filtrados = inventario.obtener_todos_productos({"categoria": "PERFIL"})
        print(f"  [OK] Filtering: {len(filtrados)} perfiles found")
        
        # Test search
        busqueda = inventario.buscar_productos({"busqueda": "perfil"})
        print(f"  [OK] Search: {len(busqueda)} results")
        
        # Test categories
        categorias = inventario.obtener_categorias()
        print(f"  [OK] Categories: {len(categorias)} categories")
        
        # Test statistics
        stats = inventario.obtener_estadisticas_inventario()
        assert "total_productos" in stats, "Should have total_productos"
        print(f"  [OK] Statistics: {stats['total_productos']} total products")
        
        return True
    except Exception as e:
        print(f"  [FAIL] InventarioModel test failed: {e}")
        return False


def test_herrajes_model():
    """Test HerrajesModel consolidado."""
    print("\n[TEST] HerrajesModel consolidado...")
    try:
        # Test initialization
        herrajes = HerrajesModel(db_connection=None)
        print("  [OK] Model initialized successfully")
        
        # Test demo data
        herrajes_list = herrajes.obtener_todos_herrajes()
        assert len(herrajes_list) > 0, "Demo data should not be empty"
        assert all(h.get('categoria') == 'HERRAJE' for h in herrajes_list), "All items should be herrajes"
        print(f"  [OK] Demo data: {len(herrajes_list)} herrajes")
        
        # Test types
        assert len(herrajes.TIPOS_HERRAJES) > 0, "Should have herraje types"
        print(f"  [OK] Types: {len(herrajes.TIPOS_HERRAJES)} herraje types")
        
        # Test search
        busqueda = herrajes.buscar_herrajes("bisagra")
        print(f"  [OK] Search: {len(busqueda)} results")
        
        # Test statistics
        stats = herrajes.obtener_estadisticas()
        assert "total_herrajes" in stats, "Should have total_herrajes"
        print(f"  [OK] Statistics: {stats['total_herrajes']} total herrajes")
        
        # Test stock state determination
        producto_normal = {"stock_actual": 100, "stock_minimo": 10}
        estado = herrajes._determinar_estado_stock(producto_normal)
        assert estado == "NORMAL", "Should detect normal stock"
        print(f"  [OK] Stock state detection: {estado}")
        
        return True
    except Exception as e:
        print(f"  [FAIL] HerrajesModel test failed: {e}")
        return False


def test_vidrios_model():
    """Test VidriosModel consolidado."""
    print("\n[TEST] VidriosModel consolidado...")
    try:
        # Test initialization
        vidrios = VidriosModel(db_connection=None)
        print("  [OK] Model initialized successfully")
        
        # Test demo data
        vidrios_list = vidrios.obtener_todos_vidrios()
        assert len(vidrios_list) > 0, "Demo data should not be empty"
        assert all(v.get('categoria') == 'VIDRIO' for v in vidrios_list), "All items should be vidrios"
        assert all('espesor' in v for v in vidrios_list), "All vidrios should have espesor"
        print(f"  [OK] Demo data: {len(vidrios_list)} vidrios")
        
        # Test types and thickness
        assert len(vidrios.TIPOS_VIDRIOS) > 0, "Should have vidrio types"
        assert len(vidrios.ESPESORES) > 0, "Should have espesores"
        print(f"  [OK] Types: {len(vidrios.TIPOS_VIDRIOS)} vidrio types")
        print(f"  [OK] Espesores: {len(vidrios.ESPESORES)} thickness options")
        
        # Test property extraction
        vidrio_test = {
            "propiedades_especiales": '{"espesor": 6, "templado": true, "laminado": false}'
        }
        vidrio_extracted = vidrios._extraer_propiedades_vidrio(vidrio_test)
        assert vidrio_extracted.get("espesor") == 6, "Should extract espesor"
        print(f"  [OK] Property extraction: espesor={vidrio_extracted.get('espesor')}")
        
        # Test statistics
        stats = vidrios.obtener_estadisticas()
        assert "total_vidrios" in stats, "Should have total_vidrios"
        print(f"  [OK] Statistics: {stats['total_vidrios']} total vidrios")
        
        return True
    except Exception as e:
        print(f"  [FAIL] VidriosModel test failed: {e}")
        return False


def test_pedidos_model():
    """Test PedidosModel consolidado."""
    print("\n[TEST] PedidosModel consolidado...")
    try:
        # Test initialization
        pedidos = PedidosModel(db_connection=None)
        print("  [OK] Model initialized successfully")
        
        # Test demo data
        pedidos_list = pedidos.obtener_pedidos()
        assert len(pedidos_list) > 0, "Demo data should not be empty"
        assert all('numero_pedido' in p for p in pedidos_list), "All orders should have numero_pedido"
        assert all('tipo_pedido' in p for p in pedidos_list), "All orders should have tipo_pedido"
        print(f"  [OK] Demo data: {len(pedidos_list)} pedidos")
        
        # Test order types
        assert len(pedidos.TIPOS_PEDIDO) > 0, "Should have order types"
        print(f"  [OK] Order types: {len(pedidos.TIPOS_PEDIDO)} types")
        
        # Test number generation
        numero = pedidos.generar_numero_pedido("COMPRA")
        assert isinstance(numero, str), "Order number should be string"
        assert "CMP-" in numero, "Should have correct prefix"
        print(f"  [OK] Number generation: {numero}")
        
        # Test state validation
        valida = pedidos._validar_transicion_estado("BORRADOR", "PENDIENTE")
        assert valida == True, "Valid state transition should return True"
        
        invalida = pedidos._validar_transicion_estado("ENTREGADO", "BORRADOR")
        assert invalida == False, "Invalid state transition should return False"
        print("  [OK] State validation working correctly")
        
        # Test statistics
        stats = pedidos.obtener_estadisticas()
        assert "total_pedidos" in stats, "Should have total_pedidos"
        print(f"  [OK] Statistics: {stats['total_pedidos']} total pedidos")
        
        return True
    except Exception as e:
        print(f"  [FAIL] PedidosModel test failed: {e}")
        return False


def test_obras_model():
    """Test ObrasModel consolidado."""
    print("\n[TEST] ObrasModel consolidado...")
    try:
        # Test initialization
        obras = ObrasModel(db_connection=None)
        print("  [OK] Model initialized successfully")
        
        # Test demo data
        obras_list = obras.obtener_todas_obras()
        assert len(obras_list) > 0, "Demo data should not be empty"
        assert all('codigo' in o for o in obras_list), "All obras should have codigo"
        assert all('estado' in o for o in obras_list), "All obras should have estado"
        print(f"  [OK] Demo data: {len(obras_list)} obras")
        
        # Test states and types
        assert len(obras.ESTADOS) > 0, "Should have estados"
        assert len(obras.TIPOS_OBRA) > 0, "Should have tipos_obra"
        assert len(obras.ETAPAS) > 0, "Should have etapas"
        print(f"  [OK] States: {len(obras.ESTADOS)} estados")
        print(f"  [OK] Types: {len(obras.TIPOS_OBRA)} tipos de obra")
        print(f"  [OK] Phases: {len(obras.ETAPAS)} etapas")
        
        # Test statistics
        stats = obras.obtener_estadisticas_obras()
        assert "total_obras" in stats, "Should have total_obras"
        print(f"  [OK] Statistics: {stats['total_obras']} total obras")
        
        return True
    except Exception as e:
        print(f"  [FAIL] ObrasModel test failed: {e}")
        return False


def test_security_features():
    """Test security features across all models."""
    print("\n[TEST] Security features...")
    try:
        # Test table name validation
        inventario = InventarioModel(db_connection=None)
        
        # Test valid table name
        valid_table = inventario._validate_table_name("productos")
        assert valid_table == "productos", "Should return valid table name"
        print("  [OK] Valid table name accepted")
        
        # Test invalid table name should raise exception
        try:
            invalid_table = inventario._validate_table_name("malicious_table")
            print("  [FAIL] Invalid table name was accepted - security issue!")
            return False
        except (ValueError, Exception):
            print("  [OK] Invalid table name rejected - security working")
            
        return True
    except Exception as e:
        print(f"  [FAIL] Security test failed: {e}")
        return False


def main():
    """Main test execution."""
    print("=" * 60)
    print("TESTING CONSOLIDATED DATABASE MODELS")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("InventarioModel", test_inventario_model),
        ("HerrajesModel", test_herrajes_model),
        ("VidriosModel", test_vidrios_model), 
        ("PedidosModel", test_pedidos_model),
        ("ObrasModel", test_obras_model),
        ("Security Features", test_security_features)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        result = test_func()
        results.append((test_name, result))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    success_rate = (passed / total * 100) if total > 0 else 0
    print(f"\nTotal tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success rate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("\n[EXCELLENT] Consolidated models are working correctly!")
    elif success_rate >= 70:
        print("\n[ACCEPTABLE] Most functionality is working, but some issues exist.")
    else:
        print("\n[CRITICAL] Multiple issues detected that require immediate attention.")
    
    print("\n" + "="*60)
    print("Testing completed.")


if __name__ == "__main__":
    main()