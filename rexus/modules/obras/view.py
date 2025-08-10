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

Vista de Obras - Interfaz de gestión de obras y proyectos
"""

import datetime
from typing import Any, Dict, Optional, List

from PyQt6.QtCore import QDate, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QSplitter,
    QStackedWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from rexus.ui.standard_components import StandardComponents
from rexus.ui.style_manager import style_manager
from rexus.ui.components import (
    RexusButton,
    RexusLabel,
    RexusLineEdit,
    RexusComboBox,
    RexusTable
)

# Reemplazar componentes por versiones Rexus
from PyQt6.QtWidgets import QLabel, QLineEdit, QComboBox, QPushButton
QLabel = RexusLabel
QLineEdit = RexusLineEdit
QComboBox = RexusComboBox
QPushButton = RexusButton
from rexus.utils.contextual_error_system import ContextualErrorManager
from rexus.utils.form_validators import FormValidator, FormValidatorManager
from rexus.utils.keyboard_navigation import KeyboardNavigationManager
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric

# Importar sistema moderno de mensajes
from rexus.utils.message_system import show_error, show_success, show_warning

# Importar sistemas globales de mejora UX
from rexus.utils.smart_tooltips import setup_smart_tooltips
from rexus.utils.xss_protection import FormProtector

# Importar componentes estándar
try:
    from rexus.ui.standard_components import StandardComponents as UIStandardComponents
except ImportError:
    print("[WARNING] StandardComponents no disponible")

    # Crear fallback para StandardComponents
    from PyQt6.QtWidgets import QTableWidget
    class StandardComponents:
        @staticmethod
        def create_title(text, layout):
            title_label = RexusLabel(text)
            title_label.setStyleSheet("""
                QLabel {
                    font-size: 11px;
                    font-weight: bold;
                    color: #2c3e50;
                    padding: 6px;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                               stop:0 #3498db, stop:1 #2980b9);
                    color: white;
                    border-radius: 4px;
                    margin-bottom: 6px;
                }
            """)
            layout.addWidget(title_label)

        @staticmethod
        def create_primary_button(text):
            btn = RexusButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3498db;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-size: 11px;
                    font-weight: bold;
                    min-height: 20px;
                }
                QPushButton:hover {
                    background-color: #2980b9;
                }
            """)
            return btn

        @staticmethod
        def create_secondary_button(text):
            btn = QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #95a5a6;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #7f8c8d;
                }
            """)
            return btn

        @staticmethod
        def create_danger_button(text):
            btn = QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            return btn

        @staticmethod
        def create_standard_table():
            table = RexusTable()
            # RexusTable ya tiene estilos integrados
            return table

    style_manager = None


# Import global para testing - permite mocking
try:
    from .model import ObrasModel
except ImportError:
    # Fallback para testing
    ObrasModel = None

from .cronograma_view import CronogramaObrasView


class ObrasView(QWidget):
    obra_agregada = pyqtSignal(dict)
    obra_editada = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        
        # INICIALIZAR SISTEMA DE AUTENTICACIÓN POR DEFECTO PARA DESARROLLO
        self._inicializar_auth_desarrollo()
            
        self.controller = None
        self.model = None  # Agregar referencia directa al modelo
        self.vista_actual = "tabla"  # "tabla" o "cronograma"

        # Inicializar protección XSS
        self.form_protector = FormProtector(self)
        self.form_protector.dangerous_content_detected.connect(
            self._on_dangerous_content
        )

        # Inicializar sistemas globales
        self.contextual_error_manager = ContextualErrorManager()
        self.keyboard_navigation = KeyboardNavigationManager(self)

        self.init_ui()

        # Configurar tooltips inteligentes después de crear la UI
        self.setup_smart_tooltips()
        
        # Aplicar estilo unificado (reemplaza todos los estilos previos)
        self.aplicar_estilos()
        
        # Inicializar modelo y cargar datos después de crear la UI
        self.init_model()
        self.cargar_datos_iniciales_seguro()

    def _inicializar_auth_desarrollo(self):
        """
        Inicializa el sistema de autenticación con permisos por defecto para desarrollo.
        En producción, esto debería ser configurado por el proceso de login.
        """
        try:
            from rexus.core.auth_manager import AuthManager, UserRole
            
            # Si no hay usuario autenticado, establecer permisos de desarrollo
            if AuthManager.current_user_role is None:
                print("[OBRAS] Configurando permisos de desarrollo por defecto")
                AuthManager.set_current_user_role(UserRole.ADMIN)
                AuthManager.current_user = "dev_user"
                
        except Exception as e:
            print(f"[OBRAS] Warning: Error configurando auth de desarrollo: {e}")
            # Continuar sin autenticación para no bloquear desarrollo

    def _crear_vista_acceso_denegado(self):
        """Crea una vista informativa cuando el usuario no tiene permisos"""
        from PyQt6.QtWidgets import QVBoxLayout, QLabel
        from PyQt6.QtCore import Qt
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Mensaje principal
        mensaje = QLabel("[LOCK] Acceso Restringido")
        mensaje.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #dc3545;
                margin-bottom: 20px;
            }
        """)
        mensaje.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Descripción
        descripcion = QLabel(
            "No tiene permisos para acceder al módulo de Obras.\n\n"
            "Contacte al administrador del sistema para solicitar acceso."
        )
        descripcion.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #6c757d;
                text-align: center;
            }
        """)
        descripcion.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(mensaje)
        layout.addWidget(descripcion)

    def apply_high_contrast_style(self):
        """Los componentes Rexus ya tienen estilos integrados."""
        high_contrast_style = """
        /* Tabla de obras */
        QTableWidget {
            background-color: #ffffff;
            color: #000000;
            border: 2px solid #cccccc;
            gridline-color: #dddddd;
            selection-background-color: #0078d4;
            selection-color: #ffffff;
            font-size: 13px;
        }
        
        QTableWidget::item {
            background-color: #ffffff;
            color: #000000;
            border: 1px solid #dddddd;
            padding: 8px;
        }
        
        QTableWidget::item:selected {
            background-color: #0078d4;
            color: #ffffff;
        }
        
        QTableWidget::item:hover {
            background-color: #f0f0f0;
            color: #000000;
        }
        
        /* Headers de la tabla */
        QHeaderView::section {
            background-color: #f8f9fa;
            color: #000000;
            border: 1px solid #cccccc;
            padding: 8px;
            font-weight: bold;
            font-size: 13px;
        }
        
        /* Botones */
        QPushButton {
            background-color: #0078d4;
            color: #ffffff;
            border: 2px solid #0078d4;
            border-radius: 4px;
            padding: 8px 16px;
            font-size: 13px;
            font-weight: bold;
        }
        
        QPushButton:hover {
            background-color: #106ebe;
            border-color: #106ebe;
        }
        
        QPushButton:pressed {
            background-color: #005a9e;
            border-color: #005a9e;
        }
        
        /* Filtros */
        QComboBox, QLineEdit {
            background-color: #ffffff;
            color: #000000;
            border: 2px solid #cccccc;
            border-radius: 4px;
            padding: 6px;
            font-size: 13px;
        }
        
        QComboBox:focus, QLineEdit:focus {
            border-color: #0078d4;
        }
        
        /* Panel de estadísticas */
        QLabel {
            color: #000000;
            font-size: 13px;
        }
        """
        self.setStyleSheet(high_contrast_style)

    def init_model(self):
        """Inicializar el modelo de obras."""
        try:
            from rexus.core.database import get_inventario_connection
            
            print("[OBRAS VIEW] Inicializando modelo...")
            
            # Verificar que ObrasModel esté disponible
            if ObrasModel is None:
                print("[OBRAS VIEW] ObrasModel no disponible")
                self.model = None
                return
            
            # Obtener conexión a la base de datos
            db_conn = get_inventario_connection(auto_connect=True)
            if db_conn and db_conn.connection:
                self.model = ObrasModel(db_conn.connection)
                print("[OBRAS VIEW] Modelo inicializado correctamente")
            else:
                print("[OBRAS VIEW] Error: No se pudo conectar a la base de datos")
                self.model = None
        except Exception as e:
            print(f"[OBRAS VIEW] Error inicializando modelo: {e}")
            import traceback
            traceback.print_exc()
            self.model = None

    def cargar_datos_iniciales(self):
        """Cargar datos iniciales en la tabla."""
        if self.model is None:
            print("[OBRAS VIEW] No hay modelo disponible para cargar datos")
            return
            
        try:
            obras = self.model.obtener_todas_obras()
            if obras:
                # Convertir tuplas a diccionarios usando el mapeo real de la base de datos
                # Índices según la estructura real: 0:id, 1:nombre, 5:cliente, 6:estado, 20:codigo, 21:responsable, etc.
                obras_dict = []
                for obra in obras:
                    obra_dict = {
                        'id': obra[0] if len(obra) > 0 else '',           # id
                        'codigo': obra[20] if len(obra) > 20 else '',     # codigo (índice 20)
                        'nombre': obra[1] if len(obra) > 1 else '',       # nombre (índice 1)
                        'descripcion': obra[26] if len(obra) > 26 else '', # descripcion (índice 26)
                        'cliente': obra[5] if len(obra) > 5 else '',      # cliente (índice 5)
                        'fecha_inicio': obra[22] if len(obra) > 22 else '', # fecha_inicio (índice 22)
                        'fecha_fin_estimada': obra[23] if len(obra) > 23 else '', # fecha_fin_estimada (índice 23)
                        'estado': obra[6] if len(obra) > 6 else '',       # estado (índice 6)
                        'presupuesto_inicial': obra[24] if len(obra) > 24 else 0, # presupuesto_total (índice 24)
                        'responsable': obra[21] if len(obra) > 21 else '' # responsable (índice 21)
                    }
                    obras_dict.append(obra_dict)
                
                self.cargar_obras_en_tabla(obras_dict)
                print(f"[OBRAS VIEW] Cargadas {len(obras_dict)} obras en la tabla")
            else:
                print("[OBRAS VIEW] No hay obras para mostrar")
                self.cargar_obras_en_tabla([])
        except Exception as e:
            print(f"[OBRAS VIEW] Error cargando datos iniciales: {e}")
            import traceback
            traceback.print_exc()
            self.cargar_obras_en_tabla([])

    def actualizar_datos(self):
        """Actualizar datos desde la base de datos."""
        self.cargar_datos_iniciales_seguro()
        
        # Inicializar modelo y cargar datos
        self.init_model()
        self.cargar_datos_iniciales_seguro()

    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        # Layout principal
        layout_principal = QVBoxLayout(self)
        layout_principal.setSpacing(10)
        layout_principal.setContentsMargins(10, 10, 10, 10)

    # Contenedor de vistas con QStackedWidget
        self.stacked_widget = QStackedWidget()

        # Vista de tabla (existente)
        self.vista_tabla = self.crear_vista_tabla()
        self.stacked_widget.addWidget(self.vista_tabla)

        # Vista de cronograma (nueva)
        self.vista_cronograma = CronogramaObrasView()
        self.stacked_widget.addWidget(self.vista_cronograma)

        # Conectar señales del cronograma
        self.vista_cronograma.obra_seleccionada.connect(
            self.on_obra_seleccionada_cronograma
        )

        layout_principal.addWidget(self.stacked_widget)

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
            
            QTabBar::tab:hover:!selected {
                background-color: #e1e4e8;
                color: #24292e;
            }
            
            /* Tablas compactas */
            QTableWidget {
                gridline-color: #e1e4e8;
                selection-background-color: #f1f8ff;
                selection-color: #24292e;
                alternate-background-color: #f6f8fa;
                font-size: 11px;
                border: 1px solid #e1e4e8;
                border-radius: 4px;
            }
            
            QTableWidget::item {
                padding: 4px 8px;
                border: none;
            }
            
            QHeaderView::section {
                background-color: #f6f8fa;
                color: #586069;
                font-weight: 600;
                font-size: 10px;
                border: none;
                border-right: 1px solid #e1e4e8;
                border-bottom: 1px solid #e1e4e8;
                padding: 6px 8px;
            }
            
            /* GroupBox minimalista */
            QGroupBox {
                font-weight: 600;
                font-size: 11px;
                color: #24292e;
                border: 1px solid #e1e4e8;
                border-radius: 6px;
                margin-top: 8px;
                padding-top: 8px;
                background-color: white;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 8px 0 8px;
                background-color: white;
                color: #24292e;
            }
            
            /* Botones minimalistas */
            QPushButton {
                background-color: #f6f8fa;
                border: 1px solid #e1e4e8;
                color: #24292e;
                font-size: 11px;
                font-weight: 500;
                padding: 6px 12px;
                border-radius: 4px;
                min-height: 20px;
            }
            
            QPushButton:hover {
                background-color: #e1e4e8;
                border-color: #d0d7de;
            }
            
            QPushButton:pressed {
                background-color: #d0d7de;
            }
            
            /* Campos de entrada compactos */
            QLineEdit, QComboBox {
                border: 1px solid #e1e4e8;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
                background-color: white;
                min-height: 18px;
            }
            
            QLineEdit:focus, QComboBox:focus {
                border-color: #0366d6;
                outline: none;
            }
            
            /* Labels compactos */
            QLabel {
                color: #24292e;
                font-size: 11px;
            }
            
            /* Scroll bars minimalistas */
            QScrollBar:vertical {
                width: 12px;
                background-color: #f6f8fa;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #d0d7de;
                border-radius: 6px;
                min-height: 20px;
                margin: 2px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #bbb;
            }
        """)

    def setup_smart_tooltips(self):
        """Configura tooltips inteligentes para toda la vista."""
        try:
            setup_smart_tooltips(self)
            print("[INFO] Tooltips inteligentes configurados en módulo Obras")
        except Exception as e:
            print(f"[WARNING] Error configurando tooltips: {e}")

    def crear_vista_tabla(self) -> QWidget:
        """Crea la vista de tabla original."""
        vista_widget = QWidget()
        layout = QVBoxLayout(vista_widget)

        # Splitter horizontal para dividir filtros/estadísticas y tabla
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Panel izquierdo (filtros y estadísticas)
        panel_izquierdo = self.crear_panel_izquierdo()
        splitter.addWidget(panel_izquierdo)

        # Panel derecho (tabla y botones)
        panel_derecho = self.crear_panel_derecho()
        splitter.addWidget(panel_derecho)

        # Configurar proporciones del splitter
        splitter.setStretchFactor(0, 0)  # Panel izquierdo fijo
        splitter.setStretchFactor(1, 1)  # Panel derecho expansible
        splitter.setSizes([300, 800])

        layout.addWidget(splitter)
        return vista_widget

    def crear_panel_izquierdo(self) -> QWidget:
        """Crea el panel izquierdo con filtros y estadísticas."""
        panel = QWidget()
        panel.setMaximumWidth(300)
        layout = QVBoxLayout(panel)

        # Grupo de filtros
        grupo_filtros = self.crear_grupo_filtros()
        layout.addWidget(grupo_filtros)

        # Grupo de estadísticas
        grupo_estadisticas = self.crear_grupo_estadisticas()
        layout.addWidget(grupo_estadisticas)

        layout.addStretch()
        return panel

    def crear_grupo_filtros(self) -> QGroupBox:
        """Crea el grupo de filtros."""
        grupo = QGroupBox("🔍 Filtros")
        layout = QFormLayout(grupo)

        # Filtro por estado
        self.combo_filtro_estado = QComboBox()
        self.combo_filtro_estado.addItems(
            [
                "Todos",
                "PLANIFICACION",
                "EN_PROCESO",
                "PAUSADA",
                "FINALIZADA",
                "CANCELADA",
            ]
        )
        self.combo_filtro_estado.setToolTip(
            "[CHART] Filtrar obras por estado actual\n\nEstados disponibles:\n• PLANIFICACION: Obra en fase de diseño\n• EN_PROCESO: Obra en construcción\n• PAUSADA: Obra temporalmente detenida\n• FINALIZADA: Obra completada\n• CANCELADA: Obra cancelada"
        )
        layout.addRow("Estado:", self.combo_filtro_estado)

        # Filtro por responsable
        self.txt_filtro_responsable = QLineEdit()
        self.txt_filtro_responsable.setPlaceholderText("🔍 Buscar por responsable...")
        self.txt_filtro_responsable.setToolTip(
            "👷 Filtrar por nombre del responsable técnico\n\nEjemplos:\n• María González\n• Ing. Carlos Rodríguez\n• Arq. Ana Sánchez"
        )
        layout.addRow("Responsable:", self.txt_filtro_responsable)

        # Filtro por fecha de inicio
        self.date_filtro_inicio = QDateEdit()
        self.date_filtro_inicio.setDate(QDate.currentDate().addMonths(-1))
        self.date_filtro_inicio.setCalendarPopup(True)
        self.date_filtro_inicio.setToolTip(
            "📅 Filtrar obras desde esta fecha de inicio\n\nMuestra todas las obras que iniciaron en o después de esta fecha"
        )
        layout.addRow("Desde:", self.date_filtro_inicio)

        # Botón aplicar filtros
        self.btn_aplicar_filtros = StandardComponents.create_primary_button(
            "🔍 Aplicar Filtros"
        )
        self.btn_aplicar_filtros.setToolTip(
            "🔍 Aplicar los filtros seleccionados\n\nActualiza la lista de obras según los criterios configurados"
        )
        self.btn_aplicar_filtros.clicked.connect(self.aplicar_filtros)
        layout.addRow("", self.btn_aplicar_filtros)

        return grupo

    def crear_grupo_estadisticas(self) -> QGroupBox:
        """Crea el grupo de estadísticas."""
        grupo = QGroupBox("[CHART] Estadísticas")
        layout = QFormLayout(grupo)

        # Labels para estadísticas
        self.lbl_total_obras = QLabel("0")
        self.lbl_total_obras.setStyleSheet("font-weight: bold; color: #3498db;")
        self.lbl_total_obras.setToolTip(
            "📈 Número total de obras registradas en el sistema"
        )
        layout.addRow("Total Obras:", self.lbl_total_obras)

        self.lbl_obras_activas = QLabel("0")
        self.lbl_obras_activas.setStyleSheet("font-weight: bold; color: #27ae60;")
        self.lbl_obras_activas.setToolTip(
            "🚧 Obras actualmente en proceso de construcción"
        )
        layout.addRow("En Proceso:", self.lbl_obras_activas)

        self.lbl_obras_finalizadas = QLabel("0")
        self.lbl_obras_finalizadas.setStyleSheet("font-weight: bold; color: #2ecc71;")
        self.lbl_obras_finalizadas.setToolTip("[CHECK] Obras completadas exitosamente")
        layout.addRow("Finalizadas:", self.lbl_obras_finalizadas)

        self.lbl_presupuesto_total = QLabel("$0")
        self.lbl_presupuesto_total.setStyleSheet("font-weight: bold; color: #f39c12;")
        self.lbl_presupuesto_total.setToolTip(
            "💰 Suma total de presupuestos de todas las obras"
        )
        layout.addRow("Presupuesto Total:", self.lbl_presupuesto_total)

        return grupo

    def crear_panel_derecho(self) -> QWidget:
        """Crea el panel derecho con tabla y botones."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Barra de herramientas
        toolbar_layout = QHBoxLayout()

        # Botón nueva obra estandarizado
        self.btn_nueva_obra = StandardComponents.create_primary_button("➕ Nueva Obra")
        self.btn_nueva_obra.setToolTip(
            "➕ Crear una nueva obra\n\nAbre el formulario para registrar una nueva obra en el sistema"
        )
        self.btn_nueva_obra.clicked.connect(self.mostrar_formulario_nueva_obra)
        toolbar_layout.addWidget(self.btn_nueva_obra)

        # Botón editar obra estandarizado
        self.btn_editar_obra = StandardComponents.create_secondary_button("✏️ Editar")
        self.btn_editar_obra.setToolTip(
            "✏️ Editar obra seleccionada\n\nPermite modificar los datos de la obra seleccionada en la tabla"
        )
        self.btn_editar_obra.setEnabled(False)
        toolbar_layout.addWidget(self.btn_editar_obra)

        # Botón eliminar obra estandarizado
        self.btn_eliminar_obra = StandardComponents.create_danger_button("🗑️ Eliminar")
        self.btn_eliminar_obra.setToolTip(
            "🗑️ Eliminar obra seleccionada\n\n[WARN] PRECAUCIÓN: Esta acción no se puede deshacer"
        )
        self.btn_eliminar_obra.setEnabled(False)
        toolbar_layout.addWidget(self.btn_eliminar_obra)

        # Botón alternar vista
        self.btn_alternar_vista = StandardComponents.create_secondary_button(
            "📅 Vista Cronograma"
        )
        self.btn_alternar_vista.setToolTip(
            "📅 Cambiar a vista de cronograma\n\nMuestra las obras en formato de cronograma temporal"
        )
        self.btn_alternar_vista.clicked.connect(self.alternar_vista)
        toolbar_layout.addWidget(self.btn_alternar_vista)

        toolbar_layout.addStretch()

        # Botón actualizar estandarizado
        self.btn_actualizar = StandardComponents.create_secondary_button(
            "🔄 Actualizar"
        )
        self.btn_actualizar.setToolTip(
            "🔄 Actualizar lista de obras\n\nRecarga los datos desde la base de datos"
        )
        toolbar_layout.addWidget(self.btn_actualizar)

        layout.addLayout(toolbar_layout)

        # Tabla de obras estandarizada
        self.tabla_obras = StandardComponents.create_standard_table()
        self.tabla_obras.setColumnCount(9)
        self.tabla_obras.setHorizontalHeaderLabels(
            [
                "Código",
                "Nombre",
                "Cliente",
                "Responsable",
                "Fecha Inicio",
                "Fecha Fin",
                "Estado",
                "Presupuesto",
                "Acciones",
            ]
        )

        # Configurar tabla
        header = self.tabla_obras.horizontalHeader()
        if header:
            header.setStretchLastSection(True)
            header.resizeSection(0, 120)  # Código
            header.resizeSection(1, 200)  # Nombre
            header.resizeSection(2, 150)  # Cliente
            header.resizeSection(3, 150)  # Responsable
            header.resizeSection(4, 100)  # Fecha Inicio
            header.resizeSection(5, 100)  # Fecha Fin
            header.resizeSection(6, 100)  # Estado
            header.resizeSection(7, 120)  # Presupuesto

        self.tabla_obras.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.tabla_obras.setAlternatingRowColors(True)

        # Conectar selección
        self.tabla_obras.itemSelectionChanged.connect(self.on_obra_seleccionada)

        layout.addWidget(self.tabla_obras)

        return panel

    def set_controller(self, controller):
        """Configura el controlador y conecta los botones."""
        self.controller = controller
        
        # Conectar botones principales que faltaban conexiones
        if hasattr(controller, 'editar_obra_seleccionada'):
            self.btn_editar_obra.clicked.connect(controller.editar_obra_seleccionada)
        
        if hasattr(controller, 'eliminar_obra_seleccionada'):
            self.btn_eliminar_obra.clicked.connect(controller.eliminar_obra_seleccionada)
        
        if hasattr(controller, 'cargar_obras'):
            self.btn_actualizar.clicked.connect(controller.cargar_obras)
        
        print("[OBRAS VIEW] Controlador configurado y botones conectados")

    def mostrar_tabla(self):
        """Muestra la vista de tabla."""
        try:
            self.stacked_widget.setCurrentIndex(0)
            self.btn_alternar_vista.setText("📅 Vista Cronograma")
            self.vista_actual = "tabla"
            show_success(self, "Vista de tabla", "[CHART] Vista de tabla activada")
        except Exception as e:
            show_error(self, "Error de vista", f"Error cambiando a vista tabla: {e}")

    def mostrar_cronograma(self):
        """Muestra la vista de cronograma."""
        try:
            self.stacked_widget.setCurrentIndex(1)
            self.btn_alternar_vista.setText("[CHART] Vista Tabla")
            self.vista_actual = "cronograma"
            # Cargar datos en el cronograma
            self.actualizar_cronograma()
            show_success(self, "Vista de cronograma", "📅 Vista de cronograma activada")
        except Exception as e:
            show_error(
                self, "Error de vista", f"Error cambiando a vista cronograma: {e}"
            )

    def alternar_vista(self):
        """Alterna entre vista tabla y cronograma."""
        try:
            # Deshabilitar botón temporalmente
            self.btn_alternar_vista.setEnabled(False)
            self.btn_alternar_vista.setText("⏳ Cambiando vista...")

            if self.stacked_widget.currentIndex() == 0:
                self.mostrar_cronograma()
            else:
                self.mostrar_tabla()

        except Exception as e:
            show_error(self, "Error de vista", f"Error alternando vista: {e}")
        finally:
            # Reactivar botón
            self.btn_alternar_vista.setEnabled(True)

    def actualizar_cronograma(self):
        """Actualiza los datos del cronograma."""
        if hasattr(self, "controller") and self.controller:
            try:
                obras = self.controller.model.obtener_todas_obras()
                self.vista_cronograma.cargar_obras(obras)
            except Exception as e:
                show_error(
                    self, "Error de cronograma", f"Error actualizando cronograma: {e}"
                )

    def on_obra_seleccionada_cronograma(self, obra_data: Dict[str, Any]):
        """Maneja la selección de una obra desde el cronograma."""
        print(
            f"[OBRAS VIEW] Obra seleccionada en cronograma: {obra_data.get('codigo', 'Sin código')}"
        )

    def on_obra_seleccionada(self):
        """Maneja la selección de obras en la tabla."""
        seleccionadas = len(self.tabla_obras.selectedItems()) > 0
        self.btn_editar_obra.setEnabled(seleccionadas)
        self.btn_eliminar_obra.setEnabled(seleccionadas)

    def aplicar_filtros(self):
        """Aplica los filtros seleccionados."""
        try:
            # Mostrar estado de carga
            self.btn_aplicar_filtros.setEnabled(False)
            self.btn_aplicar_filtros.setText("⏳ Aplicando...")

            if hasattr(self, "controller") and self.controller:
                filtros = {
                    "estado": self.combo_filtro_estado.currentText(),
                    "responsable": self.txt_filtro_responsable.text().strip(),
                    "fecha_desde": self.date_filtro_inicio.date().toPyDate(),
                }

                # Aplicar filtros a través del controller
                self.controller.aplicar_filtros(filtros)
                show_success(
                    self, "Filtros aplicados", "[CHECK] Filtros aplicados correctamente"
                )

        except Exception as e:
            show_error(self, "Error de filtros", f"Error aplicando filtros: {e}")
        finally:
            # Restaurar botón
            self.btn_aplicar_filtros.setEnabled(True)
            self.btn_aplicar_filtros.setText("🔍 Aplicar Filtros")

    def actualizar_estadisticas(self, estadisticas: Dict[str, Any]):
        """Actualiza las estadísticas mostradas."""
        try:
            self.lbl_total_obras.setText(str(estadisticas.get("total_obras", 0)))
            self.lbl_obras_activas.setText(str(estadisticas.get("obras_activas", 0)))
            self.lbl_obras_finalizadas.setText(
                str(estadisticas.get("obras_finalizadas", 0))
            )

            presupuesto = estadisticas.get("presupuesto_total", 0)
            self.lbl_presupuesto_total.setText(f"${presupuesto:,.2f}")

        except Exception as e:
            show_error(
                self, "Error de estadísticas", f"Error actualizando estadísticas: {e}"
            )

    def set_loading_state(self, loading: bool):
        """Maneja el estado de carga de la interfaz."""
        self.btn_nueva_obra.setEnabled(not loading)
        self.btn_editar_obra.setEnabled(
            not loading and len(self.tabla_obras.selectedItems()) > 0
        )
        self.btn_eliminar_obra.setEnabled(
            not loading and len(self.tabla_obras.selectedItems()) > 0
        )
        self.btn_actualizar.setEnabled(not loading)
        self.btn_aplicar_filtros.setEnabled(not loading)

        if loading:
            self.btn_actualizar.setText("⏳ Cargando...")
        else:
            self.btn_actualizar.setText("🔄 Actualizar")

    def _on_dangerous_content(self, campo, contenido):
        """Maneja detección de contenido peligroso XSS."""
        show_warning(
            self,
            "[WARN] Contenido peligroso",
            f"Contenido potencialmente peligroso detectado en {campo}: {contenido[:50]}...",
        )

    def obtener_obra_seleccionada(self):
        """Obtiene los datos de la obra seleccionada."""
        fila_seleccionada = self.tabla_obras.currentRow()
        if fila_seleccionada >= 0:
            # Obtener datos de la fila seleccionada
            codigo_item = self.tabla_obras.item(fila_seleccionada, 0)
            if codigo_item:
                codigo = codigo_item.text()
                # Buscar la obra completa por código a través del controller
                if hasattr(self, "controller") and self.controller:
                    return self.controller.obtener_obra_por_codigo(codigo)
        return None

    def mostrar_formulario_nueva_obra(self):
        """Muestra el formulario para crear una nueva obra."""
        try:
            dialogo = DialogoObra(self)

            if dialogo.exec():
                datos = dialogo.obtener_datos()
                # Llamar al controller para crear la obra
                if hasattr(self, "controller") and self.controller:
                    self.controller.crear_obra(datos)

        except Exception as e:
            show_error(
                self,
                "Error de formulario",
                f"Error abriendo formulario de nueva obra: {e}",
            )

    def mostrar_formulario_edicion_obra(self, obra_datos):
        """Muestra el formulario para editar una obra existente."""
        try:
            dialogo = DialogoObra(self, obra_datos)

            if dialogo.exec():
                datos = dialogo.obtener_datos()
                # Llamar al controller para actualizar la obra
                if hasattr(self, "controller") and self.controller:
                    obra_id = obra_datos.get("id")
                    if obra_id:
                        self.controller.actualizar_obra(obra_id, datos)

        except Exception as e:
            show_error(
                self,
                "Error de formulario",
                f"Error abriendo formulario de edición: {e}",
            )

    def cargar_obras_en_tabla(self, obras):
        """Carga las obras en la tabla usando el mapper centralizado."""
        try:
            from .data_mapper import ObrasDataMapper, ObrasTableHelper
            
            # Limpiar tabla
            self.tabla_obras.setRowCount(0)
            
            if not obras:
                print("[OBRAS VIEW] No hay obras para mostrar")
                return
            
            # Configurar número de filas
            self.tabla_obras.setRowCount(len(obras))
            
            for fila, obra in enumerate(obras):
                self._cargar_fila_obra(fila, obra)
                
            print(f"[OBRAS VIEW] {len(obras)} obras cargadas en tabla")
            
        except Exception as e:
            print(f"[OBRAS VIEW] Error cargando obras en tabla: {e}")
            import traceback
            traceback.print_exc()
    
    def _cargar_fila_obra(self, fila: int, obra):
        """Carga una fila individual de obra en la tabla."""
        try:
            from .data_mapper import ObrasDataMapper, ObrasTableHelper
            from PyQt6.QtWidgets import QTableWidgetItem
            
            # Convertir obra a diccionario si es necesario
            if isinstance(obra, dict):
                obra_dict = obra
            else:
                # Es tupla de la BD
                obra_dict = ObrasDataMapper.tupla_a_dict(obra)
            
            # Obtener datos formateados para la tabla
            datos_fila = ObrasDataMapper.dict_a_fila_tabla(obra_dict)
            
            # Cargar datos en las columnas
            for columna, dato in enumerate(datos_fila):
                item = QTableWidgetItem(str(dato))
                self.tabla_obras.setItem(fila, columna, item)
            
            # Agregar botón de acción en la última columna
            btn_editar = ObrasTableHelper.crear_boton_accion(
                "Editar", 
                self.editar_obra_desde_tabla, 
                fila
            )
            self.tabla_obras.setCellWidget(fila, ObrasDataMapper.INDICES_TABLA['acciones'], btn_editar)
            
        except Exception as e:
            print(f"[OBRAS VIEW] Error cargando fila {fila}: {e}")
            # Llenar con datos vacíos en caso de error
            for columna in range(8):  # 8 columnas de datos
                self.tabla_obras.setItem(fila, columna, QTableWidgetItem(""))
    def editar_obra_desde_tabla(self, fila):
        """Edita una obra desde la tabla."""
        try:
            # Obtener datos de la fila
            item = self.tabla_obras.item(fila, 0)
            codigo = item.text() if item else ""
            print(f"[OBRAS VIEW] Editando obra con código: {codigo}")
            
            if not codigo:
                show_warning(self, "Error", "No se pudo obtener el código de la obra")
                return
            
            # Buscar la obra por código usando el controlador
            if hasattr(self, "controller") and self.controller:
                try:
                    obra = self.controller.model.obtener_obra_por_codigo(codigo)
                    if obra:
                        # Convertir tupla/datos a diccionario si es necesario
                        if isinstance(obra, tuple):
                            from .data_mapper import ObrasDataMapper
                            obra_dict = ObrasDataMapper.tupla_a_dict(obra)
                        elif isinstance(obra, dict):
                            obra_dict = obra
                        else:
                            show_error(self, "Error", f"Formato de datos no reconocido: {type(obra)}")
                            return
                        
                        # Abrir formulario de edición
                        self.mostrar_formulario_edicion_obra(obra_dict)
                    else:
                        show_error(self, "Error", f"No se encontró la obra con código: {codigo}")
                except Exception as e:
                    show_error(self, "Error", f"Error obteniendo datos de la obra: {str(e)}")
            else:
                show_warning(self, "Sin Controlador", "No hay controlador disponible para editar la obra")
                
        except Exception as e:
            print(f"[OBRAS VIEW] Error editando obra: {e}")
            show_error(self, "Error", f"Error editando obra: {str(e)}")

    def mostrar_detalles_obra(self, obra_id):
        """Muestra los detalles de una obra."""
        try:
            if hasattr(self, "controller") and self.controller:
                obra = self.controller.model.obtener_obra_por_id(obra_id)
                if obra:
                    # Convertir tupla/datos a diccionario si es necesario
                    if isinstance(obra, tuple):
                        from .data_mapper import ObrasDataMapper
                        obra_dict = ObrasDataMapper.tupla_a_dict(obra)
                    elif isinstance(obra, dict):
                        obra_dict = obra
                    else:
                        show_error(self, "Error", f"Formato de datos no reconocido: {type(obra)}")
                        return
                    
                    # Crear diálogo de detalles (solo lectura)
                    dialogo = DetallesObraDialog(self, obra_dict)
                    dialogo.exec()
                else:
                    show_error(self, "Error", f"No se encontró la obra con ID: {obra_id}")
            else:
                show_warning(self, "Sin Controlador", "No hay controlador disponible")
        except Exception as e:
            print(f"[OBRAS VIEW] Error mostrando detalles: {e}")
            show_error(self, "Error", f"Error mostrando detalles: {str(e)}")



    def validar_datos_obra(self, datos_obra: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Valida los datos de una obra antes de procesarlos."""
        try:
            from .data_mapper import ObrasValidator
            return ObrasValidator.validar_obra_dict(datos_obra)
        except Exception as e:
            print(f"[OBRAS VIEW] Error en validación: {e}")
            return False, [f"Error en validación: {str(e)}"]
    
    def mostrar_errores_validacion(self, errores: List[str]):
        """Muestra errores de validación al usuario."""
        try:
            from rexus.utils.message_system import show_error
            mensaje = "Errores encontrados:\n\n" + "\n".join(f"• {error}" for error in errores)
            show_error(self, "[WARN] Datos inválidos", mensaje)
        except Exception as e:
            print(f"[OBRAS VIEW] Error mostrando errores: {e}")
    
    def cargar_datos_iniciales_seguro(self):
        """Versión segura de cargar_datos_iniciales con mejor manejo de errores."""
        try:
            if self.model is None:
                print("[OBRAS VIEW] No hay modelo disponible para cargar datos")
                self.cargar_obras_en_tabla([])
                return
            
            print("[OBRAS VIEW] Cargando datos iniciales...")
            obras = self.model.obtener_todas_obras()
            
            if obras:
                # Usar el mapper para convertir datos
                from .data_mapper import ObrasDataMapper
                obras_dict = ObrasDataMapper.lista_tuplas_a_dicts(obras)
                
                # Validar datos antes de cargar
                obras_validas = []
                for obra in obras_dict:
                    es_valida, errores = self.validar_datos_obra(obra)
                    if es_valida:
                        obras_validas.append(obra)
                    else:
                        print(f"[OBRAS VIEW] Obra inválida ignorada: {obra.get('codigo', 'Sin código')} - {errores}")
                
                self.cargar_obras_en_tabla(obras_validas)
                print(f"[OBRAS VIEW] {len(obras_validas)} obras válidas cargadas de {len(obras)} totales")
            else:
                print("[OBRAS VIEW] No hay obras para mostrar")
                self.cargar_obras_en_tabla([])
                
        except Exception as e:
            print(f"[OBRAS VIEW] Error cargando datos iniciales: {e}")
            import traceback
            traceback.print_exc()
            self.cargar_obras_en_tabla([])


