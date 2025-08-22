# -*- coding: utf-8 -*-
"""
Breadcrumb Widget - Navegación por migas de pan
Proporciona navegación contextual en todos los módulos
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtGui import QFont


class BreadcrumbWidget(QWidget):
    """Widget de navegación por migas de pan."""
    
    # Señales
    breadcrumb_clicked = pyqtSignal(str)  # Emite el nombre del breadcrumb clickeado
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.breadcrumbs = []
        self.setup_ui()
        self.apply_styles()
    
    def setup_ui(self):
        """Configura la interfaz del widget."""
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)
        
        # Icono de inicio
        self.home_btn = QPushButton("🏠")
        self.home_btn.setToolTip("Ir al Dashboard")
        self.home_btn.clicked.connect(lambda: self.breadcrumb_clicked.emit("Dashboard"))
        self.layout.addWidget(self.home_btn)
    
    def apply_styles(self):
        """Aplica estilos al widget."""
        self.setStyleSheet("""
            BreadcrumbWidget {
                background: transparent;
                padding: 5px 0px;
            }
            QPushButton {
                background: transparent;
                border: none;
                color: #667eea;
                font-weight: 500;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #f0f0f0;
                color: #4c51bf;
            }
            QLabel {
                color: #999;
                font-size: 13px;
                padding: 4px 2px;
            }
        """)
    
    def set_breadcrumbs(self, breadcrumbs_list):
        """
        Establece la lista de breadcrumbs.
        
        Args:
            breadcrumbs_list: Lista de strings con los nombres de las migas
        """
        # Limpiar breadcrumbs existentes (excepto el botón home)
        self.clear_breadcrumbs()
        
        self.breadcrumbs = breadcrumbs_list
        
        for i, breadcrumb in enumerate(breadcrumbs_list):
            # Agregar separador antes del breadcrumb (excepto el primero)
            if i > 0 or len(breadcrumbs_list) > 0:
                separator = QLabel("›")
                separator.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.layout.addWidget(separator)
            
            # Crear botón o label según si es el último elemento
            if i == len(breadcrumbs_list) - 1:
                # Último elemento - mostrar como label (no clickeable)
                label = QLabel(breadcrumb)
                label.setStyleSheet("""
                    QLabel {
                        color: #333;
                        font-weight: bold;
                        font-size: 13px;
                        padding: 4px 8px;
                    }
                """)
                self.layout.addWidget(label)
            else:
                # Elementos anteriores - mostrar como botones clickeables
                btn = QPushButton(breadcrumb)
                btn.clicked.connect(lambda checked, name=breadcrumb: self.breadcrumb_clicked.emit(name))
                self.layout.addWidget(btn)
        
        # Agregar stretch al final
        self.layout.addStretch()
    
    def clear_breadcrumbs(self):
        """Limpia todos los breadcrumbs excepto el botón home."""
        while self.layout.count() > 1:
            child = self.layout.takeAt(1)
            if child.widget():
                child.widget().deleteLater()
    
    def add_breadcrumb(self, name):
        """Agrega un breadcrumb al final de la lista."""
        current_breadcrumbs = self.breadcrumbs.copy()
        current_breadcrumbs.append(name)
        self.set_breadcrumbs(current_breadcrumbs)
    
    def navigate_to(self, target_breadcrumb):
        """
        Navega a un breadcrumb específico, eliminando los que están después.
        
        Args:
            target_breadcrumb: Nombre del breadcrumb objetivo
        """
        try:
            index = self.breadcrumbs.index(target_breadcrumb)
            new_breadcrumbs = self.breadcrumbs[:index + 1]
            self.set_breadcrumbs(new_breadcrumbs)
        except ValueError:
            # El breadcrumb no existe en la lista actual
            pass


class ModuleBreadcrumb(BreadcrumbWidget):
    """Breadcrumb especializado para módulos con patrones comunes."""
    
    def __init__(self, module_name, parent=None):
        super().__init__(parent)
        self.module_name = module_name
        self.set_module_context(module_name)
    
    def set_module_context(self, module_name):
        """Establece el contexto del módulo."""
        self.set_breadcrumbs([module_name])
    
    def set_sub_context(self, sub_context):
        """Establece un sub-contexto dentro del módulo."""
        self.set_breadcrumbs([self.module_name, sub_context])
    
    def set_item_context(self, sub_context, item_name):
        """Establece contexto para un ítem específico."""
        self.set_breadcrumbs([self.module_name, sub_context, item_name])


class SmartBreadcrumb(BreadcrumbWidget):
    """Breadcrumb inteligente que detecta automáticamente el contexto."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.context_history = []
    
    def auto_detect_context(self, current_view, current_action=None, current_item=None):
        """
        Detecta automáticamente el contexto basado en la vista actual.
        
        Args:
            current_view: Nombre de la vista actual
            current_action: Acción actual (crear, editar, ver, etc.)
            current_item: Item específico si aplica
        """
        breadcrumbs = []
        
        # Mapeo de vistas a breadcrumbs
        view_mapping = {
            'InventarioView': 'Inventario',
            'ObrasView': 'Obras', 
            'PedidosView': 'Pedidos',
            'ComprasView': 'Compras',
            'UsuariosView': 'Usuarios',
            'ConfiguracionView': 'Configuración',
            'VidriosView': 'Vidrios',
            'NotificacionesView': 'Notificaciones'
        }
        
        # Agregar módulo base
        if current_view in view_mapping:
            breadcrumbs.append(view_mapping[current_view])
        
        # Agregar acción si existe
        if current_action:
            action_names = {
                'create': 'Crear Nuevo',
                'edit': 'Editar',
                'view': 'Ver Detalles',
                'list': 'Lista',
                'reports': 'Reportes',
                'settings': 'Configuración'
            }
            if current_action in action_names:
                breadcrumbs.append(action_names[current_action])
        
        # Agregar item específico si existe
        if current_item:
            breadcrumbs.append(str(current_item))
        
        self.set_breadcrumbs(breadcrumbs)
        
        # Guardar en historial para navegación
        self.context_history.append({
            'view': current_view,
            'action': current_action, 
            'item': current_item,
            'breadcrumbs': breadcrumbs.copy()
        })
    
    def get_navigation_history(self):
        """Retorna el historial de navegación."""
        return self.context_history
    
    def clear_history(self):
        """Limpia el historial de navegación."""
        self.context_history.clear()