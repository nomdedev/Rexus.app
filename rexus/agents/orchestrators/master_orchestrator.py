"""
Master Orchestrator - Orquestador Maestro para auditoría exhaustiva
Coordina todos los agentes para realizar un análisis completo de Rexus.app
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import logging
import asyncio

# Agregar ruta del proyecto
root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root))

from rexus.agents.orchestrators.orchestrator import AgentOrchestrator
from rexus.agents.module_auditors.audit_agent import AuditAgent
from rexus.agents.pixel_bridge import get_pixel_bridge, PixelAgentsBridge

logger = logging.getLogger(__name__)


class MasterOrchestrator(AgentOrchestrator):
    """
    Orquestador Maestro que coordina auditoría exhaustiva de Rexus.app

    Responsabilidades:
    - Analizar la estructura completa del proyecto
    - Coordinar agentes especializados por módulo
    - Generar reporte consolidado de auditoría
    - Identificar problemas críticos y áreas de mejora
    - Proporcionar roadmap de mejoras prioritarias
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Inicializar orquestador maestro"""
        super().__init__(name="MasterOrchestrator")
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.pixel_bridge = get_pixel_bridge()
        self.audit_findings = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }
        self.modules_structure = {}
        self.code_metrics = {}

    async def perform_comprehensive_audit(
        self,
        agent_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Realizar auditoría exhaustiva de toda la aplicación

        Args:
            agent_ids: Lista de agentes a usar (todos si es None)

        Returns:
            Resultados completos de auditoría
        """
        # Iniciar tarea principal en Pixel Agents
        main_task = self.pixel_bridge.start_task(
            "master-orchestrator",
            "🎯 Iniciando Auditoría Exhaustiva de Rexus.app",
            "audit"
        )

        self.pixel_bridge.update_progress(main_task, "Analizando estructura del proyecto", 5)

        # Fase 1: Análisis de estructura del proyecto
        structure_analysis = await self._analyze_project_structure()

        self.pixel_bridge.update_progress(main_task, "Auditoría de módulos especializados", 20)

        # Fase 2: Ejecutar auditoría de cada módulo
        module_reports = await self._audit_all_modules(agent_ids)

        self.pixel_bridge.update_progress(main_task, "Analizando calidad de código", 60)

        # Fase 3: Análisis de calidad de código global
        code_quality = await self._analyze_global_code_quality()

        self.pixel_bridge.update_progress(main_task, "Verificando seguridad", 75)

        # Fase 4: Análisis de seguridad
        security_analysis = await self._analyze_security()

        self.pixel_bridge.update_progress(main_task, "Verificando rendimiento", 85)

        # Fase 5: Análisis de rendimiento
        performance_analysis = await self._analyze_performance()

        self.pixel_bridge.update_progress(main_task, "Generando reporte consolidado", 95)

        # Fase 6: Consolidar resultados
        final_report = await self._generate_comprehensive_report({
            'structure': structure_analysis,
            'modules': module_reports,
            'code_quality': code_quality,
            'security': security_analysis,
            'performance': performance_analysis
        })

        # Completar tarea
        report_summary = self._create_report_summary(final_report)
        self.pixel_bridge.complete_task(main_task, report_summary)

        return final_report

    async def _analyze_project_structure(self) -> Dict[str, Any]:
        """Analizar estructura del proyecto"""
        self.logger.info("Analizando estructura del proyecto...")

        modules_dir = self.project_root / "rexus" / "modules"
        structure = {
            'modules_found': [],
            'total_files': 0,
            'total_lines': 0,
            'frameworks_detected': [],
            'patterns': {}
        }

        if modules_dir.exists():
            for module_path in modules_dir.iterdir():
                if module_path.is_dir() and not module_path.name.startswith('_'):
                    module_info = await self._analyze_module_structure(module_path)
                    structure['modules_found'].append(module_info)
                    structure['total_files'] += module_info['file_count']
                    structure['total_lines'] += module_info.get('line_count', 0)

        # Detectar frameworks y tecnologías
        structure['frameworks_detected'] = await self._detect_frameworks()

        return structure

    async def _analyze_module_structure(self, module_path: Path) -> Dict[str, Any]:
        """Analizar estructura de un módulo específico"""
        module_name = module_path.name
        file_count = 0
        line_count = 0

        for file_path in module_path.rglob("*.py"):
            file_count += 1
            try:
                line_count += len(file_path.read_text(encoding='utf-8', errors='ignore').splitlines())
            except:
                pass

        return {
            'name': module_name,
            'path': str(module_path),
            'file_count': file_count,
            'line_count': line_count
        }

    async def _detect_frameworks(self) -> List[str]:
        """Detectar frameworks y tecnologías utilizadas"""
        frameworks = []
        root = self.project_root

        # Verificar requirements.txt
        req_file = root / "requirements.txt"
        requirements_content = ""
        if req_file.exists():
            try:
                requirements_content = req_file.read_text(encoding='utf-8', errors='ignore').lower()
            except:
                pass

        # Detectar Flask
        flask_files = list((root / "rexus/modules").rglob("*flask*")) if (root / "rexus/modules").exists() else []
        if flask_files or "flask" in requirements_content:
            frameworks.append("Flask")

        # Detectar SQLAlchemy
        if "sqlalchemy" in requirements_content:
            frameworks.append("SQLAlchemy")

        # Detectar WTForms
        if "wtforms" in requirements_content:
            frameworks.append("WTForms")

        # Detectar otras librerías comunes
        if "pytest" in requirements_content:
            frameworks.append("PyTest")

        if "werkzeug" in requirements_content:
            frameworks.append("Werkzeug")

        return frameworks

    async def _audit_all_modules(self, agent_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Auditar todos los módulos usando agentes especializados"""
        self.logger.info("Auditoría de módulos...")

        agents_to_audit = agent_ids or list(self.registered_agents.keys())
        module_reports = {}

        for agent_id in agents_to_audit:
            if agent_id not in self.registered_agents:
                continue

            agent = self.registered_agents[agent_id]

            # Actualizar progreso en Pixel Agents
            self.pixel_bridge.update_progress(
                self.pixel_bridge.start_task(
                    agent_id,
                    f"Auditando {agent_id}",
                    "analyze"
                ),
                f"Análisis de {agent_id}",
                50
            )

            try:
                # Ejecutar análisis del módulo
                response = await agent.analyze(
                    target=agent.module_name,
                    context={'orchestrator': self.name}
                )

                # Generar reporte
                report = await agent.generate_report(response.metadata.get('audit_results', {}))

                # Proponer mejoras
                improvements = await agent.propose_improvements(response.metadata.get('audit_results', {}))

                module_reports[agent_id] = {
                    'status': 'completed',
                    'response': response.to_dict() if hasattr(response, 'to_dict') else str(response),
                    'report': json.loads(report) if isinstance(report, str) else report,
                    'improvements': improvements
                }

                # Clasificar hallazgos por severidad
                for improvement in improvements:
                    priority = improvement.get('prioridad', 'media').lower()
                    if priority in ['crítica', 'alta']:
                        self.audit_findings['critical'].append(improvement)
                    elif priority == 'alta':
                        self.audit_findings['high'].append(improvement)
                    elif priority == 'media':
                        self.audit_findings['medium'].append(improvement)
                    else:
                        self.audit_findings['low'].append(improvement)

            except Exception as e:
                self.logger.error(f"Error auditando {agent_id}: {e}")
                module_reports[agent_id] = {
                    'status': 'error',
                    'error': str(e)
                }

        return module_reports

    async def _analyze_global_code_quality(self) -> Dict[str, Any]:
        """Analizar calidad de código global"""
        self.logger.info("Analizando calidad de código global...")

        quality_metrics = {
            'total_python_files': 0,
            'total_lines_of_code': 0,
            'avg_lines_per_file': 0,
            'complexity_score': 0,
            'code_smells': [],
            'duplications': []
        }

        # Analizar archivos Python
        for py_file in self.project_root.rglob("*.py"):
            if 'venv' not in str(py_file) and '__pycache__' not in str(py_file):
                quality_metrics['total_python_files'] += 1
                try:
                    lines = len(py_file.read_text(encoding='utf-8', errors='ignore').splitlines())
                    quality_metrics['total_lines_of_code'] += lines
                except:
                    pass

        if quality_metrics['total_python_files'] > 0:
            quality_metrics['avg_lines_per_file'] = \
                quality_metrics['total_lines_of_code'] // quality_metrics['total_python_files']

        return quality_metrics

    async def _analyze_security(self) -> Dict[str, Any]:
        """Analizar seguridad de la aplicación"""
        self.logger.info("Analizando seguridad...")

        security_issues = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }

        # Verificar archivos con credenciales potenciales
        sensitive_patterns = ['.env', 'config.py', 'secrets.py', 'credentials.json']
        for pattern in sensitive_patterns:
            for file_path in self.project_root.rglob(pattern):
                if 'venv' not in str(file_path):
                    security_issues['medium'].append({
                        'type': 'potential_credentials_file',
                        'file': str(file_path.relative_to(self.project_root)),
                        'description': f'Archivo potencial con credenciales: {file_path.name}'
                    })

        # Verificar dependencias vulnerables
        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            # En implementación real, verificaríamos contra bases de datos de vulnerabilidades
            security_issues['low'].append({
                'type': 'dependency_scan',
                'description': 'Se recomienda ejecutar: pip-audit o safety check'
            })

        return security_issues

    async def _analyze_performance(self) -> Dict[str, Any]:
        """Analizar rendimiento de la aplicación"""
        self.logger.info("Analizando rendimiento...")

        performance_metrics = {
            'database_queries': [],
            'large_files': [],
            'optimization_opportunities': []
        }

        # Identificar archivos Python grandes (potencial optimización)
        for py_file in self.project_root.rglob("*.py"):
            if 'venv' not in str(py_file) and '__pycache__' not in str(py_file):
                try:
                    lines = len(py_file.read_text(encoding='utf-8', errors='ignore').splitlines())
                    if lines > 500:
                        performance_metrics['large_files'].append({
                            'file': str(py_file.relative_to(self.project_root)),
                            'lines': lines,
                            'recommendation': 'Considerar dividir en módulos más pequeños'
                        })
                except:
                    pass

        return performance_metrics

    async def _generate_comprehensive_report(self, audit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generar reporte consolidado de auditoría"""
        self.logger.info("Generando reporte consolidado...")

        report = {
            'audit_metadata': {
                'timestamp': datetime.now().isoformat(),
                'orchestrator': self.name,
                'project_root': str(self.project_root),
                'audit_type': 'comprehensive'
            },
            'executive_summary': self._create_executive_summary(audit_data),
            'detailed_findings': audit_data,
            'prioritized_recommendations': self._prioritize_recommendations(),
            'action_plan': self._create_action_plan()
        }

        # Guardar reporte en archivo
        reports_dir = self.project_root / "reports" / "audits"
        reports_dir.mkdir(parents=True, exist_ok=True)

        report_file = reports_dir / f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Reporte guardado en: {report_file}")

        return report

    def _create_executive_summary(self, audit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Crear resumen ejecutivo"""
        structure = audit_data.get('structure', {})
        modules = audit_data.get('modules', {})

        total_modules = len(structure.get('modules_found', []))
        completed_audits = sum(1 for m in modules.values() if m.get('status') == 'completed')

        return {
            'total_modules_analyzed': total_modules,
            'audits_completed': completed_audits,
            'audits_failed': total_modules - completed_audits,
            'critical_findings': len(self.audit_findings['critical']),
            'high_priority_findings': len(self.audit_findings['high']),
            'medium_priority_findings': len(self.audit_findings['medium']),
            'total_files_analyzed': structure.get('total_files', 0),
            'frameworks_detected': structure.get('frameworks_detected', []),
            'overall_health_score': self._calculate_health_score()
        }

    def _calculate_health_score(self) -> Dict[str, Any]:
        """Calcular score de salud del proyecto"""
        # Algoritmo simple de scoring
        base_score = 100

        # Reducir por hallazgos críticos
        base_score -= len(self.audit_findings['critical']) * 15
        base_score -= len(self.audit_findings['high']) * 10
        base_score -= len(self.audit_findings['medium']) * 5
        base_score -= len(self.audit_findings['low']) * 1

        base_score = max(0, min(100, base_score))

        # Determinar categoría
        if base_score >= 90:
            category = "Excelente"
        elif base_score >= 75:
            category = "Bueno"
        elif base_score >= 60:
            category = "Aceptable"
        elif base_score >= 40:
            category = "Necesita Mejoras"
        else:
            category = "Crítico"

        return {
            'score': base_score,
            'category': category,
            'max_score': 100
        }

    def _prioritize_recommendations(self) -> List[Dict[str, Any]]:
        """Priorizar recomendaciones"""
        all_recommendations = []

        # Combinar todos los hallazgos
        for severity, findings in self.audit_findings.items():
            for finding in findings:
                all_recommendations.append({
                    'finding': finding,
                    'severity': severity,
                    'priority_order': self._get_priority_order(severity)
                })

        # Ordenar por prioridad
        all_recommendations.sort(key=lambda x: x['priority_order'])

        return all_recommendations[:20]  # Top 20 recomendaciones

    def _get_priority_order(self, severity: str) -> int:
        """Obtener orden de prioridad numérico"""
        priority_map = {
            'critical': 0,
            'high': 1,
            'medium': 2,
            'low': 3
        }
        return priority_map.get(severity, 4)

    def _create_action_plan(self) -> Dict[str, Any]:
        """Crear plan de acción"""
        return {
            'immediate_actions': [
                {
                    'action': 'Revisar hallazgos críticos',
                    'priority': 'alta',
                    'estimated_time': '1-2 días',
                    'resources': 'Equipo de desarrollo'
                },
                {
                    'action': 'Implementar correcciones de seguridad',
                    'priority': 'crítica',
                    'estimated_time': '2-3 días',
                    'resources': 'Equipo de seguridad + desarrollo'
                }
            ],
            'short_term_goals': [
                {
                    'goal': 'Mejorar calidad de código',
                    'timeline': '2-4 semanas',
                    'metrics': ['Reducir code smells', 'Aumentar cobertura de tests']
                },
                {
                    'goal': 'Optimizar rendimiento',
                    'timeline': '3-4 semanas',
                    'metrics': ['Reducir tiempo de respuesta', 'Optimizar queries']
                }
            ],
            'long_term_goals': [
                {
                    'goal': 'Establecer cultura de calidad continua',
                    'timeline': '3-6 meses',
                    'initiatives': ['CI/CD mejorado', 'Testing automatizado', 'Code reviews']
                }
            ]
        }

    def _create_report_summary(self, report: Dict[str, Any]) -> str:
        """Crear resumen del reporte para mostrar en consola"""
        summary = report['executive_summary']
        health = summary['overall_health_score']

        return f"""
🎯 AUDITORÍA EXHAUSTIVA COMPLETADA

📊 RESUMEN EJECUTIVO:
  • Módulos analizados: {summary['total_modules_analyzed']}
  • Auditorías completadas: {summary['audits_completed']}
  • Archivos analizados: {summary['total_files_analyzed']}
  • Frameworks detectados: {', '.join(summary['frameworks_detected'])}

⚠️ HALLAZGOS:
  • Críticos: {summary['critical_findings']}
  • Alta prioridad: {summary['high_priority_findings']}
  • Media prioridad: {summary['medium_priority_findings']}

💯 SCORE DE SALUD: {health['score']}/100 - {health['category']}

📄 Reporte completo guardado en: reports/audits/
"""


async def main():
    """Ejecutar auditoría exhaustiva"""
    print("\n" + "="*80)
    print("🎯 ORQUESTADOR MAESTRO - AUDITORÍA EXHAUSTIVA")
    print("="*80 + "\n")

    # Crear orquestador
    orchestrator = MasterOrchestrator()

    # Registrar agentes de auditoría
    modules = [
        'obras', 'inventario', 'herrajes', 'vidrios', 'logística',
        'pedidos', 'compras', 'administración', 'mantenimiento',
        'auditoría', 'usuarios', 'configuración', 'notificaciones'
    ]

    print(f"[*] Registrando {len(modules)} agentes de auditoría...")
    for module_name in modules:
        agent = AuditAgent(module_name=module_name)
        agent_id = f"audit-{module_name}"
        orchestrator.register_agent(agent_id, agent)
        print(f"    ✅ {agent_id}")

    print(f"\n[OK] {len(modules)} agentes registrados\n")

    # Ejecutar auditoría exhaustiva
    print("[*] Iniciando auditoría exhaustiva...\n")

    try:
        report = await orchestrator.perform_comprehensive_audit()

        print("\n" + "="*80)
        print("✅ AUDITORÍA COMPLETADA")
        print("="*80)

        # Mostrar resumen
        summary = orchestrator._create_report_summary(report)
        print(summary)

        print("[*] Recomendaciones prioritarias:")
        recommendations = report['prioritized_recommendations'][:5]
        for i, rec in enumerate(recommendations, 1):
            finding = rec['finding']
            print(f"  {i}. [{rec['severity'].upper()}] {finding.get('título', finding.get('description', 'N/A'))}")

        print("\n[*] Próximos pasos recomendados:")
        for action in report['action_plan']['immediate_actions']:
            print(f"  • {action['action']} ({action['priority']} prioridad)")

        print("\n" + "="*80 + "\n")

    except Exception as e:
        print(f"\n[ERROR] Error durante auditoría: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[INFO] Auditoría interrumpida")
        sys.exit(0)
