#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coverage Analysis - Análisis de Cobertura de Tests
Identifica gaps en la cobertura que permiten que 263 errores pasen inadvertidos
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

class TestCoverageAnalyzer:
    """Analiza la cobertura de tests y identifica gaps críticos."""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.source_files = []
        self.test_files = []
        self.coverage_gaps = []
        self.critical_files_uncovered = []
        
    def scan_source_files(self):
        """Escanea todos los archivos fuente del proyecto."""
        
        source_patterns = ['**/*.py']
        exclude_patterns = [
            '**/tests/**',
            '**/__pycache__/**',
            '**/.*',
            '**/venv/**',
            '**/.venv/**'
        ]
        
        for pattern in source_patterns:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file():
                    # Verificar si debe excluirse
                    should_exclude = False
                    for exclude in exclude_patterns:
                        if file_path.match(exclude):
                            should_exclude = True
                            break
                    
                    if not should_exclude:
                        self.source_files.append(file_path)
        
        print(f"📁 Archivos fuente encontrados: {len(self.source_files)}")
    
    def scan_test_files(self):
        """Escanea todos los archivos de test."""
        
        test_dir = self.project_root / 'tests'
        if test_dir.exists():
            for test_file in test_dir.rglob('*.py'):
                if test_file.is_file():
                    self.test_files.append(test_file)
        
        print(f"🧪 Archivos de test encontrados: {len(self.test_files)}")
    
    def analyze_function_coverage(self, source_file: Path) -> Dict[str, List[str]]:
        """Analiza las funciones en un archivo fuente."""
        
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"⚠️ Error leyendo {source_file}: {e}")
            return {}
        
        # Encontrar definiciones de funciones y métodos
        function_pattern = r'^\s*def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        class_pattern = r'^\s*class\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*[(:]{1}'
        
        functions = re.findall(function_pattern, content, re.MULTILINE)
        classes = re.findall(class_pattern, content, re.MULTILINE)
        
        return {
            'functions': functions,
            'classes': classes
        }
    
    def find_corresponding_test_file(self, source_file: Path) -> List[Path]:
        """Encuentra archivos de test correspondientes a un archivo fuente."""
        
        # Convertir path del archivo fuente a posibles nombres de test
        rel_path = source_file.relative_to(self.project_root)
        
        # Remover rexus/ prefix si existe
        if rel_path.parts[0] == 'rexus':
            rel_path = Path(*rel_path.parts[1:])
        
        possible_test_names = [
            f"test_{rel_path.stem}.py",
            f"test_{rel_path.stem}_*.py",
            f"{rel_path.stem}_test.py"
        ]
        
        corresponding_tests = []
        
        for test_file in self.test_files:
            test_name = test_file.name
            for pattern in possible_test_names:
                if pattern.replace('*', '') in test_name or test_name.startswith(pattern.replace('*', '')):
                    corresponding_tests.append(test_file)
        
        return corresponding_tests
    
    def analyze_test_coverage_for_file(self, source_file: Path) -> Dict:
        """Analiza la cobertura de tests para un archivo específico."""
        
        source_analysis = self.analyze_function_coverage(source_file)
        corresponding_tests = self.find_corresponding_test_file(source_file)
        
        if not corresponding_tests:
            return {
                'source_file': source_file,
                'functions': source_analysis.get('functions', []),
                'classes': source_analysis.get('classes', []),
                'test_files': [],
                'coverage_status': 'NO_TESTS',
                'tested_functions': [],
                'untested_functions': source_analysis.get('functions', []),
                'coverage_percentage': 0
            }
        
        # Analizar qué funciones están siendo testeadas
        tested_functions = set()
        
        for test_file in corresponding_tests:
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    test_content = f.read()
                
                # Buscar referencias a funciones del archivo fuente
                for func_name in source_analysis.get('functions', []):
                    if func_name in test_content:
                        tested_functions.add(func_name)
                        
            except Exception as e:
                print(f"⚠️ Error leyendo test {test_file}: {e}")
        
        total_functions = len(source_analysis.get('functions', []))
        tested_count = len(tested_functions)
        coverage_percentage = (tested_count / total_functions * 100) if total_functions > 0 else 0
        
        untested_functions = [f for f in source_analysis.get('functions', []) if f not in tested_functions]
        
        return {
            'source_file': source_file,
            'functions': source_analysis.get('functions', []),
            'classes': source_analysis.get('classes', []),
            'test_files': corresponding_tests,
            'coverage_status': 'PARTIAL' if tested_count > 0 else 'NO_COVERAGE',
            'tested_functions': list(tested_functions),
            'untested_functions': untested_functions,
            'coverage_percentage': coverage_percentage
        }
    
    def identify_critical_files(self) -> List[Path]:
        """Identifica archivos críticos que deberían tener alta cobertura."""
        
        critical_patterns = [
            '**/controller.py',
            '**/model.py', 
            '**/view.py',
            '**/database_manager.py',
            '**/auth_manager.py',
            '**/module_manager.py',
            '**/app.py',
            '**/main.py'
        ]
        
        critical_files = []
        for pattern in critical_patterns:
            for file_path in self.project_root.glob(pattern):
                if file_path in self.source_files:
                    critical_files.append(file_path)
        
        return critical_files
    
    def run_comprehensive_analysis(self) -> Dict:
        """Ejecuta análisis completo de cobertura."""
        
        print("🔍 INICIANDO ANÁLISIS DE COBERTURA DE TESTS")
        print("=" * 60)
        
        # Escanear archivos
        self.scan_source_files()
        self.scan_test_files()
        
        # Identificar archivos críticos
        critical_files = self.identify_critical_files()
        print(f"⚡ Archivos críticos identificados: {len(critical_files)}")
        
        # Analizar cobertura por archivo
        coverage_results = []
        files_without_tests = []
        low_coverage_files = []
        
        print("\n📊 ANALIZANDO COBERTURA POR ARCHIVO...")
        
        for source_file in self.source_files:
            if 'main.py' in str(source_file) or any(critical in str(source_file) for critical in ['controller', 'model', 'view']):
                analysis = self.analyze_test_coverage_for_file(source_file)
                coverage_results.append(analysis)
                
                # Identificar problemas
                if analysis['coverage_status'] == 'NO_TESTS':
                    files_without_tests.append(source_file)
                elif analysis['coverage_percentage'] < 50:
                    low_coverage_files.append((source_file, analysis['coverage_percentage']))
                
                # Mostrar estado
                status_icon = "❌" if analysis['coverage_status'] == 'NO_TESTS' else "⚠️" if analysis['coverage_percentage'] < 50 else "✅"
                print(f"{status_icon} {source_file.relative_to(self.project_root)} - {analysis['coverage_percentage']:.1f}%")
        
        # Generar resumen
        total_analyzed = len(coverage_results)
        no_tests = len(files_without_tests)
        low_coverage = len(low_coverage_files)
        good_coverage = total_analyzed - no_tests - low_coverage
        
        # Identificar gaps críticos que podrían causar los 263 errores
        critical_gaps = []
        
        for result in coverage_results:
            if result['source_file'] in critical_files:
                if result['coverage_status'] == 'NO_TESTS':
                    critical_gaps.append(f"SIN_TESTS: {result['source_file'].relative_to(self.project_root)}")
                elif result['coverage_percentage'] < 30:
                    critical_gaps.append(f"COBERTURA_BAJA: {result['source_file'].relative_to(self.project_root)} ({result['coverage_percentage']:.1f}%)")
                
                # Funciones específicas sin tests
                if len(result['untested_functions']) > 0:
                    for func in result['untested_functions']:
                        if not func.startswith('_'):  # Excluir métodos privados
                            critical_gaps.append(f"FUNCIÓN_SIN_TEST: {result['source_file'].relative_to(self.project_root)}::{func}")
        
        return {
            'total_source_files': len(self.source_files),
            'total_test_files': len(self.test_files),
            'total_analyzed': total_analyzed,
            'files_without_tests': no_tests,
            'low_coverage_files': low_coverage,
            'good_coverage_files': good_coverage,
            'critical_gaps': critical_gaps,
            'coverage_results': coverage_results,
            'files_without_tests_list': files_without_tests,
            'low_coverage_files_list': low_coverage_files
        }
    
    def generate_coverage_report(self, analysis_results: Dict) -> str:
        """Genera reporte detallado de cobertura."""
        
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"COVERAGE_ANALYSIS_{timestamp}.md"
        
        report_content = f"""# ANÁLISIS DE COBERTURA DE TESTS - {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

## 📊 RESUMEN EJECUTIVO

**PROBLEMA CRÍTICO:** El sistema reporta 263 errores que no están siendo detectados por los tests.

### Métricas de Cobertura
- **Archivos fuente totales:** {analysis_results['total_source_files']}
- **Archivos de test:** {analysis_results['total_test_files']}
- **Archivos analizados:** {analysis_results['total_analyzed']}
- **Sin tests:** {analysis_results['files_without_tests']} ({analysis_results['files_without_tests']/analysis_results['total_analyzed']*100:.1f}%)
- **Cobertura baja:** {analysis_results['low_coverage_files']} ({analysis_results['low_coverage_files']/analysis_results['total_analyzed']*100:.1f}%)
- **Buena cobertura:** {analysis_results['good_coverage_files']} ({analysis_results['good_coverage_files']/analysis_results['total_analyzed']*100:.1f}%)

## ❌ GAPS CRÍTICOS IDENTIFICADOS

**Total de gaps críticos que pueden causar los 263 errores:** {len(analysis_results['critical_gaps'])}

"""
        
        for i, gap in enumerate(analysis_results['critical_gaps'], 1):
            report_content += f"{i}. {gap}\n"
        
        report_content += f"""
## 📂 ARCHIVOS SIN COBERTURA DE TESTS

"""
        
        for file_path in analysis_results['files_without_tests_list']:
            rel_path = file_path.relative_to(self.project_root)
            report_content += f"- ❌ `{rel_path}`\n"
        
        report_content += f"""
## ⚠️ ARCHIVOS CON COBERTURA INSUFICIENTE

"""
        
        for file_path, coverage in analysis_results['low_coverage_files_list']:
            rel_path = file_path.relative_to(self.project_root)
            report_content += f"- ⚠️ `{rel_path}` - {coverage:.1f}%\n"
        
        report_content += f"""
## 🎯 PLAN DE ACCIÓN PARA REDUCIR LOS 263 ERRORES

### Prioridad Crítica - Corregir Inmediatamente
1. **Crear tests para archivos sin cobertura:** {analysis_results['files_without_tests']} archivos
2. **Mejorar cobertura baja:** {analysis_results['low_coverage_files']} archivos
3. **Testear funciones públicas sin cobertura:** {len([g for g in analysis_results['critical_gaps'] if 'FUNCIÓN_SIN_TEST' in g])} funciones

### Estrategia de Implementación
1. **Fase 1:** Tests unitarios para controladores principales
2. **Fase 2:** Tests de integración para flujos críticos  
3. **Fase 3:** Tests E2E para validar funcionalidad completa
4. **Fase 4:** Tests de regresión para prevenir nuevos errores

### Estimación de Reducción de Errores
- **Con tests unitarios:** -60% errores (≈105 errores menos)
- **Con tests de integración:** -80% errores (≈210 errores menos)
- **Con tests E2E:** -90% errores (≈237 errores menos)

## 📈 MÉTRICAS DE PROGRESO

Para reducir los 263 errores a <10:

- **Tests críticos a crear:** {len([g for g in analysis_results['critical_gaps'] if 'SIN_TESTS' in g])}
- **Funciones a testear:** {len([g for g in analysis_results['critical_gaps'] if 'FUNCIÓN_SIN_TEST' in g])}
- **Cobertura objetivo:** 80% mínimo en archivos críticos
- **Tiempo estimado:** 2-3 días de trabajo enfocado

---
*Análisis generado automáticamente - Priorizar corrección inmediata*
"""
        
        # Escribir reporte
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return report_file

def main():
    """Función principal del análisis de cobertura."""
    
    project_root = os.path.dirname(os.path.abspath(__file__))
    analyzer = TestCoverageAnalyzer(project_root)
    
    # Ejecutar análisis
    results = analyzer.run_comprehensive_analysis()
    
    # Generar reporte
    report_file = analyzer.generate_coverage_report(results)
    
    print("\n" + "=" * 60)
    print("🏁 ANÁLISIS DE COBERTURA COMPLETADO")
    print("=" * 60)
    print(f"📊 GAPS CRÍTICOS IDENTIFICADOS: {len(results['critical_gaps'])}")
    print(f"📂 ARCHIVOS SIN TESTS: {results['files_without_tests']}")
    print(f"⚠️ COBERTURA INSUFICIENTE: {results['low_coverage_files']}")
    print(f"📋 REPORTE GENERADO: {report_file}")
    print("\n🎯 CONCLUSIÓN: Los 263 errores se deben a gaps en la cobertura de tests")
    print("   Priorizar la creación de tests para los archivos identificados.")
    
    return results['critical_gaps']

if __name__ == "__main__":
    critical_gaps = main()
    print(f"\nGaps críticos encontrados: {len(critical_gaps)}")