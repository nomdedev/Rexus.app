#!/usr/bin/env python3
"""
Script para corregir errores de sintaxis en el controller de usuarios
"""

import re

def fix_fstring_errors():
    """Corrige errores de f-strings en el controller de usuarios"""
    
    file_path = "rexus/modules/11_usuarios/controller.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Corregir errores específicos encontrados
        corrections = [
            # Error 1: Línea 353 - f-string mal cerrado
            (r'errores\.append\(f"Rol inválido\. Debe ser uno de: \{\'\.join\(self\.model\.ROLES\.keys\(\)"\}\)', 
             'errores.append(f"Rol inválido. Debe ser uno de: {\\\', \\\'.join(self.model.ROLES.keys())}")'),
            
            # Error 2: Línea 357 - f-string mal cerrado
            (r'errores\.append\(f"Estado inválido\. Debe ser uno de: \{\'\.join\(self\.model\.ESTADOS\.keys\(\)"\}\)', 
             'errores.append(f"Estado inválido. Debe ser uno de: {\\\', \\\'.join(self.model.ESTADOS.keys())}")'),
            
            # Error 3: Línea 513 - f-string sin cerrar
            (r'self\.mostrar_exito\(f"Usuario \'\{username\}\' desbloqueado exitosamente\)', 
             'self.mostrar_exito(f"Usuario \\\'{username}\\\' desbloqueado exitosamente")'),
            
            # Error 4: Línea 514 - comillas extra
            (r'print\(f"\[CHECK\] \[ADMIN\] Usuario \'\{username\}\' desbloqueado manualmente\)"\)', 
             'print(f"[CHECK] [ADMIN] Usuario \\\'{username}\\\' desbloqueado manualmente")'),
            
            # Error 5: Línea 519 - f-string sin cerrar
            (r'print\(f"\[ERROR USUARIOS CONTROLLER\] Error desbloqueando usuario: \{e\}\)', 
             'print(f"[ERROR USUARIOS CONTROLLER] Error desbloqueando usuario: {e}")'),
            
            # Error 6: Línea 561 - f-string sin cerrar
            (r'print\(f"\[ERROR USUARIOS CONTROLLER\] Error obteniendo estado de bloqueo: \{e\}\)', 
             'print(f"[ERROR USUARIOS CONTROLLER] Error obteniendo estado de bloqueo: {e}")'),
            
            # Error 7: Línea 573 - f-string sin cerrar
            (r'print\(f"\[AUDITORIA\] \{accion\} - \{modulo\} - \{detalles\}\)', 
             'print(f"[AUDITORIA] {accion} - {modulo} - {detalles}")'),
            
            # Error 8: Línea 592 - f-string sin cerrar
            (r'print\(f"\[USUARIOS CONTROLLER\] Usuario actual: \{usuario\.get\(\'nombre_completo\', \'Desconocido\'\)\}\)', 
             'print(f"[USUARIOS CONTROLLER] Usuario actual: {usuario.get(\\\'nombre_completo\\\', \\\'Desconocido\\\')}")'),
            
            # Error 9: Línea 625 - f-string sin cerrar
            (r'logger\.error\(f"Error cargando página: \{e\}\)', 
             'logger.error(f"Error cargando página: {e}")'),
            
            # Error 10: Línea 627 - f-string sin cerrar
            (r'self\.mostrar_error\("Error", f"Error cargando página: \{str\(e\)\}\)', 
             'self.mostrar_error("Error", f"Error cargando página: {str(e)}")'),
        ]
        
        # Aplicar correcciones
        for pattern, replacement in corrections:
            content = re.sub(pattern, replacement, content)
        
        # Corrección general para f-strings sin cerrar
        content = re.sub(r'f"([^"]*)\{([^}]*)\}([^"]*)"', lambda m: f'f"{m.group(1)}{{{m.group(2)}}}{m.group(3)}"', content)
        
        # Guardar archivo corregido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"OK Archivo {file_path} corregido exitosamente")
        return True
        
    except Exception as e:
        print(f"ERROR corrigiendo archivo {file_path}: {e}")
        return False

if __name__ == "__main__":
    fix_fstring_errors()