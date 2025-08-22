# -*- coding: utf-8 -*-
"""
Sistema de Workflows - Rexus.app
Motor de workflows para automatizar procesos empresariales
"""

import datetime
import json
from enum import Enum
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

from PyQt6.QtCore import QObject, pyqtSignal


class WorkflowStatus(Enum):
    """Estados posibles de un workflow."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ERROR = "error"


class StepStatus(Enum):
    """Estados posibles de un paso del workflow."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    APPROVED = "approved"
    REJECTED = "rejected"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class WorkflowData:
    """Datos que fluyen a través del workflow."""
    workflow_id: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    created_at: datetime.datetime
    updated_at: datetime.datetime


@dataclass
class StepResult:
    """Resultado de la ejecución de un paso."""
    success: bool
    message: str
    data: Dict[str, Any]
    next_step: Optional[str] = None


class BaseWorkflowStep(ABC):
    """Clase base para pasos de workflow."""
    
    def __init__(self, step_id: str, name: str, description: str = ""):
        self.step_id = step_id
        self.name = name
        self.description = description
        self.status = StepStatus.PENDING
        self.created_at = datetime.datetime.now()
        self.completed_at = None
        self.assigned_to = None
        self.approval_required = False
        self.timeout_minutes = None
    
    @abstractmethod
    def execute(self, workflow_data: WorkflowData) -> StepResult:
        """Ejecuta el paso del workflow."""
        pass
    
    def can_execute(self, workflow_data: WorkflowData) -> bool:
        """Verifica si el paso puede ejecutarse."""
        return self.status == StepStatus.PENDING
    
    def approve(self, approver: str, comments: str = "") -> bool:
        """Aprueba el paso si requiere aprobación."""
        if self.approval_required and self.status == StepStatus.IN_PROGRESS:
            self.status = StepStatus.APPROVED
            self.completed_at = datetime.datetime.now()
            return True
        return False
    
    def reject(self, approver: str, comments: str = "") -> bool:
        """Rechaza el paso si requiere aprobación."""
        if self.approval_required and self.status == StepStatus.IN_PROGRESS:
            self.status = StepStatus.REJECTED
            return True
        return False


class ApprovalStep(BaseWorkflowStep):
    """Paso que requiere aprobación manual."""
    
    def __init__(self, step_id: str, name: str, approvers: List[str], 
                 description: str = "", required_approvals: int = 1):
        super().__init__(step_id, name, description)
        self.approvers = approvers
        self.required_approvals = required_approvals
        self.approval_required = True
        self.approvals_received = []
        self.rejections_received = []
    
    def execute(self, workflow_data: WorkflowData) -> StepResult:
        """Inicia el proceso de aprobación."""
        self.status = StepStatus.IN_PROGRESS
        
        return StepResult(
            success=True,
            message=f"Aprobación requerida de: {', '.join(self.approvers)}",
            data={"approvers": self.approvers, "required": self.required_approvals}
        )
    
    def add_approval(self, approver: str, comments: str = "") -> bool:
        """Agrega una aprobación."""
        if approver in self.approvers and approver not in [a['approver'] for a in self.approvals_received]:
            self.approvals_received.append({
                'approver': approver,
                'timestamp': datetime.datetime.now(),
                'comments': comments
            })
            
            # Verificar si se alcanzó el número requerido de aprobaciones
            if len(self.approvals_received) >= self.required_approvals:
                self.status = StepStatus.APPROVED
                self.completed_at = datetime.datetime.now()
                return True
        
        return False
    
    def add_rejection(self, approver: str, comments: str = "") -> bool:
        """Agrega un rechazo."""
        if approver in self.approvers:
            self.rejections_received.append({
                'approver': approver,
                'timestamp': datetime.datetime.now(),
                'comments': comments
            })
            self.status = StepStatus.REJECTED
            return True
        return False


