#!/usr/bin/env python3
"""
Script para corregir comentarios XSS que rompen strings
Rexus.app - Corrección de Errores Críticos

Corrige específicamente los comentarios XSS mal ubicados que 
interrumpen strings y causan errores de sintaxis.
"""

import re
from pathlib import Path

def fix_broken_strings_by_xss_comments(content: str) -> str:
    """Corrige strings rotos por comentarios XSS mal ubicados."""
    
    # Patrón 1: String que se rompe por comentarios XSS
    # Ejemplo: "Hasta:\n        # 🔒 PROTECCIÓN XSS...\n"))
    pattern1 = r'("[^"]*?)\n\s*#\s*🔒.*?XSS.*?\n.*?#.*?\n.*?#.*?\n([^"]*")'
    content = re.sub(pattern1, r'\1\2', content, flags=re.DOTALL)
    
    # Patrón 2: String interrumpido por comentarios en la misma línea
    # Ejemplo: "background-color:\n        # 🔒...\n #f39c12;"
    pattern2 = r'("[^"]*?:)\n\s*#\s*🔒.*?XSS.*?\n.*?#.*?\n.*?#.*?\n\s*([^"]*")'
    content = re.sub(pattern2, r'\1 \2', content, flags=re.DOTALL)
    
    # Patrón 3: Comentarios XSS dentro de parámetros de función
    pattern3 = r'(\([^)]*?"[^"]*?)\n\s*#\s*🔒.*?XSS.*?\n.*?#.*?\n.*?#.*?\n([^"]*"[^)]*\))'
    content = re.sub(pattern3, r'\1\2', content, flags=re.DOTALL)
    
    # Limpiar comentarios XSS que quedaron colgando
    lines = content.split('\n')
    cleaned_lines = []
    skip_xss_block = False
    
    for line in lines:
        # Detectar inicio de bloque XSS mal ubicado
        if '🔒' in line and 'XSS' in line and line.strip().startswith('#'):
            skip_xss_block = True
            continue
        
        # Detectar continuación del bloque XSS
        if skip_xss_block and line.strip().startswith('#'):
            continue
        
        # Fin del bloque XSS
        if skip_xss_block and not line.strip().startswith('#'):
            skip_xss_block = False
        
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def fix_specific_patterns(content: str) -> str:
    """Corrige patrones específicos encontrados en los archivos."""
    
    # Corregir strings específicos rotos
    specific_fixes = [
        # Patrón: "Hasta:" seguido de comentarios
        (r'"Hasta:\s*\n\s*#.*?XSS.*?\n.*?#.*?\n.*?#.*?\n\s*"\)', '"Hasta:")'),
        
        # Patrón: "background-color:" seguido de comentarios  
        (r'"background-color:\s*\n\s*#.*?XSS.*?\n.*?#.*?\n.*?#.*?\n\s*#([^"]*)"', r'"background-color: #\1"'),
        
        # Patrón: "Nuevo Estado:" seguido de comentarios
        (r'"Nuevo Estado:\s*\n\s*#.*?XSS.*?\n.*?#.*?\n.*?#.*?\n\s*"\)', '"Nuevo Estado:")'),
        
        # Limpiar comentarios TODO sueltos después de correcciones
        (r'\n\s*#\s*TODO:.*?sanitización.*?\n', '\n'),
        (r'\n\s*#\s*Ejemplo:.*?SecurityUtils\.sanitize_input.*?\n', '\n'),
    ]
    
    for pattern, replacement in specific_fixes:
        content = re.sub(pattern, replacement, content, flags=re.DOTALL | re.IGNORECASE)
    
    return content

def fix_file(file_path: Path) -> bool:
    """Corrige un archivo específico."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Aplicar correcciones
        content = original_content
        content = fix_broken_strings_by_xss_comments(content)
        content = fix_specific_patterns(content)
        
        # Guardar si hubo cambios
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        return False

def main():
    """Función principal."""
    project_root = Path(__file__).parent.parent
    
    # Archivos específicos con errores conocidos
    problem_files = [
        "rexus/modules/compras/view.py",
        "rexus/modules/inventario/view.py", 
        "rexus/modules/obras/view.py",
        "rexus/modules/usuarios/view.py",
        "rexus/modules/logistica/view.py",
        "rexus/modules/herrajes/view.py",
        "rexus/modules/pedidos/view.py",
        "rexus/modules/configuracion/view.py",
        "rexus/modules/auditoria/view.py"
    ]
    
    print("Corrigiendo comentarios XSS que rompen strings...")
    
    fixes_applied = 0
    for file_path_str in problem_files:
        file_path = project_root / file_path_str
        if file_path.exists():
            print(f"Procesando: {file_path_str}")
            if fix_file(file_path):
                print(f"  - Corregido")
                fixes_applied += 1
            else:
                print(f"  - Sin cambios")
        else:
            print(f"No encontrado: {file_path_str}")
    
    print(f"\\nCorrecciones aplicadas: {fixes_applied}")
    return fixes_applied

if __name__ == "__main__":
    main()