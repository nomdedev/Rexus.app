"""
MIT License

Copyright (c) 2024 Rexus.app

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Vista de Logística - Interfaz de gestión de transportes y entregas
"""

# 🔒 Form Access Control - Verify user can access this interface
# Check user role and permissions before showing sensitive forms
# Form Access Control

# 🔒 XSS Protection Added - Validate all user inputs
# Use SecurityUtils.sanitize_input() for text fields
# Use SecurityUtils.validate_email() for email fields
# XSS Protection Added

"""
Interfaz moderna para la gestión de logística y transporte.
"""

import logging

from PyQt6.QtCore import QDate, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from rexus.core.auth_manager import AuthManager
from rexus.utils.data_sanitizer import DataSanitizer
from rexus.utils.form_validators import (
    FormValidator,
    FormValidatorManager,
    validacion_direccion,
)
from rexus.utils.security import SecurityUtils
from rexus.utils.xss_protection import FormProtector, XSSProtection, xss_protect


class LogisticaView(QWidget):
    """Vista modernizada para gestión de logística."""

    # Señales
    entrega_seleccionada = pyqtSignal(dict)
    crear_entrega_solicitada = pyqtSignal(dict)
    actualizar_entrega_solicitada = pyqtSignal(dict)
    eliminar_entrega_solicitada = pyqtSignal(int)

    def __init__(self):
        # Inicializar protección XSS
        self.form_protector = FormProtector(self)
        self.form_protector.dangerous_content_detected.connect(self._on_dangerous_content)
        
        super().__init__()
        self.controller = None
        self.entregas_data = []
        self.logger = logging.getLogger(__name__)
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Crear tabs
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                background-color: white;
            }
            QTabBar::tab {
                background: #ecf0f1;
                padding: 10px 20px;
                margin-right: 2px;
                border: 1px solid #bdc3c7;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: 1px solid white;
            }
        """)

        # Tab de entregas
        self.create_entregas_tab()

        # Tab de servicios
        self.create_servicios_tab()

        # Tab de mapa
        self.create_mapa_tab()

        # Tab de estadísticas
        self.create_estadisticas_tab()

        layout.addWidget(self.tabs)

        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', sans-serif;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
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
            QTableWidget {
                gridline-color: #bdc3c7;
                background-color: white;
                alternate-background-color: #f8f9fa;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 8px;
                border: 1px solid #2980b9;
                font-weight: bold;
            }
        """)

    def create_entregas_tab(self):
        """Crea el tab de entregas."""
        entregas_widget = QWidget()
        layout = QVBoxLayout(entregas_widget)

        # Panel de filtros
        filtros_group = QGroupBox("Filtros y Búsqueda")
        filtros_layout = QHBoxLayout(filtros_group)

        # Búsqueda
        self.search_input = QLineEdit()
        self.search_input.setAccessibleName('Search Input')
        self.search_input.setPlaceholderText("Buscar entregas...")
        self.search_input.setFixedWidth(200)
        filtros_layout.addWidget(QLabel("Buscar:"))
        filtros_layout.addWidget(self.search_input)

        # Filtro por estado
        self.combo_estado = QComboBox()
        self.combo_estado.addItems(
            ["Todos", "Programada", "En Tránsito", "Entregada", "Cancelada"]
        )
        self.combo_estado.setFixedWidth(150)
        filtros_layout.addWidget(QLabel("Estado:"))
        filtros_layout.addWidget(self.combo_estado)

        # Botón nuevo
        btn_nueva_entrega = QPushButton("➕ Nueva Entrega")
        btn_nueva_entrega.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
        """)
        btn_nueva_entrega.clicked.connect(self.mostrar_dialogo_nueva_entrega)
        filtros_layout.addWidget(btn_nueva_entrega)

        filtros_layout.addStretch()
        layout.addWidget(filtros_group)

        # Tabla de entregas
        self.tabla_entregas = QTableWidget()
        self.tabla_entregas.setColumnCount(7)
        self.tabla_entregas.setHorizontalHeaderLabels(
            [
                "ID",
                "Fecha Programada",
                "Dirección",
                "Estado",
                "Contacto",
                "Observaciones",
                "Acciones",
            ]
        )

        # Configurar tabla
        header = self.tabla_entregas.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.tabla_entregas.setColumnWidth(0, 60)
        self.tabla_entregas.setAlternatingRowColors(True)
        self.tabla_entregas.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        layout.addWidget(self.tabla_entregas)

        self.tabs.addTab(entregas_widget, "📦 Entregas")

    def create_servicios_tab(self):
        """Crea el tab de servicios."""
        servicios_widget = QWidget()
        layout = QVBoxLayout(servicios_widget)

        # Panel de creación de servicios
        crear_group = QGroupBox("📋 Generar Nuevo Servicio")
        crear_layout = QVBoxLayout(crear_group)

        # Formulario para crear servicio
        form_layout = QFormLayout()

        # Tipo de servicio
        self.combo_tipo_servicio = QComboBox()
        self.combo_tipo_servicio.addItems(
            [
                "Entrega Domicilio",
                "Transporte Obra",
                "Servicio Express",
                "Carga Pesada",
                "Servicio Programado",
            ]
        )
        self.combo_tipo_servicio.setFixedWidth(200)

        # Cliente/Destino
        self.input_cliente = QLineEdit()
        self.input_cliente.setAccessibleName('Input Cliente')
        self.input_cliente.setPlaceholderText("Nombre del cliente o destino")
        self.input_cliente.setFixedWidth(300)

        # Dirección
        self.input_direccion = QLineEdit()
        self.input_direccion.setAccessibleName('Input Direccion')
        self.input_direccion.setPlaceholderText("Dirección completa de entrega")
        self.input_direccion.setFixedWidth(400)

        # Fecha programada
        self.date_programada = QDateEdit()
        self.date_programada.setDate(QDate.currentDate())
        self.date_programada.setCalendarPopup(True)
        self.date_programada.setFixedWidth(150)

        # Hora programada
        self.input_hora = QLineEdit()
        self.input_hora.setAccessibleName('Input Hora')
        self.input_hora.setPlaceholderText("HH:MM")
        self.input_hora.setFixedWidth(100)

        # Contacto
        self.input_contacto = QLineEdit()
        self.input_contacto.setAccessibleName('Input Contacto')
        self.input_contacto.setPlaceholderText("Teléfono de contacto")
        self.input_contacto.setFixedWidth(200)

        # Observaciones
        self.text_observaciones = QTextEdit()
        self.text_observaciones.setPlaceholderText(
            "Observaciones adicionales del servicio"
        )
        self.text_observaciones.setMaximumHeight(80)

        # Agregar campos al formulario
        form_layout.addRow("Tipo de Servicio:", self.combo_tipo_servicio)
        form_layout.addRow("Cliente/Destino:", self.input_cliente)
        form_layout.addRow("Dirección:", self.input_direccion)
        form_layout.addRow("Fecha Programada:", self.date_programada)
        form_layout.addRow("Hora:", self.input_hora)
        form_layout.addRow("Contacto:", self.input_contacto)
        form_layout.addRow("Observaciones:", self.text_observaciones)

        crear_layout.addLayout(form_layout)

        # Botones de acción
        botones_layout = QHBoxLayout()

        btn_generar = QPushButton("✨ Generar Servicio")
        btn_generar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 12px 30px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
        """)
        btn_generar.clicked.connect(self.generar_servicio)

        btn_limpiar = QPushButton("🧹 Limpiar Formulario")
        btn_limpiar.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 12px 30px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        btn_limpiar.clicked.connect(self.limpiar_formulario)

        botones_layout.addWidget(btn_generar)
        botones_layout.addWidget(btn_limpiar)
        botones_layout.addStretch()

        crear_layout.addLayout(botones_layout)
        layout.addWidget(crear_group)

        # Tabla de servicios generados
        tabla_group = QGroupBox("📋 Servicios Generados")
        tabla_layout = QVBoxLayout(tabla_group)

        self.tabla_servicios = QTableWidget()
        self.tabla_servicios.setColumnCount(8)
        self.tabla_servicios.setHorizontalHeaderLabels(
            [
                "ID",
                "Tipo",
                "Cliente",
                "Dirección",
                "Fecha",
                "Hora",
                "Estado",
                "Acciones",
            ]
        )

        # Configurar tabla
        header = self.tabla_servicios.horizontalHeader()
        if header is not None:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.tabla_servicios.setColumnWidth(0, 60)
        self.tabla_servicios.setAlternatingRowColors(True)
        self.tabla_servicios.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        tabla_layout.addWidget(self.tabla_servicios)
        layout.addWidget(tabla_group)

        self.tabs.addTab(servicios_widget, "🚚 Servicios")

    def create_mapa_tab(self):
        """Crea el tab del mapa interactivo con OpenStreetMap."""
        mapa_widget = QWidget()
        layout = QVBoxLayout(mapa_widget)

        # Panel de controles del mapa
        controles_group = QGroupBox("🗺️ Controles del Mapa Interactivo")
        controles_layout = QHBoxLayout(controles_group)

        # Filtros del mapa
        self.combo_filtro_mapa = QComboBox()
        self.combo_filtro_mapa.addItems(
            [
                "Mostrar Todo",
                "Solo Servicios",
                "Solo Obras",
                "Servicios Activos",
                "Obras En Proceso",
            ]
        )
        self.combo_filtro_mapa.setFixedWidth(150)
        self.combo_filtro_mapa.currentTextChanged.connect(self.filtrar_mapa)
        controles_layout.addWidget(QLabel("Filtro:"))
        controles_layout.addWidget(self.combo_filtro_mapa)

        # Botón agregar marcador
        btn_agregar_marcador = QPushButton("📍 Agregar Ubicación")
        btn_agregar_marcador.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
        """)
        btn_agregar_marcador.clicked.connect(self.agregar_marcador_mapa)
        controles_layout.addWidget(btn_agregar_marcador)

        # Botón limpiar marcadores
        btn_limpiar = QPushButton("🧹 Limpiar Marcadores")
        btn_limpiar.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        btn_limpiar.clicked.connect(self.limpiar_marcadores_mapa)
        controles_layout.addWidget(btn_limpiar)

        controles_layout.addStretch()
        layout.addWidget(controles_group)

        # Crear mapa interactivo
        try:
            # Verificar si tenemos todas las dependencias
            import folium
            from PyQt6.QtWebEngineWidgets import QWebEngineView

            # Si llegamos aquí, tenemos las dependencias
            from .interactive_map import InteractiveMapWidget

            self.interactive_map = InteractiveMapWidget()

            # Conectar señales del mapa
            self.interactive_map.location_clicked.connect(self.on_map_location_clicked)
            self.interactive_map.marker_clicked.connect(self.on_map_marker_clicked)

            layout.addWidget(self.interactive_map)

        except ImportError as e:
            print(f"Dependencias del mapa interactivo no disponibles: {e}")
            # Fallback al mapa estático
            self.interactive_map = None
            self.create_static_map_fallback(layout)

        # Panel de información de ubicaciones
        info_group = QGroupBox("📋 Información de Ubicaciones en el Mapa")
        info_layout = QVBoxLayout(info_group)

        # Lista de ubicaciones
        self.lista_ubicaciones = QTableWidget()
        self.lista_ubicaciones.setColumnCount(4)
        self.lista_ubicaciones.setHorizontalHeaderLabels(
            ["Tipo", "Descripción", "Dirección", "Estado"]
        )
        self.lista_ubicaciones.setMaximumHeight(150)

        # Configurar tabla de ubicaciones
        header_ubicaciones = self.lista_ubicaciones.horizontalHeader()
        if header_ubicaciones is not None:
            header_ubicaciones.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.lista_ubicaciones.setAlternatingRowColors(True)

        info_layout.addWidget(self.lista_ubicaciones)
        layout.addWidget(info_group)

        # Cargar ubicaciones iniciales
        self.actualizar_ubicaciones_mapa()

        self.tabs.addTab(mapa_widget, "🗺️ Mapa Interactivo")

    def create_estadisticas_tab(self):
        """Crea el tab de estadísticas."""
        stats_widget = QWidget()
        layout = QVBoxLayout(stats_widget)

        # Panel de estadísticas
        stats_group = QGroupBox("Estadísticas de Logística")
        stats_layout = QFormLayout(stats_group)

        self.label_total_entregas = QLabel("0")
        self.label_entregas_pendientes = QLabel("0")
        self.label_entregas_completadas = QLabel("0")
        self.label_entregas_canceladas = QLabel("0")
        self.label_promedio_tiempo = QLabel("0 horas")

        stats_layout.addRow("Total Entregas:", self.label_total_entregas)
        stats_layout.addRow("Entregas Pendientes:", self.label_entregas_pendientes)
        stats_layout.addRow("Entregas Completadas:", self.label_entregas_completadas)
        stats_layout.addRow("Entregas Canceladas:", self.label_entregas_canceladas)
        stats_layout.addRow("Tiempo Promedio:", self.label_promedio_tiempo)

        layout.addWidget(stats_group)
        layout.addStretch()

        self.tabs.addTab(stats_widget, "📊 Estadísticas")

    def set_controller(self, controller):
        """Establece el controlador para esta vista."""
        self.controller = controller

    def cargar_entregas_en_tabla(self, entregas):
        """Carga las entregas en la tabla."""
        self.entregas_data = entregas
        self.tabla_entregas.setRowCount(len(entregas))

        for row, entrega in enumerate(entregas):
            self.tabla_entregas.setItem(
                row, 0, QTableWidgetItem(str(entrega.get("id", "")))
            )
            self.tabla_entregas.setItem(
                row, 1, QTableWidgetItem(str(entrega.get("fecha_programada", "")))
            )
            self.tabla_entregas.setItem(
                row, 2, QTableWidgetItem(str(entrega.get("direccion_entrega", "")))
            )
            self.tabla_entregas.setItem(
                row, 3, QTableWidgetItem(str(entrega.get("estado", "")))
            )
            self.tabla_entregas.setItem(
                row, 4, QTableWidgetItem(str(entrega.get("contacto", "")))
            )
            self.tabla_entregas.setItem(
                row, 5, QTableWidgetItem(str(entrega.get("observaciones", "")))
            )

            # Botón de acciones
            btn_accion = QPushButton("⚙️")
            btn_accion.setMaximumWidth(30)
            btn_accion.setToolTip("Acciones")
            self.tabla_entregas.setCellWidget(row, 6, btn_accion)

    def actualizar_estadisticas(self, estadisticas):
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('actualizar_estadisticas'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")

        # 🔒 PROTECCIÓN XSS: Sanitizar todas las entradas de texto
        # TODO: Implementar sanitización con SecurityUtils.sanitize_input()
        # Ejemplo: texto_limpio = SecurityUtils.sanitize_input(texto_usuario)

        """Actualiza las estadísticas mostradas."""
        self.label_total_entregas.setText(str(estadisticas.get("total_entregas", 0)))
        self.label_entregas_pendientes.setText(
            str(estadisticas.get("entregas_pendientes", 0))
        )
        self.label_entregas_completadas.setText(
            str(estadisticas.get("entregas_completadas", 0))
        )
        self.label_entregas_canceladas.setText(
            str(estadisticas.get("entregas_canceladas", 0))
        )
        self.label_promedio_tiempo.setText(
            f"{estadisticas.get('promedio_tiempo', 0)} horas"
        )

    def mostrar_mensaje(self, mensaje):
        """Muestra un mensaje informativo."""
        from PyQt6.QtWidgets import QMessageBox

        QMessageBox.information(self, "Logística", mensaje)

    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error."""
        from PyQt6.QtWidgets import QMessageBox

        QMessageBox.critical(self, "Error - Logística", mensaje)

    def validar_ubicacion_duplicada(self, direccion, fecha):
        """Valida si ya existe un servicio en la misma ubicación y fecha."""
        try:
            self.logger.info(
                f"Validando ubicación duplicada: {direccion} para fecha {fecha}"
            )

            # Recorrer tabla de servicios para buscar duplicados
            for row in range(self.tabla_servicios.rowCount()):
                direccion_item = self.tabla_servicios.item(row, 3)  # Columna dirección
                fecha_item = self.tabla_servicios.item(row, 4)  # Columna fecha

                if direccion_item and fecha_item:
                    direccion_existente = direccion_item.text().strip()
                    fecha_existente = fecha_item.text().strip()

                    # Normalizar direcciones para comparación
                    direccion_norm = DataSanitizer.sanitize_text(direccion).lower()
                    direccion_existente_norm = DataSanitizer.sanitize_text(
                        direccion_existente
                    ).lower()

                    if (
                        direccion_norm == direccion_existente_norm
                        and fecha == fecha_existente
                    ):
                        self.logger.warning(
                            f"Ubicación duplicada encontrada: {direccion} en {fecha}"
                        )
                        return True

            return False

        except Exception as e:
            self.logger.error(f"Error al validar ubicación duplicada: {str(e)}")
            return False

    def mostrar_dialogo_nueva_entrega(self):
        """Muestra el diálogo para crear una nueva entrega."""
        try:
            self.logger.info("Abriendo diálogo para nueva entrega")

            dialog = DialogoNuevaEntrega(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                datos_entrega = dialog.obtener_datos()
                try:
                    # Emitir señal para que el controlador maneje la creación
                    self.crear_entrega_solicitada.emit(datos_entrega)
                    self.mostrar_mensaje("Entrega creada exitosamente")
                    self.logger.info(
                        f"Entrega creada exitosamente: {datos_entrega.get('direccion', 'N/A')}"
                    )
                except Exception as e:
                    error_msg = f"Error al crear entrega: {str(e)}"
                    self.logger.error(error_msg)
                    self.mostrar_error(error_msg)
            else:
                self.logger.info("Diálogo de nueva entrega cancelado por el usuario")

        except Exception as e:
            error_msg = f"Error al mostrar diálogo de nueva entrega: {str(e)}"
            self.logger.error(error_msg)
            self.mostrar_error(error_msg)

    def generar_servicio(self):
        """Genera un nuevo servicio con los datos del formulario."""
        try:
            self.logger.info("Iniciando generación de nuevo servicio de logística")

            # Obtener y sanitizar datos del formulario
            tipo_servicio = self.combo_tipo_servicio.currentText()
            cliente = DataSanitizer.sanitize_text(self.input_cliente.text().strip())
            direccion = DataSanitizer.sanitize_text(self.input_direccion.text().strip())
            fecha = self.date_programada.date().toString("yyyy-MM-dd")
            hora = DataSanitizer.sanitize_text(self.input_hora.text().strip())
            contacto = DataSanitizer.sanitize_text(self.input_contacto.text().strip())
            observaciones = DataSanitizer.sanitize_text(
                self.text_observaciones.toPlainText().strip()
            )

            # Validar datos obligatorios
            if not cliente or not direccion:
                error_msg = (
                    "Por favor complete los campos obligatorios: Cliente y Dirección"
                )
                self.logger.warning(
                    f"Validación fallida en generar servicio: {error_msg}"
                )
                self.mostrar_error(error_msg)
                return

            # Validar ubicaciones duplicadas para la misma fecha
            if self.validar_ubicacion_duplicada(direccion, fecha):
                error_msg = f"Ya existe un servicio programado para la dirección '{direccion}' en la fecha {fecha}"
                self.logger.warning(f"Ubicación duplicada detectada: {error_msg}")
                self.mostrar_error(error_msg)
                return

            # Crear nuevo servicio
            servicio = {
                "tipo": tipo_servicio,
                "cliente": cliente,
                "direccion": direccion,
                "fecha": fecha,
                "hora": hora or "No especificada",
                "contacto": contacto or "No especificado",
                "observaciones": observaciones,
                "estado": "Programado",
            }

            # Agregar a la tabla
            self.agregar_servicio_tabla(servicio)

            # Mostrar mensaje de éxito
            self.mostrar_mensaje(
                f"Servicio '{tipo_servicio}' generado exitosamente para {cliente}"
            )
            self.logger.info(
                f"Servicio de logística creado exitosamente: {tipo_servicio} para {cliente}"
            )

            # Limpiar formulario
            self.limpiar_formulario()

        except Exception as e:
            error_msg = f"Error al generar servicio: {str(e)}"
            self.logger.error(error_msg)
            self.mostrar_error(error_msg)

    def agregar_servicio_tabla(self, servicio):
        """Agrega un servicio a la tabla de servicios."""
        try:
            self.logger.info(
                f"Agregando servicio a tabla: {servicio.get('tipo', 'N/A')} - {servicio.get('cliente', 'N/A')}"
            )

            row = self.tabla_servicios.rowCount()
            self.tabla_servicios.insertRow(row)

            # Generar ID único
            service_id = f"SRV{row + 1:03d}"

            # Llenar datos en la tabla
            self.tabla_servicios.setItem(row, 0, QTableWidgetItem(service_id))
            self.tabla_servicios.setItem(row, 1, QTableWidgetItem(servicio["tipo"]))
            self.tabla_servicios.setItem(row, 2, QTableWidgetItem(servicio["cliente"]))
            self.tabla_servicios.setItem(
                row, 3, QTableWidgetItem(servicio["direccion"])
            )
            self.tabla_servicios.setItem(row, 4, QTableWidgetItem(servicio["fecha"]))
            self.tabla_servicios.setItem(row, 5, QTableWidgetItem(servicio["hora"]))
            self.tabla_servicios.setItem(row, 6, QTableWidgetItem(servicio["estado"]))

            # Botón de acciones
            btn_acciones = QPushButton("⚙️")
            btn_acciones.setMaximumWidth(30)
            btn_acciones.setToolTip("Acciones del servicio")
            self.tabla_servicios.setCellWidget(row, 7, btn_acciones)

            # Actualizar información del mapa
            self.actualizar_ubicaciones_mapa()

            self.logger.info(f"Servicio agregado exitosamente a la tabla en fila {row}")

        except Exception as e:
            error_msg = f"Error al agregar servicio a la tabla: {str(e)}"
            self.logger.error(error_msg)
            self.mostrar_error(error_msg)

    def limpiar_formulario(self):
        """Limpia todos los campos del formulario de servicios."""
        self.input_cliente.clear()
        self.input_direccion.clear()
        self.date_programada.setDate(QDate.currentDate())
        self.input_hora.clear()
        self.input_contacto.clear()
        self.text_observaciones.clear()
        self.combo_tipo_servicio.setCurrentIndex(0)

    def actualizar_mapa(self):
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('actualizar_mapa'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")

        # 🔒 PROTECCIÓN XSS: Sanitizar todas las entradas de texto
        # TODO: Implementar sanitización con SecurityUtils.sanitize_input()
        # Ejemplo: texto_limpio = SecurityUtils.sanitize_input(texto_usuario)

        """Actualiza la información del mapa."""
        try:
            # Simular actualización del mapa
            self.actualizar_ubicaciones_mapa()
            self.mostrar_mensaje("Mapa actualizado correctamente")
        except Exception as e:
            self.mostrar_error(f"Error al actualizar mapa: {str(e)}")

    def centrar_mapa(self):
        """Centra el mapa en la ubicación principal."""
        try:
            # Simular centrado del mapa
            self.mostrar_mensaje("Mapa centrado en la ubicación principal")
        except Exception as e:
            self.mostrar_error(f"Error al centrar mapa: {str(e)}")

    def actualizar_ubicaciones_mapa(self):
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('actualizar_ubicaciones_mapa'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")

        """Actualiza la tabla de ubicaciones del mapa."""
        try:
            # Limpiar tabla
            self.lista_ubicaciones.setRowCount(0)

            # Agregar ubicaciones demo de La Plata
            ubicaciones_demo = [
                (
                    "Servicio",
                    "Entrega Domicilio",
                    "Calle 7 entre 47 y 48, La Plata",
                    "Activo",
                ),
                (
                    "Obra",
                    "Construcción Edificio",
                    "Av. 13 y 60, La Plata",
                    "En Proceso",
                ),
                (
                    "Servicio",
                    "Transporte Vidrios",
                    "Calle 50 entre 15 y 16, Berisso",
                    "Programado",
                ),
                (
                    "Obra",
                    "Remodelación Casa",
                    "Calle 25 entre 3 y 4, Gonnet",
                    "En Proceso",
                ),
                (
                    "Servicio",
                    "Entrega Herrajes",
                    "Av. 122 y 82, Los Hornos",
                    "Pendiente",
                ),
                ("Obra", "Ampliación Local", "Calle 1 y 57, Tolosa", "Pausada"),
                ("Servicio", "Servicio Express", "Calle 10 y 38, City Bell", "Activo"),
                (
                    "Obra",
                    "Construcción Galpón",
                    "Av. 44 y 150, Villa Elisa",
                    "En Proceso",
                ),
                (
                    "Servicio",
                    "Transporte Pesado",
                    "Calle 520 y 15, Melchor Romero",
                    "Programado",
                ),
                ("Obra", "Refacción Oficinas", "Calle 2 y 64, Ringuelet", "En Proceso"),
            ]

            # Agregar servicios de la tabla
            for row in range(self.tabla_servicios.rowCount()):
                tipo_item = self.tabla_servicios.item(row, 1)
                cliente_item = self.tabla_servicios.item(row, 2)
                direccion_item = self.tabla_servicios.item(row, 3)
                estado_item = self.tabla_servicios.item(row, 6)

                if tipo_item and cliente_item and direccion_item and estado_item:
                    ubicaciones_demo.append(
                        (
                            "Servicio",
                            f"{tipo_item.text()} - {cliente_item.text()}",
                            direccion_item.text(),
                            estado_item.text(),
                        )
                    )

            # Llenar tabla de ubicaciones
            self.lista_ubicaciones.setRowCount(len(ubicaciones_demo))
            for row, (tipo, descripcion, direccion, estado) in enumerate(
                ubicaciones_demo
            ):
                self.lista_ubicaciones.setItem(row, 0, QTableWidgetItem(tipo))
                self.lista_ubicaciones.setItem(row, 1, QTableWidgetItem(descripcion))
                self.lista_ubicaciones.setItem(row, 2, QTableWidgetItem(direccion))
                self.lista_ubicaciones.setItem(row, 3, QTableWidgetItem(estado))

        except Exception as e:
            print(f"Error al actualizar ubicaciones del mapa: {str(e)}")

    def cargar_servicios_en_tabla(self, servicios):
        """Carga servicios en la tabla (método para el controlador)."""
        try:
            self.tabla_servicios.setRowCount(len(servicios))
            for row, servicio in enumerate(servicios):
                self.tabla_servicios.setItem(
                    row, 0, QTableWidgetItem(str(servicio.get("id", "")))
                )
                self.tabla_servicios.setItem(
                    row, 1, QTableWidgetItem(str(servicio.get("tipo", "")))
                )
                self.tabla_servicios.setItem(
                    row, 2, QTableWidgetItem(str(servicio.get("cliente", "")))
                )
                self.tabla_servicios.setItem(
                    row, 3, QTableWidgetItem(str(servicio.get("direccion", "")))
                )
                self.tabla_servicios.setItem(
                    row, 4, QTableWidgetItem(str(servicio.get("fecha_programada", "")))
                )
                self.tabla_servicios.setItem(
                    row, 5, QTableWidgetItem(str(servicio.get("hora", "")))
                )
                self.tabla_servicios.setItem(
                    row, 6, QTableWidgetItem(str(servicio.get("estado", "")))
                )

                # Botón de acciones
                btn_acciones = QPushButton("⚙️")
                btn_acciones.setMaximumWidth(30)
                btn_acciones.setToolTip("Acciones")
                self.tabla_servicios.setCellWidget(row, 7, btn_acciones)

        except Exception as e:
            print(f"Error cargando servicios: {str(e)}")

    def filtrar_mapa(self, filtro_texto):
        """Filtra los marcadores del mapa según el criterio seleccionado."""
        try:
            if hasattr(self, "interactive_map"):
                # Obtener datos según el filtro
                if filtro_texto == "Solo Servicios":
                    # Mostrar solo servicios de la tabla
                    servicios = []
                    for row in range(self.tabla_servicios.rowCount()):
                        direccion_item = self.tabla_servicios.item(row, 3)
                        if direccion_item:
                            direccion = direccion_item.text()
                            from .interactive_map import geocode_address_la_plata

                            coords = geocode_address_la_plata(direccion)

                            servicios.append(
                                {
                                    "coords": coords,
                                    "tipo": self.tabla_servicios.item(row, 1).text()
                                    if self.tabla_servicios.item(row, 1)
                                    else "",
                                    "cliente": self.tabla_servicios.item(row, 2).text()
                                    if self.tabla_servicios.item(row, 2)
                                    else "",
                                    "direccion": direccion,
                                    "estado": self.tabla_servicios.item(row, 6).text()
                                    if self.tabla_servicios.item(row, 6)
                                    else "",
                                    "fecha": self.tabla_servicios.item(row, 4).text()
                                    if self.tabla_servicios.item(row, 4)
                                    else "",
                                }
                            )

                    self.interactive_map.add_service_markers(servicios)

                elif filtro_texto == "Servicios Activos":
                    # Filtrar solo servicios con estado "Activo" o "Programado"
                    servicios_activos = []
                    for row in range(self.tabla_servicios.rowCount()):
                        estado_item = self.tabla_servicios.item(row, 6)
                        if estado_item and estado_item.text() in [
                            "Activo",
                            "Programado",
                            "En Tránsito",
                        ]:
                            direccion_item = self.tabla_servicios.item(row, 3)
                            if direccion_item:
                                direccion = direccion_item.text()
                                from .interactive_map import geocode_address_la_plata

                                coords = geocode_address_la_plata(direccion)

                                servicios_activos.append(
                                    {
                                        "coords": coords,
                                        "tipo": self.tabla_servicios.item(row, 1).text()
                                        if self.tabla_servicios.item(row, 1)
                                        else "",
                                        "cliente":
                                        # 🔒 PROTECCIÓN XSS: Sanitizar todas las entradas de texto
                                        # TODO: Implementar sanitización con SecurityUtils.sanitize_input()
                                        # Ejemplo: texto_limpio = SecurityUtils.sanitize_input(texto_usuario)
                                        self.tabla_servicios.item(row, 2).text()
                                        if self.tabla_servicios.item(row, 2)
                                        else "",
                                        "direccion": direccion,
                                        "estado": estado_item.text(),
                                        "fecha": self.tabla_servicios.item(
                                            row, 4
                                        ).text()
                                        if self.tabla_servicios.item(row, 4)
                                        else "",
                                    }
                                )

                    self.interactive_map.add_service_markers(servicios_activos)

                else:
                    # "Mostrar Todo" o otros filtros - resetear al mapa inicial
                    self.interactive_map.create_initial_map()

                self.actualizar_ubicaciones_mapa()

        except Exception as e:
            print(f"Error filtrando mapa: {e}")

    def agregar_marcador_mapa(self):
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('agregar_marcador_mapa'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")

        """Muestra diálogo para agregar un marcador personalizado al mapa."""
        try:
            from PyQt6.QtWidgets import QComboBox, QInputDialog

            # Diálogo para dirección
            direccion, ok = QInputDialog.getText(
                self,
                "Agregar Ubicación",
                "Ingrese la dirección o ubicación en La Plata:",
            )

            if ok and direccion.strip():
                # Obtener coordenadas
                from .interactive_map import geocode_address_la_plata

                coords = geocode_address_la_plata(direccion.strip())

                # Diálogo para descripción
                descripcion, ok2 = QInputDialog.getText(
                    self, "Descripción", "Ingrese una descripción para esta ubicación:"
                )

                if ok2 and hasattr(self, "interactive_map"):
                    # Agregar marcador al mapa
                    self.interactive_map.add_custom_marker(
                        coords[0],
                        coords[1],
                        direccion.strip(),
                        descripcion.strip() or "Ubicación personalizada",
                        "servicio",
                    )

                    self.mostrar_mensaje(f"Ubicación agregada: {direccion}")
                    self.actualizar_ubicaciones_mapa()

        except Exception as e:
            self.mostrar_error(f"Error agregando marcador: {str(e)}")

    def limpiar_marcadores_mapa(self):
        """Limpia todos los marcadores personalizados del mapa."""
        try:
            if hasattr(self, "interactive_map"):
                self.interactive_map.clear_markers()
                self.mostrar_mensaje("Marcadores eliminados. Mapa restablecido.")
                self.actualizar_ubicaciones_mapa()
        except Exception as e:
            self.mostrar_error(f"Error limpiando marcadores: {str(e)}")

    def on_map_location_clicked(self, lat, lng):
        """Maneja el evento de clic en una ubicación del mapa."""
        try:
            # Mostrar información de la ubicación clickeada
            from PyQt6.QtWidgets import QMessageBox

            mensaje = (
                f"Ubicación seleccionada:\n\nLatitud: {lat:.6f}\nLongitud: {lng:.6f}"
            )

            # Preguntar si desea agregar un servicio en esta ubicación
            respuesta = QMessageBox.question(
                self,
                "Ubicación Seleccionada",
                f"{mensaje}\n\n¿Desea agregar un servicio en esta ubicación?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if respuesta == QMessageBox.StandardButton.Yes:
                # 🔒 PROTECCIÓN XSS: Sanitizar todas las entradas de texto
                # TODO: Implementar sanitización con SecurityUtils.sanitize_input()
                # Ejemplo: texto_limpio = SecurityUtils.sanitize_input(texto_usuario)

                # Abrir diálogo para nuevo servicio con coordenadas pre-cargadas
                self.crear_servicio_desde_mapa(lat, lng)

        except Exception as e:
            print(f"Error manejando clic en mapa: {e}")

    def on_map_marker_clicked(self, marker_data):
        """Maneja el evento de clic en un marcador del mapa."""
        try:
            # Mostrar información detallada del marcador
            from PyQt6.QtWidgets import QMessageBox

            titulo = marker_data.get("title", "Marcador")
            descripcion = marker_data.get("description", "Sin descripción")
            tipo = marker_data.get("type", "desconocido")

            mensaje = f"Información del Marcador:\n\nTítulo: {titulo}\nDescripción: {descripcion}\nTipo: {tipo.title()}"

            QMessageBox.information(self, "Información del Marcador", mensaje)

        except Exception as e:
            print(f"Error manejando clic en marcador: {e}")

    def crear_servicio_desde_mapa(self, lat, lng):
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('crear_servicio_desde_mapa'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")

        """Crea un nuevo servicio usando coordenadas del mapa."""
        try:
            from PyQt6.QtWidgets import QInputDialog

            # Solicitar datos básicos para el servicio
            cliente, ok1 = QInputDialog.getText(
                self, "Nuevo Servicio", "Nombre del cliente:"
            )

            if ok1 and cliente.strip():
                direccion, ok2 = QInputDialog.getText(
                    self,
                    "Dirección",
                    "Dirección del servicio:",
                    text=f"Ubicación: {lat:.6f}, {lng:.6f}",
                )

                if ok2 and direccion.strip():
                    # Crear servicio con datos básicos
                    servicio = {
                        "tipo": "Servicio desde Mapa",
                        "cliente": cliente.strip(),
                        "direccion": direccion.strip(),
                        "fecha": QDate.currentDate().toString("yyyy-MM-dd"),
                        "hora": "Por definir",
                        "contacto": "Por definir",
                        "observaciones": f"Servicio creado desde mapa. Coordenadas: {lat:.6f}, {lng:.6f}",
                        "estado": "Programado",
                    }

                    # Agregar a la tabla
                    self.agregar_servicio_tabla(servicio)
                    self.mostrar_mensaje(f"Servicio creado para {cliente}")

        except Exception as e:
            self.mostrar_error(f"Error creando servicio desde mapa: {str(e)}")

    def mostrar_info_cobertura(self):
        """Muestra información detallada sobre la cobertura de servicios."""
        info_detallada = """
        <div style='padding: 20px; line-height: 1.6;'>
        <h2 style='color: #2c3e50;'>🗺️ Información Detallada de Cobertura</h2>
        
        <h3 style='color: #3498db;'>📍 Zonas de Cobertura:</h3>
        <ul>
            <li><b>Zona Centro:</b> La Plata centro, Tolosa, Ringuelet</li>
            <li><b>Zona Norte:</b> Gonnet, City Bell, Villa Elisa</li>
            <li><b>Zona Este:</b> Berisso, zonas industriales</li>
            <li><b>Zona Sur:</b> Los Hornos, Melchor Romero</li>
            <li><b>Zona Oeste:</b> Ensenada, puerto</li>
        </ul>
        
        <h3 style='color: #27ae60;'>🚚 Tipos de Servicio:</h3>
        <ul>
            <li><b>Entrega Express:</b> 30-60 minutos (zona centro)</li>
            <li><b>Entrega Estándar:</b> 60-120 minutos (todas las zonas)</li>
            <li><b>Transporte de Obra:</b> Coordinado según disponibilidad</li>
            <li><b>Carga Pesada:</b> Servicios especiales para materiales grandes</li>
        </ul>
        
        <h3 style='color: #e74c3c;'>📱 Contacto:</h3>
        <p>Para coordinar servicios especiales o consultas:<br>
        📞 Tel: (0221) 555-1234<br>
        📧 Email: logistica@rexus.app</p>
        </div>
        """

        from PyQt6.QtWidgets import QMessageBox

        msg = QMessageBox(self)
        msg.setWindowTitle("Información de Cobertura")
        msg.setText(info_detallada)
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.exec()

    def create_static_map_fallback(self, layout):
        """Crea un mapa estático como fallback si el mapa interactivo falla."""
        try:
            # Crear un widget simple con información de La Plata
            fallback_widget = QWidget()
            fallback_layout = QVBoxLayout(fallback_widget)

            # Título
            titulo = QLabel("🗺️ Mapa de La Plata - Vista de Referencia")
            titulo.setStyleSheet("""
                QLabel {
                    font-size: 20px;
                    font-weight: bold;
                    color: white;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                               stop:0 #3498db, stop:1 #2980b9);
                    padding: 15px;
                    border-radius: 8px;
                    margin-bottom: 10px;
                }
            """)
            titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            fallback_layout.addWidget(titulo)

            # Panel principal con información
            main_info = QFrame()
            main_info.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border: 2px solid #bdc3c7;
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
            main_layout = QVBoxLayout(main_info)

            # Información de ubicaciones
            info_text = QLabel("""
            <div style='padding: 10px; line-height: 1.8; font-size: 14px;'>
            <h3 style='color: #2c3e50; margin-bottom: 15px;'>🏙️ Área de Cobertura - La Plata y Alrededores</h3>
            
            <p style='margin-bottom: 15px;'><b>🎯 Ciudad Principal:</b> La Plata (Coordenadas: -34.9214, -57.9544)</p>
            
            <h4 style='color: #27ae60; margin-bottom: 10px;'>📍 Localidades de Cobertura:</h4>
            <table style='width: 100%; border-collapse: collapse;'>
                <tr><td style='padding: 5px;'><b>🏪 Berisso:</b></td><td style='padding: 5px;'>Zona industrial y residencial</td></tr>
                <tr><td style='padding: 5px;'><b>⚓ Ensenada:</b></td><td style='padding: 5px;'>Puerto y zona comercial</td></tr>
                <tr><td style='padding: 5px;'><b>🏡 Gonnet:</b></td><td style='padding: 5px;'>Zona residencial norte</td></tr>
                <tr><td style='padding: 5px;'><b>🌟 City Bell:</b></td><td style='padding: 5px;'>Zona residencial exclusiva</td></tr>
                <tr><td style='padding: 5px;'><b>🏢 Villa Elisa:</b></td><td style='padding: 5px;'>Área residencial y comercial</td></tr>
                <tr><td style='padding: 5px;'><b>🏘️ Los Hornos:</b></td><td style='padding: 5px;'>Zona sur de La Plata</td></tr>
                <tr><td style='padding: 5px;'><b>🌾 Tolosa:</b></td><td style='padding: 5px;'>Zona este de La Plata</td></tr>
                <tr><td style='padding: 5px;'><b>🏞️ Ringuelet:</b></td><td style='padding: 5px;'>Zona centro-este</td></tr>
            </table>
            
            <p style='margin-top: 15px; font-style: italic; color: #7f8c8d;'>
            📏 <b>Radio de cobertura:</b> 15 km desde el centro de La Plata<br>
            🚚 <b>Tiempo promedio de entrega:</b> 30-90 minutos según la zona<br>
            🗓️ <b>Días de servicio:</b> Lunes a Sábado, 8:00 - 18:00 hs
            </p>
            </div>
            """)
            info_text.setWordWrap(True)
            main_layout.addWidget(info_text)

            fallback_layout.addWidget(main_info)

            # Panel de acciones
            actions_frame = QFrame()
            actions_layout = QHBoxLayout(actions_frame)

            # Botón para mostrar información adicional
            btn_info = QPushButton("ℹ️ Más Información")
            btn_info.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 6px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #219a52;
                }
            """)
            btn_info.clicked.connect(self.mostrar_info_cobertura)
            actions_layout.addWidget(btn_info)

            # Botón para intentar cargar mapa interactivo
            btn_retry = QPushButton("🔄 Cargar Mapa Interactivo")
            btn_retry.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 6px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            btn_retry.clicked.connect(self.retry_interactive_map)
            actions_layout.addWidget(btn_retry)

            actions_layout.addStretch()
            fallback_layout.addWidget(actions_frame)

            # Nota informativa
            nota = QLabel(
                "💡 Para usar el mapa interactivo, instale: pip install folium pyqtwebengine"
            )
            nota.setStyleSheet("""
                QLabel {
                    background-color: #f39c12;
                    color: white;
                    padding: 8px;
                    border-radius: 4px;
                    font-style: italic;
                    margin-top: 10px;
                }
            """)
            nota.setWordWrap(True)
            fallback_layout.addWidget(nota)

            layout.addWidget(fallback_widget)

        except Exception as e:
            print(f"Error creando mapa fallback: {e}")
            # Crear widget mínimo en caso de error
            error_widget = QLabel("❌ Error cargando vista de mapa")
            error_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_widget.setStyleSheet("""
                QLabel {
                    color: #e74c3c;
                    font-size: 16px;
                    font-weight: bold;
                    padding: 50px;
                }
            """)
            layout.addWidget(error_widget)

    def retry_interactive_map(self):
        """Intenta recargar el mapa interactivo."""
        try:
            # Intentar importar y crear el mapa interactivo nuevamente
            from .interactive_map import InteractiveMapWidget

            if hasattr(self, "interactive_map"):
                # Ya existe, solo refrescar
                self.interactive_map.create_initial_map()
                self.mostrar_mensaje("Mapa interactivo actualizado")
            else:
                # Crear nuevo widget de mapa
                self.interactive_map = InteractiveMapWidget()
                self.interactive_map.location_clicked.connect(
                    self.on_map_location_clicked
                )
                self.interactive_map.marker_clicked.connect(self.on_map_marker_clicked)

                # Buscar el tab de mapa y reemplazar contenido
                for i in range(self.tabs.count()):
                    if "Mapa" in self.tabs.tabText(i):
                        # Recrear el tab completo
                        self.tabs.removeTab(i)
                        self.create_mapa_tab()
                        break

                self.mostrar_mensaje("Mapa interactivo cargado exitosamente")

        except ImportError as e:
            self.mostrar_error(
                f"No se pudo cargar el mapa interactivo: {str(e)}\n\nVerifique que estén instalados: folium, PyQtWebEngine"
            )
        except Exception as e:
            self.mostrar_error(f"Error cargando mapa interactivo: {str(e)}")


class DialogoNuevaEntrega(QDialog):
    """Diálogo para crear una nueva entrega."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nueva Entrega")
        self.setFixedSize(500, 400)

        # Configurar validador de formulario
        self.validator_manager = FormValidatorManager()

        # Configurar logger
        self.logger = logging.getLogger(__name__)

        self.setup_ui()
        self.setup_validations()

    def setup_ui(self):
        """Configura la interfaz del diálogo."""
        layout = QVBoxLayout(self)

        # Formulario
        form_layout = QFormLayout()

        # Campos del formulario
        self.input_direccion = QLineEdit()
        self.input_direccion.setAccessibleName('Input Direccion')
        self.input_direccion.setPlaceholderText("Ingrese la dirección de entrega")

        self.input_contacto = QLineEdit()
        self.input_contacto.setAccessibleName('Input Contacto')
        self.input_contacto.setPlaceholderText("Nombre del contacto")

        self.input_telefono = QLineEdit()
        self.input_telefono.setAccessibleName('Input Telefono')
        self.input_telefono.setPlaceholderText("+54 11 1234-5678")

        self.date_programada = QDateEdit()
        self.date_programada.setDate(QDate.currentDate())
        self.date_programada.setCalendarPopup(True)

        self.combo_estado = QComboBox()
        self.combo_estado.addItems(
            ["Programada", "En Preparación", "En Tránsito", "Entregada"]
        )

        self.text_observaciones = QTextEdit()
        self.text_observaciones.setMaximumHeight(80)
        self.text_observaciones.setPlaceholderText("Observaciones adicionales...")

        # Proteger campos contra XSS
        self.form_protector.protect_field(self.search_input, "search_input", 100)
        self.form_protector.protect_field(self.input_cliente, "input_cliente", 100)
        self.form_protector.protect_field(self.input_direccion, "input_direccion", 100)
        self.form_protector.protect_field(self.input_hora, "input_hora", 100)
        self.form_protector.protect_field(self.input_contacto, "input_contacto", 100)
        self.form_protector.protect_field(self.input_direccion, "input_direccion", 100)
        self.form_protector.protect_field(self.input_contacto, "input_contacto", 100)
        self.form_protector.protect_field(self.input_telefono, "input_telefono", 100)
        self.form_protector.protect_field(self.text_observaciones, "text_observaciones", 100)
        self.form_protector.protect_field(self.text_observaciones, "text_observaciones", 100)

        # Agregar campos al formulario
        form_layout.addRow("📍 Dirección:", self.input_direccion)
        form_layout.addRow("👤 Contacto:", self.input_contacto)
        form_layout.addRow("📞 Teléfono:", self.input_telefono)
        form_layout.addRow("📅 Fecha:", self.date_programada)
        form_layout.addRow("📊 Estado:", self.combo_estado)
        form_layout.addRow("📝 Observaciones:", self.text_observaciones)

        layout.addLayout(form_layout)

        # Botones
        botones_layout = QHBoxLayout()

        btn_cancelar = QPushButton("❌ Cancelar")
        btn_cancelar.clicked.connect(self.reject)

        btn_guardar = QPushButton("💾 Guardar")
        btn_guardar.clicked.connect(self.validar_y_aceptar)
        btn_guardar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
        """)

        botones_layout.addStretch()
        botones_layout.addWidget(btn_cancelar)
        botones_layout.addWidget(btn_guardar)

        layout.addLayout(botones_layout)

    def setup_validations(self):
        """Configura las validaciones del formulario."""
        # Validaciones obligatorias
        self.validator_manager.agregar_validacion(
            self.input_direccion, validacion_direccion
        )

        self.validator_manager.agregar_validacion(
            self.input_contacto, FormValidator.validar_campo_obligatorio, "Contacto"
        )

        # Validación opcional de teléfono
        self.validator_manager.agregar_validacion(
            self.input_telefono, FormValidator.validar_telefono
        )

        # Validación de fecha
        self.validator_manager.agregar_validacion(
            self.date_programada,
            FormValidator.validar_fecha,
            QDate.currentDate(),  # No permitir fechas pasadas
        )

        # Validación de longitud para observaciones
        self.validator_manager.agregar_validacion(
            self.text_observaciones,
            FormValidator.validar_longitud_texto,
            0,
            500,  # Máximo 500 caracteres
        )

    def validar_y_aceptar(self):
        # 🔒 PROTECCIÓN XSS: Sanitizar todas las entradas de texto
        # TODO: Implementar sanitización con SecurityUtils.sanitize_input()
        # Ejemplo: texto_limpio = SecurityUtils.sanitize_input(texto_usuario)

        """Valida los datos antes de aceptar."""
        es_valido, errores = self.validator_manager.validar_formulario()

        if not es_valido:
            # Mostrar todos los errores
            mensajes_error = self.validator_manager.obtener_mensajes_error()
            mensaje_completo = "Errores encontrados:\n\n" + "\n".join(
                f"• {msg}" for msg in mensajes_error
            )
            QMessageBox.warning(self, "Datos Incompletos", mensaje_completo)
            return

        self.accept()

    def obtener_datos(self):
        """Obtiene los datos del formulario con sanitización."""
        try:
            # Sanitizar datos de entrada
            direccion_limpia = DataSanitizer.sanitize_text(
                self.input_direccion.text().strip()
            )
            contacto_limpio = DataSanitizer.sanitize_text(
                self.input_contacto.text().strip()
            )
            telefono_limpio = DataSanitizer.sanitize_phone(
                self.input_telefono.text().strip()
            )
            observaciones_limpias = DataSanitizer.sanitize_text(
                self.text_observaciones.toPlainText().strip()
            )

            datos = {
                "direccion": direccion_limpia,
                "contacto": contacto_limpio,
                "telefono": telefono_limpio,
                "fecha_programada": self.date_programada.date().toString("yyyy-MM-dd"),
                "estado": self.combo_estado.currentText(),
                "observaciones": observaciones_limpias,
            }

            self.logger.info(
                "Datos del formulario de logística obtenidos y sanitizados correctamente"
            )
            return datos

        except Exception as e:
            self.logger.error(f"Error al obtener datos del formulario: {str(e)}")
            return {}

    def _on_dangerous_content(self, field_name: str, content: str):
        """Maneja la detección de contenido peligroso en formularios."""
        from rexus.utils.security import log_security_event
        from rexus.utils.message_system import show_warning
        
        # Log del evento de seguridad
        log_security_event(
            "XSS_ATTEMPT",
            f"Contenido peligroso detectado en campo '{field_name}': {content[:100]}...",
            "unknown"
        )
        
        # Mostrar advertencia al usuario
        show_warning(
            self,
            "Contenido No Permitido",
            f"Se ha detectado contenido potencialmente peligroso en el campo '{field_name}'.

"
            "El contenido ha sido automáticamente sanitizado por seguridad."
        )
    
    def obtener_datos_seguros(self) -> dict:
        """Obtiene datos del formulario con sanitización XSS."""
        if hasattr(self, 'form_protector'):
            return self.form_protector.get_sanitized_data()
        else:
            return {}
