# -*- coding: utf-8 -*-
"""
Chart Widget - Componente para gráficos en el dashboard
Soporte para diferentes tipos de gráficos con datos dinámicos
"""

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
    QComboBox, QPushButton, QScrollArea
)
from PyQt6.QtGui import QFont, QPainter, QColor, QPen, QBrush
import datetime


class ChartWidget(QFrame):
    """Widget para mostrar gráficos en el dashboard."""
    
    def __init__(self, tipo_chart="line", parent=None):
        super().__init__(parent)
        
        self.tipo_chart = tipo_chart
        self.datos = []
        self.labels = []
        self.colores = ["#667eea", "#764ba2", "#f093fb", "#f5576c", "#4facfe"]
        
        self.setup_ui()
        self.aplicar_estilos()
        
        # Datos de ejemplo para testing
        self.cargar_datos_ejemplo()
    
    def setup_ui(self):
        """Configura la interfaz del widget."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header con controles
        header_layout = QHBoxLayout()
        
        self.titulo_label = QLabel("📊 Gráfico")
        self.titulo_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.titulo_label.setStyleSheet("color: #333;")
        
        # Selector de período
        self.periodo_combo = QComboBox()
        self.periodo_combo.addItems(["Última semana", "Último mes", "Últimos 3 meses", "Último año"])
        self.periodo_combo.setCurrentText("Último mes")
        self.periodo_combo.currentTextChanged.connect(self.cambiar_periodo)
        
        # Botón actualizar
        self.btn_actualizar = QPushButton("🔄")
        self.btn_actualizar.setFixedSize(30, 30)
        self.btn_actualizar.clicked.connect(self.actualizar_grafico)
        
        header_layout.addWidget(self.titulo_label)
        header_layout.addStretch()
        header_layout.addWidget(self.periodo_combo)
        header_layout.addWidget(self.btn_actualizar)
        
        # Área del gráfico
        self.chart_area = QFrame()
        self.chart_area.setMinimumHeight(250)
        self.chart_area.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
            }
        """)
        
        layout.addLayout(header_layout)
        layout.addWidget(self.chart_area)
    
    def aplicar_estilos(self):
        """Aplica estilos al widget."""
        self.setStyleSheet("""
            QFrame {
                background: #f8f9fa;
                border: none;
                border-radius: 8px;
            }
            QComboBox {
                padding: 5px;
                border: 1px solid #ddd;
                border-radius: 4px;
                background: white;
            }
            QPushButton {
                border: 1px solid #ddd;
                border-radius: 4px;
                background: white;
            }
            QPushButton:hover {
                background: #f0f0f0;
            }
        """)
    
    def paintEvent(self, event):
        """Dibuja el gráfico personalizado."""
        super().paintEvent(event)
        
        if not self.datos:
            return
        
        painter = QPainter(self.chart_area)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Obtener dimensiones del área de gráfico
        rect = self.chart_area.rect()
        margin = 40
        chart_rect = rect.adjusted(margin, margin, -margin, -margin)
        
        if self.tipo_chart == "line":
            self.dibujar_linea(painter, chart_rect)
        elif self.tipo_chart == "bar":
            self.dibujar_barras(painter, chart_rect)
        elif self.tipo_chart == "pie":
            self.dibujar_pie(painter, chart_rect)
    
    def dibujar_linea(self, painter, rect):
        """Dibuja un gráfico de líneas."""
        if len(self.datos) < 2:
            return
        
        # Configurar pen para la línea
        pen = QPen(QColor(self.colores[0]), 3)
        painter.setPen(pen)
        
        # Calcular escalas
        max_val = max(self.datos) if self.datos else 1
        min_val = min(self.datos) if self.datos else 0
        rango = max_val - min_val if max_val != min_val else 1
        
        width = rect.width()
        height = rect.height()
        
        # Dibujar línea
        for i in range(len(self.datos) - 1):
            x1 = rect.x() + (i * width / (len(self.datos) - 1))
            y1 = rect.bottom() - ((self.datos[i] - min_val) / rango * height)
            x2 = rect.x() + ((i + 1) * width / (len(self.datos) - 1))
            y2 = rect.bottom() - ((self.datos[i + 1] - min_val) / rango * height)
            
            painter.drawLine(int(x1), int(y1), int(x2), int(y2))
        
        # Dibujar puntos
        brush = QBrush(QColor(self.colores[0]))
        painter.setBrush(brush)
        
        for i, valor in enumerate(self.datos):
            x = rect.x() + (i * width / (len(self.datos) - 1))
            y = rect.bottom() - ((valor - min_val) / rango * height)
            painter.drawEllipse(int(x - 4), int(y - 4), 8, 8)
    
    def dibujar_barras(self, painter, rect):
        """Dibuja un gráfico de barras."""
        if not self.datos:
            return
        
        max_val = max(self.datos) if self.datos else 1
        bar_width = rect.width() / len(self.datos) * 0.8
        spacing = rect.width() / len(self.datos) * 0.2
        
        for i, valor in enumerate(self.datos):
            # Color de la barra
            color = QColor(self.colores[i % len(self.colores)])
            brush = QBrush(color)
            painter.setBrush(brush)
            painter.setPen(QPen(color.darker(120), 1))
            
            # Calcular posición y altura
            x = rect.x() + i * (bar_width + spacing)
            height = (valor / max_val) * rect.height()
            y = rect.bottom() - height
            
            painter.drawRect(int(x), int(y), int(bar_width), int(height))
    
    def dibujar_pie(self, painter, rect):
        """Dibuja un gráfico de pie."""
        if not self.datos:
            return
        
        total = sum(self.datos)
        if total == 0:
            return
        
        # Centro y radio del círculo
        center_x = rect.center().x()
        center_y = rect.center().y()
        radius = min(rect.width(), rect.height()) // 2 - 10
        
        start_angle = 0
        
        for i, valor in enumerate(self.datos):
            # Calcular ángulo
            angle = int((valor / total) * 360 * 16)  # Qt usa 1/16 de grado
            
            # Color del segmento
            color = QColor(self.colores[i % len(self.colores)])
            brush = QBrush(color)
            painter.setBrush(brush)
            painter.setPen(QPen(color.darker(120), 2))
            
            # Dibujar segmento
            painter.drawPie(
                center_x - radius, center_y - radius,
                radius * 2, radius * 2,
                start_angle, angle
            )
            
            start_angle += angle
    
    def cargar_datos_ejemplo(self):
        """Carga datos de ejemplo para testing."""
        if self.tipo_chart == "line":
            self.datos = [12, 19, 15, 25, 22, 18, 30, 28]
            self.labels = ["Sem 1", "Sem 2", "Sem 3", "Sem 4", "Sem 5", "Sem 6", "Sem 7", "Sem 8"]
            self.titulo_label.setText("📈 Tendencia de Ventas")
        elif self.tipo_chart == "bar":
            self.datos = [45, 60, 35, 80, 25]
            self.labels = ["Productos", "Obras", "Pedidos", "Compras", "Usuarios"]
            self.titulo_label.setText("📊 Actividad por Módulo")
        elif self.tipo_chart == "pie":
            self.datos = [30, 25, 20, 15, 10]
            self.labels = ["Completado", "En Proceso", "Pendiente", "Cancelado", "Borrador"]
            self.titulo_label.setText("🥧 Estados de Pedidos")
    
    def actualizar_datos(self, nuevos_datos, nuevas_labels=None):
        """Actualiza los datos del gráfico."""
        self.datos = nuevos_datos
        if nuevas_labels:
            self.labels = nuevas_labels
        self.update()  # Redibuja el widget
    
    def cambiar_periodo(self, periodo):
        """Cambia el período de visualización."""
        # TODO: Implementar lógica para cambiar período
        self.actualizar_grafico()
    
    def actualizar_grafico(self):
        """Actualiza el gráfico con datos frescos."""
        # TODO: Solicitar nuevos datos al backend
        self.update()


