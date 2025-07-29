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

from rexus.utils.form_validators import FormValidator, FormValidatorManager, validacion_direccion


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
        btn_nueva_entrega.clicked.connect(self.mostrar_dialogo_nueva_entrega)
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
        if header is not None:
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
        if header is not None:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.tabla_servicios.setColumnWidth(0, 60)
        self.tabla_servicios.setAlternatingRowColors(True)
        self.tabla_servicios.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        tabla_layout.addWidget(self.tabla_servicios)
        layout.addWidget(tabla_group)
        
        self.tabs.addTab(servicios_widget, "🚚 Servicios")
    
    def create_mapa_tab(self):
        """Crea el tab del mapa interactivo con OpenStreetMap."""
        mapa_widget = QWidget()
        layout = QVBoxLayout(mapa_widget)
        layout.setContentsMargins(5, 5, 5, 5)  # Menos margen para más espacio al mapa
        
        # Panel de controles compacto
        controles_group = QGroupBox("🗺️ Mapa Interactivo")
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
        self.combo_filtro_mapa.setFixedWidth(130)
        self.combo_filtro_mapa.currentTextChanged.connect(self.filtrar_mapa)
        controles_layout.addWidget(QLabel("Filtro:"))
        controles_layout.addWidget(self.combo_filtro_mapa)
        
        # Botón agregar marcador (más compacto)
        btn_agregar_marcador = QPushButton("📍 Agregar")
        btn_agregar_marcador.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 6px 12px;
                font-weight: bold;
                border-radius: 3px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
        """)
        btn_agregar_marcador.clicked.connect(self.agregar_marcador_mapa)
        controles_layout.addWidget(btn_agregar_marcador)
        
        # Botón limpiar marcadores (más compacto)
        btn_limpiar = QPushButton("🧹 Limpiar")
        btn_limpiar.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                padding: 6px 12px;
                font-weight: bold;
                border-radius: 3px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        btn_limpiar.clicked.connect(self.limpiar_marcadores_mapa)
        controles_layout.addWidget(btn_limpiar)
        
        controles_layout.addStretch()
        layout.addWidget(controles_group)
        
        # Crear mapa interactivo (ocupa la mayor parte del espacio)
        try:
            from .interactive_map import InteractiveMapWidget
            self.interactive_map = InteractiveMapWidget()
            
            # Conectar señales del mapa
            self.interactive_map.location_clicked.connect(self.on_map_location_clicked)
            self.interactive_map.marker_clicked.connect(self.on_map_marker_clicked)
            
            # El mapa toma todo el espacio disponible
            layout.addWidget(self.interactive_map, stretch=1)
            
            # Cargar ubicaciones iniciales directamente en el mapa
            self.actualizar_ubicaciones_mapa()
            
        except ImportError as e:
            print(f"Error importando mapa interactivo: {e}")
            # Fallback simplificado sin información de cobertura
            self.create_simple_map_fallback(layout)
        
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
    
    def mostrar_dialogo_nueva_entrega(self):
        """Muestra el diálogo para crear una nueva entrega."""
        dialog = DialogoNuevaEntrega(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            datos_entrega = dialog.obtener_datos()
            try:
                # Emitir señal para que el controlador maneje la creación
                self.crear_entrega_solicitada.emit(datos_entrega)
                self.mostrar_mensaje("Entrega creada exitosamente")
            except Exception as e:
                self.mostrar_error(f"Error al crear entrega: {str(e)}")
    
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
    
    def filtrar_mapa(self, filtro_texto):
        """Filtra los marcadores del mapa según el criterio seleccionado."""
        try:
            if hasattr(self, 'interactive_map'):
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
                            
                            servicios.append({
                                'coords': coords,
                                'tipo': self.tabla_servicios.item(row, 1).text() if self.tabla_servicios.item(row, 1) else "",
                                'cliente': self.tabla_servicios.item(row, 2).text() if self.tabla_servicios.item(row, 2) else "",
                                'direccion': direccion,
                                'estado': self.tabla_servicios.item(row, 6).text() if self.tabla_servicios.item(row, 6) else "",
                                'fecha': self.tabla_servicios.item(row, 4).text() if self.tabla_servicios.item(row, 4) else ""
                            })
                    
                    self.interactive_map.add_service_markers(servicios)
                
                elif filtro_texto == "Servicios Activos":
                    # Filtrar solo servicios con estado "Activo" o "Programado"
                    servicios_activos = []
                    for row in range(self.tabla_servicios.rowCount()):
                        estado_item = self.tabla_servicios.item(row, 6)
                        if estado_item and estado_item.text() in ["Activo", "Programado", "En Tránsito"]:
                            direccion_item = self.tabla_servicios.item(row, 3)
                            if direccion_item:
                                direccion = direccion_item.text()
                                from .interactive_map import geocode_address_la_plata
                                coords = geocode_address_la_plata(direccion)
                                
                                servicios_activos.append({
                                    'coords': coords,
                                    'tipo': self.tabla_servicios.item(row, 1).text() if self.tabla_servicios.item(row, 1) else "",
                                    'cliente': self.tabla_servicios.item(row, 2).text() if self.tabla_servicios.item(row, 2) else "",
                                    'direccion': direccion,
                                    'estado': estado_item.text(),
                                    'fecha': self.tabla_servicios.item(row, 4).text() if self.tabla_servicios.item(row, 4) else ""
                                })
                    
                    self.interactive_map.add_service_markers(servicios_activos)
                
                else:
                    # "Mostrar Todo" o otros filtros - resetear al mapa inicial
                    self.interactive_map.create_initial_map()
                    
                self.actualizar_ubicaciones_mapa()
                
        except Exception as e:
            print(f"Error filtrando mapa: {e}")
    
    def agregar_marcador_mapa(self):
        """Muestra diálogo para agregar un marcador personalizado al mapa."""
        try:
            from PyQt6.QtWidgets import QInputDialog, QComboBox
            
            # Diálogo para dirección
            direccion, ok = QInputDialog.getText(
                self, 
                "Agregar Ubicación", 
                "Ingrese la dirección o ubicación en La Plata:"
            )
            
            if ok and direccion.strip():
                # Obtener coordenadas
                from .interactive_map import geocode_address_la_plata
                coords = geocode_address_la_plata(direccion.strip())
                
                # Diálogo para descripción
                descripcion, ok2 = QInputDialog.getText(
                    self,
                    "Descripción",
                    "Ingrese una descripción para esta ubicación:"
                )
                
                if ok2 and hasattr(self, 'interactive_map'):
                    # Agregar marcador al mapa
                    self.interactive_map.add_custom_marker(
                        coords[0], coords[1],
                        direccion.strip(),
                        descripcion.strip() or "Ubicación personalizada",
                        "servicio"
                    )
                    
                    self.mostrar_mensaje(f"Ubicación agregada: {direccion}")
                    self.actualizar_ubicaciones_mapa()
                    
        except Exception as e:
            self.mostrar_error(f"Error agregando marcador: {str(e)}")
    
    def limpiar_marcadores_mapa(self):
        """Limpia todos los marcadores personalizados del mapa."""
        try:
            if hasattr(self, 'interactive_map'):
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
            
            mensaje = f"Ubicación seleccionada:\n\nLatitud: {lat:.6f}\nLongitud: {lng:.6f}"
            
            # Preguntar si desea agregar un servicio en esta ubicación
            respuesta = QMessageBox.question(
                self,
                "Ubicación Seleccionada",
                f"{mensaje}\n\n¿Desea agregar un servicio en esta ubicación?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if respuesta == QMessageBox.StandardButton.Yes:
                # Abrir diálogo para nuevo servicio con coordenadas pre-cargadas
                self.crear_servicio_desde_mapa(lat, lng)
                
        except Exception as e:
            print(f"Error manejando clic en mapa: {e}")
    
    def on_map_marker_clicked(self, marker_data):
        """Maneja el evento de clic en un marcador del mapa."""
        try:
            # Mostrar información detallada del marcador
            from PyQt6.QtWidgets import QMessageBox
            
            titulo = marker_data.get('title', 'Marcador')
            descripcion = marker_data.get('description', 'Sin descripción')
            tipo = marker_data.get('type', 'desconocido')
            
            mensaje = f"Información del Marcador:\n\nTítulo: {titulo}\nDescripción: {descripcion}\nTipo: {tipo.title()}"
            
            QMessageBox.information(
                self,
                "Información del Marcador",
                mensaje
            )
            
        except Exception as e:
            print(f"Error manejando clic en marcador: {e}")
    
    def crear_servicio_desde_mapa(self, lat, lng):
        """Crea un nuevo servicio usando coordenadas del mapa."""
        try:
            from PyQt6.QtWidgets import QInputDialog
            
            # Solicitar datos básicos para el servicio
            cliente, ok1 = QInputDialog.getText(
                self,
                "Nuevo Servicio",
                "Nombre del cliente:"
            )
            
            if ok1 and cliente.strip():
                direccion, ok2 = QInputDialog.getText(
                    self,
                    "Dirección",
                    "Dirección del servicio:",
                    text=f"Ubicación: {lat:.6f}, {lng:.6f}"
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
                        "estado": "Programado"
                    }
                    
                    # Agregar a la tabla
                    self.agregar_servicio_tabla(servicio)
                    self.mostrar_mensaje(f"Servicio creado para {cliente}")
                    
        except Exception as e:
            self.mostrar_error(f"Error creando servicio desde mapa: {str(e)}")
    
    def create_static_map_fallback(self, layout):
        """Crea un mapa estático como fallback si el mapa interactivo falla."""
        try:
            # Crear un widget simple con información de La Plata
            fallback_widget = QWidget()
            fallback_layout = QVBoxLayout(fallback_widget)
            
            # Título
            titulo = QLabel("🗺️ Mapa de La Plata - Vista Simplificada")
            titulo.setStyleSheet("""
                QLabel {
                    font-size: 18px;
                    font-weight: bold;
                    color: #2c3e50;
                    padding: 20px;
                    text-align: center;
                }
            """)
            titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            fallback_layout.addWidget(titulo)
            
            # Información de ubicaciones
            info_text = QLabel("""
            <div style='padding: 20px; line-height: 1.6;'>
            <h3>Área de Cobertura - La Plata y Alrededores</h3>
            <p><b>Ciudad Principal:</b> La Plata (-34.9214, -57.9544)</p>
            
            <h4>Localidades de Cobertura:</h4>
            <ul>
                <li><b>Berisso:</b> Zona industrial y residencial</li>
                <li><b>Ensenada:</b> Puerto y zona comercial</li>
                <li><b>Gonnet:</b> Zona residencial norte</li>
                <li><b>City Bell:</b> Zona residencial exclusiva</li>
                <li><b>Villa Elisa:</b> Área residencial y comercial</li>
                <li><b>Los Hornos:</b> Zona sur de La Plata</li>
                <li><b>Tolosa:</b> Zona este de La Plata</li>
                <li><b>Ringuelet:</b> Zona centro-este</li>
            </ul>
            
            <p><i>Radio de cobertura: 15 km desde el centro de La Plata</i></p>
            </div>
            """)
            info_text.setWordWrap(True)
            info_text.setStyleSheet("""
                QLabel {
                    background-color: white;
                    border: 1px solid #bdc3c7;
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
            fallback_layout.addWidget(info_text)
            
            # Botón para intentar cargar mapa interactivo
            btn_retry = QPushButton("🔄 Intentar Cargar Mapa Interactivo")
            btn_retry.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 6px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            btn_retry.clicked.connect(self.retry_interactive_map)
            fallback_layout.addWidget(btn_retry)
            
            fallback_layout.addStretch()
            layout.addWidget(fallback_widget)
            
        except Exception as e:
            print(f"Error creando mapa fallback: {e}")
    
    def create_simple_map_fallback(self, layout):
        """Crea un mapa simplificado sin información de cobertura."""
        try:
            # Widget simple para el mapa
            fallback_widget = QWidget()
            fallback_layout = QVBoxLayout(fallback_widget)
            
            # Título simple
            titulo = QLabel("🗺️ Mapa de Ubicaciones")
            titulo.setStyleSheet("""
                QLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #2c3e50;
                    padding: 15px;
                    text-align: center;
                    background-color: white;
                    border: 1px solid #bdc3c7;
                    border-radius: 6px;
                }
            """)
            titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
            fallback_layout.addWidget(titulo)
            
            # Lista compacta de ubicaciones actuales
            ubicaciones_label = QLabel("📍 Ubicaciones Registradas:")
            ubicaciones_label.setStyleSheet("font-weight: bold; padding: 10px; color: #34495e;")
            fallback_layout.addWidget(ubicaciones_label)
            
            # Tabla simple de ubicaciones
            self.lista_ubicaciones = QTableWidget()
            self.lista_ubicaciones.setColumnCount(3)
            self.lista_ubicaciones.setHorizontalHeaderLabels([
                "Tipo", "Descripción", "Estado"
            ])
            
            # Configurar tabla
            header = self.lista_ubicaciones.horizontalHeader()
            if header is not None:
                header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.lista_ubicaciones.setAlternatingRowColors(True)
            self.lista_ubicaciones.setMaximumHeight(200)
            self.lista_ubicaciones.setStyleSheet("""
                QTableWidget {
                    gridline-color: #bdc3c7;
                    background-color: white;
                    border: 1px solid #bdc3c7;
                    border-radius: 4px;
                }
            """)
            
            fallback_layout.addWidget(self.lista_ubicaciones)
            
            # Mensaje informativo
            info_label = QLabel("💡 Use los botones de arriba para agregar nuevas ubicaciones")
            info_label.setStyleSheet("color: #7f8c8d; font-style: italic; padding: 10px;")
            info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            fallback_layout.addWidget(info_label)
            
            fallback_layout.addStretch()
            layout.addWidget(fallback_widget)
            
        except Exception as e:
            print(f"Error en simple fallback: {e}")
            error_label = QLabel("❌ Error cargando vista del mapa")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setStyleSheet("color: red; padding: 20px;")
            layout.addWidget(error_label)
    
    def retry_interactive_map(self):
        """Intenta recargar el mapa interactivo."""
        try:
            # Intentar importar y crear el mapa interactivo nuevamente
            from .interactive_map import InteractiveMapWidget
            
            if hasattr(self, 'interactive_map'):
                # Ya existe, solo refrescar
                self.interactive_map.create_initial_map()
                self.mostrar_mensaje("Mapa interactivo actualizado")
            else:
                # Crear nuevo widget de mapa
                self.interactive_map = InteractiveMapWidget()
                self.interactive_map.location_clicked.connect(self.on_map_location_clicked)
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
            self.mostrar_error(f"No se pudo cargar el mapa interactivo: {str(e)}\n\nVerifique que estén instalados: folium, PyQtWebEngine")
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
        
        self.setup_ui()
        self.setup_validations()
    
    def setup_ui(self):
        """Configura la interfaz del diálogo."""
        layout = QVBoxLayout(self)
        
        # Formulario
        form_layout = QFormLayout()
        
        # Campos del formulario
        self.input_direccion = QLineEdit()
        self.input_direccion.setPlaceholderText("Ingrese la dirección de entrega")
        
        self.input_contacto = QLineEdit()
        self.input_contacto.setPlaceholderText("Nombre del contacto")
        
        self.input_telefono = QLineEdit()
        self.input_telefono.setPlaceholderText("+54 11 1234-5678")
        
        self.date_programada = QDateEdit()
        self.date_programada.setDate(QDate.currentDate())
        self.date_programada.setCalendarPopup(True)
        
        self.combo_estado = QComboBox()
        self.combo_estado.addItems(["Programada", "En Preparación", "En Tránsito", "Entregada"])
        
        self.text_observaciones = QTextEdit()
        self.text_observaciones.setMaximumHeight(80)
        self.text_observaciones.setPlaceholderText("Observaciones adicionales...")
        
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
            self.input_direccion, 
            validacion_direccion
        )
        
        self.validator_manager.agregar_validacion(
            self.input_contacto,
            FormValidator.validar_campo_obligatorio,
            "Contacto"
        )
        
        # Validación opcional de teléfono
        self.validator_manager.agregar_validacion(
            self.input_telefono,
            FormValidator.validar_telefono
        )
        
        # Validación de fecha
        self.validator_manager.agregar_validacion(
            self.date_programada,
            FormValidator.validar_fecha,
            QDate.currentDate()  # No permitir fechas pasadas
        )
        
        # Validación de longitud para observaciones
        self.validator_manager.agregar_validacion(
            self.text_observaciones,
            FormValidator.validar_longitud_texto,
            0, 500  # Máximo 500 caracteres
        )
    
    def validar_y_aceptar(self):
        """Valida los datos antes de aceptar."""
        es_valido, errores = self.validator_manager.validar_formulario()
        
        if not es_valido:
            # Mostrar todos los errores
            mensajes_error = self.validator_manager.obtener_mensajes_error()
            mensaje_completo = "Errores encontrados:\n\n" + "\n".join(f"• {msg}" for msg in mensajes_error)
            QMessageBox.warning(self, "Datos Incompletos", mensaje_completo)
            return
        
        self.accept()
    
    def obtener_datos(self):
        """Obtiene los datos del formulario."""
        return {
            'direccion': self.input_direccion.text().strip(),
            'contacto': self.input_contacto.text().strip(),
            'telefono': self.input_telefono.text().strip(),
            'fecha_programada': self.date_programada.date().toString('yyyy-MM-dd'),
            'estado': self.combo_estado.currentText(),
            'observaciones': self.text_observaciones.toPlainText().strip()
        }