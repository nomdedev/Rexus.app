"""
Ejemplo de uso del sistema de agentes Rexus.app
Demuestra cómo:
1. Registrar agentes de auditoría
2. Ejecutar un ciclo de auditoría
3. Generar reportes para el consejo
4. Ejecutar cambios aprobados
"""

import asyncio
import logging
from datetime import datetime

from rexus.agents.module_auditors.audit_agent import AuditAgent
from rexus.agents.orchestrators.orchestrator import AgentOrchestrator

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    """Ejemplo de inicialización y ejecución de agentes"""
    
    logger.info("=" * 80)
    logger.info("INICIANDO SISTEMA DE AGENTES REXUS.APP")
    logger.info("=" * 80)
    
    # 1. Crear orquestador central
    orchestrator = AgentOrchestrator(name="RexusMainOrchestrator")
    logger.info(f"Orquestador creado: {orchestrator.name}")
    
    # 2. Crear y registrar agentes de auditoría por módulo
    modules = [
        'inventario',
        'usuarios',
        'auditoría',
        'compras',
        'logística'
    ]
    
    logger.info(f"\nRegistrando {len(modules)} agentes de auditoría...")
    for module_name in modules:
        agent = AuditAgent(module_name=module_name)
        agent_id = f"audit-{module_name}"
        orchestrator.register_agent(agent_id, agent)
        logger.info(f"  ✓ {agent_id} registrado")
    
    # 3. Mostrar estado del orquestador
    status = orchestrator.get_orchestrator_status()
    logger.info(f"\nOrcuestador Status: {status}")
    
    # 4. Ejecutar ciclo de auditoría
    logger.info("\n" + "=" * 80)
    logger.info("EJECUTANDO CICLO DE AUDITORÍA")
    logger.info("=" * 80)
    
    audit_results = await orchestrator.run_audit_cycle(
        generate_council_report=True
    )
    
    # 5. Mostrar resultados
    logger.info("\nResultados de auditoría:")
    summary = audit_results['summary']
    logger.info(f"  - Agentes auditados: {summary['total_agents_auditados']}")
    logger.info(f"  - Auditorías completadas: {summary['auditorías_completadas']}")
    
    # 6. Mostrar reporte del consejo
    logger.info("\n" + "=" * 80)
    logger.info("REPORTE PARA CONSEJO SUPERIOR")
    logger.info("=" * 80)
    logger.info(audit_results['council_report'])
    
    # 7. Ejemplo: Ejecutar cambios aprobados
    logger.info("\n" + "=" * 80)
    logger.info("EJECUTANDO CAMBIOS APROBADOS POR CONSEJO")
    logger.info("=" * 80)
    
    council_decisions = {
        'audit-inventario': [
            {
                'id': 'IMP-001',
                'tipo': 'añadir_validación',
                'componente': 'modelo',
                'descripción': 'Añadir validación de cantidad mínima'
            }
        ],
        'audit-usuarios': [
            {
                'id': 'IMP-002',
                'tipo': 'seguridad',
                'componente': 'autenticación',
                'descripción': 'Implementar autenticación de dos factores'
            }
        ]
    }
    
    execution_results = await orchestrator.execute_council_decisions(council_decisions)
    
    logger.info(f"\nCambios ejecutados: {len(execution_results['decisions_executed'])}")
    logger.info(f"Cambios fallidos: {len(execution_results['decisions_failed'])}")
    
    logger.info("\n" + "=" * 80)
    logger.info("SISTEMA DE AGENTES INICIALIZADO CORRECTAMENTE")
    logger.info("=" * 80)
    
    return {
        'orchestrator': orchestrator,
        'audit_results': audit_results,
        'execution_results': execution_results
    }


if __name__ == "__main__":
    # Ejecutar demo
    results = asyncio.run(main())
    
    # Los agentes están listos para recibir tareas
    logger.info("\n✓ Los agentes están activos y listos para trabajar")
    logger.info("✓ Puedes enviar tareas específicas a través del orquestador")
