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

import logging

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QTextEdit,
    QDateEdit,
    QDoubleSpinBox,
    QSpinBox,
)

# Importar componentes Rexus
from rexus.ui.components.base_components import (
    RexusButton,
    RexusLabel,
    RexusLineEdit,
    RexusComboBox,
    RexusTable,
    RexusFrame,
    RexusGroupBox,
    RexusLayoutHelper
)

from rexus.ui.standard_components import StandardComponents
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric

from rexus.utils.message_system import show_error, show_warning
from rexus.utils.xss_protection import FormProtector, XSSProtection


class LogisticaView(QWidget):
    """Vista principal del módulo de logística."""

    # Señales
    solicitud_crear_transporte = pyqtSignal(dict)
    solicitud_actualizar_transporte = pyqtSignal(dict)
    solicitud_eliminar_transporte = pyqtSignal(str)
    crear_entrega_solicitada = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.controller = None
        self.form_protector = None
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)


        # Panel de control
        control_panel = self.crear_panel_control()
        layout.addWidget(control_panel)

        # Panel de estadísticas
        stats_panel = self.crear_panel_estadisticas()
        layout.addWidget(stats_panel)

        # Tabla de transportes
        self.tabla_transportes = StandardComponents.create_standard_table()
        self.configurar_tabla()
        layout.addWidget(self.tabla_transportes)

        # Aplicar estilos modernos
        self.configurar_estilos()

        # Inicializar protección XSS
        self.init_xss_protection()

    def crear_titulo(self, layout: QVBoxLayout):
        """Crea el título moderno de la vista."""
        titulo_container = RexusFrame()
        titulo_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                           stop:0 #17a2b8, stop:1 #6c757d);
                border-radius: 8px;
                padding: 6px;
                margin-bottom: 10px;
            }
        """)

        titulo_layout = QHBoxLayout(titulo_container)

        # Título principal
        title_label = RexusLabel("🚚 Gestión de Logística")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: white;
                background: transparent;
                padding: 0;
                margin: 0;
            }
        """)
        titulo_layout.addWidget(title_label)

        # Botón de configuración
        self.btn_configuracion = RexusButton("⚙️ Configuración")
        self.btn_configuracion.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: rgba(255, 255, 255, 0.1);
                color: rgba(255, 255, 255, 0.5);
                border-color: rgba(255, 255, 255, 0.2);
            }
        """)
        self.btn_configuracion.setToolTip("⚙️ Configuración del módulo de logística")
        titulo_layout.addWidget(self.btn_configuracion)

        layout.addWidget(titulo_container)

    def init_xss_protection(self):
        """Inicializa la protección XSS para los campos del formulario."""
        try:
            self.form_protector = FormProtector()

            # Proteger campos si existen
            if hasattr(self, "input_busqueda"):
                self.form_protector.protect_field(self.input_busqueda, "busqueda")
            if hasattr(self, "input_destino"):
                self.form_protector.protect_field(self.input_destino, "destino")
            if hasattr(self, "input_conductor"):
                self.form_protector.protect_field(self.input_conductor, "conductor")

        except Exception as e:
            logging.error(f"Error inicializando protección XSS: {e}")

    def crear_panel_control(self):
        """Crea el panel de control superior con botones modernos."""
        panel = RexusGroupBox("🎛️ Panel de Control")
        panel.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #17a2b8;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #17a2b8;
            }
        """)

        layout = QHBoxLayout(panel)

        # Botón Nuevo Transporte
        self.btn_nuevo_transporte = RexusButton("➕ Nuevo Transporte")
        self.btn_nuevo_transporte.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 14px;
                min-width: 140px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
            QPushButton:disabled {
                background-color: #adb5bd;
                color: #6c757d;
            }
        """)
        self.btn_nuevo_transporte.setToolTip("➕ Crear un nuevo transporte en el sistema")
        self.btn_nuevo_transporte.clicked.connect(self.nuevo_transporte)
        layout.addWidget(self.btn_nuevo_transporte)

        # Campo de búsqueda
        self.input_busqueda = RexusLineEdit()
        self.input_busqueda.setPlaceholderText("🔍 Buscar por destino, conductor o placa...")
        self.input_busqueda.setToolTip("🔍 Buscar transportes por destino, conductor o placa del vehículo")
        self.input_busqueda.setStyleSheet("""
            QLineEdit {
                border: 2px solid #ced4da;
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 14px;
                min-width: 200px;
            }
            QLineEdit:focus {
                border-color: #17a2b8;
            }
        """)
        self.input_busqueda.returnPressed.connect(self.buscar_transportes)
        layout.addWidget(self.input_busqueda)

        # Filtro de estado
        self.combo_estado = RexusComboBox()
        self.combo_estado.addItems([
            "🚚 Todos los estados",
            "⏳ PENDIENTE",
            "🚛 EN_TRANSITO",
            "[CHECK] ENTREGADO",
            "[ERROR] CANCELADO"
        ])
        self.combo_estado.setToolTip("[CHART] Filtrar transportes por estado")
        self.combo_estado.setStyleSheet("""
            QComboBox {
                border: 2px solid #ced4da;
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 14px;
                min-width: 160px;
            }
            QComboBox:focus {
                border-color: #17a2b8;
            }
        """)
        self.combo_estado.currentTextChanged.connect(self.buscar_transportes)
        layout.addWidget(self.combo_estado)

        # Botón buscar
        self.btn_buscar = RexusButton("🔍 Buscar")
        self.btn_buscar.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #0069d9;
            }
            QPushButton:disabled {
                background-color: #adb5bd;
                color: #6c757d;
            }
        """)
        self.btn_buscar.setToolTip("🔍 Ejecutar búsqueda con filtros actuales")
        self.btn_buscar.clicked.connect(self.buscar_transportes)
        layout.addWidget(self.btn_buscar)

        # Botón actualizar
        self.btn_actualizar = RexusButton("🔄 Actualizar")
        self.btn_actualizar.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #adb5bd;
                color: #6c757d;
            }
        """)
        self.btn_actualizar.setToolTip("🔄 Actualizar lista completa de transportes")
        self.btn_actualizar.clicked.connect(self.actualizar_datos)
        layout.addWidget(self.btn_actualizar)

        # Separador y botones de acción
        layout.addStretch()
        
        # Botón editar
        self.btn_editar = RexusButton("✏️ Editar")
        self.btn_editar.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: #212529;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #ffcd39;
            }
            QPushButton:disabled {
                background-color: #adb5bd;
                color: #6c757d;
            }
        """)
        self.btn_editar.setToolTip("✏️ Editar transporte seleccionado")
        self.btn_editar.setEnabled(False)
        layout.addWidget(self.btn_editar)

        # Botón eliminar
        self.btn_eliminar = RexusButton("🗑️ Eliminar")
        self.btn_eliminar.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 16px;
                font-weight: bold;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:disabled {
                background-color: #adb5bd;
                color: #6c757d;
            }
        """)
        self.btn_eliminar.setToolTip("🗑️ Eliminar transporte seleccionado")
        self.btn_eliminar.setEnabled(False)
        layout.addWidget(self.btn_eliminar)

        return panel

    def crear_panel_estadisticas(self):
        """Crea el panel de estadísticas de logística."""
        panel = RexusGroupBox("[CHART] Estadísticas de Logística")
        panel.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #6c757d;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #6c757d;
            }
        """)

        layout = QHBoxLayout(panel)

        # Total transportes
        self.lbl_total_transportes = self.crear_stat_widget("🚚", "Total Transportes", "0", "#17a2b8")
        layout.addWidget(self.lbl_total_transportes)

        # En tránsito
        self.lbl_en_transito = self.crear_stat_widget("🚛", "En Tránsito", "0", "#ffc107")
        layout.addWidget(self.lbl_en_transito)

        # Entregados
        self.lbl_entregados = self.crear_stat_widget("[CHECK]", "Entregados", "0", "#28a745")
        layout.addWidget(self.lbl_entregados)

        # Pendientes
        self.lbl_pendientes = self.crear_stat_widget("⏳", "Pendientes", "0", "#6c757d")
        layout.addWidget(self.lbl_pendientes)

        return panel

    def crear_stat_widget(self, icono, titulo, valor, color):
        """Crea un widget de estadística individual."""
        widget = RexusFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
            }}
            QFrame:hover {{
                border-color: {color};
                background-color: #f8f9fa;
            }}
        """)
        
        layout = QVBoxLayout(widget)
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Icono y título
        header_layout = QHBoxLayout()
        
        icono_lbl = RexusLabel(icono)
        icono_lbl.setStyleSheet(f"font-size: 18px; color: {color};")
        header_layout.addWidget(icono_lbl)
        
        titulo_lbl = RexusLabel(titulo)
        titulo_lbl.setStyleSheet(f"font-weight: bold; color: {color}; font-size: 12px;")
        header_layout.addWidget(titulo_lbl)
        
        layout.addLayout(header_layout)

        # Valor
        valor_lbl = RexusLabel(valor)
        valor_lbl.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {color};")
        valor_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(valor_lbl)

        # Guardar referencia al label del valor para actualizar
        setattr(widget, 'valor_label', valor_lbl)
        
        return widget

    def configurar_tabla(self):
        """Configura la tabla de transportes con estilos modernos."""
        self.tabla_transportes.setColumnCount(8)
        self.tabla_transportes.setHorizontalHeaderLabels([
            "🆔 ID",
            "📍 Destino", 
            "🚗 Conductor",
            "📅 Fecha",
            "[CHART] Estado",
            "📝 Observaciones",
            "🕰️ Última Actualización",
            "⚡ Acciones"
        ])

        # Configurar tamaños de columnas
        header = self.tabla_transportes.horizontalHeader()
        if header is not None:
            try:
                header.resizeSection(0, 60)   # ID
                header.resizeSection(1, 150)  # Destino
                header.resizeSection(2, 120)  # Conductor
                header.resizeSection(3, 100)  # Fecha
                header.resizeSection(4, 100)  # Estado
                header.resizeSection(5, 150)  # Observaciones
                header.resizeSection(6, 140)  # Última Actualización
                header.setStretchLastSection(True)  # Acciones
            except Exception as e:
                import logging
                logging.warning(f"No se pudo configurar el header de la tabla: {e}")
        try:
            self.form_protector = FormProtector()

            # Proteger campos si existen
            if hasattr(self, "input_busqueda"):
                self.form_protector.protect_field(self.input_busqueda, "busqueda")
            if hasattr(self, "input_destino"):
                self.form_protector.protect_field(self.input_destino, "destino")
            else:
                import logging
                logging.warning("input_destino no existe en LogisticaView")
            if hasattr(self, "input_conductor"):
                self.form_protector.protect_field(self.input_conductor, "conductor")
            else:
                import logging
                logging.warning("input_conductor no existe en LogisticaView")

        except Exception as e:
            import logging
            logging.error(f"Error inicializando protección XSS: {e}")

        # Bloque de estilos de la tabla (asegurar delimitador correcto)
        self.tabla_transportes.setStyleSheet("""
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f1f3f4;
            }
            QTableWidget::item:selected {
                background-color: #e7f3ff;
                color: #0066cc;
            }
            QTableWidget::item:hover {
                background-color: #f8f9fa;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #dee2e6;
                font-weight: bold;
                color: #495057;
            }
        """)
        
        # Conectar señal de selección
        self.tabla_transportes.itemSelectionChanged.connect(self.on_transporte_seleccionado)

    def configurar_estilos(self):
        """Configura los estilos modernos usando FormStyleManager."""
        try:
            from rexus.utils.form_styles import FormStyleManager, setup_form_widget
            
            # Aplicar estilos modernos del FormStyleManager
            setup_form_widget(self, apply_animations=True)
            
            # Estilos específicos del módulo de logística
            self.setStyleSheet("""
                QWidget {
                    font-family: 'Segoe UI', Arial, sans-serif;
                    background-color: #f8f9fa;
                }
                QGroupBox {
                    font-weight: bold;
                    border-radius: 8px;
                    margin-top: 1ex;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
            """)
            
        except ImportError:
            print("[WARNING] FormStyleManager no disponible, usando estilos básicos")
            self.aplicar_estilo_basico()

    def aplicar_estilo_basico(self):
        """Aplica estilos básicos como fallback."""
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #138496;
            }
            QLineEdit, QComboBox {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
            QTableWidget {
                background-color: white;
                gridline-color: #dee2e6;
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
        """)

    def set_loading_state(self, loading: bool):
        """Maneja el estado de carga de la interfaz."""
        # Estados de botones principales
        self.btn_nuevo_transporte.setEnabled(not loading)
        self.btn_buscar.setEnabled(not loading)
        self.btn_actualizar.setEnabled(not loading)
        self.btn_configuracion.setEnabled(not loading)
        
        # Estados de botones de acción
        selected = self.tabla_transportes.currentRow() >= 0
        self.btn_editar.setEnabled(not loading and selected)
        self.btn_eliminar.setEnabled(not loading and selected)
        
        # Cambiar textos durante loading
        if loading:
            self.btn_actualizar.setText("⏳ Actualizando...")
            self.btn_buscar.setText("🔍 Buscando...")
        else:
            self.btn_actualizar.setText("🔄 Actualizar")
            self.btn_buscar.setText("🔍 Buscar")

    def on_transporte_seleccionado(self):
        """Maneja la selección de transportes en la tabla."""
        hay_seleccion = self.tabla_transportes.currentRow() >= 0
        self.btn_editar.setEnabled(hay_seleccion)
        self.btn_eliminar.setEnabled(hay_seleccion)

    def actualizar_estadisticas(self, stats):
        """Actualiza las estadísticas mostradas en el panel."""
        try:
            if hasattr(self.lbl_total_transportes, 'valor_label'):
                self.lbl_total_transportes.valor_label.setText(str(stats.get('total_transportes', 0)))
            elif hasattr(self.lbl_total_transportes, 'setText'):
                self.lbl_total_transportes.setText(str(stats.get('total_transportes', 0)))

            if hasattr(self.lbl_en_transito, 'valor_label'):
                self.lbl_en_transito.valor_label.setText(str(stats.get('en_transito', 0)))
            elif hasattr(self.lbl_en_transito, 'setText'):
                self.lbl_en_transito.setText(str(stats.get('en_transito', 0)))

            if hasattr(self.lbl_entregados, 'valor_label'):
                self.lbl_entregados.valor_label.setText(str(stats.get('entregados', 0)))
            elif hasattr(self.lbl_entregados, 'setText'):
                self.lbl_entregados.setText(str(stats.get('entregados', 0)))

            if hasattr(self.lbl_pendientes, 'valor_label'):
                self.lbl_pendientes.valor_label.setText(str(stats.get('pendientes', 0)))
            elif hasattr(self.lbl_pendientes, 'setText'):
                self.lbl_pendientes.setText(str(stats.get('pendientes', 0)))

        except Exception as e:
            show_error(self, message=f"Error actualizando estadísticas: {e}")

    def nuevo_transporte(self):
        """Abre el diálogo para crear un nuevo transporte."""
        dialogo = DialogoTransporte(self)
        
        if dialogo.exec() == dialogo.DialogCode.Accepted:
            if dialogo.validar_datos():
                datos = dialogo.obtener_datos()
                
                if self.controller:
                    try:
                        exito = self.controller.crear_transporte(datos)
                        if exito:
                            from rexus.utils.message_system import show_success
                            show_success(self, "Éxito", "Transporte creado exitosamente.")
                            self.actualizar_datos()
                        else:
                            show_error(self, "Error", "No se pudo crear el transporte.")
                    except Exception as e:
                        show_error(self, "Error", f"Error al crear transporte: {str(e)}")
                else:
                    show_warning(self, "Advertencia", "No hay controlador disponible.")

    def buscar_transportes(self):
        """Busca transportes según los criterios especificados."""
        if self.controller:
            filtros = {
                "busqueda": self.input_busqueda.text(),
                "estado": self.combo_estado.currentText()
                if self.combo_estado.currentText() != "Todos"
                else "",
            }
            self.controller.buscar_transportes(filtros)

    def actualizar_datos(self):
        """Actualiza los datos de la tabla."""
        if self.controller:
            self.controller.cargar_transportes()

    def cargar_transportes_en_tabla(self, transportes):
        """Carga los transportes en la tabla."""
        self.tabla_transportes.setRowCount(len(transportes))

        for row, transporte in enumerate(transportes):
            self.tabla_transportes.setItem(
                row, 0, QTableWidgetItem(str(transporte.get("id", "")))
            )
            self.tabla_transportes.setItem(
                row, 1, QTableWidgetItem(str(transporte.get("destino", "")))
            )
            self.tabla_transportes.setItem(
                row, 2, QTableWidgetItem(str(transporte.get("conductor", "")))
            )
            self.tabla_transportes.setItem(
                row, 3, QTableWidgetItem(str(transporte.get("fecha", "")))
            )
            self.tabla_transportes.setItem(
                row, 4, QTableWidgetItem(str(transporte.get("estado", "")))
            )
            self.tabla_transportes.setItem(
                row, 5, QTableWidgetItem(str(transporte.get("observaciones", "")))
            )

            # Botón de acciones
            btn_editar = RexusButton("Editar")
            btn_editar.setStyleSheet("background-color: #ffc107; color: #212529;")
            self.tabla_transportes.setCellWidget(row, 6, btn_editar)

    def obtener_datos_seguros(self) -> dict:
        """Obtiene datos del formulario con sanitización XSS."""
        if hasattr(self, "form_protector") and self.form_protector:
            return self.form_protector.get_sanitized_data()
        else:
            # Fallback manual
            datos = {}
            if hasattr(self, "input_busqueda"):
                datos["busqueda"] = XSSProtection.sanitize_text(
                    self.input_busqueda.text()
                )
            return datos

    def set_controller(self, controller):
        """Establece el controlador para la vista."""
        self.controller = controller


