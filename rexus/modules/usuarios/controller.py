"""
Controlador de Usuarios - Rexus.app v2.0.0

Maneja la lógica de negocio entre la vista y el modelo de usuarios.
"""

                def registrar_auditoria(self,
accion: str,
        modulo: str,
        detalles: Dict[str,
        Any]):
        """Registra una acción en el log de auditoría."""
        try:
            # Aquí se podría integrar con el módulo de auditoría
            self.logger.info(f"AUDITORIA: {accion} - {modulo} - {detalles}")
        except Exception as e:
            self.                self.mostrar_error("Error", f"Error cargando página: {str(e)}")

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

    def mostrar_error(self, mensaje: str):
        """Muestra un mensaje de error con el sistema mejorado."""
        if self.view:
            show_error(self.view, "Error", mensaje)

    def mostrar_advertencia(self, mensaje: str):
        """Muestra un mensaje de advertencia con el sistema mejorado."""
        if self.view:
            from rexus.utils.message_system import show_warning
            show_warning(self.view, , mensaje)

    def mostrar_info(self, mensaje: str):
        """Muestra un mensaje informativo con el sistema mejorado."""
        if self.view:
            from rexus.utils.message_system import show_info
            show_info(self.view, , mensaje)

    def get_view(self):
        """Retorna la vista del módulo."""
        return self.view

    def cleanup(self):
        """Limpia recursos al cerrar el módulo."""
        try:
            self.logger.info("Limpiando recursos...")
            # Desconectar señales si es necesario
            # Cerrar conexiones, etc.
        except Exception as e:
            self.
    def buscar_usuarios(self, termino: str) -> Optional[List[Dict]]:
        """
        Busca usuarios por término de búsqueda.
        
        Args:
            termino: Término de búsqueda
            
        Returns:
            Lista de usuarios encontrados o None en caso de error
        """
        try:
            self.logger.info(f"Buscando usuarios con término: '{termino}'")
            
            if not self.model:
                self.logger.error("Modelo no disponible")
                return None
            
            # Usar filtros para realizar la búsqueda
            filtros = {'busqueda': termino}
            usuarios = self.model.obtener_usuarios_filtrados(filtros)
            
            if usuarios is not None:
                self.logger.info(f"Encontrados {len(usuarios)} usuarios")
                return usuarios
            else:
                self.logger.error("Error en búsqueda del modelo")
                return None
                
        except Exception as e:
            self.
    def obtener_todos_usuarios(self) -> Optional[List[Dict]]:
        """Obtiene todos los usuarios del sistema."""
        try:
            if not self.model:
                return None
            return self.model.obtener_todos_usuarios()
        except Exception as e:
            self.
    def desactivar_usuario(self, usuario_id: int) -> bool:
        """Desactiva un usuario del sistema."""
        try:
            if not self.model:
                return False
            return self.model.desactivar_usuario(usuario_id)
        except Exception as e:
