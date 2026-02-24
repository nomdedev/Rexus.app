"""
Base Agent Class - Fundación para todos los agentes Rexus.app
Construido con Microsoft Agent Framework
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional, List
from datetime import datetime
import json
import logging
import os

logger = logging.getLogger(__name__)

# Importar state manager para UI dashboard
try:
    from ..state_manager import get_state_manager, TaskStatus
    HAS_STATE_MANAGER = True
except (ImportError, ModuleNotFoundError):
    HAS_STATE_MANAGER = False
    def get_state_manager(): return None
    # Dummy TaskStatus si no está disponible
    class TaskStatus:
        ANALYZING = "analyzing"
        GENERATING_REPORT = "generating"
        PROPOSING_CHANGES = "proposing"
        EXECUTING = "executing"
        COMPLETED = "completed"
        FAILED = "failed"

USE_STATE_MANAGER = os.getenv("REXUS_AGENT_STATE_MANAGER", "false").lower() == "true"

# Importar bridge para Pixel Agents
try:
    from ..pixel_bridge import get_pixel_bridge
    HAS_PIXEL_BRIDGE = True
except (ImportError, ModuleNotFoundError):
    HAS_PIXEL_BRIDGE = False

    def get_pixel_bridge():
        return None


@dataclass
class AgentConfig:
    """Configuración base para agentes"""
    name: str
    description: str
    model: str = "claude-opus"  # Usando Claude por defecto
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: int = 300  # segundos
    retry_attempts: int = 3
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class AgentResponse:
    """Respuesta estructurada de un agente"""
    
    def __init__(
        self,
        agent_name: str,
        status: str,  # 'success', 'error', 'warning'
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        timestamp: Optional[datetime] = None
    ):
        self.agent_name = agent_name
        self.status = status
        self.content = content
        self.metadata = metadata or {}
        self.timestamp = timestamp or datetime.now()
        self.execution_id = None
        
    def to_dict(self) -> Dict[str, Any]:
        """Convertir respuesta a diccionario"""
        return {
            'agent': self.agent_name,
            'status': self.status,
            'content': self.content,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat()
        }
    
    def to_json(self) -> str:
        """Convertir respuesta a JSON"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


