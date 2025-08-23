"""Controlador de Obras"""

import datetime
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
            logger.info(f"[ERROR OBRAS CONTROLLER] Error eliminando obra: {e}")
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
            logger.info(f"[ERROR OBRAS CONTROLLER] Error cambiando estado: {e}")
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
            logger.info(f"[OBRAS CONTROLLER] Filtradas {len(obras)} obras")

        except Exception as e:
            logger.info(f"[ERROR OBRAS CONTROLLER] Error aplicando filtros: {e}")
            self.mostrar_mensaje_error(f"Error aplicando filtros: {str(e)}")

    def filtrar_obras(self):
        """Filtra las obras según los criterios seleccionados."""
        try:
            if hasattr(self.view, 'obtener_filtros_aplicados'):
                filtros = self.view.obtener_filtros_aplicados()
                self.aplicar_filtros(filtros)
            else:
                logger.info("[OBRAS CONTROLLER] Vista no tiene método obtener_filtros_aplicados")

        except Exception as e:
            logger.info(f"[ERROR OBRAS CONTROLLER] Error filtrando obras: {e}")
            self.mostrar_mensaje_error(f"Error filtrando obras: {str(e)}")
    def actualizar_estadisticas(self):
        """Actualiza las estadísticas mostradas en la vista."""
        try:
            estadisticas = self.model.obtener_estadisticas_obras()
            if hasattr(self.view, "actualizar_estadisticas"):
                self.view.actualizar_estadisticas(estadisticas)
        except Exception as e:
            logger.info(f"[ERROR OBRAS CONTROLLER] Error actualizando estadísticas: {e}")
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
            logger.info(f"[ERROR OBRAS CONTROLLER] Error obteniendo obra: {e}")
            return None

    def set_usuario_actual(self, usuario: str):
        """Establece el usuario actual del sistema."""
        self.usuario_actual = usuario
        logger.info(f"[OBRAS CONTROLLER] Usuario actual: {usuario}")

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
            logger.info(f"[ERROR] Error cargando página: {e}")
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
            logger.info(f"[ERROR] Error obteniendo total de registros: {e}")
            return 0
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
                    'fecha': datetime.now().strftime()
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
            return False
