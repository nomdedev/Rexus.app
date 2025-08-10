#!/usr/bin/env python3
"""
Script para implementar decoradores @auth_required automáticamente
Activa el sistema de autorización en métodos críticos
"""

import re
from pathlib import Path

def add_auth_decorators_to_file(file_path):
    """Agrega decoradores @auth_required a métodos críticos"""
    
    if not file_path.exists():
        return False
    
    print(f"🔧 Procesando: {file_path.name}")
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        print(f"  [ERROR] Error leyendo archivo: {e}")
        return False
    
    # Backup
    backup_path = file_path.with_suffix('.py.backup_decorators')
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # Verificar si ya tiene decoradores
    if "@auth_required" in content:
        print("  [CHECK] Ya tiene decoradores aplicados")
        return True
    
    # Buscar métodos que necesitan autorización y tienen comentarios TODO
    pattern = r'(\s*)(# [LOCK] VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA\s*\n\s*# TODO: Implementar @auth_required.*?\n)(.*?)(def\s+(\w+)\s*\()'
    
    def replace_auth_comment(match):
        indent = match.group(1)
        def_line = match.group(4)
        method_name = match.group(5)
        
        # Determinar el decorador apropiado según el método
        if any(keyword in method_name for keyword in ['eliminar', 'borrar', 'delete']):
            decorator = "@admin_required"
        elif any(keyword in method_name for keyword in ['crear', 'agregar', 'nuevo', 'actualizar', 'modificar']):
            decorator = "@manager_required"
        else:
            decorator = "@auth_required"
        
        return f"{indent}{decorator}\n{indent}{def_line}"
    
    # Aplicar reemplazos
    new_content = re.sub(pattern, replace_auth_comment, content, flags=re.DOTALL)
    
    # Verificar si se hicieron cambios
    if new_content != content:
        # Asegurar imports
        if "from rexus.core.auth_manager import" not in new_content:
            # Agregar import después de otros imports
            import_pattern = r'(from rexus\..*?import.*?\n)'
            if re.search(import_pattern, new_content):
                new_content = re.sub(
                    import_pattern,
                    r'\1from rexus.core.auth_manager import auth_required, admin_required, manager_required\n',
                    new_content,
                    count=1
                )
            else:
                # Agregar al principio después de docstring
                lines = new_content.split('\n')
                insert_line = 0
                for i, line in enumerate(lines):
                    if line.strip() and not line.startswith('#') and not line.startswith('"""') and not line.strip() == '"""':
                        insert_line = i
                        break
                
                lines.insert(insert_line, "from rexus.core.auth_manager import auth_required, admin_required, manager_required")
                new_content = '\n'.join(lines)
        
        # Escribir archivo
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        decorators_added = new_content.count("@auth_required") + new_content.count("@admin_required") + new_content.count("@manager_required")
        print(f"  [CHECK] {decorators_added} decoradores agregados")
        return True
    else:
        print("  [WARN] No se encontraron métodos para decorar")
        return True

def main():
    """Función principal"""
    print("🔐 IMPLEMENTACIÓN DE DECORADORES DE AUTORIZACIÓN")
    print("=" * 55)
    
    # Buscar archivos con comentarios de autorización
    python_files = list(Path("rexus/modules").rglob("*.py"))
    
    files_to_process = []
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if "[LOCK] VERIFICACIÓN DE AUTORIZACIÓN REQUERIDA" in content:
                    files_to_process.append(py_file)
        except Exception:
            continue
    
    if not files_to_process:
        print("[ERROR] No se encontraron archivos con comentarios de autorización")
        return
    
    print(f"📋 Archivos a procesar: {len(files_to_process)}")
    
    success_count = 0
    for file_path in files_to_process:
        if add_auth_decorators_to_file(file_path):
            success_count += 1
        print()
    
    print("=" * 55)
    print("[CHART] RESUMEN DE IMPLEMENTACIÓN")
    print(f"[CHECK] Archivos procesados: {success_count}/{len(files_to_process)}")
    
    if success_count == len(files_to_process):
        print("🎉 DECORADORES IMPLEMENTADOS EXITOSAMENTE")
        print("\n📋 PRÓXIMOS PASOS:")
        print("1. Probar sistema de autorización")
        print("2. Configurar roles de usuario")
        print("3. Validar permisos en la aplicación")
    else:
        print("[WARN] ALGUNOS ARCHIVOS NO PUDIERON SER PROCESADOS")

if __name__ == "__main__":
    main()
