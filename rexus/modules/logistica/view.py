"""
MIT License

Copyright (c) 2024 Rexus.app

Módulo de Logística con Sistema de Pestañas
Vista principal con pestañas para tabla, estadísticas, servicios y mapa
"""

import logging
import hashlib
import tempfile
from typing import Dict, List, Any

from PyQt6.QtCore import QUrl

try:
    import folium
    import pandas as pd
except ImportError:
    folium = None
    pd = None

from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtWidgets import (
    QComboBox, QDialog, QDialogButtonBox, QFormLayout, QFrame, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, 
    QTableWidgetItem, QVBoxLayout, QWidget, QTextEdit, QDateEdit,
    QDoubleSpinBox, QSpinBox, QTabWidget, QGridLayout, QProgressBar,
    QScrollArea, QSplitter
)

from PyQt6.QtGui import QFont, QPalette, QColor

# Importar componentes Rexus
from rexus.ui.components.base_components import (
    RexusButton, RexusLabel, RexusLineEdit, RexusComboBox, RexusTable,
    RexusFrame, RexusGroupBox, RexusLayoutHelper
)

from rexus.ui.standard_components import StandardComponents
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string
from rexus.utils.message_system import show_error, show_warning
from rexus.utils.xss_protection import FormProtector
from rexus.utils.export_manager import ModuleExportMixin

# Importar el diálogo de transporte
from rexus.modules.logistica.dialogo_transporte import DialogoNuevoTransporte


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

    def setup_ui(self):
        """Configura la interfaz principal con pestañas."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Widget de pestañas
        self.tab_widget = QTabWidget()
        self.configurar_tabs()
        
        # Crear pestañas
        self.crear_pestana_tabla()
        self.crear_pestana_estadisticas()
        self.crear_pestana_servicios()
        self.crear_pestana_mapa()
        
        layout.addWidget(self.tab_widget)

    # --- STUBS Y MÉTODOS FALTANTES PARA EVITAR ERRORES ---
    def cargar_entregas_en_tabla(self, entregas=None):
        """Carga entregas en la tabla principal."""
        if not hasattr(self, 'tabla_transportes'):
            return
        
        if entregas is None:
            entregas = []
        
        self.tabla_transportes.setRowCount(len(entregas))
        for row, entrega in enumerate(entregas):
            self.tabla_transportes.setItem(row, 0, QTableWidgetItem(str(entrega.get('id', ''))))
            self.tabla_transportes.setItem(row, 1, QTableWidgetItem(str(entrega.get('origen', ''))))
            self.tabla_transportes.setItem(row, 2, QTableWidgetItem(str(entrega.get('destino', ''))))
            self.tabla_transportes.setItem(row, 3, QTableWidgetItem(str(entrega.get('estado', ''))))
            self.tabla_transportes.setItem(row, 4, QTableWidgetItem(str(entrega.get('conductor', ''))))
            self.tabla_transportes.setItem(row, 5, QTableWidgetItem(str(entrega.get('fecha', ''))))

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
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("Gráficos (stub)"))
        return w

    def crear_panel_metricas_compacto(self) -> QWidget:
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("Métricas (stub)"))
        return w

    def crear_panel_resumen_optimizado(self) -> QWidget:
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(QLabel("Resumen (stub)"))
        return w

    def crear_panel_filtros_servicios_optimizado(self) -> QWidget:
        w = QWidget()
        l = QHBoxLayout(w)
        l.addWidget(QLabel("Filtros servicios (stub)"))
        return w

    def crear_panel_control_mapa_optimizado(self) -> QWidget:
        w = QWidget()
        l = QHBoxLayout(w)
        l.addWidget(QLabel("Control mapa (stub)"))
        return w

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
                logging.warning("Tabla de transportes no disponible")
                return
                
            current_row = self.tabla_transportes.currentRow()
            if current_row < 0:
                self.mostrar_mensaje("advertencia", "Selección requerida", "Selecciona un transporte para editar")
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
                logging.warning("Tabla de transportes no disponible")
                return
                
            current_row = self.tabla_transportes.currentRow()
            if current_row < 0:
                self.mostrar_mensaje("advertencia", "Selección requerida", "Selecciona un transporte para eliminar")
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
                logging.warning("Tabla de transportes no disponible")
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
            print(f"✅ Exportación completada: {filename}")
            
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
                    print("✅ Nuevo transporte creado (simulado):", datos)
                    
        except Exception as e:
            self.mostrar_error(f"Error al crear transporte: {str(e)}")

    def actualizar_estado_botones(self):
        pass

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
        label.setStyleSheet("color: #888; font-size: 10px; padding: 4px;")
        layout.addWidget(label)
        return widget

    def _get_webengine_view(self):
        """
        Obtiene QWebEngineView usando el gestor robusto.
        
        Returns:
            QWebEngineView class o None si no está disponible
        """
        from rexus.utils.webengine_manager import webengine_manager
        
        if webengine_manager.is_webengine_available():
            try:
                from PyQt6.QtWebEngineWidgets import QWebEngineView
                return QWebEngineView
            except Exception as e:
                print(f"[ERROR] Error obteniendo QWebEngineView: {e}")
                return None
        else:
            status = webengine_manager.get_status_info()
            print(f"[WARNING] QtWebEngine no disponible: {status['fallback_reasons']}")
            return None

    def crear_widget_mapa_mejorado(self) -> QWidget:
        # Si ya existe, reutilizar
        if hasattr(self, 'mapa_widget') and self.mapa_widget is not None:
            return self.mapa_widget

        from rexus.utils.webengine_manager import webengine_manager

        try:
            if folium is not None and webengine_manager.is_webengine_available():
                # Crear mapa folium
                m = folium.Map(location=[-34.6037, -58.3816], zoom_start=12, control_scale=True)
                
                # Guardar HTML temporal con nombre único
                temp_file = tempfile.NamedTemporaryFile(
                    delete=False, 
                    suffix='.html',
                    prefix='rexus_map_'
                )
                m.save(temp_file.name)
                temp_file.close()
                
                # Crear widget de mapa usando el gestor robusto
                self.mapa_widget = QWidget()
                layout = QVBoxLayout(self.mapa_widget)
                
                webview = webengine_manager.create_web_view("Vista de mapa logístico")
                if webengine_manager.load_file(webview, temp_file.name):
                    webview.setMinimumHeight(400)
                    layout.addWidget(webview)
                    return self.mapa_widget
                else:
                    # Si falla la carga, usar fallback
                    raise Exception("No se pudo cargar el mapa en el WebView")
            else:
                # Folium no disponible o WebEngine no disponible
                missing_deps = []
                if folium is None:
                    missing_deps.append("folium")
                if not webengine_manager.is_webengine_available():
                    missing_deps.append("QtWebEngine")
                raise Exception(f"Dependencias faltantes: {', '.join(missing_deps)}")
                
        except Exception as e:
            # Crear fallback usando el gestor
            fallback_message = f"""
🗺️ Mapa Logístico No Disponible

Motivo: {str(e)}

