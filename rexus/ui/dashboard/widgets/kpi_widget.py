# -*- coding: utf-8 -*-
"""
KPI Widget - Componente para mostrar métricas clave
Diseño moderno con soporte para tendencias y animaciones
"""

from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtGui import QFont, QPainter, QColor, QPalette


class KPIWidget(QFrame):
    """Widget moderno para mostrar KPIs con tendencias."""
    
    def __init__(self, titulo, valor_inicial="0", descripcion="", parent=None):
        super().__init__(parent)
        
        self.titulo = titulo
        self.valor_actual = valor_inicial
        self.descripcion = descripcion
        self.tendencia = None  # 'up', 'down', 'stable'
        self.porcentaje_cambio = 0
        
        self.setup_ui()
        self.aplicar_estilos()
        
        # Animación para cambios de valor
        self._animation_opacity = 1.0
        self.animation = QPropertyAnimation(self, b"animation_opacity")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
    
    def setup_ui(self):
        """Configura la interfaz del widget."""
        self.setFixedHeight(120)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(5)
        
        # Header con título y tendencia
        header_layout = QHBoxLayout()
        
        self.titulo_label = QLabel(self.titulo)
        self.titulo_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.titulo_label.setStyleSheet("color: #666; margin: 0;")
        
        self.tendencia_label = QLabel()
        self.tendencia_label.setFont(QFont("Segoe UI", 12))
        self.tendencia_label.setFixedSize(20, 20)
        self.tendencia_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        header_layout.addWidget(self.titulo_label)
        header_layout.addStretch()
        header_layout.addWidget(self.tendencia_label)
        
        # Valor principal
        self.valor_label = QLabel(self.valor_actual)
        self.valor_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        self.valor_label.setStyleSheet("color: #333; margin: 5px 0;")
        self.valor_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Footer con descripción y cambio porcentual
        footer_layout = QHBoxLayout()
        
        self.descripcion_label = QLabel(self.descripcion)
        self.descripcion_label.setFont(QFont("Segoe UI", 8))
        self.descripcion_label.setStyleSheet("color: #888;")
        
        self.cambio_label = QLabel()
        self.cambio_label.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
        self.cambio_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        footer_layout.addWidget(self.descripcion_label)
        footer_layout.addStretch()
        footer_layout.addWidget(self.cambio_label)
        
        layout.addLayout(header_layout)
        layout.addWidget(self.valor_label)
        layout.addStretch()
        layout.addLayout(footer_layout)
    
    def aplicar_estilos(self):
        """Aplica estilos modernos al widget."""
        self.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
            }
            QFrame:hover {
                border: 2px solid #667eea;
                background: #f8f9fa;
            }
        """)
    
    def actualizar_valor(self, nuevo_valor, tendencia=None, porcentaje_cambio=0):
        """Actualiza el valor del KPI con animación."""
        valor_anterior = self.valor_actual
        self.valor_actual = str(nuevo_valor)
        self.tendencia = tendencia
        self.porcentaje_cambio = porcentaje_cambio
        
        # Animar cambio si el valor es diferente
        if valor_anterior != self.valor_actual:
            self.animar_cambio()
        
        # Actualizar UI
        self.valor_label.setText(self.valor_actual)
        self.actualizar_tendencia()
        self.actualizar_cambio_porcentual()
    
    def actualizar_tendencia(self):
        """Actualiza el indicador de tendencia."""
        if self.tendencia == 'up':
            self.tendencia_label.setText("📈")
            self.tendencia_label.setStyleSheet("color: #4caf50;")
        elif self.tendencia == 'down':
            self.tendencia_label.setText("📉")
            self.tendencia_label.setStyleSheet("color: #f44336;")
        elif self.tendencia == 'stable':
            self.tendencia_label.setText("➖")
            self.tendencia_label.setStyleSheet("color: #ff9800;")
        else:
            self.tendencia_label.setText("")
    
    def actualizar_cambio_porcentual(self):
        """Actualiza el indicador de cambio porcentual."""
        if self.porcentaje_cambio != 0:
            signo = "+" if self.porcentaje_cambio > 0 else ""
            texto = f"{signo}{self.porcentaje_cambio:.1f}%"
            
            if self.porcentaje_cambio > 0:
                color = "#4caf50"
            elif self.porcentaje_cambio < 0:
                color = "#f44336"
            else:
                color = "#888"
            
            self.cambio_label.setText(texto)
            self.cambio_label.setStyleSheet(f"color: {color};")
        else:
            self.cambio_label.setText("")
    
    def animar_cambio(self):
        """Anima el cambio de valor."""
        # Highlight temporal
        self.setStyleSheet("""
            QFrame {
                background: #f0f8ff;
                border: 3px solid #667eea;
                border-radius: 8px;
            }
        """)
        
        # Volver al estilo normal después de la animación
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(500, self.aplicar_estilos)
    
    # Propiedad para animación
    @pyqtProperty(float)
    def animation_opacity(self):
        return self._animation_opacity
    
    @animation_opacity.setter
    def animation_opacity(self, opacity):
        self._animation_opacity = opacity
        self.update()


class KPICompactoWidget(QFrame):
    """Versión compacta del KPI widget para espacios reducidos."""
    
    def __init__(self, icono, valor, descripcion, parent=None):
        super().__init__(parent)
        
        self.icono = icono
        self.valor_actual = valor
        self.descripcion = descripcion
        
        self.setup_ui()
        self.aplicar_estilos()
    
    def setup_ui(self):
        """Configura la interfaz compacta."""
        self.setFixedSize(120, 80)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(2)
        
        # Icono y valor en la misma línea
        top_layout = QHBoxLayout()
        
        self.icono_label = QLabel(self.icono)
        self.icono_label.setFont(QFont("Segoe UI", 16))
        self.icono_label.setFixedSize(24, 24)
        
        self.valor_label = QLabel(self.valor_actual)
        self.valor_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.valor_label.setStyleSheet("color: #333;")
        
        top_layout.addWidget(self.icono_label)
        top_layout.addWidget(self.valor_label)
        top_layout.addStretch()
        
        # Descripción
        self.descripcion_label = QLabel(self.descripcion)
        self.descripcion_label.setFont(QFont("Segoe UI", 7))
        self.descripcion_label.setStyleSheet("color: #666;")
        self.descripcion_label.setWordWrap(True)
        
        layout.addLayout(top_layout)
        layout.addWidget(self.descripcion_label)
        layout.addStretch()
    
    def aplicar_estilos(self):
        """Aplica estilos compactos."""
        self.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
            }
            QFrame:hover {
                border: 1px solid #667eea;
                background: #f8f9ff;
            }
        """)
    
    def actualizar_valor(self, nuevo_valor):
        """Actualiza el valor del KPI compacto."""
        self.valor_actual = str(nuevo_valor)
        self.valor_label.setText(self.valor_actual)