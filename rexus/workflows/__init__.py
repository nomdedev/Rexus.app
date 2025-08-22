# -*- coding: utf-8 -*-
"""
Sistema de Workflows - Rexus.app
Automatización de procesos empresariales
"""

from .workflow_engine import (
    WorkflowStatus,
    StepStatus, 
    WorkflowData,
    StepResult,
    BaseWorkflowStep,
    ApprovalStep,
    AutomatedStep,
    ConditionalStep,
    Workflow,
    WorkflowEngine,
    workflow_engine
)

__all__ = [
    'WorkflowStatus',
    'StepStatus',
    'WorkflowData', 
    'StepResult',
    'BaseWorkflowStep',
    'ApprovalStep',
    'AutomatedStep',
    'ConditionalStep',
    'Workflow',
    'WorkflowEngine',
    'workflow_engine'
]