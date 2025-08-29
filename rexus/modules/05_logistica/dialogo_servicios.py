"""
Diálogos para gestión de servicios de logística - Rexus.app

Implementación completa de formularios para:
- Crear/editar servicios de transporte
- Previsualizar servicios antes de guardar
- Gestión de programaciones y cronogramas
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel,
    QLineEdit, QTextEdit, QComboBox, QDateEdit, QTimeEdit,
    QDoubleSpinBox, QPushButton, QGroupBox,
    QMessageBox, QScrollArea, QWidget, QCheckBox
)
from PyQt6.QtCore import Qt, QDate, QTime, pyqtSignal
from PyQt6.QtGui import QFont

# Importar logging
try:
    from ...utils.app_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

# Importar utilidades
try:
    from ...utils.unified_sanitizer import sanitize_string
    from ...utils.message_system import show_error, show_info, show_success
except ImportError:
    def sanitize_string(value: Any) -> str:  # type: ignore
        return str(value) if value else ""

    def show_error(parent, title: str, message: str, details: Optional[str] = None):  # type: ignore
        QMessageBox.critical(parent, title, message)

    def show_info(parent, title: str, message: str, auto_close: bool = False):  # type: ignore
        QMessageBox.information(parent, title, message)

    def show_success(parent, title: str, message: str, auto_close: bool = True):  # type: ignore
        QMessageBox.information(parent, title, message)


class DialogoGenerarServicio(QDialog):
    """
    Diálogo para crear/editar servicios de transporte.

    Permite configurar:
    - Información básica del servicio
    - Programación y fechas
    - Información de transporte
    - Costos y observaciones
    """

    # Señales
    servicio_guardado = pyqtSignal(dict)

    # Constantes para mensajes
    MSG_VALIDACION = "Validación"
    MSG_EXITO = "Éxito"
    MSG_ERROR = "Error"

    def __init__(self, parent=None, servicio_id: Optional[str] = None, controller=None):
        super().__init__(parent)
        self.servicio_id = servicio_id
        self.controller = controller
        self.es_edicion = servicio_id is not None

        self.setup_ui()
        self.configurar_validaciones()

        if self.es_edicion and self.servicio_id:
            self.cargar_datos_servicio()

        logger.info(f"Diálogo de servicio inicializado - Edición: {self.es_edicion}")

    def setup_ui(self):
        """Configurar la interfaz de usuario."""
        # Configuración básica
        titulo = "Editar Servicio" if self.es_edicion else "Nuevo Servicio de Transporte"
        self.setWindowTitle(titulo)
        self.setModal(True)
        self.resize(600, 700)

        # Layout principal
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Título
        titulo_label = QLabel(titulo)
        titulo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo_font = QFont()
        titulo_font.setPointSize(14)
        titulo_font.setBold(True)
        titulo_label.setFont(titulo_font)
        layout.addWidget(titulo_label)

        # Crear scroll area para el contenido
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Grupo: Información Básica
        self.setup_informacion_basica(scroll_layout)

        # Grupo: Programación
        self.setup_programacion(scroll_layout)

        # Grupo: Transporte
        self.setup_transporte(scroll_layout)

        # Grupo: Costos
        self.setup_costos(scroll_layout)

        # Grupo: Observaciones
        self.setup_observaciones(scroll_layout)

        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        # Botones
        self.setup_botones(layout)

    def setup_informacion_basica(self, layout):
        """Configurar sección de información básica."""
        group = QGroupBox("Información Básica")
        form_layout = QFormLayout(group)

        # Código
        self.txt_codigo = QLineEdit()
        self.txt_codigo.setPlaceholderText("Código automático o manual")
        form_layout.addRow("Código:", self.txt_codigo)

        # Descripción
        self.txt_descripcion = QTextEdit()
        self.txt_descripcion.setMaximumHeight(60)
        self.txt_descripcion.setPlaceholderText("Descripción del servicio...")
        form_layout.addRow("Descripción:", self.txt_descripcion)

        # Tipo de servicio
        self.cmb_tipo_servicio = QComboBox()
        self.cmb_tipo_servicio.addItems([
            "ENTREGA", "RECOGIDA", "TRASLADO", "DISTRIBUCION",
            "LOGISTICA_INVERSA", "SERVICIO_ESPECIAL"
        ])
        form_layout.addRow("Tipo de Servicio:", self.cmb_tipo_servicio)

        # Cliente/Obra
        self.txt_cliente = QLineEdit()
        self.txt_cliente.setPlaceholderText("Cliente o identificación de obra")
        form_layout.addRow("Cliente/Obra:", self.txt_cliente)

        layout.addWidget(group)

    def setup_programacion(self, layout):
        """Configurar sección de programación."""
        group = QGroupBox("Programación")
        form_layout = QFormLayout(group)

        # Fecha programada
        self.date_programada = QDateEdit()
        self.date_programada.setDate(QDate.currentDate())
        self.date_programada.setCalendarPopup(True)
        form_layout.addRow("Fecha Programada:", self.date_programada)

        # Hora programada
        self.time_programada = QTimeEdit()
        self.time_programada.setTime(QTime.currentTime())
        form_layout.addRow("Hora Programada:", self.time_programada)

        # Fecha real (opcional)
        self.date_real = QDateEdit()
        self.date_real.setDate(QDate.currentDate())
        self.date_real.setCalendarPopup(True)
        self.chk_fecha_real = QCheckBox("Especificar fecha real")
        self.chk_fecha_real.stateChanged.connect(self.on_fecha_real_changed)
        form_layout.addRow(self.chk_fecha_real, self.date_real)
        self.date_real.setEnabled(False)

        # Estado
        self.cmb_estado = QComboBox()
        self.cmb_estado.addItems([
            "PROGRAMADO", "CONFIRMADO", "EN_TRANSITO", "ENTREGADO",
            "CANCELADO", "REPROGRAMADO"
        ])
        self.cmb_estado.setCurrentText("PROGRAMADO")
        form_layout.addRow("Estado:", self.cmb_estado)

        layout.addWidget(group)

    def setup_transporte(self, layout):
        """Configurar sección de transporte."""
        group = QGroupBox("Información de Transporte")
        form_layout = QFormLayout(group)

        # Origen
        self.txt_origen = QLineEdit()
        self.txt_origen.setPlaceholderText("Dirección de origen")
        form_layout.addRow("Origen:", self.txt_origen)

        # Destino
        self.txt_destino = QLineEdit()
        self.txt_destino.setPlaceholderText("Dirección de destino")
        form_layout.addRow("Destino:", self.txt_destino)

        # Proveedor de transporte
        self.cmb_proveedor = QComboBox()
        self.cmb_proveedor.addItems([
            "TRANSPORTES_RAPIDOS", "LOGISTICA_EXPRESS", "CARGA_PESADA",
            "DISTRIBUCION_LOCAL", "TRANSPORTE_ESPECIAL", "OTRO"
        ])
        form_layout.addRow("Proveedor:", self.cmb_proveedor)

        # Vehículo
        self.txt_vehiculo = QLineEdit()
        self.txt_vehiculo.setPlaceholderText("Tipo/modelo de vehículo")
        form_layout.addRow("Vehículo:", self.txt_vehiculo)

        # Conductor
        self.txt_conductor = QLineEdit()
        self.txt_conductor.setPlaceholderText("Nombre del conductor")
        form_layout.addRow("Conductor:", self.txt_conductor)

        # Capacidades
        capacidades_layout = QHBoxLayout()

        self.spin_peso = QDoubleSpinBox()
        self.spin_peso.setRange(0, 50000)
        self.spin_peso.setSuffix(" kg")
        capacidades_layout.addWidget(QLabel("Peso:"))
        capacidades_layout.addWidget(self.spin_peso)

        self.spin_volumen = QDoubleSpinBox()
        self.spin_volumen.setRange(0, 1000)
        self.spin_volumen.setSuffix(" m³")
        capacidades_layout.addWidget(QLabel("Volumen:"))
        capacidades_layout.addWidget(self.spin_volumen)

        form_layout.addRow("Capacidades:", capacidades_layout)

        layout.addWidget(group)

    def setup_costos(self, layout):
        """Configurar sección de costos."""
        group = QGroupBox("Costos")
        form_layout = QFormLayout(group)

        # Costo estimado
        self.spin_costo_estimado = QDoubleSpinBox()
        self.spin_costo_estimado.setRange(0, 1000000)
        self.spin_costo_estimado.setPrefix("$")
        self.spin_costo_estimado.setDecimals(2)
        form_layout.addRow("Costo Estimado:", self.spin_costo_estimado)

        # Costo real
        self.spin_costo_real = QDoubleSpinBox()
        self.spin_costo_real.setRange(0, 1000000)
        self.spin_costo_real.setPrefix("$")
        self.spin_costo_real.setDecimals(2)
        form_layout.addRow("Costo Real:", self.spin_costo_real)

        layout.addWidget(group)

    def setup_observaciones(self, layout):
        """Configurar sección de observaciones."""
        group = QGroupBox("Observaciones")
        layout_observaciones = QVBoxLayout(group)

        self.txt_observaciones = QTextEdit()
        self.txt_observaciones.setPlaceholderText("Observaciones adicionales...")
        self.txt_observaciones.setMaximumHeight(80)
        layout_observaciones.addWidget(self.txt_observaciones)

        layout.addWidget(group)

    def setup_botones(self, layout):
        """Configurar botones del diálogo."""
        botones_layout = QHBoxLayout()

        self.btn_guardar = QPushButton("Guardar")
        self.btn_guardar.clicked.connect(self.guardar_servicio)
        self.btn_guardar.setDefault(True)
        botones_layout.addWidget(self.btn_guardar)

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.clicked.connect(self.reject)
        botones_layout.addWidget(self.btn_cancelar)

        self.btn_preview = QPushButton("Vista Previa")
        self.btn_preview.clicked.connect(self.mostrar_preview)
        botones_layout.addWidget(self.btn_preview)

        layout.addLayout(botones_layout)

    def configurar_validaciones(self):
        """Configurar validaciones de campos."""
        # Configurar validadores si es necesario
        pass

    def on_fecha_real_changed(self, state):
        """Manejar cambio en checkbox de fecha real."""
        self.date_real.setEnabled(state == Qt.CheckState.Checked)

    def cargar_datos_servicio(self):
        """Cargar datos del servicio para edición."""
        if not self.servicio_id or not self.controller:
            return

        try:
            # Aquí se cargarían los datos desde el controlador
            # servicio = self.controller.obtener_servicio(self.servicio_id)
            logger.info(f"Cargando datos del servicio {self.servicio_id}")
            # Implementar carga de datos reales

        except Exception as e:
            logger.error(f"Error cargando datos del servicio: {e}")
            show_error(self, "Error", f"Error cargando datos del servicio: {e}")

    def obtener_datos(self) -> Dict[str, Any]:
        """Obtener datos del formulario."""
        datos = {
            'codigo': sanitize_string(self.txt_codigo.text()),
            'descripcion': sanitize_string(self.txt_descripcion.toPlainText()),
            'tipo_servicio': self.cmb_tipo_servicio.currentText(),
            'cliente': sanitize_string(self.txt_cliente.text()),
            'fecha_programada': self.date_programada.date().toString("yyyy-MM-dd"),
            'hora_programada': self.time_programada.time().toString("HH:mm"),
            'estado': self.cmb_estado.currentText(),
            'origen': sanitize_string(self.txt_origen.text()),
            'destino': sanitize_string(self.txt_destino.text()),
            'proveedor_transporte': self.cmb_proveedor.currentText(),
            'vehiculo': sanitize_string(self.txt_vehiculo.text()),
            'conductor': sanitize_string(self.txt_conductor.text()),
            'capacidad_peso': self.spin_peso.value(),
            'capacidad_volumen': self.spin_volumen.value(),
            'costo_estimado': self.spin_costo_estimado.value(),
            'costo_real': self.spin_costo_real.value(),
            'observaciones': sanitize_string(self.txt_observaciones.toPlainText()),
            'fecha_creacion': datetime.now().isoformat(),
            'activo': True
        }

        # Agregar fecha real si está especificada
        if self.chk_fecha_real.isChecked():
            datos['fecha_real'] = self.date_real.date().toString("yyyy-MM-dd")

        return datos

    def validar_datos(self) -> bool:
        """Validar datos del formulario."""
        if not self.txt_descripcion.toPlainText().strip():
            show_error(self, self.MSG_VALIDACION, "La descripción es obligatoria")
            return False

        if not self.txt_origen.text().strip():
            show_error(self, self.MSG_VALIDACION, "El origen es obligatorio")
            return False

        if not self.txt_destino.text().strip():
            show_error(self, self.MSG_VALIDACION, "El destino es obligatorio")
            return False

        return True

    def guardar_servicio(self):
        """Guardar el servicio."""
        if not self.validar_datos():
            return

        try:
            datos = self.obtener_datos()

            if self.es_edicion:
                self._actualizar_servicio_existente(datos)
            else:
                self._crear_nuevo_servicio(datos)

        except Exception as e:
            logger.error(f"Error guardando servicio: {e}")
            show_error(self, self.MSG_ERROR, f"Error guardando servicio: {e}")

    def _actualizar_servicio_existente(self, datos: Dict[str, Any]):
        """Actualizar un servicio existente."""
        if not self.controller or not hasattr(self.controller, 'actualizar_servicio_transporte'):
            show_error(self, self.MSG_ERROR, "Controlador no disponible para actualizar")
            return

        exito = self.controller.actualizar_servicio_transporte(self.servicio_id, datos)
        if exito:
            show_success(self, self.MSG_EXITO, "Servicio actualizado correctamente")
            self.servicio_guardado.emit(datos)
            self.accept()
        else:
            show_error(self, self.MSG_ERROR, "Error actualizando el servicio")

    def _crear_nuevo_servicio(self, datos: Dict[str, Any]):
        """Crear un nuevo servicio."""
        if self.controller and hasattr(self.controller, 'crear_servicio_transporte'):
            servicio_id = self.controller.crear_servicio_transporte(datos)
            if servicio_id:
                show_success(self, self.MSG_EXITO, f"Servicio creado correctamente (ID: {servicio_id})")
                datos['id'] = servicio_id
                self.servicio_guardado.emit(datos)
                self.accept()
            else:
                show_error(self, self.MSG_ERROR, "Error creando el servicio")
        else:
            # Modo sin controlador - solo emitir señal
            self.servicio_guardado.emit(datos)
            self.accept()

    def mostrar_preview(self):
        """Mostrar vista previa del servicio."""
        if not self.validar_datos():
            return

        datos = self.obtener_datos()

        # Crear diálogo de preview
        preview_dialog = DialogoPreviewServicios(datos, self)
        preview_dialog.exec()


class DialogoPreviewServicios(QDialog):
    """
    Diálogo para previsualizar servicios antes de guardar.
    """

    def __init__(self, datos_servicio: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.datos_servicio = datos_servicio
        self.setup_ui()

    def setup_ui(self):
        """Configurar interfaz de preview."""
        self.setWindowTitle("Vista Previa del Servicio")
        self.setModal(True)
        self.resize(500, 600)

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        # Título
        titulo = QLabel("Vista Previa del Servicio")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo_font = QFont()
        titulo_font.setPointSize(14)
        titulo_font.setBold(True)
        titulo.setFont(titulo_font)
        layout.addWidget(titulo)

        # Contenido
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Información básica
        self.agregar_seccion(scroll_layout, "Información Básica", [
            f"Código: {self.datos_servicio.get('codigo', 'N/A')}",
            f"Tipo: {self.datos_servicio.get('tipo_servicio', 'N/A')}",
            f"Cliente: {self.datos_servicio.get('cliente', 'N/A')}",
            f"Estado: {self.datos_servicio.get('estado', 'N/A')}"
        ])

        # Programación
        self.agregar_seccion(scroll_layout, "Programación", [
            f"Fecha Programada: {self.datos_servicio.get('fecha_programada', 'N/A')}",
            f"Hora Programada: {self.datos_servicio.get('hora_programada', 'N/A')}",
            f"Fecha Real: {self.datos_servicio.get('fecha_real', 'N/A')}"
        ])

        # Transporte
        self.agregar_seccion(scroll_layout, "Transporte", [
            f"Origen: {self.datos_servicio.get('origen', 'N/A')}",
            f"Destino: {self.datos_servicio.get('destino', 'N/A')}",
            f"Proveedor: {self.datos_servicio.get('proveedor_transporte', 'N/A')}",
            f"Vehículo: {self.datos_servicio.get('vehiculo', 'N/A')}",
            f"Conductor: {self.datos_servicio.get('conductor', 'N/A')}"
        ])

        # Costos
        self.agregar_seccion(scroll_layout, "Costos", [
            f"Costo Estimado: ${self.datos_servicio.get('costo_estimado', 0):.2f}",
            f"Costo Real: ${self.datos_servicio.get('costo_real', 0):.2f}"
        ])

        # Observaciones
        if self.datos_servicio.get('observaciones'):
            self.agregar_seccion(scroll_layout, "Observaciones", [
                self.datos_servicio.get('observaciones', '')
            ])

        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        # Botones
        botones_layout = QHBoxLayout()
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.accept)
        botones_layout.addWidget(btn_cerrar)
        layout.addLayout(botones_layout)

    def agregar_seccion(self, layout, titulo: str, lineas: list):
        """Agregar una sección al preview."""
        group = QGroupBox(titulo)
        group_layout = QVBoxLayout(group)

        for linea in lineas:
            label = QLabel(linea)
            label.setWordWrap(True)
            group_layout.addWidget(label)

        layout.addWidget(group)

    def mostrar_preview(self, datos: Dict[str, Any]) -> bool:
        """Mostrar preview de datos (método de compatibilidad)."""
        self.datos_servicio = datos
        # Recrear la interfaz con los nuevos datos
        # Esto es una simplificación - en una implementación real
        # se actualizarían los widgets existentes
        return self.exec() == QDialog.DialogCode.Accepted
