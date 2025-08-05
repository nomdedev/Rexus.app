"""Controlador de Obras"""

import datetime
from rexus.core.auth_manager import AuthManager, auth_required
from typing import Any, Dict, Optional

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem


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

        if self.view:
            self.conectar_señales()

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

    def cargar_obras(self):
        """Carga todas las obras en la tabla."""
        try:
            obras = self.model.obtener_todas_obras()
            self.view.cargar_obras_en_tabla(obras)
            self.actualizar_estadisticas()
            print(f"[OBRAS CONTROLLER] Cargadas {len(obras)} obras")
        except Exception as e:
            print(f"[ERROR OBRAS CONTROLLER] Error cargando obras: {e}")
            self.mostrar_mensaje_error(f"Error cargando obras: {str(e)}")

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

    @auth_required(permission='CREATE')
    def agregar_obra(self, datos_obra:
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('agregar_obra'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")
 Dict[str, Any]) -> bool:
        """Alias para crear_obra - usado por la vista del diálogo."""
        return self.crear_obra(datos_obra)

    @auth_required(permission='CREATE')
    def crear_obra(self, datos_obra:
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('crear_obra'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")
 Dict[str, Any]) -> bool:
        """
        Crea una nueva obra con los datos proporcionados.

        Args:
            datos_obra: Diccionario con los datos de la obra

        Returns:
            bool: True si se creó exitosamente
        """
        try:
            # Validar datos requeridos
            if not self.validar_datos_obra(datos_obra):
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

    @auth_required(permission='UPDATE')
    def editar_obra_seleccionada(self):
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('editar_obra_seleccionada'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")

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

    @auth_required(permission='UPDATE')
    def actualizar_obra(self, obra_id:
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('actualizar_obra'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")
 int, datos_obra: Dict[str, Any]) -> bool:
        """
        Actualiza una obra existente.

        Args:
            obra_id: ID de la obra a actualizar
            datos_obra: Nuevos datos de la obra

        Returns:
            bool: True si se actualizó exitosamente
        """
        try:
            if not self.validar_datos_obra(datos_obra, es_actualizacion=True):
                return False

            datos_obra["usuario_modificacion"] = self.usuario_actual

            exito, mensaje = self.model.actualizar_obra(obra_id, datos_obra)

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

    @auth_required(permission='DELETE')
    def eliminar_obra_seleccionada(self):
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('eliminar_obra_seleccionada'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")

        """Elimina la obra seleccionada."""
        try:
            obra_seleccionada = self.view.obtener_obra_seleccionada()
            if not obra_seleccionada:
                self.mostrar_mensaje_advertencia(
                    "Debe seleccionar una obra para eliminar"
                )
                return

            # Confirmar eliminación
            respuesta = QMessageBox.question(
                self.view,
                "Confirmar eliminación",
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
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('cambiar_estado_obra'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")

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

    def filtrar_obras(self):
        """Filtra las obras según los criterios seleccionados."""
        try:
            filtros = self.view.obtener_filtros_aplicados()
            obras = self.model.obtener_obras_filtradas(
                estado=filtros.get("estado", ""),
                responsable=filtros.get("responsable", ""),
                fecha_inicio=filtros.get("fecha_inicio"),
                fecha_fin=filtros.get("fecha_fin"),
            )

            self.view.cargar_obras_en_tabla(obras)
            print(f"[OBRAS CONTROLLER] Filtradas {len(obras)} obras")

        except Exception as e:
            print(f"[ERROR OBRAS CONTROLLER] Error filtrando obras: {e}")
            self.mostrar_mensaje_error(f"Error filtrando obras: {str(e)}")

    @auth_required(permission='UPDATE')
    def actualizar_estadisticas(self):
        # 🔒 VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA
        # TODO: Implementar @auth_required o verificación manual
        # if not AuthManager.check_permission('actualizar_estadisticas'):
        #     raise PermissionError("Acceso denegado - Permisos insuficientes")

        """Actualiza las estadísticas mostradas en la vista."""
        try:
            estadisticas = self.model.obtener_estadisticas_obras()
            if hasattr(self.view, "actualizar_estadisticas"):
                self.view.actualizar_estadisticas(estadisticas)
        except Exception as e:
            print(f"[ERROR OBRAS CONTROLLER] Error actualizando estadísticas: {e}")

    @auth_required(permission='MANAGE')
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
        """Muestra un mensaje de éxito."""
        QMessageBox.information(self.view, "Éxito", mensaje)

    def mostrar_mensaje_error(self, mensaje: str):
        """Muestra un mensaje de error."""
        QMessageBox.critical(self.view, "Error", mensaje)

    def mostrar_mensaje_advertencia(self, mensaje: str):
        """Muestra un mensaje de advertencia."""
        QMessageBox.warning(self.view, "Advertencia", mensaje)
