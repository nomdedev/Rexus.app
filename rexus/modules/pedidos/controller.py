"""
Controlador de Pedidos - Rexus.app v2.0.0

Maneja la lógica de negocio entre la vista y el modelo de pedidos.
"""

import datetime
                def eliminar_pedido(self, pedido_id:str):
        """Elimina un pedido."""
        try:
            # Confirmar eliminación
            if self.view:
                respuesta = QMessageBox.question(
                    self.view,
                    "Confirmar eliminación",
                    f"¿Está seguro de eliminar el pedido {pedido_id}?\\n\\n"
                    "Esta acción no se puede deshacer.",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )

                if respuesta == QMessageBox.StandardButton.Yes:
                    # Implementar eliminación de pedidos
                    logger.info(f"Eliminando pedido ID: {pedido_id}")
                    
                    if self.model.eliminar_pedido(pedido_id):
                        success_msg = f"Pedido {pedido_id} eliminado exitosamente"
                        logger.info(f"Pedido {pedido_id} eliminado correctamente")
                        
                        self.mostrar_mensaje_success.emit(success_msg)
                        self.pedido_eliminado.emit(int(pedido_id))
                        self.cargar_pedidos()  # Recargar vista
                    else:
                        error_msg = f"No se pudo eliminar el pedido {pedido_id}"
                        logger.error(f"Fallo al eliminar pedido {pedido_id}")
                        self.mostrar_error(error_msg)

        except Exception as e:

    def cambiar_estado(self, pedido_id:str, nuevo_estado: str):
        """Cambia el estado de un pedido."""
        try:
            exito = self.model.actualizar_estado_pedido(
                int(pedido_id),
                nuevo_estado,
                self.usuario_actual.get("id", 1),
                f"Estado cambiado a {nuevo_estado}",
            )

            if exito:
                self.mostrar_exito(f"Estado cambiado a {nuevo_estado}")
                self.cargar_pedidos()
                self.estado_cambiado.emit(int(pedido_id), nuevo_estado)
            else:
                self.mostrar_error("No se pudo cambiar el estado del pedido")

        except Exception as e:
            logger.info(f"[ERROR PEDIDOS CONTROLLER] Error cambiando estado: {e}")
            self.mostrar_error(f"Error cambiando estado: {str(e)}")

    def actualizar_estadisticas(self):
        """Actualiza las estadísticas del módulo."""
        try:
            stats = self.model.obtener_estadisticas()

            # Actualizar estadísticas en la vista
            if self.view and \
                hasattr(self.view, "actualizar_estadisticas_completas"):
                self.view.actualizar_estadisticas_completas(stats)

        except Exception as e:
            logger.info(f"[ERROR PEDIDOS CONTROLLER] Error actualizando estadísticas: {e}")

    def validar_datos_pedido(
        self, datos: Dict[str, Any], es_actualizacion: bool = False
    ) -> bool:
        """Valida los datos del pedido."""
        errores = []

        # Validaciones básicas
        if not datos.get("tipo_pedido"):
            errores.append("Tipo de pedido es obligatorio")

        if not datos.get("prioridad"):
            errores.append("Prioridad es obligatoria")

        if not datos.get("responsable_entrega"):
            errores.append("Responsable de entrega es obligatorio")

        # Validar detalles del pedido
        detalles = datos.get("detalles", [])
        if not detalles:
            errores.append("El pedido debe tener al menos un producto")

        for i, detalle in enumerate(detalles):
            if not detalle.get("descripcion"):
                errores.append(f"Descripción requerida en producto {i + 1}")

            if not detalle.get("cantidad") or detalle["cantidad"] <= 0:
                errores.append(f"Cantidad debe ser mayor a 0 en producto {i + 1}")

            if not detalle.get("precio_unitario") or detalle["precio_unitario"] <= 0:
                errores.append(
                    f"Precio unitario debe ser mayor a 0 en producto {i + 1}"
                )

        # Validar fechas
        fecha_entrega = datos.get("fecha_entrega_solicitada")
        if fecha_entrega:
            if isinstance(fecha_entrega, str):
                try:
                    fecha_entrega = datetime.datetime.strptime(
                        fecha_entrega, "%Y-%m-%d"
                    ).date()
                except (ValueError, TypeError) as e:
                    errores.append(f"Formato de fecha de entrega inválido: {e}")

            if fecha_entrega and fecha_entrega < datetime.date.today():
                errores.append("La fecha de entrega no puede ser anterior a hoy")

        if errores:
            mensaje_error = "Errores de validación:\\n\\n" + "\\n".join(
                f"• {error}" for error in errores
            )
            self.mostrar_error(mensaje_error)
            return False

        return True

    def obtener_pedido_por_id(self, pedido_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene un pedido por su ID."""
        try:
            return self.model.obtener_pedido_por_id(pedido_id)
        except Exception as e:
            logger.info(f"[ERROR PEDIDOS CONTROLLER] Error obteniendo pedido: {e}")
            return None

    def buscar_productos_inventario(self, busqueda: str) -> List[Dict[str, Any]]:
        """Busca productos en el inventario."""
        try:
            return self.model.buscar_productos_inventario(busqueda)
        except Exception as e:
            logger.info(f"[ERROR PEDIDOS CONTROLLER] Error buscando productos: {e}")
            return []

    def obtener_estados_validos(self) -> List[str]:
        """Obtiene la lista de estados válidos."""
        return list(self.model.ESTADOS.keys())

    def obtener_tipos_pedido(self) -> List[str]:
        """Obtiene la lista de tipos de pedido."""
        return list(self.model.TIPOS_PEDIDO.keys())

    def obtener_prioridades(self) -> List[str]:
        """Obtiene la lista de prioridades."""
        return list(self.model.PRIORIDADES.keys())

    def set_usuario_actual(self, usuario: Dict[str, Any]):
        """Establece el usuario actual."""
        self.usuario_actual = usuario
        logger.info(f"[PEDIDOS CONTROLLER] Usuario actual: {usuario.get('nombre', 'Desconocido')}")

    def mostrar_exito(self, mensaje: str):
        """Muestra un mensaje de éxito."""
        logger.info(f"Éxito en pedidos: {mensaje}")
        self.mostrar_mensaje_success.emit(mensaje)


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
                    if hasattr(self.view, 'cargar_en_tabla'):
                        self.view.cargar_en_tabla(datos)

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

    def mostrar_error(self, mensaje: str):
        """Muestra un mensaje de error con logging."""        except Exception as e: