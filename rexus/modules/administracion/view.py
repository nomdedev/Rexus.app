"""
Vista Funcional de Administración - Rexus.app v2.0.0

Vista completa e integrada que conecta con el controlador y submódulos.
Reemplaza la vista genérica con funcionalidad real.
"""

import logging

from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidgetItem,
    QFormLayout, QDialog, QDialogButtonBox, QDoubleSpinBox, QFrame,
    QDateEdit, QGridLayout
)

from rexus.utils.message_system import show_error, show_success, show_warning
from rexus.utils.xss_protection import FormProtector

# Importar componentes del framework UI
from rexus.ui.components.base_components import (
    RexusButton, RexusLabel, RexusLineEdit, RexusComboBox, RexusTable,
    RexusGroupBox, RexusColors
)


class DashboardWidget(QWidget):
    """Widget del dashboard principal con métricas clave."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QGridLayout(self)

        # Tarjetas de métricas
        self.crear_tarjeta_metrica("[USERS] Empleados Activos", "0", 0, 0, layout)
        self.crear_tarjeta_metrica("[MONEY] Balance General",
"$0.00",
            0,
            1,
            layout)
        self.crear_tarjeta_metrica("[CHART] Transacciones Mes",
"0",
            1,
            0,
            layout)
        self.crear_tarjeta_metrica("[WARN] Alertas Pendientes",
"0",
            1,
            1,
            layout)

        # Gráfico de resumen (placeholder)
        grafico_frame = RexusGroupBox("Resumen Financiero")
        grafico_layout = QVBoxLayout(grafico_frame)

        self.grafico_label = RexusLabel("Gráfico de tendencias financieras", "body")
        self.grafico_label.setMinimumHeight(200)
        self.grafico_label.setStyleSheet(f"""
            QLabel {{
                background-color: {RexusColors.BACKGROUND_LIGHT};
                border: 2px dashed {RexusColors.BORDER};
                border-radius: 8px;
                padding: 20px;
                text-align: center;
            }}
        """)
        grafico_layout.addWidget(self.grafico_label)

        layout.addWidget(grafico_frame, 2, 0, 1, 2)

    def crear_tarjeta_metrica(self, titulo, valor, fila, columna, layout):
        """Crea una tarjeta de métrica."""
        tarjeta = RexusGroupBox(titulo)
        tarjeta_layout = QVBoxLayout(tarjeta)

        valor_label = RexusLabel(valor, "title")
        valor_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tarjeta_layout.addWidget(valor_label)

        # Guardar referencia para actualizar
        setattr(self, f"valor_{fila}_{columna}", valor_label)

        layout.addWidget(tarjeta, fila, columna)

    def actualizar_metricas(self, datos):
        """Actualiza las métricas del dashboard."""
        try:
            if hasattr(self, 'valor_0_0'):  # Empleados
                self.valor_0_0.setText(str(datos.get('empleados_activos', 0)))
            if hasattr(self, 'valor_0_1'):  # Balance
                balance = datos.get('balance_actual', 0)
                self.valor_0_1.setText(f"${balance:,.2f}")
            if hasattr(self, 'valor_1_0'):  # Transacciones
                self.valor_1_0.setText(str(datos.get('transacciones_mes', 0)))
            if hasattr(self, 'valor_1_1'):  # Alertas
                alertas = datos.get('alertas_pendientes', 0)
                self.valor_1_1.setText(str(alertas))

        except Exception as e:
            print(f"Error actualizando métricas: {e}")


class ContabilidadWidget(QWidget):
    """Widget de contabilidad integrado."""

    # Señales
    solicitud_crear_asiento = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Panel de controles
        controles_frame = RexusGroupBox("Gestión Contable")
        controles_layout = QHBoxLayout(controles_frame)

        self.btn_nuevo_asiento = RexusButton("[BRIEFCASE] Nuevo Asiento", "primary")
        self.btn_nuevo_asiento.clicked.connect(self.nuevo_asiento_contable)
        controles_layout.addWidget(self.btn_nuevo_asiento)

        self.btn_balance = RexusButton(" Balance General", "secondary")
        self.btn_balance.clicked.connect(self.generar_balance)
        controles_layout.addWidget(self.btn_balance)

        self.btn_reporte = RexusButton("📄 Reportes", "secondary")
        controles_layout.addWidget(self.btn_reporte)

        controles_layout.addStretch()
        layout.addWidget(controles_frame)

        # Tabla de asientos contables
        self.tabla_asientos = RexusTable()
        self.tabla_asientos.setColumnCount(7)
        self.tabla_asientos.setHorizontalHeaderLabels([
            "ID", "Fecha", "Concepto", "Cuenta", "Debe", "Haber", "Estado"
        ])
        layout.addWidget(self.tabla_asientos)

    def nuevo_asiento_contable(self):
        """Abre diálogo para crear nuevo asiento contable."""
        dialog = AsientoContableDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            datos = dialog.obtener_datos()
            self.solicitud_crear_asiento.emit(datos)

    def generar_balance(self):
        """Genera balance general."""
        show_success(self, "Balance", "Generando balance general...")

    def cargar_asientos(self, asientos):
        """Carga asientos en la tabla."""
        self.tabla_asientos.setRowCount(len(asientos))

        for row, asiento in enumerate(asientos):
            self.tabla_asientos.setItem(row,
0,
                QTableWidgetItem(str(asiento.get('id',
                ''))))
            self.tabla_asientos.setItem(row,
1,
                QTableWidgetItem(str(asiento.get('fecha_asiento',
                ''))))
            self.tabla_asientos.setItem(row,
2,
                QTableWidgetItem(str(asiento.get('concepto',
                ''))))
            self.tabla_asientos.setItem(row,
3,
                QTableWidgetItem(str(asiento.get('cuenta_contable',
                ''))))
            self.tabla_asientos.setItem(row, 4,
                QTableWidgetItem(f"${asiento.get('debe', 0):,.2f}"))
            self.tabla_asientos.setItem(row, 5,
                QTableWidgetItem(f"${asiento.get('haber', 0):,.2f}"))
            self.tabla_asientos.setItem(row,
6,
                QTableWidgetItem(str(asiento.get('estado',
                'Activo'))))


class RecursosHumanosWidget(QWidget):
    """Widget de recursos humanos integrado."""

    # Señales
    solicitud_crear_empleado = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Panel de controles
        controles_frame = RexusGroupBox("Gestión de Personal")
        controles_layout = QHBoxLayout(controles_frame)

        self.btn_nuevo_empleado = RexusButton("👤 Nuevo Empleado", "primary")
        self.btn_nuevo_empleado.clicked.connect(self.nuevo_empleado)
        controles_layout.addWidget(self.btn_nuevo_empleado)

        self.btn_nomina = RexusButton("[MONEY] Nómina", "secondary")
        self.btn_nomina.clicked.connect(self.generar_nomina)
        controles_layout.addWidget(self.btn_nomina)

        self.btn_departamentos = RexusButton("🏢 Departamentos", "secondary")
        controles_layout.addWidget(self.btn_departamentos)

        controles_layout.addStretch()
        layout.addWidget(controles_frame)

        # Tabla de empleados
        self.tabla_empleados = RexusTable()
        self.tabla_empleados.setColumnCount(6)
        self.tabla_empleados.setHorizontalHeaderLabels([
            "ID", "Nombre", "Cargo", "Departamento", "Salario", "Estado"
        ])
        layout.addWidget(self.tabla_empleados)

    def nuevo_empleado(self):
        """Abre diálogo para crear nuevo empleado."""
        dialog = EmpleadoDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            datos = dialog.obtener_datos()
            self.solicitud_crear_empleado.emit(datos)

    def generar_nomina(self):
        """Genera nómina de empleados."""
        show_success(self, "Nómina", "Generando nómina...")

    def cargar_empleados(self, empleados):
        """Carga empleados en la tabla."""
        self.tabla_empleados.setRowCount(len(empleados))

        for row, empleado in enumerate(empleados):
            self.tabla_empleados.setItem(row,
0,
                QTableWidgetItem(str(empleado.get('id',
                ''))))
            self.tabla_empleados.setItem(row, 1, QTableWidgetItem(f"{empleado.get('nombre', '')} {empleado.get('apellido', '')}"))
            self.tabla_empleados.setItem(row,
2,
                QTableWidgetItem(str(empleado.get('cargo',
                ''))))
            self.tabla_empleados.setItem(row,
3,
                QTableWidgetItem(str(empleado.get('departamento',
                ''))))
            self.tabla_empleados.setItem(row, 4,
                QTableWidgetItem(f"${empleado.get('salario', 0):,.2f}"))
            self.tabla_empleados.setItem(row,
5,
                QTableWidgetItem(str(empleado.get('estado',
                'Activo'))))


class AdministracionViewFuncional(QWidget):
    """
    Vista funcional principal del módulo de administración.
    Integra dashboard, contabilidad y recursos humanos.
    """

    # Señales principales
    solicitud_datos_dashboard = pyqtSignal()
    solicitud_crear_asiento = pyqtSignal(dict)
    solicitud_crear_empleado = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.controller = None
        self.form_protector = None
        self.init_ui()
        self.init_xss_protection()

    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Título principal
        # Quitar título específico - usar el título del BaseModuleView
        # titulo = RexusLabel("🏢 Administración y Gestión", "title")
        # titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # layout.addWidget(titulo)

        # Pestañas principales
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid {RexusColors.BORDER};
                background-color: {RexusColors.BACKGROUND};
            }}
            QTabBar::tab {{
                background-color: {RexusColors.BACKGROUND_LIGHT};
                padding: 10px 20px;
                margin: 2px;
                border-radius: 4px;
            }}
            QTabBar::tab:selected {{
                background-color: {RexusColors.PRIMARY};
                color: white;
            }}
        """)

        # Pestaña Dashboard
        self.dashboard_widget = DashboardWidget()
        self.tabs.addTab(self.dashboard_widget, "[CHART] Dashboard")

        # Pestaña Contabilidad
        self.contabilidad_widget = ContabilidadWidget()
        self.contabilidad_widget.solicitud_crear_asiento.connect(self.solicitud_crear_asiento)
        self.tabs.addTab(self.contabilidad_widget, "[MONEY] Contabilidad")

        # Pestaña Recursos Humanos
        self.rrhh_widget = RecursosHumanosWidget()
        self.rrhh_widget.solicitud_crear_empleado.connect(self.solicitud_crear_empleado)
        self.tabs.addTab(self.rrhh_widget, "[USERS] Recursos Humanos")

        layout.addWidget(self.tabs)

        # Barra de estado
        self.status_frame = QFrame()
        self.status_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {RexusColors.BACKGROUND_LIGHT};
                border-top: 1px solid {RexusColors.BORDER};
                padding: 5px;
            }}
        """)
        status_layout = QHBoxLayout(self.status_frame)

        self.status_label = RexusLabel("Sistema cargado", "body")
        status_layout.addWidget(self.status_label)

        status_layout.addStretch()

        self.btn_actualizar = RexusButton("🔄 Actualizar", "secondary")
        self.btn_actualizar.clicked.connect(self.actualizar_datos)
        status_layout.addWidget(self.btn_actualizar)

        layout.addWidget(self.status_frame)

        # Cargar datos iniciales
        self.solicitar_datos_iniciales()

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
                padding: 8px 12px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-size: 12px;
                color: #586069;
                min-width: 80px;
                height: 24px;
                max-height: 24px;
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

    def init_xss_protection(self):
        """Inicializa la protección XSS."""
        try:
            self.form_protector = FormProtector()
            logging.info("Protección XSS inicializada en AdministracionViewFuncional")
        except Exception as e:
            logging.error(f"Error inicializando protección XSS: {e}")

    def solicitar_datos_iniciales(self):
        """Solicita los datos iniciales al controlador."""
        self.solicitud_datos_dashboard.emit()

    def actualizar_datos(self):
        """Actualiza todos los datos."""
        self.status_label.setText("🔄 Actualizando datos...")
        self.solicitud_datos_dashboard.emit()

    def actualizar_dashboard(self, datos):
        """Actualiza el dashboard con nuevos datos."""
        try:
            if 'resumen' in datos:
                resumen = datos['resumen']
                metricas = {
                    'empleados_activos': resumen.get('total_empleados', 0),
                    'balance_actual': resumen.get('balance_total', 0),
                    'transacciones_mes': resumen.get('transacciones_mes', 0),
                    'alertas_pendientes': resumen.get('alertas_pendientes', 0)
                }
                self.dashboard_widget.actualizar_metricas(metricas)

            self.status_label.setText("[CHECK] Datos actualizados correctamente")

        except Exception as e:
            logging.error(f"Error actualizando dashboard: {e}")
            self.status_label.setText(f"[ERROR] Error actualizando datos: {str(e)}")

    def cargar_datos_en_tabla(self, datos):
        """Carga datos en las tablas correspondientes."""
        try:
            # Método de compatibilidad con vista genérica
            # Los datos se manejan específicamente en cada widget
            self.status_label.setText("[CHART] Datos cargados en tablas específicas")

        except Exception as e:
            logging.error(f"Error cargando datos en tabla: {e}")

    def nuevo_registro(self):
        """Manejo de nuevo registro - mostrar opciones."""
        show_warning(
            self,
            "Crear Nuevo Registro",
            "Seleccione la pestaña correspondiente:\\n\\n" +
            "• Contabilidad: Para asientos contables\n" +
            "• Recursos Humanos: Para empleados\n\n" +
            "Luego use el botón específico de cada sección."
        )

    def buscar(self, filtros=None):
        """Búsqueda global en el módulo."""
        if not filtros:
            filtros = {'busqueda': ''}

        termino = filtros.get('busqueda', '').strip()
        if termino:
            self.status_label.setText(f"[SEARCH] Buscando: {termino}")
            # La búsqueda específica se maneja en el controlador
        else:
            self.actualizar_datos()

    def mostrar_mensaje(self, titulo, mensaje, tipo="info"):
        """Muestra un mensaje al usuario."""
        if tipo == "error":
            show_error(self, titulo, mensaje)
        elif tipo == "warning":
            show_warning(self, titulo, mensaje)
        else:
            show_success(self, titulo, mensaje)

    def actualizar_status(self, mensaje):
        """Actualiza el mensaje de estado."""
        self.status_label.setText(mensaje)

    def set_controller(self, controller):
        """Establece el controlador para la vista."""
        self.controller = controller

        # Conectar señales del controlador si existen
        if hasattr(controller, 'set_view'):
            controller.set_view(self)


# Diálogos auxiliares

class AsientoContableDialog(QDialog):
    """Diálogo para crear asientos contables."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nuevo Asiento Contable")
        self.setFixedSize(500, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Formulario
        form_layout = QFormLayout()

        self.fecha_edit = QDateEdit(QDate.currentDate())
        form_layout.addRow("Fecha:", self.fecha_edit)

        self.concepto_edit = RexusLineEdit()
        form_layout.addRow("Concepto:", self.concepto_edit)

        self.cuenta_combo = RexusComboBox()
        self.cuenta_combo.addItems([
            "Caja", "Bancos", "Cuentas por Cobrar", "Inventario",
            "Gastos", "Ingresos", "Capital", "Otros"
        ])
        form_layout.addRow("Cuenta:", self.cuenta_combo)

        self.debe_spin = QDoubleSpinBox()
        self.debe_spin.setMaximum(999999.99)
        self.debe_spin.setDecimals(2)
        form_layout.addRow("Debe:", self.debe_spin)

        self.haber_spin = QDoubleSpinBox()
        self.haber_spin.setMaximum(999999.99)
        self.haber_spin.setDecimals(2)
        form_layout.addRow("Haber:", self.haber_spin)

        self.referencia_edit = RexusLineEdit()
        form_layout.addRow("Referencia:", self.referencia_edit)

        layout.addLayout(form_layout)

        # Botones
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def obtener_datos(self):
        """Obtiene los datos del formulario."""
        return {
            'fecha': self.fecha_edit.date().toPython(),
            'concepto': self.concepto_edit.text(),
            'cuenta': self.cuenta_combo.currentText(),
            'debe': self.debe_spin.value(),
            'haber': self.haber_spin.value(),
            'referencia': self.referencia_edit.text()
        }


class EmpleadoDialog(QDialog):
    """Diálogo para crear empleados."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nuevo Empleado")
        self.setFixedSize(500, 500)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Formulario
        form_layout = QFormLayout()

        self.nombre_edit = RexusLineEdit()
        form_layout.addRow("Nombre:", self.nombre_edit)

        self.apellido_edit = RexusLineEdit()
        form_layout.addRow("Apellido:", self.apellido_edit)

        self.dni_edit = RexusLineEdit()
        form_layout.addRow("DNI:", self.dni_edit)

        self.email_edit = RexusLineEdit()
        form_layout.addRow("Email:", self.email_edit)

        self.telefono_edit = RexusLineEdit()
        form_layout.addRow("Teléfono:", self.telefono_edit)

        self.cargo_combo = RexusComboBox()
        self.cargo_combo.addItems([
            "Gerente", "Supervisor", "Empleado", "Técnico",
            "Administrador", "Contador", "Otros"
        ])
        form_layout.addRow("Cargo:", self.cargo_combo)

        self.salario_spin = QDoubleSpinBox()
        self.salario_spin.setMaximum(9999999.99)
        self.salario_spin.setDecimals(2)
        form_layout.addRow("Salario:", self.salario_spin)

        self.fecha_ingreso_edit = QDateEdit(QDate.currentDate())
        form_layout.addRow("Fecha Ingreso:", self.fecha_ingreso_edit)

        layout.addLayout(form_layout)

        # Botones
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def obtener_datos(self):
        """Obtiene los datos del formulario."""
        return {
            'nombre': self.nombre_edit.text(),
            'apellidos': self.apellido_edit.text(),
            'dni': self.dni_edit.text(),
            'email': self.email_edit.text(),
            'telefono': self.telefono_edit.text(),
            'cargo': self.cargo_combo.currentText(),
            'salario': self.salario_spin.value(),
            'fecha_ingreso': self.fecha_ingreso_edit.date().toPython()
        }


# Alias para compatibilidad con el sistema de módulos existente
AdministracionView = AdministracionViewFuncional