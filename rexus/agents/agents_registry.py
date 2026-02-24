"""
Agents Registry - Registro centralizado de todos los agentes del sistema
Facilita la creación y gestión de agentes especializados
"""

from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class AgentsRegistry:
    """
    Registro centralizado de agentes

    Responsabilidades:
    - Mantener catálogo de agentes disponibles
    - Crear instancias de agentes
    - Registrar agentes en orquestadores
    - Gestionar configuraciones
    """

    # Catálogo de agentes disponibles
    AGENT_CATALOG = {
        # Agentes especializados por módulo
        'module_specialists': {
            'inventario': {
                'class': 'InventarioAgent',
                'module': 'rexus.agents.module_specialists.inventario_agent',
                'description': 'Gestión de inventario y stock',
                'tags': ['inventario', 'stock', 'productos']
            },
            'obras': {
                'class': 'ObrasAgent',
                'module': 'rexus.agents.module_specialists.obras_agent',
                'description': 'Gestión de obras y proyectos',
                'tags': ['obras', 'proyectos', 'producción']
            },
            'usuarios': {
                'class': 'UsuariosAgent',
                'module': 'rexus.agents.module_specialists.usuarios_agent',
                'description': 'Gestión de usuarios y seguridad',
                'tags': ['usuarios', 'seguridad', 'permisos']
            },
            'compras': {
                'class': 'ComprasAgent',
                'module': 'rexus.agents.module_specialists.compras_agent',
                'description': 'Gestión de compras y proveedores',
                'tags': ['compras', 'proveedores', 'adquisiciones']
            }
        },

        # Agentes de tareas específicas
        'task_agents': {
            'database': {
                'class': 'DatabaseAgent',
                'module': 'rexus.agents.task_agents.database_agent',
                'description': 'Optimización de base de datos',
                'tags': ['database', 'sql', 'optimization']
            },
            'code_quality': {
                'class': 'CodeQualityAgent',
                'module': 'rexus.agents.task_agents.code_quality_agent',
                'description': 'Análisis de calidad de código',
                'tags': ['code_quality', 'refactoring', 'clean_code']
            }
        },

        # Agentes de skills
        'skill_agents': {
            'skill_executor': {
                'class': 'SkillExecutorAgent',
                'module': 'rexus.agents.skill_agents.skill_executor_agent',
                'description': 'Ejecución de skills del sistema',
                'tags': ['skills', 'automation']
            }
        },

        # Agentes de testing
        'testing_agents': {
            'test_generator': {
                'class': 'TestGeneratorAgent',
                'module': 'rexus.agents.testing_agents.test_generator_agent',
                'description': 'Generación de tests automatizados',
                'tags': ['testing', 'pytest', 'coverage']
            }
        },

        # Agentes de seguridad
        'security_agents': {
            'security_audit': {
                'class': 'SecurityAuditAgent',
                'module': 'rexus.agents.security_agents.security_audit_agent',
                'description': 'Auditoría de seguridad',
                'tags': ['security', 'vulnerability', 'owasp']
            }
        },

        # Agentes de optimización
        'optimization_agents': {
            'performance_optimizer': {
                'class': 'PerformanceOptimizerAgent',
                'module': 'rexus.agents.optimization_agents.performance_optimizer_agent',
                'description': 'Optimización de rendimiento',
                'tags': ['performance', 'optimization']
            }
        },

        # Agentes de monitoreo
        'monitoring_agents': {
            'system_monitor': {
                'class': 'SystemMonitorAgent',
                'module': 'rexus.agents.monitoring_agents.system_monitor_agent',
                'description': 'Monitoreo del sistema',
                'tags': ['monitoring', 'metrics', 'health']
            }
        },

        # Agentes de auditoría (existentes)
        'module_auditors': {
            'audit': {
                'class': 'AuditAgent',
                'module': 'rexus.agents.module_auditors.audit_agent',
                'description': 'Auditoría de módulos',
                'tags': ['audit', 'module']
            }
        }
    }

    def __init__(self):
        """Inicializar registro"""
        self.logger = logging.getLogger(f"rexus.agents.{self.__class__.__name__}")
        self._instances: Dict[str, Any] = {}

    def get_agent_info(self, agent_type: str, agent_name: str) -> Optional[Dict[str, Any]]:
        """
        Obtener información de un agente

        Args:
            agent_type: Tipo de agente (module_specialists, task_agents, etc)
            agent_name: Nombre del agente
        """
        return self.AGENT_CATALOG.get(agent_type, {}).get(agent_name)

    def list_agents(self, agent_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Listar agentes disponibles

        Args:
            agent_type: Filtrar por tipo (None = todos)
        """
        if agent_type:
            return self.AGENT_CATALOG.get(agent_type, {})
        return self.AGENT_CATALOG

    def create_agent(
        self,
        agent_type: str,
        agent_name: str,
        config: Optional[Any] = None
    ) -> Optional[Any]:
        """
        Crear instancia de un agente

        Args:
            agent_type: Tipo de agente
            agent_name: Nombre del agente
            config: Configuración opcional
        """
        agent_info = self.get_agent_info(agent_type, agent_name)
        if not agent_info:
            self.logger.error(f"Agente no encontrado: {agent_type}.{agent_name}")
            return None

        try:
            # Importar clase del agente
            module_path = agent_info['module']
            class_name = agent_info['class']

            parts = module_path.split('.')
            module = __import__(module_path)
            for part in parts[1:]:
                module = getattr(module, part)

            agent_class = getattr(module, class_name)

            # Crear instancia
            instance = agent_class(config) if config else agent_class()

            self.logger.info(f"Agente creado: {agent_type}.{agent_name}")
            return instance

        except Exception as e:
            self.logger.error(f"Error creando agente {agent_type}.{agent_name}: {e}")
            return None

    def create_module_specialist(self, module_name: str) -> Optional[Any]:
        """Crear agente especialista para un módulo específico"""
        return self.create_agent('module_specialists', module_name)

    def create_task_agent(self, task_name: str) -> Optional[Any]:
        """Crear agente de tarea específica"""
        return self.create_agent('task_agents', task_name)

    def create_skill_agent(self, skill_name: str) -> Optional[Any]:
        """Crear agente de skill"""
        return self.create_agent('skill_agents', skill_name)

    def create_testing_agent(self, test_name: str) -> Optional[Any]:
        """Crear agente de testing"""
        return self.create_agent('testing_agents', test_name)

    def create_security_agent(self, security_name: str) -> Optional[Any]:
        """Crear agente de seguridad"""
        return self.create_agent('security_agents', security_name)

    def create_optimization_agent(self, opt_name: str) -> Optional[Any]:
        """Crear agente de optimización"""
        return self.create_agent('optimization_agents', opt_name)

    def create_monitoring_agent(self, monitor_name: str) -> Optional[Any]:
        """Crear agente de monitoreo"""
        return self.create_agent('monitoring_agents', monitor_name)

    def register_all_with_orchestrator(self, orchestrator: Any) -> Dict[str, Any]:
        """
        Registrar todos los agentes con un orquestador

        Args:
            orchestrator: Instancia de AgentOrchestrator
        """
        registered = {}

        for agent_type, agents in self.AGENT_CATALOG.items():
            for agent_name, agent_info in agents.items():
                agent_id = f"{agent_type}_{agent_name}"
                agent = self.create_agent(agent_type, agent_name)

                if agent:
                    orchestrator.register_agent(agent_id, agent)
                    registered[agent_id] = agent
                    self.logger.info(f"Agente registrado: {agent_id}")

        return registered


# Instancia global del registro
_registry = None


def get_agents_registry() -> AgentsRegistry:
    """Obtener instancia global del registro"""
    global _registry
    if _registry is None:
        _registry = AgentsRegistry()
    return _registry


def create_all_agents() -> Dict[str, Any]:
    """
    Crear todos los agentes del sistema

    Returns:
        Diccionario con {agent_id: agent_instance}
    """
    registry = get_agents_registry()
    agents = {}

    for agent_type, agents_dict in registry.AGENT_CATALOG.items():
        for agent_name, agent_info in agents_dict.items():
            agent_id = f"{agent_type}_{agent_name}"
            agent = registry.create_agent(agent_type, agent_name)
            if agent:
                agents[agent_id] = agent

    return agents


def setup_agents_with_orchestrator(orchestrator: Any) -> Dict[str, Any]:
    """
    Configurar todos los agentes con un orquestador

    Args:
        orchestrator: Instancia de AgentOrchestrator

    Returns:
        Diccionario con agentes registrados
    """
    registry = get_agents_registry()
    return registry.register_all_with_orchestrator(orchestrator)
