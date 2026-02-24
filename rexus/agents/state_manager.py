"""
Sistema de Estado para Agentes
Rastrea en tiempo real qué está haciendo cada agente
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from pathlib import Path


class TaskStatus(Enum):
    """Estados posibles de una tarea"""
    PENDING = "pendiente"
    IN_PROGRESS = "en_progreso"
    COMPLETED = "completada"
    FAILED = "fallida"
    ANALYZING = "analizando"
    GENERATING_REPORT = "generando_reporte"
    PROPOSING_CHANGES = "proponiendo_cambios"
    EXECUTING = "ejecutando_cambios"


@dataclass
class AgentTask:
    """Representa una tarea de un agente"""
    agent_id: str
    agent_name: str
    module_name: str
    task_type: str  # 'audit', 'report', 'execute', etc
    status: TaskStatus
    description: str
    start_time: str
    end_time: Optional[str] = None
    progress: int = 0  # 0-100
    result: Optional[str] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario"""
        data = asdict(self)
        data['status'] = self.status.value
        return data


class AgentStateManager:
    """
    Gestor centralizado de estado de agentes
    Permite que la UI vea qué está haciendo cada agente
    """
    
    def __init__(self, state_file: str = "logs/agents_state.json"):
        """Inicializar gestor de estado"""
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.tasks: Dict[str, List[AgentTask]] = {}
        self.lock = threading.Lock()
        self._load_state()
    
    def _load_state(self):
        """Cargar estado guardado"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Reconstruir tareas desde JSON
                    for agent_id, tasks_data in data.items():
                        self.tasks[agent_id] = [
                            AgentTask(
                                agent_id=t['agent_id'],
                                agent_name=t['agent_name'],
                                module_name=t['module_name'],
                                task_type=t['task_type'],
                                status=TaskStatus(t['status']),
                                description=t['description'],
                                start_time=t['start_time'],
                                end_time=t.get('end_time'),
                                progress=t.get('progress', 0),
                                result=t.get('result'),
                                error=t.get('error')
                            )
                            for t in tasks_data
                        ]
            except Exception as e:
                print(f"Error cargando estado: {e}")
    
    def _save_state(self):
        """Guardar estado a archivo"""
        with self.lock:
            try:
                data = {
                    agent_id: [task.to_dict() for task in tasks]
                    for agent_id, tasks in self.tasks.items()
                }
                with open(self.state_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                print(f"Error guardando estado: {e}")
    
    def start_task(
        self,
        agent_id: str,
        agent_name: str,
        module_name: str,
        task_type: str,
        description: str
    ) -> AgentTask:
        """Registrar inicio de tarea"""
        with self.lock:
            task = AgentTask(
                agent_id=agent_id,
                agent_name=agent_name,
                module_name=module_name,
                task_type=task_type,
                status=TaskStatus.IN_PROGRESS,
                description=description,
                start_time=datetime.now().isoformat(),
                progress=0
            )
            
            if agent_id not in self.tasks:
                self.tasks[agent_id] = []
            
            self.tasks[agent_id].append(task)
            self._save_state()
            
            return task
    
    def update_task(
        self,
        agent_id: str,
        task_index: int,
        status: Optional[TaskStatus] = None,
        progress: Optional[int] = None,
        description: Optional[str] = None,
        result: Optional[str] = None,
        error: Optional[str] = None
    ):
        """Actualizar estado de tarea"""
        with self.lock:
            if agent_id in self.tasks and task_index < len(self.tasks[agent_id]):
                task = self.tasks[agent_id][task_index]
                
                if status:
                    task.status = status
                    if status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                        task.end_time = datetime.now().isoformat()
                
                if progress is not None:
                    task.progress = min(100, max(0, progress))
                
                if description:
                    task.description = description
                
                if result:
                    task.result = result
                
                if error:
                    task.error = error
                
                self._save_state()
    
    def get_agent_tasks(self, agent_id: str) -> List[AgentTask]:
        """Obtener tareas de un agente"""
        with self.lock:
            return self.tasks.get(agent_id, [])
    
    def get_all_tasks(self) -> Dict[str, List[AgentTask]]:
        """Obtener todas las tareas"""
        with self.lock:
            return {
                agent_id: list(tasks)
                for agent_id, tasks in self.tasks.items()
            }
    
    def get_current_tasks(self) -> Dict[str, AgentTask]:
        """Obtener tarea actual de cada agente"""
        current = {}
        with self.lock:
            for agent_id, tasks in self.tasks.items():
                if tasks:
                    # Obtener la última tarea (más reciente)
                    current[agent_id] = tasks[-1]
        return current
    
    def get_active_tasks(self) -> List[AgentTask]:
        """Obtener solo tareas en progreso"""
        active = []
        with self.lock:
            for tasks in self.tasks.values():
                for task in tasks:
                    if task.status == TaskStatus.IN_PROGRESS:
                        active.append(task)
        return active
    
    def get_summary(self) -> Dict[str, Any]:
        """Obtener resumen de estado"""
        with self.lock:
            all_tasks = [t for tasks in self.tasks.values() for t in tasks]
            
            summary = {
                'total_agents': len(self.tasks),
                'total_tasks': len(all_tasks),
                'active_tasks': sum(
                    1 for t in all_tasks
                    if t.status == TaskStatus.IN_PROGRESS
                ),
                'completed_tasks': sum(
                    1 for t in all_tasks
                    if t.status == TaskStatus.COMPLETED
                ),
                'failed_tasks': sum(
                    1 for t in all_tasks
                    if t.status == TaskStatus.FAILED
                ),
            }
            
            return summary


# Instancia global del gestor
_state_manager = None


def get_state_manager() -> AgentStateManager:
    """Obtener instancia global del gestor"""
    global _state_manager
    if _state_manager is None:
        _state_manager = AgentStateManager()
    return _state_manager
