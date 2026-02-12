#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corregir el error específico del controller de usuarios
"""

def fix_usuarios_controller():
    """Corrige el error específico en el controller de usuarios"""
    try:
        with open('rexus/modules/11_usuarios/controller.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Reemplazar la línea problemática
        old_line = '            errores.append(f"Rol inválido. Debe ser uno de: {\', \'.join(self.model.ROLES.keys())}")'
        new_line = '            errores.append(f"Rol inválido. Debe ser uno de: {\\', \\'.join(self.model.ROLES.keys())}")'
        
        content = content.replace(old_line, new_line)
        
        # También corregir la línea de estados si existe
        old_line2 = '            errores.append(f"Estado inválido. Debe ser uno de: {\', \'.join(self.model.ESTADOS.keys())}")'
        new_line2 = '            errores.append(f"Estado inválido. Debe ser uno de: {\\', \\'.join(self.model.ESTADOS.keys())}")'
        
        content = content.replace(old_line2, new_line2)
        
        with open('rexus/modules/11_usuarios/controller.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("Controller de usuarios corregido")
        return True
        
    except Exception as e:
        print(f"Error corrigiendo controller de usuarios: {e}")
        return False

if __name__ == "__main__":
    fix_usuarios_controller()