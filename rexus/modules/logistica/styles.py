"""
Estilos CSS centralizados para el módulo de Logística

Contiene todos los estilos CSS para mantener consistencia visual y facilitar cambios.
"""

# Estilo principal de la vista con mejor contraste
MAIN_STYLE = """
QWidget {
    background-color: #ffffff;  /* Fondo más claro para mejor contraste */
    font-family: 'Segoe UI', sans-serif;
    font-size: 12px;
    color: #212529;  /* Texto más oscuro para mejor contraste */
}

QGroupBox {
    font-weight: bold;
    border: 2px solid #495057;  /* Borde más visible */
    border-radius: 4px;
    margin-top: 5px;
    padding-top: 8px;
    background-color: #f8f9fa;
    font-size: 12px;
    color: #212529;  /* Texto más oscuro */
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 8px;
    color: #212529;  /* Título más visible */
    background-color: #f8f9fa;
}

QPushButton {
    background-color: #0d6efd;  /* Azul más visible */
    color: #ffffff;
    border: 1px solid #0d6efd;
    padding: 6px 12px;  /* Botones más grandes */
    border-radius: 4px;
    font-weight: 600;
    font-size: 12px;
    min-height: 24px;  /* Altura mínima para accesibilidad */
}

QPushButton:hover {
    background-color: #0b5ed7;
    border-color: #0a58ca;
}

QPushButton:pressed {
    background-color: #0a58ca;
    border-color: #0a53be;
}

QTableWidget {
    gridline-color: #495057;  /* Líneas más visibles */
    background-color: #ffffff;
    alternate-background-color: #f8f9fa;
    font-size: 12px;
    color: #212529;
    selection-background-color: #e3f2fd;  /* Selección más visible */
}

QHeaderView::section {
    background-color: #e9ecef;  /* Fondo gris claro para headers */
    color: #212529;  /* Texto oscuro */
    padding: 8px;
    border: 1px solid #495057;
    font-weight: 600;
    font-size: 11px;
}

QLineEdit, QComboBox, QDateEdit {
    padding: 8px 12px;  /* Más padding para facilitar interacción */
    border: 2px solid #ced4da;  /* Borde más visible */
    border-radius: 4px;
    font-size: 12px;
    background-color: #ffffff;
    color: #212529;
    min-height: 20px;
}

QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
    border-color: #0d6efd;  /* Borde azul para foco */
    outline: 0;
    box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
}

QTextEdit {
    padding: 8px;
    border: 2px solid #ced4da;
    border-radius: 4px;
    font-size: 12px;
    background-color: #ffffff;
    color: #212529;
}

QTextEdit:focus {
    border-color: #0d6efd;
}
"""

# Estilos para pestañas
TAB_STYLE = """
QTabWidget::pane {
    border: 1px solid #bdc3c7;
    background-color: white;
}

QTabBar::tab {
    background: #ecf0f1;
    padding: 6px 12px;
    margin-right: 2px;
    border: 1px solid #bdc3c7;
    border-bottom: none;
    font-size: 11px;
}

QTabBar::tab:selected {
    background: white;
    border-bottom: 1px solid white;
}
"""

# Estilos para botones específicos con mejor contraste
BUTTON_STYLES = {
    "success": """
        QPushButton {{
            background-color: #198754;  /* Verde más oscuro para mejor contraste */
            color: #ffffff;
            border: 1px solid #198754;
            padding: 8px 16px;  /* Más padding */
            font-size: 12px;
            font-weight: 600;
            border-radius: 4px;
            min-height: 24px;
        }}
        QPushButton:hover {{
            background-color: #157347;
            border-color: #146c43;
        }}
        QPushButton:pressed {{
            background-color: #146c43;
        }}
    """,
    
    "secondary": """
        QPushButton {{
            background-color: #6c757d;  /* Gris más oscuro */
            color: #ffffff;
            border: 1px solid #6c757d;
            padding: 8px 16px;
            font-size: 12px;
            font-weight: 600;
            border-radius: 4px;
            min-height: 24px;
        }}
        QPushButton:hover {{
            background-color: #5c636a;
            border-color: #565e64;
        }}
        QPushButton:pressed {{
            background-color: #565e64;
        }}
    """,
    
    "info": """
        QPushButton {{
            background-color: #0d6efd;  /* Azul más accesible */
            color: #ffffff;
            border: 1px solid #0d6efd;
            padding: 8px 16px;
            font-size: 12px;
            font-weight: 600;
            border-radius: 4px;
            min-height: 24px;
        }}
        QPushButton:hover {{
            background-color: #0b5ed7;
            border-color: #0a58ca;
        }}
        QPushButton:pressed {{
            background-color: #0a58ca;
        }}
    """,
    
    "warning": """
        QPushButton {{
            background-color: #fd7e14;  /* Naranja más visible */
            color: #ffffff;
            border: 1px solid #fd7e14;
            padding: 8px 16px;
            font-size: 12px;
            font-weight: 600;
            border-radius: 4px;
            min-height: 24px;
        }}
        QPushButton:hover {{
            background-color: #e76500;
            border-color: #dc5f00;
        }}
        QPushButton:pressed {{
            background-color: #dc5f00;
        }}
    """,
    
    "danger": """
        QPushButton {{
            background-color: #dc3545;  /* Rojo para acciones peligrosas */
            color: #ffffff;
            border: 1px solid #dc3545;
            padding: 8px 16px;
            font-size: 12px;
            font-weight: 600;
            border-radius: 4px;
            min-height: 24px;
        }}
        QPushButton:hover {{
            background-color: #bb2d3b;
            border-color: #b02a37;
        }}
        QPushButton:pressed {{
            background-color: #b02a37;
        }}
    """
}

# Estilo para el mapa fallback
FALLBACK_MAP_STYLE = """
QFrame {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                stop: 0 #ecf0f1, stop: 1 #bdc3c7);
    border: 2px dashed #95a5a6;
    border-radius: 8px;
}

QLabel {
    color: #2c3e50;
    font-size: 12px;
    font-weight: bold;
    background: transparent;
}
"""

# Estilo para estadísticas
STATS_STYLE = """
QFrame[objectName="stat_frame"] {
    background-color: white;
    border: 1px solid #bdc3c7;
    border-radius: 4px;
    padding: 8px;
}

QLabel[objectName="stat_title"] {
    font-weight: bold;
    font-size: 12px;
    color: #2c3e50;
}

QLabel[objectName="stat_value"] {
    font-size: 16px;
    font-weight: bold;
    color: #27ae60;
}

QProgressBar {
    border: 1px solid #bdc3c7;
    border-radius: 3px;
    text-align: center;
    height: 8px;
}

QProgressBar::chunk {
    background-color: #3498db;
    border-radius: 2px;
}
"""