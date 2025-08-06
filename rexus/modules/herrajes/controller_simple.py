"""
Controlador simple para el módulo de herrajes
"""

from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal


class HerrajesControllerSimple(QObject):
    """Controlador simplificado para herrajes."""

    # Señales
    datos_cargados = pyqtSignal(list)
    error_ocurrido = pyqtSignal(str)

    def __init__(self, model=None):
        super().__init__()
        self.model = model
        self.view = None

    def set_view(self, view):
        """Establece la vista."""
        self.view = view

    def cargar_datos_iniciales(self):
        """Carga los datos iniciales de herrajes."""
        try:
            # Datos de ejemplo
            datos_ejemplo = [
                {
                    "codigo": "BIS001",
                    "nombre": "Bisagra Piano 1.5m",
                    "tipo": "Bisagras",
                    "stock": 25,
                    "precio_unitario": 45.50,
                    "proveedor": "Herrajes del Sur",
                    "activo": True,
                    "ultima_actualizacion": "2024-01-15",
                },
                {
                    "codigo": "CER002",
                    "nombre": "Cerradura Multipunto",
                    "tipo": "Cerraduras",
                    "stock": 8,
                    "precio_unitario": 125.00,
                    "proveedor": "Security Plus",
                    "activo": True,
                    "ultima_actualizacion": "2024-01-14",
                },
                {
                    "codigo": "MAN003",
                    "nombre": "Manija Aluminio Cromada",
                    "tipo": "Manijas",
                    "stock": 0,
                    "precio_unitario": 32.75,
                    "proveedor": "Aluminio SA",
                    "activo": True,
                    "ultima_actualizacion": "2024-01-10",
                },
            ]

            self.datos_cargados.emit(datos_ejemplo)

        except Exception as e:
            self.error_ocurrido.emit(f"Error cargando datos: {e}")

    def buscar_herrajes(self, termino):
        """Busca herrajes por término."""
        # Implementación simplificada
        pass

    def aplicar_filtros(self, filtros):
        """Aplica filtros a los herrajes."""
        # Implementación simplificada
        pass