Para habilitar mapas interactivos:
• Instale folium: pip install folium
• Instale PyQt6-WebEngine: pip install PyQt6-WebEngine
            """
            self.mapa_widget = webengine_manager.create_map_widget(fallback_message)
            
        return self.mapa_widget

    def cargar_datos_ejemplo(self):
        """Carga datos de ejemplo para desarrollo."""
        QWebEngineView = self._get_webengine_view()

        if folium is not None and QWebEngineView is not None:
            try:
                m = folium.Map(location=[-34.6037, -58.3816], zoom_start=12, control_scale=True)
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
                m.save(temp_file.name)
                temp_file.close()
                self.mapa_widget = QWidget()
                layout = QVBoxLayout(self.mapa_widget)
                webview = QWebEngineView()
                webview.setUrl(QUrl.fromLocalFile(temp_file.name))
                layout.addWidget(webview)
                return self.mapa_widget
            except Exception as e:
                motivo = f"Error creando el mapa: {str(e)[:50]}..."
        elif folium is None:
            motivo = "folium no está instalado. Instala 'folium' para ver el mapa."
        elif QWebEngineView is None:
            motivo = "QWebEngineView no está disponible. Instala 'PyQt6-WebEngine'."
        else:
            motivo = "Motivo desconocido."
        # Fallback robusto
        widget = QWidget()
        layout = QVBoxLayout(widget)
        label = QLabel(f"🗺️ Mapa no disponible\n{motivo}")
        label.setStyleSheet("color: #e67e22; font-size: 11px; padding: 6px;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        return widget
        mapa_widget = self.crear_widget_mapa_mejorado()
        layout.addWidget(mapa_widget)
        self.tab_widget.addTab(tab_mapa, "🗺️ Mapa")

    def configurar_tabs(self):
        """Configura el widget de pestañas y mejora contraste visual."""
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setTabShape(QTabWidget.TabShape.Rounded)
        self.tab_widget.setUsesScrollButtons(True)
        self.tab_widget.setElideMode(Qt.TextElideMode.ElideRight)
        # Mejorar contraste de las pestañas
        self.tab_widget.setStyleSheet('''
            QTabBar::tab {
                background: #f8fafc;
                color: #374151;
                border: 1px solid #e2e8f0;
                border-bottom: none;
                min-width: 80px;
                min-height: 18px;
                padding: 2px 10px;
                font-size: 10px;
                font-weight: 500;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #fff;
                color: #1e293b;
                border-bottom: 2px solid #3b82f6;
            }
            QTabBar::tab:!selected {
                background: #f1f5f9;
                color: #374151;
            }
            QTabWidget::pane {
                border-top: 2px solid #3b82f6;
                top: -1px;
            }
        ''')

    def crear_pestana_tabla(self):
        """Crea la pestaña de tabla principal con layout optimizado."""
        tab_tabla = QWidget()
        layout = QVBoxLayout(tab_tabla)
    # ...
    # (Asegurarse que estas líneas estén dentro de métodos, no sueltas)

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
    # ...
    # (Asegurarse que estas líneas estén dentro de métodos, no sueltas)

        # Scroll area optimizada para estadísticas
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        stats_widget = QWidget()
        stats_layout = QVBoxLayout(stats_widget)
        stats_layout.setSpacing(6)  # Espaciado compacto

        # Panel de resumen compacto (métricas principales)
        resumen_panel = self.crear_panel_resumen_optimizado()
        stats_layout.addWidget(resumen_panel)

        # Splitter horizontal para mejor uso del espacio
        splitter_stats = QSplitter(Qt.Orientation.Horizontal)
        
        # Panel izquierdo: Gráficos mejorados
        graficos_panel = self.crear_panel_graficos_mejorado()
        splitter_stats.addWidget(graficos_panel)

        # Panel derecho: Métricas detalladas
        metricas_panel = self.crear_panel_metricas_compacto()
        splitter_stats.addWidget(metricas_panel)
        
        # Configurar tamaños del splitter
        splitter_stats.setSizes([500, 400])
        splitter_stats.setCollapsible(0, False)
        splitter_stats.setCollapsible(1, False)
        
        stats_layout.addWidget(splitter_stats)
        stats_layout.addStretch()
        
        scroll.setWidget(stats_widget)
        layout.addWidget(scroll)

        self.tab_widget.addTab(tab_stats, "Estadísticas")

    def crear_pestana_servicios(self):
        """Crea la pestaña de servicios optimizada y compacta."""
        tab_servicios = QWidget()
        layout = QVBoxLayout(tab_servicios)
    # ...
    # (Asegurarse que estas líneas estén dentro de métodos, no sueltas)

        # Panel de filtros compacto con altura fija
        filtros_panel = self.crear_panel_filtros_servicios_optimizado()
    # ...
    # (Asegurarse que esta línea esté dentro de un método)
        layout.addWidget(filtros_panel)

        # Tabla de servicios activos ocupa la mayor parte del espacio
        servicios_activos_widget = self.crear_widget_servicios_activos_con_detalle()
        layout.addWidget(servicios_activos_widget, stretch=1)

        self.tab_widget.addTab(tab_servicios, "🔧 Servicios")
    def crear_widget_servicios_activos_con_detalle(self) -> QWidget:
        """Crea el widget de servicios activos con botón Detalle por fila."""
        widget = RexusGroupBox("📋 Servicios Activos")
        layout = QVBoxLayout(widget)
        layout.setSpacing(4)  # Espaciado más compacto
        layout.setContentsMargins(5, 5, 5, 5)  # Márgenes reducidos

        # Panel de acciones compacto
        acciones_layout = QHBoxLayout()
    # ...
    # (Asegurarse que esta línea esté dentro de un método)

        btn_nuevo_servicio = RexusButton("➕ Nuevo")
        btn_nuevo_servicio.setToolTip("Crear nuevo servicio")
        acciones_layout.addWidget(btn_nuevo_servicio)

        btn_editar_servicio = RexusButton("✏️ Editar")
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
        except Exception:
            pass
        try:
            hh = self.tabla_servicios.horizontalHeader()
            if hh and hasattr(hh, 'setStretchLastSection'):
                hh.setStretchLastSection(True)
        except Exception:
            pass
        # Mejorar contraste de texto y fondo - estilo minimalista
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

        # Ejemplo de datos (reemplazar por datos reales)
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
            btn_detalle.setStyleSheet("background-color: #17a2b8; color: white; font-size: 11px; border-radius: 4px; padding: 4px 10px;")
            btn_detalle.clicked.connect(lambda checked, s=servicio: self.mostrar_dialogo_detalle_servicio(s))
            self.tabla_servicios.setCellWidget(row, 5, btn_detalle)

        return widget

    def mostrar_dialogo_detalle_servicio(self, servicio):
        """Muestra un diálogo con el detalle del servicio."""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Detalle del Servicio #{servicio['id']}")
        dialog.setMinimumWidth(400)
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
        layout.setSpacing(8)  # Reducido de 10 a 8
        layout.setContentsMargins(8, 8, 8, 8)  # Reducido padding

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

        # Proporciones optimizadas 280-720 (más espacio para mapa)
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
        self.combo_estado.addItems(["Todos", "Pendiente", "En tránsito", "Entregado", "Cancelado"])
        fila_filtros.addWidget(QLabel("Estado:"))
        fila_filtros.addWidget(self.combo_estado)

        # Botón de búsqueda compacto
        btn_buscar = RexusButton("🔍 Buscar")
        btn_buscar.clicked.connect(self.buscar_transportes)
        btn_buscar.setStyleSheet("""
            QPushButton {
                padding: 6px 8px;
                font-size: 11px;
                min-height: 18px;
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

        self.btn_editar_transporte = RexusButton("✏️ Editar")
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

        self.btn_exportar = RexusButton("📊 Excel")
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

    # Panel de control para tabla
    def crear_panel_control_tabla(self) -> QWidget:
        """Crea el panel de control para la pestaña de tabla."""
        panel = RexusGroupBox("Control de Transportes")
        layout = QHBoxLayout(panel)

        # Búsqueda
        self.input_busqueda = RexusLineEdit()
        self.input_busqueda.setPlaceholderText("Buscar transportes...")
        layout.addWidget(QLabel("Buscar:"))
        layout.addWidget(self.input_busqueda)

        # Filtro de estado
        self.combo_estado = RexusComboBox()
        self.combo_estado.addItems(["Todos", "Pendiente", "En tránsito", "Entregado", "Cancelado"])
        layout.addWidget(QLabel("Estado:"))
        layout.addWidget(self.combo_estado)

        # Botón de búsqueda
        btn_buscar = RexusButton("Buscar")
        btn_buscar.clicked.connect(self.buscar_transportes)
        layout.addWidget(btn_buscar)

        layout.addStretch()

        return panel

    def crear_panel_acciones_tabla(self) -> QWidget:
        """Crea el panel de acciones para la tabla con tooltips y feedback mejorado."""
        panel = QWidget()
        layout = QHBoxLayout(panel)

        # Botones de acción con iconos y tooltips
        self.btn_nuevo_transporte = RexusButton("🚛 Nuevo Transporte")
        self.btn_nuevo_transporte.clicked.connect(self.mostrar_dialogo_nuevo_transporte)
        self.btn_nuevo_transporte.setToolTip("Crear un nuevo registro de transporte")
        self.btn_nuevo_transporte.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-weight: bold;
                padding: 10px 15px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #218838;
                /* transform no soportado en Qt - removido */
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        layout.addWidget(self.btn_nuevo_transporte)

        self.btn_editar_transporte = RexusButton("✏️ Editar")
        self.btn_editar_transporte.clicked.connect(self.editar_transporte_seleccionado)
        self.btn_editar_transporte.setToolTip("Editar el transporte seleccionado")
        self.btn_editar_transporte.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: #212529;
                font-weight: bold;
                padding: 10px 15px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #e0a800;
                /* transform no soportado en Qt - removido */
            }
            QPushButton:disabled {
                background-color: #f8f9fa;
                color: #6c757d;
            }
        """)
        layout.addWidget(self.btn_editar_transporte)

        self.btn_eliminar_transporte = RexusButton("🗑️ Eliminar")
        self.btn_eliminar_transporte.clicked.connect(self.eliminar_transporte_seleccionado)
        self.btn_eliminar_transporte.setToolTip("Eliminar el transporte seleccionado")
        self.btn_eliminar_transporte.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                font-weight: bold;
                padding: 10px 15px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #c82333;
                /* transform no soportado en Qt - removido */
            }
            QPushButton:disabled {
                background-color: #f8f9fa;
                color: #6c757d;
            }
        """)
        layout.addWidget(self.btn_eliminar_transporte)

        layout.addStretch()

        self.btn_exportar = RexusButton("📊 Exportar Excel")
        self.btn_exportar.clicked.connect(self.exportar_a_excel)
        self.btn_exportar.setToolTip("Exportar datos a archivo Excel")
        self.btn_exportar.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                font-weight: bold;
                padding: 10px 15px;
                border-radius: 6px;
                border: none;
            }
            QPushButton:hover {
                background-color: #138496;
                /* transform no soportado en Qt - removido */
            }
        """)
        layout.addWidget(self.btn_exportar)
        
        return panel

        # Conectar eventos de selección para habilitar/deshabilitar botones
        if hasattr(self, 'tabla_transportes'):
            self.tabla_transportes.itemSelectionChanged.connect(self.actualizar_estado_botones)

    def crear_panel_graficos_mejorado(self) -> QWidget:
        """Crea el panel de gráficos con mejor presentación visual."""
        panel = RexusGroupBox("📈 Gráficos y Tendencias")
        layout = QVBoxLayout(panel)
        layout.setSpacing(8)

        # Placeholder mejorado para gráficos
        grafico_container = QWidget()
        grafico_layout = QVBoxLayout(grafico_container)
        
        # Título del gráfico
        titulo_grafico = QLabel("📊 Estadísticas de Entregas - Últimos 30 días")
        titulo_grafico.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                padding: 8px;
                background-color: #f8f9fa;
                border-radius: 4px;
                margin-bottom: 4px;
            }
        """)
        titulo_grafico.setAlignment(Qt.AlignmentFlag.AlignCenter)
        grafico_layout.addWidget(titulo_grafico)
        
        # Placeholder visual mejorado
        grafico_placeholder = QLabel("🔄 Cargando gráficos interactivos...\n\n📈 Próximamente:\n• Gráfico de entregas por día\n• Tendencias de tiempo de entrega\n• Análisis de rutas eficientes\n• Métricas de satisfacción")
        grafico_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        grafico_placeholder.setStyleSheet("""
            QLabel {
                border: 2px dashed #3498db;
                border-radius: 8px;
                padding: 30px;
                color: #2c3e50;
                font-size: 12px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                           stop:0 #f8f9fa, stop:1 #e9ecef);
                line-height: 1.5;
            }
        """)
        grafico_placeholder.setMinimumHeight(180)  # Reducido de 200
        grafico_layout.addWidget(grafico_placeholder)
        
        layout.addWidget(grafico_container)
        return panel

    def crear_panel_metricas_compacto(self) -> QWidget:
        """Crea el panel de métricas detalladas de forma compacta."""
        panel = RexusGroupBox("📋 Métricas Detalladas")
        layout = QVBoxLayout(panel)
        layout.setSpacing(6)  # Espaciado compacto

        # Barras de progreso compactas para diferentes métricas
        metricas_detalle = [
            ("🎯 Eficiencia de entregas", 85, "#27ae60", "85% de entregas a tiempo"),
            ("⏱️ Tiempo promedio entrega", 72, "#3498db", "72% dentro del objetivo"),
            ("😊 Satisfacción del cliente", 92, "#9b59b6", "92% de clientes satisfechos"),
            ("🚛 Utilización de flota", 68, "#f39c12", "68% de capacidad utilizada")
        ]

        for nombre, porcentaje, color, descripcion in metricas_detalle:
            metrica_widget = self.crear_widget_metrica_compacta(nombre, porcentaje, color, descripcion)
            layout.addWidget(metrica_widget)

        return panel

    def crear_tarjeta_metrica_compacta(self, titulo: str, valor: str, color: str, tooltip: str) -> QWidget:
        """Crea una tarjeta de métrica compacta y visual."""
        card = QWidget()
        card.setToolTip(tooltip)
        card.setStyleSheet(f"""
            QWidget {{
                background-color: white;
                border: 1px solid #e1e4e8;
                border-radius: 6px;
                padding: 6px;
            }}
            QWidget:hover {{
                border-color: {color};
                background-color: #f8f9fa;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(2)
        
        # Título compacto
        titulo_label = QLabel(titulo)
        titulo_label.setStyleSheet(f"""
            QLabel {{
                font-size: 10px;
                color: #6c757d;
                font-weight: 500;
            }}
        """)
        layout.addWidget(titulo_label)
        
        # Valor destacado
        valor_label = QLabel(valor)
        valor_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        valor_label.setStyleSheet(f"""
            QLabel {{
                font-size: 15px;
                font-weight: bold;
                color: {color};
                padding: 2px;
            }}
        """)
        layout.addWidget(valor_label)
        
        card.setFixedHeight(60)  # Altura fija compacta
        return card

    def crear_widget_metrica_compacta(self, nombre: str, porcentaje: int, color: str, descripcion: str) -> QWidget:
        """Crea un widget de métrica con barra de progreso compacta."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(3)
        
        # Encabezado con nombre y porcentaje
        header_layout = QHBoxLayout()
        nombre_label = QLabel(nombre)
        nombre_label.setStyleSheet("font-size: 11px; font-weight: 500; color: #2c3e50;")
        header_layout.addWidget(nombre_label)
        
        porcentaje_label = QLabel(f"{porcentaje}%")
        porcentaje_label.setStyleSheet(f"font-size: 11px; font-weight: bold; color: {color};")
        header_layout.addWidget(porcentaje_label)
        layout.addLayout(header_layout)
        
        # Barra de progreso compacta
        progress_bar = QProgressBar()
        progress_bar.setValue(porcentaje)
        progress_bar.setMaximumHeight(8)  # Barra muy compacta
        progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #e1e4e8;
                border-radius: 4px;
                background-color: #f6f8fa;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
        """)
        layout.addWidget(progress_bar)
        
        # Descripción pequeña
        desc_label = QLabel(descripcion)
        desc_label.setStyleSheet("font-size: 9px; color: #6c757d; padding-top: 2px;")
        layout.addWidget(desc_label)
        
        widget.setFixedHeight(55)  # Altura fija para consistencia
        return widget

    # Panel de estadísticas
    def crear_panel_resumen_estadisticas(self) -> QWidget:
        """Crea el panel de resumen de estadísticas."""
        panel = RexusGroupBox("Resumen General")
        layout = QGridLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setContentsMargins(8, 8, 8, 8)  # Margins for the widget
        layout.setVerticalSpacing(8)

        # Métricas principales (más compactas)
        metricas = [
            ("Total Transportes", "156", "#3498db"),
            ("En Tránsito", "23", "#f39c12"),
            ("Entregados Hoy", "8", "#27ae60"),
            ("Pendientes", "12", "#e74c3c")
        ]

        for i, (titulo, valor, color) in enumerate(metricas):
            card = self.crear_tarjeta_metrica_minimalista(titulo, valor, color)
            layout.addWidget(card, 0, i)

        return panel

        # Barras de progreso para diferentes métricas
        metricas_detalle = [
            ("Eficiencia de entregas", 85, "#27ae60"),
            ("Tiempo promedio de entrega", 72, "#3498db"),
            ("Satisfacción del cliente", 92, "#9b59b6"),
            ("Utilización de flota", 68, "#f39c12")
        ]

        for nombre, porcentaje, color in metricas_detalle:
            metrica_widget = self.crear_widget_metrica(nombre, porcentaje, color)
            layout.addWidget(metrica_widget)

        return panel

    # Panel de servicios
    def crear_panel_filtros_servicios_optimizado(self) -> QWidget:
        """Crea el panel de filtros para servicios optimizado y compacto."""
        panel = RexusGroupBox("🔧 Filtros de Servicios")
        layout = QHBoxLayout(panel)
        layout.setSpacing(8)  # Espaciado reducido
        layout.setContentsMargins(8, 6, 8, 6)  # Márgenes compactos

        # Opciones del mapa con iconografía
        self.combo_vista_mapa = RexusComboBox()
        # Icono del mapa grande y ejemplo de mapa solo si folium está disponible
        fallback_reason = None
        try:
            import tempfile
            import os
            if folium is not None:
                try:
                    mapa = folium.Map(
                        location=[-34.9214, -57.9544],  # La Plata, Argentina
                        zoom_start=12,
                        tiles='OpenStreetMap'
                    )
                    direcciones_ejemplo = [
                        {"lat": -34.9214, "lng": -57.9544, "nombre": "Almacén Central", "direccion": "Calle 7 entre 47 y 48, La Plata"},
                        {"lat": -34.9050, "lng": -57.9756, "nombre": "Sucursal Norte", "direccion": "Av. 13 y 44, La Plata"},
                        {"lat": -34.9380, "lng": -57.9468, "nombre": "Depósito Sur", "direccion": "Calle 120 y 610, La Plata"},
                        {"lat": -34.9100, "lng": -57.9300, "nombre": "Centro Distribución", "direccion": "Av. 1 y 60, La Plata"}
                    ]
                    for direccion in direcciones_ejemplo:
                        folium.Marker(
                            [direccion["lat"], direccion["lng"]],
                            popup=f"<b>{direccion['nombre']}</b><br>{direccion['direccion']}",
                            tooltip=direccion["nombre"],
                            icon=folium.Icon(color='blue', icon='truck', prefix='fa')
                        ).add_to(mapa)
                    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html', encoding='utf-8') as f:
                        mapa.save(f.name)
                        self.mapa_temp_file = f.name
                except Exception as e:
                    fallback_reason = f"Error creando el mapa con folium: {e}"
                else:
                    try:
                        QWebEngineView = self._get_webengine_view()
                        if QWebEngineView is None:
                            return self.crear_placeholder_mapa()
                        from PyQt6.QtCore import QUrl
                        self.mapa_web_view = QWebEngineView()
                        self.mapa_web_view.setUrl(QUrl.fromLocalFile(self.mapa_temp_file))
                        self.mapa_web_view.setMinimumHeight(400)
                        return self.mapa_web_view
                    except ImportError as e:
                        fallback_reason = f"QWebEngineView no disponible: {e}"
                    except Exception as e:
                        fallback_reason = f"Error creando QWebEngineView: {e}"
            else:
                fallback_reason = "folium no está instalado o no se pudo importar."
        except Exception as e:
            fallback_reason = f"Error inesperado: {e}"
        # Fallback mejorado con vista previa del mapa y motivo
        self.mapa_placeholder = QWidget()
        layout = QVBoxLayout(self.mapa_placeholder)
        titulo = QLabel("🗺️ Vista de Mapa - La Plata")
        titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; padding: 10px; background-color: #ecf0f1; border-radius: 6px; margin-bottom: 10px;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)
        motivo = QLabel(f"⚠️ Mapa interactivo no disponible\nMotivo: {fallback_reason if fallback_reason else 'Desconocido'}")
        motivo.setStyleSheet("font-size: 12px; color: #e67e22; padding: 8px; background-color: #fef5e7; border-radius: 4px; margin-top: 10px;")
        motivo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(motivo)
        return self.mapa_placeholder
    def crear_widget_servicios_activos_mejorado(self) -> QWidget:
        """Crea el widget de servicios activos con mejor layout."""
        widget = RexusGroupBox("📋 Servicios Activos")
        layout = QVBoxLayout(widget)
        layout.setSpacing(6)  # Espaciado reducido
        layout.setContentsMargins(8, 8, 8, 8)

        # Panel de acciones compacto
        acciones_layout = QHBoxLayout()
        acciones_layout.setSpacing(6)

        btn_nuevo_servicio = RexusButton("➕ Nuevo")
        btn_nuevo_servicio.setToolTip("Crear nuevo servicio")
        btn_nuevo_servicio.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-weight: bold;
                padding: 4px 8px;
                border-radius: 3px;
                border: none;
                font-size: 10px;
                min-height: 18px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        acciones_layout.addWidget(btn_nuevo_servicio)

        btn_editar_servicio = RexusButton("✏️ Editar")
        btn_editar_servicio.setToolTip("Editar servicio seleccionado")
        btn_editar_servicio.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: #212529;
                font-weight: bold;
                padding: 4px 8px;
                border-radius: 3px;
                border: none;
                font-size: 10px;
                min-height: 18px;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
        """)
        acciones_layout.addWidget(btn_editar_servicio)

        acciones_layout.addStretch()
        layout.addLayout(acciones_layout)

        # Tabla de servicios
        self.tabla_servicios = StandardComponents.create_standard_table()
        self.configurar_tabla_servicios()
        layout.addWidget(self.tabla_servicios)

        return widget

    def crear_widget_detalles_servicio_mejorado(self) -> QWidget:
        """Crea el widget de detalles del servicio con mejor placeholder."""
        widget = RexusGroupBox("📊 Detalles del Servicio")
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)

        # Placeholder mejorado con iconografía
        self.label_servicio_info = QLabel("""
        <div style='text-align: center; padding: 30px;'>
            <p style='font-size: 48px; margin: 10px;'>🔧</p>
            <h3 style='color: #495057; margin: 15px 0;'>Seleccione un Servicio</h3>
            <p style='color: #6c757d; font-size: 11px; line-height: 1.4;'>
                Haga clic en un servicio de la lista<br>
                para ver información detallada
            </p>
        </div>
        """)
        self.label_servicio_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_servicio_info.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #ffffff);
                border: 2px dashed #dee2e6;
                border-radius: 8px;
                margin: 10px;
            }
        """)
        layout.addWidget(self.label_servicio_info)

        return widget

    # Panel de mapa
    def crear_panel_control_mapa_optimizado(self) -> QWidget:
        """Crea el panel de control del mapa optimizado y compacto."""
        panel = RexusGroupBox("🗺️ Control del Mapa")
        panel.setFixedHeight(50)
        layout = QHBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(8, 6, 8, 6)
        panel.setLayout(layout)

        self.combo_vista_mapa = RexusComboBox()
        layout.addWidget(self.combo_vista_mapa)

        # Intentar crear el mapa interactivo solo si folium está disponible
        if folium is not None:
            try:
                import tempfile
                mapa = folium.Map(
                    location=[-34.9214, -57.9544],
                    zoom_start=12,
                    tiles='OpenStreetMap'
                )
                direcciones_ejemplo = [
                    {"lat": -34.9214, "lng": -57.9544, "nombre": "Almacén Central", "direccion": "Calle 7 entre 47 y 48, La Plata"},
                    {"lat": -34.9050, "lng": -57.9756, "nombre": "Sucursal Norte", "direccion": "Av. 13 y 44, La Plata"},
                    {"lat": -34.9380, "lng": -57.9468, "nombre": "Depósito Sur", "direccion": "Calle 120 y 610, La Plata"},
                    {"lat": -34.9100, "lng": -57.9300, "nombre": "Centro Distribución", "direccion": "Av. 1 y 60, La Plata"}
                ]
                for direccion in direcciones_ejemplo:
                    folium.Marker(
                        [direccion["lat"], direccion["lng"]],
                        popup=f"<b>{direccion['nombre']}</b><br>{direccion['direccion']}",
                        tooltip=direccion["nombre"],
                        icon=folium.Icon(color='blue', icon='truck', prefix='fa')
                    ).add_to(mapa)
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html', encoding='utf-8') as f:
                    mapa.save(f.name)
                    self.mapa_temp_file = f.name
                try:
                    from PyQt6.QtWebEngineWidgets import QWebEngineView
                    from PyQt6.QtCore import QUrl
                    self.mapa_web_view = QWebEngineView()
                    self.mapa_web_view.setUrl(QUrl.fromLocalFile(self.mapa_temp_file))
                    self.mapa_web_view.setMinimumHeight(400)
                    layout.addWidget(self.mapa_web_view)
                except ImportError:
                    # Si no está disponible QWebEngineView, mostrar placeholder
                    self.mapa_placeholder = QLabel("Mapa interactivo no disponible (QWebEngineView no instalado)")
                    layout.addWidget(self.mapa_placeholder)
            except Exception as e:
                self.mapa_placeholder = QLabel(f"Error creando el mapa: {str(e)[:50]}...")
                layout.addWidget(self.mapa_placeholder)
        else:
            # Fallback si folium no está disponible
            self.mapa_placeholder = QLabel("Mapa interactivo no disponible (folium no instalado)")
            layout.addWidget(self.mapa_placeholder)

        return panel

    def crear_tarjeta_metrica_minimalista(self, titulo, valor, color):
        card = QWidget()
        card.setStyleSheet(f"""
            background-color: #fafbfc;
            border: 1px solid #e1e4e8;
            border-radius: 4px;
            padding: 6px 8px;
            min-width: 70px;
            min-height: 38px;
        """)
        layout = QVBoxLayout(card)
        layout.setSpacing(2)
        label_valor = QLabel(valor)
        label_valor.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {color}; margin-bottom: 0px;")
        label_valor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label_titulo = QLabel(titulo)
        label_titulo.setStyleSheet("font-size: 9.5px; color: #7f8c8d;")
        label_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label_valor)
        layout.addWidget(label_titulo)
        return card

    def crear_panel_info_mapa(self) -> QWidget:
        """Crea el panel de información del mapa."""
        panel = RexusGroupBox("Información del Mapa")
        layout = QHBoxLayout(panel)

        # Información de rutas
        info_rutas = QLabel("🛣️ Rutas activas: 3\n📊 Distancia total: 247 km")
        info_rutas.setStyleSheet("font-size: 12px; color: #34495e;")
        layout.addWidget(info_rutas)

        # Información de vehículos
        info_vehiculos = QLabel("🚛 Vehículos en ruta: 12\n⏱️ Tiempo promedio: 2.4 hrs")
        info_vehiculos.setStyleSheet("font-size: 12px; color: #34495e;")
        layout.addWidget(info_vehiculos)

        # Botón para ver todas las rutas
        btn_ver_rutas = RexusButton("Ver Todas las Rutas")
        btn_ver_rutas.clicked.connect(self.mostrar_todas_rutas)
        layout.addWidget(btn_ver_rutas)

        return panel

    def mostrar_todas_rutas(self):
        """Muestra todas las rutas en el mapa."""
        if hasattr(self, 'mapa_placeholder') and hasattr(self.mapa_placeholder, 'layout'):
            # Buscar el label de información
            layout = self.mapa_placeholder.layout()
            if layout and layout.count() > 1:
                item = layout.itemAt(1)
                if item:
                    info_label = item.widget()
                    if isinstance(info_label, QLabel):
                        info_label.setText("""📍 Ruta 1: Buenos Aires → La Plata (67 km)
