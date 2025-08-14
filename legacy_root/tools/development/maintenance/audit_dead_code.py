#!/usr/bin/env python3
"""
Auditoría de Código Muerto - Rexus.app

Este script identifica:
- Clases y funciones no utilizadas
- Imports no utilizados
- Archivos huérfanos sin referencias
- Utilidades duplicadas o obsoletas

Ejecutar desde la raíz del proyecto:
    python tools/development/maintenance/audit_dead_code.py
"""

import os
import ast
import sys
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

# Agregar directorio raíz al path
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_dir))

class DeadCodeAuditor:
    """Auditor de código muerto y utilidades no utilizadas."""

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.python_files = []
        self.defined_items = defaultdict(set)  # archivo -> {clases, funciones}
        self.imported_items = defaultdict(set)  # archivo -> {imports}
        self.referenced_items = defaultdict(set)  # item -> {archivos que lo referencian}
        self.suspicious_files = []

        # Archivos a excluir de la auditoría
        self.exclude_patterns = [
            "__pycache__",
            ".git",
            ".env",
            "node_modules",
            "tests/",
            "test_",
            "__init__.py"
        ]

        # Clases/funciones específicas mencionadas en checklist
        self.target_items = [
            "BackupIntegration",
            "InventoryIntegration",
            "SmartTooltip",
            "DatabaseBackupManager",
            "AutomatedBackupScheduler"
        ]

    def should_exclude_file(self, file_path: Path) -> bool:
        """Determina si un archivo debe ser excluido."""
        file_str = str(file_path)
        return any(pattern in file_str for pattern in self.exclude_patterns)

    def find_python_files(self):
        """Encuentra todos los archivos Python en el proyecto."""
        print("Buscando archivos Python...")

        for file_path in self.root_path.rglob("*.py"):
            if not self.should_exclude_file(file_path):
                self.python_files.append(file_path)

        print(f"Encontrados {len(self.python_files)} archivos Python")

    def analyze_file(self, file_path: Path):
        """Analiza un archivo Python para extraer definiciones e imports."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parsear AST
            tree = ast.parse(content)

            # Extraer definiciones (clases y funciones)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    self.defined_items[str(file_path)].add(f"class:{node.name}")
                elif isinstance(node, ast.FunctionDef):
                    self.defined_items[str(file_path)].add(f"function:{node.name}")
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        self.imported_items[str(file_path)].add(f"import:{alias.name}")
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        self.imported_items[str(file_path)].add(f"from:{module}.{alias.name}")

            # Buscar referencias a elementos objetivo
            for target in self.target_items:
                if target in content:
                    self.referenced_items[target].add(str(file_path))

        except Exception as e:
            print(f"Error analizando {file_path}: {e}")

    def find_references_in_content(self, item_name: str) -> Set[str]:
        """Busca referencias a un item en todo el contenido."""
        references = set()

        for file_path in self.python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Buscar referencias (no imports)
                patterns = [
                    rf'\b{item_name}\b\s*\(',  # Llamadas a función/clase
                    rf'\.{item_name}\b',       # Acceso a atributo
                    rf'\b{item_name}\s*=',     # Asignaciones
                    rf'isinstance\([^,]+,\s*{item_name}\)', # isinstance checks
                ]

                for pattern in patterns:
                    if re.search(pattern, content):
                        references.add(str(file_path))
                        break

            except Exception:
                continue

        return references

    def analyze_target_items(self):
        """Analiza específicamente los items objetivo del checklist."""
        print("\nAnalizando items específicos del checklist...")

        results = {}

        for target in self.target_items:
            print(f"\n🔍 Analizando: {target}")

            # Encontrar archivos que definen el item
            defining_files = []
            for file_path, definitions in self.defined_items.items():
                for definition in definitions:
                    if target in definition:
                        defining_files.append(file_path)

            # Encontrar archivos que importan el item
            importing_files = []
            for file_path, imports in self.imported_items.items():
                for import_stmt in imports:
                    if target in import_stmt:
                        importing_files.append(file_path)

            # Encontrar referencias en contenido
            reference_files = self.find_references_in_content(target)

            results[target] = {
                'defining_files': defining_files,
                'importing_files': importing_files,
                'reference_files': list(reference_files),
                'total_references': len(reference_files) + len(importing_files)
            }

            # Mostrar resultado inmediato
            if results[target]['total_references'] == 0:
                print(f"   ❌ NO UTILIZADO - 0 referencias")
            elif results[target]['total_references'] <= 2:
                print(f"   ⚠️  POCO UTILIZADO - {results[target]['total_references']} referencias")
            else:
                print(f"   ✅ UTILIZADO - {results[target]['total_references']} referencias")

        return results

    def find_suspicious_files(self):
        """Encuentra archivos que podrían ser código muerto."""
        print("\nBuscando archivos potencialmente muertos...")

        suspicious_patterns = [
            "_old",
            "_backup",
            "_deprecated",
            "_unused",
            "_legacy",
            "temp_",
            "test_manual",
            "_refactorizado",
        ]

        for file_path in self.python_files:
            file_name = file_path.name.lower()

            # Archivos con patrones sospechosos
            for pattern in suspicious_patterns:
                if pattern in file_name:
                    self.suspicious_files.append((str(file_path), f"Patrón sospechoso: {pattern}"))
                    break

            # Archivos muy pequeños (posibles stubs)
            try:
                if file_path.stat().st_size < 500:  # Menos de 500 bytes
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()

                    # Filtrar comentarios y líneas vacías
                    code_lines = [line.strip() for line in lines
                                if line.strip() and \
                                    not line.strip().startswith('#')]

                    if len(code_lines) <= 5:  # Muy poco código real
                        self.suspicious_files.append((str(file_path), f"Archivo muy pequeño: {len(code_lines)} líneas de código"))
            except Exception:
                pass

    def generate_report(self, target_analysis: Dict):
        """Genera un reporte completo de la auditoría."""
        print("\n" + "="*80)
        print("REPORTE DE AUDITORIA DE CODIGO MUERTO")
        print("="*80)

        # Analisis de items especificos
        print("\nANALISIS DE ITEMS ESPECIFICOS DEL CHECKLIST:")
        print("-" * 60)

        dead_items = []
        low_usage_items = []
        active_items = []

        for item, data in target_analysis.items():
            references = data['total_references']

            if references == 0:
                dead_items.append(item)
                print(f"❌ {item}: NO UTILIZADO")
                if data['defining_files']:
                    print(f"   📁 Definido en: {', '.join(data['defining_files'][:2])}{'...' if len(data['defining_files']) > 2 else ''}")

            elif references <= 2:
                low_usage_items.append(item)
                print(f"⚠️  {item}: POCO UTILIZADO ({references} refs)")
                if data['importing_files']:
                    print(f"   📥 Importado en: {', '.join(data['importing_files'][:2])}{'...' if len(data['importing_files']) > 2 else ''}")

            else:
                active_items.append(item)
                print(f"✅ {item}: ACTIVO ({references} refs)")

        # Archivos sospechosos
        if self.suspicious_files:
            print(f"\n📁 ARCHIVOS POTENCIALMENTE MUERTOS ({len(self.suspicious_files)}):")
            print("-" * 60)

            for file_path, reason in self.suspicious_files[:10]:  # Mostrar solo los primeros 10
                relative_path = str(Path(file_path).relative_to(self.root_path))
                print(f"⚠️  {relative_path}")
                print(f"   Razón: {reason}")

            if len(self.suspicious_files) > 10:
                print(f"   ... y {len(self.suspicious_files) - 10} más")

        # Resumen y recomendaciones
        print(f"\n📊 RESUMEN:")
        print("-" * 60)
        print(f"Items completamente muertos: {len(dead_items)}")
        print(f"Items con poco uso: {len(low_usage_items)}")
        print(f"Items activos: {len(active_items)}")
        print(f"Archivos sospechosos: {len(self.suspicious_files)}")

        print(f"\n💡 RECOMENDACIONES:")
        print("-" * 60)

        if dead_items:
            print("🗑️  ELIMINAR COMPLETAMENTE:")
            for item in dead_items:
                defining_files = target_analysis[item]['defining_files']
                if defining_files:
                    for file_path in defining_files:
                        relative_path = str(Path(file_path).relative_to(self.root_path))
                        print(f"   - {relative_path} (clase/función {item})")

        if low_usage_items:
            print("\n📝 REVISAR PARA POSIBLE ELIMINACIÓN:")
            for item in low_usage_items:
                print(f"   - {item} ({target_analysis[item]['total_references']} referencias)")

        if active_items:
            print("\n✅ MANTENER (en uso activo):")
            for item in active_items:
                print(f"   - {item}")

        return {
            'dead_items': dead_items,
            'low_usage_items': low_usage_items,
            'active_items': active_items,
            'suspicious_files': self.suspicious_files
        }

    def run_audit(self):
        """Ejecuta la auditoría completa."""
        print("Iniciando auditoria de codigo muerto...")

        # 1. Encontrar archivos Python
        self.find_python_files()

        # 2. Analizar cada archivo
        print("Analizando archivos...")
        for file_path in self.python_files:
            self.analyze_file(file_path)

        # 3. Analizar items específicos
        target_analysis = self.analyze_target_items()

        # 4. Encontrar archivos sospechosos
        self.find_suspicious_files()

        # 5. Generar reporte
        results = self.generate_report(target_analysis)

        return results

def main():
    """Función principal."""
    try:
        auditor = DeadCodeAuditor(root_dir)
        results = auditor.run_audit()

        # Determinar código de salida
        dead_count = len(results['dead_items'])
        suspicious_count = len(results['suspicious_files'])

        if dead_count > 0 or suspicious_count > 5:
            print(f"\n⚠️  Se encontraron {dead_count} items muertos y {suspicious_count} archivos sospechosos")
            print("Revisar recomendaciones para limpiar el código")
            return 1
        else:
            print(f"\n✅ Auditoría completa - código relativamente limpio")
            return 0

    except KeyboardInterrupt:
        print("\nProceso interrumpido por usuario")
        return 130
    except Exception as e:
        print(f"Error inesperado: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
