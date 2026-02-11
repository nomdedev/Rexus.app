"""
MIT License

Copyright (c) 2024 Rexus.app

Modulo de Logistica con Sistema de Pestañas
Vista principal con pestañas para tabla, estadísticas, servicios y mapa
"""

import logging
import hashlib
import tempfile
from typing import Dict, List

from PyQt6.QtCore import QUrl, Qt, pyqtSignal

try:
    import folium
    import pandas as pd
except ImportError:
    folium = None  # type: ignore
    pd = None  # type: ignore

from PyQt6.QtWidgets import (
    QComboBox, QDialog, QFrame, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget, QTabWidget, QGridLayout,
    QProgressBar, QScrollArea, QSplitter
)

# Importar componentes Rexus
from rexus.ui.components.base_components import (
    RexusButton, RexusLineEdit, RexusComboBox,
    RexusGroupBox
)

from rexus.ui.standard_components import StandardComponents
from rexus.utils.export_manager import ModuleExportMixin

# Importar el diálogo de transporte
from rexus.modules.logistica.dialogo_transporte import DialogoNuevoTransporte

# Importar constantes
from rexus.modules.logistica.constants import LogisticaConstants

# Constantes para literales duplicados
class LogisticaConstants:
    # Mensajes de estado
    TABLA_NO_DISPONIBLE = "Tabla de transportes no disponible"
    ESTADO_TRANSITO = "En tránsito"
    ETIQUETA_ESTADO = "Estado:"
    VALIDACION = "Validación"

    # Ubicaciones
    ALMACEN_CENTRAL = "Almacén Central"
    SUCURSAL_NORTE = "Sucursal Norte"
    DEPOSITO_SUR = "Depósito Sur"
    CENTRO_DISTRIBUCION = "Centro Distribución"

    # Direcciones
    DIRECCION_ALMACEN_CENTRAL = "Calle 7 entre 47 y 48, La Plata"
    DIRECCION_SUCURSAL_NORTE = "Av. 13 y 44, La Plata"
    DIRECCION_DEPOSITO_SUR = "Calle 120 y 610, La Plata"
    DIRECCION_CENTRO = "Av. 1 y 60, La Plata"

    # Ciudades
    CIUDAD_BUENOS_AIRES = "Buenos Aires"
    CIUDAD_LA_PLATA = "La Plata"

    # Archivos
    EXTENSION_HTML = ".html"

    # Botones
    BOTON_EDITAR = "✏️ Editar"

    # UI Constants
    MIN_WEBVIEW_HEIGHT = 400
    DIALOG_MIN_WIDTH = 400
    FONT_SIZE_SMALL = "10px"
    PADDING_SMALL = "4px"

    # Estilos
    TITLE_LABEL_STYLE = "font-size: 11px; font-weight: 500; color: #2c3e50;"
    CARD_STYLE = """
        QWidget {
            background-color: white;
            border: 1px solid #e1e4e8;
            border-radius: 6px;
            padding: 8px;
        }
        QWidget:hover {
            border-color: #3498db;
        }
    """


