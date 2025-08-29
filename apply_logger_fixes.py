#!/usr/bin/env python3
"""
Script para aplicar correcciones automáticas de logger en módulos de Rexus.app
"""

import os
import re

# Lista de archivos identificados que necesitan corrección
FILES_TO_FIX = [
    "rexus/modules/02_inventario/submodules/categorias_manager.py",
    "rexus/modules/02_inventario/submodules/reservas_manager.py", 
    "rexus/modules/03_pedidos/controller.py",
    "rexus/modules/03_pedidos/model.py",
    "rexus/modules/06_herrajes/controller.py", 
    "rexus/modules/07_vidrios/controller.py",
    "rexus/modules/08_mantenimiento/model.py",
    "rexus/modules/09_usuarios/submodules/profiles_manager.py",
    "rexus/modules/10_configuracion/advanced_features.py",
    "rexus/modules/13_notificaciones/controller.py"
]

def fix_logger_usage(file_path):
    """
    Corrige el uso de logger. a self.logger. en un archivo específico.
    Solo corrige líneas que están indentadas (dentro de métodos).
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        modified_lines = 0
        
        # Verificar si el archivo tiene self.logger definido
        has_self_logger = bool(re.search(r'self\.logger\s*=', content))
        
        if not has_self_logger:
            print(f"SKIP: {file_path} - No tiene self.logger definido")
            return 0
        
        for i, line in enumerate(lines):
            # Solo procesar líneas indentadas (dentro de métodos/clases)
            if line.startswith('    ') or line.startswith('\t'):
                # Buscar patrones logger.info, logger.error, etc. pero NO self.logger
                if re.search(r'(?<!self\.)logger\.(info|error|warning|debug|critical)', line):
                    # Reemplazar logger. con self.logger.
                    new_line = re.sub(r'(?<!self\.)logger\.', 'self.logger.', line)
                    if new_line != line:
                        lines[i] = new_line
                        modified_lines += 1
                        print(f"  Line {i+1}: {line.strip()} -> {new_line.strip()}")
        
        if modified_lines > 0:
            # Escribir el archivo modificado
            new_content = '\n'.join(lines)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"FIXED: {file_path} - {modified_lines} líneas corregidas")
        else:
            print(f"OK: {file_path} - No se encontraron problemas")
            
        return modified_lines
        
    except Exception as e:
        print(f"ERROR: {file_path} - {e}")
        return 0

def main():
    """Función principal"""
    base_path = r"D:\martin\Proyectos\Rexus.app"
    total_files_fixed = 0
    total_lines_fixed = 0
    
    print("Aplicando correcciones de logger en archivos identificados...")
    print("=" * 80)
    
    for rel_file_path in FILES_TO_FIX:
        full_path = os.path.join(base_path, rel_file_path)
        
        if os.path.exists(full_path):
            print(f"\nPROCESANDO: {rel_file_path}")
            lines_fixed = fix_logger_usage(full_path)
            if lines_fixed > 0:
                total_files_fixed += 1
                total_lines_fixed += lines_fixed
        else:
            print(f"NOT FOUND: {rel_file_path}")
    
    print("\n" + "=" * 80)
    print(f"RESUMEN FINAL:")
    print(f"  Archivos procesados: {len(FILES_TO_FIX)}")
    print(f"  Archivos corregidos: {total_files_fixed}")
    print(f"  Total líneas corregidas: {total_lines_fixed}")

if __name__ == "__main__":
    main()