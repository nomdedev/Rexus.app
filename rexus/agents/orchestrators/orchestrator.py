"""
Agent Orchestrator - Coordinación central de agentes Rexus.app
Maneja auditoria de módulos y presentación al consejo superior
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Orquestador central que coordina todos los agentes
    
    Flujo:
    1. Inicia agentes de auditoría para cada módulo
    2. Recopila resultados y reportes
    3. Genera informe consolidado para el consejo
    4. Ejecuta cambios aprobados por el consejo
    """
    
    def __init__(self, name: str = "MainOrchestrator"):
        """Inicializar orquestador"""
        self.name = name
        self.logger = logging.getLogger(f"rexus.orchestrator.{name}")
        self.registered_agents: Dict[str, Any] = {}
        self.audit_schedule = []
        self.council_approvals = {}
        
    def register_agent(self, agent_id: str, agent: Any) -> None:
        """
        Registrar un agente con el orquestador
        
        Args:
            agent_id: Identificador único del agente
            agent: Instancia del agente
        """
        self.registered_agents[agent_id] = agent
        self.logger.info(f"Agente registrado: {agent_id}")
    
    async def run_audit_cycle(
        self,
        agent_ids: Optional[List[str]] = None,
        generate_council_report: bool = True
    ) -> Dict[str, Any]:
        """
        Ejecutar ciclo de auditoría
        
        Args:
            agent_ids: IDs de agentes a auditar (todos si es None)
            generate_council_report: Generar reporte para consejo
            
        Returns:
            Resultados consolidados de auditoría
        """
        audit_results = {
            'timestamp': datetime.now().isoformat(),
            'agent_reports': {},
            'summary': None,
            'council_report': None
        }
        
        agents_to_audit = agent_ids or list(self.registered_agents.keys())
        
        self.logger.info(f"Iniciando ciclo de auditoría para {len(agents_to_audit)} agentes")
        
        # Ejecutar auditoría para cada agente
        for agent_id in agents_to_audit:
            if agent_id not in self.registered_agents:
                self.logger.warning(f"Agente no registrado: {agent_id}")
                continue
            
            agent = self.registered_agents[agent_id]
            
            try:
                # Analizar módulo
                response = await agent.analyze(
                    target=agent_id,
                    context={'orchestrator': self.name}
                )
                
                # Generar reporte
                report = await agent.generate_report(response.metadata.get('audit_results', {}))
                
                audit_results['agent_reports'][agent_id] = {
                    'response': response.to_dict(),
                    'report': report,
                    'status': 'completed'
                }
                
            except Exception as e:
                self.logger.error(f"Error auditando {agent_id}: {e}")
                audit_results['agent_reports'][agent_id] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        # Generar resumen
        audit_results['summary'] = self._generate_summary(audit_results)
        
        # Generar reporte para consejo si se solicita
        if generate_council_report:
            audit_results['council_report'] = self._generate_council_report(audit_results)
        
        return audit_results
    
    def _generate_summary(self, audit_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generar resumen de auditoría"""
        total_agents = len(audit_results['agent_reports'])
        completed = sum(
            1 for r in audit_results['agent_reports'].values()
            if r.get('status') == 'completed'
        )
        
        return {
            'total_agents_auditados': total_agents,
            'auditorías_completadas': completed,
            'auditorías_fallidas': total_agents - completed,
            'timestamp': audit_results['timestamp']
        }
    
    def _generate_council_report(self, audit_results: Dict[str, Any]) -> str:
        """
        Generar reporte para el consejo superior
        
        Este reporte contiene:
        - Resumen ejecutivo de cada módulo
        - Hallazgos críticos
        - Mejoras propuestas
        - Recomendaciones
        """
        council_report = {
            'tipo_documento': 'REPORTE_DE_CONSEJO',
            'fecha': datetime.now().isoformat(),
            'resumen_ejecutivo': audit_results.get('summary'),
            'módulos_auditados': {}
        }
        
        for agent_id, report_data in audit_results['agent_reports'].items():
            if report_data.get('status') == 'completed':
                council_report['módulos_auditados'][agent_id] = {
                    'estado': 'Auditado',
                    'reporte_disponible': True
                }
        
        council_report['instrucciones'] = (
            "Revise los hallazgos de cada módulo. "
            "Apruebe o rechace las mejoras propuestas. "
            "El consejo debe autorizar cambios significativos."
        )
        
        return json.dumps(council_report, indent=2, ensure_ascii=False)
    
    async def execute_council_decisions(
        self,
        decisions: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, Any]:
        """
        Ejecutar decisiones aprobadas por el consejo
        
        Args:
            decisions: Dict con formato {agent_id: [cambios aprobados]}
            
        Returns:
            Resultados de ejecución
        """
        execution_results = {
            'timestamp': datetime.now().isoformat(),
            'decisions_executed': [],
            'decisions_failed': []
        }
        
        self.logger.info(f"Ejecutando {len(decisions)} sets de decisiones del consejo")
        
        for agent_id, changes in decisions.items():
            if agent_id not in self.registered_agents:
                self.logger.warning(f"Agente no registrado: {agent_id}")
                continue
            
            agent = self.registered_agents[agent_id]
            
            try:
                approval_metadata = {
                    'approved_by': 'council',
                    'approved_at': datetime.now().isoformat(),
                    'orchestrator': self.name
                }
                
                response = await agent.execute_approved_changes(
                    changes=changes,
                    approval_metadata=approval_metadata
                )
                
                execution_results['decisions_executed'].append({
                    'agent_id': agent_id,
                    'changes_count': len(changes),
                    'response': response.to_dict()
                })
                
                # Registrar aprobación
                self.council_approvals[agent_id] = approval_metadata
                
            except Exception as e:
                self.logger.error(f"Error ejecutando decisiones para {agent_id}: {e}")
                execution_results['decisions_failed'].append({
                    'agent_id': agent_id,
                    'error': str(e)
                })
        
        return execution_results
    
    def get_orchestrator_status(self) -> Dict[str, Any]:
        """Obtener estado actual del orquestador"""
        return {
            'nombre': self.name,
            'agentes_registrados': list(self.registered_agents.keys()),
            'total_agentes': len(self.registered_agents),
            'aprobaciones_procesadas': len(self.council_approvals),
            'última_auditoría': None  # Se actualiza después de ejecutar ciclo
        }
