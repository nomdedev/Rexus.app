#!/usr/bin/env python3
"""
Validador de Seguridad de Contraseñas - Rexus.app
Verifica que todos los scripts de mantenimiento usen hashing seguro
y que no haya contraseñas hardcodeadas o métodos inseguros.
"""

import os
import sys
import re
from pathlib import Path

# Agregar ruta del proyecto
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

class SecurityValidator:
    """Validador de seguridad para scripts de mantenimiento."""
    
    def __init__(self):
        self.issues = []
        self.files_checked = 0
        self.critical_issues = 0
        self.warnings = 0
        
    def scan_file_for_security_issues(self, file_path: Path) -> list:
        """Escanea un archivo en busca de problemas de seguridad."""
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Patrones de vulnerabilidades críticas
            critical_patterns = [
                # SHA256 inseguro
                (r'hashlib\.sha256\([^)]+\)\.hexdigest\(\)', 
                 "SHA256 simple detectado - CRÍTICO"),
                
                # Contraseñas hardcodeadas
                (r'password\s*=\s*["\']admin["\']', 
                 "Contraseña 'admin' hardcodeada - CRÍTICO"),
                (r'password\s*=\s*["\']password["\']', 
                 "Contraseña 'password' hardcodeada - CRÍTICO"),
                (r'password\s*=\s*["\']123["\']', 
                 "Contraseña numérica hardcodeada - CRÍTICO"),
                
                # Hash MD5
                (r'hashlib\.md5\(', 
                 "MD5 detectado - CRÍTICO"),
            ]
            
            # Patrones de advertencias
            warning_patterns = [
                (r'print\([^)]*password[^)]*\)', 
                 "Possible password logging - WARNING"),
                (r'print\([^)]*"admin"[^)]*\)', 
                 "Admin credentials in print - WARNING"),
                (r'cursor\.execute\([^)]*admin[^)]*\)', 
                 "Hardcoded admin in query - WARNING"),
            ]
            
            # Buscar patrones críticos
            for line_num, line in enumerate(lines, 1):
                for pattern, description in critical_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        issues.append({
                            'severity': 'CRITICAL',
                            'line': line_num,
                            'issue': description,
                            'code': line.strip()
                        })
                        
                for pattern, description in warning_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        issues.append({
                            'severity': 'WARNING',
                            'line': line_num,
                            'issue': description,
                            'code': line.strip()
                        })
            
            # Verificar que use password_security si maneja passwords
            if 'password' in content.lower() and 'hash' in content.lower():
                if 'from rexus.utils.password_security' not in content:
                    if 'import password_security' not in content:
                        issues.append({
                            'severity': 'WARNING',
                            'line': 0,
                            'issue': 'Script maneja passwords pero no usa password_security.py',
                            'code': 'Missing import'
                        })
            
        except Exception as e:
            issues.append({
                'severity': 'ERROR',
                'line': 0,
                'issue': f'Error leyendo archivo: {e}',
                'code': ''
            })
            
        return issues
    
    def scan_maintenance_scripts(self):
        """Escanea todos los scripts de mantenimiento."""
        print("=== VALIDADOR DE SEGURIDAD DE CONTRASEÑAS ===")
        print("Escaneando scripts de mantenimiento...\n")
        
        # Directorios a escanear
        scan_dirs = [
            project_root / 'tools' / 'maintenance',
            project_root / 'tools' / 'development',
            project_root / 'scripts' / 'security',
            project_root / 'tools' / 'development' / 'setup',
            project_root / 'tools' / 'development' / 'testing',
        ]
        
        for scan_dir in scan_dirs:
            if not scan_dir.exists():
                continue
                
            print(f"Escaneando: {scan_dir}")
            
            for py_file in scan_dir.rglob('*.py'):
                if py_file.name.startswith('.') or '__pycache__' in str(py_file):
                    continue
                    
                self.files_checked += 1
                file_issues = self.scan_file_for_security_issues(py_file)
                
                if file_issues:
                    self.issues.append({
                        'file': str(py_file.relative_to(project_root)),
                        'issues': file_issues
                    })
                    
                    for issue in file_issues:
                        if issue['severity'] == 'CRITICAL':
                            self.critical_issues += 1
                        elif issue['severity'] == 'WARNING':
                            self.warnings += 1
    
    def generate_report(self):
        """Genera reporte de seguridad."""
        print(f"\n{'='*80}")
        print("REPORTE DE SEGURIDAD DE CONTRASEÑAS")
        print(f"{'='*80}")
        print(f"Archivos escaneados: {self.files_checked}")
        print(f"Issues críticos: {self.critical_issues}")
        print(f"Advertencias: {self.warnings}")
        print()
        
        if not self.issues:
            print("[OK] NO SE ENCONTRARON PROBLEMAS DE SEGURIDAD")
            print("Todos los scripts de mantenimiento están seguros.")
            return True
        
        # Mostrar issues por archivo
        for file_data in self.issues:
            print(f"ARCHIVO: {file_data['file']}")
            print("-" * 60)
            
            for issue in file_data['issues']:
                icon = "[CRITICAL]" if issue['severity'] == 'CRITICAL' else "[WARNING]" if issue['severity'] == 'WARNING' else "[INFO]"
                print(f"{icon} {issue['severity']}: {issue['issue']}")
                if issue['line'] > 0:
                    print(f"   Linea {issue['line']}: {issue['code']}")
                print()
        
        print(f"{'='*80}")
        if self.critical_issues > 0:
            print("[ERROR] SE ENCONTRARON VULNERABILIDADES CRITICAS")
            print("ACCION REQUERIDA: Corregir todos los issues criticos antes de continuar")
            return False
        else:
            print("[OK] NO HAY VULNERABILIDADES CRITICAS")
            if self.warnings > 0:
                print(f"[INFO] Se encontraron {self.warnings} advertencias que pueden ser revisadas")
            return True
    
    def validate_password_security_usage(self):
        """Valida que password_security.py esté bien configurado."""
        print(f"\n{'='*60}")
        print("VALIDACIÓN DE MÓDULO PASSWORD_SECURITY")
        print(f"{'='*60}")
        
        password_security_file = project_root / 'rexus' / 'utils' / 'password_security.py'
        
        if not password_security_file.exists():
            print("[CRITICAL] password_security.py no encontrado")
            return False
        
        try:
            from rexus.utils.password_security import (
                hash_password_secure, 
                verify_password_secure,
                check_password_needs_rehash
            )
            
            # Test básico
            test_password = "TestPassword123!"
            hashed = hash_password_secure(test_password)
            
            if verify_password_secure(test_password, hashed):
                print("[OK] password_security.py funciona correctamente")
                print(f"   Metodo detectado: {hashed.split('$')[0] if '$' in hashed else 'legacy'}")
                
                # Verificar si necesita rehash para SHA256
                legacy_hash = "a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3"  # "hello" en SHA256
                needs_rehash = check_password_needs_rehash(legacy_hash)
                if needs_rehash:
                    print("[OK] Deteccion de SHA256 legacy funciona correctamente")
                
                return True
            else:
                print("[CRITICAL] password_security.py no verifica contrasenas correctamente")
                return False
                
        except Exception as e:
            print(f"[CRITICAL] Error importando password_security.py: {e}")
            return False

def main():
    """Función principal."""
    validator = SecurityValidator()
    
    # Escanear scripts
    validator.scan_maintenance_scripts()
    
    # Generar reporte
    scripts_secure = validator.generate_report()
    
    # Validar módulo password_security
    module_secure = validator.validate_password_security_usage()
    
    # Resultado final
    print(f"\n{'='*80}")
    if scripts_secure and module_secure:
        print("[SUCCESS] VALIDACION EXITOSA: Sistema de contrasenas seguro")
        print("\n[COMPLETED] ACCIONES COMPLETADAS:")
        print("- Scripts de mantenimiento revisados")
        print("- Sistema password_security.py validado")
        print("- Sin vulnerabilidades criticas detectadas")
        sys.exit(0)
    else:
        print("[ERROR] VALIDACION FALLIDA: Se requieren correcciones")
        print("\n[TODO] ACCIONES REQUERIDAS:")
        if not scripts_secure:
            print("- Corregir vulnerabilidades en scripts de mantenimiento")
        if not module_secure:
            print("- Corregir modulo password_security.py")
        sys.exit(1)

if __name__ == "__main__":
    main()