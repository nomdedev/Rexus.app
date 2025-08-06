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
"""

"""
DiÃ¡logos faltantes para el mÃ³dulo de inventario
Implementaciones temporales para resolver errores de compilaciÃ³n
"""

from typing import Dict, Any, Optional
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit,
    QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QWidget, QMessageBox,
    QGroupBox, QHeaderView, QScrollArea
)

# Importar validadores si estÃ¡n disponibles
try:
    from rexus.utils.form_validators import FormValidator, FormValidatorManager
    VALIDATORS_AVAILABLE = True
except ImportError:
    print("[INFO] Form validators not available, using basic validation")
    VALIDATORS_AVAILABLE = False


class DialogoEditarProducto(QDialog):
    """DiÃ¡logo para editar un producto existente"""
    
    def __init__(self, parent=None, producto=None):
        super().__init__(parent)
        self.producto = producto or {}
        self.setWindowTitle("Editar Producto")
        self.setModal(True)
        self.setFixedSize(500, 650)
        self.init_ui()
        self.cargar_datos_producto()
        
    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout(self)
        
        # TÃ­tulo
        title_label = QLabel("âï¸ Editar Producto")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                margin: 10px;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 8px;
            }
        """)
        layout.addWidget(title_label)
        
        # Formulario en scroll area
        scroll_area = QScrollArea()
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        
        # Campos del formulario
        self.codigo_input = QLineEdit()
        self.codigo_input.setPlaceholderText("CÃ³digo del producto")
        form_layout.addRow("CÃ³digo:", self.codigo_input)
        
        self.descripcion_input = QLineEdit()
        self.descripcion_input.setPlaceholderText("DescripciÃ³n del producto")
        form_layout.addRow("DescripciÃ³n:", self.descripcion_input)
        
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["Marco", "Vidrio", "Herraje", "Accesorio", "Sellador"])
        form_layout.addRow("Tipo:", self.tipo_combo)
        
        self.acabado_combo = QComboBox()
        self.acabado_combo.addItems(["Natural", "Blanco", "Negro", "Bronce", "Cromado"])
        form_layout.addRow("Acabado:", self.acabado_combo)
        
        self.cantidad_input = QSpinBox()
        self.cantidad_input.setRange(0, 999999)
        form_layout.addRow("Cantidad:", self.cantidad_input)
        
        self.precio_input = QDoubleSpinBox()
        self.precio_input.setRange(0.01, 999999.99)
        self.precio_input.setDecimals(2)
        self.precio_input.setPrefix("$ ")
        form_layout.addRow("Precio:", self.precio_input)
        
        self.unidad_combo = QComboBox()
        self.unidad_combo.addItems(["UN", "MT", "M2", "KG", "LT"])
        form_layout.addRow("Unidad:", self.unidad_combo)
        
        self.proveedor_input = QLineEdit()
        self.proveedor_input.setPlaceholderText("Nombre del proveedor")
        form_layout.addRow("Proveedor:", self.proveedor_input)
        
        self.ubicacion_input = QLineEdit()
        self.ubicacion_input.setPlaceholderText("UbicaciÃ³n en almacÃ©n")
        form_layout.addRow("UbicaciÃ³n:", self.ubicacion_input)
        
        self.observaciones_input = QTextEdit()
        self.observaciones_input.setMaximumHeight(80)
        self.observaciones_input.setPlaceholderText("Observaciones adicionales")
        form_layout.addRow("Observaciones:", self.observaciones_input)
        
        scroll_area.setWidget(form_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
        
        # Botones
        button_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("â Cancelar")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = QPushButton("â Actualizar")
        self.save_btn.clicked.connect(self.validar_y_guardar)
        
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.save_btn)
        layout.addLayout(button_layout)
        
    def cargar_datos_producto(self):
        """Carga los datos del producto en el formulario"""
        if not self.producto:
            return
            
        self.codigo_input.setText(str(self.producto.get("codigo", "")))
        self.descripcion_input.setText(str(self.producto.get("descripcion", "")))
        
        # Tipo/categorÃ­a
        tipo = str(self.producto.get("tipo", ""))
        if tipo:
            index = self.tipo_combo.findText(tipo)
            if index >= 0:
                self.tipo_combo.setCurrentIndex(index)
                
        # Acabado
        acabado = str(self.producto.get("acabado", ""))
        if acabado:
            index = self.acabado_combo.findText(acabado)
            if index >= 0:
                self.acabado_combo.setCurrentIndex(index)
                
        self.cantidad_input.setValue(int(self.producto.get("cantidad", 0)))
        self.precio_input.setValue(float(self.producto.get("precio_unitario", 0.0)))
        
        # Unidad
        unidad = str(self.producto.get("unidad_medida", "UN"))
        index = self.unidad_combo.findText(unidad)
        if index >= 0:
            self.unidad_combo.setCurrentIndex(index)
            
        self.proveedor_input.setText(str(self.producto.get("proveedor", "")))
        self.ubicacion_input.setText(str(self.producto.get("ubicacion", "")))
        self.observaciones_input.setPlainText(str(self.producto.get("observaciones", "")))
        
    def validar_y_guardar(self):
        """Valida los datos y guarda"""
        # Validaciones bÃ¡sicas
        if not self.codigo_input.text().strip():
            QMessageBox.warning(self, "Error", "El cÃ³digo es obligatorio")
            return
            
        if not self.descripcion_input.text().strip():
            QMessageBox.warning(self, "Error", "La descripciÃ³n es obligatoria")
            return
            
        if self.precio_input.value() <= 0:
            QMessageBox.warning(self, "Error", "El precio debe ser mayor a 0")
            return
            
        self.accept()
        
    def obtener_datos(self):
        """Obtiene los datos del formulario"""
        return {
            "codigo": self.codigo_input.text().strip().upper(),
            "descripcion": self.descripcion_input.text().strip(),
            "tipo": self.tipo_combo.currentText(),
            "acabado": self.acabado_combo.currentText(),
            "cantidad": self.cantidad_input.value(),
            "precio_unitario": self.precio_input.value(),
            "unidad_medida": self.unidad_combo.currentText(),
            "proveedor": self.proveedor_input.text().strip(),
            "ubicacion": self.ubicacion_input.text().strip(),
            "observaciones": self.observaciones_input.toPlainText().strip(),
        }


