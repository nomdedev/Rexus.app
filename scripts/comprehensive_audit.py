#!/usr/bin/env python3
"""
Auditoría integral y consolidada - Estado actual del proyecto
Identifica todos los issues pendientes según checklists y auditorías
"""

import os
import subprocess
from pathlib import Path
from datetime import datetime
import json
import re
from typing import Dict, List, Any, Optional

class ComprehensiveAudit:
    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.issues_found = []
        self.modules_checked = []
        
    def check_permissions_manager_issues(self) -> List[Dict[str, Any]]:
        """Verifica issues específicos en permissions_manager.py"""
        issues = []
        file_path = Path("rexus/modules/usuarios/submodules/permissions_manager.py")
        
        if file_path.exists():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Buscar try/except/pass patterns
                if re.search(r'except Exception.*:\s*\n\s*pass', content, re.MULTILINE):
                    issues.append({
                        'file': str(file_path),
                        'type': 'Try/Except/Pass Pattern',
                        'severity': 'WARNING',
                        'description': 'Detected try/except/pass pattern that should log errors'
                    })
                
                # Buscar f-strings en logs
                if re.search(r'logger\.\w+\(f".*\{.*\}.*"\)', content):
                    issues.append({
                        'file': str(file_path),
                        'type': 'F-string in Logger',
                        'severity': 'WARNING', 
                        'description': 'F-strings in logger should use % formatting for security'
                    })
                    
            except Exception as e:
                issues.append({
                    'file': str(file_path),
                    'type': 'Read Error',
                    'severity': 'ERROR',
                    'description': f'Could not read file: {e}'
                })
        
        return issues
    
    def check_core_modules_completeness(self) -> List[Dict[str, Any]]:
        """Verifica completitud de módulos core según auditorías"""
        issues = []
        
        # Archivos críticos que deben existir según auditorías
        critical_files = [
            "rexus/core/security_manager.py",
            "requirements.txt",
            "rexus/core/rate_limiter.py",
            "rexus/utils/performance_monitor.py",
            "config/backup_automated.py"
        ]
        
        for file_path in critical_files:
            full_path = Path(file_path)
            if not full_path.exists():
                issues.append({
                    'file': file_path,
                    'type': 'Missing Critical File',
                    'severity': 'HIGH',
                    'description': f'File mentioned in audits but not found: {file_path}'
                })
        
        return issues
    
    def check_sql_injection_completeness(self) -> List[Dict[str, Any]]:
        """Verifica que la migración SQL esté 100% completa"""
        issues = []
        
        # Buscar posibles patrones SQL injection restantes
        python_files = list(Path("rexus").rglob("*.py"))
        
        sql_injection_patterns = [
            r'cursor\.execute\(.*\+.*\)',  # String concatenation in execute
            r'cursor\.execute\(.*\.format\(.*\)\)',  # .format() in execute
            r'cursor\.execute\(.*%.*\)',  # % formatting in execute
            r'f".*\{.*\}".*execute',  # f-strings followed by execute
        ]
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for pattern in sql_injection_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        issues.append({
                            'file': str(py_file),
                            'type': 'Potential SQL Injection',
                            'severity': 'CRITICAL',
                            'description': f'Detected potential SQL injection pattern: {pattern}'
                        })
                        break  # Solo reportar una vez por archivo
                        
            except Exception:
                continue  # Skip unreadable files
        
        return issues
    
    def check_test_coverage(self) -> List[Dict[str, Any]]:
        """Verifica estado de tests según auditorías"""
        issues = []
        
        # Verificar que existan tests básicos
        test_dirs = [
            Path("tests"),
            Path("test"),
        ]
        
        has_tests = any(test_dir.exists() and any(test_dir.rglob("test_*.py")) for test_dir in test_dirs)
        
        if not has_tests:
            issues.append({
                'file': 'tests/',
                'type': 'Missing Test Coverage',
                'severity': 'MEDIUM',
                'description': 'No test files found - testing coverage incomplete'
            })
        
        # Verificar tests para módulos críticos según auditorías
        critical_modules = ['usuarios', 'inventario', 'obras', 'herrajes']
        
        for module in critical_modules:
            test_file = Path(f"tests/test_{module}.py")
            if not test_file.exists():
                issues.append({
                    'file': f'tests/test_{module}.py',
                    'type': 'Missing Module Test',
                    'severity': 'MEDIUM',
                    'description': f'No tests found for critical module: {module}'
                })
        
        return issues
    
    def check_configuration_completeness(self) -> List[Dict[str, Any]]:
        """Verifica configuración para producción según checklists"""
        issues = []
        
        # Archivos de configuración requeridos
        config_files = [
            ".env.production.template",
            "config/production_config_template.json",
            "config/rexus_config.json"
        ]
        
        for config_file in config_files:
            if not Path(config_file).exists():
                issues.append({
                    'file': config_file,
                    'type': 'Missing Config File',
                    'severity': 'MEDIUM',
                    'description': f'Production config file missing: {config_file}'
                })
        
        # Verificar que main.py esté listo para producción
        main_file = Path("main.py")
        if main_file.exists():
            try:
                with open(main_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Verificar que no haya debug hardcodeado
                if 'debug=True' in content or 'DEBUG = True' in content:
                    issues.append({
                        'file': 'main.py',
                        'type': 'Debug Mode Hardcoded',
                        'severity': 'MEDIUM',
                        'description': 'Debug mode should be configurable, not hardcoded'
                    })
                    
            except Exception:
                pass
        
        return issues
    
    def check_documentation_completeness(self) -> List[Dict[str, Any]]:
        """Verifica completitud de documentación según auditorías"""
        issues = []
        
        # Documentos críticos que deben existir
        required_docs = [
            "README.md",
            "docs/installation.md", 
            "docs/configuration.md",
            "docs/deployment.md",
            "docs/security.md"
        ]
        
        for doc in required_docs:
            if not Path(doc).exists():
                issues.append({
                    'file': doc,
                    'type': 'Missing Documentation',
                    'severity': 'LOW',
                    'description': f'Important documentation file missing: {doc}'
                })
        
        return issues
    
    def run_comprehensive_audit(self) -> Dict[str, Any]:
        """Ejecuta auditoría completa y consolida resultados"""
        print("🔍 EJECUTANDO AUDITORÍA INTEGRAL CONSOLIDADA")
        print("=" * 60)
        print(f"📅 Fecha: {self.timestamp}")
        print()
        
        # Ejecutar todas las verificaciones
        all_issues = []
        
        print("🔧 Verificando permissions_manager issues...")
        all_issues.extend(self.check_permissions_manager_issues())
        
        print("🔧 Verificando completitud de módulos core...")
        all_issues.extend(self.check_core_modules_completeness())
        
        print("🔧 Verificando migración SQL...")
        all_issues.extend(self.check_sql_injection_completeness())
        
        print("🔧 Verificando cobertura de tests...")
        all_issues.extend(self.check_test_coverage())
        
        print("🔧 Verificando configuración...")
        all_issues.extend(self.check_configuration_completeness())
        
        print("🔧 Verificando documentación...")
        all_issues.extend(self.check_documentation_completeness())
        
        # Agrupar issues por severidad
        issues_by_severity = {
            'CRITICAL': [],
            'HIGH': [],
            'MEDIUM': [],
            'WARNING': [],
            'LOW': []
        }
        
        for issue in all_issues:
            severity = issue.get('severity', 'UNKNOWN')
            if severity in issues_by_severity:
                issues_by_severity[severity].append(issue)
        
        # Generar reporte
        total_issues = len(all_issues)
        
        print(f"\n📊 RESULTADOS DE AUDITORÍA INTEGRAL")
        print("-" * 50)
        print(f"Total de issues encontrados: {total_issues}")
        
        for severity, issues in issues_by_severity.items():
            count = len(issues)
            if count > 0:
                emoji = {
                    'CRITICAL': '🔴',
                    'HIGH': '🟠', 
                    'MEDIUM': '🟡',
                    'WARNING': '⚠️',
                    'LOW': '🔵'
                }.get(severity, '❓')
                
                print(f"{emoji} {severity}: {count} issues")
                
                for issue in issues:
                    print(f"  • {issue['file']}: {issue['description']}")
        
        print(f"\n🎯 ESTADO GENERAL DEL PROYECTO")
        print("-" * 50)
        
        if total_issues == 0:
            print("✅ EXCELENTE: Sin issues detectados - Listo para producción")
            status = "READY_FOR_PRODUCTION"
        elif issues_by_severity['CRITICAL'] or issues_by_severity['HIGH']:
            print("🔴 CRÍTICO: Issues de alta prioridad requieren atención inmediata")
            status = "NEEDS_CRITICAL_FIXES"
        elif len(all_issues) <= 5:
            print("🟡 BUENO: Pocos issues menores - Casi listo para producción")
            status = "MINOR_ISSUES_ONLY"
        else:
            print("🟠 MODERADO: Varios issues requieren atención antes de producción")
            status = "MODERATE_ISSUES"
        
        # Guardar reporte detallado
        report = {
            'timestamp': self.timestamp,
            'total_issues': total_issues,
            'status': status,
            'issues_by_severity': issues_by_severity,
            'all_issues': all_issues
        }
        
        report_file = f"comprehensive_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Reporte detallado guardado en: {report_file}")
        
        return report

def main():
    auditor = ComprehensiveAudit()
    return auditor.run_comprehensive_audit()

if __name__ == "__main__":
    main()
