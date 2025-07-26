"""
Vista de Logística Modernizada

Interfaz moderna para la gestión de logística y transporte.
"""

from datetime import datetime

from PyQt6.QtCore import QDate, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
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


class LogisticaView(QWidget):
    """Vista modernizada para gestión de logística."""
    
    # Señales
    entrega_seleccionada = pyqtSignal(dict)
    crear_entrega_solicitada = pyqtSignal(dict)
    actualizar_entrega_solicitada = pyqtSignal(dict)
    eliminar_entrega_solicitada = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.controller = None
        self.entregas_data = []
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
        self.search_input.setPlaceholderText("Buscar entregas...")
        self.search_input.setFixedWidth(200)
        filtros_layout.addWidget(QLabel("Buscar:"))
        filtros_layout.addWidget(self.search_input)
        
        # Filtro por estado
        self.combo_estado = QComboBox()
        self.combo_estado.addItems(["Todos", "Programada", "En Tránsito", "Entregada", "Cancelada"])
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
        filtros_layout.addWidget(btn_nueva_entrega)
        
        filtros_layout.addStretch()
        layout.addWidget(filtros_group)
        
        # Tabla de entregas
        self.tabla_entregas = QTableWidget()
        self.tabla_entregas.setColumnCount(7)
        self.tabla_entregas.setHorizontalHeaderLabels([
            "ID", "Fecha Programada", "Dirección", "Estado", "Contacto", "Observaciones", "Acciones"
        ])
        
        # Configurar tabla
        header = self.tabla_entregas.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.tabla_entregas.setColumnWidth(0, 60)
        self.tabla_entregas.setAlternatingRowColors(True)
        self.tabla_entregas.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
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
        self.combo_tipo_servicio.addItems([
            "Entrega Domicilio",
            "Transporte Obra",
            "Servicio Express",
            "Carga Pesada",
            "Servicio Programado"
        ])
        self.combo_tipo_servicio.setFixedWidth(200)
        
        # Cliente/Destino
        self.input_cliente = QLineEdit()
        self.input_cliente.setPlaceholderText("Nombre del cliente o destino")
        self.input_cliente.setFixedWidth(300)
        
        # Dirección
        self.input_direccion = QLineEdit()
        self.input_direccion.setPlaceholderText("Dirección completa de entrega")
        self.input_direccion.setFixedWidth(400)
        
        # Fecha programada
        self.date_programada = QDateEdit()
        self.date_programada.setDate(QDate.currentDate())
        self.date_programada.setCalendarPopup(True)
        self.date_programada.setFixedWidth(150)
        
        # Hora programada
        self.input_hora = QLineEdit()
        self.input_hora.setPlaceholderText("HH:MM")
        self.input_hora.setFixedWidth(100)
        
        # Contacto
        self.input_contacto = QLineEdit()
        self.input_contacto.setPlaceholderText("Teléfono de contacto")
        self.input_contacto.setFixedWidth(200)
        
        # Observaciones
        self.text_observaciones = QTextEdit()
        self.text_observaciones.setPlaceholderText("Observaciones adicionales del servicio")
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
        self.tabla_servicios.setHorizontalHeaderLabels([
            "ID", "Tipo", "Cliente", "Dirección", "Fecha", "Hora", "Estado", "Acciones"
        ])
        
        # Configurar tabla
        header = self.tabla_servicios.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.tabla_servicios.setColumnWidth(0, 60)
        self.tabla_servicios.setAlternatingRowColors(True)
        self.tabla_servicios.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        tabla_layout.addWidget(self.tabla_servicios)
        layout.addWidget(tabla_group)
        
        self.tabs.addTab(servicios_widget, "🚚 Servicios")
    
    def create_mapa_tab(self):
        """Crea el tab del mapa con ubicaciones."""
        mapa_widget = QWidget()
        layout = QVBoxLayout(mapa_widget)
        
        # Panel de controles del mapa
        controles_group = QGroupBox("🗺️ Controles del Mapa")
        controles_layout = QHBoxLayout(controles_group)
        
        # Filtros del mapa
        self.combo_filtro_mapa = QComboBox()
        self.combo_filtro_mapa.addItems([
            "Mostrar Todo",
            "Solo Servicios",
            "Solo Obras",
            "Servicios Activos",
            "Obras En Proceso"
        ])
        self.combo_filtro_mapa.setFixedWidth(150)
        controles_layout.addWidget(QLabel("Filtro:"))
        controles_layout.addWidget(self.combo_filtro_mapa)
        
        # Botón actualizar mapa
        btn_actualizar_mapa = QPushButton("🔄 Actualizar Mapa")
        btn_actualizar_mapa.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        btn_actualizar_mapa.clicked.connect(self.actualizar_mapa)
        controles_layout.addWidget(btn_actualizar_mapa)
        
        # Botón centrar mapa
        btn_centrar = QPushButton("📍 Centrar Mapa")
        btn_centrar.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        btn_centrar.clicked.connect(self.centrar_mapa)
        controles_layout.addWidget(btn_centrar)
        
        controles_layout.addStretch()
        layout.addWidget(controles_group)
        
        # Área del mapa de La Plata y alrededores
        mapa_frame = QFrame()
        mapa_frame.setMinimumHeight(500)
        mapa_frame.setStyleSheet("""
            QFrame {
                background-color: #e8f5e8;
                border: 2px solid #27ae60;
                border-radius: 8px;
                background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="800" height="500" viewBox="0 0 800 500"><rect width="800" height="500" fill="%23e8f5e8"/><g stroke="%23666" stroke-width="1" fill="none"><path d="M50 50 Q200 80 350 60 Q500 40 650 70 Q750 90 800 100"/><path d="M0 150 Q150 130 300 140 Q450 150 600 135 Q750 120 800 130"/><path d="M50 250 Q200 230 350 240 Q500 250 650 235 Q750 220 800 230"/><path d="M0 350 Q150 330 300 340 Q450 350 600 335 Q750 320 800 330"/><path d="M50 450 Q200 430 350 440 Q500 450 650 435 Q750 420 800 430"/></g><g stroke="%23999" stroke-width="0.5" fill="none"><line x1="100" y1="0" x2="100" y2="500"/><line x1="200" y1="0" x2="200" y2="500"/><line x1="300" y1="0" x2="300" y2="500"/><line x1="400" y1="0" x2="400" y2="500"/><line x1="500" y1="0" x2="500" y2="500"/><line x1="600" y1="0" x2="600" y2="500"/><line x1="700" y1="0" x2="700" y2="500"/><line x1="0" y1="100" x2="800" y2="100"/><line x1="0" y1="200" x2="800" y2="200"/><line x1="0" y1="300" x2="800" y2="300"/><line x1="0" y1="400" x2="800" y2="400"/></g><text x="200" y="30" font-size="16" fill="%23333" font-weight="bold">BERISSO</text><text x="350" y="30" font-size="20" fill="%23333" font-weight="bold">LA PLATA</text><text x="550" y="30" font-size="16" fill="%23333" font-weight="bold">ENSENADA</text><text x="120" y="180" font-size="14" fill="%23666">Los Hornos</text><text x="280" y="150" font-size="14" fill="%23666">Casco Urbano</text><text x="450" y="160" font-size="14" fill="%23666">Gonnet</text><text x="580" y="180" font-size="14" fill="%23666">City Bell</text><text x="150" y="280" font-size="14" fill="%23666">San Carlos</text><text x="350" y="250" font-size="14" fill="%23666">Tolosa</text><text x="500" y="280" font-size="14" fill="%23666">Villa Elisa</text><text x="100" y="380" font-size="14" fill="%23666">Melchor Romero</text><text x="320" y="350" font-size="14" fill="%23666">Ringuelet</text><text x="520" y="380" font-size="14" fill="%23666">Arturo Seguí</text><circle cx="180" cy="200" r="4" fill="%23e74c3c"/><text x="190" y="205" font-size="10" fill="%23e74c3c">Servicio Activo</text><circle cx="380" cy="170" r="4" fill="%2327ae60"/><text x="390" y="175" font-size="10" fill="%2327ae60">Obra en Proceso</text><circle cx="520" cy="300" r="4" fill="%233498db"/><text x="530" y="305" font-size="10" fill="%233498db">Entrega Programada</text><circle cx="150" cy="320" r="4" fill="%23f39c12"/><text x="160" y="325" font-size="10" fill="%23f39c12">Servicio Pendiente</text><circle cx="450" cy="220" r="4" fill="%239b59b6"/><text x="460" y="225" font-size="10" fill="%239b59b6">Ruta Optimizada</text><circle cx="600" cy="150" r="4" fill="%23e67e22"/><text x="610" y="155" font-size="10" fill="%23e67e22">Punto de Entrega</text></svg>');
                background-repeat: no-repeat;
                background-position: center;
                background-size: contain;
            }
        """)
        
        mapa_layout = QVBoxLayout(mapa_frame)
        
        # Panel de información del mapa (sin ocupar espacio del mapa)
        info_panel = QWidget()
        info_panel.setMaximumHeight(60)
        info_panel.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 0.95);
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                margin: 10px;
            }
        """)
        info_layout = QHBoxLayout(info_panel)
        
        # Leyenda compacta
        leyenda_label = QLabel("🗺️ Mapa de La Plata y Alrededores | 🔴 Servicios Activos | 🟢 Obras en Proceso | 🔵 Entregas Programadas | 🟠 Servicios Pendientes | 🟣 Rutas Optimizadas")
        leyenda_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #2c3e50;
                font-weight: bold;
                padding: 8px;
            }
        """)
        info_layout.addWidget(leyenda_label)
        
        # Agregar panel de información encima del mapa
        layout.addWidget(info_panel)
        
        layout.addWidget(mapa_frame)
        
        # Panel de información lateral
        info_group = QGroupBox("📋 Información de Ubicaciones")
        info_layout = QVBoxLayout(info_group)
        
        # Lista de ubicaciones
        self.lista_ubicaciones = QTableWidget()
        self.lista_ubicaciones.setColumnCount(4)
        self.lista_ubicaciones.setHorizontalHeaderLabels([
            "Tipo", "Descripción", "Dirección", "Estado"
        ])
        self.lista_ubicaciones.setMaximumHeight(150)
        
        # Configurar tabla de ubicaciones
        header_ubicaciones = self.lista_ubicaciones.horizontalHeader()
        header_ubicaciones.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.lista_ubicaciones.setAlternatingRowColors(True)
        
        info_layout.addWidget(self.lista_ubicaciones)
        layout.addWidget(info_group)
        
        self.tabs.addTab(mapa_widget, "🗺️ Mapa")
    
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
            self.tabla_entregas.setItem(row, 0, QTableWidgetItem(str(entrega.get('id', ''))))
            self.tabla_entregas.setItem(row, 1, QTableWidgetItem(str(entrega.get('fecha_programada', ''))))
            self.tabla_entregas.setItem(row, 2, QTableWidgetItem(str(entrega.get('direccion_entrega', ''))))
            self.tabla_entregas.setItem(row, 3, QTableWidgetItem(str(entrega.get('estado', ''))))
            self.tabla_entregas.setItem(row, 4, QTableWidgetItem(str(entrega.get('contacto', ''))))
            self.tabla_entregas.setItem(row, 5, QTableWidgetItem(str(entrega.get('observaciones', ''))))
            
            # Botón de acciones
            btn_accion = QPushButton('⚙️')
            btn_accion.setMaximumWidth(30)
            btn_accion.setToolTip("Acciones")
            self.tabla_entregas.setCellWidget(row, 6, btn_accion)
    
    def actualizar_estadisticas(self, estadisticas):
        """Actualiza las estadísticas mostradas."""
        self.label_total_entregas.setText(str(estadisticas.get('total_entregas', 0)))
        self.label_entregas_pendientes.setText(str(estadisticas.get('entregas_pendientes', 0)))
        self.label_entregas_completadas.setText(str(estadisticas.get('entregas_completadas', 0)))
        self.label_entregas_canceladas.setText(str(estadisticas.get('entregas_canceladas', 0)))
        self.label_promedio_tiempo.setText(f"{estadisticas.get('promedio_tiempo', 0)} horas")
    
    def mostrar_mensaje(self, mensaje):
        """Muestra un mensaje informativo."""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.information(self, "Logística", mensaje)
    
    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error."""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(self, "Error - Logística", mensaje)
    
    def generar_servicio(self):
        """Genera un nuevo servicio con los datos del formulario."""
        try:
            # Obtener datos del formulario
            tipo_servicio = self.combo_tipo_servicio.currentText()
            cliente = self.input_cliente.text().strip()
            direccion = self.input_direccion.text().strip()
            fecha = self.date_programada.date().toString("yyyy-MM-dd")
            hora = self.input_hora.text().strip()
            contacto = self.input_contacto.text().strip()
            observaciones = self.text_observaciones.toPlainText().strip()
            
            # Validar datos obligatorios
            if not cliente or not direccion:
                self.mostrar_error("Por favor complete los campos obligatorios: Cliente y Dirección")
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
                "estado": "Programado"
            }
            
            # Agregar a la tabla
            self.agregar_servicio_tabla(servicio)
            
            # Mostrar mensaje de éxito
            self.mostrar_mensaje(f"Servicio '{tipo_servicio}' generado exitosamente para {cliente}")
            
            # Limpiar formulario
            self.limpiar_formulario()
            
        except Exception as e:
            self.mostrar_error(f"Error al generar servicio: {str(e)}")
    
    def agregar_servicio_tabla(self, servicio):
        """Agrega un servicio a la tabla de servicios."""
        try:
            row = self.tabla_servicios.rowCount()
            self.tabla_servicios.insertRow(row)
            
            # Generar ID único
            service_id = f"SRV{row + 1:03d}"
            
            # Llenar datos en la tabla
            self.tabla_servicios.setItem(row, 0, QTableWidgetItem(service_id))
            self.tabla_servicios.setItem(row, 1, QTableWidgetItem(servicio["tipo"]))
            self.tabla_servicios.setItem(row, 2, QTableWidgetItem(servicio["cliente"]))
            self.tabla_servicios.setItem(row, 3, QTableWidgetItem(servicio["direccion"]))
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
            
        except Exception as e:
            self.mostrar_error(f"Error al agregar servicio a la tabla: {str(e)}")
    
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
        """Actualiza la tabla de ubicaciones del mapa."""
        try:
            # Limpiar tabla
            self.lista_ubicaciones.setRowCount(0)
            
            # Agregar ubicaciones demo de La Plata
            ubicaciones_demo = [
                ("Servicio", "Entrega Domicilio", "Calle 7 entre 47 y 48, La Plata", "Activo"),
                ("Obra", "Construcción Edificio", "Av. 13 y 60, La Plata", "En Proceso"),
                ("Servicio", "Transporte Vidrios", "Calle 50 entre 15 y 16, Berisso", "Programado"),
                ("Obra", "Remodelación Casa", "Calle 25 entre 3 y 4, Gonnet", "En Proceso"),
                ("Servicio", "Entrega Herrajes", "Av. 122 y 82, Los Hornos", "Pendiente"),
                ("Obra", "Ampliación Local", "Calle 1 y 57, Tolosa", "Pausada"),
                ("Servicio", "Servicio Express", "Calle 10 y 38, City Bell", "Activo"),
                ("Obra", "Construcción Galpón", "Av. 44 y 150, Villa Elisa", "En Proceso"),
                ("Servicio", "Transporte Pesado", "Calle 520 y 15, Melchor Romero", "Programado"),
                ("Obra", "Refacción Oficinas", "Calle 2 y 64, Ringuelet", "En Proceso"),
            ]
            
            # Agregar servicios de la tabla
            for row in range(self.tabla_servicios.rowCount()):
                tipo_item = self.tabla_servicios.item(row, 1)
                cliente_item = self.tabla_servicios.item(row, 2)
                direccion_item = self.tabla_servicios.item(row, 3)
                estado_item = self.tabla_servicios.item(row, 6)
                
                if tipo_item and cliente_item and direccion_item and estado_item:
                    ubicaciones_demo.append((
                        "Servicio",
                        f"{tipo_item.text()} - {cliente_item.text()}",
                        direccion_item.text(),
                        estado_item.text()
                    ))
            
            # Llenar tabla de ubicaciones
            self.lista_ubicaciones.setRowCount(len(ubicaciones_demo))
            for row, (tipo, descripcion, direccion, estado) in enumerate(ubicaciones_demo):
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
                self.tabla_servicios.setItem(row, 0, QTableWidgetItem(str(servicio.get('id', ''))))
                self.tabla_servicios.setItem(row, 1, QTableWidgetItem(str(servicio.get('tipo', ''))))
                self.tabla_servicios.setItem(row, 2, QTableWidgetItem(str(servicio.get('cliente', ''))))
                self.tabla_servicios.setItem(row, 3, QTableWidgetItem(str(servicio.get('direccion', ''))))
                self.tabla_servicios.setItem(row, 4, QTableWidgetItem(str(servicio.get('fecha_programada', ''))))
                self.tabla_servicios.setItem(row, 5, QTableWidgetItem(str(servicio.get('hora', ''))))
                self.tabla_servicios.setItem(row, 6, QTableWidgetItem(str(servicio.get('estado', ''))))
                
                # Botón de acciones
                btn_acciones = QPushButton('⚙️')
                btn_acciones.setMaximumWidth(30)
                btn_acciones.setToolTip("Acciones")
                self.tabla_servicios.setCellWidget(row, 7, btn_acciones)
                
        except Exception as e:
            print(f"Error cargando servicios: {str(e)}")