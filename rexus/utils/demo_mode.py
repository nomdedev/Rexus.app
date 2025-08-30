"""
Modo Demo para Rexus.app

Sistema que proporciona datos falsos cuando no hay conexión a BD
o cuando se habilita explícitamente el modo demo.
"""

import logging
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class DemoDataProvider:
    """Proveedor de datos demo para desarrollo y pruebas."""

    def __init__(self):
        self.demo_mode_enabled = os.environ.get('REXUS_MODO_DEMO', 'false').lower() == 'true'

    def is_demo_mode(self) -> bool:
        """Verifica si el modo demo está habilitado."""
        return self.demo_mode_enabled

    def authenticate_demo_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Autentica un usuario en modo demo."""
        usuarios_demo = self.get_demo_usuarios()
        user_data = next((u for u in usuarios_demo if u["username"] == username), None)

        if user_data:
            # Actualizar último login
            user_data["ultimo_login"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            return user_data

        return None

    def get_demo_usuarios(self) -> List[Dict[str, Any]]:
        """Retorna usuarios demo."""
        return [
            {
                "id": 1,
                "username": "admin",
                "password": "admin123",
                "nombre": "Administrador",
                "apellido": "Sistema",
                "email": "admin@rexus.com",
                "rol": "admin",
                "estado": "activo",
                "ultimo_login": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                "id": 2,
                "username": "usuario",
                "password": "user123",
                "nombre": "Usuario",
                "apellido": "Demo",
                "email": "usuario@rexus.com",
                "rol": "usuario",
                "estado": "activo",
                "ultimo_login": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        ]

    def get_demo_obras(self) -> List[Dict[str, Any]]:
        """Retorna obras demo."""
        return [
            {
                "id": 1,
                "nombre": "Edificio Residencial Norte",
                "direccion": "Av. Principal 123",
                "estado": "en_progreso",
                "fecha_inicio": "2024-01-15",
                "fecha_fin_estimada": "2024-12-15",
                "presupuesto": 1500000.00,
                "cliente": "Constructora ABC"
            },
            {
                "id": 2,
                "nombre": "Centro Comercial Sur",
                "direccion": "Calle Comercio 456",
                "estado": "planificacion",
                "fecha_inicio": "2024-03-01",
                "fecha_fin_estimada": "2025-02-28",
                "presupuesto": 2500000.00,
                "cliente": "Inversiones XYZ"
            }
        ]

    def get_demo_inventario(self) -> List[Dict[str, Any]]:
        """Retorna inventario demo."""
        return [
            {
                "id": 1,
                "nombre": "Cemento Portland",
                "categoria": "Materiales",
                "cantidad": 150,
                "unidad": "sacos",
                "precio_unitario": 25.50,
                "proveedor": "Cementos Nacionales"
            },
            {
                "id": 2,
                "nombre": "Varilla de Acero 1/2",
                "categoria": "Acero",
                "cantidad": 200,
                "unidad": "barras",
                "precio_unitario": 15.75,
                "proveedor": "Acero del Valle"
            }
        ]

    def get_demo_compras(self) -> List[Dict[str, Any]]:
        """Retorna compras demo."""
        return [
            {
                "id": 1,
                "proveedor": "Materiales y Construcción SA",
                "fecha": "2024-01-20",
                "total": 12500.00,
                "estado": "recibido",
                "items": ["Cemento", "Arena", "Grava"]
            },
            {
                "id": 2,
                "proveedor": "Ferretería Industrial",
                "fecha": "2024-01-25",
                "total": 8750.00,
                "estado": "pendiente",
                "items": ["Herramientas", "Pinturas"]
            }
        ]

    def get_demo_logistica(self) -> List[Dict[str, Any]]:
        """Retorna datos de logística demo."""
        return [
            {
                "id": 1,
                "tipo": "transporte",
                "origen": "Planta Principal",
                "destino": "Obra Norte",
                "fecha": "2024-01-22",
                "estado": "en_camino",
                "materiales": ["Cemento", "Arena"]
            },
            {
                "id": 2,
                "tipo": "entrega",
                "origen": "Almacén Central",
                "destino": "Obra Sur",
                "fecha": "2024-01-23",
                "estado": "programado",
                "materiales": ["Varillas", "Concreto"]
            }
        ]


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
