"""
MIT License

Copyright (c) 2024 Rexus.app

Módulo de Logística - Vista Principal
Vista básica funcional para el módulo de logística
"""

import logging
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTabWidget,
                             QMessageBox, QHeaderView)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

# Importar logging
try:
    from ...utils.app_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# Importar componentes base
try:
    from ...ui.templates.base_module_view import BaseModuleView
except ImportError:
    logger.warning("No se pudo importar BaseModuleView, usando QWidget")
    BaseModuleView = QWidget


class LogisticaView(QWidget):
    """Vista principal del módulo de logística."""
    
    # Señales
    servicio_selected = pyqtSignal(dict)
    transporte_selected = pyqtSignal(dict)
    
    def __init__(self, controller=None):
        """Inicializar vista de logística."""
        super().__init__()
        self.controller = controller
        self.current_data = {}
        
        self.setup_ui()
        self.load_initial_data()
        
        logger.info("LogisticaView inicializada correctamente")
    
    def setup_ui(self):
        """Configurar interfaz de usuario."""
        try:
            # Layout principal
            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(10, 10, 10, 10)
            main_layout.setSpacing(15)
            
            # Título
            title_label = QLabel("Gestión de Logística")
            title_font = QFont()
            title_font.setPointSize(16)
            title_font.setBold(True)
            title_label.setFont(title_font)
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            main_layout.addWidget(title_label)
            
            # Pestañas principales
            self.tab_widget = QTabWidget()
            main_layout.addWidget(self.tab_widget)
            
            # Pestaña de servicios
            self.setup_servicios_tab()
            
            # Pestaña de transportes
            self.setup_transportes_tab()
            
            # Pestaña de rutas
            self.setup_rutas_tab()
            
            logger.debug("Interfaz de logística configurada")
            
        except Exception as e:
            logger.error(f"Error configurando UI de logística: {e}")
    
    def setup_servicios_tab(self):
        """Configurar pestaña de servicios."""
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
        self.tabla_servicios = QTableWidget(0, 6)
        self.tabla_servicios.setHorizontalHeaderLabels([
            "ID", "Cliente", "Tipo", "Estado", "Fecha", "Costo"
        ])
        
        # Configurar tabla
        header = self.tabla_servicios.horizontalHeader()
        if header:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        servicios_layout.addWidget(self.tabla_servicios)
        
        self.tab_widget.addTab(servicios_widget, "Servicios")
    
    def setup_transportes_tab(self):
        """Configurar pestaña de transportes."""
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
    
    def load_initial_data(self):
        """Cargar datos iniciales."""
        try:
            if self.controller:
                # Cargar servicios
                self.refresh_servicios()
                
                # Cargar transportes
                self.refresh_transportes()
                
                # Cargar rutas
                self.refresh_rutas()
                
            logger.debug("Datos iniciales de logística cargados")
            
        except Exception as e:
            logger.error(f"Error cargando datos iniciales: {e}")
    
    def refresh_servicios(self):
        """Actualizar tabla de servicios."""
        try:
            if hasattr(self, 'tabla_servicios') and self.controller:
                # Aquí se cargarían los servicios desde el controlador
                logger.debug("Servicios actualizados")
                
        except Exception as e:
            logger.error(f"Error actualizando servicios: {e}")
    
    def refresh_transportes(self):
        """Actualizar tabla de transportes."""
        try:
            if hasattr(self, 'tabla_transportes') and self.controller:
                # Aquí se cargarían los transportes desde el controlador
                logger.debug("Transportes actualizados")
                
        except Exception as e:
            logger.error(f"Error actualizando transportes: {e}")
    
    def refresh_rutas(self):
        """Actualizar tabla de rutas."""
        try:
            if hasattr(self, 'tabla_rutas') and self.controller:
                # Aquí se cargarían las rutas desde el controlador
                logger.debug("Rutas actualizadas")
                
        except Exception as e:
            logger.error(f"Error actualizando rutas: {e}")
    
    # Métodos de acción
    def nuevo_servicio(self):
        """Crear nuevo servicio."""
        try:
            if not self.controller:
                return
                
            # Aquí iría la lógica para crear nuevo servicio
            logger.info("Crear nuevo servicio solicitado")
            
        except Exception as e:
            logger.error(f"Error creando nuevo servicio: {e}")
    
    def editar_servicio(self):
        """Editar servicio seleccionado."""
        try:
            if not hasattr(self, 'tabla_servicios'):
                return
                
            current_row = self.tabla_servicios.currentRow()
            if current_row >= 0:
                logger.info(f"Editar servicio en fila {current_row}")
                # Aquí iría la lógica de edición
                
        except Exception as e:
            logger.error(f"Error editando servicio: {e}")
    
    def eliminar_servicio(self):
        """Eliminar servicio seleccionado."""
        try:
            if not hasattr(self, 'tabla_servicios'):
                return
                
            current_row = self.tabla_servicios.currentRow()
            if current_row >= 0:
                respuesta = QMessageBox.question(
                    self,
                    "Confirmar Eliminación",
                    "¿Está seguro de que desea eliminar este servicio?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if respuesta == QMessageBox.StandardButton.Yes:
                    logger.info(f"Eliminar servicio en fila {current_row}")
                    # Aquí iría la lógica de eliminación
                    
        except Exception as e:
            logger.error(f"Error eliminando servicio: {e}")
    
    def nuevo_transporte(self):
        """Crear nuevo transporte."""
        try:
            logger.info("Crear nuevo transporte solicitado")
            # Aquí iría la lógica para crear nuevo transporte
            
        except Exception as e:
            logger.error(f"Error creando nuevo transporte: {e}")
    
    def editar_transporte(self):
        """Editar transporte seleccionado."""
        try:
            if not hasattr(self, 'tabla_transportes'):
                return
                
            current_row = self.tabla_transportes.currentRow()
            if current_row >= 0:
                logger.info(f"Editar transporte en fila {current_row}")
                # Aquí iría la lógica de edición
                
        except Exception as e:
            logger.error(f"Error editando transporte: {e}")


# Crear alias para compatibilidad
LogisticaModernView = LogisticaView