class BaseAgent:
    """
    Clase base para todos los agentes de Rexus.app
    
    Responsabilidades:
    - Interactuar con módulos específicos
    - Generar análisis y reportes
    - Proponer mejoras
    - Ejecutar cambios autorizados
    """
    
    def __init__(self, config: AgentConfig):
        """Inicializar agente con configuración"""
        self.config = config
        self.logger = logging.getLogger(f"rexus.agents.{config.name}")
        self.execution_history: List[Dict[str, Any]] = []
        self.state_manager = get_state_manager() if (HAS_STATE_MANAGER and USE_STATE_MANAGER) else None
        self.pixel_bridge = get_pixel_bridge() if HAS_PIXEL_BRIDGE else None
        self.current_task_index = None
        self.current_pixel_task_ref = None
        
    async def analyze(self, target: str, context: Dict[str, Any]) -> AgentResponse:
        """
        Analizar un objetivo específico
        
        Args:
            target: Identificador del objetivo (módulo, función, etc)
            context: Contexto adicional para el análisis
            
        Returns:
            AgentResponse con resultados del análisis
        """
        raise NotImplementedError("Subclases deben implementar analyze()")
    
    async def generate_report(self, analysis_data: Dict[str, Any]) -> str:
        """
        Generar reporte estructurado basado en análisis
        
        Args:
            analysis_data: Datos del análisis
            
        Returns:
            Reporte en formato string o JSON
        """
        raise NotImplementedError("Subclases deben implementar generate_report()")
    
    async def propose_improvements(
        self,
        analysis_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Proponer mejoras basadas en análisis
        
        Args:
            analysis_data: Datos del análisis
            
        Returns:
            Lista de mejoras propuestas
        """
        raise NotImplementedError("Subclases deben implementar propose_improvements()")
    
    async def execute_approved_changes(
        self,
        changes: List[Dict[str, Any]],
        approval_metadata: Dict[str, Any]
    ) -> AgentResponse:
        """
        Ejecutar cambios que fueron aprobados por el consejo
        
        Args:
            changes: Lista de cambios a ejecutar
            approval_metadata: Metadata de la aprobación (quién, cuándo, etc)
            
        Returns:
            AgentResponse con resultado de ejecución
        """
        raise NotImplementedError("Subclases deben implementar execute_approved_changes()")
    
    def log_execution(self, action: str, result: Any, status: str = "success"):
        """Registrar ejecución del agente"""
        execution_record = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'status': status,
            'result': str(result)[:500]  # Limitar a 500 chars
        }
        self.execution_history.append(execution_record)
        self.logger.info(f"{action}: {status}")
    
    def register_task(
        self,
        module_name: str,
        task_type: str,
        description: str
    ) -> Optional[int]:
        """
        Registrar una tarea para el dashboard
        
        Returns:
            Índice de la tarea (para actualizar después)
        """
        if HAS_STATE_MANAGER and self.state_manager:
            try:
                self.state_manager.start_task(
                    agent_id=self.config.name,
                    agent_name=self.config.name,
                    module_name=module_name,
                    task_type=task_type,
                    description=description
                )
                tasks = self.state_manager.get_agent_tasks(self.config.name)
                self.current_task_index = len(tasks) - 1
            except Exception as e:
                self.logger.warning(f"No se pudo registrar tarea en state manager: {e}")

        if HAS_PIXEL_BRIDGE and self.pixel_bridge:
            try:
                self.current_pixel_task_ref = self.pixel_bridge.start_task(
                    agent_id=self.config.name,
                    description=f"[{module_name}] {description}",
                    task_type=task_type,
                )
            except Exception as e:
                self.logger.warning(f"No se pudo registrar tarea en Pixel Agents: {e}")

        return self.current_task_index
    
    def update_task_progress(
        self,
        progress: int,
        description: Optional[str] = None,
        status: Optional[str] = None
    ):
        """
        Actualizar progreso de tarea en dashboard
        
        Args:
            progress: 0-100
            description: Descripción actualizada
            status: Nuevo estado si aplica
        """
        if HAS_STATE_MANAGER and self.state_manager and self.current_task_index is not None:
            try:
                task_status = None
                if status == "analyzing":
                    task_status = TaskStatus.ANALYZING
                elif status == "generating_report":
                    task_status = TaskStatus.GENERATING_REPORT
                elif status == "proposing_changes":
                    task_status = TaskStatus.PROPOSING_CHANGES
                elif status == "executing":
                    task_status = TaskStatus.EXECUTING

                self.state_manager.update_task(
                    agent_id=self.config.name,
                    task_index=self.current_task_index,
                    progress=progress,
                    description=description,
                    status=task_status
                )
            except Exception as e:
                self.logger.warning(f"Error actualizando progreso en state manager: {e}")

        if HAS_PIXEL_BRIDGE and self.pixel_bridge and self.current_pixel_task_ref is not None:
            try:
                self.pixel_bridge.update_progress(
                    task_ref=self.current_pixel_task_ref,
                    description=description or "En progreso",
                    progress=progress,
                )
            except Exception as e:
                self.logger.warning(f"Error actualizando progreso en Pixel Agents: {e}")
    
    def complete_task(self, result: str, error: Optional[str] = None):
        """Marcar tarea como completada"""
        if HAS_STATE_MANAGER and self.state_manager and self.current_task_index is not None:
            try:
                status = TaskStatus.FAILED if error else TaskStatus.COMPLETED

                self.state_manager.update_task(
                    agent_id=self.config.name,
                    task_index=self.current_task_index,
                    status=status,
                    progress=100 if not error else 50,
                    result=result,
                    error=error
                )
            except Exception as e:
                self.logger.warning(f"Error completando tarea en state manager: {e}")

        if HAS_PIXEL_BRIDGE and self.pixel_bridge and self.current_pixel_task_ref is not None:
            try:
                self.pixel_bridge.complete_task(
                    task_ref=self.current_pixel_task_ref,
                    result=result,
                    is_error=error is not None,
                )
                self.current_pixel_task_ref = None
            except Exception as e:
                self.logger.warning(f"Error completando tarea en Pixel Agents: {e}")
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Obtener resumen de ejecuciones"""
        return {
            'agent_name': self.config.name,
            'total_executions': len(self.execution_history),
            'recent_executions': self.execution_history[-10:],  # Últimas 10
            'tags': self.config.tags
        }
