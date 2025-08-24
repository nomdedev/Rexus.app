#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix específico y preciso para errores de formato en logística controller
"""

def fix_precise_format_errors():
    """Corrige errores específicos de formato con precisión."""
    
    with open('rexus/modules/logistica/controller.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 1. Corregir imports mal indentados
    content = content.replace(
        'from rexus.utils.unified_sanitizer import (\n    unified_sanitizer, sanitize_string\n)',
        'from rexus.utils.unified_sanitizer import (\n        unified_sanitizer, sanitize_string\n    )'
    )
    
    content = content.replace(
        'from rexus.utils.message_system import (\n    show_info, show_error, show_warning, show_success\n)',
        'from rexus.utils.message_system import (\n        show_info, show_error, show_warning, show_success\n    )'
    )
    
    # 2. Corregir definiciones de método multilinea
    content = content.replace(
        'def crear_servicio_transporte(self,\n                                datos_servicio: Dict[str, Any]) -> bool:',
        'def crear_servicio_transporte(self, datos_servicio: Dict[str, Any]) -> bool:'
    )
    
    content = content.replace(
        'def actualizar_servicio_transporte(self, servicio_id: int,\n                                      datos_servicio: Dict[str, Any]) -> bool:',
        'def actualizar_servicio_transporte(self, servicio_id: int,\n                                     datos_servicio: Dict[str, Any]) -> bool:'
    )
    
    # 3. Corregir continuaciones de línea mal indentadas
    content = content.replace(
        'if (self.model and \n        hasattr(self.model, \'generar_codigo_servicio\'))',
        'if (self.model and \n            hasattr(self.model, \'generar_codigo_servicio\'))'
    )
    
    content = content.replace(
        'if (self.model and \n        hasattr(self.model, \'actualizar_servicio_transporte\'))',
        'if (self.model and \n            hasattr(self.model, \'actualizar_servicio_transporte\'))'
    )
    
    # 4. Corregir asignaciones multilinea
    content = content.replace(
        'datos_servicio[\'codigo\'] = (\n            self.model.generar_codigo_servicio())',
        'datos_servicio[\'codigo\'] = \\\n            self.model.generar_codigo_servicio()'
    )
    
    content = content.replace(
        'datos_servicio[\'costo_estimado\'] = (\n            costo_info.get(\'costo_estimado\', 0.0))',
        'datos_servicio[\'costo_estimado\'] = \\\n            costo_info.get(\'costo_estimado\', 0.0)'
    )
    
    # 5. Simplificar líneas demasiado complejas
    content = content.replace(
        'servicio_id = self.model.crear_servicio_transporte(datos_servicio)',
        'servicio_id = \\\n            self.model.crear_servicio_transporte(datos_servicio)'
    )
    
    content = content.replace(
        'success = self.model.actualizar_servicio_transporte(servicio_id, datos_servicio)',
        'success = \\\n            self.model.actualizar_servicio_transporte(servicio_id, datos_servicio)'
    )
    
    # 6. Corregir show_error y show_success multilinea
    content = content.replace(
        'show_error(self.view, "Error",\n                   "No hay conexión al modelo de datos")',
        'show_error(self.view, "Error",\n                    "No hay conexión al modelo de datos")'
    )
    
    content = content.replace(
        'show_success(self.view, "Éxito",\n                     "Servicio de transporte creado correctamente")',
        'show_success(self.view, "Éxito",\n                      "Servicio de transporte creado correctamente")'
    )
    
    content = content.replace(
        'show_success(self.view, "Éxito",\n                     "Proveedor de transporte creado correctamente")',
        'show_success(self.view, "Éxito",\n                      "Proveedor de transporte creado correctamente")'
    )
    
    # 7. Corregir logger multilinea
    content = content.replace(
        'logger.warning(\n                "Método crear_servicio_transporte no disponible")',
        'logger.warning(\n            "Método crear_servicio_transporte no disponible")'
    )
    
    content = content.replace(
        'logger.warning(\n            "Método actualizar_servicio_transporte no disponible")',
        'logger.warning(\n            "Método actualizar_servicio_transporte no disponible")'
    )
    
    # 8. Corregir estadísticas multilinea - simplificar con backslash
    content = content.replace(
        'en_transito = len([s for s in servicios \n                        if s.get(\'estado\') == \'EN_TRANSITO\'])',
        'en_transito = len([s for s in servicios \\\n                       if s.get(\'estado\') == \'EN_TRANSITO\'])'
    )
    
    content = content.replace(
        'completados = len([s for s in servicios \n                        if s.get(\'estado\') == \'COMPLETADO\'])',
        'completados = len([s for s in servicios \\\n                       if s.get(\'estado\') == \'COMPLETADO\'])'
    )
    
    content = content.replace(
        'cancelados = len([s for s in servicios \n                       if s.get(\'estado\') == \'CANCELADO\'])',
        'cancelados = len([s for s in servicios \\\n                      if s.get(\'estado\') == \'CANCELADO\'])'
    )
    
    content = content.replace(
        'pendientes = len([s for s in servicios \n                       if s.get(\'estado\') == \'PENDIENTE\'])',
        'pendientes = len([s for s in servicios \\\n                      if s.get(\'estado\') == \'PENDIENTE\'])'
    )
    
    # 9. Corregir costo_total multilinea
    content = content.replace(
        'costo_total = sum([s.get(\'costo_real\', 0) for s in servicios \n                        if s.get(\'estado\') == \'COMPLETADO\'])',
        'costo_total = sum([s.get(\'costo_real\', 0) for s in servicios \\\n                       if s.get(\'estado\') == \'COMPLETADO\'])'
    )
    
    # 10. Corregir promedio_entrega
    content = content.replace(
        '\'promedio_entrega\': round(\n                costo_total / completados if completados > 0 else 0, 2)',
        '\'promedio_entrega\': round(costo_total / completados \\\n                                 if completados > 0 else 0, 2)'
    )
    
    # 11. Simplificar definiciones de método largas
    content = content.replace(
        'def _sanitizar_criterios_busqueda(self,\n                                    criterios: Dict[str, Any]) -> Dict[str, Any]:',
        'def _sanitizar_criterios_busqueda(self, criterios: Dict[str, Any]) \\\n        -> Dict[str, Any]:'
    )
    
    content = content.replace(
        'def _sanitizar_datos_servicio(self,\n                                datos: Dict[str, Any]) -> Dict[str, Any]:',
        'def _sanitizar_datos_servicio(self, datos: Dict[str, Any]) \\\n        -> Dict[str, Any]:'
    )
    
    content = content.replace(
        'def _calcular_costo_servicio(self,\n                               datos_servicio: Dict[str, Any]) -> Dict[str, Any]:',
        'def _calcular_costo_servicio(self, datos_servicio: Dict[str, Any]) \\\n        -> Dict[str, Any]:'
    )
    
    # 12. Corregir arrays largos
    content = content.replace(
        'campos_texto = [\'origen\', \'destino\', \'descripcion\',\n                     \'observaciones\', \'codigo\']',
        'campos_texto = [\'origen\', \'destino\', \'descripcion\',\n                    \'observaciones\', \'codigo\']'
    )
    
    # 13. Corregir hasattr multilinea
    content = content.replace(
        'if (self.model and \n        hasattr(self.model, \'obtener_servicios_transporte\'))',
        'if (self.model and \\\n        hasattr(self.model, \'obtener_servicios_transporte\'))'
    )
    
    content = content.replace(
        'if (self.model and \n        hasattr(self.model, \'obtener_proveedores_transporte\'))',
        'if (self.model and \\\n        hasattr(self.model, \'obtener_proveedores_transporte\'))'
    )
    
    # 14. Corregir _registrar_auditoria
    content = content.replace(
        'def _registrar_auditoria(self, accion: str, id_objeto: Optional[int],\n                           detalles: Optional[Dict[str, Any]] = None):',
        'def _registrar_auditoria(self, accion: str, id_objeto: Optional[int],\n                          detalles: Optional[Dict[str, Any]] = None):'
    )
    
    # 15. Corregir logging extremadamente largo
    content = content.replace(
        'logger.info(f"Auditoría - Módulo: logistica, "\n                    f"Acción: {accion}, ID: {id_objeto}, "\n                    f"Detalles: {detalles}")',
        'logger.info(f"Auditoría - Módulo: logistica, Acción: {accion}, "\n                    f"ID: {id_objeto}, Detalles: {detalles}")'
    )
    
    # 16. Corregir operador ternario largo
    content = content.replace(
        'mensaje = ("Transporte eliminado exitosamente" if success \n               else "Error eliminando transporte")',
        'mensaje = ("Transporte eliminado exitosamente" if success\n               else "Error eliminando transporte")'
    )
    
    # 17. Limpiar líneas en blanco con espacios
    lines = content.split('\n')
    clean_lines = [line.rstrip() for line in lines]
    content = '\n'.join(clean_lines)
    
    # 18. Asegurar newline al final
    if not content.endswith('\n'):
        content += '\n'
    
    # Escribir archivo si hay cambios
    if content != original_content:
        with open('rexus/modules/logistica/controller.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Correcciones precisas de formato aplicadas")
        return True
    else:
        print("No hay cambios que aplicar")
        return False

if __name__ == "__main__":
    fix_precise_format_errors()