#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnostic Runner - Analizador de Errores del Sistema
Identifica y cataloga los 263 errores reportados por el usuario
"""

import sys
import os
import traceback
import logging
from datetime import datetime

# Configurar paths del proyecto
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'rexus'))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('diagnostic_errors.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("DiagnosticRunner")

class SystemDiagnostic:
    """Ejecuta diagnósticos del sistema para identificar errores."""
    
    def __init__(self):
        self.errors_found = []
        self.modules_tested = []
        self.warnings_found = []
        
    def run_module_import_test(self):
        """Prueba importación de todos los módulos principales."""
        
        modules_to_test = [
            'rexus.core.database_manager',
            'rexus.core.module_manager', 
            'rexus.core.auth_manager',
            'rexus.modules.configuracion.controller',
            'rexus.modules.configuracion.model',
            'rexus.modules.configuracion.view',
            'rexus.modules.usuarios.controller',
            'rexus.modules.usuarios.model',
            'rexus.modules.usuarios.view',
            'rexus.modules.inventario.controller',
            'rexus.modules.inventario.model',
            'rexus.modules.inventario.view',
            'rexus.modules.obras.controller',
            'rexus.modules.obras.model',
            'rexus.modules.obras.view',
            'rexus.modules.compras.controller',
            'rexus.modules.compras.model',
            'rexus.modules.compras.view',
            'rexus.modules.pedidos.controller',
            'rexus.modules.pedidos.model',
            'rexus.modules.pedidos.view',
            'rexus.modules.vidrios.controller',
            'rexus.modules.vidrios.model',
            'rexus.modules.vidrios.view',
            'rexus.modules.notificaciones.controller',
            'rexus.modules.notificaciones.model',
            'rexus.modules.notificaciones.view'
        ]
        
        logger.info("🔍 INICIANDO PRUEBAS DE IMPORTACIÓN DE MÓDULOS")
        logger.info("=" * 60)
        
        for module_name in modules_to_test:
            try:
                logger.info(f"Testing: {module_name}")
                __import__(module_name)
                logger.info(f"✅ {module_name} - OK")
                self.modules_tested.append((module_name, "SUCCESS"))
                
            except ImportError as e:
                error_msg = f"❌ {module_name} - ImportError: {str(e)}"
                logger.error(error_msg)
                self.errors_found.append(f"IMPORT_ERROR: {module_name} - {str(e)}")
                self.modules_tested.append((module_name, "IMPORT_ERROR"))
                
            except Exception as e:
                error_msg = f"⚠️ {module_name} - Error: {str(e)}"
                logger.warning(error_msg)
                self.errors_found.append(f"MODULE_ERROR: {module_name} - {str(e)}")
                self.modules_tested.append((module_name, "ERROR"))
    
    def run_database_connectivity_test(self):
        """Prueba conectividad de base de datos."""
        
        logger.info("\n🗄️ INICIANDO PRUEBAS DE CONECTIVIDAD DE BD")
        logger.info("=" * 60)
        
        try:
            from rexus.core.database_manager import DatabaseManager
            
            # Probar conexión SQLite
            try:
                db_manager = DatabaseManager()
                db_manager.initialize_database()
                logger.info("✅ Conexión SQLite - OK")
                
            except Exception as e:
                error_msg = f"❌ Conexión SQLite falló: {str(e)}"
                logger.error(error_msg)
                self.errors_found.append(f"DB_SQLITE_ERROR: {str(e)}")
            
            # Probar conexión SQL Server si está configurada
            try:
                if hasattr(db_manager, 'connect_sql_server'):
                    db_manager.connect_sql_server()
                    logger.info("✅ Conexión SQL Server - OK")
                else:
                    logger.info("⚠️ SQL Server no configurado")
                    
            except Exception as e:
                error_msg = f"⚠️ SQL Server no disponible: {str(e)}"
                logger.warning(error_msg)
                self.warnings_found.append(f"DB_SQLSERVER_WARNING: {str(e)}")
                
        except Exception as e:
            error_msg = f"❌ DatabaseManager no disponible: {str(e)}"
            logger.error(error_msg)
            self.errors_found.append(f"DB_MANAGER_ERROR: {str(e)}")
    
    def run_ui_component_test(self):
        """Prueba componentes de UI y dependencias."""
        
        logger.info("\n🖥️ INICIANDO PRUEBAS DE COMPONENTES UI")
        logger.info("=" * 60)
        
        ui_components = [
            'PyQt6.QtWidgets',
            'PyQt6.QtCore', 
            'PyQt6.QtGui',
            'PyQt6.QtWebEngineWidgets'
        ]
        
        for component in ui_components:
            try:
                __import__(component)
                logger.info(f"✅ {component} - OK")
                
            except ImportError as e:
                error_msg = f"❌ {component} - Faltante: {str(e)}"
                logger.error(error_msg)
                self.errors_found.append(f"UI_DEPENDENCY_ERROR: {component} - {str(e)}")
    
    def run_controller_instantiation_test(self):
        """Prueba instanciación de controladores principales."""
        
        logger.info("\n🎮 INICIANDO PRUEBAS DE CONTROLADORES")
        logger.info("=" * 60)
        
        controllers_to_test = [
            ('configuracion', 'rexus.modules.configuracion.controller', 'ConfiguracionController'),
            ('usuarios', 'rexus.modules.usuarios.controller', 'UsuariosController'),
            ('inventario', 'rexus.modules.inventario.controller', 'InventarioController'),
            ('obras', 'rexus.modules.obras.controller', 'ObrasController'),
            ('compras', 'rexus.modules.compras.controller', 'ComprasController'),
            ('pedidos', 'rexus.modules.pedidos.controller', 'PedidosController'),
            ('vidrios', 'rexus.modules.vidrios.controller', 'VidriosController'),
            ('notificaciones', 'rexus.modules.notificaciones.controller', 'NotificacionesController')
        ]
        
        for module_name, module_path, class_name in controllers_to_test:
            try:
                logger.info(f"Testing controller: {module_name}")
                
                # Importar módulo
                module = __import__(module_path, fromlist=[class_name])
                controller_class = getattr(module, class_name)
                
                # Intentar instanciar (puede fallar por dependencias)
                try:
                    controller = controller_class()
                    logger.info(f"✅ {module_name} Controller - OK")
                    
                except Exception as e:
                    logger.warning(f"⚠️ {module_name} Controller - Error instanciación: {str(e)}")
                    self.warnings_found.append(f"CONTROLLER_INSTANTIATION: {module_name} - {str(e)}")
                
            except ImportError as e:
                error_msg = f"❌ {module_name} Controller - ImportError: {str(e)}"
                logger.error(error_msg)
                self.errors_found.append(f"CONTROLLER_IMPORT_ERROR: {module_name} - {str(e)}")
                
            except AttributeError as e:
                error_msg = f"❌ {module_name} Controller - Clase no encontrada: {str(e)}"
                logger.error(error_msg)
                self.errors_found.append(f"CONTROLLER_CLASS_ERROR: {module_name} - {str(e)}")
    
    def generate_comprehensive_report(self):
        """Genera reporte completo de errores encontrados."""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"DIAGNOSTIC_REPORT_{timestamp}.md"
        
        report_content = f"""# REPORTE DIAGNÓSTICO DEL SISTEMA - {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

