"""
Sistema de Agentes Rexus.app
Proporciona agentes especializados para automatizar y optimizar el sistema
"""

# Importar registro centralizado
from .agents_registry import (
    AgentsRegistry,
    get_agents_registry,
    create_all_agents,
    setup_agents_with_orchestrator
)

# Importar clases base
from .core.base_agent import BaseAgent, AgentConfig, AgentResponse

# Importar orquestador
from .orchestrators.orchestrator import AgentOrchestrator

# Importar gestor de estado
from .state_manager import (
    AgentStateManager,
    get_state_manager,
    TaskStatus
)

# Importar bridge de Pixel Agents
from .pixel_bridge import PixelAgentsBridge, get_pixel_bridge

# Importar agentes de módulos
from .module_specialists.inventario_agent import InventarioAgent
from .module_specialists.obras_agent import ObrasAgent
from .module_specialists.usuarios_agent import UsuariosAgent
from .module_specialists.compras_agent import ComprasAgent

# Importar agentes de tareas
from .task_agents.database_agent import DatabaseAgent
from .task_agents.code_quality_agent import CodeQualityAgent

# Importar agentes de skills
from .skill_agents.skill_executor_agent import SkillExecutorAgent

# Importar agentes de testing
from .testing_agents.test_generator_agent import TestGeneratorAgent

# Importar agentes de seguridad
from .security_agents.security_audit_agent import SecurityAuditAgent

# Importar agentes de optimización
from .optimization_agents.performance_optimizer_agent import PerformanceOptimizerAgent

# Importar agentes de monitoreo
from .monitoring_agents.system_monitor_agent import SystemMonitorAgent

# Importar agente de auditoría
from .module_auditors.audit_agent import AuditAgent

__all__ = [
    # Registro
    'AgentsRegistry',
    'get_agents_registry',
    'create_all_agents',
    'setup_agents_with_orchestrator',

    # Base
    'BaseAgent',
    'AgentConfig',
    'AgentResponse',

    # Orquestación
    'AgentOrchestrator',

    # Estado
    'AgentStateManager',
    'get_state_manager',
    'TaskStatus',

    # Pixel bridge
    'PixelAgentsBridge',
    'get_pixel_bridge',

    # Agentes de módulos
    'InventarioAgent',
    'ObrasAgent',
    'UsuariosAgent',
    'ComprasAgent',

    # Agentes de tareas
    'DatabaseAgent',
    'CodeQualityAgent',

    # Agentes de skills
    'SkillExecutorAgent',

    # Agentes de testing
    'TestGeneratorAgent',

    # Agentes de seguridad
    'SecurityAuditAgent',

    # Agentes de optimización
    'PerformanceOptimizerAgent',

    # Agentes de monitoreo
    'SystemMonitorAgent',

    # Agentes de auditoría
    'AuditAgent',
]


# Función de conveniencia para inicializar todo el sistema
def initialize_agents_system(
    orchestrator_name: str = "RexusMainOrchestrator"
) -> tuple:
    """
    Inicializar el sistema completo de agentes

    Args:
        orchestrator_name: Nombre del orquestador principal

    Returns:
        (orchestrator, agents_dict, state_manager)
    """
    import logging

    logger = logging.getLogger(__name__)
    logger.info("Inicializando sistema de agentes Rexus.app...")

    # Crear orquestador
    orchestrator = AgentOrchestrator(name=orchestrator_name)

    # Registrar todos los agentes
    agents_dict = setup_agents_with_orchestrator(orchestrator)

    # Obtener gestor de estado
    state_manager = get_state_manager()

    logger.info(f"Sistema inicializado: {len(agents_dict)} agentes registrados")

    return orchestrator, agents_dict, state_manager
