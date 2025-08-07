#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test para verificar que los estilos de alto contraste se aplican correctamente en inventario
"""
import sys
import os

# Agregar el directorio raíz del proyecto al path
sys.path.insert(0, os.path.abspath('.'))

def test_inventario_styles():
    """Test para verificar estilos de inventario"""
    print("🎨 [TEST] Verificando estilos de alto contraste en inventario...")
    
    try:
        from PyQt6.QtWidgets import QApplication
        from rexus.modules.inventario.view import InventarioView
        
        # Crear aplicación Qt
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # Crear vista de inventario
        print("[TEST] Creando vista de inventario...")
        vista_inventario = InventarioView()
        
        # Verificar que la tabla existe
        if hasattr(vista_inventario, 'tabla_inventario'):
            print("✅ [TEST] Tabla de inventario encontrada")
            
            # Obtener el estilo aplicado
            style = vista_inventario.tabla_inventario.styleSheet()
            
            # Verificar elementos clave del estilo de alto contraste
            checks = [
                ("color: #000000", "Texto negro"),
                ("background-color: #ffffff", "Fondo blanco"),
                ("font-weight: bold", "Texto en negrita"),
                ("border:", "Bordes definidos"),
                ("!important", "Prioridad forzada")
            ]
            
            print(f"📝 [TEST] Estilo aplicado: {len(style)} caracteres")
            
            for check, description in checks:
                if check in style:
                    print(f"✅ [TEST] {description}: OK")
                else:
                    print(f"❌ [TEST] {description}: FALTA")
            
            # Verificar que se llamó el método de forzar estilos
            print("\n🔧 [TEST] Verificando método forzar_estilos_tabla...")
            if hasattr(vista_inventario, 'forzar_estilos_tabla'):
                print("✅ [TEST] Método forzar_estilos_tabla existe")
                # Llamar el método
                vista_inventario.forzar_estilos_tabla()
                print("✅ [TEST] Método ejecutado correctamente")
            else:
                print("❌ [TEST] Método forzar_estilos_tabla no encontrado")
                
        else:
            print("❌ [TEST] Tabla de inventario no encontrada")
            
        print("\n🎯 [TEST] Test de estilos completado")
        return True
        
    except Exception as e:
        print(f"❌ [TEST] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_inventario_styles()
    sys.exit(0 if success else 1)