class AutomatedStep(BaseWorkflowStep):
    """Paso automatizado que ejecuta una función."""
    
    def __init__(self, step_id: str, name: str, action_function: Callable, 
                 description: str = "", parameters: Dict = None):
        super().__init__(step_id, name, description)
        self.action_function = action_function
        self.parameters = parameters or {}
    
    def execute(self, workflow_data: WorkflowData) -> StepResult:
        """Ejecuta la función automatizada."""
        self.status = StepStatus.IN_PROGRESS
        
        try:
            # Ejecutar función con datos del workflow
            result = self.action_function(workflow_data, **self.parameters)
            
            self.status = StepStatus.COMPLETED
            self.completed_at = datetime.datetime.now()
            
            return StepResult(
                success=True,
                message=f"Paso {self.name} completado exitosamente",
                data=result if isinstance(result, dict) else {}
            )
            
        except Exception as e:
            self.status = StepStatus.ERROR
            return StepResult(
                success=False,
                message=f"Error en paso {self.name}: {str(e)}",
                data={}
            )


class ConditionalStep(BaseWorkflowStep):
    """Paso que evalúa una condición para determinar el siguiente paso."""
    
    def __init__(self, step_id: str, name: str, condition_function: Callable,
                 true_step: str, false_step: str, description: str = ""):
        super().__init__(step_id, name, description)
        self.condition_function = condition_function
        self.true_step = true_step
        self.false_step = false_step
    
    def execute(self, workflow_data: WorkflowData) -> StepResult:
        """Evalúa la condición."""
        self.status = StepStatus.IN_PROGRESS
        
        try:
            condition_result = self.condition_function(workflow_data)
            next_step = self.true_step if condition_result else self.false_step
            
            self.status = StepStatus.COMPLETED
            self.completed_at = datetime.datetime.now()
            
            return StepResult(
                success=True,
                message=f"Condición evaluada: {condition_result}",
                data={"condition_result": condition_result},
                next_step=next_step
            )
            
        except Exception as e:
            self.status = StepStatus.ERROR
            return StepResult(
                success=False,
                message=f"Error evaluando condición: {str(e)}",
                data={}
            )


