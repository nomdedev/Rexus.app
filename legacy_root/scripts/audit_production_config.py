#!/usr/bin/env python3
"""
Script para auditar y corregir problemas de configuración para producción
Detecta credenciales hardcodeadas, configuraciones de debug, etc.
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Any
import shutil
from datetime import datetime

class ProductionConfigAuditor:
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.issues = []
        self.fixes_applied = []

    def detect_hardcoded_credentials(self) -> List[Dict]:
        """Detecta credenciales hardcodeadas en código fuente."""
        credentials = []

        # Patrones de credenciales peligrosas (excluyendo ejemplos obvios)
        credential_patterns = [
            (r'password\s*=\s*["\'](?!(?:password|test|example|demo|default|123|admin|root))[^"\']{4,}["\']', 'Password hardcodeado'),
            (r'pwd\s*=\s*["\'](?!(?:pwd|test|example|demo|default))[^"\']{3,}["\']', 'Password hardcodeado'),
            (r'api_key\s*=\s*["\'](?!(?:api_key|test|example|demo|your_key))[^"\']{10,}["\']', 'API Key hardcodeada'),
            (r'secret\s*=\s*["\'](?!(?:secret|test|example|demo|your_secret))[^"\']{8,}["\']', 'Secret hardcodeado'),
            (r'token\s*=\s*["\'](?!(?:token|test|example|demo|your_token))[^"\']{10,}["\']', 'Token hardcodeado'),
            (r'connectionString\s*=\s*["\'][^"\']+;[^"\']*password[^"\']*["\']', 'Connection string con password'),
        ]

        for py_file in self.root_path.rglob("*.py"):
            # Saltar archivos no relevantes
            if any(skip in str(py_file) for skip in ['__pycache__',
'.pyc',
                'backup',
                '.venv',
                'test']):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                for i, line in enumerate(content.split('\n'), 1):
                    for pattern, description in credential_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            # Filtrar falsos positivos
                            if not any(fp in line.lower() for fp in ['example', 'test', 'demo', 'placeholder', 'todo']):
                                credentials.append({
                                    'file': str(py_file.relative_to(self.root_path)),
                                    'line': i,
                                    'content': line.strip(),
                                    'type': description,
                                    'severity': 'HIGH'
                                })

            except Exception:
                continue

        return credentials

    def detect_debug_configurations(self) -> List[Dict]:
        """Detecta configuraciones de debug que no deberían ir a producción."""
        debug_issues = []

        debug_patterns = [
            (r'DEBUG\s*=\s*True', 'Modo DEBUG activado'),
            (r'debug\s*=\s*True', 'Debug flag activado'),
            (r'TESTING\s*=\s*True', 'Modo TESTING activado'),
            (r'print\s*\(', 'Print statement (debería usar logging)'),
            (r'console\.log\s*\(', 'Console.log encontrado'),
            (r'pdb\.set_trace\(\)', 'Breakpoint de debug'),
            (r'breakpoint\(\)', 'Breakpoint de Python'),
        ]

        for py_file in self.root_path.rglob("*.py"):
            if any(skip in str(py_file) for skip in ['__pycache__',
'.pyc',
                'backup',
                '.venv',
                'test']):
                continue

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                for i, line in enumerate(content.split('\n'), 1):
                    for pattern, description in debug_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            # Filtrar líneas comentadas y logging válido
                            stripped = line.strip()
                            if not stripped.startswith('#') and 'logging.' not in line and 'logger.' not in line:
                                debug_issues.append({
                                    'file': str(py_file.relative_to(self.root_path)),
                                    'line': i,
                                    'content': line.strip(),
                                    'type': description,
                                    'severity': 'MEDIUM'
                                })

            except Exception:
                continue

        return debug_issues

    def audit_config_files(self) -> List[Dict]:
        """Audita archivos de configuración."""
        config_issues = []

        # Verificar archivos de configuración críticos
        config_files = [
            'config/rexus_config.json',
            'config/secure_config.json',
            'config/config_manager.py'
        ]

        for config_file in config_files:
            config_path = self.root_path / config_file

            if not config_path.exists():
                config_issues.append({
                    'file': config_file,
                    'line': 0,
                    'content': 'Archivo faltante',
                    'type': 'Archivo de configuración crítico faltante',
                    'severity': 'HIGH'
                })
                continue

            if config_file.endswith('.json'):
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config_data = json.load(f)

                    # Verificar campos críticos según el archivo
                    if 'rexus_config.json' in config_file:
                        required_fields = ['db_server', 'db_name', 'sistema_version']
                        for field in required_fields:
                            if not config_data.get(field):
                                config_issues.append({
                                    'file': config_file,
                                    'line': 0,
                                    'content': f'Campo {field} vacío o faltante',
                                    'type': 'Campo de configuración crítico faltante',
                                    'severity': 'HIGH'
                                })

                    # Buscar credenciales en configuración
                    config_str = json.dumps(config_data, indent=2)
                    for line_num, line in enumerate(config_str.split('\n'), 1):
                        if re.search(r'password|secret|key|token', line, re.IGNORECASE):
                            if not any(safe in line.lower() for safe in ['null',
'""',
                                "''",
                                'placeholder']):
                                config_issues.append({
                                    'file': config_file,
                                    'line': line_num,
                                    'content': line.strip(),
                                    'type': 'Posible credencial en configuración',
                                    'severity': 'HIGH'
                                })

                except json.JSONDecodeError:
                    config_issues.append({
                        'file': config_file,
                        'line': 0,
                        'content': 'JSON inválido',
                        'type': 'Archivo de configuración corrupto',
                        'severity': 'HIGH'
                    })
                except Exception as e:
                    config_issues.append({
                        'file': config_file,
                        'line': 0,
                        'content': str(e),
                        'type': 'Error leyendo configuración',
                        'severity': 'MEDIUM'
                    })

        return config_issues

    def create_production_config_template(self):
        """Crea template de configuración para producción."""
        production_config = {
            "production_ready_checklist": {
                "database": {
                    "use_connection_pooling": True,
                    "connection_timeout": 30,
                    "max_connections": 50,
                    "enable_ssl": True
                },
                "security": {
                    "use_environment_variables": True,
                    "enable_encryption": True,
                    "session_timeout": 3600,
                    "password_policy": {
                        "min_length": 8,
                        "require_uppercase": True,
                        "require_numbers": True,
                        "require_special": True
                    }
                },
                "logging": {
                    "level": "INFO",
                    "enable_file_logging": True,
                    "log_retention_days": 30,
                    "enable_audit_trail": True
                },
                "performance": {
                    "enable_caching": True,
                    "cache_ttl": 300,
                    "enable_compression": True,
                    "max_request_size": "10MB"
                },
                "monitoring": {
                    "enable_health_checks": True,
                    "enable_metrics": True,
                    "alert_on_errors": True
                }
            },
            "environment_variables_required": [
                "REXUS_DB_SERVER",
                "REXUS_DB_NAME",
                "REXUS_DB_USER",
                "REXUS_DB_PASSWORD",
                "REXUS_SECRET_KEY",
                "REXUS_ENVIRONMENT"
            ]
        }

        config_path = self.root_path / "config" / "production_config_template.json"
        config_path.parent.mkdir(exist_ok=True)

        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(production_config, f, indent=2, ensure_ascii=False)

        return str(config_path)

    def generate_environment_file(self):
        """Genera archivo .env template para producción."""
        env_template = """# Configuración de Producción - Rexus.app
