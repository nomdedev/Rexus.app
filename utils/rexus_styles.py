"""
Estilos UI/UX Centralizados para Rexus.app
Archivo generado automáticamente
"""

from PyQt6.QtGui import QFont, QColor

class RexusStyles:
    """Estilos estandarizados para toda la aplicación"""
    
    # Colores del sistema
    COLOR_PRIMARIO = "#2E7D32"      # Verde oscuro
    COLOR_SECUNDARIO = "#388E3C"    # Verde medio  
    COLOR_ACENTO = "#4CAF50"        # Verde claro
    COLOR_INFO = "#1976D2"          # Azul
    COLOR_ADVERTENCIA = "#FF9800"   # Naranja
    COLOR_ERROR = "#F44336"         # Rojo
    COLOR_EXITO = "#4CAF50"         # Verde
    
    # Fuentes estandarizadas
    FUENTE_PRINCIPAL = "Arial"
    FUENTE_MONOSPACE = "Courier New"
    
    # Tamaños de fuente
    TAMAÑO_TITULO = 16
    TAMAÑO_SUBTITULO = 14
    TAMAÑO_NORMAL = 11
    TAMAÑO_PEQUEÑO = 9
    
    # Espaciado estándar
    ESPACIADO_PEQUENO = 5
    ESPACIADO_NORMAL = 10
    ESPACIADO_GRANDE = 15
    ESPACIADO_EXTRA = 20
    
    # Márgenes estándar
    MARGEN_PEQUENO = 5
    MARGEN_NORMAL = 10
    MARGEN_GRANDE = 15
    MARGEN_EXTRA = 20
    
    @staticmethod
    def fuente_titulo():
        """Retorna fuente para títulos"""
        font = QFont(RexusStyles.FUENTE_PRINCIPAL, RexusStyles.TAMAÑO_TITULO)
        font.setBold(True)
        return font
        
    @staticmethod
    def fuente_subtitulo():
        """Retorna fuente para subtítulos"""
        font = QFont(RexusStyles.FUENTE_PRINCIPAL, RexusStyles.TAMAÑO_SUBTITULO)
        font.setBold(True)
        return font
        
    @staticmethod
    def fuente_normal():
        """Retorna fuente normal"""
        return QFont(RexusStyles.FUENTE_PRINCIPAL, RexusStyles.TAMAÑO_NORMAL)
        
    @staticmethod
    def fuente_monospace():
        """Retorna fuente monospace"""
        return QFont(RexusStyles.FUENTE_MONOSPACE, RexusStyles.TAMAÑO_NORMAL)
        
    @staticmethod
    def color_primario():
        """Retorna color primario como QColor"""
        return QColor(RexusStyles.COLOR_PRIMARIO)
        
    @staticmethod
    def estilo_boton_primario():
        """Retorna stylesheet para botón primario"""
        return f"""
        QPushButton {{
            background-color: {RexusStyles.COLOR_PRIMARIO};
            color: white;
            border: 2px solid {RexusStyles.COLOR_PRIMARIO};
            border-radius: 5px;
            padding: 8px 16px;
            font-family: {RexusStyles.FUENTE_PRINCIPAL};
            font-size: {RexusStyles.TAMAÑO_NORMAL}px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {RexusStyles.COLOR_SECUNDARIO};
            border-color: {RexusStyles.COLOR_SECUNDARIO};
        }}
        QPushButton:pressed {{
            background-color: {RexusStyles.COLOR_ACENTO};
        }}
        QPushButton:disabled {{
            background-color: #CCCCCC;
            color: #666666;
            border-color: #CCCCCC;
        }}
        """
        
    @staticmethod
    def estilo_input():
        """Retorna stylesheet para campos de entrada"""
        return f"""
        QLineEdit, QTextEdit {{
            border: 2px solid #DDDDDD;
            border-radius: 4px;
            padding: 5px;
            font-family: {RexusStyles.FUENTE_PRINCIPAL};
            font-size: {RexusStyles.TAMAÑO_NORMAL}px;
            background-color: white;
        }}
        QLineEdit:focus, QTextEdit:focus {{
            border-color: {RexusStyles.COLOR_PRIMARIO};
        }}
        QLineEdit:disabled, QTextEdit:disabled {{
            background-color: #F5F5F5;
            color: #666666;
        }}
        """
        
    @staticmethod
    def estilo_tabla():
        """Retorna stylesheet para tablas"""
        return f"""
        QTableWidget {{
            gridline-color: #DDDDDD;
            background-color: white;
            alternate-background-color: #F9F9F9;
            selection-background-color: {RexusStyles.COLOR_ACENTO};
            font-family: {RexusStyles.FUENTE_PRINCIPAL};
            font-size: {RexusStyles.TAMAÑO_NORMAL}px;
        }}
        QTableWidget::item {{
            padding: 5px;
            border: none;
        }}
        QHeaderView::section {{
            background-color: transparent;
            color: #222;
            padding: 8px;
            border: none;
            font-weight: bold;
        }}
        """