class Workflow(QObject):
    """Representa un workflow completo."""
    
    # Señales
    step_started = pyqtSignal(str, str)  # workflow_id, step_id
    step_completed = pyqtSignal(str, str, bool)  # workflow_id, step_id, success
    workflow_completed = pyqtSignal(str)  # workflow_id
    approval_required = pyqtSignal(str, str, list)  # workflow_id, step_id, approvers
    
    def __init__(self, workflow_id: str, name: str, description: str = ""):
        super().__init__()
        self.workflow_id = workflow_id
        self.name = name
        self.description = description
        self.status = WorkflowStatus.DRAFT
        self.steps: Dict[str, BaseWorkflowStep] = {}
        self.step_sequence: List[str] = []
        self.current_step = None
        self.workflow_data = None
        self.created_at = datetime.datetime.now()
        self.started_at = None
        self.completed_at = None
        self.history = []
    
    def add_step(self, step: BaseWorkflowStep, after_step: str = None):
        """Agrega un paso al workflow."""
        self.steps[step.step_id] = step
        
        if after_step and after_step in self.step_sequence:
            index = self.step_sequence.index(after_step) + 1
            self.step_sequence.insert(index, step.step_id)
        else:
            self.step_sequence.append(step.step_id)
    
    def start(self, initial_data: Dict[str, Any]) -> bool:
        """Inicia la ejecución del workflow."""
        if self.status != WorkflowStatus.DRAFT:
            return False
        
        self.workflow_data = WorkflowData(
            workflow_id=self.workflow_id,
            data=initial_data,
            metadata={},
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now()
        )
        
        self.status = WorkflowStatus.ACTIVE
        self.started_at = datetime.datetime.now()
        
        # Ejecutar primer paso
        if self.step_sequence:
            return self._execute_step(self.step_sequence[0])
        
        return False
    
    def _execute_step(self, step_id: str) -> bool:
        """Ejecuta un paso específico."""
        if step_id not in self.steps:
            return False
        
        step = self.steps[step_id]
        self.current_step = step_id
        
        # Verificar si el paso puede ejecutarse
        if not step.can_execute(self.workflow_data):
            return False
        
        self.step_started.emit(self.workflow_id, step_id)
        
        # Ejecutar el paso
        result = step.execute(self.workflow_data)
        
        # Registrar en historial
        self.history.append({
            'step_id': step_id,
            'step_name': step.name,
            'timestamp': datetime.datetime.now(),
            'result': asdict(result)
        })
        
        # Actualizar datos del workflow si el paso fue exitoso
        if result.success and result.data:
            self.workflow_data.data.update(result.data)
            self.workflow_data.updated_at = datetime.datetime.now()
        
        self.step_completed.emit(self.workflow_id, step_id, result.success)
        
        # Determinar siguiente paso
        if result.success:
            if step.approval_required and step.status == StepStatus.IN_PROGRESS:
                # Paso requiere aprobación
                self.approval_required.emit(self.workflow_id, step_id, 
                                          getattr(step, 'approvers', []))
                return True
            else:
                # Continuar al siguiente paso
                return self._continue_to_next_step(result)
        else:
            # Error en el paso
            self.status = WorkflowStatus.ERROR
            return False
    
    def _continue_to_next_step(self, step_result: StepResult) -> bool:
        """Continúa al siguiente paso del workflow."""
        current_index = self.step_sequence.index(self.current_step)
        
        # Determinar siguiente paso
        if step_result.next_step:
            # Paso específico indicado por el resultado
            next_step = step_result.next_step
        elif current_index + 1 < len(self.step_sequence):
            # Siguiente paso en secuencia
            next_step = self.step_sequence[current_index + 1]
        else:
            # No hay más pasos - workflow completado
            self._complete_workflow()
            return True
        
        # Ejecutar siguiente paso
        return self._execute_step(next_step)
    
    def _complete_workflow(self):
        """Completa el workflow."""
        self.status = WorkflowStatus.COMPLETED
        self.completed_at = datetime.datetime.now()
        self.workflow_completed.emit(self.workflow_id)
    
    def approve_step(self, step_id: str, approver: str, comments: str = "") -> bool:
        """Aprueba un paso del workflow."""
        if step_id not in self.steps:
            return False
        
        step = self.steps[step_id]
        
        if isinstance(step, ApprovalStep):
            approved = step.add_approval(approver, comments)
            if approved:
                # Continuar workflow después de aprobación
                result = StepResult(success=True, message="Aprobado", data={})
                return self._continue_to_next_step(result)
        else:
            approved = step.approve(approver, comments)
            if approved:
                result = StepResult(success=True, message="Aprobado", data={})
                return self._continue_to_next_step(result)
        
        return False
    
    def reject_step(self, step_id: str, approver: str, comments: str = "") -> bool:
        """Rechaza un paso del workflow."""
        if step_id not in self.steps:
            return False
        
        step = self.steps[step_id]
        
        if isinstance(step, ApprovalStep):
            step.add_rejection(approver, comments)
        else:
            step.reject(approver, comments)
        
        # Workflow se pausa o cancela según configuración
        self.status = WorkflowStatus.PAUSED
        return True
    
    def pause(self):
        """Pausa el workflow."""
        if self.status == WorkflowStatus.ACTIVE:
            self.status = WorkflowStatus.PAUSED
            return True
        return False
    
    def resume(self):
        """Reanuda el workflow."""
        if self.status == WorkflowStatus.PAUSED:
            self.status = WorkflowStatus.ACTIVE
            # Continuar desde el paso actual
            if self.current_step:
                return self._execute_step(self.current_step)
        return False
    
    def cancel(self):
        """Cancela el workflow."""
        if self.status in [WorkflowStatus.ACTIVE, WorkflowStatus.PAUSED]:
            self.status = WorkflowStatus.CANCELLED
            return True
        return False
    
    def get_progress(self) -> Dict[str, Any]:
        """Retorna el progreso actual del workflow."""
        total_steps = len(self.step_sequence)
        completed_steps = sum(1 for step_id in self.step_sequence 
                            if self.steps[step_id].status in 
                            [StepStatus.COMPLETED, StepStatus.APPROVED])
        
        return {
            'total_steps': total_steps,
            'completed_steps': completed_steps,
            'progress_percentage': (completed_steps / total_steps * 100) if total_steps > 0 else 0,
            'current_step': self.current_step,
            'status': self.status.value,
            'started_at': self.started_at,
            'completed_at': self.completed_at
        }


