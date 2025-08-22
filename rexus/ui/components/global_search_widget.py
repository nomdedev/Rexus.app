# -*- coding: utf-8 -*-
"""
Global Search Widget - Búsqueda global inteligente
Permite buscar en todos los módulos desde cualquier lugar
"""

from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QScrollArea, QFrame, QLabel, QApplication
)
from PyQt6.QtGui import QFont, QKeySequence, QShortcut, QAction
import re
from typing import List, Dict, Any


class GlobalSearchWorker(QThread):
    """Worker thread para búsquedas asíncronas."""
    
    results_ready = pyqtSignal(list)
    search_finished = pyqtSignal()
    
    def __init__(self, search_term, search_engines):
        super().__init__()
        self.search_term = search_term
        self.search_engines = search_engines
        self.results = []
    
    def run(self):
        """Ejecuta la búsqueda en background."""
        self.results = []
        
        for engine in self.search_engines:
            try:
                engine_results = engine.search(self.search_term)
                self.results.extend(engine_results)
            except Exception as e:
                print(f"Error en búsqueda {engine.__class__.__name__}: {e}")
        
        # Ordenar por relevancia
        self.results.sort(key=lambda x: x.get('relevance', 0), reverse=True)
        
        self.results_ready.emit(self.results)
        self.search_finished.emit()


class SearchResult:
    """Representa un resultado de búsqueda."""
    
    def __init__(self, title, description, module, action_data=None, relevance=1.0):
        self.title = title
        self.description = description 
        self.module = module
        self.action_data = action_data or {}
        self.relevance = relevance
    
    def to_dict(self):
        return {
            'title': self.title,
            'description': self.description,
            'module': self.module, 
            'action_data': self.action_data,
            'relevance': self.relevance
        }


class BaseSearchEngine:
    """Clase base para motores de búsqueda de módulos."""
    
    def __init__(self, module_name):
        self.module_name = module_name
    
    def search(self, term: str) -> List[Dict]:
        """
        Busca el término en el módulo.
        
        Args:
            term: Término de búsqueda
            
        Returns:
            Lista de resultados como diccionarios
        """
        raise NotImplementedError("Subclasses must implement search method")
    
    def calculate_relevance(self, term: str, text: str) -> float:
        """Calcula la relevancia de un resultado."""
        if not term or not text:
            return 0.0
        
        term_lower = term.lower()
        text_lower = text.lower()
        
        # Coincidencia exacta
        if term_lower == text_lower:
            return 1.0
        
        # Comienza con el término
        if text_lower.startswith(term_lower):
            return 0.9
        
        # Contiene el término
        if term_lower in text_lower:
            return 0.7
        
        # Coincidencia de palabras
        term_words = term_lower.split()
        text_words = text_lower.split()
        
        matches = sum(1 for word in term_words if any(word in text_word for text_word in text_words))
        return (matches / len(term_words)) * 0.5


class InventarioSearchEngine(BaseSearchEngine):
    """Motor de búsqueda para el módulo de inventario."""
    
    def __init__(self):
        super().__init__("Inventario")
    
    def search(self, term: str) -> List[Dict]:
        results = []
        
        # Búsquedas de ejemplo (en una implementación real, consultaría la base de datos)
        sample_products = [
            {"name": "Vidrio Templado 6mm", "category": "Vidrios", "stock": 150},
            {"name": "Herraje Bisagra Premium", "category": "Herrajes", "stock": 45},
            {"name": "Marco Aluminio Blanco", "category": "Marcos", "stock": 30},
            {"name": "Vidrio Laminado 8mm", "category": "Vidrios", "stock": 80},
        ]
        
        for product in sample_products:
            relevance = max(
                self.calculate_relevance(term, product["name"]),
                self.calculate_relevance(term, product["category"]) * 0.7
            )
            
            if relevance > 0.3:  # Threshold mínimo
                results.append({
                    'title': product["name"],
                    'description': f'{product["category"]} - Stock: {product["stock"]}',
                    'module': 'Inventario',
                    'action_data': {'type': 'view_product', 'product_name': product["name"]},
                    'relevance': relevance
                })
        
        return results


