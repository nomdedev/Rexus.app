"""
Demostración simple del Sistema de Agentes Rexus.app
Inicializa y muestra estado de los agentes
"""

import sys
import logging
from pathlib import Path

# Fijar encoding para Windows
if sys.platform == 'win32':
    import os
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Setup path
root = Path(__file__).parent.parent
sys.path.insert(0, str(root))

# Logging simple
logging.basicConfig(
    level=logging.WARNING,  # Solo warnings y errores
    format='%(message)s'
)

from rexus.agents.module_auditors.audit_agent import AuditAgent
from rexus.agents.orchestrators.orchestrator import AgentOrchestrator


def main():
    """Demostración simple de agentes"""
    
    print("\n" + "="*80)
    print("[SYSTEM] REXUS.APP - SYSTEM DE AGENTES")
    print("="*80 + "\n")
    
    # Módulos de Rexus.app
    MODULES = [
        'obras', 'inventario', 'herrajes', 'vidrios', 'logistica',
        'pedidos', 'compras', 'administracion', 'mantenimiento',
        'auditoria', 'usuarios', 'configuracion', 'notificaciones'
    ]
    
    # Crear orquestador
    print("[*] Inicializando Orchestrator...")
    orchestrator = AgentOrchestrator(name="RexusMainOrchestrator")
    print("[OK] Orchestrator 'RexusMainOrchestrator' creado\n")
    
    # Registrar agentes
    print(f"[*] Registrando {len(MODULES)} agentes de auditoria...\n")
    for i, module_name in enumerate(MODULES, 1):
        agent = AuditAgent(module_name=module_name)
        agent_id = f"audit-{module_name}"
        orchestrator.register_agent(agent_id, agent)
        status = f"[OK] #{i:2d} {agent_id:30s} - Auditor de '{module_name}' registrado"
        print(status)
    
    # Mostrar estado
    print("\n" + "-"*80)
    status = orchestrator.get_orchestrator_status()
    print("\n[STATUS] Estado del Sistema:\n")
    print(f"  Nombre del Orchestrator: {status['nombre']}")
    print(f"  Agentes Registrados: {status['total_agentes']}")
    print(f"  Agentes Activos: {', '.join(status['agentes_registrados'][:3])}...")
    print(f"  Decisiones del Consejo Procesadas: {status['aprobaciones_procesadas']}")
    
    print("\n" + "-"*80)
    print("\n[SUCCESS] SISTEMA DE AGENTES OPERACIONAL\n")
    print("[INFO] Los agentes están listos para:")
    print("  * Auditar modulos de Rexus.app")
    print("  * Generar reportes para consejo superior")
    print("  * Proponer mejoras especificas")
    print("  * Ejecutar cambios aprobados")
    print("\n[INFO] Ver documentacion en:")
    print("  * docs/AGENTS_ARCHITECTURE.md")
    print("  * rexus/agents/README.md")
    print("\n[INFO] Visualiza los agentes en Pixel Agents panel de VS Code\n")


if __name__ == "__main__":
    main()
