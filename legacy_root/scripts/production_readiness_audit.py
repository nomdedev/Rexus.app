#!/usr/bin/env python3
"""
Script de auditoría completa para detectar problemas críticos antes de producción
Checklist de preparación para producción - Rexus.app
"""

import ast
import os
import re
from pathlib import Path
import json
from typing import Dict, List, Any

class ProductionReadinessChecker:
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.issues = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }
        
    def check_syntax_errors(self) -> List[str]:
        """Detecta errores de sintaxis en archivos Python."""
        syntax_errors = []
        
        for py_file in self.root_path.rglob("*.py"):
            # Saltar archivos de backup y cache
            if any(skip in str(py_file) for skip in ['__pycache__', '.pyc', 'backup']):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                ast.parse(content)
            except SyntaxError as e:
                syntax_errors.append(f"{py_file.relative_to(self.root_path)}: {e}")
            except Exception as e:
                syntax_errors.append(f"{py_file.relative_to(self.root_path)}: Error inesperado - {e}")
        
        return syntax_errors
    
    def check_sql_injection_vulnerabilities(self) -> List[str]:
        """Detecta posibles vulnerabilidades de SQL injection."""
        vulnerabilities = []
        
        sql_injection_patterns = [
            r'\.format\([^)]*\).*(?:execute|query|cursor)',
            r'f"[^"]*\{[^}]*\}[^"]*".*(?:execute|query|cursor)',
            r'".*\+.*".*(?:execute|query|cursor)',
            r'%.*%.*(?:execute|query|cursor)',
            r'cursor\.execute\([^?]*["\'][^"\']*["\'][^)]*\)',
        ]
        
        for py_file in self.root_path.rglob("*.py"):
            if any(skip in str(py_file) for skip in ['__pycache__', '.pyc', 'backup']):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for i, line in enumerate(content.split('\n'), 1):
                    for pattern in sql_injection_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            vulnerabilities.append(f"{py_file.relative_to(self.root_path)}:{i} - Posible SQL injection: {line.strip()}")
            
            except Exception as e:
                continue
        
        return vulnerabilities
    
    def check_hardcoded_credentials(self) -> List[str]:
        """Detecta credenciales hardcodeadas."""
        credentials = []
        
        credential_patterns = [
            r'password\s*=\s*["\'][^"\']{3,}["\']',
            r'pwd\s*=\s*["\'][^"\']{3,}["\']',
            r'api_key\s*=\s*["\'][^"\']{10,}["\']',
            r'secret\s*=\s*["\'][^"\']{10,}["\']',
            r'token\s*=\s*["\'][^"\']{10,}["\']',
        ]
        
        for py_file in self.root_path.rglob("*.py"):
            if any(skip in str(py_file) for skip in ['__pycache__', '.pyc', 'backup']):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for i, line in enumerate(content.split('\n'), 1):
                    for pattern in credential_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            # Filtrar casos obvios como ejemplos o defaults
                            if not any(exclude in line.lower() for exclude in ['example', 'default', 'test', 'demo']):
                                credentials.append(f"{py_file.relative_to(self.root_path)}:{i} - Credencial hardcodeada: {line.strip()}")
            
            except Exception as e:
                continue
        
        return credentials
    
    def check_missing_error_handling(self) -> List[str]:
        """Detecta funciones sin manejo de errores."""
        missing_error_handling = []
        
        for py_file in self.root_path.rglob("*.py"):
            if any(skip in str(py_file) for skip in ['__pycache__', '.pyc', 'backup']):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Buscar funciones que hacen conexiones DB sin try/except
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if re.search(r'\.connect\(|\.execute\(|\.cursor\(', line):
                        # Verificar si está dentro de un bloque try
                        in_try_block = False
                        for j in range(max(0, i-10), i):
                            if re.search(r'^\s*try:', lines[j]):
                                in_try_block = True
                                break
                        
                        if not in_try_block:
                            missing_error_handling.append(f"{py_file.relative_to(self.root_path)}:{i+1} - Sin manejo de errores: {line.strip()}")
            
            except Exception as e:
                continue
        
        return missing_error_handling
    
    def check_debug_code(self) -> List[str]:
        """Detecta código de debug que no debería ir a producción."""
        debug_code = []
        
        debug_patterns = [
            r'print\s*\(',
            r'pdb\.set_trace\(\)',
            r'breakpoint\(\)',
            r'console\.log\(',
            r'debugger;',
            r'DEBUG\s*=\s*True',
        ]
        
        for py_file in self.root_path.rglob("*.py"):
            if any(skip in str(py_file) for skip in ['__pycache__', '.pyc', 'backup', 'test']):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                for i, line in enumerate(content.split('\n'), 1):
                    for pattern in debug_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            # Filtrar logging válido
                            if not any(valid in line.lower() for valid in ['logging.', 'logger.', 'log.']):
                                debug_code.append(f"{py_file.relative_to(self.root_path)}:{i} - Código de debug: {line.strip()}")
            
            except Exception as e:
                continue
        
        return debug_code
    
    def check_configuration_files(self) -> List[str]:
        """Verifica archivos de configuración críticos."""
        config_issues = []
        
        # Verificar archivos de configuración requeridos
        required_configs = [
            'config/rexus_config.json',
            'config/secure_config.json'
        ]
        
        for config_file in required_configs:
            config_path = self.root_path / config_file
            if not config_path.exists():
                config_issues.append(f"Archivo de configuración faltante: {config_file}")
            else:
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)
                    
                    # Verificar campos críticos
                    if 'rexus_config.json' in config_file:
                        required_fields = ['db_server', 'db_name', 'sistema_version']
                        for field in required_fields:
                            if not config_data.get(field):
                                config_issues.append(f"{config_file}: Campo requerido vacío - {field}")
                
                except json.JSONDecodeError:
                    config_issues.append(f"{config_file}: JSON inválido")
                except Exception as e:
                    config_issues.append(f"{config_file}: Error leyendo archivo - {e}")
        
        return config_issues
    
    def check_imports(self) -> List[str]:
        """Detecta imports problemáticos o faltantes."""
        import_issues = []
        
        for py_file in self.root_path.rglob("*.py"):
            if any(skip in str(py_file) for skip in ['__pycache__', '.pyc', 'backup']):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Detectar imports relativos problemáticos
                for i, line in enumerate(content.split('\n'), 1):
                    if re.search(r'from\s+\.\.\.\s+import', line):
                        import_issues.append(f"{py_file.relative_to(self.root_path)}:{i} - Import relativo profundo: {line.strip()}")
                    
                    if re.search(r'import\s+\*', line):
                        import_issues.append(f"{py_file.relative_to(self.root_path)}:{i} - Import * detectado: {line.strip()}")
            
            except Exception as e:
                continue
        
        return import_issues
    
    def run_complete_audit(self) -> Dict[str, Any]:
        """Ejecuta auditoría completa del sistema."""
        print("🔍 Iniciando auditoría completa para preparación de producción...")
        
        # Ejecutar todas las verificaciones
        syntax_errors = self.check_syntax_errors()
        sql_vulnerabilities = self.check_sql_injection_vulnerabilities()
        credentials = self.check_hardcoded_credentials()
        error_handling = self.check_missing_error_handling()
        debug_code = self.check_debug_code()
        config_issues = self.check_configuration_files()
        import_issues = self.check_imports()
        
        # Clasificar problemas por severidad
        if syntax_errors:
            self.issues['critical'].extend([f"SINTAXIS: {error}" for error in syntax_errors])
        
        if sql_vulnerabilities:
            self.issues['critical'].extend([f"SQL INJECTION: {vuln}" for vuln in sql_vulnerabilities])
        
        if credentials:
            self.issues['high'].extend([f"CREDENCIALES: {cred}" for cred in credentials])
        
        if config_issues:
            self.issues['high'].extend([f"CONFIGURACIÓN: {issue}" for issue in config_issues])
        
        if error_handling:
            self.issues['medium'].extend([f"ERROR HANDLING: {error}" for error in error_handling])
        
        if debug_code:
            self.issues['medium'].extend([f"DEBUG CODE: {debug}" for debug in debug_code])
        
        if import_issues:
            self.issues['low'].extend([f"IMPORTS: {imp}" for imp in import_issues])
        
        # Generar reporte
        total_issues = sum(len(issues) for issues in self.issues.values())
        
        report = {
            'timestamp': '2025-08-09',
            'total_issues': total_issues,
            'issues_by_severity': {
                'critical': len(self.issues['critical']),
                'high': len(self.issues['high']),
                'medium': len(self.issues['medium']),
                'low': len(self.issues['low'])
            },
            'details': self.issues,
            'production_ready': len(self.issues['critical']) == 0 and len(self.issues['high']) == 0
        }
        
        return report

