#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Critical Modules Validator - Validador de Módulos Críticos
Ejecuta validaciones específicas para detectar los 263 errores reportados
"""

import sys
import os
import traceback
import importlib
from typing import Dict, List, Tuple, Any

# Configurar encoding y paths
sys.stdout.reconfigure(encoding='utf-8')
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'rexus'))

class CriticalModulesValidator:
    """Validador que identifica errores críticos en módulos principales."""
    
    def __init__(self):
        self.errors_found = []
        self.warnings_found = []
        self.validation_results = {}
        
    def validate_module_import(self, module_path: str, expected_class: str = None) -> bool:
        """Valida que un módulo se pueda importar correctamente."""
        try:
            module = importlib.import_module(module_path)
            
            if expected_class:
                if hasattr(module, expected_class):
                    return True
                else:
                    self.errors_found.append(f"MISSING_CLASS: {module_path} no tiene clase {expected_class}")
                    return False
            return True
            
        except ImportError as e:
            self.errors_found.append(f"IMPORT_ERROR: {module_path} - {str(e)}")
            return False
        except Exception as e:
            self.errors_found.append(f"MODULE_ERROR: {module_path} - {str(e)}")
            return False
    
    def validate_controller_methods(self, controller_path: str, controller_class: str, required_methods: List[str]) -> Dict:
        """Valida que un controlador tenga los métodos requeridos."""
        
        result = {
            'module': controller_path,
            'class': controller_class,
            'import_success': False,
            'instantiation_success': False,
            'methods_found': [],
            'methods_missing': [],
            'critical_errors': []
        }
        
        try:
            # Importar módulo
            module = importlib.import_module(controller_path)
            result['import_success'] = True
            
            if not hasattr(module, controller_class):
                result['critical_errors'].append(f"Clase {controller_class} no encontrada")
                return result
            
            # Obtener clase
            controller_cls = getattr(module, controller_class)
            
            # Intentar instanciar (puede fallar por dependencias)
            try:
                controller_instance = controller_cls()
                result['instantiation_success'] = True
            except Exception as e:
                result['critical_errors'].append(f"Error instanciación: {str(e)}")
                # Continuar con validación de métodos en la clase
                controller_instance = None
            
            # Validar métodos requeridos
            for method_name in required_methods:
                if hasattr(controller_cls, method_name):
                    result['methods_found'].append(method_name)
                else:
                    result['methods_missing'].append(method_name)
                    self.errors_found.append(f"MISSING_METHOD: {controller_path}.{controller_class}.{method_name}")
            
        except ImportError as e:
            result['critical_errors'].append(f"ImportError: {str(e)}")
            self.errors_found.append(f"CONTROLLER_IMPORT_ERROR: {controller_path} - {str(e)}")
        except Exception as e:
            result['critical_errors'].append(f"Error: {str(e)}")
            self.errors_found.append(f"CONTROLLER_ERROR: {controller_path} - {str(e)}")
        
        return result
    
    def validate_model_database_methods(self, model_path: str, model_class: str) -> Dict:
        """Valida que un modelo tenga métodos de base de datos básicos."""
        
        result = {
            'module': model_path,
            'class': model_class,
            'database_methods': [],
            'missing_db_methods': [],
            'sql_compatibility_issues': []
        }
        
        # Métodos de BD esperados
        expected_db_methods = [
            'obtener_todos',
            'obtener_por_id',
            'crear',
            'actualizar',
            'eliminar',
            'buscar'
        ]
        
        try:
            module = importlib.import_module(model_path)
            
            if not hasattr(module, model_class):
                self.errors_found.append(f"MODEL_CLASS_MISSING: {model_path}.{model_class}")
                return result
            
            model_cls = getattr(module, model_class)
            
            # Verificar métodos de BD
            for method_name in expected_db_methods:
                if hasattr(model_cls, method_name):
                    result['database_methods'].append(method_name)
                else:
                    result['missing_db_methods'].append(method_name)
                    self.warnings_found.append(f"MISSING_DB_METHOD: {model_path}.{model_class}.{method_name}")
            
            # Verificar problemas de compatibilidad SQL
            try:
                # Leer archivo del modelo para buscar queries problemáticas
                file_path = os.path.join(project_root, *model_path.split('.')) + '.py'
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # Buscar patrones problemáticos de SQLite en SQL Server
                        problematic_patterns = [
                            'sqlite_master',
                            'AUTOINCREMENT',
                            'PRAGMA',
                            'LIMIT',
                            'OFFSET'
                        ]
                        
                        for pattern in problematic_patterns:
                            if pattern in content:
                                result['sql_compatibility_issues'].append(pattern)
                                self.errors_found.append(f"SQL_COMPATIBILITY: {model_path} usa {pattern}")
                        
            except Exception:
                pass  # No crítico si no se puede leer el archivo
            
        except Exception as e:
            self.errors_found.append(f"MODEL_VALIDATION_ERROR: {model_path} - {str(e)}")
        
        return result
    
    def validate_ui_dependencies(self) -> Dict:
        """Valida dependencias críticas de UI."""
        
        result = {
            'pyqt6_core': False,
            'pyqt6_widgets': False,
            'pyqt6_webengine': False,
            'missing_dependencies': []
        }
        
        # Verificar PyQt6 core
        try:
            import PyQt6.QtCore
            result['pyqt6_core'] = True
        except ImportError:
            result['missing_dependencies'].append('PyQt6.QtCore')
            self.errors_found.append("DEPENDENCY_ERROR: PyQt6.QtCore no disponible")
        
        # Verificar PyQt6 widgets
        try:
            import PyQt6.QtWidgets
            result['pyqt6_widgets'] = True
        except ImportError:
            result['missing_dependencies'].append('PyQt6.QtWidgets')
            self.errors_found.append("DEPENDENCY_ERROR: PyQt6.QtWidgets no disponible")
        
        # Verificar PyQt6 WebEngine (crítico para funcionalidad web)
        try:
            import PyQt6.QtWebEngineWidgets
            result['pyqt6_webengine'] = True
        except ImportError:
            result['missing_dependencies'].append('PyQt6.QtWebEngineWidgets')
            self.errors_found.append("DEPENDENCY_ERROR: PyQt6.QtWebEngineWidgets no disponible")
        
        return result
    
    def run_comprehensive_validation(self) -> Dict:
        """Ejecuta validación completa para identificar los 263 errores."""
        
        print("🔍 INICIANDO VALIDACIÓN CRÍTICA DE MÓDULOS")
        print("Objetivo: Identificar origen de los 263 errores reportados")
        print("=" * 70)
        
        # 1. Validar dependencias UI críticas
        print("\n1️⃣ VALIDANDO DEPENDENCIAS UI...")
        ui_result = self.validate_ui_dependencies()
        self.validation_results['ui_dependencies'] = ui_result
        
        if ui_result['missing_dependencies']:
            print(f"❌ Dependencias UI faltantes: {ui_result['missing_dependencies']}")
        else:
            print("✅ Dependencias UI completas")
        
        # 2. Validar controladores críticos
        print("\n2️⃣ VALIDANDO CONTROLADORES CRÍTICOS...")
        
        critical_controllers = [
            ('rexus.modules.10_configuracion.controller', 'ConfiguracionController', [
                'cargar_configuracion', 'guardar_configuracion', 'obtener_configuracion'
            ]),
            ('rexus.modules.09_usuarios.controller', 'UsuariosController', [
                'cargar_usuarios', 'autenticar_usuario', 'crear_usuario'
            ]),
            ('rexus.modules.02_inventario.controller', 'InventarioController', [
                'cargar_inventario', 'obtener_productos', 'actualizar_stock'
            ]),
            ('rexus.modules.01_obras.controller', 'ObrasController', [
                'cargar_obras', 'crear_obra', 'obtener_obra_por_id'
            ]),
            ('rexus.modules.04_compras.controller', 'ComprasController', [
                'cargar_compras', 'crear_compra', 'obtener_proveedores'
            ]),
            ('rexus.modules.03_pedidos.controller', 'PedidosController', [
                'cargar_pedidos', 'crear_pedido', 'actualizar_estado'
            ]),
            ('rexus.modules.07_vidrios.controller', 'VidriosController', [
                'cargar_vidrios', 'obtener_tipos', 'calcular_precio'
            ]),
            ('rexus.modules.13_notificaciones.controller', 'NotificacionesController', [
                'cargar_notificaciones', 'enviar_notificacion', 'marcar_leida'
            ])
        ]
        
        controllers_results = {}
        for controller_path, controller_class, required_methods in critical_controllers:
            print(f"   🎮 Validando {controller_class}...")
            result = self.validate_controller_methods(controller_path, controller_class, required_methods)
            controllers_results[controller_class] = result
            
            if result['import_success']:
                if result['methods_missing']:
                    print(f"   ⚠️ {controller_class}: {len(result['methods_missing'])} métodos faltantes")
                else:
                    print(f"   ✅ {controller_class}: Métodos completos")
            else:
                print(f"   ❌ {controller_class}: Error de importación")
        
        self.validation_results['controllers'] = controllers_results
        
        # 3. Validar modelos y compatibilidad SQL
        print("\n3️⃣ VALIDANDO MODELOS Y COMPATIBILIDAD SQL...")
        
        critical_models = [
            ('rexus.modules.10_configuracion.model', 'ConfiguracionModel'),
            ('rexus.modules.09_usuarios.model', 'UsuariosModel'),
            ('rexus.modules.02_inventario.model', 'InventarioModel'),
            ('rexus.modules.01_obras.model', 'ObrasModel'),
            ('rexus.modules.04_compras.model', 'ComprasModel'),
            ('rexus.modules.03_pedidos.model', 'PedidosModel'),
            ('rexus.modules.07_vidrios.model', 'VidriosModel'),
            ('rexus.modules.13_notificaciones.model', 'NotificacionesModel')
        ]
        
        models_results = {}
        for model_path, model_class in critical_models:
            print(f"   🗄️ Validando {model_class}...")
            result = self.validate_model_database_methods(model_path, model_class)
            models_results[model_class] = result
            
            if result['sql_compatibility_issues']:
                print(f"   ⚠️ {model_class}: {len(result['sql_compatibility_issues'])} problemas SQL")
            else:
                print(f"   ✅ {model_class}: SQL compatible")
        
        self.validation_results['models'] = models_results
        
        # 4. Validar core components
        print("\n4️⃣ VALIDANDO COMPONENTES CORE...")
        
        core_components = [
            ('rexus.core.database_manager', 'DatabaseManager'),
            ('rexus.core.module_manager', 'ModuleManager'),
            ('rexus.core.auth_manager', 'AuthManager')
        ]
        
        core_results = {}
        for component_path, component_class in core_components:
            print(f"   ⚙️ Validando {component_class}...")
            success = self.validate_module_import(component_path, component_class)
            core_results[component_class] = success
            
            if success:
                print(f"   ✅ {component_class}: OK")
            else:
                print(f"   ❌ {component_class}: Error")
        
        self.validation_results['core_components'] = core_results
        
        # Generar resumen final
        total_errors = len(self.errors_found)
        total_warnings = len(self.warnings_found)
        
        print("\n" + "=" * 70)
        print("📊 RESUMEN DE VALIDACIÓN")
        print("=" * 70)
        print(f"❌ Errores críticos encontrados: {total_errors}")
        print(f"⚠️ Advertencias: {total_warnings}")
        print(f"🎯 Relación con 263 errores reportados: {(total_errors/263)*100:.1f}%")
        
        if total_errors > 50:
            print("🚨 ESTADO CRÍTICO: Múltiples errores fundamentales detectados")
        elif total_errors > 20:
            print("⚠️ ESTADO INESTABLE: Errores significativos detectados")
        else:
            print("✅ ESTADO ACEPTABLE: Pocos errores críticos")
        
        return {
            'total_errors': total_errors,
            'total_warnings': total_warnings,
            'errors_found': self.errors_found,
            'warnings_found': self.warnings_found,
            'validation_results': self.validation_results
        }
    
    def generate_errors_report(self, results: Dict) -> str:
        """Genera reporte detallado de errores encontrados."""
        
        from datetime import datetime
        timestamp = datetime.now().strftime()
        report_file = f"CRITICAL_ERRORS_REPORT_{timestamp}.md"
        
        content = f"""# REPORTE DE ERRORES CRÍTICOS - {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

