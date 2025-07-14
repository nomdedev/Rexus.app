#!/usr/bin/env python3
"""
Test runner simple para identificar problemas.
"""

# Agregar path
sys.path.insert(0, os.path.dirname(__file__))

print("=== SIMPLE TEST RUNNER ===")

# Test 1: Imports básicos
print("\n1. Testing basic imports...")
try:
    print("  ✓ pytest")
except ImportError:
    print("  ✗ pytest not available")

try:
    print("  ✓ unittest.mock")
except ImportError:
    print("  ✗ unittest.mock not available")

try:
    print("  ✓ PyQt6.QtWidgets")
except ImportError:
    print("  ✗ PyQt6.QtWidgets not available")

# Test 2: Test pedidos controller
print("\n2. Testing pedidos controller...")
try:
    model = DummyModel()
    pedido_id = model.generar_pedido(1)
    print(f"  ✓ Pedido generated: {pedido_id}")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test 3: Test edge cases
print("\n3. Testing edge cases...")
try:
    test = TestEdgeCasesGeneral()
    test.test_strings_extremadamente_largos()
    print("  ✓ String test passed")
except Exception as e:
import os
from tests.test_edge_cases import TestEdgeCasesGeneral
from tests.test_pedidos_controller import DummyModel
import sys

    print(f"  ✗ Error: {e}")

print("\n=== TEST COMPLETE ===")
