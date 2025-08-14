#!/usr/bin/env python3
"""
Dependency Security Audit - Rexus.app

Auditoría completa de seguridad de dependencias del proyecto.
Identifica vulnerabilidades conocidas y versiones desactualizadas.
"""

import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import re


class DependencySecurityAuditor:
    """Auditor de seguridad para dependencias del proyecto."""

    def __init__(self, requirements_file: str = "requirements.txt"):
        """
        Inicializa el auditor.

        Args:
            requirements_file: Archivo de requirements a auditar
        """
        self.requirements_file = Path(requirements_file)
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "dependencies_analyzed": 0,
            "vulnerabilities_found": [],
            "outdated_packages": [],
            "security_recommendations": [],
            "compliance_status": "unknown"
        }

    def run_full_audit(self) -> Dict:
        """
        Ejecuta auditoría completa de dependencias.

        Returns:
            Diccionario con resultados de la auditoría
        """
        print("[LOCK] INICIANDO AUDITORÍA DE SEGURIDAD DE DEPENDENCIAS")
        print("=" * 60)

        # 1. Analizar archivo requirements.txt
        dependencies = self._parse_requirements()
        self.report["dependencies_analyzed"] = len(dependencies)

        print(f"📦 Dependencias encontradas: {len(dependencies)}")

        # 2. Verificar vulnerabilidades conocidas
        vulnerabilities = self._check_known_vulnerabilities(dependencies)
        self.report["vulnerabilities_found"] = vulnerabilities

        # 3. Verificar versiones desactualizadas
        outdated = self._check_outdated_packages(dependencies)
        self.report["outdated_packages"] = outdated

        # 4. Verificar configuración de seguridad
        security_config = self._check_security_configuration(dependencies)
        self.report["security_recommendations"].extend(security_config)

        # 5. Generar recomendaciones específicas
        recommendations = self._generate_security_recommendations()
        self.report["security_recommendations"].extend(recommendations)

        # 6. Evaluar compliance de seguridad
        self.report["compliance_status"] = self._evaluate_security_compliance()

        return self.report

    def _parse_requirements(self) -> List[Dict[str, str]]:
        """
        Parsea el archivo requirements.txt.

        Returns:
            Lista de dependencias con nombre y versión
        """
        dependencies = []

        if not self.requirements_file.exists():
            print(f"[WARN]  Archivo {self.requirements_file} no encontrado")
            return dependencies

        with open(self.requirements_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()

                # Saltar comentarios y líneas vacías
                if not line or line.startswith('#'):
                    continue

                # Parsear dependencia
                dependency = self._parse_dependency_line(line, line_num)
                if dependency:
                    dependencies.append(dependency)

        return dependencies

    def _parse_dependency_line(self,
line: str,
        line_num: int) -> Optional[Dict[str,
        str]]:
        """
        Parsea una línea de dependencia.

        Args:
            line: Línea del requirements.txt
            line_num: Número de línea

        Returns:
            Diccionario con información de la dependencia
        """
        # Remover comentarios inline
        line = line.split('#')[0].strip()

        # Patrones comunes de versioning
        patterns = [
            r'^([a-zA-Z0-9_-]+)>=([^,<>!\s]+)',  # package>=1.0.0
            r'^([a-zA-Z0-9_-]+)==([^,<>!\s]+)',  # package==1.0.0
            r'^([a-zA-Z0-9_-]+)~=([^,<>!\s]+)',  # package~=1.0.0
            r'^([a-zA-Z0-9_-]+)>([^,<>!\s]+)',   # package>1.0.0
            r'^([a-zA-Z0-9_-]+)<([^,<>!\s]+)',   # package<2.0.0
            r'^([a-zA-Z0-9_-]+)\[([^\]]+)\]>=([^,<>!\s]+)',  # package[extra]>=1.0.0
            r'^([a-zA-Z0-9_-]+)$'                # package (sin versión)
        ]

        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                groups = match.groups()
                name = groups[0]

                # Determinar versión
                if len(groups) >= 2:
                    # Si hay extras como [pil], tomar la versión del grupo correcto
                    version = groups[-1] if len(groups) > 2 else groups[1]
                else:
                    version = "unspecified"

                return {
                    "name": name,
                    "version": version,
                    "line_number": line_num,
                    "raw_line": line
                }

        print(f"[WARN]  No se pudo parsear línea {line_num}: {line}")
        return None

    def _check_known_vulnerabilities(self, dependencies: List[Dict]) -> List[Dict]:
        """
        Verifica vulnerabilidades conocidas usando pip-audit si está disponible.

        Args:
            dependencies: Lista de dependencias

        Returns:
            Lista de vulnerabilidades encontradas
        """
        print("\n🔍 Verificando vulnerabilidades conocidas...")

        vulnerabilities = []

        # Verificar si pip-audit está disponible
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "show", "pip-audit"],
                capture_output=True, text=True, timeout=10
            )

            if result.returncode != 0:
                print("[WARN]  pip-audit no está instalado")
                print("   Instalar con: pip install pip-audit")

                # Verificaciones manuales para paquetes críticos
                vulnerabilities.extend(self._manual_vulnerability_checks(dependencies))

                return vulnerabilities

            # Ejecutar pip-audit
            print("   Ejecutando pip-audit...")
            result = subprocess.run(
                [sys.executable, "-m", "pip-audit", "--format=json"],
                capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                try:
                    audit_data = json.loads(result.stdout)
                    for vuln in audit_data.get("vulnerabilities", []):
                        vulnerabilities.append({
                            "package": vuln.get("package"),
                            "version": vuln.get("installed_version"),
                            "vulnerability_id": vuln.get("id"),
                            "description": vuln.get("description"),
                            "fix_versions": vuln.get("fix_versions", []),
                            "severity": "unknown"
                        })
                except json.JSONDecodeError:
                    print("[WARN]  Error parsing pip-audit output")

            print(f"   Vulnerabilidades encontradas: {len(vulnerabilities)}")

        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            print(f"[WARN]  Error ejecutando pip-audit: {e}")
            vulnerabilities.extend(self._manual_vulnerability_checks(dependencies))

        return vulnerabilities

    def _manual_vulnerability_checks(self, dependencies: List[Dict]) -> List[Dict]:
        """
        Verificaciones manuales de vulnerabilidades para paquetes críticos.

        Args:
            dependencies: Lista de dependencias

        Returns:
            Lista de vulnerabilidades potenciales
        """
        vulnerabilities = []

        # Diccionario de versiones mínimas recomendadas por seguridad
        security_minimums = {
            "cryptography": "42.0.0",
            "requests": "2.31.0",
            "pillow": "10.0.0",
            "pyjwt": "2.4.0",
            "sqlalchemy": "2.0.0",
            "pyodbc": "4.0.34",
            "bcrypt": "4.0.0",
            "pydantic": "2.0.0",
            "httpx": "0.24.0"
        }

        for dep in dependencies:
            package_name = dep["name"].lower()
            version = dep["version"]

            if package_name in security_minimums:
                min_version = security_minimums[package_name]

                if version != "unspecified" and \
                    self._is_version_older(version, min_version):
                    vulnerabilities.append({
                        "package": dep["name"],
                        "version": version,
                        "vulnerability_id": f"MANUAL_CHECK_{package_name.upper()}",
                        "description": f"Version may contain known vulnerabilities. Minimum recommended: {min_version}",
                        "fix_versions": [f">={min_version}"],
                        "severity": "medium"
                    })

        return vulnerabilities

    def _is_version_older(self, current: str, minimum: str) -> bool:
        """
        Compara versiones de forma simplificada.

        Args:
            current: Versión actual
            minimum: Versión mínima requerida

        Returns:
            True si current es menor que minimum
        """
        try:
            current_parts = [int(x) for x in current.split('.')]
            minimum_parts = [int(x) for x in minimum.split('.')]

            # Normalizar longitudes
            max_len = max(len(current_parts), len(minimum_parts))
            current_parts.extend([0] * (max_len - len(current_parts)))
            minimum_parts.extend([0] * (max_len - len(minimum_parts)))

            return current_parts < minimum_parts

        except ValueError:
            # Si no se puede parsear, asumir que es antigua
            return True

    def _check_outdated_packages(self, dependencies: List[Dict]) -> List[Dict]:
        """
        Verifica paquetes desactualizados.

        Args:
            dependencies: Lista de dependencias

        Returns:
            Lista de paquetes desactualizados
        """
        print("\n📦 Verificando paquetes desactualizados...")

        outdated = []

        # Esta verificación requeriría acceso a PyPI o ejecución de pip list --outdated
        # Por simplicidad, documentamos el proceso
        print("   Para verificar paquetes desactualizados ejecutar:")
        print("   pip list --outdated --format=json")

        return outdated

    def _check_security_configuration(self, dependencies: List[Dict]) -> List[str]:
        """
        Verifica configuración de seguridad en las dependencias.

        Args:
            dependencies: Lista de dependencias

        Returns:
            Lista de recomendaciones de seguridad
        """
        recommendations = []

        # Verificar presencia de paquetes de seguridad críticos
        security_packages = {"cryptography", "bcrypt", "pyjwt"}
        found_security = {dep["name"].lower() for dep in dependencies}

        missing_security = security_packages - found_security
        if missing_security:
            recommendations.append(f"Considerar añadir paquetes de seguridad: {', '.join(missing_security)}")

        # Verificar versionado adecuado
        unversioned = [dep for dep in dependencies if dep["version"] == "unspecified"]
        if unversioned:
            recommendations.append(f"Fijar versiones para: {', '.join(d['name'] for d in unversioned)}")

        return recommendations

    def _generate_security_recommendations(self) -> List[str]:
        """
        Genera recomendaciones específicas de seguridad.

        Returns:
            Lista de recomendaciones
        """
        recommendations = [
            "Actualizar regularmente las dependencias de seguridad",
            "Usar herramientas como pip-audit para monitoreo continuo",
            "Implementar análisis automático de dependencias en CI/CD",
            "Revisar y aprobar nuevas dependencias antes de añadir",
            "Mantener un inventario actualizado de dependencias críticas"
        ]

        return recommendations

    def _evaluate_security_compliance(self) -> str:
        """
        Evalúa el nivel de compliance de seguridad.

        Returns:
            Estado de compliance: excellent, good, needs_improvement, critical
        """
        vuln_count = len(self.report["vulnerabilities_found"])
        outdated_count = len(self.report["outdated_packages"])

        if vuln_count == 0 and outdated_count == 0:
            return "excellent"
        elif vuln_count <= 2 and outdated_count <= 5:
            return "good"
        elif vuln_count <= 5 and outdated_count <= 10:
            return "needs_improvement"
        else:
            return "critical"

    def generate_report(self) -> str:
        """
        Genera reporte formateado de la auditoría.

        Returns:
            Reporte en formato texto
        """
        lines = [
            "[LOCK] REPORTE DE AUDITORÍA DE DEPENDENCIAS - REXUS.APP",
            "=" * 60,
            f"Fecha: {self.report['timestamp'][:19]}",
            f"Dependencias analizadas: {self.report['dependencies_analyzed']}",
            ""
        ]

        # Estado de compliance
        compliance_icons = {
            "excellent": "🟢 EXCELENTE",
            "good": "🟡 BUENO",
            "needs_improvement": "🟠 NECESITA MEJORAS",
            "critical": "🔴 CRÍTICO"
        }

        status = self.report['compliance_status']
        lines.append(f"Estado de Seguridad: {compliance_icons.get(status, '❓ DESCONOCIDO')}")
        lines.append("")

        # Vulnerabilidades
        vulns = self.report["vulnerabilities_found"]
        lines.append(f"🚨 VULNERABILIDADES ENCONTRADAS: {len(vulns)}")
        lines.append("-" * 40)

        if vulns:
            for vuln in vulns:
                lines.append(f"• {vuln['package']} v{vuln['version']}")
                lines.append(f"  ID: {vuln['vulnerability_id']}")
                lines.append(f"  Descripción: {vuln['description'][:100]}...")
                if vuln['fix_versions']:
                    lines.append(f"  Solución: Actualizar a {', '.join(vuln['fix_versions'])}")
                lines.append("")
        else:
            lines.append("[CHECK] No se encontraron vulnerabilidades críticas")

        lines.append("")

        # Paquetes desactualizados
        outdated = self.report["outdated_packages"]
        lines.append(f"📦 PAQUETES DESACTUALIZADOS: {len(outdated)}")
        lines.append("-" * 30)

        if outdated:
            for pkg in outdated:
                lines.append(f"• {pkg.get('name', 'unknown')}: {pkg.get('current', 'unknown')} → {pkg.get('latest', 'unknown')}")
        else:
            lines.append("ℹ️  Verificación de paquetes desactualizados pendiente")

        lines.append("")

        # Recomendaciones
        recs = self.report["security_recommendations"]
        lines.append(f"💡 RECOMENDACIONES DE SEGURIDAD: {len(recs)}")
        lines.append("-" * 35)

        for i, rec in enumerate(recs, 1):
            lines.append(f"{i}. {rec}")

        lines.extend([
            "",
            "🔧 ACCIONES RECOMENDADAS:",
            "1. pip install pip-audit (para auditorías automáticas)",
            "2. pip list --outdated (verificar paquetes desactualizados)",
            "3. Actualizar paquetes críticos de seguridad",
            "4. Implementar verificaciones automáticas en CI/CD",
            "5. Revisar y aprobar cambios de dependencias",
            ""
        ])

        return "\n".join(lines)

    def save_report(self, filename: str = None) -> str:
        """
        Guarda el reporte en un archivo.

        Args:
            filename: Nombre del archivo (opcional)

        Returns:
            Nombre del archivo guardado
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"dependency_security_audit_{timestamp}.txt"

        report_text = self.generate_report()

        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report_text)

        return filename


def main():
    """Función principal para ejecutar la auditoría."""
    print("[LOCK] AUDITORÍA DE SEGURIDAD DE DEPENDENCIAS - REXUS.APP")

    # Buscar archivo requirements.txt
    req_file = "requirements.txt"
    if not Path(req_file).exists():
        print(f"[ERROR] Archivo {req_file} no encontrado")
        print("   Ejecutar desde el directorio raíz del proyecto")
        return 1

    # Ejecutar auditoría
    auditor = DependencySecurityAuditor(req_file)
    results = auditor.run_full_audit()

    # Mostrar reporte
    print("\n" + auditor.generate_report())

    # Guardar reporte
    report_file = auditor.save_report()
    print(f"📄 Reporte guardado en: {report_file}")

    # Código de salida basado en compliance
    status = results["compliance_status"]
    if status == "critical":
        return 2
    elif status == "needs_improvement":
        return 1
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())
