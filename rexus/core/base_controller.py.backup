"""
Base Controller - Clase base para todos los controladores de Rexus.app
Proporciona funcionalidad común, defensas y patrones estandarizados.

Fecha: 15/08/2025
Objetivo: Resolver problemas críticos de estabilidad y consistencia
"""

                        if field not in data or data[field] is None or data[field] == "":
                missing_fields.append(field)
        
        if missing_fields:
            error_msg = f"Campos requeridos faltantes: {', '.join(missing_fields)}"
            self.logger.warning(error_msg)
            self.show_error_message(error_msg)
            return False
        
        return True
    
    def cleanup(self):
        """
        Limpia recursos cuando se cierra el controlador.
        Debe ser sobrescrito por las subclases si necesitan limpieza específica.
        """
        self.logger.info(f"Limpiando recursos del controlador {self.module_name}")
        
        # Limpiar referencias
        if self.view and hasattr(self.view, 'controller'):
            self.view.controller = None
            
        self.model = None
        self.view = None
        self.db_connection = None