class DialogoMovimientoInventario(QDialog):
    """DiÃ¡logo para registrar movimientos de inventario"""
    
    def __init__(self, parent=None, producto=None):
        super().__init__(parent)
        self.producto = producto or {}
        self.setWindowTitle("Registrar Movimiento")
        self.setModal(True)
        self.setFixedSize(450, 500)
        self.init_ui()
        
    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout(self)
        
        # TÃ­tulo
        title_label = QLabel("ð¦ Registrar Movimiento de Inventario")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                margin: 10px;
                padding: 10px;
                background-color: #e8f4fd;
                border-radius: 8px;
            }
        """)
        layout.addWidget(title_label)
        
        # InformaciÃ³n del producto
        if self.producto:
            info_group = QGroupBox("InformaciÃ³n del Producto")
            info_layout = QFormLayout(info_group)
            
            info_layout.addRow("CÃ³digo:", QLabel(str(self.producto.get("codigo", "N/A"))))
            info_layout.addRow("DescripciÃ³n:", QLabel(str(self.producto.get("descripcion", "N/A"))))
            info_layout.addRow("Stock Actual:", QLabel(str(self.producto.get("stock_actual", 0))))
            
            layout.addWidget(info_group)
        
        # Formulario de movimiento
        form_layout = QFormLayout()
        
        # Tipo de movimiento
        self.tipo_movimiento_combo = QComboBox()
        self.tipo_movimiento_combo.addItems([
            "ENTRADA", "SALIDA", "AJUSTE_POSITIVO", "AJUSTE_NEGATIVO", 
            "TRANSFERENCIA", "DEVOLUCION"
        ])
        form_layout.addRow("Tipo de Movimiento:", self.tipo_movimiento_combo)
        
        # Cantidad
        self.cantidad_input = QSpinBox()
        self.cantidad_input.setRange(1, 999999)
        self.cantidad_input.setValue(1)
        form_layout.addRow("Cantidad:", self.cantidad_input)
        
        # Motivo/RazÃ³n
        self.motivo_input = QLineEdit()
        self.motivo_input.setPlaceholderText("RazÃ³n del movimiento")
        form_layout.addRow("Motivo:", self.motivo_input)
        
        # Fecha
        self.fecha_input = QDateEdit()
        self.fecha_input.setDate(QDate.currentDate())
        self.fecha_input.setCalendarPopup(True)
        form_layout.addRow("Fecha:", self.fecha_input)
        
        # Observaciones
        self.observaciones_input = QTextEdit()
        self.observaciones_input.setMaximumHeight(80)
        self.observaciones_input.setPlaceholderText("Observaciones del movimiento")
        form_layout.addRow("Observaciones:", self.observaciones_input)
        
        layout.addLayout(form_layout)
        
        # Botones
        button_layout = QHBoxLayout()
        
        self.cancel_btn = QPushButton("â Cancelar")
        self.cancel_btn.clicked.connect(self.reject)
        
        self.save_btn = QPushButton("â Registrar Movimiento")
        self.save_btn.clicked.connect(self.validar_y_guardar)
        
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.save_btn)
        layout.addLayout(button_layout)
        
    def validar_y_guardar(self):
        """Valida y guarda el movimiento"""
        if not self.motivo_input.text().strip():
            QMessageBox.warning(self, "Error", "El motivo es obligatorio")
            return
            
        if self.cantidad_input.value() <= 0:
            QMessageBox.warning(self, "Error", "La cantidad debe ser mayor a 0")
            return
            
        # Validar stock suficiente para salidas
        tipo_mov = self.tipo_movimiento_combo.currentText()
        if tipo_mov in ["SALIDA", "AJUSTE_NEGATIVO"]:
            stock_actual = self.producto.get("stock_actual", 0)
            if self.cantidad_input.value() > stock_actual:
                QMessageBox.warning(
                    self, "Error", 
                    f"Stock insuficiente. Stock actual: {stock_actual}"
                )
                return
                
        self.accept()
        
    def obtener_datos(self):
        """Obtiene los datos del movimiento"""
        return {
            "producto_id": self.producto.get("id"),
            "tipo_movimiento": self.tipo_movimiento_combo.currentText(),
            "cantidad": self.cantidad_input.value(),
            "motivo": self.motivo_input.text().strip(),
            "fecha": self.fecha_input.date().toString("yyyy-MM-dd"),
            "observaciones": self.observaciones_input.toPlainText().strip(),
        }


class DialogoHistorialProducto(QDialog):
    """DiÃ¡logo para mostrar el historial de movimientos de un producto"""
    
    def __init__(self, parent=None, producto=None):
        super().__init__(parent)
        self.producto = producto or {}
        self.setWindowTitle(f"Historial - {self.producto.get('codigo', 'Producto')}")
        self.setModal(True)
        self.resize(800, 600)
        self.init_ui()
        self.cargar_historial()
        
    def init_ui(self):
        """Inicializa la interfaz"""
        layout = QVBoxLayout(self)
        
        # InformaciÃ³n del producto
        info_group = QGroupBox("ð¦ InformaciÃ³n del Producto")
        info_layout = QFormLayout(info_group)
        
        info_layout.addRow("CÃ³digo:", QLabel(str(self.producto.get("codigo", "N/A"))))
        info_layout.addRow("DescripciÃ³n:", QLabel(str(self.producto.get("descripcion", "N/A"))))
        info_layout.addRow("Stock Actual:", QLabel(str(self.producto.get("stock_actual", 0))))
        info_layout.addRow("CategorÃ­a:", QLabel(str(self.producto.get("categoria", "N/A"))))
        
        layout.addWidget(info_group)
        
        # Tabla de historial
        historial_group = QGroupBox("ð Historial de Movimientos")
        historial_layout = QVBoxLayout(historial_group)
        
        self.tabla_historial = QTableWidget()
        self.tabla_historial.setColumnCount(6)
        self.tabla_historial.setHorizontalHeaderLabels([
            "Fecha", "Tipo", "Cantidad", "Stock Resultante", "Motivo", "Usuario"
        ])
        
        # Configurar tabla
        header = self.tabla_historial.horizontalHeader()
        if header:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            
        self.tabla_historial.setAlternatingRowColors(True)
        self.tabla_historial.setStyleSheet("""
            QTableWidget {
                gridline-color: #ecf0f1;
                background-color: white;
                alternate-background-color: #f8f9fa;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 8px;
                font-weight: bold;
            }
        """)
        
        historial_layout.addWidget(self.tabla_historial)
        layout.addWidget(historial_group)
        
        # BotÃ³n cerrar
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.close_btn = QPushButton("â Cerrar")
        self.close_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
    def cargar_historial(self):
        """Carga el historial de movimientos (simulado)"""
        # Datos de ejemplo - en implementaciÃ³n real vendrÃ­a del controlador
        movimientos_ejemplo = [
            {
                "fecha": "2024-01-15",
                "tipo": "ENTRADA",
                "cantidad": 100,
                "stock_resultante": 100,
                "motivo": "Compra inicial",
                "usuario": "admin"
            },
            {
                "fecha": "2024-01-20",
                "tipo": "SALIDA", 
                "cantidad": 25,
                "stock_resultante": 75,
                "motivo": "Venta obra ABC",
                "usuario": "vendedor1"
            },
            {
                "fecha": "2024-01-25",
                "tipo": "AJUSTE_POSITIVO",
                "cantidad": 5,
                "stock_resultante": 80,
                "motivo": "CorrecciÃ³n de inventario",
                "usuario": "supervisor"
            }
        ]
        
        self.tabla_historial.setRowCount(len(movimientos_ejemplo))
        
        for row, mov in enumerate(movimientos_ejemplo):
            items = [
                mov["fecha"],
                mov["tipo"], 
                str(mov["cantidad"]),
                str(mov["stock_resultante"]),
                mov["motivo"],
                mov["usuario"]
            ]
            
            for col, item in enumerate(items):
                table_item = QTableWidgetItem(str(item))
                
                # Colorear segÃºn tipo de movimiento
                if col == 1:  # Columna tipo
                    if item == "ENTRADA":
                        table_item.setBackground(Qt.GlobalColor.lightGreen)
                    elif item == "SALIDA":
                        table_item.setBackground(Qt.GlobalColor.lightCoral)
                    elif "AJUSTE" in item:
                        table_item.setBackground(Qt.GlobalColor.lightBlue)
                        
                self.tabla_historial.setItem(row, col, table_item)