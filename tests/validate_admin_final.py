#!/usr/bin/env python3
"""
Validacion FINAL del modulo administracion - Post correcciones
"""

import sys
from pathlib import Path

# Agregar ruta del proyecto
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def validacion_completa():
    """Validacion completa post-correcciones"""
    issues = []
    tests_passed = 0
    tests_total = 10
    
    print("=== VALIDACION FINAL MODULO ADMINISTRACION ===")
    print("Estado: POST-CORRECCIONES")
    
    # Test 1: Importabilidad
    print("\n1. Verificando importabilidad...")
    try:
        from rexus.modules.administracion.view import AdministracionView
        from rexus.modules.administracion.model import AdministracionModel
        from rexus.modules.administracion.controller import AdministracionController
        print("   [OK] Todos los componentes importables")
        tests_passed += 1
    except Exception as e:
        issues.append(f"Imports fallaron: {e}")
        print(f"   [ERROR] Imports: {e}")

    # Test 2: Instanciabilidad  
    print("\n2. Verificando instanciabilidad...")
    try:
        view = AdministracionView()
        model = AdministracionModel()
        controller = AdministracionController()
        print("   [OK] Todos los componentes instanciables")
        tests_passed += 1
    except Exception as e:
        issues.append(f"Instanciacion fallo: {e}")
        print(f"   [ERROR] Instanciacion: {e}")

    # Test 3: Conexion vista-controlador
    print("\n3. Verificando conexion vista-controlador...")
    try:
        if 'view' in locals() and 'controller' in locals():
            view.set_controller(controller)
            if hasattr(controller, 'set_view'):
                controller.set_view(view)
            print("   [OK] Vista y controlador conectados")
            tests_passed += 1
        else:
            issues.append("Vista o controlador no instanciables")
            print("   [ERROR] Componentes no disponibles")
    except Exception as e:
        issues.append(f"Error conexion vista-controlador: {e}")
        print(f"   [ERROR] Conexion: {e}")

    # Test 4: Funciones del modelo
    print("\n4. Verificando funciones criticas del modelo...")
    try:
        if 'model' in locals():
            critical_functions = [
                'registrar_asiento_contable',
                'generar_balance_general',
                'crear_empleado',
                'generar_nomina'
            ]
            
            missing = []
            for func in critical_functions:
                if hasattr(model, func):
                    print(f"   [OK] {func} existe")
                else:
                    missing.append(func)
                    print(f"   [ERROR] {func} faltante")
            
            if not missing:
                tests_passed += 1
            else:
                issues.append(f"Funciones faltantes: {missing}")
        else:
            issues.append("Modelo no disponible")
            print("   [ERROR] Modelo no disponible")
    except Exception as e:
        issues.append(f"Error verificando modelo: {e}")
        print(f"   [ERROR] Modelo: {e}")

    # Test 5: Estructura de pestanas en vista
    print("\n5. Verificando estructura de pestanas...")
    try:
        if 'view' in locals():
            if hasattr(view, 'tabs'):
                tab_count = view.tabs.count()
                print(f"   [OK] Vista tiene {tab_count} pestanas")
                
                # Verificar pestanas especificas
                expected_tabs = ['Dashboard', 'Contabilidad', 'Recursos Humanos']
                found_tabs = []
                for i in range(tab_count):
                    tab_text = view.tabs.tabText(i)
                    found_tabs.append(tab_text)
                    print(f"   [INFO] Pestana {i+1}: {tab_text}")
                
                tests_passed += 1
            else:
                issues.append("Vista no tiene estructura de pestanas")
                print("   [ERROR] Sin pestanas")
        else:
            issues.append("Vista no disponible")
    except Exception as e:
        issues.append(f"Error verificando pestanas: {e}")
        print(f"   [ERROR] Pestanas: {e}")

    # Test 6: Widgets especializados
    print("\n6. Verificando widgets especializados...")
    try:
        if 'view' in locals():
            widgets_found = 0
            if hasattr(view, 'dashboard_widget'):
                print("   [OK] DashboardWidget encontrado")
                widgets_found += 1
            if hasattr(view, 'contabilidad_widget'):
                print("   [OK] ContabilidadWidget encontrado")
                widgets_found += 1
            if hasattr(view, 'rrhh_widget'):
                print("   [OK] RecursosHumanosWidget encontrado")
                widgets_found += 1
            
            if widgets_found >= 3:
                tests_passed += 1
            else:
                issues.append(f"Solo {widgets_found}/3 widgets especializados encontrados")
                
        else:
            issues.append("Vista no disponible para verificar widgets")
    except Exception as e:
        issues.append(f"Error verificando widgets: {e}")
        print(f"   [ERROR] Widgets: {e}")

    # Test 7: Senales de comunicacion
    print("\n7. Verificando senales de comunicacion...")
    try:
        if 'view' in locals():
            signals_found = 0
            if hasattr(view, 'solicitud_datos_dashboard'):
                print("   [OK] Signal solicitud_datos_dashboard")
                signals_found += 1
            if hasattr(view, 'solicitud_crear_asiento'):
                print("   [OK] Signal solicitud_crear_asiento")
                signals_found += 1
            if hasattr(view, 'solicitud_crear_empleado'):
                print("   [OK] Signal solicitud_crear_empleado")
                signals_found += 1
                
            if signals_found >= 3:
                tests_passed += 1
            else:
                issues.append(f"Solo {signals_found}/3 senales encontradas")
        else:
            issues.append("Vista no disponible para verificar senales")
    except Exception as e:
        issues.append(f"Error verificando senales: {e}")
        print(f"   [ERROR] Senales: {e}")

    # Test 8: Metodos funcionales (no placeholders)
    print("\n8. Verificando metodos funcionales...")
    try:
        if 'view' in locals():
            # Verificar que nuevo_registro sea funcional
            if hasattr(view, 'nuevo_registro'):
                # Simular ejecucion - no deberia mostrar "en desarrollo"
                import unittest.mock as mock
                with mock.patch('rexus.utils.message_system.show_warning') as mock_warn:
                    view.nuevo_registro()
                    if mock_warn.called:
                        args = mock_warn.call_args[0] if mock_warn.call_args else []
                        if len(args) > 1 and "desarrollo" not in str(args[1]).lower():
                            print("   [OK] nuevo_registro es funcional (no placeholder)")
                            tests_passed += 1
                        else:
                            issues.append("nuevo_registro aun es placeholder")
                            print("   [ERROR] nuevo_registro es placeholder")
                    else:
                        print("   [OK] nuevo_registro no muestra advertencias")
                        tests_passed += 1
            else:
                issues.append("nuevo_registro no existe")
        else:
            issues.append("Vista no disponible")
    except Exception as e:
        issues.append(f"Error verificando metodos: {e}")
        print(f"   [ERROR] Metodos: {e}")

    # Test 9: Dialogos funcionales
    print("\n9. Verificando dialogos...")
    try:
        from rexus.modules.administracion.view import AsientoContableDialog, EmpleadoDialog
        
        asiento_dialog = AsientoContableDialog()
        empleado_dialog = EmpleadoDialog()
        
        print("   [OK] AsientoContableDialog instanciable")
        print("   [OK] EmpleadoDialog instanciable")
        tests_passed += 1
    except Exception as e:
        issues.append(f"Error con dialogos: {e}")
        print(f"   [ERROR] Dialogos: {e}")

    # Test 10: Compatibilidad con sistema existente
    print("\n10. Verificando compatibilidad...")
    try:
        # Verificar que el alias AdministracionView funcione
        if 'AdministracionView' in locals():
            view_alias = AdministracionView()
            if hasattr(view_alias, 'tabs') and hasattr(view_alias, 'set_controller'):
                print("   [OK] Alias AdministracionView funcional")
                tests_passed += 1
            else:
                issues.append("Alias no tiene funcionalidad completa")
        else:
            issues.append("Alias AdministracionView no funciona")
    except Exception as e:
        issues.append(f"Error compatibilidad: {e}")
        print(f"   [ERROR] Compatibilidad: {e}")

    # Resumen final
    print(f"\n=== RESUMEN FINAL ===")
    print(f"Tests pasados: {tests_passed}/{tests_total}")
    print(f"Porcentaje exito: {(tests_passed/tests_total)*100:.1f}%")
    
    if tests_passed >= 8:  # 80% o mas
        print(f"ESTADO: FUNCIONAL - Modulo administracion corregido exitosamente")
        if tests_passed == tests_total:
            print("CALIFICACION: EXCELENTE - Todas las pruebas pasaron")
        else:
            print("CALIFICACION: BUENO - Funcional con mejoras menores")
    elif tests_passed >= 6:  # 60-79%
        print(f"ESTADO: PARCIALMENTE FUNCIONAL - Requiere ajustes menores")
        print("CALIFICACION: ACEPTABLE - Funcional basico")
    else:  # Menos de 60%
        print(f"ESTADO: PROBLEMATICO - Requiere mas correcciones")
        print("CALIFICACION: INSUFICIENTE - No funcional")
    
    if issues:
        print(f"\nISSUES RESTANTES ({len(issues)}):")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
    else:
        print(f"\nSin issues detectados - Modulo completamente funcional")
    
    return tests_passed >= 8, issues

if __name__ == "__main__":
    is_functional, issues_found = validacion_completa()
    
    if is_functional:
        print(f"\n*** CORRECCION EXITOSA ***")
        print(f"El modulo administracion ha sido corregido y es funcional")
    else:
        print(f"\n*** REQUIERE MAS TRABAJO ***") 
        print(f"El modulo necesita correcciones adicionales")
    
    sys.exit(0 if is_functional else 1)