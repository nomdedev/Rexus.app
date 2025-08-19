"""Controlador de Obras"""

import datetime
from typing import Any, Dict, Optional

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox

from rexus.core.auth_decorators import auth_required, admin_required
# Importar sistema moderno de mensajes
from rexus.utils.message_system import show_success, show_error, show_warning, ask_question

# Importar logging centralizado
try:
    from rexus.utils.app_logger import get_logger
    logger = get_logger("obras.controller")
except ImportError:
    class DummyLogger:
        def info(self, msg): print(f"[INFO] {msg}")
        def warning(self, msg): print(f"[WARNING] {msg}")
        def error(self, msg): print(f"[ERROR] {msg}")
        def debug(self, msg): print(f"[DEBUG] {msg}")
    logger = DummyLogger()

class ObrasController(QObject):
    # Señales para comunicación con otros módulos
    obra_creada = pyqtSignal(dict)  # Emitida cuando se crea una nueva obra
    obra_actualizada = pyqtSignal(dict)  # Emitida cuando se actualiza una obra
    obra_eliminada = pyqtSignal(int)  # Emitida cuando se elimina una obra

    def __init__(
        self,
        model=None,
        view=None,
        db_connection=None,
        usuarios_model=None,
        logistica_controller=None,
    ):
        super().__init__()
        self.model = model
        self.view = view
        self.db_connection = db_connection
        self.usuarios_model = usuarios_model
        self.logistica_controller = logistica_controller
        self.usuario_actual = "SISTEMA"

        # Inicializar current_user para compatibilidad con @auth_required
        self.current_user = self._get_current_auth_user()

        # Validar y conectar componentes de forma segura
        self._validate_components()
        
        # Asegurar que la vista tiene referencia al controller
        if self.view:
            self.view.controller = self
            self.conectar_señales()
        else:
            logger.warning("Vista no disponible durante inicialización del controlador de obras")

    def _validate_components(self):
        """
        Valida que los componentes críticos estén disponibles.
        """
        logger.debug("Validando componentes del controlador de obras")
        
        if not self.model:
            logger.error("CRITICO: Modelo de obras no disponible")
            
        if not self.view:
            logger.warning("Vista de obras no disponible")
            
        if not self.db_connection:
            logger.warning("Conexión de base de datos no disponible")
            
        logger.info("Validación de componentes completada")
    
    def _ensure_model_available(self, operation_name="operación"):
        """
        Asegura que el modelo esté disponible para una operación.
        
        Args:
            operation_name: Nombre de la operación para logging
            
        Returns:
            bool: True si el modelo está disponible
        """
        if not self.model:
            error_msg = f"Modelo no disponible para {operation_name}"
            logger.error(error_msg)
            if self.view:
                show_error(self.view, "Error del Sistema", error_msg)
            return False
        return True
    
    def _ensure_view_available(self, operation_name="operación"):
        """
        Asegura que la vista esté disponible para una operación.
        
        Args:
            operation_name: Nombre de la operación para logging
            
        Returns:
            bool: True si la vista está disponible
        """
        if not self.view:
            error_msg = f"Vista no disponible para {operation_name}"
            logger.error(error_msg)
            return False
        return True

    def _get_current_auth_user(self):
        """Obtiene el usuario autenticado actual desde AuthManager."""
        try:
            from rexus.core.auth_manager import AuthManager

            # Si hay un usuario actual en AuthManager, usarlo
            if AuthManager.current_user and AuthManager.current_user_role:
                return {
                    'id': 1,  # ID por defecto
                    'username': AuthManager.current_user,
                    'role': AuthManager.current_user_role.value,
                    'name': AuthManager.current_user
                }
            else:
                # Usuario por defecto para desarrollo/fallback
                return {
                    'id': 1,
                    'username': 'SISTEMA',
                    'role': 'admin',
                    'name': 'Usuario Sistema'
                }
        except ImportError:
            # Fallback si AuthManager no está disponible
            return {
                'id': 1,
                'username': 'SISTEMA',
                'role': 'admin',
                'name': 'Usuario Sistema'
            }

    def conectar_señales(self):
        """Conecta las señales de la vista con los métodos del controlador."""
        if hasattr(self.view, "btn_nueva_obra"):
            self.view.btn_nueva_obra.clicked.connect(self.mostrar_formulario_nueva_obra)
        if hasattr(self.view, "btn_editar_obra"):
            self.view.btn_editar_obra.clicked.connect(self.editar_obra_seleccionada)
        if hasattr(self.view, "btn_eliminar_obra"):
            self.view.btn_eliminar_obra.clicked.connect(self.eliminar_obra_seleccionada)
        if hasattr(self.view, "btn_cambiar_estado"):
            self.view.btn_cambiar_estado.clicked.connect(self.cambiar_estado_obra)
        if hasattr(self.view, "btn_actualizar"):
            self.view.btn_actualizar.clicked.connect(self.cargar_obras)
        if hasattr(self.view, "combo_filtro_estado"):
            self.view.combo_filtro_estado.currentTextChanged.connect(self.filtrar_obras)
        
        # Conectar señal de exportación
        if hasattr(self.view, 'solicitud_exportar'):
            self.view.solicitud_exportar.connect(self.exportar_obras)

    def cargar_obras(self):
        """Carga todas las obras en la tabla."""
        try:
            logger.debug("Iniciando carga de obras")
            
            # CRITICO: Verificar componentes
            if not self._ensure_model_available("cargar obras"):
                return
                
            if not self._ensure_view_available("cargar obras"):
                logger.warning("Vista no disponible, cargando datos solo en modelo")
            
            obras = self.model.obtener_todas_obras()
            
            # Solo actualizar vista si está disponible
            if self.view and hasattr(self.view, 'cargar_obras_en_tabla'):
                self.view.cargar_obras_en_tabla(obras)
            else:
                logger.warning("Vista no tiene método cargar_obras_en_tabla")
            
            self.actualizar_estadisticas()
            logger.info(f"Cargadas {len(obras)} obras exitosamente")
            
        except Exception as e:
            logger.error(f"Error cargando obras: {e}", exc_info=True)
            if self.view:
                show_error(self.view, "Error", f"Error cargando obras: {str(e)}")

    def mostrar_formulario_nueva_obra(self):
        """Muestra el formulario para crear una nueva obra."""
        try:
            if hasattr(self.view, "mostrar_dialogo_nueva_obra"):
                self.view.mostrar_dialogo_nueva_obra()
            else:
                print(
                    "[OBRAS CONTROLLER] Vista no tiene método mostrar_dialogo_nueva_obra"
                )
        except Exception as e:
            print(f"[ERROR OBRAS CONTROLLER] Error mostrando formulario: {e}")

    @auth_required
    def agregar_obra(self, datos_obra: Dict[str, Any]) -> bool:
        """Alias para crear_obra - usado por la vista del diálogo."""
        return self.crear_obra(datos_obra)

    @auth_required
    def crear_obra(self, datos_obra: Dict[str, Any]) -> bool:
        """
        Crea una nueva obra con los datos proporcionados.

        Args:
            datos_obra: Diccionario con los datos de la obra

        Returns:
            bool: True si se creó exitosamente
        """
        try:
            logger.info(f"Iniciando creación de obra para usuario: {self.usuario_actual}")
            
            # CRITICO: Verificar que el modelo esté disponible
            if not self._ensure_model_available("crear obra"):
                return False
            
            # Validar datos requeridos
            if not self.validar_datos_obra(datos_obra):
                logger.warning("Validación de datos fallida para nueva obra")
                return False

            # Asignar usuario actual
            datos_obra["usuario_creacion"] = self.usuario_actual

            exito, mensaje = self.model.crear_obra(datos_obra)

            if exito:
                self.mostrar_mensaje_exito(mensaje)
                self.cargar_obras()  # Recargar la tabla

                # Emitir señal para otros módulos
                obra = self.model.obtener_obra_por_codigo(datos_obra["codigo"])
                if obra:
                    self.obra_creada.emit(obra)

                return True
            else:
                self.mostrar_mensaje_error(mensaje)
                return False

        except Exception as e:
            print(f"[ERROR OBRAS CONTROLLER] Error creando obra: {e}")
            self.mostrar_mensaje_error(f"Error creando obra: {str(e)}")
            return False

    @auth_required
    def editar_obra_seleccionada(self):
        """Edita la obra seleccionada en la tabla."""
        try:
            obra_seleccionada = self.view.obtener_obra_seleccionada()
            if not obra_seleccionada:
                self.mostrar_mensaje_advertencia(
                    "Debe seleccionar una obra para editar"
                )
                return

            if hasattr(self.view, "mostrar_formulario_edicion_obra"):
                self.view.mostrar_formulario_edicion_obra(obra_seleccionada)
            else:
                print(
                    "[OBRAS CONTROLLER] Vista no tiene método mostrar_formulario_edicion_obra"
                )

        except Exception as e:
            print(f"[ERROR OBRAS CONTROLLER] Error editando obra: {e}")
            self.mostrar_mensaje_error(f"Error editando obra: {str(e)}")

    @auth_required
    def actualizar_obra(self,
obra_id: int,
        datos_actualizados: Dict[str,
        Any]) -> bool:
        """Actualiza una obra existente con nuevos datos."""
        try:
            if not self.validar_datos_obra(datos_actualizados, es_actualizacion=True):
                return False

            datos_actualizados["usuario_modificacion"] = self.usuario_actual

            exito, mensaje = self.model.actualizar_obra(obra_id, datos_actualizados)

            if exito:
                self.mostrar_mensaje_exito(mensaje)
                self.cargar_obras()  # Recargar la tabla

                # Emitir señal para otros módulos
                obra = self.model.obtener_obra_por_id(obra_id)
                if obra:
                    self.obra_actualizada.emit(obra)

                return True
            else:
                self.mostrar_mensaje_error(mensaje)
                return False

        except Exception as e:
            print(f"[ERROR OBRAS CONTROLLER] Error actualizando obra: {e}")
            self.mostrar_mensaje_error(f"Error actualizando obra: {str(e)}")
            return False

    @admin_required
    def eliminar_obra_seleccionada(self):
        """Elimina la obra seleccionada."""
        try:
            obra_seleccionada = self.view.obtener_obra_seleccionada()
            if not obra_seleccionada:
                self.mostrar_mensaje_advertencia(
                    "Debe seleccionar una obra para eliminar"
                )
                return

            # Confirmar eliminación con sistema moderno
            respuesta = ask_question(
                self.view,
                f"¿Está seguro de eliminar la obra '{obra_seleccionada['codigo']}'?\n\n"
                "Esta acción no se puede deshacer.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if respuesta == QMessageBox.StandardButton.Yes:
                exito, mensaje = self.model.eliminar_obra(
                    obra_seleccionada["id"], self.usuario_actual
                )

                if exito:
                    self.mostrar_mensaje_exito(mensaje)
                    self.cargar_obras()  # Recargar la tabla
                    self.obra_eliminada.emit(obra_seleccionada["id"])
                else:
                    self.mostrar_mensaje_error(mensaje)

        except Exception as e:
            print(f"[ERROR OBRAS CONTROLLER] Error eliminando obra: {e}")
            self.mostrar_mensaje_error(f"Error eliminando obra: {str(e)}")

    def cambiar_estado_obra(self):
        """Cambia el estado de la obra seleccionada."""
        try:
            obra_seleccionada = self.view.obtener_obra_seleccionada()
            if not obra_seleccionada:
                self.mostrar_mensaje_advertencia(
                    "Debe seleccionar una obra para cambiar el estado"
                )
                return

            if hasattr(self.view, "mostrar_dialogo_cambiar_estado"):
                nuevo_estado = self.view.mostrar_dialogo_cambiar_estado(
                    obra_seleccionada["estado"]
                )

                if nuevo_estado:
                    exito, mensaje = self.model.cambiar_estado_obra(
                        obra_seleccionada["id"], nuevo_estado, self.usuario_actual
                    )

                    if exito:
                        self.mostrar_mensaje_exito(mensaje)
                        self.cargar_obras()  # Recargar la tabla
                    else:
                        self.mostrar_mensaje_error(mensaje)

        except Exception as e:
            print(f"[ERROR OBRAS CONTROLLER] Error cambiando estado: {e}")
            self.mostrar_mensaje_error(f"Error cambiando estado: {str(e)}")

    def aplicar_filtros(self, filtros):
        """Aplica filtros a las obras."""
        try:
            if not self.model:
                self.mostrar_mensaje_error("Modelo no inicializado")
                return

            obras = self.model.obtener_obras_filtradas(filtros)
            self.view.cargar_obras_en_tabla(obras)
            self.actualizar_estadisticas()
            print(f"[OBRAS CONTROLLER] Filtradas {len(obras)} obras")

        except Exception as e:
            print(f"[ERROR OBRAS CONTROLLER] Error aplicando filtros: {e}")
            self.mostrar_mensaje_error(f"Error aplicando filtros: {str(e)}")

    def filtrar_obras(self):
        """Filtra las obras según los criterios seleccionados."""
        try:
            if hasattr(self.view, 'obtener_filtros_aplicados'):
                filtros = self.view.obtener_filtros_aplicados()
                self.aplicar_filtros(filtros)
            else:
                print("[OBRAS CONTROLLER] Vista no tiene método obtener_filtros_aplicados")

        except Exception as e:
            print(f"[ERROR OBRAS CONTROLLER] Error filtrando obras: {e}")
            self.mostrar_mensaje_error(f"Error filtrando obras: {str(e)}")

    @auth_required
    def actualizar_estadisticas(self):
        """Actualiza las estadísticas mostradas en la vista."""
        try:
            estadisticas = self.model.obtener_estadisticas_obras()
            if hasattr(self.view, "actualizar_estadisticas"):
                self.view.actualizar_estadisticas(estadisticas)
        except Exception as e:
            print(f"[ERROR OBRAS CONTROLLER] Error actualizando estadísticas: {e}")

    @auth_required
    def validar_datos_obra(
        self, datos_obra: Dict[str, Any], es_actualizacion: bool = False
    ) -> bool:
        """
        Valida los datos de una obra antes de crear o actualizar.

        Args:
            datos_obra: Diccionario con los datos a validar
            es_actualizacion: True si es una actualización, False si es creación

        Returns:
            bool: True si los datos son válidos
        """
        errores = []

        # Validaciones para creación
        if not es_actualizacion:
            if not datos_obra.get("codigo"):
                errores.append("El código de la obra es obligatorio")
            elif len(datos_obra.get("codigo", "")) < 3:
                errores.append("El código debe tener al menos 3 caracteres")

        # Validaciones comunes
        if not datos_obra.get("nombre"):
            errores.append("El nombre de la obra es obligatorio")

        if not datos_obra.get("cliente"):
            errores.append("El cliente es obligatorio")

        if not datos_obra.get("responsable"):
            errores.append("El responsable es obligatorio")

        # Validar fechas
        fecha_inicio = datos_obra.get("fecha_inicio")
        fecha_fin = datos_obra.get("fecha_fin_estimada")

        if fecha_inicio and fecha_fin:
            if isinstance(fecha_inicio, str):
                fecha_inicio = datetime.datetime.strptime(
                    fecha_inicio, "%Y-%m-%d"
                ).date()
            if isinstance(fecha_fin, str):
                fecha_fin = datetime.datetime.strptime(fecha_fin, "%Y-%m-%d").date()

            if fecha_fin < fecha_inicio:
                errores.append(
                    "La fecha de finalización no puede ser anterior a la fecha de inicio"
                )

        # Validar presupuesto
        presupuesto = datos_obra.get("presupuesto_total")
        if presupuesto is not None:
            try:
                presupuesto_float = float(presupuesto)
                if presupuesto_float < 0:
                    errores.append("El presupuesto no puede ser negativo")
            except (ValueError, TypeError):
                errores.append("El presupuesto debe ser un número válido")

        if errores:
            mensaje_error = "Errores de validación:\n\n" + "\n".join(
                f"• {error}" for error in errores
            )
            self.mostrar_mensaje_error(mensaje_error)
            return False

        return True

    def obtener_obra_por_codigo(self, codigo: str) -> Optional[Dict[str, Any]]:
        """Obtiene una obra por su código."""
        try:
            return self.model.obtener_obra_por_codigo(codigo)
        except Exception as e:
            print(f"[ERROR OBRAS CONTROLLER] Error obteniendo obra: {e}")
            return None

    def set_usuario_actual(self, usuario: str):
        """Establece el usuario actual del sistema."""
        self.usuario_actual = usuario
        print(f"[OBRAS CONTROLLER] Usuario actual: {usuario}")

    def mostrar_mensaje_exito(self, mensaje: str):
        """Muestra un mensaje de éxito con sistema moderno."""
        show_success(self.view, mensaje)

    def mostrar_mensaje_error(self, mensaje: str):
        """Muestra un mensaje de error con sistema moderno."""
        show_error(self.view, "Error en Obras", mensaje)

    def mostrar_mensaje_advertencia(self, mensaje: str):
        """Muestra un mensaje de advertencia con sistema moderno."""
        show_warning(self.view, mensaje)

    def cargar_pagina(self, pagina, registros_por_pagina=50):
        """Carga una página específica de datos"""
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
            print(f"[ERROR] Error cargando página: {e}")
            if hasattr(self, 'mostrar_error'):
                self.mostrar_error("Error", f"Error cargando página: {str(e)}")

    def cambiar_registros_por_pagina(self, registros):
        """Cambia la cantidad de registros por página y recarga"""
        self.registros_por_pagina = registros
        self.cargar_pagina(1, registros)

    def obtener_total_registros(self):
        """Obtiene el total de registros disponibles"""
        try:
            if self.model:
                return self.model.obtener_total_registros()
            return 0
        except Exception as e:
            print(f"[ERROR] Error obteniendo total de registros: {e}")
            return 0

    @auth_required
    def exportar_obras(self, formato="excel"):
        """Exporta obras al formato especificado."""
        try:
            logger.info(f"Iniciando exportación de obras en formato {formato}")
            
            if not self._ensure_model_available("exportar obras"):
                return False

            # Obtener todos los datos para exportar
            datos, total = self.model.obtener_datos_paginados(0, 10000)  # Obtener todos los registros
            
            if not datos:
                show_warning(self.view, "Exportar", "No hay obras para exportar")
                return False

            # Usar ExportManager para exportar
            try:
                from rexus.utils.export_manager import ExportManager
                from datetime import datetime
                
                export_manager = ExportManager()
                
                # Preparar datos para exportación
                datos_export = {
                    'datos': datos,
                    'columnas': ['Código', 'Nombre', 'Cliente', 'Estado', 'Fecha Inicio', 'Fecha Fin', 'Presupuesto', 'Responsable'],
                    'titulo': 'Listado de Obras',
                    'modulo': 'Obras',
                    'usuario': self.usuario_actual,
                    'fecha': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Generar nombre de archivo
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"obras_export_{timestamp}.{formato}"
                
                # Exportar según formato
                resultado = False
                if formato.lower() == 'excel':
                    resultado = export_manager.exportar_excel(datos_export, filename)
                elif formato.lower() == 'csv':
                    resultado = export_manager.exportar_csv(datos_export, filename)
                elif formato.lower() == 'pdf':
                    resultado = export_manager.exportar_pdf(datos_export, filename)
                else:
                    self.mostrar_mensaje_error(f"Formato {formato} no soportado")
                    return False
                
                if resultado:
                    self.mostrar_mensaje_exito(f"Obras exportadas exitosamente a {filename}")
                    logger.info(f"Obras exportadas exitosamente a {filename}")
                    return True
                else:
                    self.mostrar_mensaje_error("Error durante la exportación")
                    return False
                    
            except ImportError:
                self.mostrar_mensaje_error("ExportManager no disponible")
                return False
            except Exception as e:
                self.mostrar_mensaje_error(f"Error en exportación: {str(e)}")
                return False

        except Exception as e:
            logger.error(f"Error exportando obras: {e}")
            self.mostrar_mensaje_error(f"Error exportando obras: {str(e)}")
            return False