class LogisticaView(QWidget, ModuleExportMixin):
    # Señales para comunicación con el controlador
    solicitud_actualizar_estadisticas = pyqtSignal()
    solicitud_actualizar_transporte = pyqtSignal(dict)
    solicitud_eliminar_transporte = pyqtSignal(str)

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        ModuleExportMixin.__init__(self)
        self.controller = None
        self.setup_ui()
        self.cargar_datos_ejemplo()
        self.aplicar_estilo_botones_compactos()

    def setup_ui(self) -> None:
        """Configura la interfaz principal con pestañas mejoradas."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(5)

        # Widget de pestañas con mejor organización
        self.tab_widget = QTabWidget()
        self.configurar_tabs()

        # Crear pestañas con orden optimizado
        self.crear_pestana_tabla()
        self.crear_pestana_estadisticas()
        self.crear_pestana_servicios()
        self.crear_pestana_mapa()

        layout.addWidget(self.tab_widget)

    def aplicar_estilo_botones_compactos(self) -> None:
        """Aplica estilo ultra compacto a todos los botones del módulo."""
        estilo_compacto = """
            QPushButton {
                padding: 2px 8px;
                font-size: 10px;
                font-weight: normal;
                min-height: 18px;
                max-height: 22px;
                border-radius: 3px;
            }
            QPushButton:hover {
                transform: none;
            }
        """

        # Aplicar a todos los botones RexusButton del widget
        for button in self.findChildren(QPushButton):
            if isinstance(button, (RexusButton, QPushButton)):
                current_style = button.styleSheet()
                button.setStyleSheet(f"{current_style}\n{estilo_compacto}")

    # --- STUBS Y MÉTODOS FALTANTES PARA EVITAR ERRORES ---
    def cargar_entregas_en_tabla(self, entregas=None):
        """Carga entregas en la tabla principal."""
        if not hasattr(self, 'tabla_transportes'):
            return

        if entregas is None:
            entregas = []

        self.tabla_transportes.setRowCount(len(entregas))
        for row, entrega in enumerate(entregas):
            self.tabla_transportes.setItem(row, 0,
                QTableWidgetItem(str(entrega.get('id', ''))))
            self.tabla_transportes.setItem(row, 1,
                QTableWidgetItem(str(entrega.get('origen', ''))))
            self.tabla_transportes.setItem(row, 2,
                QTableWidgetItem(str(entrega.get('destino', ''))))
            self.tabla_transportes.setItem(row, 3,
                QTableWidgetItem(str(entrega.get('estado', ''))))
            self.tabla_transportes.setItem(row, 4,
                QTableWidgetItem(str(entrega.get('conductor', ''))))
            self.tabla_transportes.setItem(row, 5,
                QTableWidgetItem(str(entrega.get('fecha', ''))))

    def configurar_tabla_transportes(self):
        """Configura la tabla de transportes."""
        headers = ["ID", "Origen", "Destino", "Estado", "Conductor", "Fecha"]
        self.tabla_transportes.setColumnCount(len(headers))
        self.tabla_transportes.setHorizontalHeaderLabels(headers)

        # Ajustar anchos compactos
        self.tabla_transportes.setColumnWidth(0, 50)
        self.tabla_transportes.setColumnWidth(1, 90)
        self.tabla_transportes.setColumnWidth(2, 90)
        self.tabla_transportes.setColumnWidth(3, 70)
        self.tabla_transportes.setColumnWidth(4, 80)
        self.tabla_transportes.setColumnWidth(5, 70)

        # Desactivar filas alternadas y mejorar estilo
        self.tabla_transportes.setAlternatingRowColors(False)
        self.tabla_transportes.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        # Estilo mejorado con headers visibles
        self.tabla_transportes.setStyleSheet("""
            QTableWidget {
                color: #1e293b;
                background: transparent;
                alternate-background-color: transparent;
                selection-background-color: #3b82f6;
                selection-color: white;
                font-size: 11px;
                font-weight: normal;
                gridline-color: #e2e8f0;
            }
            QTableWidget::item {
                color: #1e293b;
                background: transparent;
                padding: 4px 6px;
                font-size: 11px;
                font-weight: normal;
                border-bottom: 1px solid #e2e8f0;
            }
            QTableWidget::item:selected {
                background: #3b82f6;
                color: white;
            }
            QHeaderView::section {
                color: #1e293b;
                font-weight: bold;
                font-size: 12px;
                border: none;
                border-right: 1px solid #e2e8f0;
                border-bottom: 2px solid #e2e8f0;
                padding: 8px 6px;
                background: transparent;
                text-align: left;
            }
            QHeaderView::section:hover {
                background: #f8fafc;
            }
        """)

    def crear_panel_graficos_mejorado(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("Gráficos (stub)"))
        return widget

    def crear_panel_metricas_compacto(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("Métricas (stub)"))
        return widget

    def crear_panel_resumen_optimizado(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addWidget(QLabel("Resumen (stub)"))
        return widget

    def crear_panel_filtros_servicios_optimizado(self) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.addWidget(QLabel("Filtros servicios (stub)"))
        return widget

    def crear_panel_control_mapa_optimizado(self) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.addWidget(QLabel("Control mapa (stub)"))
        return widget

    def buscar_transportes(self):
        """Realiza búsqueda de transportes con filtros."""
        try:
            # Obtener criterios de búsqueda
            termino = ""
            estado = "Todos"

            # Buscar elementos de búsqueda en la interfaz
            if hasattr(self, 'campo_busqueda'):
                termino = self.campo_busqueda.text().strip()
            if hasattr(self, 'combo_estado'):
                estado = self.combo_estado.currentText()

            # Solicitar búsqueda al controlador
            if self.controller:
                self.controller.buscar_transportes(termino, estado)
            logging.info(f"Buscando transportes: '{termino}' - Estado: {estado}")
        except Exception as e:
            logging.error(f"Error en búsqueda de transportes: {e}")

    def editar_transporte_seleccionado(self):
        """Edita el transporte seleccionado en la tabla."""
        try:
            if not hasattr(self, 'tabla_transportes'):
                logging.warning(LogisticaConstants.TABLA_NO_DISPONIBLE)
                return

            current_row = self.tabla_transportes.currentRow()
            if current_row < 0:
                self.mostrar_mensaje("Selecciona un transporte para editar", "advertencia")
                return

            # Obtener ID del transporte seleccionado
            transporte_id = self.tabla_transportes.item(current_row, 0).text()

            # Abrir diálogo de edición
            dialog = DialogoNuevoTransporte(self, transporte_id)
            if dialog.exec() == dialog.DialogCode.Accepted:
                # Actualizar datos
                datos = dialog.obtener_datos()
                if self.controller:
                    self.controller.actualizar_transporte(datos)

        except Exception as e:
            self.mostrar_error(f"Error al editar transporte: {str(e)}")

    def eliminar_transporte_seleccionado(self):
        """Elimina el transporte seleccionado."""
        try:
            if not hasattr(self, 'tabla_transportes'):
                logging.warning(LogisticaConstants.TABLA_NO_DISPONIBLE)
                return

            current_row = self.tabla_transportes.currentRow()
            if current_row < 0:
                self.mostrar_mensaje("Selecciona un transporte para eliminar", "advertencia")
                return

            # Obtener datos del transporte
            transporte_id = self.tabla_transportes.item(current_row, 0).text()
            origen = self.tabla_transportes.item(current_row, 1).text()
            destino = self.tabla_transportes.item(current_row, 2).text()

            # Confirmar eliminación
            if self.confirmar_accion(f"¿Eliminar transporte de {origen} a {destino}?", "Confirmar Eliminación"):
                if self.controller:
                    self.controller.eliminar_transporte(transporte_id)

        except Exception as e:
            self.mostrar_error(f"Error al eliminar transporte: {str(e)}")

    def exportar_a_excel(self):
        """Exporta los datos de transportes a Excel."""
        try:
            if not hasattr(self, 'tabla_transportes'):
                logging.warning(LogisticaConstants.TABLA_NO_DISPONIBLE)
                return

            from PyQt6.QtWidgets import QFileDialog
            import csv
            from datetime import datetime

            # Seleccionar archivo de destino
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "Exportar Transportes",
                f"transportes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV files (*.csv);;All files (*.*)"
            )

            if not filename:
                return

            # Exportar datos
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)

                # Escribir encabezados
                headers = []
                for col in range(self.tabla_transportes.columnCount()):
                    headers.append(self.tabla_transportes.horizontalHeaderItem(col).text())
                writer.writerow(headers)

                # Escribir datos
                for row in range(self.tabla_transportes.rowCount()):
                    row_data = []
                    for col in range(self.tabla_transportes.columnCount()):
                        item = self.tabla_transportes.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)

            self.mostrar_informacion(f"Datos exportados exitosamente a:\n{filename}")
            print(f"[OK] Exportación completada: {filename}")

        except Exception as e:
            self.mostrar_error(f"Error al exportar: {str(e)}")

    def mostrar_dialogo_nuevo_transporte(self):
        """Muestra el diálogo para crear un nuevo transporte."""
        try:
            dialog = DialogoNuevoTransporte(self)
            if dialog.exec() == dialog.DialogCode.Accepted:
                # Obtener datos del diálogo
                datos = dialog.obtener_datos()

                # Enviar al controlador
                if self.controller:
                    self.controller.crear_transporte(datos)
                else:
                    print("[OK] Nuevo transporte creado (simulado):", datos)

        except Exception as e:
            self.mostrar_error(f"Error al crear transporte: {str(e)}")

    def actualizar_estado_botones(self):
        """
        Actualiza el estado de habilitación de los botones según el contexto.
        TODO: Implementar lógica de habilitación/deshabilitación de botones
        basada en selecciones de tabla y permisos de usuario.
        """

    @property
    def combo_tipo_servicio(self):
        return QComboBox()

    @property
    def combo_estado_servicio(self):
        return QComboBox()

    def crear_widget_direcciones_mejorado(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel("Sin direcciones disponibles.")
        label.setStyleSheet(f"color: #888; font-size: {LogisticaConstants.FONT_SIZE_SMALL}; padding: {LogisticaConstants.PADDING_SMALL};")
        layout.addWidget(label)
        return widget

    def _get_webengine_view(self):
        """
        Obtiene QWebEngineView usando el gestor robusto.

        Returns:
            QWebEngineView class o None si no está disponible
        """
        try:
            from rexus.utils.webengine_manager import webengine_manager

            if webengine_manager.is_webengine_available():
                try:
                    from PyQt6.QtWebEngineWidgets import QWebEngineView
                    return QWebEngineView
                except ImportError as e:
                    print(f"[ERROR] Error importando QWebEngineView: {e}")
                    return None
            else:
                status = webengine_manager.get_status_info()
                print(f"[WARNING] QtWebEngine no disponible: {status['fallback_reasons']}")
                return None
        except ImportError:
            return None

    def crear_widget_mapa_mejorado(self) -> QWidget:
        # Si ya existe, reutilizar
        if hasattr(self, 'mapa_widget') and self.mapa_widget is not None:
            return self.mapa_widget

        try:
            webengine_view_class = self._get_webengine_view()

            if folium is not None and webengine_view_class is not None:
                try:
                    m = folium.Map(location=[-34.6037, -58.3816],
                        zoom_start=12,
                        control_scale=True)
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
                    m.save(temp_file.name)
                    temp_file.close()
                    self.mapa_widget = QWidget()
                    layout = QVBoxLayout(self.mapa_widget)
                    webview = webengine_view_class()
                    webview.setUrl(QUrl.fromLocalFile(temp_file.name))
                    layout.addWidget(webview)
                    return self.mapa_widget
                except Exception as e:
                    motivo = f"Error creando el mapa: {str(e)[:50]}..."
            elif folium is None:
                motivo = "folium no está instalado. Instala 'folium' para ver el mapa."
            elif webengine_view_class is None:
                motivo = "QWebEngineView no está disponible. Instala 'PyQt6-WebEngine'."
            else:
                motivo = "Motivo desconocido."
        except Exception as e:
            motivo = f"Error inesperado: {str(e)}"

        # Fallback robusto
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel(f"🗺️ Mapa no disponible\n{motivo}")
        label.setStyleSheet("color: #e67e22; font-size: 11px; padding: 6px;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        return widget

    def cargar_datos_ejemplo(self):
        """Carga datos de ejemplo para desarrollo."""
        # Datos de ejemplo para transportes
        transportes_ejemplo = [
            {'id': '001', 'origen': 'Buenos Aires', 'destino': 'La Plata', 'estado': 'En tránsito', 'conductor': 'Juan Pérez', 'fecha': '2025-08-09'},
            {'id': '002', 'origen': 'La Plata', 'destino': 'Berisso', 'estado': 'Pendiente', 'conductor': 'María González', 'fecha': '2025-08-09'},
            {'id': '003', 'origen': 'Buenos Aires', 'destino': 'San Isidro', 'estado': 'Entregado', 'conductor': 'Carlos Ruiz', 'fecha': '2025-08-08'},
        ]

        if hasattr(self, 'tabla_transportes'):
            self.cargar_transportes(transportes_ejemplo)

    def configurar_tabs(self):
        """Configura el widget de pestañas con diseño moderno y compacto."""
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setTabShape(QTabWidget.TabShape.Rounded)
        self.tab_widget.setUsesScrollButtons(True)
        self.tab_widget.setElideMode(Qt.TextElideMode.ElideRight)

        # Estilos modernos con mejor jerarquía visual - ESTANDARIZADO
        self.tab_widget.setStyleSheet('''
            QTabWidget {
                border: none;
                background: transparent;
            }
            QTabBar::tab {
                background: #f8fafc;
                color: #6b7280;
                border: 1px solid #e5e7eb;
                border-bottom: none;
                min-width: 80px;
                min-height: 24px;
                max-height: 24px;
                padding: 8px 12px;
                font-size: 12px;
                font-weight: 500;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                color: #1f2937;
                border-color: #e5e7eb;
                border-bottom: 3px solid #3b82f6;
                font-weight: 600;
            }
            QTabBar::tab:hover:!selected {
                background: #f3f4f6;
                color: #374151;
            }
            QTabWidget::pane {
                border: 1px solid #e5e7eb;
                border-top: none;
                background: #ffffff;
                border-radius: 0 0 8px 8px;
            }
        ''')

    def crear_pestana_tabla(self):
        """Crea la pestaña de tabla principal con layout optimizado."""
        tab_tabla = QWidget()
        layout = QVBoxLayout(tab_tabla)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        # Panel unificado de control y acciones (optimizado)
        panel_unificado = self.crear_panel_unificado_tabla()
        layout.addWidget(panel_unificado)

        # Divisor visual entre panel y tabla
        divisor = QFrame()
        divisor.setFrameShape(QFrame.Shape.HLine)
        divisor.setFrameShadow(QFrame.Shadow.Sunken)
        divisor.setStyleSheet("QFrame { color: #e1e4e8; margin: 4px 0; }")
        layout.addWidget(divisor)

        # Tabla principal
        self.tabla_transportes = StandardComponents.create_standard_table()
        self.configurar_tabla_transportes()
        layout.addWidget(self.tabla_transportes)

        # Asignar referencia para exportación
        self.tabla_principal = self.tabla_transportes

        # Panel de acciones con botón de exportación
        panel_acciones = QFrame()
        acciones_layout = QHBoxLayout(panel_acciones)

        # Agregar botón de exportación
        self.add_export_button(acciones_layout, "📄 Exportar Logística")

        acciones_layout.addStretch()
        layout.addWidget(panel_acciones)

        self.tab_widget.addTab(tab_tabla, "Transportes")

    def crear_pestana_estadisticas(self):
        """Crea la pestaña de estadísticas con layout optimizado y compacto."""
        tab_stats = QWidget()
        layout = QVBoxLayout(tab_stats)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        # Scroll area optimizada para estadísticas
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        stats_widget = QWidget()
        stats_layout = QVBoxLayout(stats_widget)
        stats_layout.setSpacing(4)
        stats_layout.setContentsMargins(4, 4, 4, 4)

        # Panel de resumen compacto (métricas principales)
        resumen_panel = self.crear_panel_resumen_optimizado()
        stats_layout.addWidget(resumen_panel)

        # Splitter horizontal para mejor uso del espacio
        splitter_stats = QSplitter(Qt.Orientation.Horizontal)
        splitter_stats.setHandleWidth(2)

        # Panel izquierdo: Gráficos mejorados
        graficos_panel = self.crear_panel_graficos_mejorado()
        splitter_stats.addWidget(graficos_panel)

        # Panel derecho: Métricas detalladas
        metricas_panel = self.crear_panel_metricas_compacto()
        splitter_stats.addWidget(metricas_panel)

        # Configurar tamaños del splitter más responsivos
        splitter_stats.setSizes([60, 40])
        splitter_stats.setCollapsible(0, False)
        splitter_stats.setCollapsible(1, True)
        splitter_stats.setStretchFactor(0, 3)
        splitter_stats.setStretchFactor(1, 2)

        stats_layout.addWidget(splitter_stats)
        stats_layout.addStretch()

        scroll.setWidget(stats_widget)
        layout.addWidget(scroll)

        self.tab_widget.addTab(tab_stats, "Estadísticas")

    def crear_pestana_servicios(self):
        """Crea la pestaña de servicios optimizada y compacta."""
        tab_servicios = QWidget()
        layout = QVBoxLayout(tab_servicios)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        # Panel de filtros compacto con altura fija
        filtros_panel = self.crear_panel_filtros_servicios_optimizado()
        layout.addWidget(filtros_panel)

        # Tabla de servicios activos ocupa la mayor parte del espacio
        servicios_activos_widget = self.crear_widget_servicios_activos_con_detalle()
        layout.addWidget(servicios_activos_widget, stretch=1)

        self.tab_widget.addTab(tab_servicios, "[TOOL] Servicios")

    def crear_widget_servicios_activos_con_detalle(self) -> QWidget:
        """Crea el widget de servicios activos con botón Detalle por fila."""
        widget = RexusGroupBox("📋 Servicios Activos")
        layout = QVBoxLayout(widget)
        layout.setSpacing(4)
        layout.setContentsMargins(5, 5, 5, 5)

        # Panel de acciones compacto
        acciones_layout = QHBoxLayout()

        btn_nuevo_servicio = RexusButton("➕ Nuevo")
        btn_nuevo_servicio.setToolTip("Crear nuevo servicio")
        acciones_layout.addWidget(btn_nuevo_servicio)

        btn_editar_servicio = RexusButton(LogisticaConstants.BOTON_EDITAR)
        btn_editar_servicio.setToolTip("Editar servicio seleccionado")
        acciones_layout.addWidget(btn_editar_servicio)

        acciones_layout.addStretch()
        layout.addLayout(acciones_layout)

        # Tabla de servicios con botón Detalle
        from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton
        self.tabla_servicios = QTableWidget(0, 6)
        self.tabla_servicios.setHorizontalHeaderLabels([
            "ID", "Tipo", "Estado", "Cliente", "Prioridad", "Detalle"
        ])
        self.tabla_servicios.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_servicios.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla_servicios.setAlternatingRowColors(False)

        try:
            vh = self.tabla_servicios.verticalHeader()
            if vh and hasattr(vh, 'setVisible'):
                vh.setVisible(False)
        except AttributeError as e:
            print(f"[WARNING] Error configurando header vertical: {e}")

        try:
            hh = self.tabla_servicios.horizontalHeader()
            if hh and hasattr(hh, 'setStretchLastSection'):
                hh.setStretchLastSection(True)
        except AttributeError as e:
            print(f"[WARNING] Error configurando header horizontal: {e}")

        # Mejorar contraste de texto y fondo
        self.tabla_servicios.setStyleSheet("""
            QTableWidget {
                color: #1e293b;
                background: transparent;
                alternate-background-color: transparent;
                selection-background-color: #3b82f6;
                selection-color: white;
                font-size: 11px;
                font-weight: normal;
            }
            QTableWidget::item {
                color: #1e293b;
                background: transparent;
                padding: 3px 6px;
                font-size: 11px;
                font-weight: normal;
                border-bottom: 1px solid #e2e8f0;
            }
            QTableWidget::item:selected {
                background: #3b82f6;
                color: white;
            }
            QHeaderView::section {
                color: #1e293b;
                font-weight: bold;
                font-size: 12px;
                border: none;
                border-right: 1px solid #e2e8f0;
                border-bottom: 2px solid #e2e8f0;
                padding: 8px 6px;
                background: transparent;
                text-align: left;
            }
            QHeaderView::section:hover {
                background: transparent;
            }
        """)
        layout.addWidget(self.tabla_servicios)

        # Ejemplo de datos
        ejemplo_servicios = [
            {"id": 1, "tipo": "Express", "estado": "Activo", "cliente": "ACME S.A.", "prioridad": "Alta"},
            {"id": 2, "tipo": "Estándar", "estado": "Finalizado", "cliente": "Beta Ltda.", "prioridad": "Media"},
            {"id": 3, "tipo": "Económico", "estado": "Pausado", "cliente": "Gamma SRL", "prioridad": "Baja"},
        ]

        self.tabla_servicios.setRowCount(len(ejemplo_servicios))
        for row, servicio in enumerate(ejemplo_servicios):
            self.tabla_servicios.setItem(row, 0, QTableWidgetItem(str(servicio["id"])))
            self.tabla_servicios.setItem(row, 1, QTableWidgetItem(servicio["tipo"]))
            self.tabla_servicios.setItem(row, 2, QTableWidgetItem(servicio["estado"]))
            self.tabla_servicios.setItem(row, 3, QTableWidgetItem(servicio["cliente"]))
            self.tabla_servicios.setItem(row, 4, QTableWidgetItem(servicio["prioridad"]))
            btn_detalle = QPushButton("Detalle")
            btn_detalle.setStyleSheet(
                "background-color: #17a2b8; color: white; font-size: 11px; "
                "border-radius: 4px; padding: 4px 10px;"
            )
            btn_detalle.clicked.connect(lambda checked, s=servicio: self.mostrar_dialogo_detalle_servicio(s))
            self.tabla_servicios.setCellWidget(row, 5, btn_detalle)

        return widget

    def mostrar_dialogo_detalle_servicio(self, servicio):
        """Muestra un diálogo con el detalle del servicio."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Detalle del Servicio #{servicio['id']}")
        dialog.setMinimumWidth(LogisticaConstants.DIALOG_MIN_WIDTH)
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(f"<b>ID:</b> {servicio['id']}"))
        layout.addWidget(QLabel(f"<b>Tipo:</b> {servicio['tipo']}"))
        layout.addWidget(QLabel(f"<b>Estado:</b> {servicio['estado']}"))
        layout.addWidget(QLabel(f"<b>Cliente:</b> {servicio['cliente']}"))
        layout.addWidget(QLabel(f"<b>Prioridad:</b> {servicio['prioridad']}"))
        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(dialog.accept)
        layout.addWidget(btn_cerrar)
        dialog.exec()

    def crear_pestana_mapa(self):
        """Crea la pestaña del mapa optimizada con direcciones."""
        tab_mapa = QWidget()
        layout = QVBoxLayout(tab_mapa)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)

        # Panel de control del mapa compacto
        control_mapa_panel = self.crear_panel_control_mapa_optimizado()
        layout.addWidget(control_mapa_panel)

        # Contenedor principal del mapa con proporciones responsivas
        mapa_container = QSplitter(Qt.Orientation.Horizontal)

        # Panel lateral con direcciones mejorado
        direcciones_widget = self.crear_widget_direcciones_mejorado()
        mapa_container.addWidget(direcciones_widget)

        # Widget del mapa con fallback mejorado
        mapa_widget = self.crear_widget_mapa_mejorado()
        mapa_container.addWidget(mapa_widget)

        # Proporciones optimizadas
        mapa_container.setSizes([280, 720])
        layout.addWidget(mapa_container)

        self.tab_widget.addTab(tab_mapa, "🗺️ Mapa")

    # Panel unificado optimizado para tabla
    def crear_panel_unificado_tabla(self) -> QWidget:
        """Crea panel unificado que combina control y acciones de forma compacta."""
        panel = RexusGroupBox("Control de Transportes y Acciones")
        layout = QVBoxLayout(panel)
        layout.setSpacing(6)

        # Fila superior: Filtros y búsqueda
        fila_filtros = QHBoxLayout()

        # Búsqueda
        self.input_busqueda = RexusLineEdit()
        self.input_busqueda.setPlaceholderText("Buscar transportes...")
        fila_filtros.addWidget(QLabel("Buscar:"))
        fila_filtros.addWidget(self.input_busqueda)

        # Filtro de estado
        self.combo_estado = RexusComboBox()
        self.combo_estado.addItems([
            "Todos", "Pendiente", LogisticaConstants.ESTADO_TRANSITO,
            "Entregado", "Cancelado"
        ])
        fila_filtros.addWidget(QLabel(LogisticaConstants.ETIQUETA_ESTADO))
        fila_filtros.addWidget(self.combo_estado)

        # Botón de búsqueda compacto
        btn_buscar = RexusButton("[SEARCH] Buscar")
        btn_buscar.clicked.connect(self.buscar_transportes)
        btn_buscar.setStyleSheet("""
            QPushButton {
                padding: 4px 12px;
                font-size: 11px;
                min-height: 24px;
                max-height: 28px;
                font-weight: 500;
            }
        """)
        fila_filtros.addWidget(btn_buscar)

        fila_filtros.addStretch()
        layout.addLayout(fila_filtros)

        # Fila inferior: Acciones principales (botones compactos)
        fila_acciones = QHBoxLayout()

        # Botones de acción compactos
        self.btn_nuevo_transporte = RexusButton("🚛 Nuevo")
        self.btn_nuevo_transporte.clicked.connect(self.mostrar_dialogo_nuevo_transporte)
        self.btn_nuevo_transporte.setToolTip("Crear un nuevo registro de transporte")
        self.btn_nuevo_transporte.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-weight: bold;
                padding: 6px 8px;
                border-radius: 4px;
                border: none;
                font-size: 11px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        fila_acciones.addWidget(self.btn_nuevo_transporte)

        self.btn_editar_transporte = RexusButton(LogisticaConstants.BOTON_EDITAR)
        self.btn_editar_transporte.clicked.connect(self.editar_transporte_seleccionado)
        self.btn_editar_transporte.setToolTip("Editar el transporte seleccionado")
        self.btn_editar_transporte.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: #212529;
                font-weight: bold;
                padding: 6px 8px;
                border-radius: 4px;
                border: none;
                font-size: 11px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
            QPushButton:disabled {
                background-color: #f8f9fa;
                color: #6c757d;
            }
        """)
        fila_acciones.addWidget(self.btn_editar_transporte)

        self.btn_eliminar_transporte = RexusButton("🗑️ Eliminar")
        self.btn_eliminar_transporte.clicked.connect(self.eliminar_transporte_seleccionado)
        self.btn_eliminar_transporte.setToolTip("Eliminar el transporte seleccionado")
        self.btn_eliminar_transporte.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                font-weight: bold;
                padding: 6px 8px;
                border-radius: 4px;
                border: none;
                font-size: 11px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:disabled {
                background-color: #f8f9fa;
                color: #6c757d;
            }
        """)
        fila_acciones.addWidget(self.btn_eliminar_transporte)

        fila_acciones.addStretch()

        self.btn_exportar = RexusButton("[CHART] Excel")
        self.btn_exportar.clicked.connect(self.exportar_a_excel)
        self.btn_exportar.setToolTip("Exportar datos a archivo Excel")
        self.btn_exportar.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                font-weight: bold;
                padding: 6px 8px;
                border-radius: 4px;
                border: none;
                font-size: 11px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        fila_acciones.addWidget(self.btn_exportar)

        layout.addLayout(fila_acciones)

        # Conectar eventos de selección para habilitar/deshabilitar botones
        if hasattr(self, 'tabla_transportes'):
            self.tabla_transportes.itemSelectionChanged.connect(self.actualizar_estado_botones)

        return panel

    # Métodos auxiliares
    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error."""
        from rexus.utils.message_system import show_error
        show_error(self, "Error", mensaje)

    def mostrar_informacion(self, mensaje):
        """Muestra un mensaje informativo."""
        from rexus.utils.message_system import show_success
        show_success(self, "Información", mensaje)

    def confirmar_accion(self, mensaje, titulo):
        """Muestra un diálogo de confirmación."""
        from PyQt6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self, titulo, mensaje,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes

    def cargar_transportes(self, transportes: List[Dict]):
        """Carga transportes en la tabla."""
        if not hasattr(self, 'tabla_transportes'):
            return

        self.tabla_transportes.setRowCount(len(transportes))

        for row, transporte in enumerate(transportes):
            self.tabla_transportes.setItem(row, 0,
                QTableWidgetItem(str(transporte.get('id', ''))))
            self.tabla_transportes.setItem(row, 1,
                QTableWidgetItem(str(transporte.get('origen', ''))))
            self.tabla_transportes.setItem(row, 2,
                QTableWidgetItem(str(transporte.get('destino', ''))))
            self.tabla_transportes.setItem(row, 3,
                QTableWidgetItem(str(transporte.get('estado', ''))))
            self.tabla_transportes.setItem(row, 4,
                QTableWidgetItem(str(transporte.get('conductor', ''))))
            self.tabla_transportes.setItem(row, 5,
                QTableWidgetItem(str(transporte.get('fecha', ''))))

    def cargar_servicios(self, servicios: List[Dict]):
        """Carga servicios en la tabla de servicios."""
        if not hasattr(self, 'tabla_servicios'):
            return

        self.tabla_servicios.setRowCount(len(servicios))

        for row, servicio in enumerate(servicios):
            self.tabla_servicios.setItem(row, 0,
                QTableWidgetItem(str(servicio.get('id', ''))))
            self.tabla_servicios.setItem(row, 1,
                QTableWidgetItem(str(servicio.get('tipo', ''))))
            self.tabla_servicios.setItem(row, 2,
                QTableWidgetItem(str(servicio.get('estado', ''))))
            self.tabla_servicios.setItem(row, 3,
                QTableWidgetItem(str(servicio.get('cliente', ''))))
            self.tabla_servicios.setItem(row, 4,
                QTableWidgetItem(str(servicio.get('prioridad', ''))))

    def cargar_direcciones(self, direcciones: List[Dict]):
        """Stub: tabla de direcciones no implementada."""
        pass

    def actualizar_estadisticas(self, stats: Dict):
        """Actualiza las estadísticas mostradas."""
        pass

    def set_controller(self, controller):
        """Establece el controlador."""
        self.controller = controller
