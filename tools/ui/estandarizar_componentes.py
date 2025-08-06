#!/usr/bin/env python3
"""
MIT License - Copyright (c) 2025 Rexus.app

Estandarizador de Componentes UI - Rexus.app
===========================================

Herramienta para estandarizar componentes UI entre módulos:
- Detecta componentes no estandarizados
- Convierte componentes personalizados a estándar
- Elimina código duplicado de estilos
- Asegura consistencia visual en toda la aplicación

Uso:
python tools/ui/estandarizar_componentes.py
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Agregar ruta del proyecto
root_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_dir))


class ComponentStandardizer:
    """Estandarizador de componentes UI para módulos"""
    
    def __init__(self):
        self.modules_dir = root_dir / "rexus" / "modules"
        self.results = {
            "processed": [],
            "standardized": [],
            "errors": []
        }
        
        # Patrones de componentes a estandarizar
        self.patterns = {
            "custom_title": {
                "detect": r'def crear_titulo\(.*?\):|title_label\s*=\s*QLabel\(["\'].*?["\'].*?\)|titulo_container\s*=\s*QFrame\(\)',
                "standard": "StandardComponents.create_title",
                "description": "Títulos personalizados"
            },
            "custom_buttons": {
                "detect": r'QPushButton\(["\'].*?["\'].*?\)(?!.*StandardComponents)',
                "standard": "StandardComponents.create_*_button", 
                "description": "Botones personalizados"
            },
            "custom_table": {
                "detect": r'QTableWidget\(\)(?!.*StandardComponents)',
                "standard": "StandardComponents.create_standard_table",
                "description": "Tablas personalizadas"
            },
            "inline_styles": {
                "detect": r'\.setStyleSheet\(\s*""".*?"""\s*\)',
                "standard": "style_manager.apply_*",
                "description": "Estilos inline duplicados"
            },
            "missing_import": {
                "detect": r'from rexus\.ui\.standard_components import StandardComponents',
                "standard": "Importación requerida",
                "description": "Falta importación de StandardComponents"
            }
        }
    
    def scan_module(self, module_path: Path) -> Dict:
        """Escanea un módulo en busca de componentes no estandarizados"""
        view_file = module_path / "view.py"
        
        if not view_file.exists():
            return {"skipped": True, "reason": "No view.py found"}
        
        try:
            content = view_file.read_text(encoding='utf-8')
            
            issues = {}
            for pattern_name, pattern_info in self.patterns.items():
                matches = re.findall(pattern_info["detect"], content, re.DOTALL | re.MULTILINE)
                if matches:
                    issues[pattern_name] = {
                        "count": len(matches),
                        "matches": matches[:3],  # Primeros 3 para evitar spam
                        "description": pattern_info["description"],
                        "standard": pattern_info["standard"]
                    }
            
            # Verificar si ya usa componentes estandarizados
            uses_standard = "StandardComponents" in content
            
            return {
                "issues": issues,
                "uses_standard": uses_standard,
                "total_issues": sum(len(matches) for matches in issues.values()),
                "content": content,
                "file_path": view_file
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def generate_standardized_title(self, original_content: str) -> str:
        """Genera código estandarizado para títulos"""
        
        # Buscar títulos existentes con emojis y texto
        title_matches = re.findall(r'QLabel\(["\'](.*?)["\']\)', original_content)
        
        if title_matches:
            # Usar el primer título encontrado
            title_text = title_matches[0]
            
            standardized = f'''
        # Título estandarizado
        StandardComponents.create_title("{title_text}", layout)
'''
        else:
            # Título por defecto basado en nombre del módulo
            standardized = f'''
        # Título estandarizado  
        StandardComponents.create_title("📋 Gestión de Módulo", layout)
'''
        
        return standardized.strip()
    
    def generate_standardized_buttons(self, original_content: str) -> str:
        """Genera código estandarizado para botones"""
        
        # Buscar botones existentes
        button_matches = re.findall(r'QPushButton\(["\'](.*?)["\']\)', original_content)
        
        standardized_buttons = []
        for button_text in button_matches[:5]:  # Máximo 5 botones
            # Determinar tipo de botón basado en texto
            if any(word in button_text.lower() for word in ['nuevo', 'crear', 'agregar', 'add']):
                button_code = f'StandardComponents.create_primary_button("{button_text}")'
            elif any(word in button_text.lower() for word in ['eliminar', 'borrar', 'delete']):
                button_code = f'StandardComponents.create_danger_button("{button_text}")'
            elif any(word in button_text.lower() for word in ['guardar', 'save']):
                button_code = f'StandardComponents.create_success_button("{button_text}")'
            else:
                button_code = f'StandardComponents.create_secondary_button("{button_text}")'
            
            standardized_buttons.append(button_code)
        
        return "\n        ".join(standardized_buttons)
    
    def standardize_module(self, module_path: Path, scan_result: Dict) -> Dict:
        """Estandariza un módulo específico"""
        
        if "error" in scan_result or scan_result.get("skipped"):
            return {"skipped": True, "reason": "Cannot standardize"}
        
        content = scan_result["content"]
        file_path = scan_result["file_path"]
        
        modifications = []
        
        try:
            # 1. Agregar import de StandardComponents si no existe
            if not scan_result["uses_standard"]:
                import_line = "from rexus.ui.standard_components import StandardComponents"
                if import_line not in content:
                    # Buscar línea de imports para insertar
                    import_section = re.search(r'(from PyQt6\.QtWidgets import.*?\))', content, re.DOTALL)
                    if import_section:
                        insert_pos = import_section.end()
                        content = content[:insert_pos] + f"\n\n{import_line}" + content[insert_pos:]
                        modifications.append("Agregado import StandardComponents")
            
            # 2. Reemplazar títulos personalizados
            if "custom_title" in scan_result["issues"]:
                # Buscar y reemplazar método crear_titulo completo
                titulo_method_pattern = r'def crear_titulo\(self, layout.*?\n        layout\.addWidget\(titulo_container\)'
                titulo_matches = re.search(titulo_method_pattern, content, re.DOTALL)
                
                if titulo_matches:
                    # Extraer texto del título
                    title_text_match = re.search(r'QLabel\(["\'](.*?)["\']\)', titulo_matches.group())
                    if title_text_match:
                        title_text = title_text_match.group(1)
                        
                        # Reemplazar todo el método por llamada estándar
                        standardized_call = f'        # Título estandarizado\n        StandardComponents.create_title("{title_text}", layout)'
                        content = content.replace(titulo_matches.group(), standardized_call)
                        modifications.append(f"Estandarizado título: {title_text}")
                        
                        # Eliminar llamada al método crear_titulo
                        content = re.sub(r'\s*self\.crear_titulo\(layout\)', '\n        # Título ya creado arriba', content)
            
            # 3. Reemplazar tablas personalizadas con estándar
            if "custom_table" in scan_result["issues"]:
                # Buscar inicialización de QTableWidget
                table_pattern = r'self\.tabla_\w+\s*=\s*QTableWidget\(\)'
                table_matches = re.findall(table_pattern, content)
                
                for match in table_matches:
                    standardized_table = match.replace('QTableWidget()', 'StandardComponents.create_standard_table()')
                    content = content.replace(match, standardized_table)
                    modifications.append("Estandarizada tabla")
            
            # 4. Limpiar estilos inline duplicados en títulos
            if "inline_styles" in scan_result["issues"]:
                # Remover estilos de títulos ya que StandardComponents los maneja
                title_style_pattern = r'title_label\.setStyleSheet\(.*?\)\s*'
                content = re.sub(title_style_pattern, '# Estilo manejado por StandardComponents\n        ', content, flags=re.DOTALL)
                modifications.append("Limpiados estilos inline duplicados")
            
            # 5. Asegurar que se use style_manager
            if "style_manager" not in content:
                style_import = "from rexus.ui.style_manager import style_manager"
                if style_import not in content:
                    # Agregar import después de StandardComponents
                    std_comp_import = "from rexus.ui.standard_components import StandardComponents"
                    content = content.replace(std_comp_import, f"{std_comp_import}\n{style_import}")
                    modifications.append("Agregado import style_manager")
            
            # Escribir archivo modificado
            if modifications:
                file_path.write_text(content, encoding='utf-8')
                return {
                    "success": True,
                    "modifications": modifications,
                    "file": str(file_path)
                }
            else:
                return {
                    "success": True,
                    "modifications": ["Sin cambios necesarios"],
                    "file": str(file_path)
                }
                
        except Exception as e:
            return {"error": f"Error estandarizando {file_path}: {e}"}
    
    def scan_all_modules(self) -> Dict:
        """Escanea todos los módulos en busca de inconsistencias"""
        
        print(f"\n{'='*60}")
        print(f"[SCAN] Escaneando módulos para componentes no estandarizados")
        print(f"{'='*60}")
        
        if not self.modules_dir.exists():
            print(f"[ERROR] Directorio de módulos no encontrado: {self.modules_dir}")
            return {}
        
        scan_results = {}
        total_issues = 0
        
        # Obtener todos los directorios de módulos
        module_dirs = [d for d in self.modules_dir.iterdir() if d.is_dir() and not d.name.startswith('_')]
        
        print(f"[INFO] Encontrados {len(module_dirs)} módulos para analizar\n")
        
        for module_dir in sorted(module_dirs):
            module_name = module_dir.name
            print(f"[SCANNING] {module_name}")
            
            result = self.scan_module(module_dir)
            scan_results[module_name] = result
            
            if "error" in result:
                print(f"  [ERROR] {result['error']}")
                self.results["errors"].append(f"{module_name}: {result['error']}")
                
            elif result.get("skipped"):
                print(f"  [SKIPPED] {result.get('reason', 'Unknown reason')}")
                
            else:
                issues_count = result.get("total_issues", 0)
                total_issues += issues_count
                uses_standard = result.get("uses_standard", False)
                
                print(f"  [RESULT] Issues: {issues_count}, Uses StandardComponents: {uses_standard}")
                
                if issues_count > 0:
                    for issue_type, issue_data in result.get("issues", {}).items():
                        print(f"    - {issue_data['description']}: {issue_data['count']} casos")
        
        print(f"\n[SUMMARY] Total issues encontrados: {total_issues}")
        return scan_results
    
    def standardize_all_modules(self, scan_results: Dict):
        """Estandariza todos los módulos que necesiten cambios"""
        
        print(f"\n{'='*60}")
        print(f"[STANDARDIZE] Estandarizando componentes UI")
        print(f"{'='*60}")
        
        standardized_count = 0
        
        for module_name, scan_result in scan_results.items():
            
            if scan_result.get("skipped") or "error" in scan_result:
                continue
                
            if scan_result.get("total_issues", 0) == 0:
                print(f"[SKIP] {module_name}: Ya estandarizado")
                continue
            
            print(f"\n[PROCESSING] {module_name}")
            
            module_path = self.modules_dir / module_name
            result = self.standardize_module(module_path, scan_result)
            
            if result.get("success"):
                modifications = result.get("modifications", [])
                print(f"  [SUCCESS] {len(modifications)} modificaciones:")
                for mod in modifications:
                    print(f"    - {mod}")
                
                self.results["standardized"].append({
                    "module": module_name,
                    "modifications": modifications
                })
                standardized_count += 1
                
            elif "error" in result:
                print(f"  [ERROR] {result['error']}")
                self.results["errors"].append(f"{module_name}: {result['error']}")
        
        print(f"\n[COMPLETE] {standardized_count} módulos estandarizados")
    
    def generate_report(self, scan_results: Dict):
        """Genera reporte final de estandarización"""
        
        print(f"\n{'='*60}")
        print(f"[REPORT] Reporte de Estandarización de Componentes UI")
        print(f"{'='*60}")
        
        total_modules = len(scan_results)
        standardized_modules = len(self.results["standardized"])
        error_modules = len(self.results["errors"])
        
        print(f"[STATISTICS] ESTADISTICAS:")
        print(f"   Total modulos analizados: {total_modules}")
        print(f"   Modulos estandarizados: {standardized_modules}")
        print(f"   Errores: {error_modules}")
        print(f"   Porcentaje de exito: {(standardized_modules/total_modules)*100:.1f}%")
        
        if self.results["standardized"]:
            print(f"\n[SUCCESS] MODULOS ESTANDARIZADOS:")
            for item in self.results["standardized"]:
                print(f"   * {item['module']}: {len(item['modifications'])} cambios")
                for mod in item['modifications'][:3]:  # Primeros 3
                    print(f"     - {mod}")
                if len(item['modifications']) > 3:
                    print(f"     - ... y {len(item['modifications']) - 3} mas")
        
        if self.results["errors"]:
            print(f"\n[ERROR] ERRORES:")
            for error in self.results["errors"]:
                print(f"   * {error}")
        
        # Recomendaciones
        print(f"\n[BENEFITS] BENEFICIOS OBTENIDOS:")
        print(f"   * Consistencia visual en toda la aplicacion")
        print(f"   * Reduccion de codigo duplicado")
        print(f"   * Facilita mantenimiento futuro")
        print(f"   * Mejora la experiencia de usuario")
        
        if standardized_modules == total_modules - error_modules:
            print(f"\n[SUCCESS] Todos los modulos han sido estandarizados exitosamente")
            return True
        else:
            print(f"\n[PARTIAL] Estandarizacion parcialmente completada")
            return False


def main():
    """Función principal"""
    
    print("[UI STANDARDIZATION] Estandarizador de Componentes UI - Rexus.app")
    print("=" * 70)
    print("Herramienta para estandarizar componentes UI entre módulos")
    
    try:
        standardizer = ComponentStandardizer()
        
        # Fase 1: Escanear módulos
        scan_results = standardizer.scan_all_modules()
        
        if not scan_results:
            print("[ERROR] No se pudieron escanear los módulos")
            return 1
        
        # Fase 2: Estandarizar componentes
        standardizer.standardize_all_modules(scan_results)
        
        # Fase 3: Generar reporte
        success = standardizer.generate_report(scan_results)
        
        if success:
            print(f"\n[INFO] Estandarización completada exitosamente")
            return 0
        else:
            print(f"\n[WARNING] Estandarización completada con algunas limitaciones")
            return 1
            
    except Exception as e:
        print(f"[ERROR] Error ejecutando estandarizador: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())