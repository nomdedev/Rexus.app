#!/usr/bin/env python3
"""
AUDITORÍA EXPERTA COMPLETA - Rexus.app v2.0.0
Análisis exhaustivo de cada archivo del proyecto para optimización máxima.

Este script analiza TODOS los archivos del proyecto y genera un reporte
completo de optimizaciones, duplicados, archivos innecesarios y mejoras.
"""

import os
import re
import ast
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict, Counter
import json


class ExpertProjectAuditor:
    """Auditor experto para análisis completo del proyecto."""

    def __init__(self, project_path: str = "."):
        self.project_path = Path(project_path)
        self.report = {
            "summary": {
                "total_files": 0,
                "total_size": 0,
                "duplicates_found": 0,
                "unused_files": 0,
                "optimization_opportunities": 0
            },
            "file_analysis": {},
            "duplicates": [],
            "unused_files": [],
            "optimization_suggestions": [],
            "structure_analysis": {},
            "code_quality": {}
        }

        # Patrones de archivos críticos que NO se deben tocar
        self.critical_files = {
            'main.py', '__init__.py', 'requirements.txt', '.env',
            'README.md', '.gitignore', 'setup.py'
        }

        # Extensiones de archivos a analizar
        self.code_extensions = {'.py', '.js', '.html', '.css', '.json', '.sql'}
        self.doc_extensions = {'.md', '.txt', '.rst'}
        self.config_extensions = {'.ini', '.cfg', '.conf', '.yaml', '.yml'}

        # Patrones de archivos innecesarios
        self.unnecessary_patterns = [
            r'.*_backup.*',
            r'.*_old.*',
            r'.*_temp.*',
            r'.*_test.*\.py$',
            r'.*_ejemplo.*',
            r'.*_prueba.*',
            r'.*\.backup$',
            r'.*\.bak$',
            r'.*~$',
            r'\.DS_Store$',
            r'Thumbs\.db$',
            r'.*\.log$',
            r'.*\.tmp$'
        ]

    def run_complete_audit(self) -> Dict:
        """Ejecuta auditoría completa del proyecto."""
        print("INICIANDO AUDITORIA EXPERTA COMPLETA")
        print("=" * 60)

        # Fase 1: Análisis de estructura
        print("Fase 1: Analizando estructura del proyecto...")
        self._analyze_project_structure()

        # Fase 2: Análisis de archivos
        print("Fase 2: Analizando cada archivo...")
        self._analyze_all_files()

        # Fase 3: Detección de duplicados
        print("Fase 3: Detectando archivos duplicados...")
        self._detect_duplicates()

        # Fase 4: Detección de archivos no utilizados
        print("Fase 4: Identificando archivos no utilizados...")
        self._detect_unused_files()

        # Fase 5: Análisis de calidad de código
        print("Fase 5: Analizando calidad del código...")
        self._analyze_code_quality()

        # Fase 6: Oportunidades de optimización
        print("Fase 6: Identificando optimizaciones...")
        self._identify_optimizations()

        # Fase 7: Generar reporte
        print("Fase 7: Generando reporte final...")
        self._generate_final_report()

        return self.report

    def _analyze_project_structure(self):
        """Analiza la estructura general del proyecto."""
        structure = {}
        total_size = 0
        total_files = 0

        for root, dirs, files in os.walk(self.project_path):
            root_path = Path(root)
            relative_path = root_path.relative_to(self.project_path)

            # Ignorar directorios específicos
            if any(ignore in str(relative_path) for ignore in ['.git', '__pycache__', '.pytest_cache']):
                continue

            dir_info = {
                'files': len(files),
                'subdirs': len(dirs),
                'size': 0,
                'file_types': Counter()
            }

            for file in files:
                file_path = root_path / file
                if file_path.exists():
                    file_size = file_path.stat().st_size
                    dir_info['size'] += file_size
                    total_size += file_size
                    total_files += 1

                    ext = file_path.suffix.lower()
                    dir_info['file_types'][ext] += 1

            structure[str(relative_path)] = dir_info

        self.report['structure_analysis'] = structure
        self.report['summary']['total_files'] = total_files
        self.report['summary']['total_size'] = total_size

    def _analyze_all_files(self):
        """Analiza cada archivo individualmente."""
        for root, dirs, files in os.walk(self.project_path):
            # Ignorar ciertos directorios
            dirs[:] = [d for d in dirs if not d.startswith('.') and \
                d != '__pycache__']

            for file in files:
                file_path = Path(root) / file
                relative_path = file_path.relative_to(self.project_path)

                # Analizar el archivo
                analysis = self._analyze_single_file(file_path)
                self.report['file_analysis'][str(relative_path)] = analysis

    def _analyze_single_file(self, file_path: Path) -> Dict:
        """Analiza un archivo específico."""
        analysis = {
            'size': 0,
            'type': 'unknown',
            'lines': 0,
            'is_empty': False,
            'is_duplicate_candidate': False,
            'is_unnecessary': False,
            'imports': [],
            'classes': [],
            'functions': [],
            'issues': []
        }

        if not file_path.exists():
            analysis['issues'].append('File does not exist')
            return analysis

        # Información básica
        stat = file_path.stat()
        analysis['size'] = stat.st_size
        analysis['extension'] = file_path.suffix.lower()

        # Verificar si es innecesario por patrón
        file_name = file_path.name
        for pattern in self.unnecessary_patterns:
            if re.match(pattern, file_name):
                analysis['is_unnecessary'] = True
                analysis['issues'].append(f'Matches unnecessary pattern: {pattern}')

        # Análisis específico por tipo de archivo
        if analysis['extension'] == '.py':
            analysis.update(self._analyze_python_file(file_path))
        elif analysis['extension'] in self.doc_extensions:
            analysis.update(self._analyze_doc_file(file_path))
        elif analysis['extension'] in self.config_extensions:
            analysis.update(self._analyze_config_file(file_path))

        return analysis

    def _analyze_python_file(self, file_path: Path) -> Dict:
        """Análisis específico para archivos Python."""
        analysis = {
            'type': 'python',
            'imports': [],
            'classes': [],
            'functions': [],
            'is_module': False,
            'has_main': False,
            'issues': []
        }

        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            analysis['lines'] = len(content.splitlines())
            analysis['is_empty'] = len(content.strip()) == 0

            # Análisis AST
            try:
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            analysis['imports'].append(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        module = node.module or ''
                        for alias in node.names:
                            analysis['imports'].append(f"{module}.{alias.name}")
                    elif isinstance(node, ast.ClassDef):
                        analysis['classes'].append(node.name)
                    elif isinstance(node, ast.FunctionDef):
                        analysis['functions'].append(node.name)
                        if node.name == 'main':
                            analysis['has_main'] = True

                # Verificar si es un módulo válido
                if analysis['imports'] or analysis['classes'] or analysis['functions']:
                    analysis['is_module'] = True

            except SyntaxError as e:
                analysis['issues'].append(f'Syntax error: {e}')
            except Exception as e:
                analysis['issues'].append(f'AST analysis error: {e}')

        except Exception as e:
            analysis['issues'].append(f'File read error: {e}')

        return analysis

    def _analyze_doc_file(self, file_path: Path) -> Dict:
        """Análisis para archivos de documentación."""
        analysis = {'type': 'documentation'}

        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            analysis['lines'] = len(content.splitlines())
            analysis['is_empty'] = len(content.strip()) == 0
            analysis['word_count'] = len(content.split())
        except Exception as e:
            analysis['issues'] = [f'Read error: {e}']

        return analysis

    def _analyze_config_file(self, file_path: Path) -> Dict:
        """Análisis para archivos de configuración."""
        analysis = {'type': 'configuration'}

        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            analysis['lines'] = len(content.splitlines())
            analysis['is_empty'] = len(content.strip()) == 0
        except Exception as e:
            analysis['issues'] = [f'Read error: {e}']

        return analysis

    def _detect_duplicates(self):
        """Detecta archivos duplicados por contenido."""
        file_hashes = defaultdict(list)

        # Calcular hashes de todos los archivos
        for file_rel_path, analysis in self.report['file_analysis'].items():
            file_path = self.project_path / file_rel_path

            if not file_path.exists() or analysis['size'] == 0:
                continue

            try:
                content = file_path.read_bytes()
                file_hash = hashlib.md5(content).hexdigest()
                file_hashes[file_hash].append(file_rel_path)
            except Exception:
                continue

        # Identificar duplicados
        for file_hash, files in file_hashes.items():
            if len(files) > 1:
                duplicate_group = {
                    'hash': file_hash,
                    'files': files,
                    'size': self.report['file_analysis'][files[0]]['size'],
                    'recommendation': self._recommend_duplicate_action(files)
                }
                self.report['duplicates'].append(duplicate_group)

        self.report['summary']['duplicates_found'] = len(self.report['duplicates'])

    def _recommend_duplicate_action(self, files: List[str]) -> str:
        """Recomienda qué hacer con archivos duplicados."""
        # Priorizar archivos en ubicaciones estándar
        priority_order = [
            lambda f: 'view.py' in f and \
                not any(x in f for x in ['_old', '_backup', '_temp']),
            lambda f: 'model.py' in f and \
                not any(x in f for x in ['_old', '_backup', '_temp']),
            lambda f: 'controller.py' in f and \
                not any(x in f for x in ['_old', '_backup', '_temp']),
            lambda f: not any(x in f for x in ['_old',
'_backup',
                '_temp',
                '_copy']),
            lambda f: True  # Fallback
        ]

        for priority_func in priority_order:
            keeper_candidates = [f for f in files if priority_func(f)]
            if keeper_candidates:
                keeper = keeper_candidates[0]
                others = [f for f in files if f != keeper]
                return f"Keep: {keeper}, Delete: {', '.join(others)}"

        return f"Manual review needed for: {', '.join(files)}"

    def _detect_unused_files(self):
        """Detecta archivos que no son utilizados."""
        # Archivos que definitivamente no se usan
        definitely_unused = []

        for file_rel_path, analysis in self.report['file_analysis'].items():
            file_name = Path(file_rel_path).name

            # Archivos marcados como innecesarios
            if analysis.get('is_unnecessary', False):
                definitely_unused.append({
                    'file': file_rel_path,
                    'reason': 'Matches unnecessary pattern',
                    'safe_to_delete': True
                })

            # Archivos vacíos (excepto __init__.py)
            elif analysis.get('is_empty', False) and \
                file_name != '__init__.py':
                definitely_unused.append({
                    'file': file_rel_path,
                    'reason': 'Empty file',
                    'safe_to_delete': True
                })

            # Archivos Python sin funciones, clases o imports útiles
            elif (analysis.get('type') == 'python' and
                  not analysis.get('is_module', False) and
                  not analysis.get('has_main', False) and
                  file_name != '__init__.py'):
                definitely_unused.append({
                    'file': file_rel_path,
                    'reason': 'Python file with no useful content',
                    'safe_to_delete': False  # Requiere revisión manual
                })

        self.report['unused_files'] = definitely_unused
        self.report['summary']['unused_files'] = len(definitely_unused)

    def _analyze_code_quality(self):
        """Analiza la calidad general del código."""
        quality_metrics = {
            'files_with_syntax_errors': 0,
            'empty_files': 0,
            'large_files': 0,
            'files_with_issues': 0,
            'total_lines': 0,
            'avg_file_size': 0
        }

        total_size = 0
        valid_files = 0

        for file_rel_path, analysis in self.report['file_analysis'].items():
            if analysis.get('issues'):
                quality_metrics['files_with_issues'] += 1
                if any('syntax error' in issue.lower() for issue in analysis['issues']):
                    quality_metrics['files_with_syntax_errors'] += 1

            if analysis.get('is_empty', False):
                quality_metrics['empty_files'] += 1

            if analysis.get('size', 0) > 50000:  # 50KB
                quality_metrics['large_files'] += 1

            lines = analysis.get('lines', 0)
            if lines > 0:
                quality_metrics['total_lines'] += lines
                total_size += analysis.get('size', 0)
                valid_files += 1

        if valid_files > 0:
            quality_metrics['avg_file_size'] = total_size // valid_files

        self.report['code_quality'] = quality_metrics

    def _identify_optimizations(self):
        """Identifica oportunidades de optimización."""
        optimizations = []

        # Optimización 1: Archivos duplicados
        if self.report['duplicates']:
            optimizations.append({
                'category': 'Duplicates',
                'priority': 'High',
                'description': f"Found {len(self.report['duplicates'])} groups of duplicate files",
                'action': 'Remove duplicate files as recommended',
                'estimated_savings': sum(dup['size'] * (len(dup['files']) - 1) for dup in self.report['duplicates'])
            })

        # Optimización 2: Archivos innecesarios
        safe_to_delete = [f for f in self.report['unused_files'] if f['safe_to_delete']]
        if safe_to_delete:
            total_size = sum(self.report['file_analysis'][f['file']]['size'] for f in safe_to_delete)
            optimizations.append({
                'category': 'Unused Files',
                'priority': 'Medium',
                'description': f"Found {len(safe_to_delete)} files safe to delete",
                'action': 'Delete unused files',
                'estimated_savings': total_size
            })

        # Optimización 3: Archivos grandes
        large_files = [
            (path, analysis) for path, analysis in self.report['file_analysis'].items()
            if analysis.get('size', 0) > 100000  # 100KB
        ]
        if large_files:
            optimizations.append({
                'category': 'Large Files',
                'priority': 'Low',
                'description': f"Found {len(large_files)} large files that could be optimized",
                'action': 'Review and potentially split large files',
                'estimated_savings': 0
            })

        self.report['optimization_suggestions'] = optimizations
        self.report['summary']['optimization_opportunities'] = len(optimizations)

    def _generate_final_report(self):
        """Genera el reporte final."""
        total_savings = sum(opt.get('estimated_savings', 0) for opt in self.report['optimization_suggestions'])

        print("\n" + "=" * 60)
        print("🎯 REPORTE FINAL DE AUDITORÍA EXPERTA")
        print("=" * 60)
        print(f"📊 Archivos analizados: {self.report['summary']['total_files']:,}")
        print(f"💾 Tamaño total: {self._format_size(self.report['summary']['total_size'])}")
        print(f"🔍 Duplicados encontrados: {self.report['summary']['duplicates_found']}")
        print(f"🗑️  Archivos no utilizados: {self.report['summary']['unused_files']}")
        print(f"⚡ Oportunidades de optimización: {self.report['summary']['optimization_opportunities']}")
        print(f"💰 Ahorro estimado: {self._format_size(total_savings)}")

        print("\n📋 ACCIONES RECOMENDADAS:")
        print("-" * 30)

        for i, opt in enumerate(self.report['optimization_suggestions'], 1):
            print(f"{i}. [{opt['priority']}] {opt['category']}")
            print(f"   {opt['description']}")
            print(f"   Acción: {opt['action']}")
            if opt['estimated_savings'] > 0:
                print(f"   Ahorro: {self._format_size(opt['estimated_savings'])}")
            print()

    def _format_size(self, size_bytes: int) -> str:
        """Formatea el tamaño en bytes a una representación legible."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def execute_cleanup(self) -> bool:
        """Ejecuta la limpieza automática basada en el análisis."""
        print("\n🧹 EJECUTANDO LIMPIEZA AUTOMÁTICA")
        print("=" * 40)

        files_deleted = 0
        bytes_saved = 0

        # Eliminar duplicados recomendados
        for dup_group in self.report['duplicates']:
            recommendation = dup_group['recommendation']
            if 'Delete:' in recommendation:
                files_to_delete = recommendation.split('Delete:')[1].strip().split(', ')
                for file_rel_path in files_to_delete:
                    file_path = self.project_path / file_rel_path.strip()
                    if file_path.exists():
                        file_size = file_path.stat().st_size
                        try:
                            file_path.unlink()
                            print(f"✅ Eliminado duplicado: {file_rel_path}")
                            files_deleted += 1
                            bytes_saved += file_size
                        except Exception as e:
                            print(f"❌ Error eliminando {file_rel_path}: {e}")

        # Eliminar archivos innecesarios seguros
        for unused_file in self.report['unused_files']:
            if unused_file['safe_to_delete']:
                file_path = self.project_path / unused_file['file']
                if file_path.exists():
                    file_size = file_path.stat().st_size
                    try:
                        file_path.unlink()
                        print(f"✅ Eliminado innecesario: {unused_file['file']}")
                        files_deleted += 1
                        bytes_saved += file_size
                    except Exception as e:
                        print(f"❌ Error eliminando {unused_file['file']}: {e}")

        print(f"\n🎉 LIMPIEZA COMPLETADA")
        print(f"🗑️  Archivos eliminados: {files_deleted}")
        print(f"💾 Espacio liberado: {self._format_size(bytes_saved)}")

        return files_deleted > 0

    def save_report(self, output_file: str = "expert_audit_report.json"):
        """Guarda el reporte en un archivo JSON."""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, indent=2, ensure_ascii=False)
        print(f"📄 Reporte guardado en: {output_file}")


def main():
    """Función principal."""
    auditor = ExpertProjectAuditor()

    # Ejecutar auditoría completa
    report = auditor.run_complete_audit()

    # Guardar reporte
    auditor.save_report()

    # Preguntar si ejecutar limpieza
    print("\n❓ ¿Desea ejecutar la limpieza automática? (s/n): ", end="")
    response = input().lower().strip()

    if response in ['s', 'si', 'y', 'yes']:
        auditor.execute_cleanup()

        # Ejecutar auditoría post-limpieza
        print("\n🔄 Ejecutando auditoría post-limpieza...")
        post_report = auditor.run_complete_audit()
        auditor.save_report("expert_audit_post_cleanup.json")

    print("\n✅ AUDITORÍA EXPERTA COMPLETADA")
    return report


if __name__ == "__main__":
    main()
