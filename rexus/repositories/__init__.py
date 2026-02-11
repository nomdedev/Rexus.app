"""
Repositories Layer - Capa de Acceso a Datos

Esta capa proporciona una abstracción sobre el acceso a datos, separando
la lógica de persistencia de la lógica de negocio.

Beneficios:
- Testabilidad: Permite mockear fácilmente en tests
- Mantenibilidad: Centraliza la lógica de acceso a datos
- Flexibilidad: Permite cambiar ORM/BD sin afectar el negocio
"""

from .base import BaseRepository

__all__ = ['BaseRepository']
