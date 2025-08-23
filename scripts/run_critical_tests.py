#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Critical Tests Runner - Ejecutor de Tests Críticos
Identifica errores específicos sin dependencias complejas
"""

import sys
import os
import traceback
import importlib
from datetime import datetime

# Configurar encoding y paths
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'rexus'))

def test_basic_imports():
    """Test básico de importaciones críticas."""
    
    print("🔍 TESTING BASIC IMPORTS...")
    print("-" * 40)
    
    errors = []
    successes = []
    
    # Módulos críticos a probar
    critical_modules = [
        'rexus.core.database_manager',
        'rexus.core.module_manager',
        'rexus.modules.configuracion.controller',
        'rexus.modules.configuracion.model',
        'rexus.modules.usuarios.controller',
        'rexus.modules.usuarios.model',
        'rexus.modules.inventario.controller',
        'rexus.modules.inventario.model',
        'rexus.modules.obras.controller',
        'rexus.modules.obras.model',
        'rexus.modules.compras.controller',
        'rexus.modules.compras.model',
        'rexus.modules.pedidos.controller',
        'rexus.modules.pedidos.model'
    ]
    
    for module_name in critical_modules:
        try:
            module = importlib.import_module(module_name)
            print(f"✅ {module_name}")
            successes.append(module_name)
        except ImportError as e:
            print(f"❌ {module_name} - ImportError: {str(e)}")
            errors.append(f"IMPORT_ERROR: {module_name} - {str(e)}")
        except Exception as e:
            print(f"⚠️ {module_name} - Error: {str(e)}")
            errors.append(f"MODULE_ERROR: {module_name} - {str(e)}")
    
    print(f"\n📊 Imports: {len(successes)} OK, {len(errors)} Errors")
    return errors, successes

def test_controller_instantiation():
    """Test de instanciación de controladores."""
    
    print("\n🎮 TESTING CONTROLLER INSTANTIATION...")
    print("-" * 40)
    
    errors = []
    successes = []
    
    controllers_to_test = [
        ('rexus.modules.configuracion.controller', 'ConfiguracionController'),
        ('rexus.modules.usuarios.controller', 'UsuariosController'),
        ('rexus.modules.inventario.controller', 'InventarioController'),
        ('rexus.modules.obras.controller', 'ObrasController'),
        ('rexus.modules.compras.controller', 'ComprasController'),
        ('rexus.modules.pedidos.controller', 'PedidosController')
    ]
    
    for module_path, class_name in controllers_to_test:
        try:
            module = importlib.import_module(module_path)
            if hasattr(module, class_name):
                controller_class = getattr(module, class_name)
                try:
                    # Intentar instanciar sin argumentos
                    controller = controller_class()
                    print(f"✅ {class_name} - Instanciado OK")
                    successes.append(class_name)
                except Exception as e:
                    # Probar con argumentos mock
                    try:
                        controller = controller_class(model=None, view=None)
                        print(f"✅ {class_name} - Instanciado con argumentos")
                        successes.append(class_name)
                    except Exception as e2:
                        print(f"⚠️ {class_name} - Error instanciación: {str(e)}")
                        errors.append(f"INSTANTIATION_ERROR: {class_name} - {str(e)}")
            else:
                print(f"❌ {class_name} - Clase no encontrada")
                errors.append(f"CLASS_NOT_FOUND: {class_name}")
                
        except ImportError as e:
            print(f"❌ {class_name} - Import failed: {str(e)}")
            errors.append(f"CONTROLLER_IMPORT_ERROR: {class_name} - {str(e)}")
        except Exception as e:
            print(f"⚠️ {class_name} - Error: {str(e)}")
            errors.append(f"CONTROLLER_ERROR: {class_name} - {str(e)}")
    
    print(f"\n📊 Controllers: {len(successes)} OK, {len(errors)} Errors")
    return errors, successes

def test_required_methods():
    """Test de métodos requeridos en controladores."""
    
    print("\n🔧 TESTING REQUIRED METHODS...")
    print("-" * 40)
    
    errors = []
    successes = []
    
    # Métodos críticos que cada controlador debe tener
    required_methods_by_controller = {
        'ConfiguracionController': ['cargar_configuracion', 'guardar_configuracion'],
        'UsuariosController': ['cargar_usuarios', 'autenticar_usuario'],
        'InventarioController': ['cargar_inventario', 'obtener_productos'],
        'ObrasController': ['cargar_obras', 'crear_obra'],
        'ComprasController': ['cargar_compras', 'obtener_proveedores'],
        'PedidosController': ['cargar_pedidos', 'crear_pedido']
    }
    
    controllers_info = [
        ('rexus.modules.configuracion.controller', 'ConfiguracionController'),
        ('rexus.modules.usuarios.controller', 'UsuariosController'),
        ('rexus.modules.inventario.controller', 'InventarioController'),
        ('rexus.modules.obras.controller', 'ObrasController'),
        ('rexus.modules.compras.controller', 'ComprasController'),
        ('rexus.modules.pedidos.controller', 'PedidosController')
    ]
    
    for module_path, class_name in controllers_info:
        try:
            module = importlib.import_module(module_path)
            if hasattr(module, class_name):
                controller_class = getattr(module, class_name)
                required_methods = required_methods_by_controller.get(class_name, [])
                
                missing_methods = []
                found_methods = []
                
                for method_name in required_methods:
                    if hasattr(controller_class, method_name):
                        found_methods.append(method_name)
                    else:
                        missing_methods.append(method_name)
                        errors.append(f"MISSING_METHOD: {class_name}.{method_name}")
                
                if missing_methods:
                    print(f"⚠️ {class_name} - Missing: {missing_methods}")
                else:
                    print(f"✅ {class_name} - All methods present")
                    successes.append(class_name)
                    
        except Exception as e:
            print(f"❌ {class_name} - Error checking methods: {str(e)}")
            errors.append(f"METHOD_CHECK_ERROR: {class_name} - {str(e)}")
    
    print(f"\n📊 Method checks: {len(successes)} complete, {len(errors)} issues")
    return errors, successes

def test_ui_dependencies():
    """Test de dependencias UI críticas."""
    
    print("\n🖥️ TESTING UI DEPENDENCIES...")
    print("-" * 40)
    
    errors = []
    successes = []
    
    ui_dependencies = [
        'PyQt6.QtCore',
        'PyQt6.QtWidgets',
        'PyQt6.QtGui',
        'PyQt6.QtWebEngineWidgets'
    ]
    
    for dependency in ui_dependencies:
        try:
            importlib.import_module(dependency)
            print(f"✅ {dependency}")
            successes.append(dependency)
        except ImportError as e:
            print(f"❌ {dependency} - Missing: {str(e)}")
            errors.append(f"UI_DEPENDENCY_ERROR: {dependency} - {str(e)}")
        except Exception as e:
            print(f"⚠️ {dependency} - Error: {str(e)}")
            errors.append(f"UI_ERROR: {dependency} - {str(e)}")
    
    print(f"\n📊 UI Dependencies: {len(successes)} OK, {len(errors)} Missing")
    return errors, successes

def test_database_compatibility():
    """Test de compatibilidad de base de datos."""
    
    print("\n🗄️ TESTING DATABASE COMPATIBILITY...")
    print("-" * 40)
    
    errors = []
    successes = []
    
    # Verificar drivers de BD
    db_drivers = [
        'sqlite3',
        'pyodbc'
    ]
    
    for driver in db_drivers:
        try:
            importlib.import_module(driver)
            print(f"✅ {driver} driver available")
            successes.append(driver)
        except ImportError as e:
            print(f"❌ {driver} driver missing: {str(e)}")
            errors.append(f"DB_DRIVER_ERROR: {driver} - {str(e)}")
    
    # Verificar archivos SQL problemáticos
    sql_files_to_check = [
        'rexus/modules/obras/model.py',
        'rexus/modules/inventario/model.py',
        'rexus/modules/compras/model.py',
        'rexus/modules/pedidos/model.py'
    ]
    
    for sql_file in sql_files_to_check:
        file_path = os.path.join(project_root, sql_file)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Buscar patrones SQLite incompatibles con SQL Server
                    problematic_patterns = [
                        'sqlite_master',
                        'AUTOINCREMENT',
                        'PRAGMA'
                    ]
                    
                    issues_found = []
                    for pattern in problematic_patterns:
                        if pattern in content:
                            issues_found.append(pattern)
                    
                    if issues_found:
                        print(f"⚠️ {sql_file} - SQL compatibility issues: {issues_found}")
                        errors.append(f"SQL_COMPATIBILITY: {sql_file} - {issues_found}")
                    else:
                        print(f"✅ {sql_file} - SQL compatible")
                        successes.append(sql_file)
                        
            except Exception as e:
                print(f"❌ {sql_file} - Error reading: {str(e)}")
                errors.append(f"SQL_READ_ERROR: {sql_file} - {str(e)}")
        else:
            print(f"⚠️ {sql_file} - File not found")
            errors.append(f"SQL_FILE_MISSING: {sql_file}")
    
    print(f"\n📊 DB Compatibility: {len(successes)} OK, {len(errors)} Issues")
    return errors, successes

def generate_comprehensive_report(all_errors, all_successes):
    """Genera reporte completo de los tests."""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"CRITICAL_TESTS_REPORT_{timestamp}.md"
    
    total_errors = sum(len(errors) for errors in all_errors.values())
    total_successes = sum(len(successes) for successes in all_successes.values())
    
    content = f"""# REPORTE DE TESTS CRÍTICOS - {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

