#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script completo para corregir TODOS los errores de formato en logística controller
"""

import re

def fix_all_format_errors():
    """Corrige todos los errores de formato detectados por flake8."""
    
    with open('rexus/modules/logistica/controller.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 1. Corregir líneas demasiado largas (E501) - imports
    content = re.sub(
        r'from rexus\.utils\.unified_sanitizer import unified_sanitizer, sanitize_string',
        'from rexus.utils.unified_sanitizer import (\n    unified_sanitizer, sanitize_string\n)',
        content
    )
    
    content = re.sub(
        r'from rexus\.utils\.message_system import show_info, show_error, show_warning, show_success',
        'from rexus.utils.message_system import (\n    show_info, show_error, show_warning, show_success\n)',
        content
    )
    
    # 2. Eliminar líneas en blanco excesivas (E303)
    content = re.sub(r'\n\n\n\n\n+', '\n\n\n', content)
    
    # 3. Corregir líneas largas en métodos - dividir parámetros largos
    content = re.sub(
        r'def crear_servicio_transporte\(self, datos_servicio: Dict\[str, Any\]\) -> bool:',
        'def crear_servicio_transporte(self,\n                                datos_servicio: Dict[str, Any]) -> bool:',
        content
    )
    
    content = re.sub(
        r'def actualizar_servicio_transporte\(self, servicio_id: int, datos_servicio: Dict\[str, Any\]\) -> bool:',
        'def actualizar_servicio_transporte(self, servicio_id: int,\n                                      datos_servicio: Dict[str, Any]) -> bool:',
        content
    )
    
    # 4. Corregir show_error y show_success largos
    content = re.sub(
        r'show_error\(self\.view, "Error", "No hay conexión al modelo de datos"\)',
        'show_error(self.view, "Error",\n                   "No hay conexión al modelo de datos")',
        content
    )
    
    content = re.sub(
        r'show_success\(self\.view, "Éxito", "Servicio actualizado correctamente"\)',
        'show_success(self.view, "Éxito",\n                     "Servicio actualizado correctamente")',
        content
    )
    
    content = re.sub(
        r'show_error\(self\.view, "Error", "No se pudo actualizar el servicio"\)',
        'show_error(self.view, "Error",\n                   "No se pudo actualizar el servicio")',
        content
    )
    
    # 5. Corregir líneas de método largas con hasattr
    content = re.sub(
        r'if self\.model and hasattr\(self\.model, \'actualizar_servicio_transporte\'\):',
        'if (self.model and \n        hasattr(self.model, \'actualizar_servicio_transporte\')):'
        , content
    )
    
    content = re.sub(
        r'if self\.model and hasattr\(self\.model, \'generar_codigo_servicio\'\):',
        'if (self.model and \n        hasattr(self.model, \'generar_codigo_servicio\')):'
        , content
    )
    
    # 6. Corregir asignaciones largas
    content = re.sub(
        r'datos_servicio\[\'codigo\'\] = self\.model\.generar_codigo_servicio\(\)',
        'datos_servicio[\'codigo\'] = (\n            self.model.generar_codigo_servicio())',
        content
    )
    
    content = re.sub(
        r'datos_servicio\[\'costo_estimado\'\] = costo_info\.get\(\'costo_estimado\', 0\.0\)',
        'datos_servicio[\'costo_estimado\'] = (\n            costo_info.get(\'costo_estimado\', 0.0))',
        content
    )
    
    # 7. Corregir continuaciones de línea mal indentadas (E122, E128)
    content = re.sub(
        r'logger\.warning\(\n            "Método crear_servicio_transporte no disponible en el modelo"\)',
        'logger.warning(\n                "Método crear_servicio_transporte no disponible")',
        content
    )
    
    content = re.sub(
        r'show_success\(self\.view, "Éxito",\n        "Servicio de transporte creado correctamente"\)',
        'show_success(self.view, "Éxito",\n                     "Servicio de transporte creado correctamente")',
        content
    )
    
    # 8. Corregir líneas largas en métodos de cálculo y estadísticas
    long_lines_patterns = [
        (r'en_transito = len\(\[s for s in servicios if s\.get\(\'estado\'\) == \'EN_TRANSITO\'\]\)',
         'en_transito = len([s for s in servicios \n                        if s.get(\'estado\') == \'EN_TRANSITO\'])'),
        
        (r'completados = len\(\[s for s in servicios if s\.get\(\'estado\'\) == \'COMPLETADO\'\]\)',
         'completados = len([s for s in servicios \n                        if s.get(\'estado\') == \'COMPLETADO\'])'),
        
        (r'cancelados = len\(\[s for s in servicios if s\.get\(\'estado\'\) == \'CANCELADO\'\]\)',
         'cancelados = len([s for s in servicios \n                       if s.get(\'estado\') == \'CANCELADO\'])'),
        
        (r'pendientes = len\(\[s for s in servicios if s\.get\(\'estado\'\) == \'PENDIENTE\'\]\)',
         'pendientes = len([s for s in servicios \n                       if s.get(\'estado\') == \'PENDIENTE\'])'),
    ]
    
    for old_pattern, new_pattern in long_lines_patterns:
        content = re.sub(old_pattern, new_pattern, content)
    
    # 9. Corregir líneas extremadamente largas (>100 chars)
    very_long_patterns = [
        (r'costo_total = sum\(\[s\.get\(\'costo_real\', 0\) for s in servicios if s\.get\(\'estado\'\) == \'COMPLETADO\'\]\)',
         'costo_total = sum([s.get(\'costo_real\', 0) for s in servicios \n                        if s.get(\'estado\') == \'COMPLETADO\'])'),
        
        (r'\'promedio_entrega\': round\(costo_total / completados if completados > 0 else 0, 2\)',
         '\'promedio_entrega\': round(\n                costo_total / completados if completados > 0 else 0, 2)'),
    ]
    
    for old_pattern, new_pattern in very_long_patterns:
        content = re.sub(old_pattern, new_pattern, content)
    
    # 10. Corregir líneas largas en validaciones y mensajes de error
    content = re.sub(
        r'show_error\(self\.view, "Error", "El nombre del proveedor es obligatorio"\)',
        'show_error(self.view, "Error",\n                   "El nombre del proveedor es obligatorio")',
        content
    )
    
    # 11. Corregir definiciones de método largas
    content = re.sub(
        r'def _sanitizar_criterios_busqueda\(self, criterios: Dict\[str, Any\]\) -> Dict\[str, Any\]:',
        'def _sanitizar_criterios_busqueda(self,\n                                    criterios: Dict[str, Any]) -> Dict[str, Any]:',
        content
    )
    
    content = re.sub(
        r'def _sanitizar_datos_servicio\(self, datos: Dict\[str, Any\]\) -> Dict\[str, Any\]:',
        'def _sanitizar_datos_servicio(self,\n                                datos: Dict[str, Any]) -> Dict[str, Any]:',
        content
    )
    
    content = re.sub(
        r'def _calcular_costo_servicio\(self, datos_servicio: Dict\[str, Any\]\) -> Dict\[str, Any\]:',
        'def _calcular_costo_servicio(self,\n                               datos_servicio: Dict[str, Any]) -> Dict[str, Any]:',
        content
    )
    
    # 12. Corregir líneas largas en listas y asignaciones
    content = re.sub(
        r'campos_texto = \[\'origen\', \'destino\', \'descripcion\', \'observaciones\', \'codigo\'\]',
        'campos_texto = [\'origen\', \'destino\', \'descripcion\',\n                     \'observaciones\', \'codigo\']',
        content
    )
    
    content = re.sub(
        r'criterios_sanitizados\[key\] = value\.strip\(\)\[:100\]  # Limitar longitud',
        'criterios_sanitizados[key] = value.strip()[:100]',
        content
    )
    
    # 13. Corregir líneas con hasattr largas
    content = re.sub(
        r'if self\.model and hasattr\(self\.model, \'obtener_servicios_transporte\'\):',
        'if (self.model and \n        hasattr(self.model, \'obtener_servicios_transporte\')):'
        , content
    )
    
    content = re.sub(
        r'if self\.model and hasattr\(self\.model, \'obtener_proveedores_transporte\'\):',
        'if (self.model and \n        hasattr(self.model, \'obtener_proveedores_transporte\')):'
        , content
    )
    
    # 14. Corregir logging largo
    content = re.sub(
        r'logger\.warning\("Método obtener_servicios_transporte no disponible"\)',
        'logger.warning(\n            "Método obtener_servicios_transporte no disponible")',
        content
    )
    
    content = re.sub(
        r'logger\.warning\("Método obtener_proveedores_transporte no disponible"\)',
        'logger.warning(\n            "Método obtener_proveedores_transporte no disponible")',
        content
    )
    
    # 15. Corregir definiciones extremadamente largas
    content = re.sub(
        r'def _registrar_auditoria\(self, accion: str, id_objeto: Optional\[int\], detalles: Optional\[Dict\[str, Any\]\] = None\):',
        'def _registrar_auditoria(self, accion: str, id_objeto: Optional[int],\n                           detalles: Optional[Dict[str, Any]] = None):',
        content
    )
    
    # 16. Corregir logging extremadamente largo
    content = re.sub(
        r'logger\.info\(f"Auditoría - Módulo: logistica, Acción: \{accion\}, ID: \{id_objeto\}, Detalles: \{detalles\}"\)',
        'logger.info(f"Auditoría - Módulo: logistica, "\n                    f"Acción: {accion}, ID: {id_objeto}, "\n                    f"Detalles: {detalles}")',
        content
    )
    
    # 17. Corregir mensaje largo con operador ternario
    content = re.sub(
        r'mensaje = "Transporte eliminado exitosamente" if success else "Error eliminando transporte"',
        'mensaje = ("Transporte eliminado exitosamente" if success \n               else "Error eliminando transporte")',
        content
    )
    
    # 18. Asegurar newline al final
    if not content.endswith('\n'):
        content += '\n'
    
    # 19. Limpiar líneas en blanco con espacios (W293)
    lines = content.split('\n')
    clean_lines = [line.rstrip() for line in lines]
    content = '\n'.join(clean_lines)
    
    # Escribir el archivo corregido si hay cambios
    if content != original_content:
        with open('rexus/modules/logistica/controller.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("TODOS los errores de formato corregidos en logística controller")
        return True
    else:
        print("No se encontraron cambios que hacer")
        return False

if __name__ == "__main__":
    fix_all_format_errors()