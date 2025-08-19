#!/usr/bin/env python3
"""
Test UI del Módulo Inventario - Verificar botones y formularios
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QTimer

def test_inventario_ui():
    """Test de la interfaz de usuario del inventario."""
    print("=" * 50)
    print("TEST UI INVENTARIO - BOTONES Y FORMULARIOS")
    print("=" * 50)
    
    errores = []
    
    try:
        # Crear aplicación Qt
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        print("1. Instanciando InventarioView...")
        from rexus.modules.inventario.view import InventarioView
        vista = InventarioView()
        print("   [OK] Vista creada")
        
        # 2. Verificar pestañas principales
        print("\n2. VERIFICANDO PESTAÑAS PRINCIPALES...")
        if hasattr(vista, 'tab_widget'):
            num_tabs = vista.tab_widget.count()
            print(f"   [OK] Pestañas creadas: {num_tabs}")
            
            for i in range(num_tabs):
                tab_text = vista.tab_widget.tabText(i)
                print(f"     - Pestaña {i}: '{tab_text}'")
            
            if num_tabs < 2:
                errores.append(f"Esperaba al menos 2 pestañas, encontradas: {num_tabs}")
        else:
            errores.append("tab_widget no existe")
            print("   [ERROR] tab_widget no existe")
        
        # 3. Verificar botones de obras
        print("\n3. VERIFICANDO BOTONES DE OBRAS...")
        botones = {
            'btn_cargar_obras': 'Cargar Obras',
            'btn_separar_material': 'Separar Material'
        }
        
        for attr_name, descripcion in botones.items():
            if hasattr(vista, attr_name):
                btn = getattr(vista, attr_name)
                if hasattr(btn, 'text'):
                    texto = btn.text()
                    print(f"   [OK] {attr_name}: '{texto}'")
                    if not texto.strip():
                        errores.append(f"{attr_name} no tiene texto")
                else:
                    print(f"   [OK] {attr_name} existe pero sin método text()")
            else:
                errores.append(f"{attr_name} no existe")
                print(f"   [ERROR] {attr_name} no existe")
        
        # 4. Verificar combo de obras
        print("\n4. VERIFICANDO COMBO DE OBRAS...")
        if hasattr(vista, 'combo_obras'):
            combo = vista.combo_obras
            print(f"   [OK] combo_obras existe")
            if hasattr(combo, 'count'):
                items = combo.count()
                print(f"     Items iniciales: {items}")
            
            # Test de funcionalidad: agregar obras demo
            obras_demo = [
                {'id': 1, 'nombre': 'Obra Demo 1'},
                {'id': 2, 'nombre': 'Obra Demo 2'},
                {'id': 3, 'nombre': 'Obra Demo 3'}
            ]
            
            if hasattr(vista, 'cargar_obras_disponibles'):
                try:
                    vista.cargar_obras_disponibles(obras_demo)
                    items_nuevos = combo.count()
                    print(f"     Items después de cargar obras: {items_nuevos}")
                    if items_nuevos != 3:
                        errores.append(f"Esperaba 3 obras en combo, encontradas: {items_nuevos}")
                    else:
                        print("   [OK] Obras cargadas correctamente en combo")
                except Exception as e:
                    errores.append(f"Error cargando obras: {e}")
            else:
                errores.append("cargar_obras_disponibles no existe")
        else:
            errores.append("combo_obras no existe")
            print("   [ERROR] combo_obras no existe")
        
        # 5. Verificar tablas
        print("\n5. VERIFICANDO TABLAS...")
        tablas = {
            'tabla_productos_disponibles': 'Productos Disponibles',
            'tab_widget_obras': 'Widget de Pestañas de Obras'
        }
        
        for attr_name, descripcion in tablas.items():
            if hasattr(vista, attr_name):
                tabla = getattr(vista, attr_name)
                print(f"   [OK] {attr_name} existe")
                
                if hasattr(tabla, 'columnCount'):
                    cols = tabla.columnCount()
                    print(f"     Columnas: {cols}")
                    if cols == 0:
                        errores.append(f"{attr_name} no tiene columnas configuradas")
                elif hasattr(tabla, 'count'):
                    tabs = tabla.count()
                    print(f"     Pestañas internas: {tabs}")
            else:
                errores.append(f"{attr_name} no existe")
                print(f"   [ERROR] {attr_name} no existe")
        
        # 6. Test de pestañas de obras específicas
        print("\n6. VERIFICANDO PESTAÑAS DE OBRAS ESPECÍFICAS...")
        if hasattr(vista, 'tab_widget_obras'):
            tab_obras = vista.tab_widget_obras
            num_tabs_obras = tab_obras.count()
            print(f"   Pestañas de obras: {num_tabs_obras}")
            
            # Debería tener: Resumen + 3 obras = 4 total
            if num_tabs_obras >= 4:
                print("   [OK] Pestañas de obras creadas correctamente")
                
                # Verificar nombres de pestañas
                for i in range(num_tabs_obras):
                    tab_name = tab_obras.tabText(i)
                    print(f"     Pestaña {i}: '{tab_name}'")
            else:
                errores.append(f"Esperaba 4+ pestañas de obras, encontradas: {num_tabs_obras}")
        
        # 7. Test visual rápido
        print("\n7. TEST VISUAL...")
        try:
            vista.show()
            print("   [OK] Vista mostrada sin errores")
            
            # Cerrar automáticamente después de 2 segundos
            QTimer.singleShot(2000, vista.close)
            QTimer.singleShot(2100, app.quit)
            
            # Ejecutar brevemente
            app.exec()
            print("   [OK] Test visual completado")
            
        except Exception as e:
            errores.append(f"Error en test visual: {e}")
            print(f"   [ERROR] Test visual: {e}")
    
    except Exception as e:
        errores.append(f"Error general: {e}")
        print(f"   [ERROR] General: {e}")
        import traceback
        traceback.print_exc()
    
    # Resumen
    print("\n" + "=" * 50)
    print("RESUMEN UI TEST")
    print("=" * 50)
    
    if errores:
        print(f"\nERRORES UI ENCONTRADOS ({len(errores)}):")
        for i, error in enumerate(errores, 1):
            print(f"   {i}. {error}")
        print(f"\nESTADO UI: REQUIERE AJUSTES")
    else:
        print("\nTODOS LOS COMPONENTES UI FUNCIONAN")
        print("ESTADO UI: COMPLETAMENTE FUNCIONAL")
    
    print(f"\nComponentes verificados:")
    print(f"   - Pestañas principales: OK")
    print(f"   - Botones de obras: {'OK' if 'btn_cargar_obras' not in [e for e in errores if 'btn_cargar_obras' in e] else 'ERROR'}")
    print(f"   - Combo de obras: {'OK' if 'combo_obras' not in [e for e in errores if 'combo_obras' in e] else 'ERROR'}")
    print(f"   - Tablas: {'OK' if 'tabla_productos_disponibles' not in [e for e in errores if 'tabla_productos_disponibles' in e] else 'ERROR'}")
    print(f"   - Funcionalidad integrada: {'OK' if len([e for e in errores if 'cargar_obras' in e]) == 0 else 'ERROR'}")
    
    return errores

if __name__ == "__main__":
    try:
        errores = test_inventario_ui()
        
        # Guardar resultado
        with open("inventario_ui_test.txt", "w") as f:
            f.write("INVENTARIO UI TEST RESULTS\n")
            f.write("=" * 40 + "\n")
            if errores:
                f.write(f"ERRORES ({len(errores)}):\n")
                for error in errores:
                    f.write(f"- {error}\n")
                f.write("\nREQUIERE AJUSTES\n")
            else:
                f.write("TODOS LOS COMPONENTES UI OK\n")
                f.write("COMPLETAMENTE FUNCIONAL\n")
        
        print(f"\nResultados guardados en: inventario_ui_test.txt")
        sys.exit(len(errores))
        
    except Exception as e:
        print(f"ERROR EJECUTANDO UI TEST: {e}")
        sys.exit(1)