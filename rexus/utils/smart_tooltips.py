"""
Sistema de Tooltips Inteligentes para Rexus.app

Proporciona tooltips contextuales y dinámicos para mejorar la experiencia del usuario.
"""

import logging
from typing import Dict, Optional


class SmartTooltips:
    """
    Sistema de tooltips inteligentes para Rexus.app
    """

    # Base de datos de tooltips por módulo
    OBRAS_TOOLTIPS = {
        'btn_nueva_obra': 'Crear una nueva obra o proyecto',
        'btn_editar_obra': 'Editar los datos de la obra seleccionada',
        'btn_eliminar_obra': 'Eliminar permanentemente la obra seleccionada',
        'input_codigo_obra': 'Código único de identificación de la obra',
        'input_nombre_obra': 'Nombre descriptivo de la obra',
        'combo_estado_obra': 'Estado actual de la obra (Activa, Pausada, Finalizada)',
        'fecha_inicio': 'Fecha de inicio planificada de la obra',
        'fecha_fin': 'Fecha de finalización estimada de la obra',
    }

    INVENTARIO_TOOLTIPS = {
        'btn_nuevo_item': 'Agregar un nuevo artículo al inventario',
        'btn_editar_item': 'Modificar los datos del artículo seleccionado',
        'input_codigo_item': 'Código único del artículo (SKU)',
        'input_stock_actual': 'Cantidad actual en stock',
        'input_stock_minimo': 'Cantidad mínima para alertas de reposición',
    }

    HERRAJES_TOOLTIPS = {
        'btn_nuevo_herraje': 'Agregar un nuevo herraje al catálogo',
        'input_codigo_herraje': 'Código único del herraje',
        'combo_categoria_herraje': 'Categoría del herraje (Bisagras, Cerraduras, etc.)',
        'input_precio_herraje': 'Precio unitario del herraje',
    }

    USUARIOS_TOOLTIPS = {
        'btn_nuevo_usuario': 'Crear una nueva cuenta de usuario',
        'btn_editar_usuario': 'Modificar los datos del usuario seleccionado',
        'input_username': 'Nombre de usuario único para el sistema',
        'input_email': 'Dirección de correo electrónico del usuario',
        'combo_rol': 'Rol y permisos del usuario en el sistema',
        'btn_cambiar_password': 'Cambiar la contraseña del usuario',
    }

    PEDIDOS_TOOLTIPS = {
        'btn_nuevo_pedido': 'Crear un nuevo pedido de materiales',
        'btn_aprobar_pedido': 'Aprobar el pedido para procesamiento',
        'input_fecha_entrega': 'Fecha estimada de entrega del pedido',
        'combo_proveedor': 'Proveedor seleccionado para el pedido',
        'input_total_pedido': 'Monto total del pedido incluyendo IVA',
    }

    def __init__(self):
        """Inicializar el sistema de tooltips"""
        self.logger = logging.getLogger(__name__)
        self._tooltips_cache = {}

        # Combinar todos los tooltips en un diccionario maestro
        self._all_tooltips = {}
        self._all_tooltips.update(self.OBRAS_TOOLTIPS)
        self._all_tooltips.update(self.INVENTARIO_TOOLTIPS)
        self._all_tooltips.update(self.HERRAJES_TOOLTIPS)
        self._all_tooltips.update(self.USUARIOS_TOOLTIPS)
        self._all_tooltips.update(self.PEDIDOS_TOOLTIPS)

    def get_tooltip(self, widget_id: str, module: Optional[str] = None) -> str:
        """
        Obtiene el tooltip para un widget específico

        Args:
            widget_id: ID del widget
            module: Módulo específico (opcional)

        Returns:
            str: Texto del tooltip o cadena vacía si no se encuentra
        """
        try:
            # Buscar en cache primero
            cache_key = f"{module}_{widget_id}" if module else widget_id
            if cache_key in self._tooltips_cache:
                return self._tooltips_cache[cache_key]

            # Buscar en el diccionario maestro
            tooltip = self._all_tooltips.get(widget_id, "")

            # Si no se encuentra y se especificó módulo, buscar en módulo específico
            if not tooltip and module:
                module_tooltips = self._get_module_tooltips(module)
                tooltip = module_tooltips.get(widget_id, "")

            # Cachear el resultado
            self._tooltips_cache[cache_key] = tooltip

            return tooltip

        except Exception as e:
            self.logger.error(f"Error al obtener tooltip para {widget_id}: {str(e)}")
            return ""

    def _get_module_tooltips(self, module: str) -> Dict[str, str]:
        """
        Obtiene los tooltips para un módulo específico

        Args:
            module: Nombre del módulo

        Returns:
            dict: Diccionario de tooltips del módulo
        """
        module_map = {
            'obras': self.OBRAS_TOOLTIPS,
            'inventario': self.INVENTARIO_TOOLTIPS,
            'herrajes': self.HERRAJES_TOOLTIPS,
            'usuarios': self.USUARIOS_TOOLTIPS,
            'pedidos': self.PEDIDOS_TOOLTIPS,
        }

        return module_map.get(module.lower(), {})

    def get_all_tooltips(self, module: Optional[str] = None) -> Dict[str, str]:
        """
        Obtiene todos los tooltips, opcionalmente filtrados por módulo

        Args:
            module: Módulo para filtrar (opcional)

        Returns:
            dict: Diccionario de tooltips
        """
        if module:
            return self._get_module_tooltips(module).copy()
        else:
            return self._all_tooltips.copy()

    def add_custom_tooltip(self, widget_id: str, tooltip: str, module: Optional[str] = None):
        """
        Agrega un tooltip personalizado

        Args:
            widget_id: ID del widget
            tooltip: Texto del tooltip
            module: Módulo (opcional)
        """
        try:
            cache_key = f"{module}_{widget_id}" if module else widget_id
            self._all_tooltips[widget_id] = tooltip
            self._tooltips_cache[cache_key] = tooltip

            self.logger.info(f"Tooltip personalizado agregado: {widget_id}")

        except Exception as e:
            self.logger.error(f"Error al agregar tooltip personalizado: {str(e)}")

    def clear_cache(self):
        """Limpia la cache de tooltips"""
        self._tooltips_cache.clear()
        self.logger.info("Cache de tooltips limpiada")

    def get_contextual_help(self, context: str) -> str:
        """
        Obtiene ayuda contextual basada en el contexto actual

        Args:
            context: Contexto actual de la aplicación

        Returns:
            str: Texto de ayuda contextual
        """
        help_texts = {
            'obras_dashboard': 'Panel principal de obras. Use los botones para gestionar proyectos.',
            'inventario_bajo': 'Algunos artículos están por debajo del stock mínimo.',
            'pedidos_pendientes': 'Hay pedidos pendientes de aprobación.',
            'usuarios_activos': 'Vista de usuarios activos en el sistema.',
        }

        return help_texts.get(context, 'Ayuda no disponible para este contexto.')


# Instancia global para uso fácil
smart_tooltips = SmartTooltips()


def get_tooltip(widget_id: str, module: Optional[str] = None) -> str:
    """
    Función de conveniencia para obtener tooltips

    Args:
        widget_id: ID del widget
        module: Módulo (opcional)

    Returns:
        str: Texto del tooltip
    """
    return smart_tooltips.get_tooltip(widget_id, module)


def setup_widget_tooltips(widget, widget_id: str, module: Optional[str] = None):
    """
    Configura tooltips para un widget PyQt

    Args:
        widget: Widget PyQt
        widget_id: ID del widget
        module: Módulo (opcional)
    """
    try:
        tooltip = get_tooltip(widget_id, module)
        if tooltip:
            widget.setToolTip(tooltip)
    except (AttributeError, TypeError):
        # Silenciar errores en configuración de tooltips
        pass