class DialogoTransporte(QDialog):
    """Diálogo para crear/editar transportes."""
    
    def __init__(self, parent=None, transporte=None):
        super().__init__(parent)
        self.transporte = transporte
        self.init_ui()
        
        if transporte:
            self.cargar_datos(transporte)
    
    def init_ui(self):
        """Inicializa la interfaz del diálogo."""
        self.setWindowTitle("Nuevo Transporte" if not self.transporte else "Editar Transporte")
        self.setModal(True)
        self.resize(500, 600)
        
        layout = QVBoxLayout(self)
        
        # Título
        titulo = RexusLabel("🚚 " + ("Nuevo Transporte" if not self.transporte else "Editar Transporte"))
        titulo.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: white;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #17a2b8, stop:1 #6c757d);
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
            }
        """)
        layout.addWidget(titulo)
        
        # Formulario principal
        form_layout = QFormLayout()
        
        # Información básica del transporte
        self.input_codigo = RexusLineEdit()
        self.input_codigo.setPlaceholderText("Ej: LOG-2024-001")
        form_layout.addRow("📋 Código:", self.input_codigo)
        
        self.input_destino = RexusLineEdit()
        self.input_destino.setPlaceholderText("Destino de entrega")
        form_layout.addRow("📍 Destino:", self.input_destino)
        
        self.input_origen = RexusLineEdit()
        self.input_origen.setPlaceholderText("Punto de origen")
        form_layout.addRow("🏠 Origen:", self.input_origen)
        
        # Información del vehículo y conductor
        self.input_vehiculo = RexusLineEdit()
        self.input_vehiculo.setPlaceholderText("Placa del vehículo")
        form_layout.addRow("🚛 Vehículo:", self.input_vehiculo)
        
        self.input_conductor = RexusLineEdit()
        self.input_conductor.setPlaceholderText("Nombre del conductor")
        form_layout.addRow("👨‍💼 Conductor:", self.input_conductor)
        
        self.input_telefono = RexusLineEdit()
        self.input_telefono.setPlaceholderText("Teléfono del conductor")
        form_layout.addRow("📱 Teléfono:", self.input_telefono)
        
        # Fechas y tiempos
        from PyQt6.QtCore import QDate
        self.date_salida = QDateEdit()
        self.date_salida.setDate(QDate.currentDate())
        self.date_salida.setCalendarPopup(True)
        form_layout.addRow("📅 Fecha Salida:", self.date_salida)
        
        self.date_llegada_estimada = QDateEdit()
        self.date_llegada_estimada.setDate(QDate.currentDate().addDays(1))
        self.date_llegada_estimada.setCalendarPopup(True)
        form_layout.addRow("📅 Llegada Estimada:", self.date_llegada_estimada)
        
        # Información de carga
        self.input_peso = QDoubleSpinBox()
        self.input_peso.setRange(0.0, 99999.99)
        self.input_peso.setSuffix(" kg")
        self.input_peso.setDecimals(2)
        form_layout.addRow("⚖️ Peso:", self.input_peso)
        
        self.input_volumen = QDoubleSpinBox()
        self.input_volumen.setRange(0.0, 9999.99)
        self.input_volumen.setSuffix(" m³")
        self.input_volumen.setDecimals(2)
        form_layout.addRow("📦 Volumen:", self.input_volumen)
        
        # Estado y prioridad
        self.combo_estado = RexusComboBox()
        self.combo_estado.addItems(["PENDIENTE", "EN_TRANSITO", "ENTREGADO", "CANCELADO"])
        form_layout.addRow("[CHART] Estado:", self.combo_estado)
        
        self.combo_prioridad = RexusComboBox()
        self.combo_prioridad.addItems(["BAJA", "NORMAL", "ALTA", "URGENTE"])
        self.combo_prioridad.setCurrentText("NORMAL")
        form_layout.addRow("⚡ Prioridad:", self.combo_prioridad)
        
        # Costos
        self.input_costo_transporte = QDoubleSpinBox()
        self.input_costo_transporte.setRange(0.0, 999999.99)
        self.input_costo_transporte.setPrefix("$ ")
        self.input_costo_transporte.setDecimals(2)
        form_layout.addRow("💰 Costo Transporte:", self.input_costo_transporte)
        
        # Observaciones
        self.input_observaciones = QTextEdit()
        self.input_observaciones.setPlaceholderText("Observaciones adicionales del transporte")
        self.input_observaciones.setMaximumHeight(80)
        form_layout.addRow("📝 Observaciones:", self.input_observaciones)
        
        layout.addLayout(form_layout)
        
        # Botones
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Aplicar estilo
        self.aplicar_estilo()
    
    def aplicar_estilo(self):
        """Aplica estilo al diálogo."""
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {
                padding: 8px;
                border: 2px solid #ced4da;
                border-radius: 4px;
                background-color: white;
                font-size: 13px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {
                border-color: #17a2b8;
            }
            QPushButton {
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 13px;
            }
            QFormLayout QLabel {
                font-weight: bold;
                color: #495057;
            }
        """)
    
    def cargar_datos(self, transporte):
        """Carga los datos de un transporte existente."""
        self.input_codigo.setText(transporte.get("codigo", ""))
        self.input_destino.setText(transporte.get("destino", ""))
        self.input_origen.setText(transporte.get("origen", ""))
        self.input_vehiculo.setText(transporte.get("vehiculo", ""))
        self.input_conductor.setText(transporte.get("conductor", ""))
        self.input_telefono.setText(transporte.get("telefono", ""))
        self.input_peso.setValue(transporte.get("peso", 0.0))
        self.input_volumen.setValue(transporte.get("volumen", 0.0))
        self.input_costo_transporte.setValue(transporte.get("costo_transporte", 0.0))
        self.input_observaciones.setPlainText(transporte.get("observaciones", ""))
        
        # Cargar combos
        estado = transporte.get("estado", "PENDIENTE")
        index = self.combo_estado.findText(estado)
        if index >= 0:
            self.combo_estado.setCurrentIndex(index)
            
        prioridad = transporte.get("prioridad", "NORMAL")
        index = self.combo_prioridad.findText(prioridad)
        if index >= 0:
            self.combo_prioridad.setCurrentIndex(index)
    
    def obtener_datos(self):
        """Obtiene los datos del formulario."""
        return {
            "codigo": self.input_codigo.text().strip(),
            "destino": self.input_destino.text().strip(),
            "origen": self.input_origen.text().strip(),
            "vehiculo": self.input_vehiculo.text().strip(),
            "conductor": self.input_conductor.text().strip(),
            "telefono": self.input_telefono.text().strip(),
            "fecha_salida": self.date_salida.date().toString("yyyy-MM-dd"),
            "fecha_llegada_estimada": self.date_llegada_estimada.date().toString("yyyy-MM-dd"),
            "peso": self.input_peso.value(),
            "volumen": self.input_volumen.value(),
            "estado": self.combo_estado.currentText(),
            "prioridad": self.combo_prioridad.currentText(),
            "costo_transporte": self.input_costo_transporte.value(),
            "observaciones": self.input_observaciones.toPlainText().strip()
        }
    
    def validar_datos(self):
        """Valida los datos del formulario."""
        datos = self.obtener_datos()
        
        if not datos["codigo"]:
            show_error(self, "Error de Validación", "El código es obligatorio.")
            return False
        
        if not datos["destino"]:
            show_error(self, "Error de Validación", "El destino es obligatorio.")
            return False
        
        if not datos["origen"]:
            show_error(self, "Error de Validación", "El origen es obligatorio.")
            return False
        
        if not datos["conductor"]:
            show_error(self, "Error de Validación", "El conductor es obligatorio.")
            return False
        
        if not datos["vehiculo"]:
            show_error(self, "Error de Validación", "El vehículo (placa) es obligatorio.")
            return False
        
        # Validar fechas
        from PyQt6.QtCore import QDate
        fecha_salida = self.date_salida.date()
        fecha_llegada = self.date_llegada_estimada.date()
        
        if fecha_llegada <= fecha_salida:
            show_error(self, "Error de Validación", "La fecha de llegada debe ser posterior a la fecha de salida.")
            return False
        
        # Validar peso y volumen
        if datos["peso"] <= 0:
            show_error(self, "Error de Validación", "El peso debe ser mayor a 0.")
            return False
        
        if datos["volumen"] <= 0:
            show_error(self, "Error de Validación", "El volumen debe ser mayor a 0.")
            return False
        
        return True
