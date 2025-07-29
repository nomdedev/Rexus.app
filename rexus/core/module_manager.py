"""
Gestor de Módulos Robusto para Rexus.app

Proporciona una solución sistemática para la carga de módulos,
manejo de errores y prevención de vulnerabilidades SQL injection.
"""

from typing import Optional, Dict, Any
from PyQt6.QtWidgets import QWidget
from rexus.utils.module_utils import module_registry, normalize_module_name


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
            
            # SIEMPRE mostrar widget de error detallado en lugar del fallback genérico
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
        """Carga datos iniciales de forma segura usando registry centralizado."""
        try:
            # Normalizar nombre del módulo para búsqueda consistente
            normalized_name = normalize_module_name(module_name)
            module_key = module_registry.normalize_and_find(module_name)
            
            # Mapeo robusto basado en registry 
            loader_method_map = {
                'usuarios': 'cargar_usuarios',
                'obras': 'cargar_obras',
                'inventario': 'cargar_inventario', 
                'compras': 'cargar_compras',
                'pedidos': 'cargar_pedidos',
                'logistica': 'cargar_logistica',
                'herrajes': 'cargar_herrajes',
                'vidrios': 'cargar_vidrios',
                'mantenimiento': 'cargar_mantenimiento',
                'auditoria': 'cargar_auditoria',
                'administracion': 'cargar_administracion',
                'contabilidad': 'cargar_contabilidad',
                'configuracion': 'cargar_configuracion'
            }
            
            # Métodos de carga alternativos en orden de prioridad
            fallback_methods = ["cargar_datos_iniciales", "actualizar_tabla", "inicializar_datos", "refresh_data"]
            
            # 1. Intentar método específico basado en registry
            if module_key and module_key in loader_method_map:
                specific_method = loader_method_map[module_key]
                if hasattr(controller, specific_method):
                    getattr(controller, specific_method)()
                    print(f"✅ [{module_name}] Datos cargados con método específico: {specific_method}")
                    return
                else:
                    print(f"⚠️  [{module_name}] Método {specific_method} no encontrado en controlador")
            
            # 2. Intentar métodos genéricos de fallback
            for method_name in fallback_methods:
                if hasattr(controller, method_name):
                    getattr(controller, method_name)()
                    print(f"✅ [{module_name}] Datos cargados con método genérico: {method_name}")
                    return
            
            # 3. Módulo no requiere carga inicial
            print(f"ℹ️  [{module_name}] No requiere carga inicial de datos")
            
        except Exception as e:
            # No fallar completamente por error de datos iniciales
            print(f"❌ [{module_name}] Error cargando datos iniciales: {e}")
            # Log más detallado para debugging
            import traceback
            print(f"[DEBUG] Stack trace para {module_name}:")
            print(f"[DEBUG] {traceback.format_exc()}")
            
            # Intentar mostrar error en UI si es posible
            self._show_data_loading_error(module_name, str(e))
    
    def _show_data_loading_error(self, module_name: str, error_message: str):
        """Muestra error de carga de datos de forma visual."""
        try:
            from PyQt6.QtWidgets import QMessageBox
            from PyQt6.QtCore import QTimer
            
            # Crear mensaje de error no bloqueante
            def show_error():
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Warning)
                msg.setWindowTitle(f"Error cargando {module_name}")
                msg.setText(f"No se pudieron cargar los datos iniciales del módulo {module_name}")
                msg.setDetailedText(f"Error técnico: {error_message}")
                msg.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg.exec()
            
            # Mostrar después de que la UI esté lista
            QTimer.singleShot(1000, show_error)
            
        except Exception as ui_error:
            print(f"[ERROR] No se pudo mostrar error de UI: {ui_error}")
    
    def _create_error_widget(self, module_name: str, error_message: str) -> QWidget:
        """Crea widget de error informativo con diagnóstico detallado."""
        from PyQt6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QTextEdit, QGroupBox
        from PyQt6.QtCore import Qt
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título de error
        title = QLabel(f"❌ Error en módulo {module_name}")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #e74c3c;
            margin-bottom: 20px;
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Diagnóstico del error
        diagnosis = self._analyze_error(error_message)
        diagnosis_label = QLabel(f"📋 Diagnóstico: {diagnosis}")
        diagnosis_label.setStyleSheet("""
            font-size: 14px;
            color: #2c3e50;
            margin-bottom: 15px;
            font-weight: bold;
        """)
        diagnosis_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        diagnosis_label.setWordWrap(True)
        
        # Grupo de detalles técnicos
        details_group = QGroupBox("🔧 Detalles Técnicos")
        details_layout = QVBoxLayout(details_group)
        
        # Mensaje de error detallado
        error_text = QTextEdit()
        error_text.setPlainText(error_message)
        error_text.setReadOnly(True)
        error_text.setMaximumHeight(100)
        error_text.setStyleSheet("""
            QTextEdit {
                font-family: monospace;
                font-size: 11px;
                color: #7f8c8d;
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        
        details_layout.addWidget(error_text)
        
        # Sugerencias de solución
        suggestions = self._get_error_suggestions(error_message, module_name)
        if suggestions:
            suggestions_label = QLabel(f"💡 Sugerencias:\n{suggestions}")
            suggestions_label.setStyleSheet("""
                font-size: 12px;
                color: #27ae60;
                margin-top: 10px;
                padding: 10px;
                background-color: #eafaf1;
                border: 1px solid #d5f4e6;
                border-radius: 4px;
            """)
            suggestions_label.setWordWrap(True)
            details_layout.addWidget(suggestions_label)
        
        layout.addWidget(title)
        layout.addWidget(diagnosis_label)
        layout.addWidget(details_group)
        layout.addStretch()
        
        return widget
    
    def _analyze_error(self, error_message: str) -> str:
        """Analiza el error y proporciona un diagnóstico."""
        error_lower = error_message.lower()
        
        if "connection" in error_lower or "conexión" in error_lower:
            return "Problema de conexión a la base de datos"
        elif "import" in error_lower or "module" in error_lower:
            return "Error de importación de módulos Python"
        elif "table" in error_lower or "tabla" in error_lower:
            return "Problema con tablas de base de datos"
        elif "sql" in error_lower or "database" in error_lower:
            return "Error en operación de base de datos"
        elif "permission" in error_lower or "access" in error_lower:
            return "Problema de permisos o acceso"
        else:
            return "Error general del módulo"
    
    def _get_error_suggestions(self, error_message: str, module_name: str) -> str:
        """Proporciona sugerencias específicas según el error."""
        error_lower = error_message.lower()
        suggestions = []
        
        if "connection" in error_lower:
            suggestions.extend([
                "• Verificar que SQL Server esté ejecutándose",
                "• Revisar variables de entorno de base de datos",
                "• Comprobar credenciales de conexión"
            ])
        
        if "table" in error_lower:
            suggestions.extend([
                "• Verificar que las tablas existan en la base de datos",
                "• Ejecutar scripts de creación de tablas",
                "• Revisar estructura de la base de datos"
            ])
        
        if "import" in error_lower:
            suggestions.extend([
                "• Verificar que todos los archivos del módulo existan",
                "• Revisar sintaxis de los archivos Python",
                "• Comprobar dependencias del módulo"
            ])
        
        if not suggestions:
            suggestions.append("• Revisar logs de la aplicación para más detalles")
        
        return "\n".join(suggestions)
    
    def get_module_status(self, module_name: str) -> Dict[str, Any]:
        """Obtiene el estado de un módulo."""
        return self.loaded_modules.get(module_name, {'status': 'not_loaded'})
    
    def get_all_modules_status(self) -> Dict[str, Dict[str, Any]]:
        """Obtiene el estado de todos los módulos."""
        return self.loaded_modules.copy()


# Instancia global del gestor
module_manager = ModuleManager()