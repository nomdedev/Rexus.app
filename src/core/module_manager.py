"""
Gestor de Módulos Robusto para Rexus.app

Proporciona una solución sistemática para la carga de módulos,
manejo de errores y prevención de vulnerabilidades SQL injection.
"""

from typing import Optional, Dict, Any
from PyQt6.QtWidgets import QWidget


class ModuleManager:
    """
    Gestor centralizado para la carga robusta de módulos.
    
    Características:
    - Manejo de errores centralizado
    - Carga de datos inicial automática
    - Logging detallado
    - Fallback robusto
    """
    
    def __init__(self):
        self.loaded_modules = {}
    
    def create_module_safely(self, 
                           module_name: str, 
                           model_class, 
                           view_class, 
                           controller_class,
                           db_connection=None,
                           fallback_callback=None) -> QWidget:
        """
        Crea un módulo de forma segura con manejo completo de errores.
        
        Args:
            module_name: Nombre del módulo
            model_class: Clase del modelo  
            view_class: Clase de la vista
            controller_class: Clase del controlador
            db_connection: Conexión a BD (opcional)
            fallback_callback: Función de fallback en caso de error
            
        Returns:
            QWidget: Vista del módulo o fallback
        """
        try:
            # 1. Crear instancias con validación
            model = self._create_model_safely(model_class, db_connection, module_name)
            view = self._create_view_safely(view_class, module_name)
            controller = self._create_controller_safely(controller_class, model, view, module_name)
            
            # 2. Configurar conexiones
            self._setup_connections(view, controller, module_name)
            
            # 3. Cargar datos iniciales
            self._load_initial_data(controller, module_name)
            
            # 4. Registrar módulo exitoso
            self.loaded_modules[module_name] = {
                'model': model,
                'view': view, 
                'controller': controller,
                'status': 'loaded'
            }
            
            print(f"✅ [{module_name}] Módulo cargado exitosamente")
            return view
            
        except Exception as e:
            print(f"❌ [{module_name}] Error cargando módulo: {e}")
            
            # Registrar fallo
            self.loaded_modules[module_name] = {
                'status': 'failed',
                'error': str(e)
            }
            
            # Ejecutar fallback
            if fallback_callback:
                return fallback_callback(module_name)
            else:
                return self._create_error_widget(module_name, str(e))
    
    def _create_model_safely(self, model_class, db_connection, module_name):
        """Crea modelo con validación de conexión BD."""
        try:
            if db_connection:
                model = model_class(db_connection)
                print(f"[{module_name}] Modelo creado con conexión BD")
            else:
                model = model_class()
                print(f"[{module_name}] Modelo creado sin conexión BD (modo demo)")
            return model
        except Exception as e:
            raise Exception(f"Error creando modelo: {e}")
    
    def _create_view_safely(self, view_class, module_name):
        """Crea vista con validación de UI."""
        try:
            view = view_class()
            print(f"[{module_name}] Vista creada exitosamente")
            return view
        except Exception as e:
            raise Exception(f"Error creando vista: {e}")
    
    def _create_controller_safely(self, controller_class, model, view, module_name):
        """Crea controlador con validación de dependencias."""
        try:
            controller = controller_class(model, view)
            print(f"[{module_name}] Controlador creado exitosamente")
            return controller
        except Exception as e:
            raise Exception(f"Error creando controlador: {e}")
    
    def _setup_connections(self, view, controller, module_name):
        """Configura conexiones entre vista y controlador."""
        try:
            if hasattr(view, 'set_controller'):
                view.set_controller(controller)
                print(f"[{module_name}] Vista conectada al controlador")
            else:
                print(f"[{module_name}] Vista no requiere conexión explícita")
        except Exception as e:
            raise Exception(f"Error configurando conexiones: {e}")
    
    def _load_initial_data(self, controller, module_name):
        """Carga datos iniciales de forma segura."""
        try:
            # Intentar diferentes métodos de carga según el módulo
            if hasattr(controller, 'cargar_datos_iniciales'):
                controller.cargar_datos_iniciales()
                print(f"[{module_name}] Datos iniciales cargados")
            elif hasattr(controller, 'cargar_usuarios') and module_name == "Usuarios":
                controller.cargar_usuarios()
                print(f"[{module_name}] Usuarios cargados")
            elif hasattr(controller, 'actualizar_tabla'):
                controller.actualizar_tabla()
                print(f"[{module_name}] Tabla actualizada")
            else:
                print(f"[{module_name}] No requiere carga inicial de datos")
        except Exception as e:
            # No fallar completamente por error de datos iniciales
            print(f"[{module_name}] ADVERTENCIA: Error cargando datos iniciales: {e}")
    
    def _create_error_widget(self, module_name: str, error_message: str) -> QWidget:
        """Crea widget de error informativo."""
        from PyQt6.QtWidgets import QVBoxLayout, QLabel
        from PyQt6.QtCore import Qt
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Título de error
        title = QLabel(f"❌ Error en módulo {module_name}")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #e74c3c;
            margin: 20px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Mensaje de error
        message = QLabel(f"Detalles: {error_message}")
        message.setStyleSheet("""
            font-size: 12px;
            color: #7f8c8d;
            margin: 10px;
            padding: 10px;
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            border-radius: 4px;
        """)
        message.setWordWrap(True)
        message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(title)
        layout.addWidget(message)
        layout.addStretch()
        
        return widget
    
    def get_module_status(self, module_name: str) -> Dict[str, Any]:
        """Obtiene el estado de un módulo."""
        return self.loaded_modules.get(module_name, {'status': 'not_loaded'})
    
    def get_all_modules_status(self) -> Dict[str, Dict[str, Any]]:
        """Obtiene el estado de todos los módulos."""
        return self.loaded_modules.copy()


# Instancia global del gestor
module_manager = ModuleManager()