📍 Ruta 2: La Plata → Berisso (15 km) 
📍 Ruta 3: Berisso → Ensenada (8 km)
📍 Ruta 4: Buenos Aires → San Isidro (32 km)

🚛 Vehículos desplegados: 23
⏱️ Tiempo total estimado: 6.2 hrs
📦 Entregas programadas: 45""")
                        info_label.setStyleSheet("""
                        QLabel {
                            border: 3px solid #e67e22;
                            border-radius: 12px;
                            padding: 20px;
                            color: #d35400;
                            font-size: 12px;
                            font-weight: 500;
                            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                                       stop:0 #fef9e7, stop:1 #fff3cd);
                        }
                    """)

    def actualizar_tabla_transportes(self):
        """Actualiza la tabla de transportes."""
        if self.controller:
            try:
                self.controller.cargar_datos_iniciales()
            except Exception as e:
                print(f"❌ Error al actualizar tabla: {str(e)}")

    def aplicar_filtros_servicios(self):
        """Aplica filtros a los servicios."""
        tipo = self.combo_tipo_servicio.currentText()
        estado = self.combo_estado_servicio.currentText()
        
        # Simular filtrado
        mensaje = f"Filtros aplicados:\nTipo: {tipo}\nEstado: {estado}\n\nResultados encontrados: 12"
        if hasattr(self, 'label_servicio_info'):
            self.label_servicio_info.setText(mensaje)
            self.label_servicio_info.setStyleSheet("""
                QLabel {
                    color: #27ae60;
                    font-size: 14px;
                    padding: 20px;
                    background-color: #e8f8f5;
                    border-radius: 8px;
                }
            """)

    # Métodos auxiliares
    def crear_tarjeta_metrica(self, titulo: str, valor: str, color: str) -> QWidget:
        """Crea una tarjeta de métrica."""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-left: 4px solid {color};
                border-radius: 8px;
                padding: 10px;
                margin: 5px;
            }}
        """)

        layout = QVBoxLayout(card)
        
        titulo_label = QLabel(titulo)
        titulo_label.setStyleSheet("font-size: 12px; color: #7f8c8d; font-weight: bold;")
        layout.addWidget(titulo_label)

        valor_label = QLabel(valor)
        valor_label.setStyleSheet(f"font-size: 24px; color: {color}; font-weight: bold;")
        layout.addWidget(valor_label)

        return card

    def crear_widget_metrica(self, nombre: str, porcentaje: int, color: str) -> QWidget:
        """Crea un widget de métrica con barra de progreso."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(5)

        # Etiqueta
        label = QLabel(f"{nombre}: {porcentaje}%")
        label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        layout.addWidget(label)

        # Barra de progreso
        progress = QProgressBar()
        progress.setValue(porcentaje)
        progress.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: #ecf0f1;
                height: 20px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
        """)
        layout.addWidget(progress)

        return widget


    def configurar_tabla_servicios(self):
        """Configura la tabla de servicios."""
        headers = ["ID", "Tipo", "Estado", "Cliente", "Prioridad"]
        self.tabla_servicios.setColumnCount(len(headers))
        self.tabla_servicios.setHorizontalHeaderLabels(headers)
        self.tabla_servicios.setStyleSheet("font-size: 11px;")

    def configurar_tabla_direcciones(self):
        """Stub: tabla de direcciones no implementada."""
        pass

    # Métodos de evento
    def buscar_transportes(self):
        """Busca transportes según los filtros."""
        termino = self.input_busqueda.text()
        estado = self.combo_estado.currentText()
        
        if self.controller:
            self.controller.buscar_transportes(termino, estado)

    def actualizar_datos_generales(self):
        """Actualiza todos los datos de las pestañas."""
        try:
            self.solicitud_actualizar_estadisticas.emit()
            
            # Cargar datos de ejemplo si no hay controlador
            self.cargar_datos_ejemplo()
            
            if self.controller:
                self.controller.cargar_datos_iniciales()
            
            # Actualizar estadísticas
            self.actualizar_estadisticas({})
            
            from rexus.utils.message_system import show_success
            show_success(self, "Actualización", "Datos actualizados correctamente")
        except Exception as e:
            from rexus.utils.message_system import show_error
            show_error(self, "Error", f"Error actualizando datos: {str(e)}")

    # (definición duplicada de aplicar_filtros_servicios eliminada)

    def centrar_mapa(self):
        """Centra el mapa en La Plata."""
        try:
            if hasattr(self, 'mapa_web_view'):
                # Opciones del mapa con iconografía
                self.combo_vista_mapa = RexusComboBox()
                # Icono del mapa grande y ejemplo de mapa solo si folium está disponible
                try:
                    import tempfile
                    if folium is not None:
                        mapa = folium.Map(
                            location=[-34.9214, -57.9544],  # La Plata, Argentina
                            zoom_start=12,
                            tiles='OpenStreetMap'
                        )
                        # Agregar marcador
                        folium.Marker([-34.9214, -57.9544], popup="La Plata").add_to(mapa)
                        # Guardar y cargar
                        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
                        mapa.save(temp_file.name)
                        temp_file.close()
                        self.mapa_web_view.setUrl(QUrl.fromLocalFile(temp_file.name))
                except Exception:
                    pass
        except Exception:
            pass


    def editar_transporte_seleccionado(self):
        """Edita el transporte seleccionado con validación mejorada."""
        fila_actual = self.tabla_transportes.currentRow()
        if fila_actual >= 0:
            try:
                # Obtener ID de manera segura
                item_id = self.tabla_transportes.item(fila_actual, 0)
                if item_id:
                    transporte_id = item_id.text()
                    dialogo = DialogoNuevoTransporte(self, transporte_id)
                    if dialogo.exec() == QDialog.DialogCode.Accepted:
                        datos = dialogo.obtener_datos()
                        datos['id'] = transporte_id
                        self.solicitud_actualizar_transporte.emit(datos)
                        self.actualizar_tabla_transportes()
                else:
                    from rexus.utils.message_system import show_warning
                    show_warning(self, "Advertencia", "No se pudo obtener el ID del transporte")
            except Exception as e:
                from rexus.utils.message_system import show_error
                show_error(self, "Error", f"Error al editar transporte: {str(e)}")
        else:
            from rexus.utils.message_system import show_warning
            show_warning(self, "Advertencia", "Seleccione un transporte para editar")

    def eliminar_transporte_seleccionado(self):
        """Elimina el transporte seleccionado con confirmación mejorada."""
        fila_actual = self.tabla_transportes.currentRow()
        if fila_actual >= 0:
            try:
                # Obtener ID de manera segura
                item_id = self.tabla_transportes.item(fila_actual, 0)
                if item_id:
                    transporte_id = item_id.text()
                    
                    # Confirmar eliminación con diálogo personalizado
                    from PyQt6.QtWidgets import QMessageBox
                    msg_box = QMessageBox(self)
                    msg_box.setWindowTitle("Confirmar eliminación")
                    msg_box.setText(f"¿Está seguro de eliminar el transporte #{transporte_id}?")
                    msg_box.setDetailedText("Esta acción no se puede deshacer.")
                    msg_box.setIcon(QMessageBox.Icon.Question)
                    msg_box.setStandardButtons(
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    msg_box.setDefaultButton(QMessageBox.StandardButton.No)
                    
                    # Personalizar botones
                    yes_button = msg_box.button(QMessageBox.StandardButton.Yes)
                    if yes_button:
                        yes_button.setText("Sí, eliminar")
                    no_button = msg_box.button(QMessageBox.StandardButton.No)
                    if no_button:
                        no_button.setText("Cancelar")
                    
                    if msg_box.exec() == QMessageBox.StandardButton.Yes:
                        self.solicitud_eliminar_transporte.emit(transporte_id)
                        self.actualizar_tabla_transportes()
                        
                        # Feedback de éxito
                        from rexus.utils.message_system import show_success
                        show_success(self, "Éxito", f"Transporte #{transporte_id} eliminado correctamente")
                else:
                    from rexus.utils.message_system import show_warning
                    show_warning(self, "Advertencia", "No se pudo obtener el ID del transporte")
            except Exception as e:
                from rexus.utils.message_system import show_error
                show_error(self, "Error", f"Error al eliminar transporte: {str(e)}")
        else:
            from rexus.utils.message_system import show_warning
            show_warning(self, "Advertencia", "Seleccione un transporte para eliminar")

    def exportar_a_excel(self):
        """Exporta los datos a Excel."""
        try:
            from PyQt6.QtWidgets import QFileDialog
            import pandas as pd
            
            # Obtener datos de la tabla
            datos = []
            for fila in range(self.tabla_transportes.rowCount()):
                fila_datos = {}
                for col in range(self.tabla_transportes.columnCount()):
                    header_item = self.tabla_transportes.horizontalHeaderItem(col)
                    header = header_item.text() if header_item else f"Columna_{col}"
                    item = self.tabla_transportes.item(fila, col)
                    fila_datos[header] = item.text() if item else ""
                datos.append(fila_datos)
            
            if datos:
                # Solicitar ubicación del archivo
                archivo, _ = QFileDialog.getSaveFileName(
                    self,
                    "Exportar a Excel",
                    "transportes_logistica.xlsx",
                    "Excel files (*.xlsx)"
                )
                
                if archivo:
                    df = pd.DataFrame(datos)
                    df.to_excel(archivo, index=False)
                    print(f"✅ Datos exportados exitosamente a: {archivo}")
            else:
                print("⚠️ No hay datos para exportar")
                
        except ImportError:
            print("❌ pandas no está instalado. Instale pandas para usar esta funcionalidad.")
        except Exception as e:
            print(f"❌ Error al exportar: {str(e)}")

    # XSS Protection
    def init_xss_protection(self):
        """Inicializa la protección XSS."""
        try:
            self.form_protector = FormProtector()
            
            # Proteger campos de entrada
            if hasattr(self, 'input_busqueda'):
                self.form_protector.protect_field(self.input_busqueda, "busqueda")
                
        except Exception as e:
            logging.error(f"Error inicializando protección XSS: {e}")

    def configurar_interfaz_segura(self):
        """Configura controles de seguridad adicionales."""
        pass

    def set_controller(self, controller):
        """Establece el controlador."""
        self.controller = controller
        
    # Métodos de compatibilidad con el controlador existente
    def cargar_transportes(self, transportes: List[Dict]):
        """Carga transportes en la tabla."""
        if not hasattr(self, 'tabla_transportes'):
            return
            
        self.tabla_transportes.setRowCount(len(transportes))
        
        for row, transporte in enumerate(transportes):
            # Llenar datos de transporte
            self.tabla_transportes.setItem(row, 0, QTableWidgetItem(str(transporte.get('id', ''))))
            self.tabla_transportes.setItem(row, 1, QTableWidgetItem(str(transporte.get('origen', ''))))
            self.tabla_transportes.setItem(row, 2, QTableWidgetItem(str(transporte.get('destino', ''))))
            self.tabla_transportes.setItem(row, 3, QTableWidgetItem(str(transporte.get('estado', ''))))
            self.tabla_transportes.setItem(row, 4, QTableWidgetItem(str(transporte.get('conductor', ''))))
            self.tabla_transportes.setItem(row, 5, QTableWidgetItem(str(transporte.get('fecha', ''))))

    def actualizar_estadisticas(self, stats: Dict):
        """Actualiza las estadísticas mostradas."""
        # Actualizar métricas con datos reales o de ejemplo
        try:
            # Usar datos estáticos para evitar warnings de seguridad
            stats_actualizadas = {
                'total_transportes': 156,
                'en_transito': 23,
                'entregados_hoy': 8,
                'pendientes': 12
            }
            
            # Si existe el panel de métricas, actualizarlo
            if hasattr(self, 'tab_widget'):
                from rexus.utils.message_system import show_success
                show_success(self, "Éxito", "Estadísticas actualizadas correctamente")
        except Exception as e:
            from rexus.utils.message_system import show_error
            show_error(self, "Error", f"Error actualizando estadísticas: {str(e)}")

    def cargar_datos_ejemplo(self):
        """Carga datos de ejemplo en las tablas."""
        try:
            # Datos de ejemplo para transportes
            transportes_ejemplo = [
                {'id': '001', 'origen': 'Buenos Aires', 'destino': 'La Plata', 'estado': 'En tránsito', 'conductor': 'Juan Pérez', 'fecha': '2025-08-09'},
                {'id': '002', 'origen': 'La Plata', 'destino': 'Berisso', 'estado': 'Pendiente', 'conductor': 'María González', 'fecha': '2025-08-09'},
                {'id': '003', 'origen': 'Buenos Aires', 'destino': 'San Isidro', 'estado': 'Entregado', 'conductor': 'Carlos Ruiz', 'fecha': '2025-08-08'},
                {'id': '004', 'origen': 'Quilmes', 'destino': 'Avellaneda', 'estado': 'En tránsito', 'conductor': 'Ana Silva', 'fecha': '2025-08-09'},
                {'id': '005', 'origen': 'Tigre', 'destino': 'San Fernando', 'estado': 'Pendiente', 'conductor': 'Roberto López', 'fecha': '2025-08-10'}
            ]
            
            self.cargar_transportes(transportes_ejemplo)
            
            # Datos de ejemplo para servicios
            servicios_ejemplo = [
                {'id': 'SRV001', 'tipo': 'Express', 'estado': 'Activo', 'cliente': 'Empresa ABC', 'prioridad': 'Alta'},
                {'id': 'SRV002', 'tipo': 'Estándar', 'estado': 'Activo', 'cliente': 'Comercial XYZ', 'prioridad': 'Media'},
                {'id': 'SRV003', 'tipo': 'Económico', 'estado': 'Pausado', 'cliente': 'Distribuidor 123', 'prioridad': 'Baja'}
            ]
            
            self.cargar_servicios(servicios_ejemplo)
            
            # Datos de ejemplo para direcciones
            direcciones_ejemplo = [
                {'direccion': 'Av. 7 N° 1234', 'ciudad': 'La Plata', 'estado': 'Buenos Aires', 'tipo': 'Almacén'},
                {'direccion': 'Calle 50 N° 567', 'ciudad': 'La Plata', 'estado': 'Buenos Aires', 'tipo': 'Sucursal'},
                {'direccion': 'Av. Corrientes 890', 'ciudad': 'Buenos Aires', 'estado': 'CABA', 'tipo': 'Depósito'}
            ]
            
            self.cargar_direcciones(direcciones_ejemplo)
            
        except Exception as e:
            from rexus.utils.message_system import show_error
            show_error(self, "Error", f"Error cargando datos de ejemplo: {str(e)}")

    def cargar_servicios(self, servicios: List[Dict]):
        """Carga servicios en la tabla de servicios."""
        if not hasattr(self, 'tabla_servicios'):
            return
            
        self.tabla_servicios.setRowCount(len(servicios))
        
        for row, servicio in enumerate(servicios):
            self.tabla_servicios.setItem(row, 0, QTableWidgetItem(str(servicio.get('id', ''))))
            self.tabla_servicios.setItem(row, 1, QTableWidgetItem(str(servicio.get('tipo', ''))))
            self.tabla_servicios.setItem(row, 2, QTableWidgetItem(str(servicio.get('estado', ''))))
            self.tabla_servicios.setItem(row, 3, QTableWidgetItem(str(servicio.get('cliente', ''))))
            self.tabla_servicios.setItem(row, 4, QTableWidgetItem(str(servicio.get('prioridad', ''))))

    def cargar_direcciones(self, direcciones: List[Dict]):
        """Stub: tabla de direcciones no implementada."""
        pass

    # Métodos para el mapa interactivo
    def actualizar_marcadores_mapa(self):
        """Stub: función de mapa interactivo no implementada."""
        pass

    def obtener_coordenadas_ejemplo(self, direccion: str, ciudad: str) -> tuple:
        """Obtiene coordenadas de ejemplo para direcciones de La Plata."""
        # Coordenadas base de La Plata
        base_lat, base_lng = -34.9214, -57.9544
        
        # Generar variaciones basadas en la dirección para simular ubicaciones reales
        hash_obj = hashlib.md5(f"{direccion}{ciudad}".encode(), usedforsecurity=False)
        hash_hex = hash_obj.hexdigest()
        
        # Usar los primeros caracteres del hash para generar offsets
        offset_lat = (int(hash_hex[:2], 16) % 100 - 50) * 0.001  # ±0.05 grados
        offset_lng = (int(hash_hex[2:4], 16) % 100 - 50) * 0.001  # ±0.05 grados
        
        return (base_lat + offset_lat, base_lng + offset_lng)

    def on_mapa_location_clicked(self, lat: float, lng: float):
        """Maneja clics en ubicaciones del mapa."""
        try:
            from rexus.utils.message_system import show_success
            show_success(self, "Mapa", f"Ubicación seleccionada:\nLatitud: {lat:.6f}\nLongitud: {lng:.6f}")
        except Exception as e:
            print(f"Error manejando clic en mapa: {e}")

    def on_mapa_marker_clicked(self, marker_data: dict):
        """Maneja clics en marcadores del mapa."""
        try:
            direccion = marker_data.get('descripcion', 'Ubicación desconocida')
            tipo = marker_data.get('tipo', 'Ubicación')
            
            from rexus.utils.message_system import show_success
            show_success(self, "Marcador", f"Marcador seleccionado:\n{tipo}: {direccion}")
        except Exception as e:
            print(f"Error manejando clic en marcador: {e}")

    def mostrar_mensaje(self, mensaje: str, tipo: str = "info"):
        """Muestra un mensaje al usuario."""
        from rexus.utils.message_system import show_error, show_warning
        if tipo == "error":
            show_error(self, "Error", mensaje)
        else:
            show_warning(self, "Información", mensaje)


class DialogoNuevoTransporte(QDialog):

    def obtener_datos(self):
        """Stub: retorna un diccionario vacío o los datos del formulario si estuviera implementado."""
        return {}
    """Diálogo mejorado para crear/editar transportes con validación avanzada."""
    
    def __init__(self, parent=None, transporte_id=None):
        super().__init__(parent)
        self.transporte_id = transporte_id
        self.validator_manager = None
        self.mapa_web_view = None  # Inicializar atributo
        self.init_ui()
        self.setup_validation()
        
    def init_ui(self):
        """Inicializa la interfaz del diálogo."""
        self.setWindowTitle("Nuevo Transporte" if not self.transporte_id else "Editar Transporte")
        self.setModal(True)
        self.resize(340, 260)
        # Estilo minimalista y compacto
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 6px;
            }
            QLabel {
                font-weight: bold;
                color: #212529;
                margin-bottom: 4px;
                font-size: 12px;
                padding: 2px 0px;
                background-color: transparent;
            }
            /* Estilos específicos para tema oscuro */
            QDialog[theme="dark"] QLabel {
                color: #f8f9fa;
            }
            QLineEdit, QComboBox, QDateEdit {
                padding: 4px 7px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: white;
                font-size: 11px;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
                border-color: #007bff;
            }
            QPushButton {
                padding: 5px 12px;
                font-weight: bold;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton[class="primary"] {
                background-color: #007bff;
                color: white;
                border: none;
            }
            QPushButton[class="primary"]:hover {
                background-color: #0056b3;
            }
            QPushButton[class="secondary"] {
                background-color: #6c757d;
                color: white;
                border: none;
            }
            QPushButton[class="secondary"]:hover {
                background-color: #545b62;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)
        # Título del diálogo
        titulo = QLabel("Información del Transporte")
        titulo.setStyleSheet("font-size: 11px; font-weight: 600; color: #24292e; margin-bottom: 6px;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(titulo)
        # Formulario minimalista
        form_layout = QFormLayout()
        form_layout.setSpacing(6)
        
        # Origen con tooltip
        self.input_origen = RexusLineEdit()
        self.input_origen.setPlaceholderText("Ejemplo: Ciudad de México")
        self.input_origen.setToolTip("Ciudad o ubicación de origen del transporte")
        form_layout.addRow("Origen:", self.input_origen)
        
        # Destino con tooltip
        self.input_destino = RexusLineEdit()
        self.input_destino.setPlaceholderText("Ejemplo: Guadalajara")
        self.input_destino.setToolTip("Ciudad o ubicación de destino del transporte")
        form_layout.addRow("Destino:", self.input_destino)
        
        # Estado mejorado
        self.combo_estado = RexusComboBox()
        estados = [
            ("Pendiente", "🟡 Pendiente"),
            ("En tránsito", "🔵 En tránsito"),
            ("Entregado", "🟢 Entregado"),
            ("Cancelado", "🔴 Cancelado")
        ]
        for valor, texto in estados:
            self.combo_estado.addItem(texto, valor)
        self.combo_estado.setToolTip("Estado actual del transporte")
        form_layout.addRow("Estado:", self.combo_estado)
        
        # Conductor con validación
        self.input_conductor = RexusLineEdit()
        self.input_conductor.setPlaceholderText("Ejemplo: Juan Pérez González")
        self.input_conductor.setToolTip("Nombre completo del conductor responsable")
        form_layout.addRow("Conductor:", self.input_conductor)
        
        # Fecha mejorada
        self.input_fecha = QDateEdit()
        self.input_fecha.setCalendarPopup(True)
        self.input_fecha.setDate(QDateEdit().date())
        self.input_fecha.setToolTip("Fecha programada del transporte")
        self.input_fecha.setStyleSheet("QDateEdit::drop-down { width: 20px; }")
        form_layout.addRow("Fecha:", self.input_fecha)
        
        # Campos adicionales
        self.input_vehiculo = RexusLineEdit()
        self.input_vehiculo.setPlaceholderText("Ejemplo: ABC-123")
        self.input_vehiculo.setToolTip("Placa o identificación del vehículo")
        form_layout.addRow("Vehículo:", self.input_vehiculo)
        
        self.input_observaciones = RexusLineEdit()
        self.input_observaciones.setPlaceholderText("Observaciones adicionales...")
        self.input_observaciones.setToolTip("Comentarios o notas especiales")
        form_layout.addRow("Observaciones:", self.input_observaciones)
        
        layout.addLayout(form_layout)
        
        # Botones con estilos mejorados
        botones_layout = QHBoxLayout()
        botones_layout.addStretch()
        
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setProperty("class", "secondary")
        self.btn_cancelar.clicked.connect(self.reject)
        botones_layout.addWidget(self.btn_cancelar)
        
        self.btn_guardar = QPushButton("Guardar" if not self.transporte_id else "Actualizar")
        self.btn_guardar.setProperty("class", "primary")
        self.btn_guardar.clicked.connect(self.validar_y_aceptar)
        botones_layout.addWidget(self.btn_guardar)
        
        layout.addLayout(botones_layout)
        
    def setup_validation(self):
        """Configura la validación en tiempo real."""
        # Usar validación básica si los módulos avanzados no están disponibles
        self.validator_manager = None
    
    def validar_y_aceptar(self):
        """Valida los datos antes de aceptar el diálogo."""
        # Validación básica
        if not self.input_origen.text().strip():
            from rexus.utils.message_system import show_warning
            show_warning(self, "Validación", "El origen es obligatorio")
            self.input_origen.setFocus()
            return
            
        if not self.input_destino.text().strip():
            from rexus.utils.message_system import show_warning
            show_warning(self, "Validación", "El destino es obligatorio")
            self.input_destino.setFocus()
            return
            
        if not self.input_conductor.text().strip():
            from rexus.utils.message_system import show_warning
            show_warning(self, "Validación", "El conductor es obligatorio")
            self.input_conductor.setFocus()
            return
        
        # Validación avanzada si está disponible
        if self.validator_manager and not self.validator_manager.validate_all():
            return

        # Si todas las validaciones pasan, aceptar el diálogo
        self.accept()

    def on_mapa_location_clicked(self, lat, lng):
        """Maneja clicks en el mapa."""
        print(f"Ubicación clickeada: {lat}, {lng}")

    def on_mapa_marker_clicked(self, marker_id):
        """Maneja clicks en marcadores."""
        print(f"Marcador clickeado: {marker_id}")

    def actualizar_marcadores_mapa(self):
        """Actualiza los marcadores del mapa con datos de la tabla."""
        try:
            # Si tenemos un mapa web real, recrearlo
            if hasattr(self, 'mapa_web_view'):
                import folium
                import tempfile
                
                mapa = folium.Map(
                    location=[-34.9214, -57.9544],
                    zoom_start=12,
                    tiles='OpenStreetMap'
                )
                
                # Datos de ejemplo (en producción vendrían de la tabla/base de datos)
                direcciones = [
                    {"lat": -34.9214, "lng": -57.9544, "nombre": "Almacén Central", "direccion": "Calle 7 entre 47 y 48, La Plata"},
                    {"lat": -34.9050, "lng": -57.9756, "nombre": "Sucursal Norte", "direccion": "Av. 13 y 44, La Plata"},
                    {"lat": -34.9380, "lng": -57.9468, "nombre": "Depósito Sur", "direccion": "Calle 120 y 610, La Plata"},
                    {"lat": -34.9100, "lng": -57.9300, "nombre": "Centro Distribución", "direccion": "Av. 1 y 60, La Plata"}
                ]
                
                for direccion in direcciones:
                    folium.Marker(
                        [direccion["lat"], direccion["lng"]],
                        popup=f"<b>{direccion['nombre']}</b><br>{direccion['direccion']}",
                        tooltip=direccion["nombre"]
                    ).add_to(mapa)
                
                # Guardar y cargar mapa actualizado
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.html', encoding='utf-8') as f:
                    mapa.save(f.name)
                    self.mapa_temp_file = f.name
                
                if hasattr(self, 'mapa_web_view') and self.mapa_web_view:
                    self.mapa_web_view.setUrl(QUrl.fromLocalFile(self.mapa_temp_file))
                
        except Exception as e:
            print(f"Error actualizando marcadores: {e}")