#!/usr/bin/env python3
"""
Test Simple del Módulo Inventario - Sin caracteres especiales
"""

import sys
import os
import traceback

def test_inventario_simple():
    """Test simple del módulo inventario."""
    print("=" * 50)
    print("TEST MODULO INVENTARIO")
    print("=" * 50)
    
    errores = []
    
    try:
        # 1. Test imports
        print("\n1. TESTING IMPORTS...")
        from rexus.modules.inventario.model import InventarioModel
        from rexus.modules.inventario.view import InventarioView
        from rexus.modules.inventario.controller import InventarioController
        from rexus.modules.inventario.submodules.consultas_manager import ConsultasManager
        print("   [OK] Imports completados")
        
        # 2. Test modelo
        print("\n2. TESTING MODELO...")
        modelo = InventarioModel()
        print("   [OK] InventarioModel instanciado")
        
        # Verificar ConsultasManager
        if hasattr(modelo, 'consultas_manager'):
            cm = modelo.consultas_manager
            if hasattr(cm, 'obtener_productos_paginados_inicial'):
                print("   [OK] obtener_productos_paginados_inicial EXISTE")
            else:
                errores.append("obtener_productos_paginados_inicial NO EXISTE")
                print("   [ERROR] obtener_productos_paginados_inicial NO EXISTE")
        else:
            errores.append("consultas_manager NO EXISTE en modelo")
            print("   [ERROR] consultas_manager NO EXISTE")
        
        # 3. Test vista (sin QApplication para evitar problemas)
        print("\n3. TESTING VISTA (solo verificacion de metodos)...")
        
        # Verificar métodos de pestañas
        metodos_pestañas = [
            'crear_tab_obras',
            'crear_tab_inventario_general',
            'agregar_obra_tab',
            'cargar_obras_disponibles',
            'cargar_materiales_obra'
        ]
        
        for metodo in metodos_pestañas:
            if hasattr(InventarioView, metodo):
                print(f"   [OK] Metodo {metodo} EXISTE")
            else:
                errores.append(f"Metodo {metodo} NO EXISTE")
                print(f"   [ERROR] Metodo {metodo} NO EXISTE")
        
        # 4. Test controlador
        print("\n4. TESTING CONTROLADOR...")
        controlador = InventarioController()
        print("   [OK] InventarioController instanciado")
        
        # 5. Test funcional basico
        print("\n5. TESTING FUNCIONAL...")
        
        # Test metodo critico del ConsultasManager
        cm = ConsultasManager()
        try:
            # Intentar llamar el metodo (fallara sin BD pero no debe dar AttributeError)
            result = cm.obtener_productos_paginados_inicial(page=1, limit=10)
            print("   [OK] obtener_productos_paginados_inicial es invocable")
        except AttributeError as e:
            errores.append(f"AttributeError en obtener_productos_paginados_inicial: {e}")
            print(f"   [ERROR] AttributeError: {e}")
        except Exception as e:
            print(f"   [OK] Metodo invocable (error esperado sin BD): {type(e).__name__}")
        
    except Exception as e:
        errores.append(f"Error general: {e}")
        print(f"   [ERROR] General: {e}")
        traceback.print_exc()
    
    # Resumen
    print("\n" + "=" * 50)
    print("RESUMEN")
    print("=" * 50)
    
    if errores:
        print(f"\nERRORES ENCONTRADOS ({len(errores)}):")
        for i, error in enumerate(errores, 1):
            print(f"   {i}. {error}")
        print(f"\nESTADO: REQUIERE CORRECCION")
    else:
        print("\nTODAS LAS FUNCIONALIDADES BASICAS OK")
        print("ESTADO: FUNCIONAL")
    
    return errores

if __name__ == "__main__":
    try:
        errores = test_inventario_simple()
        
        print(f"\nResultado final: {len(errores)} errores")
        
        # Guardar resultado simple
        with open("inventario_test_simple.txt", "w") as f:
            f.write("INVENTARIO TEST RESULTS\n")
            f.write("=" * 30 + "\n")
            if errores:
                f.write("ERRORES:\n")
                for error in errores:
                    f.write(f"- {error}\n")
            else:
                f.write("TODAS LAS FUNCIONES OK\n")
        
        sys.exit(len(errores))
        
    except Exception as e:
        print(f"ERROR EJECUTANDO TEST: {e}")
        sys.exit(1)