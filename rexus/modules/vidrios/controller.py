"""Controlador de Vidrios"""

from PyQt6.QtCore import QObject, pyqtSignal
from rexus.core.auth_decorators import auth_required, admin_required

# Importar sistema de mensajería centralizado y logging
try:
    from rexus.utils.message_system import show_success, show_error, show_warning, show_info
    MESSAGING_AVAILABLE = True
except ImportError:
    # Fallback temporal con QMessageBox
    from PyQt6.QtWidgets import QMessageBox
    def show_success(parent, title, message): QMessageBox.information(parent, title, message)
    def show_error(parent, title, message): QMessageBox.critical(parent, title, message)
    def show_warning(parent, title, message): QMessageBox.warning(parent, title, message)
    def show_info(parent, title, message): QMessageBox.information(parent, title, message)
    MESSAGING_AVAILABLE = False

try:
    from rexus.utils.app_logger import get_logger
    logger = get_logger("vidrios.controller")
    LOGGING_AVAILABLE = True
except ImportError:
    # Fallback para logging
    class DummyLogger:
        def info(self, msg): print(f"[INFO] {msg}")
        def warning(self, msg): print(f"[WARNING] {msg}")
        def error(self, msg): print(f"[ERROR] {msg}")
        def debug(self, msg): print(f"[DEBUG] {msg}")
    logger = DummyLogger()
    LOGGING_AVAILABLE = False

