"""
Utilidades para manejo de módulos y normalización de nombres.
"""


import logging
logger = logging.getLogger(__name__)

import unicodedata
from typing import Dict, Any


def normalize_module_name(name: str) -> str:
    """
    Normaliza nombres de módulos eliminando tildes y espacios.

    Args:
        name: Nombre del módulo original

    Returns:
        str: Nombre normalizado
    """
    # Remover tildes
    normalized = unicodedata.normalize('NFD', name)
    without_accents = ''.join(char for char in normalized
                             if unicodedata.category(char) != 'Mn')

    # Convertir a minúsculas y remover espacios
    return without_accents.lower().replace(' ', '_')


def get_module_display_name(internal_name: str) -> str:
    """
    Convierte nombre interno a nombre para mostrar.

    Args:
        internal_name: Nombre interno del módulo

    Returns:
        str: Nombre para mostrar en UI
    """
    display_map = {
        'usuarios': 'Usuarios',
        'obras': 'Obras',
        'inventario': 'Inventario',
        'compras': 'Compras',
        'pedidos': 'Pedidos',
        'logistica': 'Logística',
        'herrajes': 'Herrajes',
        'vidrios': 'Vidrios',
        'mantenimiento': 'Mantenimiento',
        'auditoria': 'Auditoría',
        'administracion': 'Administración',
        'contabilidad': 'Contabilidad',
        'configuracion': 'Configuración'
    }

    return display_map.get(internal_name, internal_name.title())


class ModuleRegistry:
    """
    Registro centralizado de módulos para evitar inconsistencias.
    """

    _modules = {
        'usuarios': {
            'display_name': 'Usuarios',
            'factory_method': '_create_usuarios_module',
            'icon': 'users.svg',
            'description': 'Gestión de usuarios y permisos'
        },
        'obras': {
            'display_name': 'Obras',
            'factory_method': '_create_obras_module',
            'icon': 'obras.svg',
            'description': 'Gestión de obras y proyectos'
        },
        'inventario': {
            'display_name': 'Inventario',
            'factory_method': '_create_inventario_module',
            'icon': 'inventory.svg',
            'description': 'Control de inventario y stock'
        },
        'compras': {
            'display_name': 'Compras',
            'factory_method': '_create_compras_module',
            'icon': 'compras.svg',
            'description': 'Gestión de compras y proveedores'
        },
        'pedidos': {
            'display_name': 'Pedidos',
            'factory_method': '_create_pedidos_module',
            'icon': 'pedido-material.svg',
            'description': 'Gestión de pedidos de material'
        },
        'logistica': {
            'display_name': 'Logística',
            'factory_method': '_create_logistica_module',
            'icon': 'logistica.svg',
            'description': 'Gestión logística y distribución'
        },
        'herrajes': {
            'display_name': 'Herrajes',
            'factory_method': '_create_herrajes_module',
            'icon': 'herrajes.svg',
            'description': 'Gestión de herrajes'
        },
        'vidrios': {
            'display_name': 'Vidrios',
            'factory_method': '_create_vidrios_module',
            'icon': 'vidrios.svg',
            'description': 'Gestión de vidrios'
        },
        'mantenimiento': {
            'display_name': 'Mantenimiento',
            'factory_method': '_create_mantenimiento_module',
            'icon': 'mantenimiento.svg',
            'description': 'Mantenimiento del sistema'
        },
        'auditoria': {
            'display_name': 'Auditoría',
            'factory_method': '_create_auditoria_module',
            'icon': 'auditoria.svg',
            'description': 'Auditoría y logs del sistema'
        },
        'administracion': {
            'display_name': 'Administración',
            'factory_method': '_create_administracion_module',
            'icon': 'configuration.svg',
            'description': 'Administración general'
        },
        'contabilidad': {
            'display_name': 'Contabilidad',
            'factory_method': '_create_contabilidad_module',
            'icon': 'contabilidad.svg',
            'description': 'Gestión contable'
        },
        'configuracion': {
            'display_name': 'Configuración',
            'factory_method': '_create_configuracion_module',
            'icon': 'settings_icon.svg',
            'description': 'Configuración del sistema'
        }
    }

    @classmethod
    def get_all_modules(cls) -> Dict[str, Dict[str, Any]]:
        """Retorna todos los módulos registrados."""
        return cls._modules.copy()

    @classmethod
    def get_module_info(cls, module_key: str) -> Dict[str, Any]:
        """Retorna información de un módulo específico."""
        return cls._modules.get(module_key, {})

    @classmethod
    def get_display_name(cls, module_key: str) -> str:
        """Retorna el nombre para mostrar de un módulo."""
        return cls._modules.get(module_key, {}).get('display_name', module_key.title())

    @classmethod
    def get_factory_method(cls, module_key: str) -> str:
        """Retorna el método del factory para un módulo."""
        return cls._modules.get(module_key, {}).get('factory_method', '')

    @classmethod
    def normalize_and_find(cls, input_name: str) -> str:
        """
        Normaliza un nombre de entrada y encuentra el módulo correspondiente.

        Args:
            input_name: Nombre de entrada (puede tener tildes, espacios, etc.)

        Returns:
            str: Clave del módulo encontrado o cadena vacía si no existe
        """
        normalized_input = normalize_module_name(input_name)

        # Buscar coincidencia directa
        if normalized_input in cls._modules:
            return normalized_input

        # Buscar por nombre de display normalizado
        for key, info in cls._modules.items():
            if normalize_module_name(info['display_name']) == normalized_input:
                return key

        return ""


# Instancia global para fácil acceso
module_registry = ModuleRegistry()