class WorkflowEngine(QObject):
    """Motor principal de workflows."""
    
    def __init__(self):
        super().__init__()
        self.workflows: Dict[str, Workflow] = {}
        self.templates: Dict[str, Dict] = {}
    
    def register_workflow_template(self, template_name: str, template_data: Dict):
        """Registra una plantilla de workflow."""
        self.templates[template_name] = template_data
    
    def create_workflow_from_template(self, template_name: str, workflow_id: str, 
                                    name: str, **kwargs) -> Optional[Workflow]:
        """Crea un workflow desde una plantilla."""
        if template_name not in self.templates:
            return None
        
        template = self.templates[template_name]
        workflow = Workflow(workflow_id, name, template.get('description', ''))
        
        # Agregar pasos según la plantilla
        for step_config in template.get('steps', []):
            step = self._create_step_from_config(step_config, **kwargs)
            if step:
                workflow.add_step(step)
        
        self.workflows[workflow_id] = workflow
        return workflow
    
    def _create_step_from_config(self, config: Dict, **kwargs) -> Optional[BaseWorkflowStep]:
        """Crea un paso desde configuración."""
        step_type = config.get('type')
        
        if step_type == 'approval':
            return ApprovalStep(
                config['id'],
                config['name'],
                config.get('approvers', []),
                config.get('description', ''),
                config.get('required_approvals', 1)
            )
        elif step_type == 'automated':
            # Las funciones se pasarían en kwargs
            action_function = kwargs.get(f"{config['id']}_function")
            if action_function:
                return AutomatedStep(
                    config['id'],
                    config['name'],
                    action_function,
                    config.get('description', ''),
                    config.get('parameters', {})
                )
        elif step_type == 'conditional':
            condition_function = kwargs.get(f"{config['id']}_condition")
            if condition_function:
                return ConditionalStep(
                    config['id'],
                    config['name'],
                    condition_function,
                    config['true_step'],
                    config['false_step'],
                    config.get('description', '')
                )
        
        return None
    
    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Obtiene un workflow por ID."""
        return self.workflows.get(workflow_id)
    
    def get_active_workflows(self) -> List[Workflow]:
        """Retorna lista de workflows activos."""
        return [wf for wf in self.workflows.values() 
                if wf.status == WorkflowStatus.ACTIVE]
    
    def get_pending_approvals(self, approver: str) -> List[Dict]:
        """Retorna aprobaciones pendientes para un usuario."""
        pending = []
        
        for workflow in self.workflows.values():
            for step_id, step in workflow.steps.items():
                if (step.approval_required and 
                    step.status == StepStatus.IN_PROGRESS and
                    hasattr(step, 'approvers') and
                    approver in step.approvers):
                    
                    pending.append({
                        'workflow_id': workflow.workflow_id,
                        'workflow_name': workflow.name,
                        'step_id': step_id,
                        'step_name': step.name,
                        'description': step.description
                    })
        
        return pending


# Instancia global del motor de workflows
workflow_engine = WorkflowEngine()