class VidriosController(QObject):

    vidrio_agregado = pyqtSignal(dict)
    vidrio_actualizado = pyqtSignal(dict)
    vidrio_eliminado = pyqtSignal(int)
    pedido_creado = pyqtSignal(int)

    def __init__(self, model=None, view=None, db_connection=None):
        super().__init__()
        self.model = model
        self.view = view
        self.db_connection = db_connection
        self.usuario_actual = "SISTEMA"
        self.conectar_senales()

    def conectar_senales(self):
        """Conecta las señales de la vista con los métodos del controlador."""
        if self.view:
            self.view.buscar_requested.connect(self.buscar_vidrios)
            self.view.agregar_requested.connect(self.agregar_vidrio)
            self.view.editar_requested.connect(self.editar_vidrio)
            self.view.eliminar_requested.connect(self.eliminar_vidrio)
            self.view.asignar_obra_requested.connect(self.asignar_vidrio_obra)
            self.view.crear_pedido_requested.connect(self.crear_pedido)
            self.view.filtrar_requested.connect(self.filtrar_vidrios)
            
            # Conectar señal de exportación
            if hasattr(self.view, 'solicitud_exportar'):
                self.view.solicitud_exportar.connect(self.exportar_vidrios)

    def actualizar_vista(self):
        """Actualiza la vista con los datos más recientes."""
        try:
            if self.view and hasattr(self.view, 'refresh_data'):
                self.view.refresh_data()
            else:
                self.cargar_vidrios()
            logger.info("[VIDRIOS] Vista actualizada exitosamente")
        except Exception as e:
            logger.error(f"[ERROR VIDRIOS] Error actualizando vista: {e}")

    def _validar_datos_vidrio(self, datos_vidrio):
        """
        Valida y sanitiza los datos de vidrio antes de enviar al modelo.
        
        Args:
            datos_vidrio: Dict con datos del vidrio
            
        Returns:
            tuple: (es_valido, datos_sanitizados, mensaje_error)
        """
        if not isinstance(datos_vidrio, dict):
            return False, {}, "Los datos del vidrio deben ser un diccionario"
        
        # Campos requeridos
        campos_requeridos = ['tipo', 'ancho', 'alto']
        for campo in campos_requeridos:
            if campo not in datos_vidrio or not datos_vidrio[campo]:
                return False, {}, f"El campo '{campo}' es requerido"
        
        # Sanitizar datos usando el sistema unificado si está disponible
        try:
            from rexus.utils.unified_sanitizer import unified_sanitizer
            datos_sanitizados = unified_sanitizer.sanitize_dict(datos_vidrio)
        except ImportError:
            # Fallback: sanitización básica
            datos_sanitizados = {}
            for key, value in datos_vidrio.items():
                if isinstance(value, str):
                    datos_sanitizados[key] = str(value).strip()
                else:
                    datos_sanitizados[key] = value
        
        # Validaciones específicas
        try:
            ancho = float(datos_sanitizados.get('ancho', 0))
            alto = float(datos_sanitizados.get('alto', 0))
            
            if ancho <= 0 or alto <= 0:
                return False, {}, "Las dimensiones deben ser mayores a 0"
                
            # Actualizar con valores validados
            datos_sanitizados['ancho'] = ancho
            datos_sanitizados['alto'] = alto
            
        except (ValueError, TypeError):
            return False, {}, "Las dimensiones deben ser números válidos"
        
        logger.debug(f"Datos de vidrio validados: {datos_sanitizados}")
        return True, datos_sanitizados, ""

    def cargar_datos(self, filtros=None):
        """Carga los datos de vidrios en la vista."""
        if not self.model:
            return

        try:
            vidrios = self.model.obtener_todos_vidrios(filtros)
            if self.view:
                self.view.actualizar_tabla(vidrios)

            # Cargar estadísticas
            estadisticas = self.model.obtener_estadisticas()
            if self.view:
                self.view.actualizar_estadisticas(estadisticas)

        except Exception as e:
            self.mostrar_error(f"Error cargando datos: {e}")

    def cargar_datos_iniciales(self):
        """Carga los datos iniciales de vidrios."""
        self.cargar_datos()

    def buscar_vidrios(self, termino):
        """Busca vidrios por término de búsqueda."""
        if not self.model:
            return

        try:
            vidrios = self.model.buscar_vidrios(termino)
            if self.view:
                self.view.actualizar_tabla(vidrios)
        except Exception as e:
            self.mostrar_error(f"Error en búsqueda: {e}")
    def agregar_vidrio(self, datos_vidrio):
        """
        Agrega un nuevo vidrio con validación completa.
        
        Args:
            datos_vidrio: Dict con datos del vidrio
            
        Returns:
            tuple: (exito, mensaje, vidrio_id)
        """
        logger.info(f"Iniciando creación de vidrio para usuario: {self.usuario_actual}")
        
        if not self.model:
            error_msg = "Modelo de vidrios no disponible"
            logger.error(error_msg)
            self.mostrar_error(error_msg)
            return False, error_msg, None

        # Validar datos de entrada
        es_valido, datos_sanitizados, mensaje_error = self._validar_datos_vidrio(datos_vidrio)
        if not es_valido:
            logger.warning(f"Validación fallida: {mensaje_error}")
            self.mostrar_error(f"Error de validación: {mensaje_error}")
            return False, mensaje_error, None

        try:
            # Agregar información de auditoría
            datos_sanitizados['usuario_creacion'] = self.usuario_actual
            
            vidrio_id = self.model.crear_vidrio(datos_sanitizados)
            if vidrio_id:
                success_msg = "Vidrio agregado exitosamente"
                logger.info(f"Vidrio creado con ID: {vidrio_id}")
                
                self.mostrar_mensaje(success_msg, tipo="success")
                self.cargar_datos()
                self.vidrio_agregado.emit(datos_sanitizados)
                
                return True, success_msg, vidrio_id
            else:
                error_msg = "No se pudo crear el vidrio en la base de datos"
                logger.error(error_msg)
                self.mostrar_error(error_msg)
                return False, error_msg, None
                
        except Exception as e:
            error_msg = f"Error agregando vidrio: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.mostrar_error(error_msg)
            return False, error_msg, None
    def editar_vidrio(self, vidrio_id, datos_vidrio):
        """
        Edita un vidrio existente con validación completa.
        
        Args:
            vidrio_id: ID del vidrio a editar
            datos_vidrio: Dict con nuevos datos del vidrio
            
        Returns:
            tuple: (exito, mensaje)
        """
        logger.info(f"Iniciando edición de vidrio ID: {vidrio_id} por usuario: {self.usuario_actual}")
        
        if not self.model:
            error_msg = "Modelo de vidrios no disponible"
            logger.error(error_msg)
            self.mostrar_error(error_msg)
            return False, error_msg

        # Validar ID
        if not vidrio_id or not isinstance(vidrio_id, (int, str)):
            error_msg = "ID de vidrio inválido"
            logger.warning(error_msg)
            self.mostrar_error(error_msg)
            return False, error_msg

        # Validar datos de entrada
        es_valido, datos_sanitizados, mensaje_error = self._validar_datos_vidrio(datos_vidrio)
        if not es_valido:
            logger.warning(f"Validación fallida para ID {vidrio_id}: {mensaje_error}")
            self.mostrar_error(f"Error de validación: {mensaje_error}")
            return False, mensaje_error

        try:
            # Agregar información de auditoría
            datos_sanitizados['usuario_modificacion'] = self.usuario_actual
            
            if self.model.actualizar_vidrio(vidrio_id, datos_sanitizados):
                success_msg = "Vidrio actualizado exitosamente"
                logger.info(f"Vidrio ID: {vidrio_id} actualizado exitosamente")
                
                self.mostrar_mensaje(success_msg, tipo="success")
                self.cargar_datos()
                self.vidrio_actualizado.emit(datos_sanitizados)
                
                return True, success_msg
            else:
                error_msg = "No se pudo actualizar el vidrio en la base de datos"
                logger.error(f"Fallo al actualizar vidrio ID: {vidrio_id}")
                self.mostrar_error(error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Error editando vidrio: {str(e)}"
            logger.error(f"Error editando vidrio ID: {vidrio_id}: {str(e)}", exc_info=True)
            self.mostrar_error(error_msg)
            return False, error_msg

    @admin_required
    def eliminar_vidrio(self, vidrio_id):
        """
        Elimina un vidrio (requiere permisos de administrador).
        
        Args:
            vidrio_id: ID del vidrio a eliminar
            
        Returns:
            tuple: (exito, mensaje)
        """
        logger.info(f"Iniciando eliminación de vidrio ID: {vidrio_id} por usuario: {self.usuario_actual}")
        
        if not self.model:
            error_msg = "Modelo de vidrios no disponible"
            logger.error(error_msg)
            self.mostrar_error(error_msg)
            return False, error_msg

        # Validar ID
        if not vidrio_id or not isinstance(vidrio_id, (int, str)):
            error_msg = "ID de vidrio inválido"
            logger.warning(error_msg)
            self.mostrar_error(error_msg)
            return False, error_msg

        try:
            # Verificar si el vidrio está en uso antes de eliminar
            # (esta lógica puede estar en el modelo, pero es buena práctica verificar aquí también)
            
            if self.model.eliminar_vidrio(vidrio_id):
                success_msg = "Vidrio eliminado exitosamente"
                logger.info(f"Vidrio ID: {vidrio_id} eliminado por administrador: {self.usuario_actual}")
                
                self.mostrar_mensaje(success_msg, tipo="success")
                self.cargar_datos()
                self.vidrio_eliminado.emit(vidrio_id)
                
                return True, success_msg
            else:
                error_msg = "No se pudo eliminar el vidrio (puede estar en uso)"
                logger.warning(f"Fallo al eliminar vidrio ID: {vidrio_id}")
                self.mostrar_error(error_msg)
                return False, error_msg
                
        except Exception as e:
            error_msg = f"Error eliminando vidrio: {str(e)}"
            logger.error(f"Error eliminando vidrio ID: {vidrio_id}: {str(e)}", exc_info=True)
            self.mostrar_error(error_msg)
            return False, error_msg

    def asignar_vidrio_obra(self,
vidrio_id,
        obra_id,
        metros_cuadrados,
        medidas_especificas=None):
        """Asigna un vidrio a una obra específica."""
        if not self.model:
            return

        try:
            if self.model.asignar_vidrio_obra(vidrio_id,
obra_id,
                metros_cuadrados,
                medidas_especificas):
                self.mostrar_mensaje("Vidrio asignado a la obra exitosamente")
            else:
                self.mostrar_error("Error al asignar vidrio a la obra")
        except Exception as e:
            self.mostrar_error(f"Error asignando vidrio a obra: {e}")
    def crear_pedido(self, obra_id, proveedor, vidrios_lista):
        """Crea un pedido de vidrios para una obra."""
        if not self.model:
            return

        try:
            pedido_id = self.model.crear_pedido_obra(obra_id, proveedor, vidrios_lista)
            if pedido_id:
                self.mostrar_mensaje(f"Pedido #{pedido_id} creado exitosamente")
                self.pedido_creado.emit(pedido_id)
            else:
                self.mostrar_error("Error al crear pedido")
        except Exception as e:
            self.mostrar_error(f"Error creando pedido: {e}")

    def filtrar_vidrios(self, filtros):
        """Filtra vidrios por criterios específicos."""
        self.cargar_datos(filtros)

    def obtener_vidrios_por_obra(self, obra_id):
        """Obtiene vidrios asignados a una obra específica."""
        if not self.model:
            return []

        try:
            return self.model.obtener_vidrios_por_obra(obra_id)
        except Exception as e:
            self.mostrar_error(f"Error obteniendo vidrios por obra: {e}")
            return []

    def crear_vidrio(self, datos_vidrio):
        """
        Método de compatibilidad que delega al método principal agregar_vidrio.
        
        Returns:
            tuple: (exito, mensaje, vidrio_id) - Formato consistente
        """
        logger.debug("Método crear_vidrio llamado - delegando a agregar_vidrio")
        return self.agregar_vidrio(datos_vidrio)

    def actualizar_por_obra(self, obra_data):
        """
        Actualiza vidrios cuando se crea una obra.
        
        Args:
            obra_data: Datos de la obra que afecta a los vidrios
        """
        logger.info(f"Actualizando vidrios por cambio en obra: {obra_data.get('id', 'N/A')}")
        
        try:
            # Aquí iría la lógica de actualización específica
            # Por ejemplo, recalcular asignaciones, stock, etc.
            if self.view:
                self.cargar_datos()  # Recargar vista si existe
                
        except Exception as e:
            logger.error(f"Error actualizando vidrios por obra: {str(e)}", exc_info=True)
            self.mostrar_error("Error actualizando vidrios por cambio en obra")

    def mostrar_mensaje(self, mensaje, tipo="info"):
        """
        Muestra un mensaje usando el sistema centralizado.
        
        Args:
            mensaje: Mensaje a mostrar
            tipo: Tipo de mensaje ('info', 'success', 'warning', 'error')
        """
        logger.info(f"Mensaje mostrado: {mensaje}")
        
        if self.view:
            if tipo == "success":
                show_success(self.view, "Vidrios", mensaje)
            elif tipo == "warning":
                show_warning(self.view, "Vidrios", mensaje)
            elif tipo == "error":
                show_error(self.view, "Error - Vidrios", mensaje)
            else:
                show_info(self.view, "Vidrios", mensaje)

    def cargar_pagina(self, pagina, registros_por_pagina=50):
        """Carga una página específica de datos."""
        try:
            if self.model:
                offset = (pagina - 1) * registros_por_pagina

                # Obtener datos paginados
                datos, total_registros = self.model.obtener_datos_paginados(
                    offset=offset,
                    limit=registros_por_pagina
                )

                if self.view:
                    # Cargar datos en la tabla
                    if hasattr(self.view, 'cargar_datos_en_tabla'):
                        self.view.cargar_datos_en_tabla(datos)

                    # Actualizar controles de paginación
                    total_paginas = (total_registros + registros_por_pagina - 1) // registros_por_pagina
                    if hasattr(self.view, 'actualizar_controles_paginacion'):
                        self.view.actualizar_controles_paginacion(
                            pagina, total_paginas, total_registros, len(datos)
                        )

        except Exception as e:
            logger.error(f"Error cargando página: {e}")
            if hasattr(self, 'mostrar_error'):
                self.mostrar_error(f"Error cargando página: {str(e)}")

    def cambiar_registros_por_pagina(self, registros):
        """Cambia la cantidad de registros por página y recarga."""
        self.registros_por_pagina = registros
        self.cargar_pagina(1, registros)

    def obtener_total_registros(self):
        """Obtiene el total de registros disponibles."""
        try:
            if self.model:
                return self.model.obtener_total_registros()
            return 0
        except Exception as e:
            logger.error(f"Error obteniendo total de registros: {e}")
            return 0

    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error con logging."""
        logger.error(f"Error en vidrios: {mensaje}")
        
        if self.view:
            show_error(self.view, "Error - Vidrios", mensaje)
        else:
            # Fallback si no hay vista
            logger.error(f"[NO VIEW] Error: {mensaje}")
    def exportar_vidrios(self, formato="excel"):
        """Exporta vidrios al formato especificado."""
        try:
            logger.info(f"Iniciando exportación de vidrios en formato {formato}")
            
            if not self.model:
                self.mostrar_error("Modelo no disponible para exportación")
                return False

            # Obtener todos los datos para exportar
            datos, total = self.model.obtener_datos_paginados(0, 10000)  # Obtener todos los registros
            
            if not datos:
                show_warning(self.view, "Exportar", "No hay vidrios para exportar")
                return False

            # Usar ExportManager para exportar
            try:
                from rexus.utils.export_manager import ExportManager
                from datetime import datetime
                
                export_manager = ExportManager()
                
                # Preparar datos para exportación
                datos_export = {
                    'datos': datos,
                    'columnas': ['Código', 'Descripción', 'Tipo', 'Espesor', 'Precio', 'Stock'],
                    'titulo': 'Listado de Vidrios',
                    'modulo': 'Vidrios',
                    'usuario': self.usuario_actual,
                    'fecha': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Generar nombre de archivo
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"vidrios_export_{timestamp}.{formato}"
                
                # Exportar según formato
                resultado = False
                if formato.lower() == 'excel':
                    resultado = export_manager.exportar_excel(datos_export, filename)
                elif formato.lower() == 'csv':
                    resultado = export_manager.exportar_csv(datos_export, filename)
                elif formato.lower() == 'pdf':
                    resultado = export_manager.exportar_pdf(datos_export, filename)
                else:
                    self.mostrar_error(f"Formato {formato} no soportado")
                    return False
                
                if resultado:
                    show_success(self.view, "Exportar", f"Vidrios exportados exitosamente a {filename}")
                    logger.info(f"Vidrios exportados exitosamente a {filename}")
                    return True
                else:
                    self.mostrar_error("Error durante la exportación")
                    return False
                    
            except ImportError:
                self.mostrar_error("ExportManager no disponible")
                return False
            except Exception as e:
                self.mostrar_error(f"Error en exportación: {str(e)}")
                return False

        except Exception as e:
            logger.error(f"Error exportando vidrios: {e}")
            self.mostrar_error(f"Error exportando vidrios: {str(e)}")
            return False
    
    def cargar_vidrios(self):
        """Método de carga principal del módulo de vidrios."""
        logger.info("Iniciando carga del módulo de vidrios")
        try:
            # Conectar con base de datos y cargar datos
            return self.obtener_vidrios()
        except Exception as e:
            logger.error(f"Error al cargar módulo de vidrios: {e}")
            return []
    
    def obtener_vidrios(self):
        """Obtiene todos los vidrios de la base de datos."""
        logger.info("Obteniendo vidrios de la base de datos")
        try:
            if not self.model:
                logger.error("Modelo de vidrios no disponible")
                return []
            
            # Obtener vidrios del modelo
            vidrios = self.model.obtener_todos_vidrios() if hasattr(self.model, 'obtener_todos_vidrios') else []
            logger.info(f"Obtenidos {len(vidrios)} vidrios")
            return vidrios
        except Exception as e:
            logger.error(f"Error obteniendo vidrios: {e}")
            return []