# IMPORTANTE: Este archivo contiene variables sensibles
# NO subir a control de versiones

# Base de datos
REXUS_DB_SERVER=your_production_server
REXUS_DB_NAME=your_production_db
REXUS_DB_USER=your_db_user
REXUS_DB_PASSWORD=your_secure_password

# Seguridad
REXUS_SECRET_KEY=your_256_bit_secret_key
REXUS_ENCRYPTION_KEY=your_encryption_key

# Entorno
REXUS_ENVIRONMENT=production
REXUS_DEBUG=false
REXUS_LOG_LEVEL=INFO

# APIs externas (si aplica)
REXUS_API_KEY=your_api_key
REXUS_API_SECRET=your_api_secret

# Configuración de email (si aplica)
REXUS_SMTP_SERVER=your_smtp_server
REXUS_SMTP_PORT=587
REXUS_SMTP_USER=your_email
REXUS_SMTP_PASSWORD=your_email_password

# Configuración de seguridad adicional
REXUS_SESSION_TIMEOUT=3600
REXUS_MAX_LOGIN_ATTEMPTS=5
REXUS_PASSWORD_RESET_TIMEOUT=1800
"""

        env_path = self.root_path / ".env.production.template"
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(env_template)

        return str(env_path)

    def run_complete_audit(self) -> Dict[str, Any]:
        """Ejecuta auditoría completa de configuración."""
        print("🔍 Iniciando auditoría de configuración para producción...")

        # Ejecutar auditorías
        credentials = self.detect_hardcoded_credentials()
        debug_configs = self.detect_debug_configurations()
        config_issues = self.audit_config_files()

        # Crear archivos de configuración de producción
        production_config = self.create_production_config_template()
        env_template = self.generate_environment_file()

        # Clasificar problemas
        high_severity = [issue for issue in credentials + config_issues if issue['severity'] == 'HIGH']
        medium_severity = [issue for issue in debug_configs + config_issues if issue['severity'] == 'MEDIUM']

        total_issues = len(high_severity) + len(medium_severity)

        print(f"📊 Problemas de configuración encontrados: {total_issues}")
        print(f"• Severidad ALTA: {len(high_severity)}")
        print(f"• Severidad MEDIA: {len(medium_severity)}")

        # Mostrar problemas críticos
        if high_severity:
            print(f"\n🚨 PROBLEMAS CRÍTICOS (ALTA SEVERIDAD):")
            for issue in high_severity[:10]:
                print(f"  • {issue['file']}:{issue['line']} - {issue['type']}")
            if len(high_severity) > 10:
                print(f"  • ... y {len(high_severity) - 10} más")

        print(f"\n📄 Archivos de configuración creados:")
        print(f"  • {production_config}")
        print(f"  • {env_template}")

        return {
            'total_issues': total_issues,
            'high_severity': len(high_severity),
            'medium_severity': len(medium_severity),
            'credentials_issues': len(credentials),
            'debug_issues': len(debug_configs),
            'config_issues': len(config_issues),
            'production_ready': len(high_severity) == 0,
            'details': {
                'credentials': credentials,
                'debug_configs': debug_configs,
                'config_issues': config_issues
            }
        }

def main():
    print("🛠️ AUDITOR DE CONFIGURACIÓN PARA PRODUCCIÓN - REXUS.APP")
    print("=" * 60)

    auditor = ProductionConfigAuditor()
    report = auditor.run_complete_audit()

    print(f"\n📊 RESUMEN FINAL:")
    if report['production_ready']:
        print(f"✅ Configuración lista para producción")
    else:
        print(f"❌ {report['high_severity']} problemas críticos requieren corrección")

    print(f"\n📋 ACCIONES REQUERIDAS:")
    if report['credentials_issues'] > 0:
        print(f"1. Mover {report['credentials_issues']} credenciales a variables de entorno")
    if report['debug_issues'] > 0:
        print(f"2. Remover {report['debug_issues']} configuraciones de debug")
    if report['config_issues'] > 0:
        print(f"3. Corregir {report['config_issues']} problemas de configuración")

    print(f"\n🔧 PRÓXIMOS PASOS:")
    print(f"1. Configurar variables de entorno usando .env.production.template")
    print(f"2. Revisar production_config_template.json")
    print(f"3. Eliminar credenciales hardcodeadas del código")
    print(f"4. Configurar logging apropiado para producción")

    return report

if __name__ == "__main__":
    main()
