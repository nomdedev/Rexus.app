#!/usr/bin/env python3
"""
Script para detectar y corregir problemas de importación circular
Analiza las dependencias entre módulos y sugiere refactorizaciones
"""

import ast
import os
from pathlib import Path
from collections import defaultdict, deque
import json

class ImportAnalyzer:
    def __init__(self, root_path):
        self.root_path = Path(root_path)
        self.imports = defaultdict(set)
        self.all_modules = set()
        
    def extract_imports_from_file(self, file_path):
        """Extrae todas las importaciones de un archivo Python."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            imports = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module)
            
            return imports
        except Exception as e:
            print(f"Error analizando {file_path}: {e}")
            return set()
    
    def scan_project(self):
        """Escanea todo el proyecto para encontrar importaciones."""
        print("🔍 Escaneando proyecto para detectar importaciones...")
        
        for py_file in self.root_path.rglob("*.py"):
            # Saltar archivos de test y backups
            if any(skip in str(py_file) for skip in ['test_', '__pycache__', 'backup', '.pyc']):
                continue
                
            relative_path = py_file.relative_to(self.root_path)
            module_name = str(relative_path).replace(os.sep, '.').replace('.py', '')
            
            self.all_modules.add(module_name)
            imports = self.extract_imports_from_file(py_file)
            
            # Filtrar solo importaciones internas del proyecto
            internal_imports = set()
            for imp in imports:
                if imp.startswith('rexus'):
                    internal_imports.add(imp)
            
            self.imports[module_name] = internal_imports
    
    def find_circular_imports(self):
        """Detecta importaciones circulares usando DFS."""
        print("🔍 Detectando importaciones circulares...")
        
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(module, path):
            visited.add(module)
            rec_stack.add(module)
            path.append(module)
            
            for imported_module in self.imports.get(module, set()):
                # Convertir importación a módulo interno
                if imported_module in self.all_modules:
                    if imported_module in rec_stack:
                        # Encontramos un ciclo
                        cycle_start = path.index(imported_module)
                        cycle = path[cycle_start:] + [imported_module]
                        cycles.append(cycle)
                    elif imported_module not in visited:
                        dfs(imported_module, path[:])
            
            rec_stack.remove(module)
            path.pop()
        
        for module in self.all_modules:
            if module not in visited:
                dfs(module, [])
        
        return cycles
    
    def analyze_dependencies(self):
        """Analiza las dependencias del proyecto."""
        print("📊 Analizando dependencias del proyecto...")
        
        # Contar importaciones por módulo
        import_counts = {}
        for module, imports in self.imports.items():
            import_counts[module] = len(imports)
        
        # Módulos más importados
        imported_by = defaultdict(int)
        for module, imports in self.imports.items():
            for imp in imports:
                imported_by[imp] += 1
        
        return {
            'modules_by_import_count': sorted(import_counts.items(), key=lambda x: x[1], reverse=True)[:10],
            'most_imported_modules': sorted(imported_by.items(), key=lambda x: x[1], reverse=True)[:10]
        }
    
    def suggest_refactoring(self, cycles):
        """Sugiere refactorizaciones para resolver ciclos."""
        suggestions = []
        
        for cycle in cycles:
            print(f"\n🔄 Ciclo detectado: {' -> '.join(cycle)}")
            
            # Analizar el ciclo para sugerir soluciones
            if len(cycle) == 3:  # Ciclo simple A -> B -> A
                suggestions.append({
                    'cycle': cycle,
                    'solution': 'Mover funcionalidad común a un módulo base',
                    'action': f'Crear rexus.core.{cycle[0].split(".")[-1]}_base.py'
                })
            elif any('model' in module for module in cycle):
                suggestions.append({
                    'cycle': cycle,
                    'solution': 'Separar modelos de lógica de negocio',
                    'action': 'Mover modelos a rexus.core.models'
                })
            elif any('view' in module for module in cycle):
                suggestions.append({
                    'cycle': cycle,
                    'solution': 'Usar patrón Observer o Mediator',
                    'action': 'Implementar event system en rexus.core.events'
                })
            else:
                suggestions.append({
                    'cycle': cycle,
                    'solution': 'Usar importación tardía o dependency injection',
                    'action': 'Refactorizar a lazy imports o DI container'
                })
        
        return suggestions

def generate_refactoring_plan(suggestions):
    """Genera un plan de refactorización detallado."""
    plan = {
        'priority_high': [],
        'priority_medium': [],
        'priority_low': [],
        'immediate_fixes': []
    }
    
    for suggestion in suggestions:
        cycle_length = len(suggestion['cycle'])
        
        if cycle_length <= 3:
            plan['priority_high'].append(suggestion)
        elif cycle_length <= 5:
            plan['priority_medium'].append(suggestion)
        else:
            plan['priority_low'].append(suggestion)
        
        # Fixes inmediatos para casos comunes
        if 'model' in str(suggestion['cycle']):
            plan['immediate_fixes'].append({
                'file': suggestion['cycle'][0],
                'action': 'Mover imports dentro de funciones',
                'code': 'def get_related_data():\n    from .related_module import RelatedModel\n    return RelatedModel.query()'
            })
    
    return plan

def main():
    print("🔍 Iniciando análisis de importaciones circulares...")
    
    root_path = Path(".")
    analyzer = ImportAnalyzer(root_path)
    
    # Escanear proyecto
    analyzer.scan_project()
    print(f"✅ Se encontraron {len(analyzer.all_modules)} módulos")
    
    # Detectar ciclos
    cycles = analyzer.find_circular_imports()
    
    if cycles:
        print(f"\n❌ Se detectaron {len(cycles)} importaciones circulares:")
        
        # Generar sugerencias
        suggestions = analyzer.suggest_refactoring(cycles)
        
        # Crear plan de refactorización
        plan = generate_refactoring_plan(suggestions)
        
        # Guardar reporte
        report = {
            'cycles_detected': len(cycles),
            'cycles': [' -> '.join(cycle) for cycle in cycles],
            'suggestions': suggestions,
            'refactoring_plan': plan,
            'dependencies_analysis': analyzer.analyze_dependencies()
        }
        
        with open('circular_imports_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Reporte guardado en: circular_imports_report.json")
        
        # Mostrar prioridades altas
        if plan['priority_high']:
            print("\n🚨 ALTA PRIORIDAD - Corregir inmediatamente:")
            for item in plan['priority_high']:
                print(f"  • {' -> '.join(item['cycle'])}")
                print(f"    Solución: {item['solution']}")
        
        # Mostrar fixes inmediatos
        if plan['immediate_fixes']:
            print("\n🔧 FIXES INMEDIATOS disponibles:")
            for fix in plan['immediate_fixes'][:3]:
                print(f"  • {fix['file']}: {fix['action']}")
        
    else:
        print("\n✅ No se detectaron importaciones circulares")
        
        # Análisis de dependencias
        deps = analyzer.analyze_dependencies()
        print("\n📊 Análisis de dependencias:")
        print("Top módulos con más importaciones:")
        for module, count in deps['modules_by_import_count'][:5]:
            print(f"  • {module}: {count} importaciones")

if __name__ == "__main__":
    main()
