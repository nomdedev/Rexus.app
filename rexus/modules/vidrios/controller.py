"""Controlador de Vidrios"""

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

    def mostrar_error(self, mensaje):
        """Muestra un mensaje de error con logging."""
                    except Exception as e:
                self.mostrar_error(f"Error en exportación: {str(e)}")
                return False

        except Exception as e:
            return False
    
    def cargar_vidrios(self):
        """Método de carga principal del módulo de vidrios."""
        logger.info("Iniciando carga del módulo de vidrios")
        try:
            # Conectar con base de datos y cargar datos
            return self.obtener_vidrios()
        except Exception as e:
    
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