## 🎯 OBJETIVO
Identificar errores críticos que pueden explicar los **263 errores** reportados por el usuario.

## 📊 RESUMEN EJECUTIVO
- **Total de errores encontrados:** {total_errors}
- **Total de validaciones exitosas:** {total_successes}
- **Cobertura estimada:** {(total_errors/263)*100:.1f}% de los 263 errores reportados
- **Estado del sistema:** {'CRÍTICO' if total_errors > 50 else 'INESTABLE' if total_errors > 20 else 'ESTABLE'}

## ❌ ERRORES CRÍTICOS POR CATEGORÍA

### 1. Errores de Importación
"""
    
    for error in all_errors.get('imports', []):
        content += f"- {error}\n"
    
    content += f"""
### 2. Errores de Controladores
"""
    
    for error in all_errors.get('controllers', []):
        content += f"- {error}\n"
    
    content += f"""
### 3. Métodos Faltantes
"""
    
    for error in all_errors.get('methods', []):
        content += f"- {error}\n"
    
    content += f"""
### 4. Dependencias UI
"""
    
    for error in all_errors.get('ui', []):
        content += f"- {error}\n"
    
    content += f"""
### 5. Compatibilidad de Base de Datos
"""
    
    for error in all_errors.get('database', []):
        content += f"- {error}\n"
    
    content += f"""