class DialogoObra(QDialog):
    def __init__(self, parent=None, obra_datos: Optional[Dict[str, Any]] = None):
        super().__init__(parent)
        self.obra_datos = obra_datos or {}
        self.es_edicion = bool(obra_datos)

        # Inicializar FormValidatorManager para validaciones
        self.validator_manager = FormValidatorManager()

        self.setWindowTitle("✏️ Editar Obra" if self.es_edicion else "➕ Nueva Obra")
        self.setModal(True)
        self.resize(600, 500)

        self.init_ui()
        self.configurar_validaciones()
        if self.es_edicion:
            self.cargar_datos()

        self._setup_modern_styling()

    def init_ui(self):
        """Inicializa la interfaz del diálogo."""
        layout = QVBoxLayout(self)

        # Formulario principal
        form_layout = QFormLayout()

        # Código (solo para nuevas obras)
        if not self.es_edicion:
            self.txt_codigo = QLineEdit()
            self.txt_codigo.setPlaceholderText("📋 Ej: OBR-2024-001")
            self.txt_codigo.setToolTip(
                "💡 Código único de la obra\n\nFormato sugerido: OBR-YYYY-NNN\nEjemplo: OBR-2024-001"
            )
            form_layout.addRow("📋 Código:", self.txt_codigo)

        # Nombre
        self.txt_nombre = QLineEdit()
        self.txt_nombre.setPlaceholderText("🏗️ Construcción de vivienda familiar")
        self.txt_nombre.setToolTip(
            "🏗️ Nombre descriptivo de la obra\n\nEjemplos:\n• Construcción de vivienda familiar\n• Edificio residencial Torre Norte\n• Remodelación oficinas corporativas"
        )
        form_layout.addRow("🏗️ Nombre:", self.txt_nombre)

        # Cliente
        self.txt_cliente = QLineEdit()
        self.txt_cliente.setPlaceholderText("👤 Juan Pérez García")
        self.txt_cliente.setToolTip(
            "👤 Nombre completo del cliente\n\nIngrese el nombre completo de la persona o empresa contratante"
        )
        form_layout.addRow("👤 Cliente:", self.txt_cliente)

        # Descripción
        self.txt_descripcion = QTextEdit()
        self.txt_descripcion.setMaximumHeight(100)
        self.txt_descripcion.setPlaceholderText(
            "📝 Descripción detallada del proyecto..."
        )
        self.txt_descripcion.setToolTip(
            "📝 Descripción detallada del proyecto\n\nIncluya características principales, materiales, alcance del trabajo, etc."
        )
        form_layout.addRow("📝 Descripción:", self.txt_descripcion)

        # Responsable
        self.txt_responsable = QLineEdit()
        self.txt_responsable.setPlaceholderText("👷 María González (Arquitecta)")
        self.txt_responsable.setToolTip(
            "👷 Responsable técnico de la obra\n\nIncluya nombre y título profesional\nEjemplo: Ing. Carlos Martínez"
        )
        form_layout.addRow("👷 Responsable:", self.txt_responsable)

        # Dirección
        self.txt_direccion = QLineEdit()
        self.txt_direccion.setPlaceholderText("📍 Calle 123 #45-67, Barrio Norte")
        self.txt_direccion.setToolTip(
            "📍 Dirección completa de la obra\n\nIncluya calle, número, barrio/sector y ciudad"
        )
        form_layout.addRow("📍 Dirección:", self.txt_direccion)

        # Teléfono
        self.txt_telefono = QLineEdit()
        self.txt_telefono.setPlaceholderText("📞 +57 300 123 4567")
        self.txt_telefono.setToolTip(
            "📞 Teléfono de contacto\n\nIncluya código de país si es internacional\nEjemplo: +57 300 123 4567"
        )
        form_layout.addRow("📞 Teléfono:", self.txt_telefono)

        # Email
        self.txt_email = QLineEdit()
        self.txt_email.setPlaceholderText("📧 cliente@email.com")
        self.txt_email.setToolTip(
            "📧 Email de contacto del cliente\n\nDebe ser una dirección de correo válida\nEjemplo: cliente@empresa.com"
        )
        form_layout.addRow("📧 Email:", self.txt_email)

        # Fechas
        fecha_layout = QHBoxLayout()

        self.date_inicio = QDateEdit()
        self.date_inicio.setDate(QDate.currentDate())
        self.date_inicio.setCalendarPopup(True)
        self.date_inicio.setToolTip(
            "📅 Fecha de inicio planificada\n\nSeleccione la fecha en que iniciará la obra"
        )
        fecha_layout.addWidget(self.date_inicio)

        fecha_layout.addWidget(QLabel("hasta"))

        self.date_fin = QDateEdit()
        self.date_fin.setDate(QDate.currentDate().addDays(30))
        self.date_fin.setCalendarPopup(True)
        self.date_fin.setToolTip(
            "📅 Fecha de finalización estimada\n\nSeleccione la fecha estimada de terminación"
        )
        fecha_layout.addWidget(self.date_fin)

        form_layout.addRow("📅 Fechas:", fecha_layout)

        # Presupuesto
        self.spin_presupuesto = QDoubleSpinBox()
        self.spin_presupuesto.setRange(0.0, 999999999.99)
        self.spin_presupuesto.setPrefix("$ ")
        self.spin_presupuesto.setDecimals(2)
        self.spin_presupuesto.setToolTip(
            "💰 Presupuesto estimado de la obra\n\nIngrese el valor total estimado sin incluir IVA"
        )
        form_layout.addRow("💰 Presupuesto:", self.spin_presupuesto)

        # Tipo de obra
        self.combo_tipo = QComboBox()
        self.combo_tipo.addItems(
            [
                "Residencial",
                "Comercial",
                "Industrial",
                "Infraestructura",
                "Remodelación",
            ]
        )
        self.combo_tipo.setToolTip(
            "🏢 Tipo de obra\n\nCategorías:\n• Residencial: Viviendas y edificios habitacionales\n• Comercial: Oficinas, locales comerciales\n• Industrial: Fábricas, bodegas\n• Infraestructura: Vías, puentes, obras públicas\n• Remodelación: Ampliaciones y reformas"
        )
        form_layout.addRow("🏢 Tipo:", self.combo_tipo)

        # Prioridad
        self.combo_prioridad = QComboBox()
        self.combo_prioridad.addItems(["BAJA", "MEDIA", "ALTA", "CRITICA"])
        self.combo_prioridad.setToolTip(
            "⚡ Prioridad de la obra\n\nNiveles:\n• BAJA: Sin urgencia\n• MEDIA: Cronograma normal\n• ALTA: Requiere atención preferencial\n• CRITICA: Máxima urgencia"
        )
        form_layout.addRow("⚡ Prioridad:", self.combo_prioridad)

        # Observaciones
        self.txt_observaciones = QTextEdit()
        self.txt_observaciones.setMaximumHeight(80)
        self.txt_observaciones.setPlaceholderText("💭 Observaciones adicionales...")
        self.txt_observaciones.setToolTip(
            "💭 Observaciones adicionales\n\nComentarios especiales, restricciones, consideraciones técnicas, etc."
        )
        form_layout.addRow("💭 Observaciones:", self.txt_observaciones)

        layout.addLayout(form_layout)

        # Botones
        botones = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        botones.accepted.connect(self.validar_y_aceptar)
        botones.rejected.connect(self.reject)
        layout.addWidget(botones)

    def validar_y_aceptar(self):
        """Valida el formulario antes de aceptar."""
        # Validar formulario
        es_valido, errores = self.validator_manager.validar_formulario()

        if not es_valido:
            # Mostrar errores con sistema moderno
            mensajes_error = self.validator_manager.obtener_mensajes_error()
            show_warning(
                self,
                "Errores de validación",
                "Por favor corrige los siguientes errores:\n\n"
                + "\n".join(mensajes_error),
            )
            return

        # Validar fechas
        if self.date_fin.date() <= self.date_inicio.date():
            show_warning(
                self,
                "Error en fechas",
                "[WARN] La fecha de finalización debe ser posterior a la fecha de inicio.",
            )
            return

        # Si todo es válido, aceptar el diálogo
        show_success(self, "Datos validados", "[CHECK] Datos validados correctamente")
        self.accept()

    def _setup_modern_styling(self):
        """Configura el estilizado moderno para el diálogo."""
        try:
            from rexus.utils.form_styles import setup_form_widget

            # Aplicar estilos modernos
            setup_form_widget(self, apply_animations=True)

            # Configurar validación visual en tiempo real
            self._setup_realtime_validation()

        except ImportError:
            print("[WARNING] FormStyleManager no disponible")

    def _setup_realtime_validation(self):
        """Configura validación visual en tiempo real."""
        try:
            # Validación en tiempo real para campos críticos
            if not self.es_edicion:
                self.txt_codigo.textChanged.connect(
                    lambda: self._validate_field_visual(self.txt_codigo, "codigo")
                )

            self.txt_nombre.textChanged.connect(
                lambda: self._validate_field_visual(self.txt_nombre, "nombre")
            )

            self.txt_email.textChanged.connect(
                lambda: self._validate_field_visual(self.txt_email, "email")
            )

        except Exception as e:
            print(f"[WARNING] Error configurando validación en tiempo real: {e}")

    def _validate_field_visual(self, campo, tipo):
        """Valida un campo y actualiza su apariencia visual."""
        try:
            valor = campo.text().strip()
            es_valido = True

            if tipo == "codigo" and not valor:
                es_valido = False
            elif tipo == "nombre" and not valor:
                es_valido = False
            elif tipo == "email" and valor and "@" not in valor:
                es_valido = False

            # Aplicar estilo según validez
            if es_valido:
                campo.setStyleSheet("border: 2px solid #27ae60; border-radius: 4px;")
            else:
                campo.setStyleSheet("border: 2px solid #e74c3c; border-radius: 4px;")

        except Exception as e:
            print(f"[WARNING] Error en validación visual: {e}")

    def obtener_datos(self) -> Dict[str, Any]:
        """Obtiene los datos del formulario."""
        datos = {}

        if not self.es_edicion:
            datos["codigo"] = self.txt_codigo.text().strip()

        datos["nombre"] = self.txt_nombre.text().strip()
        datos["cliente"] = self.txt_cliente.text().strip()
        datos["descripcion"] = self.txt_descripcion.toPlainText().strip()
        datos["responsable"] = self.txt_responsable.text().strip()
        datos["direccion"] = self.txt_direccion.text().strip()
        datos["telefono_contacto"] = self.txt_telefono.text().strip()
        datos["email_contacto"] = self.txt_email.text().strip()

        # Fechas - convertir de QDate a datetime.date
        fecha_inicio_qt = self.date_inicio.date()
        fecha_fin_qt = self.date_fin.date()

        datos["fecha_inicio"] = datetime.date(
            fecha_inicio_qt.year(), fecha_inicio_qt.month(), fecha_inicio_qt.day()
        )
        datos["fecha_fin_estimada"] = datetime.date(
            fecha_fin_qt.year(), fecha_fin_qt.month(), fecha_fin_qt.day()
        )
        datos["presupuesto_total"] = self.spin_presupuesto.value()
        datos["tipo_obra"] = self.combo_tipo.currentText()
        datos["prioridad"] = self.combo_prioridad.currentText()
        datos["observaciones"] = self.txt_observaciones.toPlainText().strip()

        return datos

    def configurar_validaciones(self):
        """Configura las validaciones del formulario."""
        # Código obligatorio (solo para nuevas obras)
        if not self.es_edicion:
            self.validator_manager.agregar_validacion(
                self.txt_codigo, FormValidator.validar_campo_obligatorio, "Código"
            )

        # Nombre obligatorio
        self.validator_manager.agregar_validacion(
            self.txt_nombre, FormValidator.validar_campo_obligatorio, "Nombre"
        )

        # Cliente obligatorio
        self.validator_manager.agregar_validacion(
            self.txt_cliente, FormValidator.validar_campo_obligatorio, "Cliente"
        )

        # Email válido (si se proporciona)
        self.validator_manager.agregar_validacion(
            self.txt_email, FormValidator.validar_email, "Email"
        )

        # Presupuesto mayor a 0
        self.validator_manager.agregar_validacion(
            self.spin_presupuesto,
            lambda campo: campo.value() > 0,
            "El presupuesto debe ser mayor a 0",
        )

    def cargar_datos(self):
        """Carga los datos existentes para edición."""
        if not self.obra_datos:
            return

        try:
            self.txt_nombre.setText(self.obra_datos.get("nombre", ""))
            self.txt_cliente.setText(self.obra_datos.get("cliente", ""))
            self.txt_descripcion.setPlainText(self.obra_datos.get("descripcion", ""))
            self.txt_responsable.setText(self.obra_datos.get("responsable", ""))
            self.txt_direccion.setText(self.obra_datos.get("direccion", ""))
            self.txt_telefono.setText(self.obra_datos.get("telefono_contacto", ""))
            self.txt_email.setText(self.obra_datos.get("email_contacto", ""))

            # Fechas
            if self.obra_datos.get("fecha_inicio"):
                fecha_inicio = self.obra_datos["fecha_inicio"]
                if isinstance(fecha_inicio, str):
                    fecha_inicio = datetime.datetime.strptime(
                        fecha_inicio, "%Y-%m-%d"
                    ).date()
                self.date_inicio.setDate(
                    QDate(fecha_inicio.year, fecha_inicio.month, fecha_inicio.day)
                )

            if self.obra_datos.get("fecha_fin_estimada"):
                fecha_fin = self.obra_datos["fecha_fin_estimada"]
                if isinstance(fecha_fin, str):
                    fecha_fin = datetime.datetime.strptime(fecha_fin, "%Y-%m-%d").date()
                self.date_fin.setDate(
                    QDate(fecha_fin.year, fecha_fin.month, fecha_fin.day)
                )

            # Presupuesto
            self.spin_presupuesto.setValue(
                self.obra_datos.get("presupuesto_total", 0.0)
            )

            # Tipo de obra
            tipo_obra = self.obra_datos.get("tipo_obra", "Residencial")
            index = self.combo_tipo.findText(tipo_obra)
            if index >= 0:
                self.combo_tipo.setCurrentIndex(index)

            # Prioridad
            prioridad = self.obra_datos.get("prioridad", "MEDIA")
            index = self.combo_prioridad.findText(prioridad)
            if index >= 0:
                self.combo_prioridad.setCurrentIndex(index)

            self.txt_observaciones.setPlainText(
                self.obra_datos.get("observaciones", "")
            )

        except Exception as e:
            show_error(self, "Error cargando datos", f"Error cargando datos: {e}")