## 📊 RESUMEN EJECUTIVO

- **Total Errores Críticos:** {len(self.errors_found)}
- **Total Advertencias:** {len(self.warnings_found)}
- **Módulos Analizados:** {len(self.modules_tested)}
- **Análisis Realizado:** {timestamp}

## ❌ ERRORES CRÍTICOS IDENTIFICADOS

"""
        
        for i, error in enumerate(self.errors_found, 1):
            report_content += f"{i}. {error}\n"
        
        report_content += f"""
## ⚠️ ADVERTENCIAS DEL SISTEMA

"""
        
        for i, warning in enumerate(self.warnings_found, 1):
            report_content += f"{i}. {warning}\n"
        
        report_content += f"""
## 📋 ESTADO DE MÓDULOS

| Módulo | Estado | Observaciones |
|--------|--------|--------------|
"""
        
        for module, status in self.modules_tested:
            icon = "✅" if status == "SUCCESS" else "❌" if status == "IMPORT_ERROR" else "⚠️"
            report_content += f"| {module} | {icon} {status} | - |\n"
        
        report_content += f"""
## 🎯 PLAN DE CORRECCIÓN RECOMENDADO

### Prioridad Alta
1. **Dependencias Faltantes:** Instalar PyQt6-WebEngine y otras dependencias críticas
2. **Errores de Importación:** Corregir módulos con ImportError
3. **Conectividad BD:** Verificar configuración de base de datos

