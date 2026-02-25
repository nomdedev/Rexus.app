#!/usr/bin/env python3
"""
Security Scanner - Rexus.app
Escaneo automatizado de vulnerabilidades de seguridad
"""

import os
import re
import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class SecurityIssue:
    """Representa una vulnerabilidad de seguridad encontrada."""
    type: str
    file: str
    line: int
    content: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    description: str
    recommendation: str
    cwe: str = ""

class SecurityScanner:
    """Escáner de seguridad para Rexus.app"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.issues: List[SecurityIssue] = []
        
        # Patrones de vulnerabilidades
        self.vulnerability_patterns = {
            "hardcoded_credentials": [
                (r'admin\s*/\s*admin', "Credenciales admin/admin hardcodeadas"),
                (r'password\s*=\s*["\'][^"\']+["\']', "Contraseña hardcodeada"),
                (r'secret\s*=\s*["\'][^"\']+["\']', "Secret hardcodeado"),
                (r'api_key\s*=\s*["\'][^"\']+["\']', "API key hardcodeada"),
            ],
            "sql_injection": [
                (r'cursor\.execute\(f".*\{.*\}"', "SQL injection con f-string"),
                (r'cursor\.execute\(".*".*\+.*\)', "SQL injection con concatenación"),
                (r'query\s*\+=\s*f".*\{.*\}"', "SQL injection en query dinámico"),
                (r'query\s*\+=\s*".*".*\+.*', "SQL injection con concatenación"),
                (r'execute\s*\(\s*[^,]*\s*\+', "SQL injection potencial"),
            ],
            "path_traversal": [
                (r'open\s*\([^)]*\.\.', "Path traversal posible"),
                (r'file\s*=\s*["\'][^"\']*\.\.', "Path traversal en filepath"),
            ],
            "command_injection": [
                (r'os\.system\s*\([^)]*\+', "Command injection"),
                (r'subprocess\.call\s*\([^)]*\+', "Command injection"),
                (r'eval\s*\(', "Code injection con eval"),
                (r'exec\s*\(', "Code injection con exec"),
            ],
            "crypto_weaknesses": [
                (r'md5\s*\(', "Hash MD5 débil"),
                (r'sha1\s*\(', "Hash SHA1 débil"),
                (r'hashlib\.md5', "Hash MD5 débil"),
                (r'hashlib\.sha1', "Hash SHA1 débil"),
            ],
            "info_disclosure": [
                (r'print\s*\([^)]*password', "Password en logs"),
                (r'print\s*\([^)]*secret', "Secret en logs"),
                (r'print\s*\([^)]*token', "Token en logs"),
                (r'console\.log\s*\([^)]*password', "Password en console log"),
            ],
            "hardcoded_secrets": [
                (r'DB_PASSWORD\s*=\s*["\'][^"\']+["\']', "Password de BD hardcodeado"),
                (r'SECRET_KEY\s*=\s*["\'][^"\']+["\']', "Secret key hardcodeada"),
                (r'JWT_SECRET\s*=\s*["\'][^"\']+["\']', "JWT secret hardcodeado"),
                (r'ENCRYPTION_KEY\s*=\s*["\'][^"\']+["\']', "Encryption key hardcodeado"),
            ]
        }
        
        # Mapeo de severidad por tipo
        self.severity_map = {
            "hardcoded_credentials": "CRITICAL",
            "sql_injection": "CRITICAL", 
            "command_injection": "CRITICAL",
            "hardcoded_secrets": "CRITICAL",
            "path_traversal": "HIGH",
            "crypto_weaknesses": "MEDIUM",
            "info_disclosure": "MEDIUM"
        }
        
        # Recomendaciones por tipo
        self.recommendations = {
            "hardcoded_credentials": "Eliminar credenciales hardcodeadas. Usar variables de entorno o gestor de secrets.",
            "sql_injection": "Usar prepared statements con parámetros. Nunca concatenar user input en queries SQL.",
            "command_injection": "Validar y sanitizar todo input. Usar subprocess con lista de argumentos en lugar de strings.",
            "hardcoded_secrets": "Mover secrets a gestor seguro (AWS Secrets Manager, Azure Key Vault, etc.).",
            "path_traversal": "Validar paths contra whitelist. Usar os.path.join() y never concatenar user input.",
            "crypto_weaknesses": "Usar algoritmos fuertes (bcrypt, Argon2, SHA-256+).",
            "info_disclosure": "Remover información sensible de logs. Usar sistema de logging estructurado."
        }
        
        # CWE por tipo
        self.cwe_map = {
            "hardcoded_credentials": "CWE-798",
            "sql_injection": "CWE-89",
            "command_injection": "CWE-78",
            "hardcoded_secrets": "CWE-798",
            "path_traversal": "CWE-22",
            "crypto_weaknesses": "CWE-327",
            "info_disclosure": "CWE-532"
        }

    def scan_file(self, file_path: Path) -> List[SecurityIssue]:
        """Escanea un archivo en busca de vulnerabilidades."""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
            for vuln_type, patterns in self.vulnerability_patterns.items():
                for pattern, description in patterns:
                    for line_num, line in enumerate(lines, 1):
                        matches = re.finditer(pattern, line, re.IGNORECASE)
                        for match in matches:
                            # Ignorar algunos falsos positivos comunes
                            if self._is_false_positive(match.group(), vuln_type, line):
                                continue
                                
                            issue = SecurityIssue(
                                type=vuln_type,
                                file=str(file_path.relative_to(self.base_path)),
                                line=line_num,
                                content=line.strip(),
                                severity=self.severity_map.get(vuln_type, "MEDIUM"),
                                description=description,
                                recommendation=self.recommendations.get(vuln_type, "Revisar código"),
                                cwe=self.cwe_map.get(vuln_type, "")
                            )
                            issues.append(issue)
                            
        except Exception as e:
            print(f"Error escaneando {file_path}: {e}")
            
        return issues

    def _is_false_positive(self, match: str, vuln_type: str, line: str) -> bool:
        """Detecta falsos positivos comunes."""
        
        # Ignorar comentarios
        if line.strip().startswith('#') or line.strip().startswith('//'):
            return True
            
        # Ignorar strings de ejemplo o documentación
        if 'example' in line.lower() or 'demo' in line.lower():
            return True
            
        # Ignorar patterns comunes que no son vulnerabilidades
        if vuln_type == "sql_injection":
            safe_patterns = [
                'SELECT @@IDENTITY',
                'BEGIN TRANSACTION',
                'COMMIT TRANSACTION',
                'ROLLBACK TRANSACTION',
                'CREATE INDEX',
                'DROP INDEX',
                'SCOPE_IDENTITY()'
            ]
            for safe_pattern in safe_patterns:
                if safe_pattern in match.upper():
                    return True
                    
        if vuln_type == "hardcoded_secrets":
            # Ignorar variables de ejemplo o placeholders
            if any(placeholder in match.upper() for placeholder in [
                'EXAMPLE', 'PLACEHOLDER', 'YOUR_', 'CHANGE_ME', 'REPLACE_'
            ]):
                return True
                
        return False

    def scan_directory(self, directory: str = "rexus") -> List[SecurityIssue]:
        """Escanea un directorio completo en busca de vulnerabilidades."""
        all_issues = []
        
        scan_path = self.base_path / directory
        if not scan_path.exists():
            print(f"Directorio {directory} no encontrado")
            return all_issues
            
        # Escanear archivos Python
        for py_file in scan_path.rglob("*.py"):
            if '.venv' in str(py_file) or '__pycache__' in str(py_file):
                continue
            issues = self.scan_file(py_file)
            all_issues.extend(issues)
            
        # Escanear archivos de configuración
        for config_file in self.base_path.glob("*.env*"):
            issues = self.scan_file(config_file)
            all_issues.extend(issues)
            
        return all_issues

    def generate_report(self, issues: List[SecurityIssue]) -> Dict[str, Any]:
        """Genera un reporte estructurado de las vulnerabilidades encontradas."""
        
        # Agrupar por severidad
        by_severity = {
            "CRITICAL": [],
            "HIGH": [],
            "MEDIUM": [],
            "LOW": []
        }
        
        for issue in issues:
            by_severity[issue.severity].append(issue)
            
        # Agrupar por tipo
        by_type = {}
        for issue in issues:
            if issue.type not in by_type:
                by_type[issue.type] = []
            by_type[issue.type].append(issue)
            
        # Estadísticas
        stats = {
            "total_issues": len(issues),
            "by_severity": {k: len(v) for k, v in by_severity.items()},
            "by_type": {k: len(v) for k, v in by_type.items()},
            "files_affected": len(set(issue.file for issue in issues))
        }
        
        # Convertir objetos SecurityIssue a diccionarios para JSON
        issues_by_severity_dict = {}
        for severity, issue_list in by_severity.items():
            issues_by_severity_dict[severity] = [
                {
                    "type": issue.type,
                    "file": issue.file,
                    "line": issue.line,
                    "content": issue.content,
                    "severity": issue.severity,
                    "description": issue.description,
                    "recommendation": issue.recommendation,
                    "cwe": issue.cwe
                }
                for issue in issue_list
            ]
            
        issues_by_type_dict = {}
        for vuln_type, issue_list in by_type.items():
            issues_by_type_dict[vuln_type] = [
                {
                    "type": issue.type,
                    "file": issue.file,
                    "line": issue.line,
                    "content": issue.content,
                    "severity": issue.severity,
                    "description": issue.description,
                    "recommendation": issue.recommendation,
                    "cwe": issue.cwe
                }
                for issue in issue_list
            ]
        
        return {
            "scan_metadata": {
                "timestamp": datetime.now().isoformat(),
                "scanner_version": "1.0.0",
                "base_path": str(self.base_path),
                "total_files_scanned": len(list(self.base_path.rglob("*.py"))),
                "total_issues_found": len(issues)
            },
            "summary": stats,
            "issues_by_severity": issues_by_severity_dict,
            "issues_by_type": issues_by_type_dict,
            "all_issues": [
                {
                    "type": issue.type,
                    "file": issue.file,
                    "line": issue.line,
                    "content": issue.content,
                    "severity": issue.severity,
                    "description": issue.description,
                    "recommendation": issue.recommendation,
                    "cwe": issue.cwe
                }
                for issue in issues
            ]
        }

    def print_summary(self, report: Dict[str, Any]):
        """Imprime un resumen del reporte."""
        print("\n" + "="*60)
        print("🛡️  SECURITY SCAN REPORT - REXUS.APP")
        print("="*60)
        
        summary = report["summary"]
        print(f"\n📊 SUMMARY:")
        print(f"   Total Issues: {summary['total_issues']}")
        print(f"   Files Affected: {summary['files_affected']}")
        
        print(f"\n🚨 BY SEVERITY:")
        for severity, count in summary["by_severity"].items():
            if count > 0:
                icon = "🔴" if severity == "CRITICAL" else "🟠" if severity == "HIGH" else "🟡" if severity == "MEDIUM" else "🟢"
                print(f"   {icon} {severity}: {count}")
                
        print(f"\n📋 BY TYPE:")
        for vuln_type, count in summary["by_type"].items():
            if count > 0:
                print(f"   • {vuln_type}: {count}")
                
        # Mostrar issues críticos
        critical_issues = report["issues_by_severity"]["CRITICAL"]
        if critical_issues:
            print(f"\n🔴 CRITICAL ISSUES ({len(critical_issues)}):")
            for i, issue in enumerate(critical_issues[:10], 1):  # Limitar a 10
                print(f"   {i}. {issue.file}:{issue.line}")
                print(f"      {issue.description}")
                print(f"      Code: {issue.content[:80]}...")
                print(f"      CWE: {issue.cwe}")
                print()
                
            if len(critical_issues) > 10:
                print(f"   ... and {len(critical_issues) - 10} more critical issues")
                
        print("="*60)

def main():
    """Función principal del escáner."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Security Scanner for Rexus.app")
    parser.add_argument("--path", default=".", help="Base path to scan")
    parser.add_argument("--output", help="Output JSON file")
    parser.add_argument("--directory", default="rexus", help="Directory to scan")
    parser.add_argument("--quiet", action="store_true", help="Quiet mode")
    
    args = parser.parse_args()
    
    scanner = SecurityScanner(args.path)
    
    if not args.quiet:
        print(f"🔍 Scanning {args.directory} directory...")
        
    issues = scanner.scan_directory(args.directory)
    
    if not args.quiet:
        print(f"✅ Scan completed. Found {len(issues)} issues.")
        
    report = scanner.generate_report(issues)
    
    if not args.quiet:
        scanner.print_summary(report)
        
    # Guardar reporte si se especificó archivo de salida
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\nReport saved to: {args.output}")
        
    # Exit code basado en severidad
    critical_count = len(report["issues_by_severity"]["CRITICAL"])
    high_count = len(report["issues_by_severity"]["HIGH"])
    
    if critical_count > 0:
        sys.exit(2)  # Critical issues found
    elif high_count > 0:
        sys.exit(1)  # High issues found
    else:
        sys.exit(0)  # No critical/high issues

if __name__ == "__main__":
    main()