def main():
    print("🚀 AUDITORÍA DE PREPARACIÓN PARA PRODUCCIÓN - REXUS.APP")
    print("=" * 60)
    
    checker = ProductionReadinessChecker(".")
    report = checker.run_complete_audit()
    
    # Mostrar resumen
    print(f"\n📊 RESUMEN DE AUDITORÍA:")
    print(f"Total de problemas detectados: {report['total_issues']}")
    print(f"• Críticos: {report['issues_by_severity']['critical']}")
    print(f"• Altos: {report['issues_by_severity']['high']}")
    print(f"• Medios: {report['issues_by_severity']['medium']}")
    print(f"• Bajos: {report['issues_by_severity']['low']}")
    
    # Mostrar estado de producción
    if report['production_ready']:
        print(f"\n✅ SISTEMA LISTO PARA PRODUCCIÓN")
    else:
        print(f"\n❌ SISTEMA NO LISTO PARA PRODUCCIÓN")
        print(f"Se deben corregir {report['issues_by_severity']['critical']} problemas críticos y {report['issues_by_severity']['high']} problemas altos")
    
    # Mostrar detalles de problemas críticos y altos
    if report['details']['critical']:
        print(f"\n🚨 PROBLEMAS CRÍTICOS:")
        for issue in report['details']['critical'][:10]:  # Mostrar solo los primeros 10
            print(f"  • {issue}")
        if len(report['details']['critical']) > 10:
            print(f"  • ... y {len(report['details']['critical']) - 10} más")
    
    if report['details']['high']:
        print(f"\n⚠️ PROBLEMAS ALTOS:")
        for issue in report['details']['high'][:10]:
            print(f"  • {issue}")
        if len(report['details']['high']) > 10:
            print(f"  • ... y {len(report['details']['high']) - 10} más")
    
    # Guardar reporte completo
    with open('production_readiness_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Reporte completo guardado en: production_readiness_report.json")
    
    return report

if __name__ == "__main__":
    main()
