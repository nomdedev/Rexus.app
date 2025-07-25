"""
Vista de Auditoría

Interfaz de usuario para el sistema de auditoría y monitoreo.
"""

import datetime

from PyQt6.QtCore import QDate, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class AuditoriaView(QWidget):
    """Vista principal del módulo de auditoría."""

    # Señales
    filtrar_solicitud = pyqtSignal(dict)
    exportar_solicitud = pyqtSignal(str)
    limpiar_solicitud = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        self.setWindowTitle("Auditoría del Sistema")

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Título
        title_label = QLabel("📊 Auditoría del Sistema")
        title_label.setObjectName("titleLabel")
        title_label.setStyleSheet("""
            QLabel#titleLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        main_layout.addWidget(title_label)

        # Crear tabs
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                background: white;
            }
            QTabBar::tab {
                background: #ecf0f1;
                border: 1px solid #bdc3c7;
                padding: 8px 16px;
                margin-right: 2px;
                border-radius: 4px 4px 0 0;
            }
            QTabBar::tab:selected {
                background: #3498db;
                color: white;
            }
        """)

        # Tab de registros
        self.tab_registros = self._create_registros_tab()
        tab_widget.addTab(self.tab_registros, "📋 Registros")

        # Tab de estadísticas
        self.tab_estadisticas = self._create_estadisticas_tab()
        tab_widget.addTab(self.tab_estadisticas, "📈 Estadísticas")

        main_layout.addWidget(tab_widget)

    def _create_registros_tab(self):
        """Crea la pestaña de registros de auditoría."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Panel de filtros
        filters_group = QGroupBox("🔍 Filtros de Búsqueda")
        filters_layout = QVBoxLayout(filters_group)

        # Primera fila de filtros
        filter_row1 = QHBoxLayout()

        # Filtro por fechas
        filter_row1.addWidget(QLabel("Desde:"))
        self.fecha_inicio = QDateEdit()
        self.fecha_inicio.setDate(QDate.currentDate().addDays(-30))
        self.fecha_inicio.setCalendarPopup(True)
        filter_row1.addWidget(self.fecha_inicio)

        filter_row1.addWidget(QLabel("Hasta:"))
        self.fecha_fin = QDateEdit()
        self.fecha_fin.setDate(QDate.currentDate())
        self.fecha_fin.setCalendarPopup(True)
        filter_row1.addWidget(self.fecha_fin)

        # Filtro por usuario
        filter_row1.addWidget(QLabel("Usuario:"))
        self.filtro_usuario = QLineEdit()
        self.filtro_usuario.setPlaceholderText("Nombre de usuario...")
        filter_row1.addWidget(self.filtro_usuario)

        filters_layout.addLayout(filter_row1)

        # Segunda fila de filtros
        filter_row2 = QHBoxLayout()

        # Filtro por módulo
        filter_row2.addWidget(QLabel("Módulo:"))
        self.filtro_modulo = QComboBox()
        self.filtro_modulo.addItems(
            [
                "Todos",
                "Inventario",
                "Obras",
                "Logística",
                "Herrajes",
                "Pedidos",
                "Usuarios",
                "Configuración",
                "Auditoría",
                "Contabilidad",
                "Mantenimiento",
                "Vidrios",
            ]
        )
        filter_row2.addWidget(self.filtro_modulo)

        # Filtro por criticidad
        filter_row2.addWidget(QLabel("Criticidad:"))
        self.filtro_criticidad = QComboBox()
        self.filtro_criticidad.addItems(["Todas", "BAJA", "MEDIA", "ALTA", "CRÍTICA"])
        filter_row2.addWidget(self.filtro_criticidad)

        # Botones de acción
        btn_filtrar = QPushButton("🔍 Filtrar")
        btn_filtrar.setObjectName("primaryButton")
        btn_filtrar.clicked.connect(self._emit_filtrar)
        filter_row2.addWidget(btn_filtrar)

        btn_limpiar_filtros = QPushButton("🗑️ Limpiar")
        btn_limpiar_filtros.clicked.connect(self._limpiar_filtros)
        filter_row2.addWidget(btn_limpiar_filtros)

        filter_row2.addStretch()

        filters_layout.addLayout(filter_row2)
        layout.addWidget(filters_group)

        # Tabla de registros
        self.tabla_registros = QTableWidget()
        self.tabla_registros.setColumnCount(8)
        self.tabla_registros.setHorizontalHeaderLabels(
            [
                "Fecha/Hora",
                "Usuario",
                "Módulo",
                "Acción",
                "Descripción",
                "Tabla",
                "Criticidad",
                "Resultado",
            ]
        )

        # Configurar tabla
        header = self.tabla_registros.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)

        self.tabla_registros.setAlternatingRowColors(True)
        self.tabla_registros.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.tabla_registros.setStyleSheet("""
            QTableWidget {
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                background-color: white;
                gridline-color: #ecf0f1;
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

        layout.addWidget(self.tabla_registros)

        # Panel de acciones
        actions_layout = QHBoxLayout()

        btn_exportar = QPushButton("📁 Exportar CSV")
        btn_exportar.clicked.connect(self._emit_exportar)
        actions_layout.addWidget(btn_exportar)

        btn_limpiar_antiguos = QPushButton("🗑️ Limpiar Antiguos")
        btn_limpiar_antiguos.clicked.connect(self._solicitar_limpiar)
        actions_layout.addWidget(btn_limpiar_antiguos)

        actions_layout.addStretch()

        # Contador de registros
        self.label_contador = QLabel("Registros: 0")
        self.label_contador.setStyleSheet("font-weight: bold; color: #7f8c8d;")
        actions_layout.addWidget(self.label_contador)

        layout.addLayout(actions_layout)

        return widget

    def _create_estadisticas_tab(self):
        """Crea la pestaña de estadísticas."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Panel de resumen
        resumen_group = QGroupBox("📊 Resumen General (últimos 30 días)")
        resumen_layout = QHBoxLayout(resumen_group)

        # Tarjetas de estadísticas
        self.card_total = self._create_stat_card("Total Acciones", "0", "#3498db")
        self.card_criticas = self._create_stat_card("Acciones Críticas", "0", "#e74c3c")
        self.card_fallidas = self._create_stat_card("Acciones Fallidas", "0", "#f39c12")

        resumen_layout.addWidget(self.card_total)
        resumen_layout.addWidget(self.card_criticas)
        resumen_layout.addWidget(self.card_fallidas)
        resumen_layout.addStretch()

        layout.addWidget(resumen_group)

        # Splitter para gráficos
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Panel de módulos más activos
        modulos_group = QGroupBox("📈 Módulos Más Activos")
        modulos_layout = QVBoxLayout(modulos_group)

        self.tabla_modulos = QTableWidget()
        self.tabla_modulos.setColumnCount(2)
        self.tabla_modulos.setHorizontalHeaderLabels(["Módulo", "Acciones"])
        self.tabla_modulos.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        modulos_layout.addWidget(self.tabla_modulos)

        splitter.addWidget(modulos_group)

        # Panel de usuarios más activos
        usuarios_group = QGroupBox("👤 Usuarios Más Activos")
        usuarios_layout = QVBoxLayout(usuarios_group)

        self.tabla_usuarios = QTableWidget()
        self.tabla_usuarios.setColumnCount(2)
        self.tabla_usuarios.setHorizontalHeaderLabels(["Usuario", "Acciones"])
        self.tabla_usuarios.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        usuarios_layout.addWidget(self.tabla_usuarios)

        splitter.addWidget(usuarios_group)

        layout.addWidget(splitter)

        return widget

    def _create_stat_card(self, title, value, color):
        """Crea una tarjeta de estadística."""
        card = QFrame()
        card.setFrameStyle(QFrame.Shape.Box)
        card.setStyleSheet(f"""
            QFrame {{
                border: 2px solid {color};
                border-radius: 10px;
                background-color: white;
                margin: 5px;
            }}
            QLabel {{
                border: none;
                background: transparent;
            }}
        """)

        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Título
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(
            f"color: {color}; font-weight: bold; font-size: 12px;"
        )
        layout.addWidget(title_label)

        # Valor
        value_label = QLabel(value)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        value_label.setStyleSheet(
            f"color: {color}; font-weight: bold; font-size: 24px;"
        )
        value_label.setObjectName("valueLabel")
        layout.addWidget(value_label)

        return card

    def _emit_filtrar(self):
        """Emite la señal de filtrado con los parámetros."""
        filtros = {
            "fecha_inicio": self.fecha_inicio.date().toPython(),
            "fecha_fin": self.fecha_fin.date().toPython(),
            "usuario": self.filtro_usuario.text().strip(),
            "modulo": self.filtro_modulo.currentText()
            if self.filtro_modulo.currentText() != "Todos"
            else "",
            "criticidad": self.filtro_criticidad.currentText()
            if self.filtro_criticidad.currentText() != "Todas"
            else "",
        }
        self.filtrar_solicitud.emit(filtros)

    def _limpiar_filtros(self):
        """Limpia todos los filtros."""
        self.fecha_inicio.setDate(QDate.currentDate().addDays(-30))
        self.fecha_fin.setDate(QDate.currentDate())
        self.filtro_usuario.clear()
        self.filtro_modulo.setCurrentIndex(0)
        self.filtro_criticidad.setCurrentIndex(0)

    def _emit_exportar(self):
        """Emite la señal de exportación."""
        self.exportar_solicitud.emit("csv")

    def _solicitar_limpiar(self):
        """Solicita confirmación para limpiar registros antiguos."""
        reply = QMessageBox.question(
            self,
            "Confirmar Limpieza",
            "¿Desea eliminar registros de auditoría anteriores a 365 días?\n\n"
            "Los registros críticos se conservarán.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.limpiar_solicitud.emit(365)

    def actualizar_registros(self, registros):
        """Actualiza la tabla de registros."""
        self.tabla_registros.setRowCount(len(registros))

        for i, registro in enumerate(registros):
            # Formatear fecha
            fecha_str = ""
            if isinstance(registro.get("fecha_hora"), datetime.datetime):
                fecha_str = registro["fecha_hora"].strftime("%d/%m/%Y %H:%M")
            elif registro.get("fecha_hora"):
                fecha_str = str(registro["fecha_hora"])

            items = [
                fecha_str,
                registro.get("usuario", ""),
                registro.get("modulo", ""),
                registro.get("accion", ""),
                registro.get("descripcion", ""),
                registro.get("tabla_afectada", ""),
                registro.get("nivel_criticidad", ""),
                registro.get("resultado", ""),
            ]

            for j, item_text in enumerate(items):
                item = QTableWidgetItem(str(item_text))

                # Colorear según criticidad y resultado
                if j == 6:  # Columna criticidad
                    if item_text == "CRÍTICA":
                        item.setBackground(QColor("#e74c3c"))
                        item.setForeground(QColor("white"))
                    elif item_text == "ALTA":
                        item.setBackground(QColor("#f39c12"))
                        item.setForeground(QColor("white"))

                if j == 7:  # Columna resultado
                    if item_text == "FALLIDO":
                        item.setBackground(QColor("#e74c3c"))
                        item.setForeground(QColor("white"))
                    elif item_text == "EXITOSO":
                        item.setBackground(QColor("#27ae60"))
                        item.setForeground(QColor("white"))

                self.tabla_registros.setItem(i, j, item)

        # Actualizar contador
        self.label_contador.setText(f"Registros: {len(registros)}")

    def actualizar_estadisticas(self, estadisticas):
        """Actualiza las estadísticas mostradas."""
        # Actualizar tarjetas de resumen
        total = estadisticas.get("total_acciones", 0)
        criticas = estadisticas.get("acciones_criticas", 0)
        fallidas = estadisticas.get("acciones_fallidas", 0)

        self.card_total.findChild(QLabel, "valueLabel").setText(str(total))
        self.card_criticas.findChild(QLabel, "valueLabel").setText(str(criticas))
        self.card_fallidas.findChild(QLabel, "valueLabel").setText(str(fallidas))

        # Actualizar tabla de módulos
        modulos = estadisticas.get("acciones_por_modulo", [])
        self.tabla_modulos.setRowCount(len(modulos))

        for i, modulo in enumerate(modulos):
            self.tabla_modulos.setItem(i, 0, QTableWidgetItem(modulo["nombre"]))
            self.tabla_modulos.setItem(i, 1, QTableWidgetItem(str(modulo["cantidad"])))

        # Actualizar tabla de usuarios
        usuarios = estadisticas.get("acciones_por_usuario", [])
        self.tabla_usuarios.setRowCount(len(usuarios))

        for i, usuario in enumerate(usuarios):
            self.tabla_usuarios.setItem(i, 0, QTableWidgetItem(usuario["nombre"]))
            self.tabla_usuarios.setItem(
                i, 1, QTableWidgetItem(str(usuario["cantidad"]))
            )

    def mostrar_mensaje(self, mensaje, tipo="info"):
        """Muestra un mensaje al usuario."""
        if tipo == "error":
            QMessageBox.critical(self, "Error", mensaje)
        elif tipo == "warning":
            QMessageBox.warning(self, "Advertencia", mensaje)
        elif tipo == "success":
            QMessageBox.information(self, "Éxito", mensaje)
        else:
            QMessageBox.information(self, "Información", mensaje)
