#!/usr/bin/env python3
"""
TEST SIMPLE PARA VALIDADOR EXTENDIDO
===================================
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from rexus.modules.obras.validator_extended import ObrasValidatorExtended
    print("✅ Validador importado correctamente")
except Exception as e:
    print(f"❌ Error al importar validador: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


def test_validador_obra_completa():
    """Test básico del validador extendido."""
    
    # Datos válidos
    obra_valida = {
        'codigo': 'OBR-001',
        'nombre': 'Obra de Prueba',
        'cliente': 'Cliente Prueba',
        'responsable': 'Responsable Prueba',
        'fecha_inicio': '2024-01-01',
        'fecha_fin_estimada': '2024-12-31',
        'estado': 'EN_PROCESO',
        'presupuesto_inicial': 100000.0
    }
    
    es_valida, errores = ObrasValidatorExtended.validar_obra_completa(obra_valida)
    
    print(f"Obra válida: {es_valida}")
    print(f"Errores: {errores}")
    
    # Datos inválidos - XSS
    obra_xss = {
        'codigo': 'OBR-002',
        'nombre': '<script>alert("XSS")</script>Obra Maliciosa',
        'cliente': 'Cliente Normal',
        'responsable': 'Responsable Normal',
        'fecha_inicio': '2024-01-01',
        'fecha_fin_estimada': '2024-12-31',
        'estado': 'EN_PROCESO',
        'presupuesto_inicial': 100000.0
    }
    
    es_valida_xss, errores_xss = ObrasValidatorExtended.validar_obra_completa(obra_xss)
    
    print(f"\nObra con XSS válida: {es_valida_xss}")
    print(f"Errores XSS: {errores_xss}")
    
    # Test sanitización
    texto_sucio = '<script>alert("test")</script>Texto normal'
    texto_limpio = ObrasValidatorExtended.sanitizar_texto(texto_sucio)
    
    print(f"\nTexto original: {texto_sucio}")
    print(f"Texto sanitizado: {texto_limpio}")
    
    return True


if __name__ == "__main__":
    test_validador_obra_completa()
    print("\n✅ Test del validador extendido completado")