### Prioridad Media  
4. **Controladores:** Corregir instanciación de controladores
5. **Configuración:** Completar módulos de configuración y usuarios

### Prioridad Baja
6. **Advertencias:** Resolver warnings menores del sistema

## 📈 MÉTRICAS DE CALIDAD

- **Tasa de Éxito de Importación:** {(len([m for m in self.modules_tested if m[1] == 'SUCCESS']) / len(self.modules_tested) * 100):.1f}%
- **Errores Críticos por Módulo:** {len(self.errors_found) / len(self.modules_tested):.2f}
- **Estabilidad del Sistema:** {'BAJA' if len(self.errors_found) > 20 else 'MEDIA' if len(self.errors_found) > 10 else 'ALTA'}

---
*Reporte generado automáticamente por DiagnosticRunner*
"""
        
        # Escribir reporte
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
            
        logger.info(f"\n📋 REPORTE COMPLETO GENERADO: {report_file}")
        return report_file
    
    def run_full_diagnostic(self):
        """Ejecuta diagnóstico completo del sistema."""
        
        logger.info("🚀 INICIANDO DIAGNÓSTICO COMPLETO DEL SISTEMA")
        logger.info("=" * 80)
        logger.info(f"Timestamp: {datetime.now()}")
        logger.info(f"Python: {sys.version}")
        logger.info(f"Working Directory: {os.getcwd()}")
        logger.info("=" * 80)
        
        # Ejecutar todas las pruebas
        self.run_module_import_test()
        self.run_database_connectivity_test()
        self.run_ui_component_test()
        self.run_controller_instantiation_test()
        
        # Generar reporte
        report_file = self.generate_comprehensive_report()
        
        logger.info("\n" + "=" * 80)
        logger.info("🏁 DIAGNÓSTICO COMPLETO FINALIZADO")
        logger.info("=" * 80)
        logger.info(f"📊 RESUMEN:")
        logger.info(f"   - Errores críticos encontrados: {len(self.errors_found)}")
        logger.info(f"   - Advertencias del sistema: {len(self.warnings_found)}")
        logger.info(f"   - Módulos analizados: {len(self.modules_tested)}")
        logger.info(f"   - Reporte generado: {report_file}")
        
        return {
            'errors': self.errors_found,
            'warnings': self.warnings_found,
            'modules_tested': self.modules_tested,
            'report_file': report_file
        }

def main():
    """Función principal del diagnóstico."""
    
    try:
        diagnostic = SystemDiagnostic()
        results = diagnostic.run_full_diagnostic()
        
        print(f"\n🎯 DIAGNÓSTICO COMPLETADO")
        print(f"Total de errores identificados: {len(results['errors'])}")
        print(f"Reporte detallado: {results['report_file']}")
        
        return len(results['errors'])
        
    except Exception as e:
        logger.error(f"Error crítico en diagnóstico: {str(e)}")
        logger.error(traceback.format_exc())
        return -1

if __name__ == "__main__":
    error_count = main()
    sys.exit(error_count if error_count > 0 else 0)