#!/usr/bin/env python3
"""
Test Completo del Módulo Inventario - Rexus.app
Prueba todas las funcionalidades, botones, formularios y pestañas
"""

import sys
import os
import traceback
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import QTimer

def test_inventario_completo():
    """Prueba completa del módulo inventario."""
    print("="*60)
    print("TEST COMPLETO MÓDULO INVENTARIO")
    print("="*60)
    
    errores = []
    warnings = []
    
    try:
        # 1. Test de imports
        print("\n1. TESTING IMPORTS...")
        from rexus.modules.inventario.model import InventarioModel
        from rexus.modules.inventario.view import InventarioView
        from rexus.modules.inventario.controller import InventarioController
        from rexus.modules.inventario.submodules.consultas_manager import ConsultasManager
        print("   ✓ Todos los imports OK")
        
        # 2. Test de modelo
        print("\n2. TESTING MODELO...")
        modelo = InventarioModel()
        print("   ✓ InventarioModel instanciado")
        
        # Verificar ConsultasManager
        if hasattr(modelo, 'consultas_manager'):
            cm = modelo.consultas_manager
            if hasattr(cm, 'obtener_productos_paginados_inicial'):
                print("   ✓ obtener_productos_paginados_inicial: EXISTE")
            else:
                errores.append("obtener_productos_paginados_inicial: NO EXISTE")
        else:
            errores.append("InventarioModel no tiene consultas_manager")
        
        # 3. Test de vista (con QApplication)
        print("\n3. TESTING VISTA...")
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        vista = InventarioView()
        print("   ✓ InventarioView instanciada")
        
        # Verificar pestañas principales
        if hasattr(vista, 'tab_widget'):
            print("   ✓ tab_widget: EXISTE")
            print(f"   ✓ Número de pestañas: {vista.tab_widget.count()}")
            
            # Verificar nombres de pestañas
            for i in range(vista.tab_widget.count()):
                tab_text = vista.tab_widget.tabText(i)
                print(f"     - Pestaña {i}: {tab_text}")
        else:
            errores.append("tab_widget NO EXISTE")
        
        # Verificar pestaña de obras
        if hasattr(vista, 'tab_obras'):
            print("   ✓ tab_obras: EXISTE")
        else:
            errores.append("tab_obras NO EXISTE")
        
        if hasattr(vista, 'tab_inventario_general'):
            print("   ✓ tab_inventario_general: EXISTE")
        else:
            errores.append("tab_inventario_general NO EXISTE")
        
        # 4. Test de botones específicos de obras
        print("\n4. TESTING BOTONES DE OBRAS...")
        botones_obras = [
            'btn_cargar_obras',
            'btn_separar_material'
        ]
        
        for boton in botones_obras:
            if hasattr(vista, boton):
                print(f"   ✓ {boton}: EXISTE")
                # Verificar que el botón tiene texto
                btn_obj = getattr(vista, boton)
                if hasattr(btn_obj, 'text'):
                    texto = btn_obj.text()
                    print(f"     Texto: '{texto}'")
                    if not texto.strip():
                        warnings.append(f"{boton} no tiene texto")
            else:
                errores.append(f"{boton}: NO EXISTE")
        
        # 5. Test de componentes de obras
        print("\n5. TESTING COMPONENTES DE OBRAS...")
        componentes_obras = [
            'combo_obras',
            'tabla_productos_disponibles',
            'tab_widget_obras'
        ]
        
        for componente in componentes_obras:
            if hasattr(vista, componente):
                print(f"   ✓ {componente}: EXISTE")
                # Verificar configuración básica
                obj = getattr(vista, componente)
                if hasattr(obj, 'columnCount') and hasattr(obj, 'rowCount'):
                    print(f"     Tabla con {obj.columnCount()} columnas")
                elif hasattr(obj, 'count'):
                    print(f"     Widget con {obj.count()} items")
            else:
                errores.append(f"{componente}: NO EXISTE")
        
        # 6. Test de métodos de funcionalidad
        print("\n6. TESTING MÉTODOS DE FUNCIONALIDAD...")
        metodos_obras = [
            'crear_tab_obras',
            'crear_tab_inventario_general',
            'agregar_obra_tab',
            'cargar_obras_disponibles',
            'cargar_materiales_obra',
            'configurar_tabla_productos_disponibles',
            'configurar_tabla_materiales_obra'
        ]
        
        for metodo in metodos_obras:
            if hasattr(vista, metodo):
                print(f"   ✓ {metodo}: EXISTE")
            else:
                errores.append(f"{metodo}: NO EXISTE")
        
        # 7. Test de controlador
        print("\n7. TESTING CONTROLADOR...")
        controlador = InventarioController()
        print("   ✓ InventarioController instanciado")
        
        # Verificar métodos críticos
        metodos_controlador = [
            'cargar_inventario_paginado',
            'conectar_senales'
        ]
        
        for metodo in metodos_controlador:
            if hasattr(controlador, metodo):
                print(f"   ✓ {metodo}: EXISTE")
            else:
                warnings.append(f"Controlador no tiene {metodo}")
        
        # 8. Test de funcionalidad integrada
        print("\n8. TESTING FUNCIONALIDAD INTEGRADA...")
        try:
            # Simular carga de obras
            obras_demo = [
                {'id': 1, 'nombre': 'Obra Demo 1'},
                {'id': 2, 'nombre': 'Obra Demo 2'}
            ]
            
            if hasattr(vista, 'cargar_obras_disponibles'):
                vista.cargar_obras_disponibles(obras_demo)
                print("   ✓ cargar_obras_disponibles: FUNCIONA")
                
                # Verificar que se crearon las pestañas
                if hasattr(vista, 'tab_widget_obras'):
                    num_tabs = vista.tab_widget_obras.count()
                    print(f"     Pestañas de obras creadas: {num_tabs}")
                    if num_tabs < 3:  # Resumen + 2 obras
                        warnings.append(f"Esperaba 3+ pestañas, encontradas: {num_tabs}")
            
            # Simular carga de materiales
            materiales_demo = [
                {
                    'codigo': 'MAT001',
                    'nombre': 'Material Demo 1',
                    'cantidad_asignada': 10,
                    'fecha_asignacion': '2025-08-18',
                    'estado': 'Asignado'
                }
            ]
            
            if hasattr(vista, 'cargar_materiales_obra'):
                vista.cargar_materiales_obra(1, materiales_demo)
                print("   ✓ cargar_materiales_obra: FUNCIONA")
            
        except Exception as e:
            errores.append(f"Error en funcionalidad integrada: {e}")
        
        # 9. Test visual (mostrar la vista)
        print("\n9. TESTING VISUAL...")
        try:
            vista.show()
            print("   ✓ Vista se muestra correctamente")
            
            # Configurar timer para cerrar automáticamente
            QTimer.singleShot(3000, vista.close)  # Cerrar después de 3 segundos
            
            # Ejecutar brevemente para ver si hay errores de UI
            QTimer.singleShot(100, app.quit)
            app.exec()
            
            print("   ✓ Vista ejecutada sin errores críticos")
            
        except Exception as e:
            errores.append(f"Error en test visual: {e}")
    
    except Exception as e:
        errores.append(f"Error general: {e}")
        traceback.print_exc()
    
    # Resumen final
    print("\n" + "="*60)
    print("RESUMEN DEL TEST")
    print("="*60)
    
    if errores:
        print(f"\n❌ ERRORES ENCONTRADOS ({len(errores)}):")
        for i, error in enumerate(errores, 1):
            print(f"   {i}. {error}")
    
    if warnings:
        print(f"\n⚠️  ADVERTENCIAS ({len(warnings)}):")
        for i, warning in enumerate(warnings, 1):
            print(f"   {i}. {warning}")
    
    if not errores and not warnings:
        print("\n✅ TODAS LAS FUNCIONALIDADES FUNCIONAN CORRECTAMENTE")
    elif not errores:
        print(f"\n✅ FUNCIONALIDADES BÁSICAS OK (Solo {len(warnings)} advertencias)")
    else:
        print(f"\n❌ MÓDULO TIENE {len(errores)} ERRORES CRÍTICOS")
    
    # Estadísticas
    print(f"\nESTADÍSTICAS:")
    print(f"   • Errores críticos: {len(errores)}")
    print(f"   • Advertencias: {len(warnings)}")
    print(f"   • Estado general: {'✅ FUNCIONAL' if len(errores) == 0 else '❌ REQUIERE CORRECCIÓN'}")
    
    return errores, warnings

if __name__ == "__main__":
    try:
        errores, warnings = test_inventario_completo()
        
        # Guardar resultados
        with open("test_inventario_results.txt", "w", encoding="utf-8") as f:
            f.write("RESULTADOS TEST INVENTARIO COMPLETO\n")
            f.write("="*50 + "\n\n")
            
            if errores:
                f.write("ERRORES:\n")
                for i, error in enumerate(errores, 1):
                    f.write(f"{i}. {error}\n")
                f.write("\n")
            
            if warnings:
                f.write("ADVERTENCIAS:\n")
                for i, warning in enumerate(warnings, 1):
                    f.write(f"{i}. {warning}\n")
                f.write("\n")
            
            if not errores and not warnings:
                f.write("✅ TODAS LAS FUNCIONALIDADES OK\n")
        
        print(f"\n💾 Resultados guardados en: test_inventario_results.txt")
        
        # Código de salida
        sys.exit(len(errores))
        
    except Exception as e:
        print(f"❌ ERROR EJECUTANDO TEST: {e}")
        traceback.print_exc()
        sys.exit(1)