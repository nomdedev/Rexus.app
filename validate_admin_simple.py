#!/usr/bin/env python3
"""
Validacion simple del modulo administracion
"""

import sys
from pathlib import Path

# Agregar ruta del proyecto
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def simple_validation():
    """Validacion simple sin pytest"""
    issues = []
    
    print("=== VALIDACION MODULO ADMINISTRACION ===")
    
    # 1. Verificar importabilidad
    print("1. Verificando importabilidad...")
    try:
        from rexus.modules.administracion.view import AdministracionView
        print("   [OK] Vista importable")
    except Exception as e:
        issues.append(f"Vista no importable: {e}")
        print(f"   [ERROR] Vista no importable: {e}")
    
    try:
        from rexus.modules.administracion.model import AdministracionModel
        print("   [OK] Modelo importable")
    except Exception as e:
        issues.append(f"Modelo no importable: {e}")
        print(f"   [ERROR] Modelo no importable: {e}")
    
    try:
        from rexus.modules.administracion.controller import AdministracionController
        print("   [OK] Controlador importable")
    except Exception as e:
        issues.append(f"Controlador no importable: {e}")
        print(f"   [ERROR] Controlador no importable: {e}")
    
    # 2. Verificar instanciabilidad
    print("\n2. Verificando instanciabilidad...")
    try:
        view = AdministracionView()
        print("   [OK] Vista instanciable")
        
        # Verificar funciones basicas
        if hasattr(view, 'nuevo_registro'):
            print("   [OK] Funcion nuevo_registro existe")
            
            # Simular ejecucion para ver si es placeholder
            try:
                import unittest.mock as mock
                with mock.patch('rexus.utils.message_system.show_warning') as mock_warn:
                    view.nuevo_registro()
                    if mock_warn.called:
                        args = mock_warn.call_args
                        if args and len(args[0]) > 1 and "desarrollo" in str(args[0][1]).lower():
                            issues.append("nuevo_registro es funcion placeholder")
                            print("   [ERROR] nuevo_registro es placeholder ('en desarrollo')")
                        else:
                            print("   [OK] nuevo_registro ejecuta funcion real")
                    else:
                        print("   [OK] nuevo_registro no muestra warning")
            except Exception as e:
                issues.append(f"Error verificando nuevo_registro: {e}")
                print(f"   [ERROR] Error verificando nuevo_registro: {e}")
        else:
            issues.append("Funcion nuevo_registro no existe")
            print("   [ERROR] Funcion nuevo_registro no existe")
            
    except Exception as e:
        issues.append(f"Vista no instanciable: {e}")
        print(f"   [ERROR] Vista no instanciable: {e}")
    
    try:
        model = AdministracionModel()
        print("   [OK] Modelo instanciable")
        
        # Verificar funciones criticas del modelo
        critical_functions = [
            'registrar_asiento_contable',
            'generar_balance_general',
            'crear_empleado',
            'generar_nomina'
        ]
        
        missing_functions = []
        for func in critical_functions:
            if hasattr(model, func):
                print(f"   [OK] Funcion {func} existe")
            else:
                missing_functions.append(func)
                print(f"   [ERROR] Funcion {func} NO existe")
        
        if missing_functions:
            issues.append(f"Funciones criticas faltantes: {missing_functions}")
            
    except Exception as e:
        issues.append(f"Modelo no instanciable: {e}")
        print(f"   [ERROR] Modelo no instanciable: {e}")
    
    # 3. Verificar conexion vista-modelo
    print("\n3. Verificando conexion vista-modelo...")
    try:
        if 'view' in locals() and 'model' in locals():
            if hasattr(view, 'set_controller'):
                print("   [OK] Vista tiene metodo set_controller")
            else:
                issues.append("Vista no tiene metodo set_controller")
                print("   [ERROR] Vista no tiene metodo set_controller")
        else:
            issues.append("Vista o modelo no instanciables")
            print("   [ERROR] Vista o modelo no instanciables")
    except Exception as e:
        issues.append(f"Error verificando conexion: {e}")
        print(f"   [ERROR] Error verificando conexion: {e}")
    
    # Resumen
    print(f"\n=== RESUMEN ===")
    print(f"Issues encontrados: {len(issues)}")
    print(f"Estado funcional: {'NO' if issues else 'SI'}")
    
    if issues:
        print(f"\nPROBLEMAS DETECTADOS:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        print(f"\nRECOMENDACION: Resolver estos issues antes de usar el modulo")
    else:
        print(f"\nMODULO VALIDADO CORRECTAMENTE")
    
    return len(issues) == 0, issues

if __name__ == "__main__":
    is_functional, issues_found = simple_validation()
    sys.exit(0 if is_functional else 1)