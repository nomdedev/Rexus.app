"""
Services Layer - Capa de Lógica de Negocio

Esta capa contiene la lógica de negocio de la aplicación, coordinando
operaciones entre múltiples repositorios y aplicando reglas de negocio.

Separación de responsabilidades:
- Repositories: Acceso a datos (CRUD)
- Services: Lógica de negocio (reglas, validaciones, workflows)
"""

from .base import BaseService

__all__ = ['BaseService']