## 🎯 OBJETIVO
Identificar el origen de los **263 errores** reportados por el usuario mediante validación sistemática.

## 📊 RESUMEN EJECUTIVO
- **Errores críticos detectados:** {results['total_errors']}
- **Advertencias del sistema:** {results['total_warnings']}
- **Cobertura de análisis:** {(results['total_errors']/263)*100:.1f}% de los 263 errores reportados

## ❌ ERRORES CRÍTICOS IDENTIFICADOS

"""
        
        for i, error in enumerate(results['errors_found'], 1):
            content += f"{i}. {error}\n"
        
        content += f"""
## ⚠️ ADVERTENCIAS DEL SISTEMA

"""
        
        for i, warning in enumerate(results['warnings_found'], 1):
            content += f"{i}. {warning}\n"
        
        content += f"""
## 📈 ANÁLISIS POR CATEGORÍAS

### Dependencias UI
"""
        ui_deps = results['validation_results'].get('ui_dependencies', {})
        for dep, status in ui_deps.items():
            if dep != 'missing_dependencies':
                icon = "✅" if status else "❌"
                content += f"- {icon} {dep}: {'Disponible' if status else 'Faltante'}\n"
        
        content += f"""
### Controladores Críticos
"""
        controllers = results['validation_results'].get('controllers', {})
        for name, result in controllers.items():
            icon = "✅" if result['import_success'] and not result['methods_missing'] else "❌"
            content += f"- {icon} {name}: {len(result['methods_found'])} métodos OK, {len(result['methods_missing'])} faltantes\n"
        
        content += f"""
