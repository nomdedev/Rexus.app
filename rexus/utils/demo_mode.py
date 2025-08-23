"""
Modo Demo para Rexus.app

Sistema que proporciona datos falsos cuando no hay conexión a BD
o cuando se habilita explícitamente el modo demo.
"""


import logging
logger = logging.getLogger(__name__)

import os
import random
                        usuarios_demo = self.get_demo_usuarios()
            user_data = next((u for u in usuarios_demo if u["username"] == username), None)

            if user_data:
                # Actualizar último login
                user_data["ultimo_login"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                return user_data

        return None


# Instancia global del proveedor demo
demo_provider = DemoDataProvider()


def get_demo_data(modulo: str, **kwargs) -> List[Dict[str, Any]]:
    """
    Función de conveniencia para obtener datos demo de cualquier módulo.

    Args:
        modulo: Nombre del módulo (usuarios, obras, inventario, etc.)
        **kwargs: Parámetros adicionales para filtros

    Returns:
        Lista de datos demo para el módulo especificado
    """
    if not demo_provider.is_demo_mode():
        return []

    method_map = {
        "usuarios": demo_provider.get_demo_usuarios,
        "obras": demo_provider.get_demo_obras,
        "inventario": demo_provider.get_demo_inventario,
        "compras": demo_provider.get_demo_compras,
        "logistica": demo_provider.get_demo_logistica
    }

    method = method_map.get(modulo)
    if method:
        data = method()

        # Aplicar filtros básicos si se proporcionan
        if "limit" in kwargs:
            data = data[:kwargs["limit"]]

        if "estado" in kwargs:
            data = [item for item in data if item.get("estado") == kwargs["estado"]]

        return data

    return []


def is_demo_mode_active() -> bool:
    """Verifica si el modo demo está activo."""
    return demo_provider.is_demo_mode()


def enable_demo_mode():
    """Habilita el modo demo."""
    os.environ['REXUS_MODO_DEMO'] = 'true'
    demo_provider.demo_mode_enabled = True


def disable_demo_mode():
    """Deshabilita el modo demo."""
    os.environ['REXUS_MODO_DEMO'] = 'false'
    demo_provider.demo_mode_enabled = False
