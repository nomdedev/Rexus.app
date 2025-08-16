#!/usr/bin/env python3
"""
Script para migrar controladores a BaseController automáticamente
Acelera la corrección masiva de problemas de estabilidad

Fecha: 15/08/2025
Objetivo: Aplicar defensas BaseController a todos los controladores
"""

import os
import re
from pathlib import Path

def migrate_controller_to_base(file_path, module_name):
    """
    Migra un controlador específico para usar BaseController.
    
    Args:
        file_path: Ruta al archivo del controlador
        module_name: Nombre del módulo para el logging
    """
    print(f"Migrando controlador: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Hacer backup del archivo original
    backup_path = file_path + '.backup'
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Aplicar transformaciones
    new_content = content
    
    # 1. Agregar import de BaseController
    if 'from rexus.core.base_controller import BaseController' not in new_content:
        # Encontrar el lugar apropiado para insertar el import
        import_pattern = r'(from PyQt6\.QtCore import [^\n]+)\n'
        if re.search(import_pattern, new_content):
            new_content = re.sub(
                import_pattern,
                r'\1\nfrom rexus.core.base_controller import BaseController\n',
                new_content
            )
    
    # 2. Cambiar herencia de QObject a BaseController
    class_pattern = r'class (\w+Controller)\(QObject\):'
    if re.search(class_pattern, new_content):
        new_content = re.sub(
            class_pattern,
            r'class \1(BaseController):',
            new_content
        )
    
    # 3. Actualizar el constructor para usar BaseController
    constructor_pattern = r'def __init__\(self[^)]*\):\s*\n\s*super\(\).__init__\(\)'
    if re.search(constructor_pattern, new_content):
        # Buscar el patrón más específico del constructor
        specific_pattern = r'def __init__\(self, model[^)]*\):\s*\n\s*super\(\).__init__\(\)\s*\n\s*self\.model = model\s*\n\s*self\.view = view\s*\n\s*self\.db_connection = [^\n]+\s*\n'
        
        replacement = f'''def __init__(self, model, view, db_connection=None):
        # BaseController inicializa los componentes básicos
        super().__init__("{module_name}", model, view, db_connection)
        
        # Configuración específica del controlador (agregar aquí si es necesario)
        '''
        
        if re.search(specific_pattern, new_content, re.DOTALL):
            new_content = re.sub(specific_pattern, replacement, new_content, flags=re.DOTALL)
    
    # 4. Agregar métodos de defensas si no existen
    defensive_methods = '''
    def ensure_safe_operation(self, operation_name, operation_func, *args, **kwargs):
        """Ejecuta una operación de forma segura con defensas completas."""
        try:
            if not self._ensure_model_available(operation_name):
                return None
            
            self.logger.debug(f"Ejecutando operación segura: {operation_name}")
            result = operation_func(*args, **kwargs)
            self.logger.info(f"Operación {operation_name} completada exitosamente")
            return result
            
        except Exception as e:
            error_msg = f"Error en {operation_name}: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.show_error_message(error_msg)
            return None
    '''
    
    if 'ensure_safe_operation' not in new_content:
        # Agregar al final de la clase
        class_end_pattern = r'(\n\s*def cleanup\(self\):[^\n]*(?:\n(?:\s{4,}[^\n]*|\s*$))*)'
        if not re.search(class_end_pattern, new_content):
            # Si no hay cleanup, agregar al final de la clase
            new_content = new_content.rstrip() + defensive_methods
    
    # Escribir el archivo actualizado
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✅ Migración completada: {file_path}")

def main():
    """Migra todos los controladores críticos."""
    
    # Definir controladores a migrar y sus nombres de módulo
    controllers_to_migrate = [
        ('rexus/modules/compras/controller.py', 'compras'),
        ('rexus/modules/herrajes/controller.py', 'herrajes'), 
        ('rexus/modules/auditoria/controller.py', 'auditoria'),
        ('rexus/modules/configuracion/controller.py', 'configuracion'),
        ('rexus/modules/mantenimiento/controller.py', 'mantenimiento'),
        ('rexus/modules/notificaciones/controller.py', 'notificaciones'),
    ]
    
    base_path = Path('.')
    
    for controller_path, module_name in controllers_to_migrate:
        full_path = base_path / controller_path
        
        if full_path.exists():
            try:
                migrate_controller_to_base(str(full_path), module_name)
            except Exception as e:
                print(f"❌ Error migrando {controller_path}: {e}")
        else:
            print(f"⚠️ Archivo no encontrado: {controller_path}")
    
    print("\n🎉 Migración masiva de controladores completada!")
    print("📝 Se crearon archivos .backup para seguridad")

if __name__ == "__main__":
    main()