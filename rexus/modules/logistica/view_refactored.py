"""
Vista de Logística Refactorizada

Versión modular y bien estructurada de la vista de logística.
Utiliza componentes separados para cada pestaña y centraliza la gestión.
"""

from typing import Optional, Dict, Any, List
from PyQt6.QtCore import pyqtSignal, QWidget
from PyQt6.QtWidgets import QVBoxLayout, QTabWidget

# Importar componentes refactorizados
from .constants import ICONS, MESSAGES
from .styles import MAIN_STYLE, TAB_STYLE
from .tabs import TabEntregas, TabServicios, TabMapa, TabEstadisticas
from .widgets import NotificationManager
from .dialogs import DialogoNuevaEntrega

# Importar validadores
from rexus.utils.form_validators import FormValidator, FormValidatorManager, validacion_direccion


class LogisticaViewRefactored(QWidget):
    """
    Vista modernizada y refactorizada para gestión de logística.
    
    Características principales:
    - Arquitectura modular con pestañas separadas
    - Estilos centralizados con mejor contraste
    - Componentes reutilizables
    - Mejor separación de responsabilidades
    - Tipado y documentación mejorados
    """
    
    # Señales principales (compatibilidad con vista original)
    entrega_seleccionada = pyqtSignal(dict)
    crear_entrega_solicitada = pyqtSignal(dict)
    actualizar_entrega_solicitada = pyqtSignal(dict)
    eliminar_entrega_solicitada = pyqtSignal(int)
    
    # Nuevas señales para acciones generales
    action_requested = pyqtSignal(str, dict)  # acción, datos
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Componentes principales
        self.controller: Optional[Any] = None
        self.notification_manager = NotificationManager()
        
        # Referencias a las pestañas
        self.tab_entregas: Optional[TabEntregas] = None
        self.tab_servicios: Optional[TabServicios] = None
        self.tab_mapa: Optional[TabMapa] = None
        self.tab_estadisticas: Optional[TabEstadisticas] = None
        
        # Datos centralizados
        self.entregas_data: List[Dict[str, Any]] = []
        
        # Inicializar interfaz
        self.init_ui()
        self.setup_connections()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario."""
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Aplicar estilos mejorados
        self.setStyleSheet(MAIN_STYLE + TAB_STYLE)
        
        # Crear widget de pestañas
        self.tabs = QTabWidget()
        self.create_tabs()
        
        main_layout.addWidget(self.tabs)
    
    def create_tabs(self):
        """Crea todas las pestañas del módulo."""
        # Pestaña de entregas
        self.tab_entregas = TabEntregas(self)
        self.tabs.addTab(self.tab_entregas, self.tab_entregas.get_display_name())
        
        # Pestaña de servicios
        self.tab_servicios = TabServicios(self)
        self.tabs.addTab(self.tab_servicios, self.tab_servicios.get_display_name())
        
        # Pestaña de mapa
        self.tab_mapa = TabMapa(self)
        self.tabs.addTab(self.tab_mapa, self.tab_mapa.get_display_name())
        
        # Pestaña de estadísticas
        self.tab_estadisticas = TabEstadisticas(self)
        self.tabs.addTab(self.tab_estadisticas, self.tab_estadisticas.get_display_name())
    
    def setup_connections(self):
        """Configura las conexiones entre pestañas y señales."""
        if self.tab_entregas:
            # Conectar señales de entregas para compatibilidad
            self.tab_entregas.entrega_seleccionada.connect(self.entrega_seleccionada.emit)
            self.tab_entregas.crear_entrega_solicitada.connect(self.crear_entrega_solicitada.emit)
            self.tab_entregas.actualizar_entrega_solicitada.connect(self.actualizar_entrega_solicitada.emit)
            self.tab_entregas.eliminar_entrega_solicitada.connect(self.eliminar_entrega_solicitada.emit)
            
            # Conectar acciones generales
            self.tab_entregas.action_requested.connect(self.handle_tab_action)
        
        if self.tab_servicios:
            self.tab_servicios.servicio_generado.connect(self.on_servicio_generado)
            self.tab_servicios.action_requested.connect(self.handle_tab_action)
        
        if self.tab_mapa:
            self.tab_mapa.marcador_agregado.connect(self.on_marcador_agregado)
            self.tab_mapa.ubicacion_seleccionada.connect(self.on_ubicacion_seleccionada)
            self.tab_mapa.action_requested.connect(self.handle_tab_action)
        
        if self.tab_estadisticas:
            self.tab_estadisticas.estadisticas_actualizadas.connect(self.on_estadisticas_actualizadas)
            self.tab_estadisticas.action_requested.connect(self.handle_tab_action)
    
    def handle_tab_action(self, action: str, data: Dict[str, Any]):
        """Maneja acciones solicitadas por las pestañas."""
        # Acciones de entregas
        if action == "mostrar_dialogo_nueva_entrega":
            self.mostrar_dialogo_nueva_entrega()
        elif action == "mostrar_dialogo_editar_entrega":
            self.mostrar_dialogo_editar_entrega(data)
        elif action == "cargar_entregas":
            self.cargar_entregas()
        elif action == "exportar_entregas":
            self.exportar_entregas(data.get("data", []))
        
        # Acciones de estadísticas
        elif action == "cargar_estadisticas":
            self.cargar_estadisticas()
        
        # Emitir acción general para el controlador
        else:
            self.action_requested.emit(action, data)
    
    # Métodos de compatibilidad con la vista original
    
    def set_controller(self, controller):
        """Establece el controlador para todas las pestañas."""
        self.controller = controller
        
        # Propagar controlador a todas las pestañas
        if self.tab_entregas:
            self.tab_entregas.set_controller(controller)
        if self.tab_servicios:
            self.tab_servicios.set_controller(controller)
        if self.tab_mapa:
            self.tab_mapa.set_controller(controller)
        if self.tab_estadisticas:
            self.tab_estadisticas.set_controller(controller)
    
    def cargar_entregas_en_tabla(self, entregas: List[Dict[str, Any]]):
        """Carga entregas en la tabla (compatibilidad con vista original)."""
        self.entregas_data = entregas
        if self.tab_entregas:
            self.tab_entregas.cargar_entregas_en_tabla(entregas)
    
    def actualizar_estadisticas(self, estadisticas: Dict[str, Any]):
        """Actualiza estadísticas (compatibilidad con vista original)."""
        if self.tab_estadisticas:
            self.tab_estadisticas.actualizar_estadisticas(estadisticas)
    
    def mostrar_mensaje(self, mensaje: str):
        """Muestra mensaje de éxito (compatibilidad)."""
        self.notification_manager.show_success(self, "Información", mensaje)
    
    def mostrar_error(self, mensaje: str):
        """Muestra mensaje de error (compatibilidad)."""
        self.notification_manager.show_error(self, "Error", mensaje)
    
    # Métodos específicos de acciones
    
    def mostrar_dialogo_nueva_entrega(self):
        """Muestra diálogo para crear nueva entrega."""
        try:
            dialogo = DialogoNuevaEntrega(self)
            if dialogo.exec() == 1:  # QDialog.Accepted
                datos = dialogo.obtener_datos()
                self.crear_entrega_solicitada.emit(datos)
        except Exception as e:
            self.mostrar_error(f"Error mostrando diálogo: {str(e)}")
    
    def mostrar_dialogo_editar_entrega(self, entrega_data: Dict[str, Any]):
        """Muestra diálogo para editar entrega."""
        try:
            dialogo = DialogoNuevaEntrega(self, entrega_data)
            if dialogo.exec() == 1:
                datos = dialogo.obtener_datos()
                datos["id"] = entrega_data.get("id")
                self.actualizar_entrega_solicitada.emit(datos)
        except Exception as e:
            self.mostrar_error(f"Error editando entrega: {str(e)}")
    
    def cargar_entregas(self):
        """Solicita cargar entregas al controlador."""
        if self.controller and hasattr(self.controller, "cargar_entregas"):
            self.controller.cargar_entregas()
        else:
            # Datos demo si no hay controlador
            self.cargar_entregas_demo()
    
    def cargar_entregas_demo(self):
        """Carga datos demo de entregas."""
        entregas_demo = [
            {
                "id": 1,
                "fecha_programada": "2025-08-15",
                "direccion": "Calle 7 y 50, La Plata",
                "estado": "Programada",
                "contacto": "Juan Pérez - 2214567890",
                "observaciones": "Entregar en horario de oficina"
            },
            {
                "id": 2,
                "fecha_programada": "2025-08-16", 
                "direccion": "Av. 1 y 60, La Plata",
                "estado": "En Tránsito",
                "contacto": "María García - 2215678901",
                "observaciones": "Llamar antes de llegar"
            }
        ]
        self.cargar_entregas_en_tabla(entregas_demo)
    
    def cargar_estadisticas(self):
        """Solicita cargar estadísticas al controlador."""
        if self.controller and hasattr(self.controller, "obtener_estadisticas"):
            try:
                estadisticas = self.controller.obtener_estadisticas()
                self.actualizar_estadisticas(estadisticas)
            except Exception as e:
                self.mostrar_error(f"Error cargando estadísticas: {str(e)}")
        else:
            # Generar estadísticas demo
            if self.tab_estadisticas:
                self.tab_estadisticas.generar_estadisticas_demo()
    
    def exportar_entregas(self, data: List[Dict[str, Any]]):
        """Exporta datos de entregas."""
        self.notification_manager.show_success(
            self, "Exportar", f"Exportando {len(data)} entregas a Excel..."
        )
    
    # Handlers de eventos de pestañas
    
    def on_servicio_generado(self, servicio_data: Dict[str, Any]):
        """Maneja la generación de un nuevo servicio."""
        # Aquí se podría integrar con el sistema de entregas
        self.mostrar_mensaje(f"Servicio generado: {servicio_data.get('tipo_servicio', 'N/A')}")
    
    def on_marcador_agregado(self, marcador_data: Dict[str, Any]):
        """Maneja la adición de marcadores en el mapa."""
        direccion = marcador_data.get('direccion', 'N/A')
        self.mostrar_mensaje(f"Marcador agregado: {direccion}")
    
    def on_ubicacion_seleccionada(self, lat: float, lng: float):
        """Maneja la selección de ubicación en el mapa."""
        self.mostrar_mensaje(f"Ubicación seleccionada: {lat:.4f}, {lng:.4f}")
    
    def on_estadisticas_actualizadas(self, estadisticas: Dict[str, Any]):
        """Maneja la actualización de estadísticas."""
        total = estadisticas.get("total_entregas", 0)
        self.mostrar_mensaje(f"Estadísticas actualizadas - Total: {total} entregas")
    
    # Métodos de utilidad
    
    def get_active_tab(self) -> Optional[str]:
        """Retorna el nombre de la pestaña activa."""
        current_index = self.tabs.currentIndex()
        tab_names = ["entregas", "servicios", "mapa", "estadisticas"]
        return tab_names[current_index] if 0 <= current_index < len(tab_names) else None
    
    def switch_to_tab(self, tab_name: str):
        """Cambia a una pestaña específica."""
        tab_indices = {
            "entregas": 0,
            "servicios": 1, 
            "mapa": 2,
            "estadisticas": 3
        }
        
        if tab_name in tab_indices:
            self.tabs.setCurrentIndex(tab_indices[tab_name])
    
    def refresh_all_tabs(self):
        """Refresca todas las pestañas."""
        if self.tab_entregas:
            self.tab_entregas.refresh()
        if self.tab_estadisticas:
            self.tab_estadisticas.refresh()
    
    def get_all_data(self) -> Dict[str, Any]:
        """Retorna todos los datos de todas las pestañas."""
        return {
            "entregas": self.tab_entregas.get_data() if self.tab_entregas else {},
            "servicios": self.tab_servicios.get_data() if self.tab_servicios else {},
            "mapa": self.tab_mapa.get_data() if self.tab_mapa else {},
            "estadisticas": self.tab_estadisticas.get_data() if self.tab_estadisticas else {}
        }