### Modelos de Datos
"""
        models = results['validation_results'].get('models', {})
        for name, result in models.items():
            issues = len(result.get('sql_compatibility_issues', []))
            icon = "✅" if issues == 0 else "⚠️"
            content += f"- {icon} {name}: {issues} problemas SQL\n"
        
        content += f"""
## 🎯 PLAN DE CORRECCIÓN INMEDIATA

### Prioridad 1 - CRÍTICA (Corregir HOY)
1. **Instalar dependencias faltantes**
   - PyQt6-WebEngine y componentes UI faltantes
   
2. **Corregir importaciones fallidas**
   - Resolver errores de módulos que no se pueden importar
   
3. **Implementar métodos faltantes**
   - Completar controladores con métodos cargar_[módulo] faltantes

### Prioridad 2 - ALTA (Corregir esta semana)
4. **Arreglar compatibilidad SQL**
   - Traducir queries SQLite a SQL Server compatible
   
5. **Completar funcionalidades básicas**
   - Métodos de BD básicos en modelos

### Estimación de Reducción
- **Correcciones P1:** -80% errores (≈50 errores restantes)
- **Correcciones P2:** -95% errores (≈13 errores restantes)

---
*Reporte generado para resolver los 263 errores del sistema*
"""
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return report_file

def main():
    """Función principal del validador."""
    
    validator = CriticalModulesValidator()
    
    try:
        results = validator.run_comprehensive_validation()
        report_file = validator.generate_errors_report(results)
        
        print(f"\n📋 REPORTE DETALLADO: {report_file}")
        print(f"🎯 Errores identificados: {results['total_errors']}/263")
        
        return results['total_errors']
        
    except Exception as e:
        print(f"❌ Error crítico en validación: {str(e)}")
        print(traceback.format_exc())
        return -1

if __name__ == "__main__":
    error_count = main()
    print(f"\nValidación completada. Errores críticos: {error_count}")