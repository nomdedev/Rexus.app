"""Vista de Obras"""

import datetime
from typing import Any, Dict, List, Optional

from PyQt6.QtCore import QDate, Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from src.utils.form_validators import FormValidator, FormValidatorManager
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .cronograma_view import CronogramaObrasView


class ObrasView(QWidget):
    obra_agregada = pyqtSignal(dict)
    obra_editada = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.controller = None
        self.vista_actual = "tabla"  # "tabla" o "cronograma"
        self.init_ui()
        self.configurar_estilos()

    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        # Layout principal
        layout_principal = QVBoxLayout(self)
        layout_principal.setSpacing(10)
        layout_principal.setContentsMargins(10, 10, 10, 10)

        # Título
        self.crear_titulo(layout_principal)

        # Contenedor de vistas con QStackedWidget
        self.stacked_widget = QStackedWidget()

        # Vista de tabla (existente)
        self.vista_tabla = self.crear_vista_tabla()
        self.stacked_widget.addWidget(self.vista_tabla)

        # Vista de cronograma (nueva)
        self.vista_cronograma = CronogramaObrasView()
        self.stacked_widget.addWidget(self.vista_cronograma)

        # Conectar señales del cronograma
        self.vista_cronograma.obra_seleccionada.connect(
            self.on_obra_seleccionada_cronograma
        )
        self.vista_cronograma.btn_alternar_vista.clicked.connect(self.alternar_vista)

        layout_principal.addWidget(self.stacked_widget)

    def crear_titulo(self, layout: QVBoxLayout):
        """Crea el título de la vista."""
        titulo_container = QFrame()
        titulo_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                           stop:0 #3498db, stop:1 #2980b9);
                border-radius: 8px;
                padding: 6px;
                margin-bottom: 10px;
            }
        """)

        titulo_layout = QHBoxLayout(titulo_container)

        # Título principal
        title_label = QLabel("🏗️ Gestión de Obras")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: white;
                background: transparent;
                padding: 0;
                margin: 0;
            }
        """)
        titulo_layout.addWidget(title_label)

        # Botón para alternar entre tabla y cronograma
        self.btn_alternar_vista = QPushButton("📅 Vista Cronograma")
        self.btn_alternar_vista.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
                border-color: rgba(255, 255, 255, 0.5);
            }
        """)
        self.btn_alternar_vista.clicked.connect(self.alternar_vista)
        titulo_layout.addWidget(self.btn_alternar_vista)

        layout.addWidget(titulo_container)

    def crear_vista_tabla(self) -> QWidget:
        """Crea la vista de tabla original."""
        vista_widget = QWidget()
        layout = QVBoxLayout(vista_widget)

        # Splitter horizontal para dividir filtros/estadísticas y tabla
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Panel izquierdo (filtros y estadísticas)
        panel_izquierdo = self.crear_panel_izquierdo()
        splitter.addWidget(panel_izquierdo)

        # Panel derecho (tabla y botones)
        panel_derecho = self.crear_panel_derecho()
        splitter.addWidget(panel_derecho)

        # Configurar proporciones del splitter
        splitter.setStretchFactor(0, 0)  # Panel izquierdo fijo
        splitter.setStretchFactor(1, 1)  # Panel derecho expansible
        splitter.setSizes([300, 800])

        layout.addWidget(splitter)
        return vista_widget

    def mostrar_tabla(self):
        """Muestra la vista de tabla."""
        try:
            self.stacked_widget.setCurrentIndex(0)
            self.btn_alternar_vista.setText("📅 Vista Cronograma")
            print("📊 Vista de tabla activada")
        except Exception as e:
            print(f"Error cambiando a vista tabla: {e}")

    def mostrar_cronograma(self):
        """Muestra la vista de cronograma."""
        try:
            self.stacked_widget.setCurrentIndex(1)
            self.btn_alternar_vista.setText("📊 Vista Tabla")
            # Cargar datos en el cronograma
            self.actualizar_cronograma()
            print("📅 Vista de cronograma activada")
        except Exception as e:
            print(f"Error cambiando a vista cronograma: {e}")

    def alternar_vista(self):
        """Alterna entre vista tabla y cronograma."""
        try:
            if self.stacked_widget.currentIndex() == 0:
                self.mostrar_cronograma()
            else:
                self.mostrar_tabla()
        except Exception as e:
            print(f"Error alternando vista: {e}")

    def actualizar_cronograma(self):
        """Actualiza los datos del cronograma."""
        if hasattr(self, "controller") and self.controller:
            try:
                obras = self.controller.model.obtener_todas_obras()
                self.vista_cronograma.cargar_obras(obras)
            except Exception as e:
                print(f"[ERROR] Error actualizando cronograma: {e}")

    def on_obra_seleccionada_cronograma(self, obra_data: Dict[str, Any]):
        """Maneja la selección de una obra desde el cronograma."""
        print(
            f"[OBRAS VIEW] Obra seleccionada en cronograma: {obra_data.get('codigo', 'Sin código')}"
        )
        # Aquí se puede agregar lógica adicional, como abrir un diálogo de detalles

    def crear_panel_izquierdo(self) -> QWidget:
        """Crea el panel izquierdo con filtros y estadísticas."""
        panel = QWidget()
        panel.setMaximumWidth(300)
        layout = QVBoxLayout(panel)

        # Grupo de filtros
        grupo_filtros = self.crear_grupo_filtros()
        layout.addWidget(grupo_filtros)

        # Grupo de estadísticas
        grupo_estadisticas = self.crear_grupo_estadisticas()
        layout.addWidget(grupo_estadisticas)

        layout.addStretch()
        return panel

    def crear_grupo_filtros(self) -> QGroupBox:
        """Crea el grupo de filtros."""
        grupo = QGroupBox("Filtros")
        layout = QFormLayout(grupo)

        # Filtro por estado
        self.combo_filtro_estado = QComboBox()
        self.combo_filtro_estado.addItems(
            [
                "Todos",
                "PLANIFICACION",
                "EN_PROCESO",
                "PAUSADA",
                "FINALIZADA",
                "CANCELADA",
            ]
        )
        layout.addRow("Estado:", self.combo_filtro_estado)

        # Filtro por responsable
        self.txt_filtro_responsable = QLineEdit()
        self.txt_filtro_responsable.setPlaceholderText("Buscar por responsable...")
        layout.addRow("Responsable:", self.txt_filtro_responsable)

        # Filtro por fecha de inicio
        self.date_filtro_inicio = QDateEdit()
        self.date_filtro_inicio.setDate(QDate.currentDate().addMonths(-1))
        self.date_filtro_inicio.setCalendarPopup(True)
        layout.addRow("Desde:", self.date_filtro_inicio)

        # Filtro por fecha fin
        self.date_filtro_fin = QDateEdit()
        self.date_filtro_fin.setDate(QDate.currentDate().addMonths(3))
        self.date_filtro_fin.setCalendarPopup(True)
        layout.addRow("Hasta:", self.date_filtro_fin)

        # Botón aplicar filtros
        self.btn_aplicar_filtros = QPushButton("Aplicar Filtros")
        self.btn_aplicar_filtros.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        layout.addRow(self.btn_aplicar_filtros)

        return grupo

    def crear_grupo_estadisticas(self) -> QGroupBox:
        """Crea el grupo de estadísticas."""
        grupo = QGroupBox("Estadísticas")
        layout = QVBoxLayout(grupo)

        self.lbl_total_obras = QLabel("Total de obras: 0")
        self.lbl_obras_activas = QLabel("Obras activas: 0")
        self.lbl_presupuesto_total = QLabel("Presupuesto total: $0")

        labels = [
            self.lbl_total_obras,
            self.lbl_obras_activas,
            self.lbl_presupuesto_total,
        ]
        for label in labels:
            label.setStyleSheet("""
                QLabel {
                    padding: 5px;
                    background-color: #ecf0f1;
                    border-radius: 3px;
                    margin: 2px 0;
                }
            """)
            layout.addWidget(label)

        return grupo

    def crear_panel_derecho(self) -> QWidget:
        """Crea el panel derecho con tabla y botones."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Botones de acción
        layout_botones = self.crear_botones_accion()
        layout.addLayout(layout_botones)

        # Tabla de obras
        self.crear_tabla_obras()
        layout.addWidget(self.tabla_obras)

        return panel

    def crear_botones_accion(self) -> QHBoxLayout:
        """Crea los botones de acción."""
        layout = QHBoxLayout()

        # Botón nueva obra
        self.btn_nueva_obra = QPushButton("📄 Nueva Obra")
        self.btn_nueva_obra.setStyleSheet(self.estilo_boton_primario())

        # Botón editar obra
        self.btn_editar_obra = QPushButton("✏️ Editar")
        self.btn_editar_obra.setStyleSheet(self.estilo_boton_secundario())

        # Botón eliminar obra
        self.btn_eliminar_obra = QPushButton("🗑️ Eliminar")
        self.btn_eliminar_obra.setStyleSheet(self.estilo_boton_peligro())

        # Botón cambiar estado
        self.btn_cambiar_estado = QPushButton("🔄 Cambiar Estado")
        self.btn_cambiar_estado.setStyleSheet(self.estilo_boton_secundario())

        # Botón actualizar
        self.btn_actualizar = QPushButton("🔄 Actualizar")
        self.btn_actualizar.setStyleSheet(self.estilo_boton_secundario())

        # Agregar botones al layout
        botones = [
            self.btn_nueva_obra,
            self.btn_editar_obra,
            self.btn_eliminar_obra,
            self.btn_cambiar_estado,
            self.btn_actualizar,
        ]

        for boton in botones:
            boton.setMinimumHeight(35)
            layout.addWidget(boton)

        layout.addStretch()
        return layout

    def crear_tabla_obras(self):
        """Crea la tabla de obras."""
        self.tabla_obras = QTableWidget()

        # Configurar columnas
        columnas = [
            "ID",
            "Código",
            "Nombre",
            "Cliente",
            "Estado",
            "Responsable",
            "Fecha Inicio",
            "Fecha Fin Est.",
            "Presupuesto",
            "Tipo",
        ]
        self.tabla_obras.setColumnCount(len(columnas))
        self.tabla_obras.setHorizontalHeaderLabels(columnas)

        # Configurar comportamiento de la tabla
        self.tabla_obras.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.tabla_obras.setSelectionMode(
            QAbstractItemView.SelectionMode.SingleSelection
        )
        self.tabla_obras.setAlternatingRowColors(True)
        self.tabla_obras.setSortingEnabled(True)

        # Ajustar columnas
        header = self.tabla_obras.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
            header.setStretchLastSection(True)

        # Ocultar columna ID
        self.tabla_obras.setColumnHidden(0, True)

        # Estilos de la tabla
        self.tabla_obras.setStyleSheet("""
            QTableWidget {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)

    def cargar_obras_en_tabla(self, obras: List[Dict[str, Any]]):
        """Carga las obras en la tabla y actualiza el cronograma."""
        self.tabla_obras.setRowCount(len(obras))

        for row, obra in enumerate(obras):
            # ID (oculto)
            self.tabla_obras.setItem(row, 0, QTableWidgetItem(str(obra.get("id", ""))))

            # Código
            self.tabla_obras.setItem(
                row, 1, QTableWidgetItem(str(obra.get("codigo", "")))
            )

            # Nombre
            self.tabla_obras.setItem(
                row, 2, QTableWidgetItem(str(obra.get("nombre", "")))
            )

            # Cliente
            self.tabla_obras.setItem(
                row, 3, QTableWidgetItem(str(obra.get("cliente", "")))
            )

            # Estado con color
            item_estado = QTableWidgetItem(str(obra.get("estado", "")))
            item_estado.setBackground(self.obtener_color_estado(obra.get("estado", "")))
            self.tabla_obras.setItem(row, 4, item_estado)

            # Responsable
            self.tabla_obras.setItem(
                row, 5, QTableWidgetItem(str(obra.get("responsable", "")))
            )

            # Fecha inicio
            fecha_inicio = obra.get("fecha_inicio")
            if fecha_inicio:
                if isinstance(fecha_inicio, datetime.date):
                    fecha_str = fecha_inicio.strftime("%d/%m/%Y")
                else:
                    fecha_str = str(fecha_inicio)[:10]  # Tomar solo la fecha
            else:
                fecha_str = ""
            self.tabla_obras.setItem(row, 6, QTableWidgetItem(fecha_str))

            # Fecha fin estimada
            fecha_fin = obra.get("fecha_fin_estimada")
            if fecha_fin:
                if isinstance(fecha_fin, datetime.date):
                    fecha_str = fecha_fin.strftime("%d/%m/%Y")
                else:
                    fecha_str = str(fecha_fin)[:10]
            else:
                fecha_str = ""
            self.tabla_obras.setItem(row, 7, QTableWidgetItem(fecha_str))

            # Presupuesto
            presupuesto = obra.get("presupuesto_total", 0)
            presupuesto_str = f"${presupuesto:,.2f}" if presupuesto else "$0.00"
            self.tabla_obras.setItem(row, 8, QTableWidgetItem(presupuesto_str))

            # Tipo
            self.tabla_obras.setItem(
                row, 9, QTableWidgetItem(str(obra.get("tipo_obra", "")))
            )

        # Actualizar cronograma también
        self.vista_cronograma.cargar_obras(obras)

        for row, obra in enumerate(obras):
            # ID (oculto)
            self.tabla_obras.setItem(row, 0, QTableWidgetItem(str(obra.get("id", ""))))

            # Código
            self.tabla_obras.setItem(
                row, 1, QTableWidgetItem(str(obra.get("codigo", "")))
            )

            # Nombre
            self.tabla_obras.setItem(
                row, 2, QTableWidgetItem(str(obra.get("nombre", "")))
            )

            # Cliente
            self.tabla_obras.setItem(
                row, 3, QTableWidgetItem(str(obra.get("cliente", "")))
            )

            # Estado con color
            item_estado = QTableWidgetItem(str(obra.get("estado", "")))
            item_estado.setBackground(self.obtener_color_estado(obra.get("estado", "")))
            self.tabla_obras.setItem(row, 4, item_estado)

            # Responsable
            self.tabla_obras.setItem(
                row, 5, QTableWidgetItem(str(obra.get("responsable", "")))
            )

            # Fecha inicio
            fecha_inicio = obra.get("fecha_inicio")
            if fecha_inicio:
                if isinstance(fecha_inicio, datetime.date):
                    fecha_str = fecha_inicio.strftime("%d/%m/%Y")
                else:
                    fecha_str = str(fecha_inicio)[:10]  # Tomar solo la fecha
            else:
                fecha_str = ""
            self.tabla_obras.setItem(row, 6, QTableWidgetItem(fecha_str))

            # Fecha fin estimada
            fecha_fin = obra.get("fecha_fin_estimada")
            if fecha_fin:
                if isinstance(fecha_fin, datetime.date):
                    fecha_str = fecha_fin.strftime("%d/%m/%Y")
                else:
                    fecha_str = str(fecha_fin)[:10]
            else:
                fecha_str = ""
            self.tabla_obras.setItem(row, 7, QTableWidgetItem(fecha_str))

            # Presupuesto
            presupuesto = obra.get("presupuesto_total", 0)
            presupuesto_str = f"${presupuesto:,.2f}" if presupuesto else "$0.00"
            self.tabla_obras.setItem(row, 8, QTableWidgetItem(presupuesto_str))

            # Tipo
            self.tabla_obras.setItem(
                row, 9, QTableWidgetItem(str(obra.get("tipo_obra", "")))
            )

    def obtener_obra_seleccionada(self) -> Optional[Dict[str, Any]]:
        """Obtiene los datos de la obra seleccionada."""
        fila_seleccionada = self.tabla_obras.currentRow()
        if fila_seleccionada < 0:
            return None

        obra = {}
        columnas = [
            "id",
            "codigo",
            "nombre",
            "cliente",
            "estado",
            "responsable",
            "fecha_inicio",
            "fecha_fin_estimada",
            "presupuesto_total",
            "tipo_obra",
        ]

        for i, columna in enumerate(columnas):
            item = self.tabla_obras.item(fila_seleccionada, i)
            if item:
                obra[columna] = item.text()

        return obra

    def obtener_filtros_aplicados(self) -> Dict[str, Any]:
        """Obtiene los filtros aplicados por el usuario."""
        filtros = {}

        estado = self.combo_filtro_estado.currentText()
        if estado != "Todos":
            filtros["estado"] = estado

        responsable = self.txt_filtro_responsable.text().strip()
        if responsable:
            filtros["responsable"] = responsable

        # Fechas
        fecha_inicio_qt = self.date_filtro_inicio.date()
        fecha_fin_qt = self.date_filtro_fin.date()

        filtros["fecha_inicio"] = datetime.date(
            fecha_inicio_qt.year(), fecha_inicio_qt.month(), fecha_inicio_qt.day()
        )
        filtros["fecha_fin"] = datetime.date(
            fecha_fin_qt.year(), fecha_fin_qt.month(), fecha_fin_qt.day()
        )

        return filtros

    def actualizar_estadisticas(self, estadisticas: Dict[str, Any]):
        """Actualiza las estadísticas mostradas."""
        self.lbl_total_obras.setText(
            f"Total de obras: {estadisticas.get('total_obras', 0)}"
        )
        self.lbl_obras_activas.setText(
            f"Obras activas: {estadisticas.get('obras_activas', 0)}"
        )

        presupuesto = estadisticas.get("presupuesto_total", 0)
        self.lbl_presupuesto_total.setText(f"Presupuesto total: ${presupuesto:,.2f}")

    def mostrar_formulario_obra(self, obra_datos: Optional[Dict] = None):
        """Muestra el formulario para crear/editar una obra."""
        dialogo = FormularioObraDialog(self, obra_datos)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            datos = dialogo.obtener_datos()
            if obra_datos:  # Es edición
                if hasattr(self, "controller") and self.controller:
                    self.controller.actualizar_obra(int(obra_datos["id"]), datos)
            else:  # Es creación
                if hasattr(self, "controller") and self.controller:
                    self.controller.crear_obra(datos)

    def mostrar_formulario_edicion_obra(self, obra: Dict[str, Any]):
        """Muestra el formulario de edición para una obra específica."""
        self.mostrar_formulario_obra(obra)

    def mostrar_dialogo_cambiar_estado(self, estado_actual: str) -> Optional[str]:
        """Muestra un diálogo para cambiar el estado de una obra."""
        from PyQt6.QtWidgets import QInputDialog

        estados = ["PLANIFICACION", "EN_PROCESO", "PAUSADA", "FINALIZADA", "CANCELADA"]

        nuevo_estado, ok = QInputDialog.getItem(
            self,
            "Cambiar Estado",
            f"Estado actual: {estado_actual}\nSeleccione el nuevo estado:",
            estados,
            0,
            False,
        )

        return nuevo_estado if ok and nuevo_estado != estado_actual else None

    def obtener_color_estado(self, estado: str):
        """Obtiene el color asociado a un estado."""
        from PyQt6.QtGui import QColor

        colores = {
            "PLANIFICACION": QColor("#f39c12"),  # Naranja
            "EN_PROCESO": QColor("#27ae60"),  # Verde
            "PAUSADA": QColor("#e74c3c"),  # Rojo
            "FINALIZADA": QColor("#2ecc71"),  # Verde claro
            "CANCELADA": QColor("#95a5a6"),  # Gris
        }
        return colores.get(estado, QColor("#bdc3c7"))

    def configurar_estilos(self):
        """Configura los estilos generales de la vista."""
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 12px;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                background-color: white;
            }
        """)

    def estilo_boton_primario(self) -> str:
        return """
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """

    def estilo_boton_secundario(self) -> str:
        return """
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #6c7b7d;
            }
        """

    def estilo_boton_peligro(self) -> str:
        return """
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """

    def set_controller(self, controller):
        """Establece el controlador para esta vista."""
        self.controller = controller

    def mostrar_dialogo_nueva_obra(self):
        """Muestra el diálogo para crear una nueva obra."""
        dialogo = FormularioObraDialog(self)
        if dialogo.exec() == QDialog.DialogCode.Accepted:
            datos_obra = dialogo.obtener_datos()
            if self.controller:
                self.controller.agregar_obra(datos_obra)
                # El método crear_obra ya recarga la tabla automáticamente

    def mostrar_formulario_nueva_obra(self):
        """Alias para mostrar_dialogo_nueva_obra (compatibilidad con controlador)."""
        self.mostrar_dialogo_nueva_obra()


