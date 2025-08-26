#!/usr/bin/env python3
"""
COMPONENTE DE PAGINACIÓN PARA OBRAS
==================================

Widget reutilizable para manejar paginación en la tabla de obras.
"""


import logging
logger = logging.getLogger(__name__)

from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
                            QLabel, QComboBox, QSpinBox, QFrame)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont
from rexus.ui.components.base_components import RexusLabel


class PaginacionWidget(QWidget):
    """Widget para manejo de paginación."""

    # Señales
    pagina_cambiada = pyqtSignal(int)  # Número de página
    items_por_pagina_cambiado = pyqtSignal(int)  # Items por página

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pagina_actual = 1
        self.total_items = 0
        self.items_por_pagina = 50
        self.total_paginas = 0

        self.setup_ui()
        self.conectar_señales()
        self.actualizar_estado()

    def setup_ui(self):
        """Configurar la interfaz de usuario."""
        layout_principal = QHBoxLayout(self)
        layout_principal.setContentsMargins(5, 5, 5, 5)
        layout_principal.setSpacing(10)

        # Frame contenedor
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.StyledPanel)
        layout_frame = QHBoxLayout(frame)

        # Información de página
        self.lbl_info_pagina = RexusLabel("Página 1 de 1", "subtitle")
        layout_frame.addWidget(self.lbl_info_pagina)

        layout_frame.addStretch()

        # Botones de navegación
        self.btn_primera = QPushButton("<<")
        self.btn_primera.setMaximumWidth(40)
        self.btn_primera.setToolTip("Primera página")
        layout_frame.addWidget(self.btn_primera)

        self.btn_anterior = QPushButton("<")
        self.btn_anterior.setMaximumWidth(40)
        self.btn_anterior.setToolTip("Página anterior")
        layout_frame.addWidget(self.btn_anterior)

        # Selector de página
        layout_frame.addWidget(RexusLabel("Página:", "body"))
        self.spin_pagina = QSpinBox()
        self.spin_pagina.setMinimum(1)
        self.spin_pagina.setMaximum(1)
        self.spin_pagina.setMaximumWidth(80)
        layout_frame.addWidget(self.spin_pagina)

        self.btn_siguiente = QPushButton(">")
        self.btn_siguiente.setMaximumWidth(40)
        self.btn_siguiente.setToolTip("Página siguiente")
        layout_frame.addWidget(self.btn_siguiente)

        self.btn_ultima = QPushButton(">>")
        self.btn_ultima.setMaximumWidth(40)
        self.btn_ultima.setToolTip("Última página")
        layout_frame.addWidget(self.btn_ultima)

        layout_frame.addStretch()

        # Selector de items por página
        layout_frame.addWidget(RexusLabel("Mostrar:", "body"))
        self.combo_items_pagina = QComboBox()
        self.combo_items_pagina.addItems(["25", "50", "100", "200"])
        self.combo_items_pagina.setCurrentText("50")
        self.combo_items_pagina.setMaximumWidth(80)
        layout_frame.addWidget(self.combo_items_pagina)
        layout_frame.addWidget(RexusLabel("por página", "body"))

        layout_frame.addStretch()

        # Información de registros
        self.lbl_info_registros = RexusLabel("0 registros", "caption")
        layout_frame.addWidget(self.lbl_info_registros)

        layout_principal.addWidget(frame)

        # Estilos
        self.setStyleSheet("""
            PaginacionWidget {
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #ffffff;
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #e7f3ff;
                border-color: #0078d4;
            }
            QPushButton:pressed {
                background-color: #deecf9;
            }
            QPushButton:disabled {
                background-color: #f0f0f0;
                color: #999;
                border-color: #ddd;
            }
            QSpinBox, QComboBox {
                background-color: #ffffff;
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 3px;
            }
        """)

    def conectar_señales(self):
        """Conectar señales de los widgets."""
        self.btn_primera.clicked.connect(self.ir_primera_pagina)
        self.btn_anterior.clicked.connect(self.ir_pagina_anterior)
        self.btn_siguiente.clicked.connect(self.ir_pagina_siguiente)
        self.btn_ultima.clicked.connect(self.ir_ultima_pagina)

        self.spin_pagina.valueChanged.connect(self.cambiar_pagina)
        self.combo_items_pagina.currentTextChanged.connect(self.cambiar_items_por_pagina)

    def actualizar_datos(self, total_items: int, pagina_actual: int = None):
        """
        Actualizar datos de paginación.

        Args:
            total_items: Total de elementos
            pagina_actual: Página actual (opcional)
        """
        self.total_items = total_items

        if pagina_actual is not None:
            self.pagina_actual = pagina_actual

        # Calcular total de páginas
        if self.items_por_pagina > 0:
            self.total_paginas = max(1, (total_items + self.items_por_pagina - 1) // self.items_por_pagina)
        else:
            self.total_paginas = 1

        # Ajustar página actual si es necesario
        if self.pagina_actual > self.total_paginas:
            self.pagina_actual = self.total_paginas
        elif self.pagina_actual < 1:
            self.pagina_actual = 1

        self.actualizar_estado()

    def actualizar_estado(self):
        """Actualizar estado de los controles."""
        # Actualizar información de página
        self.lbl_info_pagina.setText(f"Página {self.pagina_actual} de {self.total_paginas}")

        # Actualizar información de registros
        inicio = (self.pagina_actual - 1) * self.items_por_pagina + 1
        fin = min(self.pagina_actual * self.items_por_pagina, self.total_items)

        if self.total_items == 0:
            self.lbl_info_registros.setText("0 registros")
        else:
            self.lbl_info_registros.setText(f"Mostrando {inicio}-{fin} de {self.total_items} registros")

        # Actualizar spinbox
        self.spin_pagina.blockSignals(True)
        self.spin_pagina.setMaximum(max(1, self.total_paginas))
        self.spin_pagina.setValue(self.pagina_actual)
        self.spin_pagina.blockSignals(False)

        # Actualizar estado de botones
        hay_anterior = self.pagina_actual > 1
        hay_siguiente = self.pagina_actual < self.total_paginas

        self.btn_primera.setEnabled(hay_anterior)
        self.btn_anterior.setEnabled(hay_anterior)
        self.btn_siguiente.setEnabled(hay_siguiente)
        self.btn_ultima.setEnabled(hay_siguiente)

        # Habilitar/deshabilitar controles si no hay datos
        hay_datos = self.total_items > 0
        self.spin_pagina.setEnabled(hay_datos)
        self.combo_items_pagina.setEnabled(hay_datos)

    def ir_primera_pagina(self):
        """Ir a la primera página."""
        if self.pagina_actual != 1:
            self.pagina_actual = 1
            self.actualizar_estado()
            self.pagina_cambiada.emit(self.pagina_actual)

    def ir_pagina_anterior(self):
        """Ir a la página anterior."""
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self.actualizar_estado()
            self.pagina_cambiada.emit(self.pagina_actual)

    def ir_pagina_siguiente(self):
        """Ir a la página siguiente."""
        if self.pagina_actual < self.total_paginas:
            self.pagina_actual += 1
            self.actualizar_estado()
            self.pagina_cambiada.emit(self.pagina_actual)

    def ir_ultima_pagina(self):
        """Ir a la última página."""
        if self.pagina_actual != self.total_paginas:
            self.pagina_actual = self.total_paginas
            self.actualizar_estado()
            self.pagina_cambiada.emit(self.pagina_actual)

    def cambiar_pagina(self, nueva_pagina: int):
        """
        Cambiar a una página específica.

        Args:
            nueva_pagina: Número de página
        """
        if nueva_pagina != self.pagina_actual and \
            1 <= nueva_pagina <= self.total_paginas:
            self.pagina_actual = nueva_pagina
            self.actualizar_estado()
            self.pagina_cambiada.emit(self.pagina_actual)

    def cambiar_items_por_pagina(self, items_texto: str):
        """
        Cambiar cantidad de items por página.

        Args:
            items_texto: Texto con número de items
        """
        try:
            nuevos_items = int(items_texto)
            if nuevos_items != self.items_por_pagina:
                self.items_por_pagina = nuevos_items

                # Recalcular página actual para mantener posición aproximada
                item_actual = (self.pagina_actual - 1) * self.items_por_pagina + 1
                nueva_pagina = max(1, (item_actual - 1) // nuevos_items + 1)

                self.pagina_actual = nueva_pagina
                self.actualizar_datos(self.total_items, self.pagina_actual)
                self.items_por_pagina_cambiado.emit(self.items_por_pagina)

        except ValueError:
            pass

    def obtener_rango_actual(self):
        """
        Obtener el rango de items para la página actual.

        Returns:
            Tupla (inicio, fin) con índices basados en 0
        """
        inicio = (self.pagina_actual - 1) * self.items_por_pagina
        fin = min(inicio + self.items_por_pagina, self.total_items)
        return inicio, fin

    def reset(self):
        """Resetear paginación a estado inicial."""
        self.pagina_actual = 1
        self.total_items = 0
        self.total_paginas = 0
        self.actualizar_estado()


class FiltrosAvanzadosWidget(QWidget):
    """Widget para filtros avanzados de obras."""

    # Señales
    filtros_cambiados = pyqtSignal(dict)  # Diccionario con filtros
    limpiar_filtros = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.conectar_señales()

    def setup_ui(self):
        """Configurar la interfaz de usuario."""
        layout_principal = QVBoxLayout(self)
        layout_principal.setContentsMargins(10, 10, 10, 10)

        # Título
        titulo = QLabel("Filtros Avanzados")
        font_titulo = QFont()
        font_titulo.setBold(True)
        font_titulo.setPointSize(12)
        titulo.setFont(font_titulo)
        layout_principal.addWidget(titulo)

        # Frame de filtros
        frame_filtros = QFrame()
        frame_filtros.setFrameStyle(QFrame.Shape.StyledPanel)
        layout_filtros = QVBoxLayout(frame_filtros)

        # Primera fila de filtros
        layout_fila1 = QHBoxLayout()

        # Filtro por estado
        layout_fila1.addWidget(QLabel("Estado:"))
        self.combo_estado = QComboBox()
        self.combo_estado.addItems([
            "Todos", "PLANIFICACION", "EN_PROCESO",
            "SUSPENDIDA", "FINALIZADA", "CANCELADA"
        ])
        self.combo_estado.setToolTip("Filtrar obras por estado actual")
        layout_fila1.addWidget(self.combo_estado)

        layout_fila1.addStretch()

        # Filtro por responsable
        layout_fila1.addWidget(QLabel("Responsable:"))
        self.txt_responsable = QLineEdit()
        self.txt_responsable.setPlaceholderText("Nombre del responsable...")
        self.txt_responsable.setToolTip("Buscar por nombre del responsable de la obra")
        self.txt_responsable.setMaximumWidth(200)
        layout_fila1.addWidget(self.txt_responsable)

        layout_filtros.addLayout(layout_fila1)

        # Segunda fila de filtros
        layout_fila2 = QHBoxLayout()

        # Filtro por cliente
        layout_fila2.addWidget(QLabel("Cliente:"))
        self.txt_cliente = QLineEdit()
        self.txt_cliente.setPlaceholderText("Nombre del cliente...")
        self.txt_cliente.setToolTip("Buscar por nombre del cliente")
        self.txt_cliente.setMaximumWidth(200)
        layout_fila2.addWidget(self.txt_cliente)

        layout_fila2.addStretch()

        # Filtro por rango de fechas
        layout_fila2.addWidget(QLabel("Fecha desde:"))
        self.date_desde = QDateEdit()
        self.date_desde.setCalendarPopup(True)
        self.date_desde.setToolTip("Fecha de inicio de búsqueda")
        layout_fila2.addWidget(self.date_desde)

        layout_fila2.addWidget(QLabel("hasta:"))
        self.date_hasta = QDateEdit()
        self.date_hasta.setCalendarPopup(True)
        self.date_hasta.setToolTip("Fecha de fin de búsqueda")
        layout_fila2.addWidget(self.date_hasta)

        layout_filtros.addLayout(layout_fila2)

        # Botones de acción
        layout_botones = QHBoxLayout()
        layout_botones.addStretch()

        self.btn_aplicar = QPushButton("Aplicar Filtros")
        self.btn_aplicar.setToolTip("Aplicar filtros seleccionados")
        layout_botones.addWidget(self.btn_aplicar)

        self.btn_limpiar = QPushButton("Limpiar")
        self.btn_limpiar.setToolTip("Limpiar todos los filtros")
        layout_botones.addWidget(self.btn_limpiar)

        layout_filtros.addLayout(layout_botones)

        layout_principal.addWidget(frame_filtros)

        # Configurar fechas por defecto
        from datetime import date, timedelta
        hoy = date.today()
        hace_un_ano = hoy - timedelta(days=365)

        self.date_desde.setDate(hace_un_ano)
        self.date_hasta.setDate(hoy)

    def conectar_señales(self):
        """Conectar señales de los widgets."""
        self.btn_aplicar.clicked.connect(self.aplicar_filtros)
        self.btn_limpiar.clicked.connect(self.limpiar_filtros_click)

        # Auto-aplicar filtros cuando cambian
        self.combo_estado.currentTextChanged.connect(self.aplicar_filtros)
        self.txt_responsable.textChanged.connect(self.aplicar_filtros)
        self.txt_cliente.textChanged.connect(self.aplicar_filtros)

    def aplicar_filtros(self):
        """Aplicar filtros y emitir señal."""
        filtros = self.obtener_filtros()
        self.filtros_cambiados.emit(filtros)

    def obtener_filtros(self):
        """
        Obtener diccionario con filtros actuales.

        Returns:
            Diccionario con filtros aplicados
        """
        filtros = {}

        # Estado
        estado = self.combo_estado.currentText()
        if estado != "Todos":
            filtros['estado'] = estado

        # Responsable
        responsable = self.txt_responsable.text().strip()
        if responsable:
            filtros['responsable'] = responsable

        # Cliente
        cliente = self.txt_cliente.text().strip()
        if cliente:
            filtros['cliente'] = cliente

        # Fechas
        filtros['fecha_desde'] = self.date_desde.date().toString('yyyy-MM-dd')
        filtros['fecha_hasta'] = self.date_hasta.date().toString('yyyy-MM-dd')

        return filtros

    def limpiar_filtros_click(self):
        """Limpiar todos los filtros."""
        self.combo_estado.setCurrentText("Todos")
        self.txt_responsable.clear()
        self.txt_cliente.clear()

        from datetime import date, timedelta
        hoy = date.today()
        hace_un_ano = hoy - timedelta(days=365)

        self.date_desde.setDate(hace_un_ano)
        self.date_hasta.setDate(hoy)

        self.limpiar_filtros.emit()
        self.aplicar_filtros()


# Importar componentes necesarios para filtros
from PyQt6.QtWidgets import QLineEdit, QDateEdit
