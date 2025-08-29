"""
Vista de Logística Mejorada - Rexus.app

Vista completa del módulo de logística con:
- Gestión avanzada de servicios con formularios
- Programación en cronograma/calendario
- Visualización de mapa con obras y servicios
- Integración completa con base de datos
"""

import logging
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QTableWidget, QTabWidget,
                             QMessageBox, QHeaderView, QSplitter, QFrame,
                             QCalendarWidget, QTextEdit, QDateEdit, QComboBox,
                             QLineEdit, QGroupBox, QScrollArea, QTableWidgetItem)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QFont

# Importar componentes avanzados
from .components.servicios_widget import ServiciosWidget
from .components.mapa_widget import MapaWidget
from .components.estadisticas_widget import EstadisticasWidget
from .components.tabla_transportes_widget import TablaTransportesWidget

# Importar logging
try:
    from ...utils.app_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
class LogisticaView(QWidget):
    """
    Vista principal del módulo de logística con implementación completa.

    Incluye:
    - Gestión avanzada de servicios con formularios
    - Programación en cronograma/calendario
    - Visualización de mapa con obras y servicios
    - Integración completa con base de datos
    """

    # Señales
    servicio_selected = pyqtSignal(dict)
    transporte_selected = pyqtSignal(dict)
    mapa_location_selected = pyqtSignal(float, float)

    def __init__(self, controller=None):
        """Inicializar vista de logística."""
        super().__init__()
        self.controller = controller
        self.current_data = {}

        # Componentes avanzados
        self.servicios_widget = None
        self.mapa_widget = None
        self.estadisticas_widget = None
        self.transportes_widget = None

        self.setup_ui()
        self.load_initial_data()

        logger.info("LogisticaView avanzada inicializada correctamente")
    
    def setup_ui(self):
        """Configurar interfaz completa de usuario."""
        try:
            # Layout principal
            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(10, 10, 10, 10)
            main_layout.setSpacing(15)

            # Título
            title_label = QLabel("Sistema de Gestión Logística Integral")
            title_font = QFont()
            title_font.setPointSize(18)
            title_font.setBold(True)
            title_label.setFont(title_font)
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            main_layout.addWidget(title_label)

            # Pestañas principales
            self.tab_widget = QTabWidget()
            main_layout.addWidget(self.tab_widget)

            # Pestaña 1: Servicios de Mantenimiento
            self.setup_servicios_tab()

            # Pestaña 2: Cronograma/Calendario
            self.setup_cronograma_tab()

            # Pestaña 3: Mapa de Obras y Servicios
            self.setup_mapa_tab()

            # Pestaña 4: Transportes
            self.setup_transportes_tab()

            # Pestaña 5: Estadísticas y Reportes
            self.setup_estadisticas_tab()

            logger.debug("Interfaz completa de logística configurada")

        except Exception as e:
            logger.error(f"Error configurando UI completa de logística: {e}")
            QMessageBox.critical(self, "Error", f"Error configurando interfaz: {e}")
    
    def setup_servicios_tab(self):
        """Configurar pestaña avanzada de servicios de mantenimiento."""
        try:
            # Usar el componente avanzado de servicios
            self.servicios_widget = ServiciosWidget()
            self.servicios_widget.set_controller(self.controller)

            # Conectar señales
            if hasattr(self.servicios_widget, 'service_created'):
                self.servicios_widget.service_created.connect(self.on_service_created)
            if hasattr(self.servicios_widget, 'service_updated'):
                self.servicios_widget.service_updated.connect(self.on_service_updated)

            self.tab_widget.addTab(self.servicios_widget, "Servicios de Mantenimiento")

        except Exception as e:
            logger.error(f"Error configurando pestaña de servicios: {e}")
            # Fallback a implementación básica
            self.setup_servicios_basic_tab()

    # ===== MÉTODOS DE EVENTOS PARA COMPONENTES AVANZADOS =====

    def setup_servicios_basic_tab(self):
        """Configurar pestaña básica de servicios como fallback."""
        servicios_widget = QWidget()
        servicios_layout = QVBoxLayout(servicios_widget)

        # Panel de acciones
        acciones_layout = QHBoxLayout()

        btn_nuevo_servicio = QPushButton("Nuevo Servicio")
        btn_nuevo_servicio.clicked.connect(self.nuevo_servicio)
        acciones_layout.addWidget(btn_nuevo_servicio)

        btn_editar_servicio = QPushButton("Editar")
        btn_editar_servicio.clicked.connect(self.editar_servicio)
        acciones_layout.addWidget(btn_editar_servicio)

        btn_eliminar_servicio = QPushButton("Eliminar")
        btn_eliminar_servicio.clicked.connect(self.eliminar_servicio)
        acciones_layout.addWidget(btn_eliminar_servicio)

        acciones_layout.addStretch()
        servicios_layout.addLayout(acciones_layout)

        # Tabla de servicios
        self.tabla_servicios = QTableWidget(0, 8)
        self.tabla_servicios.setHorizontalHeaderLabels([
            "ID", "Código", "Cliente/Obra", "Tipo", "Estado", "Fecha Programada",
            "Fecha Real", "Costo Estimado"
        ])

        # Configurar tabla
        header = self.tabla_servicios.horizontalHeader()
        if header:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        servicios_layout.addWidget(self.tabla_servicios)
        self.tab_widget.addTab(servicios_widget, "Servicios de Mantenimiento")
    
    def setup_rutas_tab(self):
        """Configurar pestaña de rutas."""
        rutas_widget = QWidget()
        rutas_layout = QVBoxLayout(rutas_widget)

        info_label = QLabel("Gestión de rutas y planificación de entregas")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rutas_layout.addWidget(info_label)

        # Tabla de rutas
        self.tabla_rutas = QTableWidget(0, 4)
        self.tabla_rutas.setHorizontalHeaderLabels([
            "ID", "Origen", "Destino", "Distancia"
        ])

        rutas_layout.addWidget(self.tabla_rutas)

        self.tab_widget.addTab(rutas_widget, "Rutas")

    # ===== MÉTODOS DE FUNCIONALIDAD ADICIONAL =====
    def nuevo_servicio(self):
        """Crear nuevo servicio."""
        try:
            from .dialogo_servicios import DialogoGenerarServicio
            dialogo = DialogoGenerarServicio(parent=self, controller=self.controller)
            dialogo.servicio_guardado.connect(self.on_servicio_guardado)
            dialogo.exec()
            logger.info("Diálogo de nuevo servicio abierto")

        except Exception as e:
            logger.error(f"Error creando nuevo servicio: {e}")
            QMessageBox.critical(self, "Error", f"Error creando servicio: {e}")

    def editar_servicio(self):
        """Editar servicio seleccionado."""
        try:
            # Obtener el servicio seleccionado
            servicio_id = None
            if hasattr(self, 'servicios_widget') and self.servicios_widget:
                # Si tenemos el widget avanzado, obtener de ahí
                if hasattr(self.servicios_widget, 'get_selected_service_id'):
                    servicio_id = self.servicios_widget.get_selected_service_id()  # type: ignore
            elif hasattr(self, 'tabla_servicios'):
                # Fallback a tabla básica
                current_row = self.tabla_servicios.currentRow()
                if current_row >= 0:
                    item = self.tabla_servicios.item(current_row, 0)
                    if item:
                        servicio_id = item.text()

            if servicio_id:
                from .dialogo_servicios import DialogoGenerarServicio
                dialogo = DialogoGenerarServicio(
                    parent=self,
                    servicio_id=servicio_id,
                    controller=self.controller
                )
                dialogo.servicio_guardado.connect(self.on_servicio_guardado)
                dialogo.exec()
                logger.info(f"Diálogo de edición abierto para servicio {servicio_id}")
            else:
                QMessageBox.information(self, "Seleccionar Servicio",
                                      "Por favor seleccione un servicio para editar")

        except Exception as e:
            logger.error(f"Error editando servicio: {e}")
            QMessageBox.critical(self, "Error", f"Error editando servicio: {e}")

    def eliminar_servicio(self):
        """Eliminar servicio seleccionado."""
        try:
            # Obtener el servicio seleccionado
            servicio_id = None
            servicio_info = ""

            if hasattr(self, 'servicios_widget') and self.servicios_widget:
                # Si tenemos el widget avanzado, obtener de ahí
                if hasattr(self.servicios_widget, 'get_selected_service_info'):
                    servicio_info = self.servicios_widget.get_selected_service_info()  # type: ignore
                    servicio_id = servicio_info.get('id') if isinstance(servicio_info, dict) else None
            elif hasattr(self, 'tabla_servicios'):
                # Fallback a tabla básica
                current_row = self.tabla_servicios.currentRow()
                if current_row >= 0:
                    item = self.tabla_servicios.item(current_row, 0)
                    if item:
                        servicio_id = item.text()
                        servicio_info = f"Servicio {servicio_id}"

            if servicio_id:
                respuesta = QMessageBox.question(
                    self,
                    "Confirmar Eliminación",
                    f"¿Está seguro de que desea eliminar {servicio_info}?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )

                if respuesta == QMessageBox.StandardButton.Yes:
                    if self.controller and hasattr(self.controller, 'eliminar_servicio_transporte'):
                        exito = self.controller.eliminar_servicio_transporte(servicio_id)
                        if exito:
                            QMessageBox.information(self, "Éxito", "Servicio eliminado correctamente")
                            self.refresh_servicios()
                        else:
                            QMessageBox.critical(self, "Error", "Error eliminando el servicio")
                    else:
                        QMessageBox.critical(self, "Error", "Controlador no disponible")
            else:
                QMessageBox.information(self, "Seleccionar Servicio",
                                      "Por favor seleccione un servicio para eliminar")

        except Exception as e:
            logger.error(f"Error eliminando servicio: {e}")
            QMessageBox.critical(self, "Error", f"Error eliminando servicio: {e}")

    def nuevo_transporte(self):
        """Crear nuevo transporte."""
        try:
            logger.info("Crear nuevo transporte solicitado")
            # Implementar diálogo de transporte cuando esté disponible
            QMessageBox.information(self, "Próximamente", "Diálogo de transporte próximamente")

        except Exception as e:
            logger.error(f"Error creando nuevo transporte: {e}")
            QMessageBox.critical(self, "Error", f"Error creando transporte: {e}")

    def editar_transporte(self):
        """Editar transporte seleccionado."""
        try:
            logger.info("Editar transporte solicitado")
            # Implementar edición de transporte cuando esté disponible
            QMessageBox.information(self, "Próximamente", "Edición de transporte próximamente")

        except Exception as e:
            logger.error(f"Error editando transporte: {e}")
            QMessageBox.critical(self, "Error", f"Error editando transporte: {e}")

    # ===== MÉTODOS DE EVENTOS PARA SERVICIOS =====

    def on_servicio_guardado(self, servicio_data):
        """Manejar cuando se guarda un servicio."""
        try:
            logger.info(f"Servicio guardado: {servicio_data}")
            # Actualizar la vista
            self.refresh_servicios()
            # Emitir señal si es necesario
            if 'id' in servicio_data:
                self.servicio_selected.emit(servicio_data)

        except Exception as e:
            logger.error(f"Error manejando servicio guardado: {e}")

    # ===== MÉTODOS DE EVENTOS PARA COMPONENTES AVANZADOS =====

    def on_service_created(self, service_data):
        """Manejar creación de nuevo servicio."""
        try:
            logger.info(f"Servicio creado: {service_data}")
            self.servicio_selected.emit(service_data)
            # Actualizar datos si es necesario
            self.refresh_servicios()
        except Exception as e:
            logger.error(f"Error manejando creación de servicio: {e}")

    def on_service_updated(self, service_data):
        """Manejar actualización de servicio."""
        try:
            logger.info(f"Servicio actualizado: {service_data}")
            # Actualizar datos si es necesario
            self.refresh_servicios()
        except Exception as e:
            logger.error(f"Error manejando actualización de servicio: {e}")

    def on_fecha_calendario_clicked(self, date):
        """Manejar selección de fecha en calendario."""
        try:
            logger.info(f"Fecha seleccionada en calendario: {date.toString()}")
            # Cargar servicios para la fecha seleccionada
            self.cargar_servicios_por_fecha(date)
        except Exception as e:
            logger.error(f"Error manejando selección de fecha: {e}")

    def on_mapa_location_selected(self, lat, lon):
        """Manejar selección de ubicación en mapa."""
        try:
            logger.info(f"Ubicación seleccionada en mapa: {lat}, {lon}")
            self.mapa_location_selected.emit(lat, lon)
        except Exception as e:
            logger.error(f"Error manejando selección de ubicación: {e}")

    def on_transporte_selected(self, transporte_data):
        """Manejar selección de transporte en la tabla."""
        try:
            logger.info(f"Transporte seleccionado: {transporte_data}")
            self.transporte_selected.emit(transporte_data)
        except Exception as e:
            logger.error(f"Error manejando selección de transporte: {e}")

    # ===== MÉTODOS PARA NUEVAS PESTAÑAS =====

    def setup_cronograma_tab(self):
        """Configurar pestaña de cronograma/calendario."""
        cronograma_widget = QWidget()
        cronograma_layout = QVBoxLayout(cronograma_widget)

        # Título
        titulo_label = QLabel("Cronograma de Servicios y Entregas")
        titulo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo_font = QFont()
        titulo_font.setPointSize(14)
        titulo_font.setBold(True)
        titulo_label.setFont(titulo_font)
        cronograma_layout.addWidget(titulo_label)

        # Calendario
        self.calendario = QCalendarWidget()
        self.calendario.clicked.connect(self.on_fecha_calendario_clicked)
        cronograma_layout.addWidget(self.calendario)

        # Panel de detalles del día seleccionado
        detalles_group = QGroupBox("Servicios del Día Seleccionado")
        detalles_layout = QVBoxLayout(detalles_group)

        self.tabla_cronograma = QTableWidget(0, 5)
        self.tabla_cronograma.setHorizontalHeaderLabels([
            "Hora", "Tipo", "Descripción", "Ubicación", "Estado"
        ])

        header = self.tabla_cronograma.horizontalHeader()
        if header:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        detalles_layout.addWidget(self.tabla_cronograma)
        cronograma_layout.addWidget(detalles_group)

        self.tab_widget.addTab(cronograma_widget, "Cronograma")

    def setup_mapa_tab(self):
        """Configurar pestaña de mapa."""
        try:
            # Usar el componente avanzado de mapa
            self.mapa_widget = MapaWidget()
            self.mapa_widget.location_selected.connect(self.on_mapa_location_selected)

            # Configurar mapa con datos iniciales
            if hasattr(self.mapa_widget, 'refresh_data'):
                self.mapa_widget.refresh_data()

            self.tab_widget.addTab(self.mapa_widget, "Mapa de Obras y Servicios")

        except Exception as e:
            logger.error(f"Error configurando pestaña de mapa: {e}")
            # Fallback a implementación básica
            self.setup_mapa_basic_tab()

    def setup_mapa_basic_tab(self):
        """Configurar pestaña básica de mapa como fallback."""
        mapa_widget = QWidget()
        mapa_layout = QVBoxLayout(mapa_widget)

        info_label = QLabel("Mapa de visualización de obras y servicios")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("font-size: 14px; color: #666; padding: 20px;")
        mapa_layout.addWidget(info_label)

        # Placeholder para mapa
        mapa_placeholder = QLabel("Aquí se mostrará el mapa interactivo")
        mapa_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mapa_placeholder.setStyleSheet("""
            QLabel {
                border: 2px dashed #ccc;
                padding: 40px;
                background-color: #f9f9f9;
                color: #666;
                font-size: 16px;
            }
        """)
        mapa_layout.addWidget(mapa_placeholder)

        self.tab_widget.addTab(mapa_widget, "Mapa de Obras y Servicios")

    def setup_transportes_tab(self):
        """Configurar pestaña avanzada de transportes."""
        try:
            # Usar el componente avanzado de transportes
            self.transportes_widget = TablaTransportesWidget()
            # Conectar señales si existen
            if hasattr(self.transportes_widget, 'transporte_selected'):
                self.transportes_widget.transporte_selected.connect(self.on_transporte_selected)  # type: ignore

            self.tab_widget.addTab(self.transportes_widget, "Transportes")

        except Exception as e:
            logger.error(f"Error configurando pestaña de transportes: {e}")
            # Fallback a implementación básica
            self.setup_transportes_basic_tab()

    def setup_transportes_basic_tab(self):
        """Configurar pestaña básica de transportes como fallback."""
        transportes_widget = QWidget()
        transportes_layout = QVBoxLayout(transportes_widget)

        # Panel de acciones
        acciones_layout = QHBoxLayout()

        btn_nuevo_transporte = QPushButton("Nuevo Transporte")
        btn_nuevo_transporte.clicked.connect(self.nuevo_transporte)
        acciones_layout.addWidget(btn_nuevo_transporte)

        btn_editar_transporte = QPushButton("Editar")
        btn_editar_transporte.clicked.connect(self.editar_transporte)
        acciones_layout.addWidget(btn_editar_transporte)

        acciones_layout.addStretch()
        transportes_layout.addLayout(acciones_layout)

        # Tabla de transportes
        self.tabla_transportes = QTableWidget(0, 5)
        self.tabla_transportes.setHorizontalHeaderLabels([
            "ID", "Vehículo", "Conductor", "Estado", "Capacidad"
        ])

        # Configurar tabla
        header = self.tabla_transportes.horizontalHeader()
        if header:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        transportes_layout.addWidget(self.tabla_transportes)
        self.tab_widget.addTab(transportes_widget, "Transportes")

    def setup_estadisticas_tab(self):
        """Configurar pestaña de estadísticas."""
        try:
            # Usar el componente avanzado de estadísticas
            self.estadisticas_widget = EstadisticasWidget()
            # Conectar señales si existen

            self.tab_widget.addTab(self.estadisticas_widget, "Estadísticas y Reportes")

        except Exception as e:
            logger.error(f"Error configurando pestaña de estadísticas: {e}")
            # Fallback a implementación básica
            self.setup_estadisticas_basic_tab()

    def setup_estadisticas_basic_tab(self):
        """Configurar pestaña básica de estadísticas como fallback."""
        estadisticas_widget = QWidget()
        estadisticas_layout = QVBoxLayout(estadisticas_widget)

        info_label = QLabel("Estadísticas y reportes de logística")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        estadisticas_layout.addWidget(info_label)

        # Placeholder para estadísticas
        stats_placeholder = QLabel("Aquí se mostrarán las estadísticas")
        stats_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        stats_placeholder.setStyleSheet("""
            QLabel {
                border: 2px dashed #ccc;
                padding: 40px;
                background-color: #f9f9f9;
                color: #666;
                font-size: 16px;
            }
        """)
        estadisticas_layout.addWidget(stats_placeholder)

        self.tab_widget.addTab(estadisticas_widget, "Estadísticas y Reportes")

    # ===== MÉTODOS DE FUNCIONALIDAD ADICIONAL =====

    def cargar_servicios_por_fecha(self, fecha):
        """Cargar servicios programados para una fecha específica."""
        try:
            if not self.controller:
                return

            # Obtener servicios para la fecha
            servicios_fecha = self.controller.obtener_servicios_por_fecha(fecha)

            # Limpiar tabla
            if hasattr(self, 'tabla_cronograma'):
                self.tabla_cronograma.setRowCount(0)

                # Llenar tabla con servicios
                for servicio in servicios_fecha:
                    row_position = self.tabla_cronograma.rowCount()
                    self.tabla_cronograma.insertRow(row_position)

                    # Extraer datos del servicio
                    hora = servicio.get('hora_programada', 'N/A')
                    tipo = servicio.get('tipo_servicio', 'N/A')
                    descripcion = servicio.get('descripcion', 'N/A')
                    ubicacion = servicio.get('ubicacion', 'N/A')
                    estado = servicio.get('estado', 'N/A')

                    self.tabla_cronograma.setItem(row_position, 0, QTableWidgetItem(str(hora)))
                    self.tabla_cronograma.setItem(row_position, 1, QTableWidgetItem(str(tipo)))
                    self.tabla_cronograma.setItem(row_position, 2, QTableWidgetItem(str(descripcion)))
                    self.tabla_cronograma.setItem(row_position, 3, QTableWidgetItem(str(ubicacion)))
                    self.tabla_cronograma.setItem(row_position, 4, QTableWidgetItem(str(estado)))

            logger.debug(f"Servicios cargados para fecha {fecha.toString()}: {len(servicios_fecha)}")

        except Exception as e:
            logger.error(f"Error cargando servicios por fecha: {e}")

    def refresh_servicios(self):
        """Actualizar tabla de servicios."""
        try:
            if hasattr(self, 'servicios_widget') and self.servicios_widget:
                # Si tenemos el widget avanzado, usar su método de actualización
                if hasattr(self.servicios_widget, 'refresh_data'):
                    self.servicios_widget.refresh_data()
            elif hasattr(self, 'tabla_servicios') and self.controller:
                # Fallback a tabla básica
                servicios = self.controller.obtener_servicios_transporte()

                # Limpiar tabla
                self.tabla_servicios.setRowCount(0)

                # Llenar tabla con servicios
                for servicio in servicios:
                    row_position = self.tabla_servicios.rowCount()
                    self.tabla_servicios.insertRow(row_position)

                    # Extraer datos del servicio
                    id_servicio = servicio.get('id', '')
                    codigo = servicio.get('codigo', '')
                    cliente = servicio.get('cliente', 'N/A')
                    tipo = servicio.get('tipo_servicio', 'N/A')
                    estado = servicio.get('estado', 'N/A')
                    fecha_prog = servicio.get('fecha_programada', 'N/A')
                    fecha_real = servicio.get('fecha_real', 'N/A')
                    costo = servicio.get('costo_estimado', 0.0)

                    self.tabla_servicios.setItem(row_position, 0, QTableWidgetItem(str(id_servicio)))
                    self.tabla_servicios.setItem(row_position, 1, QTableWidgetItem(str(codigo)))
                    self.tabla_servicios.setItem(row_position, 2, QTableWidgetItem(str(cliente)))
                    self.tabla_servicios.setItem(row_position, 3, QTableWidgetItem(str(tipo)))
                    self.tabla_servicios.setItem(row_position, 4, QTableWidgetItem(str(estado)))
                    self.tabla_servicios.setItem(row_position, 5, QTableWidgetItem(str(fecha_prog)))
                    self.tabla_servicios.setItem(row_position, 6, QTableWidgetItem(str(fecha_real)))
                    self.tabla_servicios.setItem(row_position, 7, QTableWidgetItem(f"${costo:.2f}"))

            logger.debug("Servicios actualizados")

        except Exception as e:
            logger.error(f"Error actualizando servicios: {e}")

    def load_initial_data(self):
        """Cargar datos iniciales."""
        try:
            if self.controller:
                # Cargar servicios
                self.refresh_servicios()

                # Cargar datos de mapa si existe
                if hasattr(self, 'mapa_widget') and self.mapa_widget:
                    if hasattr(self.mapa_widget, 'cargar_datos_iniciales'):
                        self.mapa_widget.cargar_datos_iniciales()  # type: ignore

                # Cargar datos de estadísticas si existe
                if hasattr(self, 'estadisticas_widget') and self.estadisticas_widget:
                    if hasattr(self.estadisticas_widget, 'cargar_estadisticas'):
                        self.estadisticas_widget.cargar_estadisticas()  # type: ignore

            logger.debug("Datos iniciales de logística cargados")

        except Exception as e:
            logger.error(f"Error cargando datos iniciales: {e}")


# Crear alias para compatibilidad
LogisticaModernView = LogisticaView