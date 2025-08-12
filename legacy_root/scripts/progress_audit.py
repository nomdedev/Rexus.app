#!/usr/bin/env python3
"""
Auditoría de progreso en correcciones del checklist de producción
"""

import os
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class ProgressAuditor:
    def __init__(self):
        self.root_path = Path(".")
        self.progress_report = {
            'timestamp': datetime.now().isoformat(),
            'errores_sintaxis': {'resueltos': 0, 'pendientes': 0},
            'vulnerabilidades_sql': {'corregidas': 0, 'pendientes': 0},
            'manejo_errores': {'corregidos': 0, 'pendientes': 0},
            'configuracion': {'completado': 0, 'pendiente': 0},
            'archivos_criticos': []
        }
    
    def check_syntax_errors(self) -> Dict[str, Any]:
        """Verifica errores de sintaxis en archivos críticos."""
        critical_files = [
            "rexus/modules/administracion/view_integrated.py",
            "rexus/modules/compras/dialogs/dialog_proveedor.py",
            "rexus/modules/compras/dialogs/dialog_seguimiento.py",
            "rexus/modules/herrajes/view_simple.py",
            "rexus/modules/inventario/dialogs/missing_dialogs.py",
            "rexus/modules/inventario/dialogs/modern_product_dialog.py",
            "rexus/modules/obras/dialogs/modern_obra_dialog.py"
        ]
        
        syntax_status = {'clean': [], 'errors': []}
        
        for file_path in critical_files:
            py_file = self.root_path / file_path
            if py_file.exists():
                try:
                    result = subprocess.run(
                        ['python', '-m', 'py_compile', str(py_file)],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        syntax_status['clean'].append(file_path)
                    else:
                        syntax_status['errors'].append(file_path)
                except Exception:
                    syntax_status['errors'].append(file_path)
        
        return syntax_status
    
    def check_sql_vulnerabilities(self) -> Dict[str, Any]:
        """Verifica estado de vulnerabilidades SQL."""
        sql_patterns = [
            r'f".*\{.*\}.*".*(?:execute|query)',
            r'\.format\(.*\).*(?:execute|query)',
            r'".*\+.*".*(?:execute|query)'
        ]
        
        vulnerabilities = {'files_with_issues': [], 'files_clean': []}
        
        # Verificar archivos críticos que se han trabajado
        critical_files = [
            "rexus/modules/usuarios/submodules/profiles_manager.py",
            "rexus/modules/usuarios/submodules/auth_manager.py",
            "rexus/modules/usuarios/submodules/permissions_manager.py",
            "rexus/modules/herrajes/model.py",
            "rexus/modules/obras/model.py",
            "rexus/modules/usuarios/model.py"
        ]
        
        import re
        
        for file_path in critical_files:
            py_file = self.root_path / file_path
            if py_file.exists():
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    has_vulnerability = False
                    for pattern in sql_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            has_vulnerability = True
                            break
                    
                    if has_vulnerability:
                        vulnerabilities['files_with_issues'].append(file_path)
                    else:
                        vulnerabilities['files_clean'].append(file_path)
                        
                except Exception:
                    vulnerabilities['files_with_issues'].append(file_path)
        
        return vulnerabilities
    
    def check_configuration_status(self) -> Dict[str, Any]:
        """Verifica estado de archivos de configuración."""
        config_status = {'present': [], 'missing': []}
        
        required_configs = [
            'config/production_config_template.json',
            '.env.production.template',
            'rexus/core/sql_query_manager.py'
        ]
        
        for config_file in required_configs:
            config_path = self.root_path / config_file
            if config_path.exists():
                config_status['present'].append(config_file)
            else:
                config_status['missing'].append(config_file)
        
        return config_status
    
    def generate_progress_report(self) -> Dict[str, Any]:
        """Genera reporte completo de progreso."""
        print("🔍 Ejecutando auditoría de progreso...")
        
        # Verificar errores de sintaxis
        syntax_status = self.check_syntax_errors()
        
        # Verificar vulnerabilidades SQL
        sql_status = self.check_sql_vulnerabilities()
        
        # Verificar configuración
        config_status = self.check_configuration_status()
        
        # Actualizar reporte
        self.progress_report['errores_sintaxis']['resueltos'] = len(syntax_status['clean'])
        self.progress_report['errores_sintaxis']['pendientes'] = len(syntax_status['errors'])
        
        self.progress_report['vulnerabilidades_sql']['corregidas'] = len(sql_status['files_clean'])
        self.progress_report['vulnerabilidades_sql']['pendientes'] = len(sql_status['files_with_issues'])
        
        self.progress_report['configuracion']['completado'] = len(config_status['present'])
        self.progress_report['configuracion']['pendiente'] = len(config_status['missing'])
        
        # Calcular porcentaje de progreso general
        total_items = (
            self.progress_report['errores_sintaxis']['resueltos'] + 
            self.progress_report['errores_sintaxis']['pendientes'] +
            self.progress_report['vulnerabilidades_sql']['corregidas'] +
            self.progress_report['vulnerabilidades_sql']['pendientes'] +
            self.progress_report['configuracion']['completado'] +
            self.progress_report['configuracion']['pendiente']
        )
        
        completed_items = (
            self.progress_report['errores_sintaxis']['resueltos'] +
            self.progress_report['vulnerabilidades_sql']['corregidas'] +
            self.progress_report['configuracion']['completado']
        )
        
        progress_percentage = (completed_items / total_items * 100) if total_items > 0 else 0
        
        return {
            'progress_percentage': round(progress_percentage, 1),
            'syntax_status': syntax_status,
            'sql_status': sql_status,
            'config_status': config_status,
            'detailed_report': self.progress_report
        }

def main():
    print("📊 AUDITORÍA DE PROGRESO - CHECKLIST PRODUCCIÓN")
    print("=" * 55)
    
    auditor = ProgressAuditor()
    report = auditor.generate_progress_report()
    
    print(f"\n🎯 PROGRESO GENERAL: {report['progress_percentage']}%")
    
    print(f"\n✅ ERRORES DE SINTAXIS:")
    print(f"  • Resueltos: {report['detailed_report']['errores_sintaxis']['resueltos']}")
    print(f"  • Pendientes: {report['detailed_report']['errores_sintaxis']['pendientes']}")
    
    if report['syntax_status']['clean']:
        print(f"  📋 Archivos limpios:")
        for file in report['syntax_status']['clean']:
            print(f"    ✓ {file}")
    
    if report['syntax_status']['errors']:
        print(f"  📋 Archivos con errores:")
        for file in report['syntax_status']['errors']:
            print(f"    ❌ {file}")
    
    print(f"\n🛡️ VULNERABILIDADES SQL:")
    print(f"  • Corregidas: {report['detailed_report']['vulnerabilidades_sql']['corregidas']}")
    print(f"  • Pendientes: {report['detailed_report']['vulnerabilidades_sql']['pendientes']}")
    
    if report['sql_status']['files_clean']:
        print(f"  📋 Archivos seguros:")
        for file in report['sql_status']['files_clean']:
            print(f"    ✓ {file}")
    
    if report['sql_status']['files_with_issues']:
        print(f"  📋 Archivos con vulnerabilidades:")
        for file in report['sql_status']['files_with_issues']:
            print(f"    ⚠️ {file}")
    
    print(f"\n⚙️ CONFIGURACIÓN:")
    print(f"  • Completado: {report['detailed_report']['configuracion']['completado']}")
    print(f"  • Pendiente: {report['detailed_report']['configuracion']['pendiente']}")
    
    if report['config_status']['present']:
        print(f"  📋 Archivos presentes:")
        for file in report['config_status']['present']:
            print(f"    ✓ {file}")
    
    if report['config_status']['missing']:
        print(f"  📋 Archivos faltantes:")
        for file in report['config_status']['missing']:
            print(f"    ❌ {file}")
    
    # Próximos pasos basados en el progreso
    print(f"\n🎯 PRÓXIMOS PASOS PRIORITARIOS:")
    
    if report['syntax_status']['errors']:
        print(f"1. 🔴 CRÍTICO: Corregir {len(report['syntax_status']['errors'])} errores de sintaxis restantes")
    
    if report['sql_status']['files_with_issues']:
        print(f"2. 🟡 IMPORTANTE: Revisar {len(report['sql_status']['files_with_issues'])} archivos con vulnerabilidades SQL")
    
    if report['config_status']['missing']:
        print(f"3. 🟡 IMPORTANTE: Crear {len(report['config_status']['missing'])} archivos de configuración faltantes")
    
    if report['progress_percentage'] >= 80:
        print(f"4. 🔵 SIGUIENTE FASE: Ejecutar tests de integración")
        print(f"5. 🔵 SIGUIENTE FASE: Configurar entorno de producción")
    
    # Guardar reporte
    report_file = f"progress_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Reporte detallado guardado en: {report_file}")
    
    # Estado general
    if report['progress_percentage'] >= 90:
        print(f"\n🎉 ¡Excelente progreso! Sistema casi listo para producción")
    elif report['progress_percentage'] >= 70:
        print(f"\n👍 Buen progreso, continuar con correcciones")
    else:
        print(f"\n⚠️ Progreso inicial, concentrarse en problemas críticos")
    
    return report

if __name__ == "__main__":
    main()
