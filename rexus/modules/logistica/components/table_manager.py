"""
Table Manager para el módulo de Logística

Maneja todas las operaciones relacionadas con tablas de entregas y transportes.
Extraído de view.py para mejorar la mantenibilidad.
"""


import logging
logger = logging.getLogger(__name__)

from PyQt6.QtWidgets import (
    QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView
)
from PyQt6.QtCore import Qt

class LogisticaTableManager:
    """Gestor de tablas para el módulo de logística."""

    def __init__(self, parent_view):
        """Inicializa el gestor de tablas.
        
        Args:
            parent_view: Vista principal de logística
        """
        self.parent_view = parent_view
        self.tabla_entregas = None
        self.tabla_transportes = None

    def cargar_entregas_en_tabla(self, entregas=None):
        """Carga entregas en la tabla principal."""
        if not self.tabla_entregas:
            return

        # Limpiar tabla
        self.tabla_entregas.setRowCount(0)

        # Usar datos demo si no se proporcionan entregas
        if not entregas:
            entregas = self._get_demo_entregas()

        # Configurar tabla
        self.tabla_entregas.setRowCount(len(entregas))
        self.tabla_entregas.setColumnCount(7)

        headers = [
            "ID", "Cliente", "Dirección", "Estado", 
            "Fecha", "Transportista", "Observaciones"
        ]
        self.tabla_entregas.setHorizontalHeaderLabels(headers)

        # Llenar tabla
        for row, entrega in enumerate(entregas):
            self.tabla_entregas.setItem(row, 0, QTableWidgetItem(str(entrega.get('id', ''))))
            self.tabla_entregas.setItem(row, 1, QTableWidgetItem(entrega.get('cliente', '')))
            self.tabla_entregas.setItem(row, 2, QTableWidgetItem(entrega.get('direccion', '')))
            self.tabla_entregas.setItem(row, 3, QTableWidgetItem(entrega.get('estado', '')))
            self.tabla_entregas.setItem(row, 4, QTableWidgetItem(entrega.get('fecha', '')))
            self.tabla_entregas.setItem(row, 5, QTableWidgetItem(entrega.get('transportista', '')))
            self.tabla_entregas.setItem(row, 6, QTableWidgetItem(entrega.get('observaciones', '')))

        # Ajustar columnas
        header = self.tabla_entregas.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

    def configurar_tabla_transportes(self):
        """Configura la tabla de transportes."""
        if not self.tabla_transportes:
            return

        # Configurar propiedades básicas
        self.tabla_transportes.setAlternatingRowColors(True)
        self.tabla_transportes.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla_transportes.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        
        # Configurar headers
        headers = [
            "ID", "Código", "Tipo", "Proveedor", "Capacidad (kg)",
            "Capacidad (m³)", "Costo/km", "Disponible", "Estado"
        ]
        self.tabla_transportes.setColumnCount(len(headers))
        self.tabla_transportes.setHorizontalHeaderLabels(headers)

        # Cargar datos demo
        transportes_demo = self._get_demo_transportes()
        self.tabla_transportes.setRowCount(len(transportes_demo))

        for row, transporte in enumerate(transportes_demo):
            self.tabla_transportes.setItem(row, 0, QTableWidgetItem(str(transporte.get('id', ''))))
            self.tabla_transportes.setItem(row, 1, QTableWidgetItem(transporte.get('codigo', '')))
            self.tabla_transportes.setItem(row, 2, QTableWidgetItem(transporte.get('tipo', '')))
            self.tabla_transportes.setItem(row, 3, QTableWidgetItem(transporte.get('proveedor', '')))
            self.tabla_transportes.setItem(row, 4, QTableWidgetItem(str(transporte.get('capacidad_kg', ''))))
            self.tabla_transportes.setItem(row, 5, QTableWidgetItem(str(transporte.get('capacidad_m3', ''))))
            self.tabla_transportes.setItem(row, 6, QTableWidgetItem(str(transporte.get('costo_km', ''))))
            self.tabla_transportes.setItem(row, 7, QTableWidgetItem('Sí' if transporte.get('disponible') else 'No'))
            self.tabla_transportes.setItem(row, 8, QTableWidgetItem(transporte.get('estado', '')))

        # Ajustar columnas
        header = self.tabla_transportes.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def _get_demo_entregas(self):
        """Retorna datos demo para entregas."""
        return [
            {
                'id': 'ENT001',
                'cliente': 'Acme Corp',
                'direccion': 'Calle Principal 123',
                'estado': 'Pendiente',
                'fecha': '2024-01-15',
                'transportista': 'Juan Pérez',
                'observaciones': 'Entrega urgente'
            },
            {
                'id': 'ENT002', 
                'cliente': 'Tech Solutions',
                'direccion': 'Av. Tecnología 456',
                'estado': 'En tránsito',
                'fecha': '2024-01-16',
                'transportista': 'María García',
                'observaciones': 'Frágil'
            },
            {
                'id': 'ENT003',
                'cliente': 'Global Industries',
                'direccion': 'Plaza Central 789',
                'estado': 'Entregado',
                'fecha': '2024-01-14',
                'transportista': 'Carlos López',
                'observaciones': 'Completado exitosamente'
            }
        ]

    def _get_demo_transportes(self):
        """Retorna datos demo para transportes."""
        return [
            {
                'id': 1,
                'codigo': 'TRK001',
                'tipo': 'Camión',
                'proveedor': 'Transportes Unidos',
                'capacidad_kg': 5000,
                'capacidad_m3': 25,
                'costo_km': 2.5,
                'disponible': True,
                'estado': 'Activo'
            },
            {
                'id': 2,
                'codigo': 'VAN002',
                'tipo': 'Furgoneta',
                'proveedor': 'Logística Express',
                'capacidad_kg': 1000,
                'capacidad_m3': 8,
                'costo_km': 1.2,
                'disponible': True,
                'estado': 'Activo'
            },
            {
                'id': 3,
                'codigo': 'TRL003',
                'tipo': 'Trailer',
                'proveedor': 'Mega Transport',
                'capacidad_kg': 15000,
                'capacidad_m3': 60,
                'costo_km': 4.0,
                'disponible': False,
                'estado': 'Mantenimiento'
            }
        ]

    def set_tabla_entregas(self, tabla):
        """Establece la referencia a la tabla de entregas."""
        self.tabla_entregas = tabla

    def set_tabla_transportes(self, tabla):
        """Establece la referencia a la tabla de transportes."""
        self.tabla_transportes = tabla

    def buscar_en_tabla_transportes(self, termino_busqueda):
        """Busca en la tabla de transportes por término."""
        if not self.tabla_transportes:
            return

        # Mostrar todas las filas primero
        for row in range(self.tabla_transportes.rowCount()):
            self.tabla_transportes.setRowHidden(row, False)

        # Si no hay término de búsqueda, mostrar todo
        if not termino_busqueda.strip():
            return

        # Ocultar filas que no coinciden
        termino = termino_busqueda.lower()
        for row in range(self.tabla_transportes.rowCount()):
            fila_visible = False
            for col in range(self.tabla_transportes.columnCount()):
                item = self.tabla_transportes.item(row, col)
                if item and termino in item.text().lower():
                    fila_visible = True
                    break
            self.tabla_transportes.setRowHidden(row, not fila_visible)

    def get_transporte_seleccionado(self):
        """Obtiene los datos del transporte seleccionado."""
        if not self.tabla_transportes:
            return None

        current_row = self.tabla_transportes.currentRow()
        if current_row < 0:
            return None

        # Extraer datos de la fila seleccionada
        transporte = {}
        for col in range(self.tabla_transportes.columnCount()):
            item = self.tabla_transportes.item(current_row, col)
            header = self.tabla_transportes.horizontalHeaderItem(col)
            if item and header:
                transporte[header.text().lower().replace(' ', '_')] = item.text()

        return transporte