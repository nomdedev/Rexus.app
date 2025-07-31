"""Controlador de Logística"""

from PyQt6.QtCore import QObject
from rexus.utils.error_handler import ErrorHandler, safe_method_decorator


class LogisticaController(QObject):
    def __init__(self, model=None, view=None, db_connection=None, usuarios_model=None):
        super().__init__()
        self.model = model
        self.view = view
        self.db_connection = db_connection
        self.usuarios_model = usuarios_model
        self.usuario_actual = "SISTEMA"
        
        # Conectar señales de la vista
        if self.view:
            self.view.crear_entrega_solicitada.connect(self.guardar_entrega)
    
    @safe_method_decorator("cargar datos iniciales de logística")
    def cargar_datos_iniciales(self):
        """Carga los datos iniciales del módulo."""
        self.cargar_entregas()
        self.cargar_services()
    
    def cargar_entregas(self):
        """Carga las entregas en la tabla."""
        if self.model and self.view:
            try:
                entregas = self.model.obtener_entregas()
                self.view.cargar_entregas_en_tabla(entregas)
            except Exception as e:
                print(f"Error cargando entregas: {e}")

    def guardar_entrega(self, datos):
        """Guarda una nueva entrega."""
        if self.model:
            try:
                self.model.crear_entrega(datos)
                self.cargar_entregas()
                if self.view:
                    ErrorHandler.mostrar_informacion(self.view, "Logística", "Entrega guardada exitosamente")
            except Exception as e:
                ErrorHandler.manejar_error_base_datos(self.view, "guardar entrega", e)

    def cargar_services(self):
        """Carga los servicios en la tabla."""
        if self.model and self.view and hasattr(self.model, 'obtener_services'):
            try:
                services = self.model.obtener_services()
                self.view.cargar_services_en_tabla(services)
            except Exception as e:
                print(f"Error cargando servicios: {e}")

    def guardar_service(self, datos):
        """Guarda un nuevo servicio."""
        if self.model and hasattr(self.model, 'crear_service'):
            try:
                self.model.crear_service(datos)
                self.cargar_services()
            except Exception as e:
                print(f"Error guardando servicio: {e}")
                if self.view:
                    self.view.mostrar_error(f"Error al guardar servicio: {str(e)}")

    @safe_method_decorator("generar servicios de logística")
    def generar_servicios_automaticos(self):
        """Abre el diálogo para generar servicios automáticamente."""
        try:
            from .view import DialogoGenerarServicio
            
            dialogo = DialogoGenerarServicio(self.view)
            resultado = dialogo.exec()
            
            if resultado == dialogo.DialogCode.Accepted:
                # Obtener la configuración del diálogo
                configuracion = dialogo.obtener_configuracion()
                
                # Procesar la generación de servicios
                self._procesar_generacion_servicios(configuracion)
                
                # Recargar datos
                self.cargar_services()
                self.cargar_entregas()
                
        except Exception as e:
            print(f"Error abriendo diálogo de generación: {e}")
            if self.view:
                self.view.mostrar_error(f"Error al abrir generador de servicios: {str(e)}")

    def _procesar_generacion_servicios(self, configuracion):
        """Procesa la generación de servicios con la configuración especificada."""
        try:
            # Aquí iría la lógica real para generar servicios
            # Por ahora es una implementación de demostración
            
            print("[INFO] Procesando generación de servicios con configuración:")
            for clave, valor in configuracion.items():
                print(f"  - {clave}: {valor}")
            
            # Simulación de servicios generados
            servicios_generados = self._simular_servicios_generados(configuracion)
            
            # Guardar servicios en el modelo (si existe el método)
            if self.model and hasattr(self.model, 'crear_servicios_bulk'):
                self.model.crear_servicios_bulk(servicios_generados)
            
            print(f"[SUCCESS] Se generaron {len(servicios_generados)} servicios de logística")
            
        except Exception as e:
            print(f"[ERROR] Error procesando generación de servicios: {e}")
            raise

    def _simular_servicios_generados(self, configuracion):
        """Simula la generación de servicios basada en la configuración."""
        from datetime import datetime, timedelta
        import random
        
        servicios = []
        
        # Generar servicios basados en la configuración
        fecha_base = datetime.strptime(configuracion['fecha_desde'], '%Y-%m-%d')
        fecha_fin = datetime.strptime(configuracion['fecha_hasta'], '%Y-%m-%d')
        
        zonas = ["Norte", "Sur", "Este", "Oeste", "Centro"] if configuracion['zona'] == "Todas las zonas" else [configuracion['zona'].replace("Zona ", "")]
        
        # Generar entre 3-8 servicios según la configuración
        num_servicios = random.randint(3, 8)
        
        for i in range(num_servicios):
            fecha_servicio = fecha_base + timedelta(days=random.randint(0, (fecha_fin - fecha_base).days))
            zona = random.choice(zonas)
            
            servicio = {
                'codigo': f"LOG-{fecha_servicio.strftime('%Y%m%d')}-{i+1:03d}",
                'descripcion': f"Servicio de entrega - Zona {zona}",
                'zona': zona,
                'fecha_programada': fecha_servicio.strftime('%Y-%m-%d'),
                'tipo_vehiculo': configuracion['tipo_vehiculo'],
                'capacidad_maxima': configuracion['capacidad_maxima'],
                'max_paradas': configuracion['max_paradas'],
                'estado': 'PROGRAMADO',
                'observaciones': f"Generado automáticamente - {configuracion['criterio_optimizacion']}",
                'usuario_creacion': self.usuario_actual,
                'fecha_creacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            servicios.append(servicio)
        
        return servicios