class ObrasSearchEngine(BaseSearchEngine):
    """Motor de búsqueda para el módulo de obras."""
    
    def __init__(self):
        super().__init__("Obras")
    
    def search(self, term: str) -> List[Dict]:
        results = []
        
        sample_obras = [
            {"name": "Edificio Central - Torre A", "status": "En Progreso", "client": "Constructora ABC"},
            {"name": "Casa Familiar Pérez", "status": "Completada", "client": "Sr. Pérez"},
            {"name": "Oficinas Comerciales", "status": "Pendiente", "client": "Inmobiliaria XYZ"},
        ]
        
        for obra in sample_obras:
            relevance = max(
                self.calculate_relevance(term, obra["name"]),
                self.calculate_relevance(term, obra["client"]) * 0.8,
                self.calculate_relevance(term, obra["status"]) * 0.6
            )
            
            if relevance > 0.3:
                results.append({
                    'title': obra["name"],
                    'description': f'{obra["status"]} - Cliente: {obra["client"]}',
                    'module': 'Obras',
                    'action_data': {'type': 'view_obra', 'obra_name': obra["name"]},
                    'relevance': relevance
                })
        
        return results


class GlobalSearchWidget(QWidget):
    """Widget de búsqueda global con resultados en tiempo real."""
    
    # Señales
    result_selected = pyqtSignal(dict)  # Emite el resultado seleccionado
    search_closed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.search_engines = [
            InventarioSearchEngine(),
            ObrasSearchEngine(),
            # Agregar más motores según sea necesario
        ]
        
        self.search_worker = None
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        
        self.setup_ui()
        self.setup_shortcuts()
        self.apply_styles()
        
        # Ocultar por defecto
        self.hide()
    
    def setup_ui(self):
        """Configura la interfaz del widget."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Overlay semi-transparente
        self.overlay = QFrame()
        self.overlay.setStyleSheet("""
            QFrame {
                background: rgba(0, 0, 0, 0.3);
                border: none;
            }
        """)
        
        # Container central
        self.container = QFrame()
        self.container.setFixedSize(600, 400)
        
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(10)
        
        # Header con campo de búsqueda
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar en todos los módulos... (Ctrl+K)")
        self.search_input.textChanged.connect(self.on_search_text_changed)
        self.search_input.returnPressed.connect(self.select_first_result)
        
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.clicked.connect(self.hide_search)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.close_btn)
        
        # Área de resultados
        self.results_scroll = QScrollArea()
        self.results_scroll.setWidgetResizable(True)
        self.results_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.results_container = QWidget()
        self.results_layout = QVBoxLayout(self.results_container)
        self.results_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.results_scroll.setWidget(self.results_container)
        
        # Footer con ayuda
        self.help_label = QLabel("Presiona Enter para seleccionar, Esc para cerrar")
        self.help_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        container_layout.addLayout(search_layout)
        container_layout.addWidget(self.results_scroll)
        container_layout.addWidget(self.help_label)
        
        # Layout principal con overlay
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.overlay)
        
        # Centrar el container
        overlay_layout = QVBoxLayout(self.overlay)
        overlay_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        overlay_layout.addWidget(self.container)
        
        layout.addLayout(main_layout)
    
    def setup_shortcuts(self):
        """Configura los shortcuts de teclado."""
        # Ctrl+K para abrir búsqueda
        self.open_shortcut = QShortcut(QKeySequence("Ctrl+K"), self.parent() or self)
        self.open_shortcut.activated.connect(self.show_search)
        
        # Esc para cerrar
        self.close_shortcut = QShortcut(QKeySequence("Esc"), self)
        self.close_shortcut.activated.connect(self.hide_search)
    
    def apply_styles(self):
        """Aplica estilos al widget."""
        self.setStyleSheet("""
            GlobalSearchWidget {
                background: transparent;
            }
            QFrame#container {
                background: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                box-shadow: 0px 4px 20px rgba(0,0,0,0.15);
            }
            QLineEdit {
                border: 2px solid #667eea;
                border-radius: 6px;
                padding: 12px 16px;
                font-size: 14px;
                background: white;
            }
            QLineEdit:focus {
                border-color: #4c51bf;
            }
            QPushButton {
                background: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 16px;
                font-weight: bold;
                color: #666;
            }
            QPushButton:hover {
                background: #eeeeee;
                color: #333;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QLabel {
                color: #666;
                font-size: 12px;
            }
        """)
        
        self.container.setObjectName("container")
    
    def show_search(self):
        """Muestra el widget de búsqueda."""
        self.show()
        self.search_input.setFocus()
        self.search_input.selectAll()
    
    def hide_search(self):
        """Oculta el widget de búsqueda."""
        self.hide()
        self.search_input.clear()
        self.clear_results()
        self.search_closed.emit()
    
    def on_search_text_changed(self, text):
        """Maneja cambios en el texto de búsqueda."""
        if len(text) >= 2:  # Búsqueda mínima de 2 caracteres
            self.search_timer.start(300)  # Debounce de 300ms
        else:
            self.clear_results()
    
    def perform_search(self):
        """Ejecuta la búsqueda actual."""
        search_term = self.search_input.text().strip()
        
        if not search_term:
            self.clear_results()
            return
        
        # Cancelar búsqueda anterior si está ejecutándose
        if self.search_worker and self.search_worker.isRunning():
            self.search_worker.quit()
            self.search_worker.wait()
        
        # Crear nueva búsqueda
        self.search_worker = GlobalSearchWorker(search_term, self.search_engines)
        self.search_worker.results_ready.connect(self.display_results)
        self.search_worker.start()
    
    @pyqtSlot(list)
    def display_results(self, results):
        """Muestra los resultados de búsqueda."""
        self.clear_results()
        
        if not results:
            no_results = QLabel("No se encontraron resultados")
            no_results.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_results.setStyleSheet("color: #999; padding: 20px; font-size: 14px;")
            self.results_layout.addWidget(no_results)
            return
        
        # Mostrar hasta 10 resultados
        for result in results[:10]:
            result_widget = self.create_result_widget(result)
            self.results_layout.addWidget(result_widget)
    
    def create_result_widget(self, result):
        """Crea un widget para un resultado individual."""
        widget = QFrame()
        widget.setFixedHeight(60)
        widget.setStyleSheet("""
            QFrame {
                background: white;
                border: 1px solid #f0f0f0;
                border-radius: 4px;
                padding: 8px;
                margin: 2px;
            }
            QFrame:hover {
                background: #f8f9ff;
                border-color: #667eea;
            }
        """)
        widget.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(2)
        
        # Título con módulo
        title_layout = QHBoxLayout()
        
        title_label = QLabel(result['title'])
        title_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #333;")
        
        module_label = QLabel(result['module'])
        module_label.setStyleSheet("""
            background: #667eea;
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 10px;
            font-weight: bold;
        """)
        module_label.setFixedHeight(20)
        
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(module_label)
        
        # Descripción
        desc_label = QLabel(result['description'])
        desc_label.setStyleSheet("color: #666; font-size: 12px;")
        desc_label.setWordWrap(True)
        
        layout.addLayout(title_layout)
        layout.addWidget(desc_label)
        
        # Conectar click
        widget.mousePressEvent = lambda event: self.select_result(result)
        
        return widget
    
    def clear_results(self):
        """Limpia todos los resultados mostrados."""
        while self.results_layout.count():
            child = self.results_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def select_result(self, result):
        """Selecciona un resultado y cierra la búsqueda."""
        self.result_selected.emit(result)
        self.hide_search()
    
    def select_first_result(self):
        """Selecciona el primer resultado disponible."""
        if self.results_layout.count() > 0:
            # Obtener el primer widget de resultado
            first_widget = self.results_layout.itemAt(0).widget()
            if first_widget and hasattr(first_widget, 'mousePressEvent'):
                first_widget.mousePressEvent(None)
    
    def keyPressEvent(self, event):
        """Maneja eventos de teclado."""
        if event.key() == Qt.Key.Key_Escape:
            self.hide_search()
        else:
            super().keyPressEvent(event)