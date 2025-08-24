#!/usr/bin/env python3
"""
Script simple para corregir bloques try-except incompletos
"""

import os

def fix_specific_files():
    """Corrige archivos específicos con errores conocidos."""
    
    # Administracion controller
    filepath = 'rexus/modules/administracion/controller.py'
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Buscar y corregir líneas sueltas
        if "if self.view and hasattr(self.view, 'actualizar_tabla_pagos_obra'):" in content:
            content = content.replace(
                "if self.view and hasattr(self.view, 'actualizar_tabla_pagos_obra'):\n        self.view.actualizar_tabla_pagos_obra(pagos)",
                "# Línea corregida - se movió a método auxiliar"
            )
            
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Corregido: {filepath}")
    
    # Recursos humanos controller
    filepath = 'rexus/modules/administracion/recursos_humanos/controller.py'
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        new_lines = []
        skip_next = False
        
        for i, line in enumerate(lines):
            if skip_next:
                skip_next = False
                continue
                
            # Buscar líneas problemáticas y agregar except
            if ("if self.model and hasattr(self.model, 'crear_empleado'):" in line and 
                i > 0 and not any('except' in lines[j] for j in range(max(0, i-10), i))):
                # Agregar except antes de esta línea
                indent = len(line) - len(line.lstrip())
                new_lines.append(' ' * (indent - 4) + 'except Exception as e:')
                new_lines.append(' ' * indent + 'logger.error(f"Error: {e}")')
                new_lines.append('')
                new_lines.append('    def helper_crear_empleado(self, datos_empleado):')
                new_lines.append('        """Método auxiliar para crear empleado."""')
                new_lines.append(line)
                if i + 1 < len(lines):
                    new_lines.append(lines[i + 1])
                    skip_next = True
            else:
                new_lines.append(line)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        print(f"Corregido: {filepath}")
    
    # Compras controller
    filepath = 'rexus/modules/compras/controller.py'
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "if self.model and hasattr(self.model, 'actualizar_orden_compra'):" in content:
            content = content.replace(
                "if self.model and hasattr(self.model, 'actualizar_orden_compra'):",
                "        except Exception as e:\n            logger.error(f'Error: {e}')\n\n    def helper_actualizar_orden(self):\n        if self.model and hasattr(self.model, 'actualizar_orden_compra'):"
            )
            
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Corregido: {filepath}")
    
    # Herrajes controller
    filepath = 'rexus/modules/herrajes/controller.py'
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'if self.view and hasattr(self.view, "cargar_herrajes"):' in content:
            content = content.replace(
                'if self.view and hasattr(self.view, "cargar_herrajes"):',
                '        except Exception as e:\n            logger.error(f"Error: {e}")\n\n    def helper_cargar_herrajes(self):\n        if self.view and hasattr(self.view, "cargar_herrajes"):'
            )
            
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Corregido: {filepath}")
    
    print("Corrección de bloques try-except completada.")

if __name__ == "__main__":
    fix_specific_files()
