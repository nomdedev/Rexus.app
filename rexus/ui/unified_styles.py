"""
Estilos Unificados para Todos los Módulos - Rexus.app
Basado en las especificaciones del usuario:
- Pestañas de 20px de alto
- Botones con el tamaño del módulo logística (18-22px)
"""


class UnifiedStyles:
    """Estilos unificados para aplicar consistencia en todos los módulos."""
    
    @staticmethod
    def get_tab_styles():
        """Retorna estilos unificados para pestañas - 20px de alto según usuario."""
        return """
            QTabWidget {
                border: none;
                background: transparent;
            }
            QTabBar::tab {
                background: #f8fafc;
                color: #6b7280;
                border: 1px solid #e5e7eb;
                border-bottom: none;
                min-width: 80px;
                min-height: 20px;
                max-height: 20px;
                padding: 2px 12px;
                font-size: 12px;
                font-weight: 500;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                color: #1f2937;
                border-color: #e5e7eb;
                border-bottom: 2px solid #3b82f6;
                font-weight: 600;
            }
            QTabBar::tab:hover:!selected {
                background: #f3f4f6;
                color: #374151;
            }
            QTabWidget::pane {
                border: 1px solid #e5e7eb;
                border-top: none;
                background: transparent;
                border-radius: 0 0 6px 6px;
            }
        """
    
    @staticmethod
    def get_button_styles():
        """Retorna estilos unificados para botones - basado en logística."""
        return """
            QPushButton {
                background-color: #f6f8fa;
                border: 1px solid #e1e4e8;
                color: #24292e;
                font-size: 12px;
                font-weight: 500;
                padding: 6px 12px;
                border-radius: 6px;
                min-height: 18px;
                max-height: 22px;
            }
            QPushButton:hover {
                background-color: #e1e4e8;
                border-color: #d0d7de;
            }
            QPushButton:pressed {
                background-color: #d0d7de;
            }
            QPushButton:disabled {
                background-color: #f6f8fa;
                color: #959da5;
                border-color: #e1e4e8;
            }
            
            /* Botones primarios */
            QPushButton[class="primary"] {
                background-color: #007bff;
                color: white;
                border: 1px solid #007bff;
            }
            QPushButton[class="primary"]:hover {
                background-color: #0056b3;
                border-color: #0056b3;
            }
            
            /* Botones de peligro */
            QPushButton[class="danger"] {
                background-color: #dc3545;
                color: white;
                border: 1px solid #dc3545;
            }
            QPushButton[class="danger"]:hover {
                background-color: #c82333;
                border-color: #c82333;
            }
            
            /* Botones de éxito */
            QPushButton[class="success"] {
                background-color: #28a745;
                color: white;
                border: 1px solid #28a745;
            }
            QPushButton[class="success"]:hover {
                background-color: #1e7e34;
                border-color: #1e7e34;
            }
        """
    
    @staticmethod
    def get_table_styles():
        """Retorna estilos unificados para tablas."""
        return """
            QTableWidget {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                gridline-color: #dee2e6;
                font-size: 12px;
                alternate-background-color: #f8f9fa;
            }
            QTableWidget::item {
                padding: 6px 8px;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px;
                border: 1px solid #dee2e6;
                font-weight: bold;
                color: #495057;
                font-size: 12px;
            }
        """
    
    @staticmethod
    def get_input_styles():
        """Retorna estilos unificados para campos de entrada."""
        return """
            QLineEdit, QComboBox, QSpinBox, QDateEdit, QTimeEdit {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 12px;
                background-color: white;
                min-height: 16px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDateEdit:focus, QTimeEdit:focus {
                border-color: #007bff;
                outline: none;
                background-color: #ffffff;
            }
            QLineEdit:disabled, QComboBox:disabled, QSpinBox:disabled, QDateEdit:disabled, QTimeEdit:disabled {
                background-color: #e9ecef;
                color: #6c757d;
                border-color: #e9ecef;
            }
        """
    
    @staticmethod
    def get_groupbox_styles():
        """Retorna estilos unificados para group boxes."""
        return """
            QGroupBox {
                font-weight: 600;
                font-size: 12px;
                color: #212529;
                border: 1px solid #dee2e6;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 8px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 8px 0 8px;
                background-color: white;
                color: #212529;
            }
        """
    
    @staticmethod
    def get_label_styles():
        """Retorna estilos unificados para labels."""
        return """
            QLabel {
                color: #212529;
                font-size: 12px;
            }
            QLabel[class="title"] {
                font-size: 16px;
                font-weight: bold;
                color: #212529;
            }
            QLabel[class="subtitle"] {
                font-size: 14px;
                font-weight: 600;
                color: #495057;
            }
            QLabel[class="small"] {
                font-size: 11px;
                color: #6c757d;
            }
        """
    
    @staticmethod
    def get_complete_unified_styles():
        """Retorna todos los estilos unificados combinados."""
        return f"""
            /* === ESTILOS UNIFICADOS REXUS.APP === */
            
            /* Pestañas - 20px según especificación del usuario */
            {UnifiedStyles.get_tab_styles()}
            
            /* Botones - basados en módulo logística */
            {UnifiedStyles.get_button_styles()}
            
            /* Tablas */
            {UnifiedStyles.get_table_styles()}
            
            /* Campos de entrada */
            {UnifiedStyles.get_input_styles()}
            
            /* Group Boxes */
            {UnifiedStyles.get_groupbox_styles()}
            
            /* Labels */
            {UnifiedStyles.get_label_styles()}
            
            /* Scrollbars */
            QScrollBar:vertical {{
                width: 12px;
                background-color: #f8f9fa;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: #dee2e6;
                border-radius: 6px;
                min-height: 20px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: #adb5bd;
            }}
            
            /* TextEdit */
            QTextEdit {{
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
                background-color: white;
            }}
            QTextEdit:focus {{
                border-color: #007bff;
            }}
        """
    
    @staticmethod
    def apply_to_widget(widget):
        """Aplica estilos unificados a un widget específico."""
        if widget:
            widget.setStyleSheet(UnifiedStyles.get_complete_unified_styles())
    
    @staticmethod
    def apply_tab_styles_only(tab_widget):
        """Aplica solo estilos de pestañas a un QTabWidget."""
        if tab_widget:
            tab_widget.setStyleSheet(UnifiedStyles.get_tab_styles())
            
    @staticmethod
    def set_button_class(button, button_class="default"):
        """Establece la clase de un botón para aplicar estilos específicos."""
        if button:
            button.setProperty("class", button_class)
            # Forzar actualización de estilos
            button.style().unpolish(button)
            button.style().polish(button)