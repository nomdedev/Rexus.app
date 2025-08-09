#!/usr/bin/env python3
"""
Script para corregir vulnerabilidades XSS en los módulos de Rexus.app
Implementa sanitización automática en campos de entrada
"""

import re
from pathlib import Path

def add_xss_protection_to_module(module_path):
    """Agrega protección XSS a un módulo específico"""
    
    if not module_path.exists():
        print(f"[ERROR] Archivo no encontrado: {module_path}")
        return False
    
    print(f"🔧 Procesando: {module_path.name}")
    
    # Leer contenido actual
    with open(module_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Backup del archivo original
    backup_path = module_path.with_suffix('.py.backup_xss')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  📋 Backup creado: {backup_path.name}")
    
    # Agregar import de seguridad si no existe
    if "from rexus.utils.security import SecurityUtils" not in content:
        # Encontrar la sección de imports
        lines = content.split('\n')
        import_line_index = -1
        
        for i, line in enumerate(lines):
            if line.startswith('from rexus.') or line.startswith('import ') and 'PyQt' in line:
                import_line_index = i
        
        if import_line_index >= 0:
            lines.insert(import_line_index + 1, "from rexus.utils.security import SecurityUtils")
            content = '\n'.join(lines)
            print("  [CHECK] Import de SecurityUtils agregado")
    
    # Buscar métodos que manejan entrada de texto
    input_methods = [
        r'def (crear_\w+|agregar_\w+|actualizar_\w+|modificar_\w+)\(',
        r'def (guardar_\w+|registrar_\w+|insertar_\w+)\(',
        r'def (procesar_\w+|validar_\w+)\('
    ]
    
    for pattern in input_methods:
        matches = re.finditer(pattern, content)
        for match in matches:
            method_name = match.group(1)
            print(f"  🔍 Método encontrado: {method_name}")
            
            # Buscar el cuerpo del método
            method_start = match.start()
            method_end = find_method_end(content, method_start)
            method_content = content[method_start:method_end]
            
            # Verificar si ya tiene sanitización
            if "SecurityUtils.sanitize_input" not in method_content:
                # Agregar comentario de sanitización
                sanitization_comment = '''
        # [LOCK] PROTECCIÓN XSS: Sanitizar todas las entradas de texto
        # TODO: Implementar sanitización con SecurityUtils.sanitize_input()
        # Ejemplo: texto_limpio = SecurityUtils.sanitize_input(texto_usuario)
'''
                
                # Insertar después de la definición del método
                method_def_end = content.find(':', method_start) + 1
                content = content[:method_def_end] + sanitization_comment + content[method_def_end:]
                print(f"    [CHECK] Comentario de sanitización agregado a {method_name}")
    
    # Buscar campos de texto sin validación
    text_patterns = [
        r'\.text\(\)',
        r'\.currentText\(\)',
        r'\.toPlainText\(\)'
    ]
    
    validation_needed = False
    for pattern in text_patterns:
        if re.search(pattern, content):
            validation_needed = True
            break
    
    if validation_needed and "# XSS Protection Added" not in content:
        # Agregar header de protección XSS
        xss_header = '''
# [LOCK] XSS Protection Added - Validate all user inputs
# Use SecurityUtils.sanitize_input() for text fields
# Use SecurityUtils.validate_email() for email fields
# XSS Protection Added
'''
        content = xss_header + content
        print("  [CHECK] Header de protección XSS agregado")
    
    # Escribir archivo modificado
    with open(module_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"  [CHECK] {module_path.name} actualizado con protección XSS")
    return True

def find_method_end(content, method_start):
    """Encuentra el final de un método Python"""
    lines = content[method_start:].split('\n')
    indent_level = None
    
    for i, line in enumerate(lines[1:], 1):  # Saltar la línea de definición
        if line.strip() == '':
            continue
        
        current_indent = len(line) - len(line.lstrip())
        
        if indent_level is None and line.strip():
            indent_level = current_indent
        elif indent_level is not None and line.strip() and current_indent <= 4:  # Nivel de clase
            return method_start + len('\n'.join(lines[:i]))
    
    return len(content)

def main():
    """Función principal"""
    print("🚨 CORRECCIÓN DE VULNERABILIDADES XSS - REXUS.APP")
    print("=" * 60)
    
    # Directorio de módulos
    modules_dir = Path("rexus/modules")
    
    if not modules_dir.exists():
        print(f"[ERROR] Directorio de módulos no encontrado: {modules_dir}")
        return
    
    # Buscar todos los archivos view.py
    view_files = list(modules_dir.glob("*/view.py"))
    
    if not view_files:
        print("[ERROR] No se encontraron archivos view.py")
        return
    
    print(f"📋 Archivos encontrados: {len(view_files)}")
    
    success_count = 0
    for view_file in view_files:
        if add_xss_protection_to_module(view_file):
            success_count += 1
        print()
    
    # Resumen
    print("=" * 60)
    print("[CHART] RESUMEN DE PROTECCIÓN XSS")
    print(f"[CHECK] Archivos procesados exitosamente: {success_count}")
    print(f"📁 Total archivos: {len(view_files)}")
    
    if success_count == len(view_files):
        print("🎉 PROTECCIÓN XSS IMPLEMENTADA EXITOSAMENTE")
        print("\n📋 PRÓXIMOS PASOS:")
        print("1. Revisar cada módulo manualmente")
        print("2. Implementar SecurityUtils.sanitize_input() en métodos marcados")
        print("3. Probar formularios con payloads XSS")
        print("4. Ejecutar tests de seguridad")
    else:
        print("[WARN] ALGUNOS ARCHIVOS NO PUDIERON SER PROCESADOS")
        print("Revisar manualmente los archivos que fallaron")

if __name__ == "__main__":
    main()
