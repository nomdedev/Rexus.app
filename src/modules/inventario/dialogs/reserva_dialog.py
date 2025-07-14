"""
Diálogo para crear reservas de material por obra.
"""

from datetime import datetime
from typing import Dict, Optional

from PyQt6.QtCore import QDate, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
)


class ReservaDialog(QDialog):
    """Diálogo para crear una nueva reserva de material."""

    def __init__(self, parent=None, obra_id=None, productos=None):
        super().__init__(parent)
        self.obra_id = obra_id
        self.productos = productos or []
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz del diálogo."""
        self.setWindowTitle("📋 Nueva Reserva de Material")
        self.setModal(True)
        self.setMinimumSize(600, 500)

        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Título
        title_label = QLabel("📋 Nueva Reserva de Material")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        main_layout.addWidget(title_label)

        # Información de la obra
        self.create_obra_info()
        main_layout.addWidget(self.obra_info_group)

        # Datos del producto
        self.create_producto_form()
        main_layout.addWidget(self.producto_form_group)

        # Datos de la reserva
        self.create_reserva_form()
        main_layout.addWidget(self.reserva_form_group)

        # Botones
        self.create_buttons()
        main_layout.addLayout(self.buttons_layout)

        # Aplicar estilo
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                font-family: 'Segoe UI', 'Tahoma', 'Geneva', 'Verdana', sans-serif;
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
                padding: 0 5px 0 5px;
                color: #2c3e50;
            }
            QLabel {
                color: #34495e;
                font-size: 12px;
            }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
                background-color: white;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QTextEdit:focus {
                border: 2px solid #3498db;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                border: none;
                border-radius: 6px;
                color: white;
                padding: 12px 24px;
                font-size: 13px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5dade2, stop:1 #3498db);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2980b9, stop:1 #1f4e79);
            }
            QPushButton#cancelar {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #95a5a6, stop:1 #7f8c8d);
            }
            QPushButton#cancelar:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #b2bec3, stop:1 #95a5a6);
            }
        """)

    def create_obra_info(self):
        """Crea el grupo de información de la obra."""
        self.obra_info_group = QGroupBox("🏗️ Información de la Obra")
        layout = QFormLayout(self.obra_info_group)

        # Nombre de la obra (solo lectura)
        self.obra_nombre_label = QLabel("Cargando...")
        self.obra_nombre_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        layout.addRow("Obra:", self.obra_nombre_label)

        # Responsable
        self.responsable_input = QLineEdit()
        self.responsable_input.setPlaceholderText("Nombre del responsable de la obra")
        layout.addRow("Responsable:", self.responsable_input)

    def create_producto_form(self):
        """Crea el formulario de selección de producto."""
        self.producto_form_group = QGroupBox("📦 Selección de Producto")
        layout = QFormLayout(self.producto_form_group)

        # Selector de producto
        self.producto_combo = QComboBox()
        self.producto_combo.addItem("Seleccionar producto...")
        self.producto_combo.currentIndexChanged.connect(self.on_producto_changed)
        layout.addRow("Producto:", self.producto_combo)

        # Información del producto seleccionado
        self.producto_info_layout = QVBoxLayout()

        # Código del producto
        self.codigo_label = QLabel("-")
        self.codigo_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        layout.addRow("Código:", self.codigo_label)

        # Stock disponible
        self.stock_label = QLabel("-")
        self.stock_label.setStyleSheet("font-weight: bold; color: #27ae60;")
        layout.addRow("Stock Disponible:", self.stock_label)

        # Precio unitario
        self.precio_label = QLabel("-")
        self.precio_label.setStyleSheet("font-weight: bold; color: #e74c3c;")
        layout.addRow("Precio Unitario:", self.precio_label)

        # Unidad de medida
        self.unidad_label = QLabel("-")
        layout.addRow("Unidad:", self.unidad_label)

    def create_reserva_form(self):
        """Crea el formulario de datos de la reserva."""
        self.reserva_form_group = QGroupBox("📋 Datos de la Reserva")
        layout = QFormLayout(self.reserva_form_group)

        # Cantidad a reservar
        self.cantidad_input = QSpinBox()
        self.cantidad_input.setMinimum(1)
        self.cantidad_input.setMaximum(9999999)
        self.cantidad_input.setValue(1)
        self.cantidad_input.valueChanged.connect(self.calcular_valor_total)
        layout.addRow("Cantidad:", self.cantidad_input)

        # Fecha de la reserva
        self.fecha_input = QDateEdit()
        self.fecha_input.setDate(QDate.currentDate())
        self.fecha_input.setCalendarPopup(True)
        layout.addRow("Fecha Reserva:", self.fecha_input)

        # Fecha estimada de uso
        self.fecha_uso_input = QDateEdit()
        self.fecha_uso_input.setDate(QDate.currentDate().addDays(7))
        self.fecha_uso_input.setCalendarPopup(True)
        layout.addRow("Fecha Est. Uso:", self.fecha_uso_input)

        # Prioridad
        self.prioridad_combo = QComboBox()
        self.prioridad_combo.addItems(["BAJA", "MEDIA", "ALTA", "URGENTE"])
        self.prioridad_combo.setCurrentText("MEDIA")
        layout.addRow("Prioridad:", self.prioridad_combo)

        # Valor total
        self.valor_total_label = QLabel("$0.00")
        self.valor_total_label.setStyleSheet(
            "font-weight: bold; color: #e74c3c; font-size: 14px;"
        )
        layout.addRow("Valor Total:", self.valor_total_label)

        # Observaciones
        self.observaciones_input = QTextEdit()
        self.observaciones_input.setMaximumHeight(80)
        self.observaciones_input.setPlaceholderText(
            "Observaciones adicionales sobre la reserva..."
        )
        layout.addRow("Observaciones:", self.observaciones_input)

    def create_buttons(self):
        """Crea los botones del diálogo."""
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.addStretch()

        # Botón cancelar
        self.cancelar_btn = QPushButton("❌ Cancelar")
        self.cancelar_btn.setObjectName("cancelar")
        self.cancelar_btn.clicked.connect(self.reject)
        self.buttons_layout.addWidget(self.cancelar_btn)

        # Botón aceptar
        self.aceptar_btn = QPushButton("✅ Crear Reserva")
        self.aceptar_btn.clicked.connect(self.accept_reserva)
        self.buttons_layout.addWidget(self.aceptar_btn)

    def cargar_productos(self, productos):
        """Carga los productos disponibles en el combo."""
        self.producto_combo.clear()
        self.producto_combo.addItem("Seleccionar producto...")

        for producto in productos:
            texto = f"{producto['codigo']} - {producto['descripcion']}"
            self.producto_combo.addItem(texto, producto)

    def cargar_info_obra(self, obra_info):
        """Carga la información de la obra."""
        if obra_info:
            self.obra_nombre_label.setText(
                f"{obra_info['codigo']} - {obra_info['nombre']}"
            )

    def on_producto_changed(self):
        """Maneja el cambio de producto seleccionado."""
        if self.producto_combo.currentIndex() > 0:
            producto = self.producto_combo.currentData()
            if producto:
                self.codigo_label.setText(producto["codigo"])
                self.stock_label.setText(str(producto.get("stock_disponible", 0)))
                self.precio_label.setText(
                    f"${producto.get('precio_unitario', 0.0):.2f}"
                )
                self.unidad_label.setText(producto.get("unidad_medida", ""))

                # Actualizar límite de cantidad
                stock_disponible = producto.get("stock_disponible", 0)
                self.cantidad_input.setMaximum(stock_disponible)

                # Calcular valor total
                self.calcular_valor_total()
        else:
            self.codigo_label.setText("-")
            self.stock_label.setText("-")
            self.precio_label.setText("-")
            self.unidad_label.setText("-")
            self.valor_total_label.setText("$0.00")

    def calcular_valor_total(self):
        """Calcula el valor total de la reserva."""
        if self.producto_combo.currentIndex() > 0:
            producto = self.producto_combo.currentData()
            if producto:
                cantidad = self.cantidad_input.value()
                precio = producto.get("precio_unitario", 0.0)
                total = cantidad * precio
                self.valor_total_label.setText(f"${total:.2f}")

    def accept_reserva(self):
        """Valida y acepta la reserva."""
        # Validaciones
        if self.producto_combo.currentIndex() <= 0:
            QMessageBox.warning(self, "Error", "Debe seleccionar un producto.")
            return

        if not self.responsable_input.text().strip():
            QMessageBox.warning(self, "Error", "Debe especificar un responsable.")
            return

        if self.cantidad_input.value() <= 0:
            QMessageBox.warning(self, "Error", "La cantidad debe ser mayor a 0.")
            return

        producto = self.producto_combo.currentData()
        if self.cantidad_input.value() > producto.get("stock_disponible", 0):
            QMessageBox.warning(
                self, "Error", "La cantidad solicitada excede el stock disponible."
            )
            return

        # Confirmar reserva
        respuesta = QMessageBox.question(
            self,
            "Confirmar Reserva",
            f"¿Confirmar la reserva de {self.cantidad_input.value()} {producto['unidad_medida']} "
            f"de {producto['descripcion']} por un valor de {self.valor_total_label.text()}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if respuesta == QMessageBox.StandardButton.Yes:
            self.accept()

    def get_reserva_data(self) -> Dict:
        """Obtiene los datos de la reserva."""
        producto = self.producto_combo.currentData()

        return {
            "obra_id": self.obra_id,
            "producto_id": producto["id"],
            "cantidad": self.cantidad_input.value(),
            "fecha_reserva": self.fecha_input.date().toPython(),
            "fecha_uso_estimada": self.fecha_uso_input.date().toPython(),
            "prioridad": self.prioridad_combo.currentText(),
            "responsable": self.responsable_input.text().strip(),
            "observaciones": self.observaciones_input.toPlainText().strip(),
            "valor_unitario": producto.get("precio_unitario", 0.0),
            "valor_total": self.cantidad_input.value()
            * producto.get("precio_unitario", 0.0),
        }