class DetallesObraDialog(QDialog):
    """Diálogo para mostrar los detalles de una obra (solo lectura)."""
    
    def __init__(self, parent=None, obra_datos: Optional[Dict[str, Any]] = None):
        super().__init__(parent)
        self.obra_datos = obra_datos or {}
        
        self.setWindowTitle(f"🔍 Detalles de Obra - {self.obra_datos.get('nombre', 'Sin nombre')}")
        self.setModal(True)
        self.resize(500, 600)
        
        self.init_ui()
        self.cargar_datos()
        self._setup_readonly_styling()
    
    def init_ui(self):
        """Inicializa la interfaz del diálogo."""
        layout = QVBoxLayout(self)
        
        # Título principal
        titulo = QLabel(f"📋 {self.obra_datos.get('nombre', 'Obra sin nombre')}")
        titulo.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                          stop:0 #3498db, stop:1 #2980b9);
                color: white;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 15px;
            }
        """)
        layout.addWidget(titulo)
        
        # Información principal en formato de solo lectura
        info_layout = QFormLayout()
        
        # Código
        self.lbl_codigo = QLabel()
        self.lbl_codigo.setStyleSheet("font-weight: bold; color: #34495e; padding: 5px;")
        info_layout.addRow("📋 Código:", self.lbl_codigo)
        
        # Cliente
        self.lbl_cliente = QLabel()
        self.lbl_cliente.setStyleSheet("color: #34495e; padding: 5px;")
        info_layout.addRow("👤 Cliente:", self.lbl_cliente)
        
        # Ubicación
        self.lbl_ubicacion = QLabel()
        self.lbl_ubicacion.setStyleSheet("color: #34495e; padding: 5px;")
        info_layout.addRow("📍 Ubicación:", self.lbl_ubicacion)
        
        # Fechas
        fechas_layout = QHBoxLayout()
        self.lbl_fecha_inicio = QLabel()
        self.lbl_fecha_inicio.setStyleSheet("color: #27ae60; font-weight: bold; padding: 5px;")
        fechas_layout.addWidget(self.lbl_fecha_inicio)
        
        fechas_layout.addWidget(QLabel(" → "))
        
        self.lbl_fecha_fin = QLabel()
        self.lbl_fecha_fin.setStyleSheet("color: #e74c3c; font-weight: bold; padding: 5px;")
        fechas_layout.addWidget(self.lbl_fecha_fin)
        fechas_layout.addStretch()
        
        fechas_widget = QWidget()
        fechas_widget.setLayout(fechas_layout)
        info_layout.addRow("📅 Fechas:", fechas_widget)
        
        # Presupuesto
        self.lbl_presupuesto = QLabel()
        self.lbl_presupuesto.setStyleSheet("""
            color: #27ae60; 
            font-weight: bold; 
            font-size: 14px; 
            padding: 8px; 
            background-color: #d5f4e6;
            border-radius: 4px;
        """)
        info_layout.addRow("💰 Presupuesto:", self.lbl_presupuesto)
        
        # Tipo de obra
        self.lbl_tipo = QLabel()
        self.lbl_tipo.setStyleSheet("color: #34495e; padding: 5px;")
        info_layout.addRow("🏢 Tipo:", self.lbl_tipo)
        
        # Prioridad
        self.lbl_prioridad = QLabel()
        info_layout.addRow("⚡ Prioridad:", self.lbl_prioridad)
        
        # Estado
        self.lbl_estado = QLabel()
        info_layout.addRow("[CHART] Estado:", self.lbl_estado)
        
        layout.addLayout(info_layout)
        
        # Observaciones
        obs_label = QLabel("📝 Observaciones:")
        obs_label.setStyleSheet("font-weight: bold; margin-top: 15px;")
        layout.addWidget(obs_label)
        
        self.txt_observaciones = QTextEdit()
        self.txt_observaciones.setReadOnly(True)
        self.txt_observaciones.setMaximumHeight(100)
        self.txt_observaciones.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 10px;
                color: #495057;
            }
        """)
        layout.addWidget(self.txt_observaciones)
        
        # Botones
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        btn_editar = QPushButton("✏️ Editar Obra")
        btn_editar.clicked.connect(self.editar_obra)
        buttons_layout.addWidget(btn_editar)
        
        btn_cerrar = QPushButton("[ERROR] Cerrar")
        btn_cerrar.clicked.connect(self.accept)
        buttons_layout.addWidget(btn_cerrar)
        
        layout.addLayout(buttons_layout)
    
    def cargar_datos(self):
        """Carga los datos de la obra en el formulario."""
        try:
            self.lbl_codigo.setText(self.obra_datos.get('codigo', 'Sin código'))
            self.lbl_cliente.setText(self.obra_datos.get('cliente', 'Sin cliente'))
            self.lbl_ubicacion.setText(self.obra_datos.get('ubicacion', 'Sin ubicación'))
            
            # Fechas
            fecha_inicio = self.obra_datos.get('fecha_inicio', '')
            fecha_fin = self.obra_datos.get('fecha_fin', '')
            self.lbl_fecha_inicio.setText(f"Inicio: {fecha_inicio}")
            self.lbl_fecha_fin.setText(f"Fin: {fecha_fin}")
            
            # Presupuesto
            presupuesto = self.obra_datos.get('presupuesto', 0)
            self.lbl_presupuesto.setText(f"$ {presupuesto:,.2f}")
            
            # Tipo
            self.lbl_tipo.setText(self.obra_datos.get('tipo_obra', 'Sin especificar'))
            
            # Prioridad con colores
            prioridad = self.obra_datos.get('prioridad', 'MEDIA')
            if prioridad == 'ALTA':
                color_style = "color: #e74c3c; font-weight: bold; padding: 5px; background-color: #ffecec; border-radius: 4px;"
            elif prioridad == 'BAJA':
                color_style = "color: #95a5a6; padding: 5px;"
            else:
                color_style = "color: #f39c12; font-weight: bold; padding: 5px; background-color: #fef9e7; border-radius: 4px;"
            
            self.lbl_prioridad.setStyleSheet(color_style)
            self.lbl_prioridad.setText(prioridad)
            
            # Estado con colores
            estado = self.obra_datos.get('estado', 'PLANIFICACION')
            if estado == 'ACTIVA':
                estado_style = "color: #27ae60; font-weight: bold; padding: 5px; background-color: #d5f4e6; border-radius: 4px;"
            elif estado == 'COMPLETADA':
                estado_style = "color: #3498db; font-weight: bold; padding: 5px; background-color: #e3f2fd; border-radius: 4px;"
            elif estado == 'CANCELADA':
                estado_style = "color: #e74c3c; font-weight: bold; padding: 5px; background-color: #ffecec; border-radius: 4px;"
            else:
                estado_style = "color: #f39c12; padding: 5px;"
                
            self.lbl_estado.setStyleSheet(estado_style)
            self.lbl_estado.setText(estado)
            
            # Observaciones
            self.txt_observaciones.setPlainText(self.obra_datos.get('observaciones', 'Sin observaciones'))
            
        except Exception as e:
            show_error(self, "Error", f"Error cargando datos: {str(e)}")
    
    def _setup_readonly_styling(self):
        """Aplica estilos para indicar que es solo lectura."""
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            QLabel {
                font-size: 11px;
                color: #24292e;
            }
        """)
    
    def editar_obra(self):
        """Abre el diálogo de edición para esta obra."""
        try:
            self.accept()  # Cerrar diálogo actual
            
            # Obtener parent que debe ser ObrasView
            parent = self.parent()
            if parent and hasattr(parent, 'mostrar_formulario_edicion_obra'):
                # type: ignore - parent es ObrasView en tiempo de ejecución
                parent.mostrar_formulario_edicion_obra(self.obra_datos)  # type: ignore
        except Exception as e:
            show_error(self, "Error", f"Error abriendo editor: {str(e)}")
