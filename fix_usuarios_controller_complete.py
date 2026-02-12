#!/usr/bin/env python3
"""
Script para corregir completamente el controller de usuarios
"""

import re

def fix_usuarios_controller():
    """Corrige todos los errores de sintaxis en el controller de usuarios"""
    file_path = "rexus/modules/11_usuarios/controller.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # Correcciones específicas
        corrections = [
            # Corregir línea 357 - f-string mal cerrado
            (r'errores\.append\(f"Estado inválido\. Debe ser uno de: \{\'\.join\(self\.model\.ESTADOS\.keys\(\)"\}\)', 
             'errores.append(f"Estado invalido. Debe ser uno de: {\\\', \\\'.join(self.model.ESTADOS.keys())}")'),
            
            # Corregir línea 371 - f-string mal formado
            (r'f"• {error} for error in errores', 
             '"\\n".join(f"• {error}" for error in errores)'),
            
            # Corregir línea 514 - comillas extra
            (r'print\(f"\[CHECK\] \[ADMIN\] Usuario \'\{username\}\' desbloqueado manualmente\)"\)', 
             'print(f"[CHECK] [ADMIN] Usuario \\\'{username}\\\' desbloqueado manualmente")'),
            
            # Corregir línea 592 - escapes incorrectos
            (r'print\(f"\[USUARIOS CONTROLLER\] Usuario actual: \{usuario\.get\(\\\'nombre_completo\\\', \\\'Desconocido\\\'\)\}\)', 
             'print(f"[USUARIOS CONTROLLER] Usuario actual: {usuario.get(\\\"nombre_completo\\\", \\\"Desconocido\\\")}")'),
            
            # Corregir línea 671 - f-string sin cerrar
            (r'print\(f"\[ERROR USUARIOS CONTROLLER\] Error en cleanup: \{e\}\)', 
             'print(f"[ERROR USUARIOS CONTROLLER] Error en cleanup: {e}")'),
        ]
        
        # Aplicar correcciones
        for pattern, replacement in corrections:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
        
        # Corrección general para f-strings sin cerrar
        content = re.sub(r'f"([^"]*)\{([^}]*)\}([^"]*)"', lambda m: f'f"{m.group(1)}{{{m.group(2)}}}{m.group(3)}"', content)
        
        # Guardar archivo corregido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"OK Archivo {file_path} corregido exitosamente")
        return True
        
    except Exception as e:
        print(f"ERROR Corrigiendo archivo {file_path}: {e}")
        return False

if __name__ == "__main__":
    print("Corrigiendo controller de usuarios...")
    fix_usuarios_controller()