class FormularioObraDialog(QDialog):
    """Diálogo para crear/editar obras."""

    def __init__(self, parent=None, obra_datos: Optional[Dict] = None):
        super().__init__(parent)
        self.obra_datos = obra_datos
        self.es_edicion = obra_datos is not None
        self.validator_manager = FormValidatorManager()
        self.init_ui()
        self.configurar_validaciones()

        if self.es_edicion:
            self.cargar_datos_obra()

    def init_ui(self):
        """Inicializa la interfaz del diálogo."""
        titulo = "Editar Obra" if self.es_edicion else "Nueva Obra"
        self.setWindowTitle(titulo)
        self.setModal(True)
        self.resize(500, 600)

        layout = QVBoxLayout(self)

        # Formulario
        form_layout = QFormLayout()

        # Código (solo en creación)
        if not self.es_edicion:
            self.txt_codigo = QLineEdit()
            self.txt_codigo.setPlaceholderText("Ej: OBR-2024-001")
            form_layout.addRow("Código*:", self.txt_codigo)

        # Nombre
        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText("Nombre de la obra")
        form_layout.addRow("Nombre*:", self.txt_nombre)

        # Cliente
        self.txt_cliente = QLineEdit()
        self.txt_cliente.setPlaceholderText("Nombre del cliente")
        form_layout.addRow("Cliente*:", self.txt_cliente)

        # Descripción
        self.txt_descripcion = QTextEdit()
        self.txt_descripcion.setMaximumHeight(80)
        self.txt_descripcion.setPlaceholderText("Descripción de la obra...")
        form_layout.addRow("Descripción:", self.txt_descripcion)

        # Responsable
        self.txt_responsable = QLineEdit()
        self.txt_responsable.setPlaceholderText("Responsable de la obra")
        form_layout.addRow("Responsable*:", self.txt_responsable)

        # Dirección
        self.txt_direccion = QLineEdit()
        self.txt_direccion.setPlaceholderText("Dirección de la obra")
        form_layout.addRow("Dirección:", self.txt_direccion)

        # Teléfono
        self.txt_telefono = QLineEdit()
        self.txt_telefono.setPlaceholderText("Teléfono de contacto")
        form_layout.addRow("Teléfono:", self.txt_telefono)

        # Email
        self.txt_email = QLineEdit()
        self.txt_email.setPlaceholderText("email@ejemplo.com")
        form_layout.addRow("Email:", self.txt_email)

        # Fecha inicio
        self.date_inicio = QDateEdit()
        self.date_inicio.setDate(QDate.currentDate())
        self.date_inicio.setCalendarPopup(True)
        form_layout.addRow("Fecha Inicio:", self.date_inicio)

        # Fecha fin estimada
        self.date_fin = QDateEdit()
        self.date_fin.setDate(QDate.currentDate().addMonths(6))
        self.date_fin.setCalendarPopup(True)
        form_layout.addRow("Fecha Fin Est.:", self.date_fin)

        # Presupuesto
        self.spin_presupuesto = QDoubleSpinBox()
        self.spin_presupuesto.setRange(0, 999999999)
        self.spin_presupuesto.setDecimals(2)
        self.spin_presupuesto.setSuffix(" $")
        form_layout.addRow("Presupuesto:", self.spin_presupuesto)

        # Tipo de obra
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(
            ["CONSTRUCCION", "RENOVACION", "MANTENIMIENTO", "DEMOLICION", "OTRO"]
        )
        form_layout.addRow("Tipo de Obra:", self.combo_tipo)

        # Prioridad
        self.combo_prioridad = QComboBox()
        self.combo_prioridad.addItems(["BAJA", "MEDIA", "ALTA", "URGENTE"])
        self.combo_prioridad.setCurrentText("MEDIA")
        form_layout.addRow("Prioridad:", self.combo_prioridad)

        # Observaciones
        self.txt_observaciones = QTextEdit()
        self.txt_observaciones.setMaximumHeight(60)
        self.txt_observaciones.setPlaceholderText("Observaciones adicionales...")
        form_layout.addRow("Observaciones:", self.txt_observaciones)

        layout.addLayout(form_layout)

        # Botones
        botones = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        botones.accepted.connect(self.validar_y_aceptar)
        botones.rejected.connect(self.reject)
        layout.addWidget(botones)

    def cargar_datos_obra(self):
        """Carga los datos de la obra en el formulario."""
        if not self.obra_datos:
            return

        self.txt_nombre.setText(self.obra_datos.get("nombre", ""))
        self.txt_cliente.setText(self.obra_datos.get("cliente", ""))
        self.txt_descripcion.setPlainText(self.obra_datos.get("descripcion", ""))
        self.txt_responsable.setText(self.obra_datos.get("responsable", ""))
        self.txt_direccion.setText(self.obra_datos.get("direccion", ""))
        self.txt_telefono.setText(self.obra_datos.get("telefono_contacto", ""))
        self.txt_email.setText(self.obra_datos.get("email_contacto", ""))

        # Fechas
        fecha_inicio = self.obra_datos.get("fecha_inicio")
        if fecha_inicio:
            if isinstance(fecha_inicio, str):
                fecha_inicio = datetime.datetime.strptime(
                    fecha_inicio, "%Y-%m-%d"
                ).date()
            fecha_qt = QDate(fecha_inicio.year, fecha_inicio.month, fecha_inicio.day)
            self.date_inicio.setDate(fecha_qt)

        fecha_fin = self.obra_datos.get("fecha_fin_estimada")
        if fecha_fin:
            if isinstance(fecha_fin, str):
                fecha_fin = datetime.datetime.strptime(fecha_fin, "%Y-%m-%d").date()
            fecha_qt = QDate(fecha_fin.year, fecha_fin.month, fecha_fin.day)
            self.date_fin.setDate(fecha_qt)

        # Presupuesto
        presupuesto = self.obra_datos.get("presupuesto_total", 0)
        try:
            self.spin_presupuesto.setValue(float(presupuesto))
        except (ValueError, TypeError):
            self.spin_presupuesto.setValue(0)

        # Combos
        tipo_obra = self.obra_datos.get("tipo_obra", "CONSTRUCCION")
        index = self.combo_tipo.findText(tipo_obra)
        if index >= 0:
            self.combo_tipo.setCurrentIndex(index)

        prioridad = self.obra_datos.get("prioridad", "MEDIA")
        index = self.combo_prioridad.findText(prioridad)
        if index >= 0:
            self.combo_prioridad.setCurrentIndex(index)

        self.txt_observaciones.setPlainText(self.obra_datos.get("observaciones", ""))

    def obtener_datos(self) -> Dict[str, Any]:
        """Obtiene los datos del formulario."""
        datos = {}

        if not self.es_edicion:
            datos["codigo"] = self.txt_codigo.text().strip()

        datos["nombre"] = self.txt_nombre.text().strip()
        datos["cliente"] = self.txt_cliente.text().strip()
        datos["descripcion"] = self.txt_descripcion.toPlainText().strip()
        datos["responsable"] = self.txt_responsable.text().strip()
        datos["direccion"] = self.txt_direccion.text().strip()
        datos["telefono_contacto"] = self.txt_telefono.text().strip()
        datos["email_contacto"] = self.txt_email.text().strip()
        # Fechas - convertir de QDate a datetime.date
        fecha_inicio_qt = self.date_inicio.date()
        fecha_fin_qt = self.date_fin.date()

        datos["fecha_inicio"] = datetime.date(
            fecha_inicio_qt.year(), fecha_inicio_qt.month(), fecha_inicio_qt.day()
        )
        datos["fecha_fin_estimada"] = datetime.date(
            fecha_fin_qt.year(), fecha_fin_qt.month(), fecha_fin_qt.day()
        )
        datos["presupuesto_total"] = self.spin_presupuesto.value()
        datos["tipo_obra"] = self.combo_tipo.currentText()
        datos["prioridad"] = self.combo_prioridad.currentText()
        datos["observaciones"] = self.txt_observaciones.toPlainText().strip()

        return datos

    def configurar_validaciones(self):
        """Configura las validaciones del formulario."""
        # Código obligatorio (solo para nuevas obras)
        if not self.es_edicion:
            self.validator_manager.agregar_validacion(
                self.txt_codigo, FormValidator.validar_campo_obligatorio, "Código"
            )

        # Nombre obligatorio
        self.validator_manager.agregar_validacion(
            self.txt_nombre, FormValidator.validar_campo_obligatorio, "Nombre"
        )

        # Cliente obligatorio
        self.validator_manager.agregar_validacion(
            self.txt_cliente, FormValidator.validar_campo_obligatorio, "Cliente"
        )

        # Responsable obligatorio
        self.validator_manager.agregar_validacion(
            self.txt_responsable, FormValidator.validar_campo_obligatorio, "Responsable"
        )

        # Dirección obligatoria
        self.validator_manager.agregar_validacion(
            self.txt_direccion, FormValidator.validar_campo_obligatorio, "Dirección"
        )

        # Email (opcional pero con formato correcto)
        if hasattr(self, 'txt_email') and self.txt_email.text().strip():
            self.validator_manager.agregar_validacion(
                self.txt_email, FormValidator.validar_email
            )

        # Validación de fechas
        self.validator_manager.agregar_validacion(
            self.date_inicio, FormValidator.validar_fecha, QDate.currentDate()
        )

        # Presupuesto mayor que 0
        self.validator_manager.agregar_validacion(
            self.spin_presupuesto, FormValidator.validar_numero, 0.01, 999999999.99
        )

    def validar_y_aceptar(self):
        """Valida el formulario antes de aceptar."""
        es_valido, errores = self.validator_manager.validar_formulario()
        
        if not es_valido:
            # Mostrar errores
            mensajes_error = self.validator_manager.obtener_mensajes_error()
            QMessageBox.warning(
                self, 
                "Errores de Validación", 
                "Por favor corrige los siguientes errores:\n\n" + "\n".join(mensajes_error)
            )
            return

        # Validación adicional: fecha fin debe ser posterior a fecha inicio
        if self.date_fin.date() <= self.date_inicio.date():
            QMessageBox.warning(
                self,
                "Error en Fechas",
                "La fecha de finalización debe ser posterior a la fecha de inicio."
            )
            return

        # Si todo es válido, aceptar el diálogo
        self.accept()
