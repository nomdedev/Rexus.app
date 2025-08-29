"""
MIT License

Copyright (c) 2024 Rexus.app

Vista Principal de Herrajes - Interfaz moderna de gestión de herrajes
Versión simplificada con componentes básicos de PyQt6
"""

import logging
from typing import Dict, List

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QHeaderView
)

# Importar componentes básicos
from rexus.ui.components.base_components import RexusColors
from rexus.utils.loading_manager import LoadingManager
from rexus.utils.message_system import ask_question, show_error, show_warning
from rexus.utils.xss_protection import FormProtector
from rexus.utils.export_manager import ModuleExportMixin
import importlib
herrajes_constants = importlib.import_module('rexus.modules.06_herrajes.constants')
HerrajesConstants = herrajes_constants.HerrajesConstants

logger = logging.getLogger(__name__)


class HerrajesView(QWidget, ModuleExportMixin):
    """Vista principal del módulo de herrajes con UI/UX modernizada."""

    # Señales
    datos_actualizados = pyqtSignal()
    error_ocurrido = pyqtSignal(str)
    herraje_seleccionado = pyqtSignal(dict)

    def __init__(self):
        QWidget.__init__(self)
        ModuleExportMixin.__init__(self)
        self.controller = None
        self.loading_manager = LoadingManager()

        # Inicializar protección XSS
        self.form_protector = FormProtector(self)
        self.form_protector.dangerous_content_detected.connect(
            self._on_dangerous_content
        )

        # Referencias a widgets importantes
        self.tabla_herrajes = None
        self.input_busqueda = None
        self.combo_categoria = None
        self.stats_labels = {}

        self.init_ui()
        self.aplicar_estilos()

    def setup_ui(self):
        """Método de compatibilidad para setup_ui."""
        self.init_ui()

    def refresh_data(self):
        """Actualiza los datos mostrados en la vista."""
        try:
            if self.controller and hasattr(self.controller, 'cargar_herrajes'):
                self.controller.cargar_herrajes()
            else:
                self._cargar_datos_demo()
        except Exception as e:
            self.show_error(f"Error actualizando datos: {e}")

    def show_error(self, mensaje, titulo="Error"):
        """
        Muestra un mensaje de error al usuario.

        Args:
            mensaje (str): Mensaje de error
            titulo (str): Título del diálogo
        """
        try:
            show_error(self, titulo, mensaje)
        except ImportError as e:
            # Fallback usando QMessageBox si show_error no está disponible
            logger.warning("show_error no disponible, usando fallback: %s", e)
            from PyQt6.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle(titulo)
            msg.setText(mensaje)
            msg.exec()

    def _cargar_datos_demo(self):
        """Carga datos demo cuando no hay controlador."""
        datos_demo = [
            {
                'id': 1,
                'codigo': 'H001',
                'nombre': 'Bisagra Piano',
                'categoria': 'Bisagras',
                'stock_actual': 50,
                'precio_unitario': 15.75
            },
            {
                'id': 2,
                'codigo': 'H002', 
                'nombre': 'Manija Moderna',
                'categoria': 'Manijas',
                'stock_actual': 25,
                'precio_unitario': 32.50
            }
        ]
        self.actualizar_tabla_herrajes(datos_demo)

    def init_ui(self):
        """Inicializa la interfaz de usuario con pestañas (QTabWidget)."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        from PyQt6.QtWidgets import QTabWidget
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        self.tabs.setMovable(False)

        # --- Pestaña Inventario ---
        tab_inventario = QWidget()
        inventario_layout = QVBoxLayout(tab_inventario)
        inventario_layout.setSpacing(10)
        inventario_layout.setContentsMargins(10, 10, 10, 10)
        control_panel = self.crear_panel_control()
        inventario_layout.addWidget(control_panel)
        self.crear_tabla_herrajes(inventario_layout)
        self.tab_inventario = tab_inventario
        self.tabs.addTab(tab_inventario, "Inventario")

        main_layout.addWidget(self.tabs)
        
        # Aplicar estilos después de crear la interfaz
        self.aplicar_estilos()

    def aplicar_estilos(self):
        """Aplica estilos minimalistas y modernos a toda la interfaz."""
        self.setStyleSheet("""
        /* Estilo general del widget */
        QWidget {
            background-color: #fafbfc;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 12px;
        }
        
        /* Pestañas minimalistas */
        QTabWidget::pane {
            border: 1px solid #e1e4e8;
            border-radius: 6px;
            background-color: white;
            margin-top: 2px;
        }
        
        QTabBar::tab {
            background-color: #f6f8fa;
            border: 1px solid #e1e4e8;
            border-bottom: none;
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            font-size: 11px;
            color: #586069;
            min-width: 80px;
        }
        
        QTabBar::tab:selected {
            background-color: white;
            color: #24292e;
            font-weight: 500;
            border-bottom: 2px solid #0366d6;
        }
        """)

    def crear_panel_control(self) -> QGroupBox:
        """Crea el panel de control con búsqueda y acciones."""
        grupo = QGroupBox("Panel de Control")
        layout = QVBoxLayout(grupo)
        layout.setSpacing(10)

        # Fila superior: Búsqueda y filtros
        fila_busqueda = QHBoxLayout()

        # Campo de búsqueda
        self.input_busqueda = QLineEdit()
        self.input_busqueda.setPlaceholderText("Buscar herrajes por código, nombre o tipo...")
        self.input_busqueda.setToolTip("Buscar herrajes por código, nombre, tipo o proveedor")
        self.input_busqueda.setMinimumHeight(35)
        fila_busqueda.addWidget(self.input_busqueda, 2)

        layout.addLayout(fila_busqueda)

        # Fila inferior: Botones de acción
        botones_layout = QHBoxLayout()

        # Crear botones básicos
        self.btn_nuevo = self.crear_boton("+ Nuevo Herraje", "primary")
        self.btn_editar = self.crear_boton("Editar", "secondary")
        self.btn_eliminar = self.crear_boton("Eliminar", "danger")
        self.btn_actualizar = self.crear_boton("Actualizar", "info")
        
        botones_layout.addWidget(self.btn_nuevo)
        botones_layout.addWidget(self.btn_editar)
        botones_layout.addWidget(self.btn_eliminar)
        botones_layout.addWidget(self.btn_actualizar)
        botones_layout.addStretch()

        layout.addLayout(botones_layout)

        return grupo

    def crear_boton(self, texto: str, estilo: str) -> QPushButton:
        """Crea un botón con estilo específico."""
        boton = QPushButton(texto)
        boton.setMinimumHeight(30)

        # Aplicar estilos según el tipo
        if estilo == "primary":
            boton.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            """)
        elif estilo == "danger":
            boton.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            """)

        return boton

    def crear_tabla_herrajes(self, layout: QVBoxLayout):
        """Crea y configura la tabla de herrajes."""
        # Grupo contenedor
        grupo_tabla = QGroupBox("Lista de Herrajes")
        tabla_layout = QVBoxLayout(grupo_tabla)

        # Crear tabla
        self.tabla_herrajes = QTableWidget()
        self.configurar_tabla()
        tabla_layout.addWidget(self.tabla_herrajes)

        # Asignar referencia para exportación
        self.tabla_principal = self.tabla_herrajes

        layout.addWidget(grupo_tabla)

    def configurar_tabla(self):
        """Configura la tabla de herrajes con estilo moderno y robusto."""
        if not self.tabla_herrajes:
            return

        columnas = [
            "Código",
            "Nombre", 
            "Tipo",
            "Stock",
            "Precio Unit.",
            "Estado"
        ]
        self.tabla_herrajes.setColumnCount(len(columnas))
        self.tabla_herrajes.setHorizontalHeaderLabels(columnas)

        # Configurar comportamiento
        self.tabla_herrajes.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla_herrajes.setAlternatingRowColors(True)
        self.tabla_herrajes.setSortingEnabled(True)

    def set_controller(self, controller):
        """Establece el controlador."""
        self.controller = controller

    def mostrar_loading(self, mensaje: str = "Cargando herrajes..."):
        """Muestra indicador de carga."""
        self.loading_manager.show_loading(self, mensaje)

    def ocultar_loading(self):
        """Oculta indicador de carga."""
        self.loading_manager.hide_loading()

    def cargar_herrajes(self, herrajes: List[Dict]):
        """Carga herrajes en la tabla con indicadores visuales."""
        if not self.tabla_herrajes:
            return

        try:
            self.tabla_herrajes.setRowCount(len(herrajes))

            for fila, herraje in enumerate(herrajes):
                # Código
                codigo = str(herraje.get("codigo", ""))
                self.tabla_herrajes.setItem(fila, 0, QTableWidgetItem(codigo))

                # Nombre
                nombre = str(herraje.get("nombre", ""))
                self.tabla_herrajes.setItem(fila, 1, QTableWidgetItem(nombre))

                # Tipo
                tipo = str(herraje.get("tipo", herraje.get("categoria", "")))
                self.tabla_herrajes.setItem(fila, 2, QTableWidgetItem(tipo))

                # Stock con colores
                stock = int(herraje.get("stock_actual", herraje.get("stock", 0)))
                stock_item = QTableWidgetItem(str(stock))

                if stock == 0:
                    stock_item.setBackground(QColor(220, 53, 69))  # Rojo
                    stock_item.setForeground(QColor(255, 255, 255))  # Blanco
                elif stock <= 5:
                    stock_item.setBackground(QColor(255, 193, 7))  # Amarillo
                    stock_item.setForeground(QColor(0, 0, 0))  # Negro
                else:
                    stock_item.setBackground(QColor(40, 167, 69))  # Verde
                    stock_item.setForeground(QColor(255, 255, 255))  # Blanco

                self.tabla_herrajes.setItem(fila, 3, stock_item)

                # Precio
                precio = float(herraje.get("precio_unitario", 0.0))
                self.tabla_herrajes.setItem(fila, 4, QTableWidgetItem(f"${precio:,.2f}"))

                # Estado
                activo = herraje.get("activo", 1)
                estado = "Activo" if activo else "Inactivo"
                self.tabla_herrajes.setItem(fila, 5, QTableWidgetItem(estado))

            self.ocultar_loading()

        except Exception as e:
            self.error_ocurrido.emit(f"Error cargando herrajes: {str(e)}")
            show_error(
                self,
                "Error de datos",
                f"No se pudieron cargar los herrajes: {str(e)}"
            )
            self.ocultar_loading()

    def actualizar_tabla_herrajes(self, herrajes: List[Dict]):
        """Alias para compatibilidad."""
        self.cargar_herrajes(herrajes)

    def _on_dangerous_content(self, field_name: str, content: str):
        """Maneja detección de contenido peligroso."""
        show_warning(
            self,
            "Contenido no permitido",
            f"Se detectó contenido potencialmente peligroso en {field_name}. "
            "Por favor revise su entrada."
        )

        # Limpiar el campo
        if hasattr(self, "input_busqueda") and field_name == "busqueda" and self.input_busqueda:
            self.input_busqueda.clear()

    def exportar_datos(self, formato: str = "excel"):
        """Exporta los datos de herrajes."""
        if self.controller:
            self.mostrar_loading(f"Exportando a {formato.upper()}...")
            self.controller.exportar_herrajes(formato)
        else:
            show_warning(self, "Sin controlador", "El controlador no está disponible.")