class ChartLegendWidget(QWidget):
    """Widget para mostrar la leyenda del gráfico."""
    
    def __init__(self, labels, colores, parent=None):
        super().__init__(parent)
        
        self.labels = labels
        self.colores = colores
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la leyenda."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        for i, label in enumerate(self.labels):
            item_layout = QHBoxLayout()
            
            # Color box
            color_box = QFrame()
            color_box.setFixedSize(12, 12)
            color_box.setStyleSheet(f"""
                QFrame {{
                    background: {self.colores[i % len(self.colores)]};
                    border-radius: 2px;
                }}
            """)
            
            # Label
            label_widget = QLabel(label)
            label_widget.setFont(QFont("Segoe UI", 9))
            label_widget.setStyleSheet("color: #333;")
            
            item_layout.addWidget(color_box)
            item_layout.addWidget(label_widget)
            item_layout.addStretch()
            
            layout.addLayout(item_layout)
        
        layout.addStretch()


class ChartPlaceholderWidget(QFrame):
    """Placeholder para gráficos que requieren librerías externas."""
    
    def __init__(self, tipo_chart, mensaje="", parent=None):
        super().__init__(parent)
        
        self.tipo_chart = tipo_chart
        self.mensaje = mensaje or f"Gráfico {tipo_chart} aquí"
        
        self.setup_ui()
        self.aplicar_estilos()
    
    def setup_ui(self):
        """Configura el placeholder."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Icono según tipo
        iconos = {
            "line": "📈",
            "bar": "📊", 
            "pie": "🥧",
            "area": "📉"
        }
        
        icono_label = QLabel(iconos.get(self.tipo_chart, "📊"))
        icono_label.setFont(QFont("Segoe UI", 48))
        icono_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icono_label.setStyleSheet("color: #ccc;")
        
        mensaje_label = QLabel(self.mensaje)
        mensaje_label.setFont(QFont("Segoe UI", 12))
        mensaje_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mensaje_label.setStyleSheet("color: #999;")
        
        sugerencia_label = QLabel("Integrar Chart.js o matplotlib para gráficos avanzados")
        sugerencia_label.setFont(QFont("Segoe UI", 10))
        sugerencia_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sugerencia_label.setStyleSheet("color: #bbb; font-style: italic;")
        
        layout.addWidget(icono_label)
        layout.addWidget(mensaje_label)
        layout.addWidget(sugerencia_label)
    
    def aplicar_estilos(self):
        """Aplica estilos al placeholder."""
        self.setStyleSheet("""
            QFrame {
                background: #fafafa;
                border: 2px dashed #ddd;
                border-radius: 8px;
                min-height: 200px;
            }
        """)