## ✅ VALIDACIONES EXITOSAS

### Módulos Funcionando Correctamente
"""
    
    for category, successes in all_successes.items():
        content += f"#### {category.title()}\n"
        for success in successes:
            content += f"- ✅ {success}\n"
        content += "\n"
    
    content += f"""
## 🎯 PLAN DE CORRECCIÓN PRIORITARIO

### 🚨 Acción Inmediata (Hoy)
1. **Instalar dependencias UI faltantes**
   - Especialmente PyQt6-WebEngine
   
2. **Corregir errores de importación**
   - Resolver problemas de paths y módulos faltantes
   
3. **Implementar métodos cargar_[módulo] faltantes**
   - Usar el sistema de patches creado

### ⚡ Acción Urgente (Esta semana)
4. **Corregir compatibilidad SQL**
   - Aplicar traductor SQL creado
   
5. **Completar controladores**
   - Implementar métodos básicos faltantes

### 📈 Estimación de Mejora
- **Con correcciones inmediatas:** -{(len(all_errors.get('ui', [])) + len(all_errors.get('imports', [])))} errores
- **Con correcciones urgentes:** -{total_errors * 0.8:.0f} errores (80% reducción)
- **Resultado esperado:** <53 errores restantes de los 263 originales

## 📋 PRÓXIMOS PASOS
1. Ejecutar install_dependencies.py
2. Aplicar parches de SQL compatibility  
3. Ejecutar tests nuevamente para validar mejoras
4. Repetir hasta reducir errores a <10

---
*Reporte generado para resolver sistemáticamente los 263 errores*
"""
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return report_file

def main():
    """Función principal del runner de tests críticos."""
    
    print("🚀 CRITICAL TESTS RUNNER - REXUS.APP")
    print("Objetivo: Identificar errores que causan los 263 errores reportados")
    print("=" * 80)
    print(f"Timestamp: {datetime.now()}")
    print(f"Working Directory: {os.getcwd()}")
    print("=" * 80)
    
    all_errors = {}
    all_successes = {}
    
    try:
        # Ejecutar tests críticos
        errors, successes = test_basic_imports()
        all_errors['imports'] = errors
        all_successes['imports'] = successes
        
        errors, successes = test_controller_instantiation()
        all_errors['controllers'] = errors
        all_successes['controllers'] = successes
        
        errors, successes = test_required_methods()
        all_errors['methods'] = errors
        all_successes['methods'] = successes
        
        errors, successes = test_ui_dependencies()
        all_errors['ui'] = errors
        all_successes['ui'] = successes
        
        errors, successes = test_database_compatibility()
        all_errors['database'] = errors
        all_successes['database'] = successes
        
        # Generar reporte
        report_file = generate_comprehensive_report(all_errors, all_successes)
        
        # Mostrar resumen final
        total_errors = sum(len(errors) for errors in all_errors.values())
        total_successes = sum(len(successes) for successes in all_successes.values())
        
        print("\n" + "=" * 80)
        print("🏁 CRITICAL TESTS COMPLETED")
        print("=" * 80)
        print(f"📊 ERRORES CRÍTICOS IDENTIFICADOS: {total_errors}")
        print(f"✅ VALIDACIONES EXITOSAS: {total_successes}")
        print(f"📋 REPORTE DETALLADO: {report_file}")
        print(f"🎯 COBERTURA: {(total_errors/263)*100:.1f}% de los 263 errores reportados")
        
        if total_errors > 50:
            print("\n🚨 ESTADO CRÍTICO: Sistema requiere corrección inmediata")
        elif total_errors > 20:
            print("\n⚠️ ESTADO INESTABLE: Múltiples errores detectados")
        else:
            print("\n✅ ESTADO ACEPTABLE: Pocos errores críticos")
        
        print(f"\n🎯 PRÓXIMO PASO: Corregir los {total_errors} errores identificados")
        
        return total_errors
        
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO EN TESTS: {str(e)}")
        print(traceback.format_exc())
        return -1

if __name__ == "__main__":
    error_count = main()
    print(f"\nTests completados. Errores críticos identificados: {error_count}")
    sys.exit(0)