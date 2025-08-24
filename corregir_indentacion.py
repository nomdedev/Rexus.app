"""
Script para corregir problemas de indentación causados por correcciones automáticas
"""

import os

def is_orphan_else(lines, i):
    """Determina si un else: es huérfano."""
    if i == 0:
        return False
    prev_line = lines[i-1].strip()
    if not prev_line.endswith(':'):
        return True
    if not any(kw in prev_line for kw in ['if ', 'try:', 'except', 'for ', 'while ']):
        return True
    return False

def comment_orphan_else(lines, i):
    """Comenta el else: huérfano y su contenido."""
    corrected = []
    line = lines[i]
    indent = len(line) - len(line.lstrip())
    corrected.append(' ' * indent + '# else: # Comentado - bloque huérfano\n')
    i += 1
    while i < len(lines) and (lines[i].strip() == '' or len(lines[i]) - len(lines[i].lstrip()) > indent):
        if lines[i].strip():
            content_indent = len(lines[i]) - len(lines[i].lstrip())
            corrected.append(' ' * content_indent + '# ' + lines[i].lstrip())
        else:
            corrected.append(lines[i])
        i += 1
    return corrected, i

def fix_indentation(line):
    """Corrige la indentación de una línea si es necesario."""
    if line.strip() and not line.startswith('#'):
        indent = len(line) - len(line.lstrip())
        if indent % 4 != 0 and indent > 0:
            new_indent = ((indent + 3) // 4) * 4
            return ' ' * new_indent + line.lstrip()
    return line

def corregir_indentacion_archivos():
    """Corrige problemas de indentación en archivos Python."""
    archivos_corregidos = []
    archivos_principales = [
        'rexus/modules/administracion/controller.py',
        'rexus/modules/administracion/recursos_humanos/controller.py',
        'rexus/modules/compras/controller.py',
        'rexus/modules/herrajes/controller.py',
        'rexus/modules/mantenimiento/controller.py'
    ]
    for filepath in archivos_principales:
        if not os.path.exists(filepath):
            continue
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            corrected_lines = []
            i = 0
            while i < len(lines):
                line = lines[i]
                if line.strip() == 'else:' and is_orphan_else(lines, i):
                    commented, new_i = comment_orphan_else(lines, i)
                    corrected_lines.extend(commented)
                    i = new_i
                    continue
                corrected_lines.append(fix_indentation(line))
                i += 1
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(corrected_lines)
            archivos_corregidos.append(filepath)
            print(f"Corregido: {filepath}")
        except Exception as e:
            print(f"Error corrigiendo {filepath}: {e}")
    return archivos_corregidos

def compilar_y_verificar(archivos):
    """Verifica la compilación de los archivos corregidos."""
    
    import py_compile
    
    errores = []
    exitosos = []
    
    for archivo in archivos:
        try:
            py_compile.compile(archivo, doraise=True)
            exitosos.append(archivo)
        except Exception as e:
            errores.append(f"{archivo}: {e}")
    
    return exitosos, errores

# Ejecutar correcciones
if __name__ == "__main__":
    print("Corrigiendo problemas de indentación...")
    
    archivos_corregidos = corregir_indentacion_archivos()
    
    if archivos_corregidos:
        print(f"\nVerificando compilación de {len(archivos_corregidos)} archivos corregidos...")
        exitosos, errores = compilar_y_verificar(archivos_corregidos)
        
        print(f"\n✅ Archivos que compilan: {len(exitosos)}")
        print(f"❌ Archivos con errores: {len(errores)}")
        
        if errores:
            print("\nErrores restantes:")
            for error in errores:
                print(f"  - {error}")
        else:
            print("\n🎉 ¡Todos los archivos corregidos compilan correctamente!")
    else:
        print("No se encontraron archivos para corregir.")
