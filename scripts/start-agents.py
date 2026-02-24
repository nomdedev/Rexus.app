"""
Script para iniciar el sistema de agentes Rexus.app
Se integra con Pixel Agents para visualización

Uso: python scripts/start-agents.py
"""

import sys
import asyncio
import logging
from pathlib import Path
import os

# Fijar encoding para Windows
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Setup path
root = Path(__file__).parent.parent
sys.path.insert(0, str(root))

from rexus.agents.module_auditors.audit_agent import AuditAgent
from rexus.agents.orchestrators.orchestrator import AgentOrchestrator

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/agents.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

# Módulos de Rexus.app que necesitan agentes
MODULES_TO_AUDIT = [
    'obras',
    'inventario',
    'herrajes',
    'vidrios',
    'logística',
    'pedidos',
    'compras',
    'administración',
    'mantenimiento',
    'auditoría',
    'usuarios',
    'configuración',
    'notificaciones'
]


async def initialize_agents():
    """Inicializar el sistema de agentes"""
    
    print("\n" + "="*80)
    print("[INFO] INICIANDO SISTEMA DE AGENTES REXUS.APP")
    print("="*80 + "\n")
    
    # Crear orquestador
    orchestrator = AgentOrchestrator(name="RexusMainOrchestrator")
    logger.info(f"[OK] Orquestador creado: {orchestrator.name}")
    
    # Registrar agentes para cada módulo
    print(f"[*] Registrando {len(MODULES_TO_AUDIT)} agentes...")
    for module_name in MODULES_TO_AUDIT:
        agent = AuditAgent(module_name=module_name)
        agent_id = f"audit-{module_name}"
        orchestrator.register_agent(agent_id, agent)
        print(f"    [OK] {agent_id}")
    
    print(f"\n[OK] {len(MODULES_TO_AUDIT)} agentes registrados exitosamente\n")
    
    # Mostrar estado
    orchestrator_status = orchestrator.get_orchestrator_status()
    print("[*] Estado del Orquestador:")
    print(f"    - Nombre: {orchestrator_status['nombre']}")
    print(f"    - Agentes activos: {orchestrator_status['total_agentes']}")
    print(f"    - Agentes registrados: {', '.join(orchestrator_status['agentes_registrados'][:3])}...")
    
    logger.info("Sistema de agentes inicializado")
    
    return orchestrator


async def main():
    """Función principal"""
    try:
        orchestrator = await initialize_agents()
        
        print("\n" + "="*80)
        print("[SUCCESS] SISTEMA DE AGENTES ACTIVO Y LISTO")
        print("="*80)
        print("\n[*] Los agentes están disponibles para:")
        print("    * Auditar módulos")
        print("    * Generar reportes")
        print("    * Proponer mejoras")
        print("    * Ejecutar cambios autorizados")
        print("\n[*] Ver rexus/agents/README.md para más información")
        print("[*] Los agentes aparecerán en Pixel Agents panel en VS Code\n")
        
        # Mantener el sistema corriendo
        print("[*] Sistema activo. Presiona Ctrl+C para salir...\n")
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n[INFO] Sistema de agentes detenido")
        sys.exit(0)
    except Exception as e:
        logger.error(f"[ERROR] Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[INFO] Saliendo...")
        sys.exit(0)
