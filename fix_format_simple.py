#!/usr/bin/env python3
"""
Script simple para corregir errores de formato específicos
"""

def fix_remaining_issues():
    """Corrige los errores de formato restantes."""
    
    with open('rexus/modules/logistica/controller.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Corregir líneas con indentación incorrecta en show_success
    content = content.replace(
        'show_success(self.view, "Éxito",\n        "Servicio de transporte creado correctamente")',
        'show_success(self.view, "Éxito",\n                     "Servicio de transporte creado correctamente")'
    )
    
    content = content.replace(
        'show_success(self.view, "Éxito",\n        "Proveedor de transporte creado correctamente")',
        'show_success(self.view, "Éxito",\n                     "Proveedor de transporte creado correctamente")'
    )
    
    # Corregir líneas muy largas con saltos apropiados
    long_lines = [
        ('logger.warning("Método crear_servicio_transporte no disponible en el modelo")',
         'logger.warning(\n            "Método crear_servicio_transporte no disponible en el modelo")'),
        
        ('logger.warning("Método actualizar_servicio_transporte no disponible en el modelo")',
         'logger.warning(\n            "Método actualizar_servicio_transporte no disponible")'),
        
        ('logger.warning("Método eliminar_servicio_transporte no disponible en el modelo")',
         'logger.warning(\n            "Método eliminar_servicio_transporte no disponible")'),
        
        ('logger.warning("Método actualizar_estado_servicio no disponible en el modelo")',
         'logger.warning(\n            "Método actualizar_estado_servicio no disponible")'),
        
        ('logger.warning("Método crear_proveedor_transporte no disponible en el modelo")',
         'logger.warning(\n            "Método crear_proveedor_transporte no disponible")'),
        
        ('logger.warning("Método actualizar_proveedor_transporte no disponible en el modelo")',
         'logger.warning(\n            "Método actualizar_proveedor_transporte no disponible")'),
    ]
    
    for old, new in long_lines:
        content = content.replace(old, new)
    
    # Asegurar newline al final
    if not content.endswith('\n'):
        content += '\n'
    
    # Escribir si hay cambios
    if content != original:
        with open('rexus/modules/logistica/controller.py', 'w', encoding='utf-8') as f:
            f.write(content)
        print("Correcciones de formato aplicadas")
        return True
    else:
        print("No hay cambios que aplicar")
        return False

if __name__ == "__main__":
    fix_remaining_issues()