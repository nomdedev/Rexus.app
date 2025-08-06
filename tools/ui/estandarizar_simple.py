#!/usr/bin/env python3
"""
MIT License - Copyright (c) 2025 Rexus.app

Estandarizador Simple de Componentes UI - Rexus.app
==================================================

Herramienta simplificada para estandarizar componentes UI:
- Asegura que todos los módulos usen StandardComponents
- Convierte tablas personalizadas a estándar
- Elimina código duplicado básico

Uso:
python tools/ui/estandarizar_simple.py
"""

import re
import sys
from pathlib import Path

# Agregar ruta del proyecto
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))


def process_module_view(view_file: Path) -> bool:
    """Procesa un archivo view.py individual"""
    if not view_file.exists():
        return False
    
    try:
        content = view_file.read_text(encoding='utf-8')
        original_content = content
        modifications = []
        
        # 1. Asegurar import de StandardComponents
        if "from rexus.ui.standard_components import StandardComponents" not in content:
            # Buscar donde insertar el import
            import_pattern = r'(from PyQt6\.QtWidgets import.*?\n)'
            match = re.search(import_pattern, content)
            if match:
                insert_pos = match.end()
                new_import = "\nfrom rexus.ui.standard_components import StandardComponents"
                content = content[:insert_pos] + new_import + content[insert_pos:]
                modifications.append("Added StandardComponents import")
        
        # 2. Reemplazar QTableWidget() por StandardComponents.create_standard_table()
        # Solo si no está ya usando StandardComponents
        table_pattern = r'(\w+)\s*=\s*QTableWidget\(\)'
        matches = re.findall(table_pattern, content)
        
        for table_var in matches:
            old_line = f"{table_var} = QTableWidget()"
            new_line = f"{table_var} = StandardComponents.create_standard_table()"
            if old_line in content and new_line not in content:
                content = content.replace(old_line, new_line)
                modifications.append(f"Standardized table: {table_var}")
        
        # 3. Simplificar títulos largos y convertir a StandardComponents
        # Buscar métodos crear_titulo personalizados
        titulo_method_pattern = r'def crear_titulo\(.*?\n.*?layout\.addWidget\(.*?\)'
        titulo_matches = re.findall(titulo_method_pattern, content, re.DOTALL)
        
        if titulo_matches:
            # Buscar texto del título
            for match in titulo_matches:
                title_text_search = re.search(r'QLabel\(["\']([^"\']*)["\']', match)
                if title_text_search:
                    title_text = title_text_search.group(1)
                    # Reemplazar llamada al método crear_titulo
                    content = re.sub(r'self\.crear_titulo\(layout\)', 
                                   f'StandardComponents.create_title("{title_text}", layout)', 
                                   content)
                    # Comentar el método crear_titulo
                    content = content.replace(match, f"# {match.replace(chr(10), chr(10)+'# ')}")
                    modifications.append(f"Standardized title: {title_text[:30]}...")
        
        # 4. Asegurar import de style_manager si no existe
        if "from rexus.ui.style_manager import style_manager" not in content:
            if "StandardComponents" in content:
                # Agregar después del import de StandardComponents
                std_import = "from rexus.ui.standard_components import StandardComponents"
                style_import = "from rexus.ui.style_manager import style_manager"
                content = content.replace(std_import, f"{std_import}\n{style_import}")
                modifications.append("Added style_manager import")
        
        # Solo escribir si hubo cambios
        if modifications and content != original_content:
            view_file.write_text(content, encoding='utf-8')
            return True
        
    except Exception as e:
        print(f"Error processing {view_file}: {e}")
        return False
    
    return False


def main():
    """Función principal"""
    print("[SIMPLE UI STANDARDIZATION] Estandarizador Simple de Componentes")
    print("=" * 60)
    
    modules_dir = root_dir / "rexus" / "modules"
    
    if not modules_dir.exists():
        print(f"Error: {modules_dir} not found")
        return 1
    
    # Obtener todos los módulos
    module_dirs = [d for d in modules_dir.iterdir() 
                   if d.is_dir() and not d.name.startswith('_')]
    
    processed = 0
    modified = 0
    
    print(f"Found {len(module_dirs)} modules to process")
    print("-" * 60)
    
    for module_dir in sorted(module_dirs):
        view_file = module_dir / "view.py"
        
        if not view_file.exists():
            print(f"[SKIP] {module_dir.name}: No view.py")
            continue
        
        processed += 1
        print(f"[PROCESSING] {module_dir.name}...")
        
        if process_module_view(view_file):
            print(f"  [MODIFIED] Successfully updated")
            modified += 1
        else:
            print(f"  [OK] No changes needed or already standardized")
    
    # Resumen
    print("-" * 60)
    print(f"[SUMMARY] Processed: {processed}, Modified: {modified}")
    
    if modified > 0:
        print(f"[SUCCESS] {modified} modules have been standardized")
        print("Benefits:")
        print("  * Consistent UI components across all modules") 
        print("  * Standardized tables and imports")
        print("  * Better maintainability")
        return 0
    else:
        print("[INFO] All modules are already standardized")
        return 0


if __name__ == "__main__":
    sys.exit(main())